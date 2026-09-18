#!/usr/bin/env python3
"""Pool the pilot (60 logbooks) and extension (176) and recompute the
re-judgment reliability estimates on all 236.

Reads pilot_rep{1,2}_raw.json + arm_rep{1,2}_raw.json, writes
arm_per_claim_verdicts.csv and arm_results.json.

Verdict extraction matches the pilot exactly: claims are sorted by their
returned index before comparison, because the model does not always emit its
claims array in index order and an unsorted read makes identical runs look
divergent. A logbook contributes claim comparisons only where BOTH replicates
returned a parseable verdict for that index.

Schema failures are reported, not silently dropped: the harness backfills an
omitted claim as `inconclusive`, which can manufacture agreement, so any
logbook whose two replicates disagree on claim COUNT is flagged.
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent


def verdicts(rec):
    """index -> verdict for one raw record, sorted by claim index."""
    if not rec.get("raw"):
        return {}
    out = {}
    for c in rec["raw"].get("claims", []):
        try:
            out[int(c.get("claim", -1))] = c.get("verdict")
        except (TypeError, ValueError):
            continue
    return out


def load(pilot, arm):
    recs = {}
    for p in (pilot, arm):
        for r in json.load(open(HERE / p)):
            recs[r["space_id"]] = r
    return recs


def icc1(groups):
    """One-way random-effects ICC(1) on a clustered binary indicator.
    Returns (icc, n_bar, why) -- icc is None when total variance is zero."""
    groups = [np.asarray(g, float) for g in groups if len(g)]
    k = len(groups)
    ns = np.array([len(g) for g in groups], float)
    N = ns.sum()
    if k < 2:
        return None, float(ns.mean()) if k else 0.0, "fewer than 2 clusters"
    grand = np.concatenate(groups).mean()
    if np.concatenate(groups).var() == 0:
        return None, N / k, "zero total variance (constant outcome): ICC is 0/0, not 0"
    msb = sum(n * (g.mean() - grand) ** 2 for n, g in zip(ns, groups)) / (k - 1)
    msw = sum(((g - g.mean()) ** 2).sum() for g in groups) / (N - k)
    n0 = (N - (ns ** 2).sum() / N) / (k - 1)
    icc = (msb - msw) / (msb + (n0 - 1) * msw)
    return float(icc), float(N / k), "ok"


def alpha_nominal(units):
    """Krippendorff's alpha, nominal, 2 coders, no missing data."""
    units = [u for u in units if len(u) == 2]
    n = len(units)
    if n == 0:
        return None, "no units"
    cats = sorted({v for u in units for v in u})
    if len(cats) == 1:
        return None, "single category: alpha is 0/0 (no disagreement possible)"
    Do = sum(u[0] != u[1] for u in units) / n
    counts = {c: 0 for c in cats}
    for u in units:
        for v in u:
            counts[v] += 1
    tot = 2 * n
    De = 1 - sum((counts[c] / tot) ** 2 for c in cats) * (tot / (tot - 1)) \
           + (1 / (tot - 1)) * 0
    De = (tot / (tot - 1)) * (1 - sum((counts[c] / tot) ** 2 for c in cats))
    return float(1 - Do / De), "ok"


