# Gate failure diagnosis — the blocker is billing, not Space access

**Headline: the reported 401 cannot be a Space-permission error, and all ten gate logbooks are in public Spaces. The gate is blocked on inference credits, and still is.**

## 1. `run_gate.py` never reads a Space

Audited the script: it contains exactly **one** network call and **one** URL.

| Pattern | Occurrences in `run_gate.py` |
|---|---|
| `httpx.post` | 1 |
| `httpx.get` | 0 |
| `huggingface.co/spaces` | 0 |
| `hf_hub_download` | 0 |
| `resolve/` (Hub file download) | 0 |
| `/api/` | 0 |

Only URL: `https://router.huggingface.co/v1/chat/completions`.

Logbook markdown was fetched **during staging** (at each verdict's pinned `sha`) and is embedded in the prompts. Verified: every one of the 10 staged prompts contains its logbook text, so **zero fetches are required at run time**. A `401`/`402` from this script is the inference endpoint refusing the call — nothing in it can produce a Space-permission error.

## 2. Q1 — Space visibility: 10 of 10 are public

Probed each `space_id` **unauthenticated** (`GET /api/spaces/{id}` with no token):

| Result | Count | Notes |
|---|---|---|
| `200` PUBLIC | 8 | directly public |
| `307` redirect → `200` PUBLIC | 2 | renamed Spaces, see below |
| `401`/`403`/private | **0** | none |

**There are no private or restricted Spaces in `gate_set.csv`.** So the premise behind Q1 does not hold, and "rerun on public logbooks only" would be a rerun of the whole set — which is what just ran, and it failed on billing, not access.

**The two 307s are renames, and each redirects to the other member of its own duplicate-`sha` pair:**

- `AceVikings/repro-13581-nb2-lr-optimization` → `AceVikings/repro-a-sketch-and-project-analysis-of-subsampled-natural-gradient-algorithms`
- `bsenst/working` → `bsenst/Time-Conditioned-Foreseeing-An-EHR-Specific-Foundation-Model`

Those two "pairs" are therefore **one Space judged twice under an old and a new name**, not two independent submissions. For a test–retest control this is harmless and arguably ideal — it guarantees identical input, which is what the byte-identity check already found. But it should be stated in the methods: 2 of the 13 duplicate-`sha` groups are rename artefacts, not distinct submissions.

## 3. Current run: HTTP 402 on all ten, not 401

Re-ran the gate after the router began accepting this token again:

```
GATE: 0/10 pass          (every logbook: HTTP 402)
served model strings: {None}
exit: 1
```

A 4-token probe returns `200` with content; every real call (2,193–11,532 input tokens) returns `402`. That is a residual balance large enough for a trivial request and too small for the gate — the same depletion as before, not a credential problem.

**The reported 401 and the observed 402 are different failures.** `whoami-v2` on this token returns `200`, role `read`, classic (non-fine-grained) token. A `401` from the router means the token sent in *that* environment was invalid, expired, or malformed in the header — worth checking whether the shell that produced the 401 had a stale `HF_TOKEN` exported, or a fine-grained token lacking the "Make calls to Inference Providers" permission. Neither code implicates Space access.

## 4. Q2 — the evidence field cannot reconstruct the logbook

Fields present in `verdicts.json` for `bsenst/Time-Conditioned-Foreseeing-An-EHR-Specific-Foundation-Model`:

- **logbook level (9):** `claims, judged_at, model, orid, overall, paper_title, quality, sha, space_id`
- **claim level (3):** `claim, evidence, verdict`
- Field sizes for that record: `overall` 332 chars, `paper_title` 105, `space_id` 67, `sha` 40, `judged_at` 25, `model` 15, `quality` 3. **No field holds bulk text.**

That record's three evidence strings total **1,033 characters against a 27,558-character logbook — 3.75%.**

Across all ten gate logbooks:

| Measure | Value |
|---|---|
| Logbook markdown | 206,892 chars |
| All evidence strings | 13,977 chars |
| Coverage | **6.76%** (range 3.75%–21.50%) |
| Evidence strings that are verbatim logbook slices | **0 of 48** |
| Evidence strings containing markdown structure (headings, code fences, tables) | **0 of 48** |

The evidence field is **judge-authored justification prose**, not extracted logbook text — it paraphrases and summarises ("Five concrete numerical checks on the actual … implementations from the repo confirmed: correct output shapes, identical encodings for concurrent timestamps…"). Zero verbatim overlap and zero markdown structure confirm it is generated, not quoted.

**Conclusion: reconstruction is impossible, and attempting it would invalidate the gate.** Feeding judge-written summaries back to the judge would test whether the model agrees with its own prior conclusions on a 7%-length paraphrase — not whether it reproduces its verdicts on the original input. That is a different experiment with a different, and much more favourable, expected agreement.

**Logbook markdown is available only from the live Space.** That is already done and archived — `control_logbooks.json` holds the markdown fetched at each pinned `sha`, and it is embedded in `gate_prompts.json`. Nothing further needs fetching. Note the corpus is decaying (several mirrors have already been deleted from the Hub), so the archived copies are the durable record.

## What actually unblocks the gate

Pre-paid credits or a PRO subscription on the account whose token runs it — **$0.14** for the ten logbooks. Then, from any directory:

```
HF_TOKEN=<token with inference access> python run_gate.py
```

If that token returns `401`, verify it at `https://huggingface.co/api/whoami-v2` before spending time on the Spaces — a `200` there with a `401` at the router points at inference permissions on a fine-grained token.
