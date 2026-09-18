# 10-Logbook Schema Verification Gate — staged, blocked at execution

**Status: NOT RUN. 0 of 10 logbooks judged.** The gate is fully assembled and validated; it failed at the inference call, not at any preparation step. No gate result is reported below because none was produced.

## Blocker

`HTTP 402` from `router.huggingface.co` on every substantive call:

> You have depleted your monthly included credits. Purchase pre-paid credits to continue using Inference Providers.

The token itself is fine — `whoami-v2` authenticates, role `read`, and an 8-token probe returned `200` with content before the balance ran out. This is a billing limit, not a credential or permission problem. **Estimated cost to complete: $0.14** (55,774 input tokens @ $1.40/M + ~15,000 output @ $4.40/M). Add pre-paid credits or a PRO subscription and `python run_gate.py` finishes it unattended.

## Per-logbook status

All ten fail at the identical point, so there is nothing to disaggregate on the outcome side. What differs is the staged payload:

| Space | Claims | Input tokens | Status |
|---|---|---|---|
| `ICML-2026-agent-repro/repro-why-linear-rnns-more-parallelizable` | 6 | 3,458 | blocked, HTTP 402 |
| `vimarsh/repro-why-linear-rnns-more-parallelizable` | 6 | 3,458 | blocked, HTTP 402 |
| `AceVikings/repro-13581-nb2-lr-optimization` | 6 | 2,193 | blocked, HTTP 402 |
| `AceVikings/repro-a-sketch-and-project-analysis-of-subsampled-natural-gradient-algorithms` | 6 | 2,193 | blocked, HTTP 402 |
| `ICML-2026-agent-repro/repro-sgera-stein-guided-ecg-report-alignment…` | 3 | 3,522 | blocked, HTTP 402 |
| `bsenst/repro-sgera-stein-guided-ecg-report-alignment…` | 3 | 3,522 | blocked, HTTP 402 |
| `bsenst/Time-Conditioned-Foreseeing-An-EHR-Specific-Foundation-Model` | 3 | 7,182 | blocked, HTTP 402 |
| `bsenst/working` | 3 | 7,182 | blocked, HTTP 402 |
| `arthrod/repro-mmbert-annealed-multilingual-encoder` | 6 | 11,532 | blocked, HTTP 402 |
| `arthrod/repro-mmbert-annealed-multilingual-encoder-revision` | 6 | 11,532 | blocked, HTTP 402 |

Machine-readable: `gate_status.csv`. Prompts: `gate_prompts.json`.

## What was completed

**Prompts assembled and verified.** Each is `judge_prompt()` from `app.py` reproduced verbatim, filled with: paper title/orid/authors from the challenge `index.json` (all 10 resolved, and **all 10 titles match the archived `paper_title`**); the **archived** claim list from `verdicts.json` in recorded order; logbook markdown re-fetched at the pinned `sha` through the harness's own serialiser. Using archived rather than live claims is deliberate — the claim list moved between July eras, so pulling live claims would reintroduce that confound into a test meant to isolate the judge. No logbook approaches the 120,000-character truncation cap. Prompts are byte-identical within each duplicate-`sha` pair, which is the retest condition.

**Call parameters replicate the harness.** `temperature = 0.1`, `max_tokens = 8000` doubling to 16000 on a single retry, retry triggered only by failure to regex-extract JSON, no `response_format`.

**Pass criterion derived from the corpus and calibrated against it.** The nine logbook-level fields in `verdicts.json` for these same ten records are `claims, judged_at, model, orid, overall, paper_title, quality, sha, space_id`; the three claim-level fields are `claim, verdict, evidence`. Of the nine, the judge supplies only **three** — `claims`, `overall`, `quality` — and the harness synthesises the other six (`judged_at`, `model`, `orid`, `paper_title`, `sha`, `space_id`). All three claim-level fields are judge-supplied. The gate therefore tests the three-plus-three the model is actually responsible for, and additionally that claim indices are `1..n` exactly once, verdicts fall in `{verified, falsified, toy, inconclusive}`, and evidence strings are non-empty.

That last pair of checks matters because of the `normalize_verdicts` defect: a claim the judge omits is silently backfilled as `inconclusive` with empty evidence, so an incomplete index set would otherwise pass unnoticed as data.

**The criterion is calibrated, not merely asserted.** Reconstructing judge-shaped JSON from the archived records and grading it gives **10/10 pass, with no check failing on any record**. A failure on fresh output is therefore a real change in model behaviour, not a mis-specified gate.

## Revision pinning: recorded, not enforceable

`b4734de4facf877f85769a911abafc5283eab3d9` verified on the Hub — 2026-07-02, "add moe_router_dtype config", the last substantive commit before the corpus window; the 2026-09-01 commit is README-only, as expected. But the router accepts only a bare repo id: `@sha` returns 400 "does not exist" and `:sha` is parsed as a provider name. The pin is documentary. `run_gate.py` captures the served `model` string, response id, `system_fingerprint` and routed-provider header instead, which is the strongest provenance this endpoint offers. Detail and consequences in `protocol_rejudgment.md` §0.2.

## To finish

```
HF_TOKEN=... python run_gate.py     # ~$0.14, writes gate_raw.json + gate_results.json
```

Prints per-logbook pass/fail with named failing checks before the aggregate, then the served model strings. Recommended order after it passes: 10-logbook gate → 10-group positive control (24 verified pairs) → 60-logbook pilot for ICC → main arm.
