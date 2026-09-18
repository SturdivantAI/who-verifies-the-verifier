#!/usr/bin/env python3
"""Run one replicate of the extended re-judgment arm (option B).

    HF_TOKEN=... python run_arm.py 1     -> arm_rep1_raw.json
    HF_TOKEN=... python run_arm.py 2     -> arm_rep2_raw.json

Judges ONLY the logbooks the pilot has not already judged. The extension is a
superset of the pilot by construction (stage_arm walks the same draw order and
asserts the overlapping prompts rebuild byte-identically), so the pilot's 120
paid calls are reused rather than repeated.

Imports run_pilot, which imports run_gate. Both are deliberate: the
system-message checksum assertion fires at run_gate import so a replicate
cannot run against a drifted instrument, and the provider pin, call path and
grading come from run_pilot verbatim -- identical to the executed pilot.

Prints a progress marker every 25 calls and detail only for failures; the
per-logbook record lives in the JSON, not in stdout.

Refuses to overwrite an existing replicate file.
"""
import json, sys, time
from pathlib import Path
import concurrent.futures as cf
import threading

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_pilot as rp  # noqa: E402  -- pins provider; imports run_gate -> checksum
import run_gate as rg   # noqa: E402


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("usage: run_arm.py <replicate-number>")
    rep = int(sys.argv[1])
    out_path = HERE / f"arm_rep{rep}_raw.json"
    if out_path.exists():
        sys.exit(f"refusing to overwrite {out_path.name} ({out_path.stat().st_size} bytes)")

    allj = json.load(open(HERE / "arm_prompts.json"))
    prior = {p["space_id"] for p in json.load(open(HERE / "pilot_prompts.json"))}
    jobs = [j for j in allj if j["space_id"] not in prior]
    assert len(jobs) + len(prior & {j["space_id"] for j in allj}) == len(allj), "partition mismatch"
    print(f"replicate {rep}: arm has {len(allj)} logbooks, {len(prior)} already judged by the pilot")
    print(f"judging {len(jobs)} new logbooks, {sum(j['n_claims'] for j in jobs)} claims, "
          f"model {rg.MODEL}, {rp.WORKERS} workers", flush=True)

    done = [0]
    lock = threading.Lock()
    t0 = time.time()

    def one(j):
        raw, meta, err = rg.call_judge(j["prompt"])
        rec = {"space_id": j["space_id"], "orid": j["orid"], "sha": j["sha"],
               "band": j["band"], "n_claims": j["n_claims"], "replicate": rep,
               "raw": raw, "meta": meta, "error": err}
        rec["checks"] = rg.grade(raw, j["claims"]) if raw is not None else None
        rec["pass"] = bool(rec["checks"]) and all(rec["checks"].values())
        with lock:
            done[0] += 1
            if done[0] % 25 == 0 or done[0] == len(jobs):
                print("  %3d/%d  %.1f min elapsed" % (done[0], len(jobs), (time.time() - t0) / 60),
                      flush=True)
        return rec

    with cf.ThreadPoolExecutor(rp.WORKERS) as ex:
        out = list(ex.map(one, jobs))
    json.dump(out, open(out_path, "w"), indent=1)

    npass = sum(r["pass"] for r in out)
    provs = {r["meta"].get("provider") for r in out}
    fails = [r for r in out if not r["pass"]]
    print(f"\nreplicate {rep}: {npass}/{len(out)} schema-pass -> {out_path.name}")
    print("wall: %.1f min | providers served: %s | pin honoured: %s"
          % ((time.time() - t0) / 60, provs, provs == {rp.PROVIDER}))
    if fails:
        print("failures (%d):" % len(fails))
        for r in fails:
            nret = len((r["raw"] or {}).get("claims", [])) if r["raw"] else None
            print("  %-46s expected %d claims, returned %s | checks %s | err %s"
                  % (r["space_id"][:46], r["n_claims"], nret, r["checks"], r["error"]))
    usage = [r["meta"].get("usage") or {} for r in out if r["meta"].get("usage")]
    print("tokens: prompt %d | completion %d | cached %d" % (
        sum(u.get("prompt_tokens", 0) for u in usage),
        sum(u.get("completion_tokens", 0) for u in usage),
        sum((u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) for u in usage)))
    return 0 if npass == len(out) else 1


if __name__ == "__main__":
    sys.exit(main())
