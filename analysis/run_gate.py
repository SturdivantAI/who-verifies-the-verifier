#!/usr/bin/env python3
"""Execute the 10-logbook schema verification gate.

Inputs are fully staged: gate_prompts.json holds the assembled prompts (archived
claim lists, pinned-sha logbook content, paper metadata from the challenge index),
recovered_prompt_verbatim.txt holds the byte-exact JUDGE_SYSTEM.

Call parameters replicate app.py::call_judge exactly: temperature 0.1,
max_tokens 8000 doubling on the single retry, retry triggered only by failure to
extract JSON. No structured-output mode, matching the original run.

    HF_TOKEN=... python run_gate.py          -> gate_raw.json, gate_results.json

Paths resolve relative to this file, not the working directory.

Requires inference credits on the HF account (~$0.14 for 10 logbooks).
"""
import hashlib, json, os, re, sys, time
from pathlib import Path
import concurrent.futures as cf
import httpx

# All inputs and outputs live beside this script (data/icml2026-analysis/), so the
# gate can be invoked from any working directory.
HERE = Path(__file__).resolve().parent

ROUTER = "https://router.huggingface.co/v1/chat/completions"
MODEL = "zai-org/GLM-5.2"
# Intended weights revision. NOT enforceable: the router rejects both
# "<model>@<sha>" (400 model does not exist) and "<model>:<sha>" (400 invalid
# provider). Recorded for provenance only; verify the served build separately.
INTENDED_REVISION = "b4734de4facf877f85769a911abafc5283eab3d9"
MAX_TOKENS, ATTEMPTS = 8000, 2
VERDICT_VALUES = {"verified", "falsified", "toy", "inconclusive"}
TOK = os.environ["HF_TOKEN"]
# The system message MUST come from the bare-text file, not from
# recovered_prompt_verbatim.txt -- that archive is a human-readable document
# (title, the system message, the judge_prompt source, endpoint metadata), so
# reading it whole would send 3,947 chars of mixed content as the system role
# and the gate would measure a different instrument. Checksum-gated.
SYSTEM_SHA256 = "9c714851ec1373cb4ce931c83fc06622681d109da4339adcaefd2442260b407e"
SYSTEM = open(HERE / "judge_system_verbatim.txt").read()
_got = hashlib.sha256(SYSTEM.encode()).hexdigest()
if _got != SYSTEM_SHA256:
    sys.exit(f"FATAL: system message checksum mismatch\n  expected {SYSTEM_SHA256} (1783 chars)\n"
             f"  got      {_got} ({len(SYSTEM)} chars)\nRefusing to run: the instrument is not verbatim.")


def call_judge(prompt):
    last = None
    meta = {}
    for attempt in range(1, ATTEMPTS + 1):
        t0 = time.time()
        r = httpx.post(
            ROUTER,
            headers={"Authorization": f"Bearer {TOK}"},
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "max_tokens": MAX_TOKENS * attempt,
            },
            timeout=600,
        )
        if r.status_code != 200:
            return None, {"http": r.status_code, "body": r.text[:300]}, f"HTTP {r.status_code}"
        j = r.json()
        ch = j["choices"][0]
        meta = {
            "attempt": attempt,
            "secs": round(time.time() - t0, 1),
            "model": j.get("model"),
            "resp_id": j.get("id"),
            "fingerprint": j.get("system_fingerprint"),
            "provider": r.headers.get("x-inference-provider"),
            "finish_reason": ch.get("finish_reason"),
            "usage": j.get("usage"),
        }
        content = ch.get("message", {}).get("content") or ""
        m = re.search(r"\{[\s\S]*\}", content)
        if m:
            try:
                return json.loads(m.group(0)), meta, None
            except json.JSONDecodeError as e:
                last = f"JSONDecodeError: {e}"
        else:
            last = f"no JSON (finish_reason={ch.get('finish_reason')})"
    return None, meta, last


def grade(raw, claims):
    """Pass criterion: the judge's JSON must supply the three logbook-level
    fields the harness does not synthesise (claims, overall, quality) and the
    three claim-level fields (claim, verdict, evidence), with one entry per
    claim, indices 1..n exactly once, and every verdict in the label set."""
    checks = {}
    checks["is_object"] = isinstance(raw, dict)
    checks["has_claims"] = isinstance(raw.get("claims"), list)
    checks["has_overall"] = isinstance(raw.get("overall"), str) and bool(raw.get("overall"))
    checks["has_quality"] = str(raw.get("quality", "")).split()[0].lower() in {"high", "medium", "low"} if raw.get("quality") else False
    items = raw.get("claims") or []
    checks["claim_count"] = len(items) == len(claims)
    idx = []
    for it in items:
        try:
            idx.append(int(it.get("claim")))
        except (TypeError, ValueError):
            pass
    checks["indices_complete"] = sorted(idx) == list(range(1, len(claims) + 1))
    checks["fields_present"] = all(
        isinstance(it, dict) and {"claim", "verdict", "evidence"} <= set(it) for it in items
    )
    checks["verdicts_in_set"] = all(
        str(it.get("verdict", "")).lower() in VERDICT_VALUES for it in items
    )
    checks["evidence_nonempty"] = all(str(it.get("evidence", "")).strip() for it in items)
    # the silent-backfill defect: would normalize_verdicts invent a verdict?
    checks["no_silent_backfill"] = checks["indices_complete"] and checks["claim_count"]
    return checks


def main():
    jobs = json.load(open(HERE / "gate_prompts.json"))

    def one(j):
        raw, meta, err = call_judge(j["prompt"])
        rec = {"space_id": j["space_id"], "orid": j["orid"], "sha": j["sha"],
               "n_claims": j["n_claims"], "raw": raw, "meta": meta, "error": err}
        rec["checks"] = grade(raw, j["claims"]) if raw is not None else None
        rec["pass"] = bool(rec["checks"]) and all(rec["checks"].values())
        return rec

    with cf.ThreadPoolExecutor(4) as ex:
        out = list(ex.map(one, jobs))
    json.dump(out, open(HERE / "gate_raw.json", "w"), indent=1)

    print(f"{'space_id':<60} {'n':>2}  {'pass':<5} failures")
    for r in out:
        fails = [k for k, v in (r["checks"] or {}).items() if not v] if r["checks"] else [r["error"]]
        print(f"{r['space_id'][:58]:<60} {r['n_claims']:>2}  {str(r['pass']):<5} {','.join(map(str, fails)) or '-'}")
    npass = sum(r["pass"] for r in out)
    print(f"\nGATE: {npass}/{len(out)} pass")
    print("served model strings:", {r["meta"].get("model") for r in out})
    print("intended revision (unenforceable at router):", INTENDED_REVISION)
    json.dump({"pass": npass, "total": len(out), "intended_revision": INTENDED_REVISION,
               "revision_enforced": False}, open(HERE / "gate_results.json", "w"), indent=1)
    return 0 if npass == len(out) else 1


if __name__ == "__main__":
    sys.exit(main())
