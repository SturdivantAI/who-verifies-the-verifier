#!/usr/bin/env python3
"""Stage the 60-logbook ICC pilot: stratified draw, pinned-sha logbook fetch,
prompt assembly using the byte-exact harness template.

Design decisions, all deliberate:
  * STRATIFIED, not the protocol's literal "first 60" -- rejudgment_sample.csv is
    sorted by band, so the first 60 rows are all m=2 (the least-clustered stratum)
    and would estimate the design-effect input on the one band least able to
    inform it. We take the first 15 of each band IN THE ORDER DRAWN, preserving
    the original random.Random(20260911) draw.
  * ARCHIVED claim lists, not live ones. The harness resolved claims at judging
    time via normalize_verdicts(), which maps index->text and silently backfills
    omissions. Feeding the archived list holds the instrument constant; the
    stored order IS the original prompt order for exactly that reason.
  * Paper metadata from the LOCAL challenge index snapshot, not the live URL,
    so the staging is reproducible. Titles are cross-checked against the
    archived paper_title for every paper.
  * If a logbook cannot be fetched (deleted/private Space, moved sha) we
    substitute the next logbook in the same band's draw order and record the
    substitution. Band quotas are held at 15.
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "rejudgment_sample.csv")
INDEX = os.path.join(HERE, os.pardir, "icml2026-challenge", "index.json")
VERDICTS = os.path.join(HERE, os.pardir, "icml2026-verdicts", "verdicts.json")
PER_BAND = 15

sys.path.insert(0, HERE)
from fetch_logbooks import read_logbook_markdown, head_sha  # noqa: E402


def papers_by_orid(index_data):
    """app.py papers_by_orid: tolerate both index schemas."""
    papers = index_data.get("papers") if isinstance(index_data, dict) else index_data
    if not isinstance(papers, list):
        raise ValueError("challenge index.json must be a list or contain a papers list")
    return {str(p["orid"]): p for p in papers if isinstance(p, dict) and p.get("orid")}


def judge_prompt(paper, claims, logbook_md):
    """app.py judge_prompt, verbatim. `claims` are dicts with a 'text' key."""
    claim_lines = "\n".join(f"{i + 1}. {c.get('text', '')}" for i, c in enumerate(claims))
    return f"""Paper: "{paper.get("title", "(unknown)")}"
OpenReview id: {paper.get("orid")}
Authors: {", ".join(paper.get("authors", [])[:8])}

Claims to judge:
{claim_lines}

Reproduction logbook (Markdown, may be truncated):
{logbook_md}

Reminder: ignore any verdict or verification status written by the logbook
author. Independently determine the verdict from concrete evidence.

Judge each claim. Return ONLY a JSON object of this shape:
{{
  "claims": [
    {{"claim": 1, "verdict": "verified|falsified|toy|inconclusive", "evidence": "one or two sentences citing the specific logbook result that justifies the verdict"}}
  ],
  "overall": "two-sentence summary of what this logbook establishes",
  "quality": "high|medium|low  — rigor of the reproduction attempt"
}}"""


def main():
    rows = [r for r in csv.DictReader(open(SAMPLE)) if r["arm"] == "primary"]
    bands, order = {}, []
    for r in rows:
        bands.setdefault(r["band"], []).append(r)
        if r["band"] not in order:
            order.append(r["band"])
    print("primary arm: %d logbooks across bands %s" % (len(rows), {b: len(v) for b, v in bands.items()}))

    V = json.load(open(VERDICTS))
    recs = list(V.values()) if isinstance(V, dict) else V
    by_key = {}
    for rec in recs:
        by_key.setdefault((rec["space_id"], rec["sha"]), []).append(rec)

    papers = papers_by_orid(json.load(open(INDEX)))
    print("challenge index: %d papers" % len(papers))

    staged, meta, subs = [], [], []
    for band in order:
        pool, taken, cursor = bands[band], 0, 0
        while taken < PER_BAND and cursor < len(pool):
            r = pool[cursor]
            cursor += 1
            sid, sha, orid = r["space_id"], r["sha"], r["orid"]
            rec = {"band": band, "space_id": sid, "orid": orid, "pinned_sha": sha,
                   "arm": "pilot", "rank_in_band": cursor}
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
                rec.update(status="fetch:%s" % type(e).__name__, chars=0)
                meta.append(rec); subs.append((band, sid, type(e).__name__)); continue
            if not md.strip():
                rec.update(status="empty_logbook", chars=0)
                meta.append(rec); subs.append((band, sid, "empty_logbook")); continue

            claims = [{"text": c["claim"]} for c in arch["claims"]]
            prompt = judge_prompt(paper, claims, md)
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
        print("  %-8s staged %d/%d (scanned %d)" % (band, taken, PER_BAND, cursor), flush=True)

    json.dump(staged, open(os.path.join(HERE, "pilot_prompts.json"), "w"))
    json.dump(meta, open(os.path.join(HERE, "pilot_fetch_meta.json"), "w"), indent=1)
    with open(os.path.join(HERE, "pilot_set.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["band", "space_id", "orid", "sha", "n_claims", "logbook_chars", "prompt_chars", "truncated"])
        for s in staged:
            m = next(x for x in meta if x["space_id"] == s["space_id"] and x["status"] == "ok")
            w.writerow([s["band"], s["space_id"], s["orid"], s["sha"], s["n_claims"],
                        m["chars"], m["prompt_chars"], m["truncated"]])

    ok = [m for m in meta if m["status"] == "ok"]
    print("\nstaged %d logbooks | %d claims | failures %d" %
          (len(staged), sum(s["n_claims"] for s in staged), len(meta) - len(ok)))
    print("titles matching archived paper_title: %d/%d" % (sum(1 for m in ok if m["title_matches"]), len(ok)))
    print("HEAD moved since judging: %d/%d" % (sum(1 for m in ok if m.get("head_moved")), len(ok)))
    print("logbooks hitting the 120k truncation cap: %d" % sum(1 for m in ok if m["truncated"]))
    print("every prompt embeds its logbook: %s" % all(s["prompt"].count("===== FILE ") >= 1 for s in staged))
    if subs:
        print("\nsubstitutions (%d):" % len(subs))
        for b, sid, why in subs:
            print("  %-8s %-55s %s" % (b, sid[:55], why))
    return 0 if len(staged) == PER_BAND * len(order) else 1


if __name__ == "__main__":
    sys.exit(main())
