#!/usr/bin/env python3
"""Stage the extended re-judgment arm (option B: 59 per band = 236 logbooks).

Extends the 60-logbook pilot to the sample size the pilot showed is needed to
reach the protocol's alpha half-width target of 0.0458. Reuses stage_pilot's
prompt builder verbatim -- imported, not copied -- so the instrument cannot
drift between the pilot and the extension.

Design decisions:
  * SUPERSET, not a redraw. The band pools are walked in the same draw order,
    so the first 15 of each band ARE the pilot's 60. Those are already judged;
    only the new logbooks need paid calls.
  * INTEGRITY CHECK on the overlap. For every logbook the pilot already staged,
    the rebuilt prompt must be byte-identical to the stored one. A pinned sha is
    supposed to guarantee that; this asserts it rather than trusting it. A
    mismatch is a hard failure -- it would mean the pilot and extension are not
    the same instrument, and pooling them would be invalid.
  * If a logbook the pilot already judged can no longer be fetched, its stored
    prompt is reused (status ok_reused_pilot) so the superset property holds
    and the pilot's 120 paid calls stay usable.
  * Band quotas held at PER_BAND with the same next-in-band substitution rule.

Usage: python3 stage_arm.py [PER_BAND]      (default 59)
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stage_pilot as sp  # noqa: E402
from fetch_logbooks import read_logbook_markdown, head_sha  # noqa: E402


def main():
    per_band = int(sys.argv[1]) if len(sys.argv) > 1 else 59

    rows = [r for r in csv.DictReader(open(sp.SAMPLE)) if r["arm"] == "primary"]
    bands, order = {}, []
    for r in rows:
        bands.setdefault(r["band"], []).append(r)
        if r["band"] not in order:
            order.append(r["band"])
    for b in order:
        if len(bands[b]) < per_band:
            print("band %s has only %d logbooks, need %d" % (b, len(bands[b]), per_band))
            return 2
    print("primary arm: %d logbooks | quota %d/band -> %d total"
          % (len(rows), per_band, per_band * len(order)), flush=True)

    V = json.load(open(sp.VERDICTS))
    recs = list(V.values()) if isinstance(V, dict) else V
    by_key = {}
    for rec in recs:
        by_key.setdefault((rec["space_id"], rec["sha"]), []).append(rec)
    papers = sp.papers_by_orid(json.load(open(os.path.join(HERE, os.pardir, "icml2026-challenge", "index.json"))))

    prior_path = os.path.join(HERE, "pilot_prompts.json")
    prior = {p["space_id"]: p for p in json.load(open(prior_path))} if os.path.exists(prior_path) else {}
    print("pilot prompts on disk: %d" % len(prior), flush=True)

    staged, meta, subs, mismatches, reused = [], [], [], [], []
    for band in order:
        pool, taken, cursor = bands[band], 0, 0
        while taken < per_band and cursor < len(pool):
            r = pool[cursor]
            cursor += 1
            sid, sha, orid = r["space_id"], r["sha"], r["orid"]
            rec = {"band": band, "space_id": sid, "orid": orid, "pinned_sha": sha,
                   "rank_in_band": cursor, "in_pilot": sid in prior}
            cand = by_key.get((sid, sha), [])
            if len(cand) > 1:
                cand = [c for c in cand if c.get("judged_at") == r["judged_at"]] or cand
            if not cand:
                rec.update(status="no_archived_record", chars=0)
                meta.append(rec); subs.append((band, sid, "no_archived_record")); continue
            arch = cand[0]
            paper = papers.get(str(orid))
            if paper is None:
                rec.update(status="orid_not_in_index", chars=0)
                meta.append(rec); subs.append((band, sid, "orid_not_in_index")); continue
            try:
                h = head_sha(sid)
                rec["head_sha"] = h
                rec["head_moved"] = (h is not None and h != sha)
                md = read_logbook_markdown(sid, revision=sha)
            except Exception as e:
                if sid in prior:                      # keep the superset intact
                    p = prior[sid]
                    staged.append(dict(p, band=band))
                    rec.update(status="ok_reused_pilot", chars=0, n_claims=p["n_claims"],
                               prompt_chars=len(p["prompt"]), truncated=None, title_matches=None)
                    meta.append(rec); reused.append(sid); taken += 1; continue
                rec.update(status="fetch:%s" % type(e).__name__, chars=0)
                meta.append(rec); subs.append((band, sid, type(e).__name__)); continue
            if not md.strip():
                rec.update(status="empty_logbook", chars=0)
                meta.append(rec); subs.append((band, sid, "empty_logbook")); continue

            claims = [{"text": c["claim"]} for c in arch["claims"]]
            prompt = sp.judge_prompt(paper, claims, md)
            if sid in prior and prompt != prior[sid]["prompt"]:
                mismatches.append((sid, len(prior[sid]["prompt"]), len(prompt)))
            staged.append({"space_id": sid, "orid": orid, "sha": sha, "band": band,
                           "n_claims": len(claims),
                           "claims": [c["text"] for c in claims],
                           "archived_verdicts": [c.get("verdict") for c in arch["claims"]],
                           "prompt": prompt})
            rec.update(status="ok", chars=len(md),
                       truncated="[... page truncated for length ...]" in md,
                       title_matches=(paper.get("title") == arch.get("paper_title")),
                       n_claims=len(claims), prompt_chars=len(prompt))
            meta.append(rec)
            taken += 1
        print("  %-8s staged %d/%d (scanned %d)" % (band, taken, per_band, cursor), flush=True)

    if mismatches:
        print("\nFATAL: %d pilot prompts did not rebuild byte-identically:" % len(mismatches))
        for sid, a, b in mismatches:
            print("  %-55s pilot %d chars -> rebuilt %d" % (sid[:55], a, b))
        print("The pilot and extension are not the same instrument. Not writing outputs.")
        return 1

    overlap = [s for s in staged if s["space_id"] in prior]
    print("\npilot overlap: %d logbooks, all prompts byte-identical" % len(overlap))
    if reused:
        print("reused pilot prompt (refetch failed): %d -> %s" % (len(reused), reused))

    json.dump(staged, open(os.path.join(HERE, "arm_prompts.json"), "w"))
    json.dump(meta, open(os.path.join(HERE, "arm_fetch_meta.json"), "w"), indent=1)
    with open(os.path.join(HERE, "arm_set.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["band", "space_id", "orid", "sha", "n_claims", "logbook_chars",
                    "prompt_chars", "truncated", "in_pilot"])
        for s in staged:
            m = next(x for x in meta if x["space_id"] == s["space_id"]
                     and x["status"] in ("ok", "ok_reused_pilot"))
            w.writerow([s["band"], s["space_id"], s["orid"], s["sha"], s["n_claims"],
                        m["chars"], m["prompt_chars"], m["truncated"], m["in_pilot"]])

    ok = [m for m in meta if m["status"] in ("ok", "ok_reused_pilot")]
    new = [s for s in staged if s["space_id"] not in prior]
    print("\nstaged %d logbooks | %d claims | failures %d"
          % (len(staged), sum(s["n_claims"] for s in staged), len(meta) - len(ok)))
    print("NEW to judge: %d logbooks | %d claims | %d calls for 2 replicates"
          % (len(new), sum(s["n_claims"] for s in new), 2 * len(new)))
    fetched = [m for m in ok if m["status"] == "ok"]
    print("titles matching archived paper_title: %d/%d"
          % (sum(1 for m in fetched if m["title_matches"]), len(fetched)))
    print("HEAD moved since judging: %d/%d" % (sum(1 for m in fetched if m.get("head_moved")), len(fetched)))
    print("logbooks hitting the 120k truncation cap: %d" % sum(1 for m in fetched if m["truncated"]))
    print("every prompt embeds its logbook: %s" % all(s["prompt"].count("===== FILE ") >= 1 for s in staged))
    if subs:
        print("\nsubstitutions (%d):" % len(subs))
        for b, sid, why in subs:
            print("  %-8s %-55s %s" % (b, sid[:55], why))
    return 0 if len(staged) == per_band * len(order) else 1


if __name__ == "__main__":
    sys.exit(main())
