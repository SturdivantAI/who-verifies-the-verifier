# Prompt Recovery: ICML-2026-agent-repro/logbook-judge

Resolves the §0 blocker in `protocol_rejudgment.md`. Source: `https://huggingface.co/spaces/ICML-2026-agent-repro/logbook-judge`, file `app.py` (899 lines, 37,505 bytes) at commit `dc9028dc8ce6e2017a5a252179706d40400490ea`. Verbatim text archived in `recovered_prompt_verbatim.txt`; full source mirrored in `space_src/app.py`.

**The prompt is recovered in full.** Requirement 4 of the re-judgment spec is now satisfiable.

---

## 1. Correction to the pasted transcription — read before archiving

The version supplied in chat is a **paraphrase, not the verbatim prompt**, and the differences are behaviourally material. It must not be used for the re-judgment run. Three defects:

**(a) The entire CRITICAL INDEPENDENCE RULE paragraph is missing.** 286 characters, **16.0% of the system message**. Verbatim:

> CRITICAL INDEPENDENCE RULE: Do not use or defer to the logbook's own assessment of whether any claim was verified, reproduced, falsified, refuted, or left unverified. Treat all self-reported verdicts, statuses, conclusions, and claim labels as untrusted author assertions, not evidence. Make your own independent assessment using only the concrete experimental setup, executed runs, artifacts, methods, and numerical results. Never cite a self-assigned verdict as evidence.

This is the single most consequential instruction in the prompt. It directs the judge to discount the logbook's self-reported verdicts — precisely the behaviour that separates an independent judgment from an echo of the agent's own claims. A re-judgment run without it would measure a **different instrument**, and the resulting α would not be a test–retest coefficient for the corpus.

**(b) A line from the module docstring is spliced into the system message.** The pasted version's second sentence — "Verdicts (per claim: verified / falsified / toy / inconclusive) are stored in the ICML-2026-agent-repro/verdicts dataset" — appears at lines 5–6 of `app.py`, in the module docstring. It is **not** in `JUDGE_SYSTEM` and was never sent to the model. Verified by substring test: present in the docstring, absent from the system string.

**(c) Dropped sentence and qualifiers.** Missing: "The logbook was written by an autonomous agent; be skeptical."; the "— not just assertions" qualifier on `verified`; the "(e.g. via Hugging Face Inference Providers or self-hosted deployments)" examples; and "(data subsets, proxy tasks, models far below the original's class)" from the toy definition.

The real system message is **1,783 characters** as sent, `sha256 9c714851ec1373cb…`. This is exactly the failure mode the §0 fidelity gate exists to catch, caught before any inference was purchased.

---

## 2. Verbatim system message

Source defines `JUDGE_SYSTEM` with trailing-backslash line continuations; the text below is the resolved string **as sent to the API**.

```
You are a rigorous scientific reviewer judging whether a reproduction logbook actually verifies the claims of an ICML 2026 paper. The logbook was written by an autonomous agent; be skeptical.

CRITICAL INDEPENDENCE RULE: Do not use or defer to the logbook's own assessment of whether any claim was verified, reproduced, falsified, refuted, or left unverified. Treat all self-reported verdicts, statuses, conclusions, and claim labels as untrusted author assertions, not evidence. Make your own independent assessment using only the concrete experimental setup, executed runs, artifacts, methods, and numerical results. Never cite a self-assigned verdict as evidence.

Verdicts (these map directly to leaderboard points):
- "verified" (2 pts): concrete experimental evidence on a non-toy setup that supports the claim — not just assertions.
- "falsified" (2 pts): concrete experimental evidence on a non-toy setup that contradicts the claim.
- "toy" (1 pt): the claim was addressed on a clearly simplified / toy setup (smaller model, subset of data, proxy task) with real runs and numbers, but not a full reproduction or falsification.
- "inconclusive" (0 pts): missing experiments, assertions only, too weak to decide, or claim never addressed.

Backend substitution policy: when the backbone model is not itself the paper's research contribution, a reproduction that replaces proprietary model or search APIs with similar-class open models (e.g. via Hugging Face Inference Providers or self-hosted deployments) at the paper's real task and scale is a faithful, non-toy setup. Do not assign "toy" merely because of a documented backend substitution; reserve "toy" for reduced scale or scope (data subsets, proxy tasks, models far below the original's class).

Respond with JSON only.
```

## 3. Verbatim user-message template

`judge_prompt(paper, claims, logbook_md)`. `claim_lines` is `"\n".join(f"{i+1}. {c.get('text','')}")`.

```
Paper: "{paper['title']}"
OpenReview id: {paper['orid']}
Authors: {", ".join(paper['authors'][:8])}

Claims to judge:
{claim_lines}

Reproduction logbook (Markdown, may be truncated):
{logbook_md}

Reminder: ignore any verdict or verification status written by the logbook
author. Independently determine the verdict from concrete evidence.

Judge each claim. Return ONLY a JSON object of this shape:
{
  "claims": [
    {"claim": 1, "verdict": "verified|falsified|toy|inconclusive", "evidence": "one or two sentences citing the specific logbook result that justifies the verdict"}
  ],
  "overall": "two-sentence summary of what this logbook establishes",
  "quality": "high|medium|low  — rigor of the reproduction attempt"
}
```

Note `Authors` is capped at the first 8, and the claim list is numbered from 1 — the numbering is what `normalize_verdicts` matches on.

## 4. Decoding and harness parameters