def main():
    r1 = load("pilot_rep1_raw.json", "arm_rep1_raw.json")
    r2 = load("pilot_rep2_raw.json", "arm_rep2_raw.json")
    arch = {s["space_id"]: s for s in json.load(open(HERE / "arm_prompts.json"))}
    sids = [s for s in arch if s in r1 and s in r2]
    print("logbooks with both replicates: %d/%d" % (len(sids), len(arch)))

    rows, count_mismatch = [], []
    for sid in sids:
        v1, v2 = verdicts(r1[sid]), verdicts(r2[sid])
        a = arch[sid]
        av = a.get("archived_verdicts") or []
        if len(v1) != len(v2):
            count_mismatch.append((sid, len(v1), len(v2), a["n_claims"]))
        for i in sorted(set(v1) & set(v2)):
            rows.append({"space_id": sid, "band": a["band"], "orid": a["orid"],
                         "claim_idx": i, "n_claims": a["n_claims"],
                         "in_pilot": sid in {x["space_id"] for x in []} or None,
                         "rep1": v1[i], "rep2": v2[i],
                         "archived": av[i - 1] if 0 < i <= len(av) else None,
                         "agree": v1[i] == v2[i]})
    D = pd.DataFrame(rows)
    pilot_sids = {r["space_id"] for r in json.load(open(HERE / "pilot_rep1_raw.json"))}
    D["in_pilot"] = D.space_id.isin(pilot_sids)
    D.to_csv(HERE / "arm_per_claim_verdicts.csv", index=False)

    n = len(D)
    dis = int((~D.agree).sum())
    p = dis / n
    clusters = [g.agree.astype(float).values for _, g in D.groupby("space_id", sort=False)]
    icc, n_bar, why = icc1(clusters)
    units = [(r.rep1, r.rep2) for r in D.itertuples()]
    a_r, awhy = alpha_nominal(units)

    # cluster bootstrap CI for alpha
    cl = list(D.groupby("space_id", sort=False))
    rng = np.random.default_rng(20260912)
    boot = []
    for _ in range(4000):
        pick = rng.integers(0, len(cl), len(cl))
        u = [(r.rep1, r.rep2) for i in pick for r in cl[i][1].itertuples()]
        v, _w = alpha_nominal(u)
        if v is not None:
            boot.append(v)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    hw = (hi - lo) / 2

    dcl = D.groupby("space_id").agree.apply(lambda s: (~s).sum())
    res = {
        "n_logbooks": len(sids), "n_claim_comparisons": n,
        "retest_disagreements": dis, "retest_disagreement_rate": round(p, 5),
        "icc1": None if icc is None else round(icc, 4), "icc_n_bar": round(n_bar, 3),
        "icc_note": why,
        "alpha_retest": None if a_r is None else round(a_r, 4),
        "alpha_ci95": [round(float(lo), 4), round(float(hi), 4)],
        "alpha_half_width": round(float(hw), 4),
        "target_half_width": 0.0458,
        "target_met": bool(hw <= 0.0458),
        "logbooks_with_any_disagreement": int((dcl > 0).sum()),
        "logbooks_fully_stable": int((dcl == 0).sum()),
        "schema_count_mismatches": count_mismatch,
    }

    by_band = D.groupby("band").agg(claims=("agree", "size"),
                                    disagree=("agree", lambda s: int((~s).sum())))
    by_band["rate"] = (by_band.disagree / by_band.claims).round(4)
    bb = {}
    for b, g in D.groupby("band"):
        i, nb, w = icc1([gg.agree.astype(float).values for _, gg in g.groupby("space_id")])
        av, _ = alpha_nominal([(r.rep1, r.rep2) for r in g.itertuples()])
        bb[b] = {"claims": int(len(g)), "disagree": int((~g.agree).sum()),
                 "rate": round(float((~g.agree).mean()), 4),
                 "icc1": None if i is None else round(i, 4),
                 "alpha": None if av is None else round(av, 4)}
    res["by_band"] = bb

    av = D[D.archived.notna()]
    res["archive"] = {
        "n": int(len(av)),
        "fresh_vs_archive_rate": round(float((av.rep1 != av.archived).mean()), 5),
        "fresh_vs_fresh_rate": round(p, 5),
        "caveat": "archive ran the UNPINNED router; no provider field in corpus; "
                  "fresh-vs-archive conflates decode noise with regime difference "
                  "and must not be quoted as a property of the judge",
    }
    json.dump(res, open(HERE / "arm_results.json", "w"), indent=1)

    print("\nclaim comparisons: %d over %d logbooks" % (n, len(sids)))
    print("retest disagreement: %d/%d = %.2f%%" % (dis, n, 100 * p))
    print("ICC(1) = %s (n_bar %.2f) [%s]" % (icc, n_bar, why))
    print("alpha_retest = %.4f  CI [%.4f, %.4f]  half-width %.4f  target 0.0458 met=%s"
          % (a_r, lo, hi, hw, hw <= 0.0458))
    print("logbooks carrying disagreement: %d/%d" % ((dcl > 0).sum(), len(sids)))
    print("\nby band:\n", pd.DataFrame(bb).T.to_string())
    print("\nfresh-vs-archive: %.2f%% (n=%d) vs fresh-vs-fresh %.2f%%"
          % (100 * res["archive"]["fresh_vs_archive_rate"], len(av), 100 * p))
    if count_mismatch:
        print("\nschema count mismatches (%d):" % len(count_mismatch))
        for sid, a1, a2, exp in count_mismatch:
            print("  %-46s rep1 %d, rep2 %d, expected %d" % (sid[:46], a1, a2, exp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
