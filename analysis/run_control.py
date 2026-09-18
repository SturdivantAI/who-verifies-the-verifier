#!/usr/bin/env python3
"""Run one fresh replicate of the 26-logbook positive control arm.

The runnable control arm is 10 logbooks (5 duplicate-sha groups), which is
exactly the set staged in gate_prompts.json -- so this script reuses those
prompts verbatim rather than re-staging. The other 8 of the 13 groups are not
runnable: 3 have a logbook deleted from the Hub, 5 have byte-identical logbooks
judged against disjoint claim lists (claim-set drift), so no pair exists.

Replicate 1 IS the gate run (gate_raw.json) -- the calls are identical, so it is
reused rather than repeated. This script produces replicate 2 onward.

Call parameters replicate app.py::call_judge exactly, as run_gate.py does:
temperature 0.1, max_tokens 8000 doubling on the single retry, retry only on
failure to extract JSON.

    HF_TOKEN=... python run_control.py 2      -> control_rep2_raw.json

Writes to control_rep<N>_raw.json and never touches gate_raw.json, so the
gate record is preserved. Paths resolve relative to this file.

~$0.14 per replicate (10 logbooks).
"""
import json, sys
from pathlib import Path
import concurrent.futures as cf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
# Reuse the verified instrument: run_gate.py performs the checksum assertion on
# judge_system_verbatim.txt at import, so importing it is what guarantees this
# replicate uses the same byte-exact system message as the gate.
import run_gate as G


def main():
    rep = sys.argv[1] if len(sys.argv) > 1 else "2"
    out_path = HERE / f"control_rep{rep}_raw.json"
    if out_path.exists():
        sys.exit(f"FATAL: {out_path.name} exists. Refusing to overwrite a replicate.")
    jobs = json.load(open(HERE / "gate_prompts.json"))

    def one(j):
        raw, meta, err = G.call_judge(j["prompt"])
        rec = {"space_id": j["space_id"], "orid": j["orid"], "sha": j["sha"],
               "n_claims": j["n_claims"], "replicate": rep,
               "claims": j["claims"], "raw": raw, "meta": meta, "error": err}
        rec["checks"] = G.grade(raw, j["claims"]) if raw is not None else None
        rec["pass"] = bool(rec["checks"]) and all(rec["checks"].values())
        return rec

    with cf.ThreadPoolExecutor(4) as ex:
        out = list(ex.map(one, jobs))
    json.dump(out, open(out_path, "w"), indent=1)

    print(f"replicate {rep}: {sum(r['pass'] for r in out)}/{len(out)} schema-pass")
    for r in out:
        # sort by claim index: the model does not always return the array in
        # index order, and printing it as returned makes replicates that are in
        # fact identical look like they disagree.
        v = ([c.get("verdict") for c in sorted((r["raw"] or {}).get("claims", []),
                                               key=lambda c: int(c.get("claim", 0)))]
             if r["raw"] else r["error"])
        print(f"  {r['space_id'][:56]:<58} {r['n_claims']:>2}  {v}")
    print("served model strings:", {r["meta"].get("model") for r in out})
    print("providers:", {r["meta"].get("provider") for r in out})
    print("wrote", out_path.name)
    return 0 if all(r["pass"] for r in out) else 1


if __name__ == "__main__":
    sys.exit(main())
