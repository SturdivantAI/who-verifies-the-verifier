#!/usr/bin/env python3
"""Run one replicate of the 60-logbook ICC pilot.

    HF_TOKEN=... python run_pilot.py 1     -> pilot_rep1_raw.json
    HF_TOKEN=... python run_pilot.py 2     -> pilot_rep2_raw.json

Imports run_gate rather than reimplementing it. That is deliberate: the
system-message checksum assertion fires at import, so a replicate cannot run
against a drifted instrument, and call_judge/grade are shared verbatim with the
executed gate and control arms.

ONE DELIBERATE DEVIATION from the gate: the provider is pinned.

    gate/control:  model="zai-org/GLM-5.2"          -> router picks; 8 providers
                                                       serve this model live and
                                                       baseten was observed, not
                                                       guaranteed.
    pilot:         model="zai-org/GLM-5.2:baseten"  -> pinned.

Pinning fixes the served build and the billing rate for the run. Weights
revision remains unpinnable (the router rejects both @sha and :sha), so
INTENDED_REVISION is still provenance-only.

Refuses to overwrite an existing replicate file.
"""
import json, os, sys
from pathlib import Path
import concurrent.futures as cf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_gate as rg  # noqa: E402  -- checksum assertion fires here

PROVIDER = "baseten"
rg.MODEL = f"zai-org/GLM-5.2:{PROVIDER}"
WORKERS = 4  # matches the gate and control runs; avoids provider rate limiting


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("usage: run_pilot.py <replicate-number>")
    rep = int(sys.argv[1])
    out_path = HERE / f"pilot_rep{rep}_raw.json"
    if out_path.exists():
        sys.exit(f"refusing to overwrite {out_path.name} ({out_path.stat().st_size} bytes)")

    jobs = json.load(open(HERE / "pilot_prompts.json"))
    print(f"replicate {rep}: {len(jobs)} logbooks, "
          f"{sum(j['n_claims'] for j in jobs)} claims, model {rg.MODEL}", flush=True)

    def one(j):
        raw, meta, err = rg.call_judge(j["prompt"])
        rec = {"space_id": j["space_id"], "orid": j["orid"], "sha": j["sha"],
               "band": j["band"], "n_claims": j["n_claims"], "replicate": rep,
               "raw": raw, "meta": meta, "error": err}
        rec["checks"] = rg.grade(raw, j["claims"]) if raw is not None else None
        rec["pass"] = bool(rec["checks"]) and all(rec["checks"].values())
        return rec

    with cf.ThreadPoolExecutor(WORKERS) as ex:
        out = list(ex.map(one, jobs))
    json.dump(out, open(out_path, "w"), indent=1)

    for r in out:
        # sort by claim index: the model does not always return its claims array
        # in index order, and an unsorted print makes identical runs look divergent.
        if r["raw"]:
            v = [c.get("verdict") for c in
                 sorted(r["raw"].get("claims", []), key=lambda c: int(c.get("claim", 0)))]
        else:
            v = r["error"]
        print(f"  {r['band']:<7} {r['space_id'][:44]:<46} {str(r['pass']):<5} {v}", flush=True)

    npass = sum(r["pass"] for r in out)
    provs = {r["meta"].get("provider") for r in out}
    models = {r["meta"].get("model") for r in out}
    errs = [r for r in out if r["error"]]
    print(f"\nreplicate {rep}: {npass}/{len(out)} schema-pass -> {out_path.name}")
    print("providers served:", provs, "| model strings:", models)
    print("pin honoured:", provs == {PROVIDER})
    if errs:
        print("errors:", [(r["space_id"], r["error"]) for r in errs])
    usage = [r["meta"].get("usage") or {} for r in out if r["meta"].get("usage")]
    print("tokens: prompt %d | completion %d | cached %d" % (
        sum(u.get("prompt_tokens", 0) for u in usage),
        sum(u.get("completion_tokens", 0) for u in usage),
        sum((u.get("prompt_tokens_details") or {}).get("cached_tokens", 0) for u in usage)))
    return 0 if npass == len(out) else 1


if __name__ == "__main__":
    sys.exit(main())