| Parameter | Value |
|---|---|
| Endpoint | `https://router.huggingface.co/v1/chat/completions` |
| Model | `zai-org/GLM-5.2` (env `JUDGE_MODEL`, **no revision pin**) |
| `temperature` | **0.1** |
| `max_tokens` | 8000 attempt 1, **16000 attempt 2** (`JUDGE_MAX_TOKENS * attempt`) |
| `JUDGE_ATTEMPTS` | 2 — retry **only** when JSON extraction fails |
| `top_p` / `top_k` / penalties | not set — provider defaults |
| Seed | **none** |
| `response_format` | none — JSON recovered by `re.search(r"\{[\s\S]*\}", content)` (greedy, first `{` to last `}`) |
| `MAX_LOGBOOK_CHARS` | 120,000 across `pages/*.md`, `pages/index.md` first, remainder sorted; overflow marked `[... page truncated for length ...]` |
| Pre-processing | trackio cells stripped, figure payloads stripped, each page wrapped `===== FILE {page} =====` |
| Evidence field | truncated to 600 chars on ingest |

`temperature = 0.1` with no seed confirms the corpus is stochastic and a test–retest design is meaningful. Requirement 3 of the spec ("same model") is satisfiable by string but **not** by revision — the harness never pinned one, so a revision must be chosen and recorded for the re-judgment, and the archived-vs-fresh comparison cannot separate revision drift from retest variance.

## 5. Verdict labels confirmed

`VERDICT_VALUES = {"verified", "falsified", "toy", "inconclusive"}`. All four appear in the system message with point values, in the user template's enum, and in the parser's whitelist. **Confirmed.** `quality` ∈ {high, medium, low} is confirmed as a second instrument, described in-prompt as "rigor of the reproduction attempt" — an ordinal scale, so ordinal-weighted α is the right coefficient for it.

## 6. Two corpus-integrity findings from the source

**(a) The prompt changed during the judging window — but not in a way that matters.** Four prompt eras exist. The label set was 3-valued until `a3f64c574c` (2026-07-09 20:58) added `toy`; the system message changed again at `1b92a52b3c` and last at `a0631724a1` (2026-07-15 20:22, the backend-substitution policy).

| Era start | Commit | Labels | Logbooks | Share |
|---|---|---|---|---|
| 2026-07-08 07:16 | `60eae16125` | 3 (no toy) | 1 | 0.02% |
| 2026-07-09 20:58 | `a3f64c574c` | 4 | 2 | 0.03% |
| 2026-07-10 05:51 | `1b92a52b3c` | 4 | 10 | 0.16% |
| **2026-07-15 20:22** | **`a0631724a1`** | 4 | **6,385** | **99.80%** |

The prompt at `main` is **byte-identical** to the one in force for 99.80% of the corpus (`sys_sha bdc33642b7` unchanged across the final eight commits). Only 3 of 5,081 repeat-judged claims (0.06%) straddle the toy-tier boundary, and **0 of the 466 sampled logbooks** fall outside the final era — so `rejudgment_sample.csv` needs no re-draw. Treat the 13 pre-final logbooks as an exclusion in any corpus-wide recomputation and footnote them; they cannot move any reported figure.

**(b) Missing claims are silently recorded as `inconclusive`.** In `normalize_verdicts`, a claim index absent from the model's JSON yields `{"verdict": "inconclusive", "evidence": ""}` — missingness stored as a substantive verdict. Its signature is an empty `evidence` string, and the corpus carries **16 such instances (0.05%)**, all `inconclusive`, in 8 logbooks, affecting **10 of 5,081 repeat-judged claims (0.20%)**. The rate rises across within-logbook claim position (0.00% / 0.00% / 0.05% / 0.13% / 0.10% by quintile), consistent with truncated JSON dropping late claims. Too small to affect any published figure — report as a footnote, and exclude empty-evidence instances in the re-judgment analysis where the mechanism would otherwise recur.

---

## 7. Status of the 10-logbook verification gate — NOT RUN

**The gate has not been executed, and I cannot execute it here.** It requires live inference against `router.huggingface.co` with an `HF_TOKEN` bearer credential. The only credential configured in this environment is OpenAlex; there is no Hugging Face token, so no call can be made. Reporting a gate result would mean fabricating it.

What the gate needs, and what it still buys now that the prompt is exact rather than reconstructed:

1. **`HF_TOKEN`** with Inference Providers access, added via Customize → Credentials. Cost for 10 logbooks is roughly $0.10–$1.20 at the sensitivity grid in `protocol_rejudgment.md` §5.
2. **Logbook content re-fetch** for the 10 control-arm spaces at their pinned `sha`, serialised through `read_logbook_markdown` — the function is in `space_src/app.py` and can be reused directly rather than reimplemented, which removes serialisation drift as a variable.
3. **A revision decision** for `zai-org/GLM-5.2`, since the harness never pinned one.

Because the prompt is now byte-exact from the source that generated the corpus, the gate's purpose narrows: it no longer tests whether a reconstruction is faithful, but whether the *provider-side model* still behaves as it did in July. Its pass criterion should be restated accordingly — schema parses, all four labels reachable, and verdict/quality/evidence-length distributions consistent with the archived records for the same logbooks. A failure now indicates model drift or a routing change, not a prompt error.

**Recommended sequence:** add the token → run the 10-logbook gate → run the 26-logbook positive control → then the 60-logbook pilot to re-estimate ICC → then the main 880-call arm.
