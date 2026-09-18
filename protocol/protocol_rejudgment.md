# Re-Judgment Protocol: Test–Retest Reliability of zai-org/GLM-5.2 on the ICML-2026 Verdict Corpus

Methods section for the experiment that replaces the n = 34 same-`sha` estimate (α = 0.953, CI [0.840, 1.000]) with a properly powered test–retest coefficient. Machine-readable companions: `rejudgment_sample.csv` (the drawn sample, 466 rows), `rejudgment_design.json`, `rejudgment_power.csv`, `rejudgment_allocation.csv`, `rejudgment_cost.csv`, `rejudgment_walltime.csv`.

---

## 0. Prompt provenance — BLOCKER RESOLVED 2026-09-11

> **Resolved.** The prompt was recovered verbatim from the harness Space `ICML-2026-agent-repro/logbook-judge` at commit `dc9028dc8ce6e2017a5a252179706d40400490ea`. Verbatim text, decoding parameters, and the fidelity analysis are in `prompt_recovery_report.md`; the archival copy is `recovered_prompt_verbatim.txt` (system message `sha256 9c714851ec1373cb…`, 1,783 chars as sent). **Use that file, not any transcription.** Key facts that change this protocol: `temperature = 0.1` with **no seed** (so retest is meaningful); `max_tokens` 8000 rising to 16000 on the single retry; no `response_format` — JSON is regex-extracted; `MAX_LOGBOOK_CHARS = 120_000`; the model string carries **no revision pin**. The prompt at `main` is byte-identical to the one in force for 6,385 of 6,398 logbooks (99.80%), and **0 of the 466 sampled logbooks** fall outside that era, so `rejudgment_sample.csv` stands as drawn. Pinned snapshot reference for the methods section: source commit `dc9028d`, deadline-cutoff commit `d0cfe3a` (`SUBMISSION_DEADLINE = 2026-08-03T11:59:59+00:00`).
>
> The subsection below is retained as the record of what had to be recovered and why.

### 0.2 Pinned inference revision — recorded, but NOT enforceable

**Pinned revision for all re-judgment runs: `b4734de4facf877f85769a911abafc5283eab3d9` (`b4734de4facf`, 2026-07-02, "add moe_router_dtype config").** Verified against `zai-org/GLM-5.2` on the Hub: it is the last substantive model commit before the corpus window, and the only later commit (`cf457fa734ab`, 2026-09-01) is "Update README.md" — no weights or config change. So the served build should be unchanged across the corpus window and today.

**The router cannot enforce it, and the protocol must say so.** `https://router.huggingface.co/v1/chat/completions` routes to third-party inference providers and accepts only a bare repo id. Probed directly:

| Model string | Result |
|---|---|
| `zai-org/GLM-5.2` | `200` |
| `zai-org/GLM-5.2@b4734de4facf87…` | `400` — "The requested model … does not exist" |
| `zai-org/GLM-5.2:b4734de4facf` | `400` — the suffix is parsed as a provider/policy name, not a revision |

The revision is therefore **documentary, not operative**: it records which weights the corpus *should* correspond to, and it cannot pin what the provider actually serves. Three consequences for §4 and §6:

1. Record per call the `model` string, response `id`, `system_fingerprint` (when present), and the routed provider header. That is the only provenance actually obtainable, and it is weaker than a revision pin. `run_gate.py` already captures all four.
2. **Do not attribute a fresh-vs-archived discrepancy to "revision drift" — that hypothesis is now untestable at this endpoint.** Since the only post-window commit is a README edit, a discrepancy more plausibly reflects provider-side serving changes (quantisation, kernel, or backend swap) than a weights change. State it that way.
3. If revision-level control is required for the thesis claim, the run has to move off the router to a provider that exposes a revision parameter, or to self-hosted weights at `b4734de4facf87…`. That is a cost and scope decision, not a protocol detail.

### 0.1 The original blocker: the prompt is not in the corpus

`verdicts.json` carries exactly nine logbook-level fields — `space_id`, `orid`, `paper_title`, `sha`, `judged_at`, `model`, `claims`, `overall`, `quality` — and three claim-level fields — `claim`, `verdict`, `evidence`. There is **no** prompt, system-message, template, decoding-parameter, seed, or config field anywhere in the file.

**Requirement 4 ("same prompt as original corpus") therefore cannot be satisfied from the corpus.** The prompt must be recovered from the harness that produced it. §3 gives a reconstruction that is *consistent with* the observed output schema, but a reconstruction is not the original and must not be substituted for it silently. Recover these from the harness repository at the commit that generated the July–August run, and record them in the protocol log:

| Item | Why it must match |
|---|---|
| System message (verbatim bytes) | Dominates verdict-boundary behaviour |
| User-message template + slot order | Position effects are the single largest known judge bias |
| Logbook serialisation (truncation limit, whether code/output/plots are included, ordering) | Determines what the judge actually sees |
| Claim list construction (order, whether claims are numbered) | Order effects across claims within one call |
| `temperature`, `top_p`, `top_k`, `max_tokens`, penalties | Decoding stochasticity is the quantity being measured |
| Seed handling (fixed / absent / per-call) | A fixed seed would make "retest" meaningless |
| Model revision pin | `zai-org/GLM-5.2` appears in all 6,398 logbooks with no revision suffix |
| Structured-output mode (JSON schema / tool-call / free-text + parser) | Changes the output distribution |

**Verification gate.** Before the main run, re-judge 10 logbooks from the control arm (§4) with the recovered prompt and confirm the output *parses into the same schema* and that verdict/quality/evidence-length distributions are consistent with the archived records. If the recovered prompt cannot reproduce the archived schema, stop — the prompt is wrong, and nothing downstream is interpretable.

**Second dependency:** logbook *content* is also absent from the corpus. Only `space_id` (e.g. `abidlabs/wsw7Y085RY`) and `sha` (40-hex) are stored. Input must be re-fetched at the pinned `sha` for each sampled logbook. The `sha` is what makes requirement 4's "same snapshot" exactly satisfiable — 6,385 distinct `sha` across 6,398 logbooks. Any logbook whose `sha` no longer resolves must be recorded as attrition, not silently replaced.

---

## 1. Minimum re-judgment count

**Design.** Each sampled logbook is re-judged **twice** with identical input and prompt, fresh inference both times. The two fresh verdicts for a claim form one test–retest pair. Two fresh runs (rather than fresh-vs-archived) keeps the comparison inside a single time window and avoids confounding retest variance with six weeks of possible provider-side model drift. The archived verdict is retained as a *third* observation for the drift check in §6, at no additional inference cost.

**Power.** Simulation under a latent-true-verdict model (each judgment returns the claim's true verdict with probability 1 − ε, else draws from the corpus marginals: verified .5351, inconclusive .2206, toy .2002, falsified .0441; Σp² = 0.377). For each target α, ε is solved by root-finding, N pairs are simulated 1,500–2,500 times, and the half-width is the larger of |q97.5 − α| and |α − q2.5|.

| True α | ε | D_o | Independent pairs for ±0.05 |
|---|---|---|---|
| 0.50 | 0.293 | 0.311 | 984 |
| 0.60 | 0.225 | 0.249 | 984 |
| 0.667 | 0.183 | 0.207 | 729 |
| 0.75 | 0.134 | 0.156 | 729 |
| 0.85 | 0.078 | 0.093 | 400 |
| 0.953 | 0.024 | 0.029 | 163 |

Required N falls as α rises, so the sample must be sized for the *lowest* α worth distinguishing rather than for the 0.953 point estimate. Sizing at α = 0.953 (163 pairs) would be circular — it assumes the result. **Target: N_eff = 800 independent claim-pairs**, which holds ±0.05 across the whole range α ∈ [0.70, 0.97] (verified by simulation at N = 800: max half-width 0.0453) and degrades only mildly if the truth is as low as 0.60.

**Clustering is the decisive cost factor.** One inference call judges a whole logbook — mean 5.11 claims — so claim-pairs arrive in clusters and are not independent. Measured on the existing 112,380 within-claim pairs, grouped by the unordered logbook-pair that generated them:

> **ICC(disagreement | logbook-pair) = 0.4241** across 20,597 clusters, mean cluster size 5.46.

Disagreement is strongly a property of *which pair of reproduction attempts is being compared*, not of the individual claim — which is independent corroboration of the §5 reframing in `results_evidence_strata.md`. At the realised mean of 5.23 in-scope claims per logbook, DEFF = 1 + 4.23 × 0.4241 = **2.795**.

**Answer to item 1.** 2,302 raw claim-pairs are needed to yield N_eff = 2302 / 2.795 = **824 independent-equivalent pairs**, drawn from **440 logbooks × 2 fresh runs = 880 inference calls**, plus 52 control-arm calls, for **932 fresh re-judgments** total.

*Why clustering makes this cheaper, not dearer.* Assigning one distinct logbook per sampled claim would give near-independent pairs but require ~1,520 calls for the same N_eff — 0.53 effective pairs per call against 0.94 for the clustered design. Bundling wins by ~1.7× even after paying DEFF 2.8.

**Pilot re-estimation (required).** The ICC above is measured on *different-logbook* pairs; the retest condition is same-logbook-twice, where it could differ in either direction. Run the first **60 logbooks** (120 calls) of the primary arm, re-estimate ICC and α, and recompute N as N_raw = 800 × [1 + (n̄ − 1) × ICC_pilot]. If ICC_pilot > 0.50, extend the sample; the `rejudgment_sample.csv` band pools have 136–353 eligible papers each, so all four strata can be extended without replacement.

---

## 2. Stratified sample composition

**m is a paper-level property.** Within-paper spread of m is exactly 0 in 913 of 960 papers (95.1%), and all claims fall in a single m-band in the same 95.1%. Stratification is therefore applied at the **paper** level using the median m of the paper's repeat-judged claims — which is what makes requirement 1 clean rather than approximate.

**Allocation: equal, 110 papers per band, one logbook per paper.**

| Band | Eligible papers | Papers drawn | Logbooks | In-scope claims | Mean claims/logbook |
|---|---|---|---|---|---|
| m = 2 | 353 | 110 | 110 | 541 | 4.92 |
| m = 3–5 | 309 | 110 | 110 | 571 | 5.19 |
| m = 6–10 | 149 | 110 | 110 | 583 | 5.30 |
| m > 10 | 136 | 110 | 110 | 607 | 5.52 |
| **Total** | **947** | **440** | **440** | **2,302** | **5.23** |

**Why equal rather than proportional.** Population shares are 36.0 / 32.8 / 15.8 / 15.4 per cent, so proportional allocation would put only ~68 logbooks in each of the two high-m bands. The primary scientific question is whether test–retest reliability is *uniform across m-bands* — because if it is, the α decline across bands documented in `alpha_decomposition_by_band.csv` is confirmed as purely a chance-baseline artifact rather than the judge degrading on heavily-replicated claims. Equal allocation maximises power for that between-band contrast. For the population-level headline α, post-stratify: weight band b by its population share (0.360, 0.328, 0.158, 0.154) rather than by realised sample size. Report both the equal-weight and post-stratified α.

**Why one logbook per paper.** This is the mechanism that satisfies requirement 1's "avoid overrepresenting high-frequency claims." A hard cap of one logbook per paper means no paper can contribute more than ~5 claim-pairs regardless of how many logbooks reproduce it — papers in the m > 10 band have up to 48 logbooks and would otherwise dominate. It also removes the paper-level component of clustering, leaving only the within-logbook component that DEFF accounts for. Note `5nNNVY8NW4` holds only 8 claims (5 at m > 10, 3 at m = 6–10); the overrepresentation risk is real but comes from logbook count, not claim count, and the cap addresses exactly that.

**Draw.** Deterministic, `random.Random(20260911)`: shuffle eligible papers within band, take the first 110, then pick one logbook uniformly from that paper's logbooks containing ≥1 repeat-judged claim. Realised sample is in `rejudgment_sample.csv` (`arm`, `band`, `orid`, `space_id`, `sha`, `paper_title`, `inscope_claims`, `total_claims`, `judged_at`). Re-running the script reproduces it byte-for-byte.

**Scoring scope.** Judge every claim the logbook contains (the prompt must not be altered to judge a subset — that would change the input). Use only the in-scope claims — those among the 5,081 repeat-judged — for the primary estimate. Out-of-scope claims in the same logbooks give a free secondary sample; report separately.

---

## 3. Prompt template

> **Superseded 2026-09-11.** The verbatim prompt has been recovered from the harness source — use `recovered_prompt_verbatim.txt` and §2–§4 of `prompt_recovery_report.md`. The reconstruction below is retained only as the record of what was inferable from the output schema alone; **do not run it.** For the record of how close it was: it captured the four labels, their definitions, the JSON shape, the independence instruction in the user message, and the three-level quality field — but it missed the system-level CRITICAL INDEPENDENCE RULE paragraph (16% of the real system message), the skepticism framing, the leaderboard point values, and the entire backend-substitution policy, and it guessed no decoding parameters. A run on the reconstruction would have measured a different instrument.

**This was a reconstruction, not the original** — see §0. It was constrained to elicit exactly the schema observed in all 6,398 archived logbooks and offered as a diff target against the harness, not as a substitute for it.

Observed output schema, which any candidate prompt must reproduce:

- per claim: `verdict` ∈ {`verified`, `falsified`, `inconclusive`, `toy`} (nominal, unordered); `evidence` free text, 70–600 chars, mean 312, median 307
- per logbook: `overall` free text, mean 416 chars, max 877; `quality` ∈ {`low`, `medium`, `high`} (realised 1,670 / 2,518 / 2,210)

```
SYSTEM:
You are evaluating whether an autonomous reproduction attempt supports the
claims of a research paper. You will be given the paper's title, a list of
claims extracted from the paper, and the complete logbook of a reproduction
attempt. Judge each claim independently against the evidence in the logbook.

Assign exactly one verdict per claim:
  verified     - the logbook provides evidence at adequate scale that supports the claim
  falsified    - the logbook provides evidence at adequate scale that contradicts the claim
  inconclusive - the logbook does not provide evidence sufficient to decide the claim
  toy          - the logbook tests the claim only at a scale or in a proxy setting too
                 reduced to bear on the claim as stated

Judge only what the logbook demonstrates. Do not credit a claim because it is
plausible or because the paper asserts it. Cite specific numbers, scales, and
run details from the logbook in your justification.

Return JSON only, matching this schema exactly:
{"claims":[{"verdict":"<one of the four>","evidence":"<=600 chars, cites specifics>"}],
 "overall":"<=900 chars summarising what the logbook does and does not establish>",
 "quality":"low|medium|high"}
The "claims" array must have exactly one entry per input claim, in input order.

USER:
PAPER TITLE: {paper_title}

CLAIMS:
1. {claim_1}
2. {claim_2}
...
N. {claim_N}

REPRODUCTION LOGBOOK:
{logbook_content}
```

**Invariants for both runs of a logbook.** Identical bytes in system and user message; identical claim order; identical logbook serialisation; identical decoding parameters; identical model revision. The only difference between run 1 and run 2 is the sampling draw.

---

## 4. Handling the 13 duplicate-`sha` groups

**Exclude from the primary arm; re-run as a separate positive-control arm.**

The 13 groups comprise 26 logbooks across 13 papers — `29sn1uqWn3`, `2iDtIht7W4`, `2iFauBXg7Y`, `68AMoK2YNk`, `IalpB5Mzaz`, `J0y3sNbo9G`, `N9nlCRUiir`, `SGTLVjx3MN`, `cX3r7kAqr1`, `iEtOxzAs51`, `iJDJCO4mji`, `jl2f2Y3iuC`, `rEzGzILnVC` — spread across all four bands (4 / 3 / 2 / 4). All 13 papers are excluded at the *paper* level from the primary frame, which costs 13 of 960 papers and leaves 136–353 eligible per band.

Three reasons:

1. **Independence.** These 34 pairs are the evidence this experiment exists to replace. Including them would make the new estimate partly a function of the old one, so the new CI could not be read as independent confirmation.
2. **Selection bias.** The groups are not a random sample of the corpus — they are largely one author's duplicated or renamed reproduction spaces. That is precisely the non-randomness flagged as the limit on the n = 34 result, and it would propagate into the primary estimate.
3. **They are worth more as a control.** Re-judging all 26 under the new protocol tests whether the protocol reproduces α = 0.953 on the *same* pairs. This is the cleanest available check that the recovered prompt and pinned revision actually match the July–August configuration.

**Control-arm reporting.** 26 logbooks × 2 fresh runs = 52 calls, 105 in-scope claims. Report: (a) fresh-vs-fresh α on the 34 cross-logbook pairs, (b) archived-vs-archived α — which must reproduce 0.953 exactly, since it is a recomputation on stored data, and is the arithmetic check on the pipeline, (c) fresh-vs-archived agreement as the drift signal. Interpretation: if (a) ≈ (b) the protocol is faithful and the primary estimate stands on its own; if (a) ≪ (b), suspect prompt or revision mismatch and re-open §0 before reporting anything.

Do **not** pool the control arm into the primary estimate under any outcome.

---

## 5. Cost and time

**Inference volume.** 932 calls (880 primary + 52 control), plus 120 pilot calls that are a prefix of the primary arm, not an addition.

**Verified rate.** Z.ai list pricing for GLM-5.2 is **$1.40 per 1M input tokens and $4.40 per 1M output tokens**. That is the only rate figure confirmed from retrieval; cheaper third-party routes and any prompt-cache discount are plausible but were **not verified here**, so they are excluded from the estimate rather than assumed. Treat the figures below as an upper bound on the list-price path.

**Output tokens per call**, from corpus text lengths at 4 chars/token: 568 (if claims are not echoed) to 835 (if echoed) visible tokens. GLM-5.2 reasoning tokens bill at the output rate and their volume is **not** recoverable from the corpus — it is the dominant uncertainty. **Input tokens are also unmeasurable from the corpus**, since logbook content is not stored; size them by fetching 20 logbooks at their pinned `sha`, serialising them through the recovered harness path, and tokenising.

Total USD, 932 calls, 835 visible output tokens/call:

| Input tok/call | +0 reasoning | +1k | +3k | +8k |
|---|---|---|---|---|
| 5,000 | $9.95 | $14.05 | $22.25 | $42.76 |
| 15,000 | $23.00 | $27.10 | $35.30 | $55.80 |
| 30,000 | $42.57 | $46.67 | $54.87 | $75.38 |
| 60,000 | $81.71 | $85.81 | $94.02 | $114.52 |

**Cost is not a constraint on this experiment.** The whole grid spans $10–$115. Even the most pessimistic cell is well below the threshold at which sample size would need defending on budget grounds — which means the pilot should be used to refine precision, not to decide affordability. If the pilot shows ICC > 0.50, extend the sample rather than accept a wider CI.

**Wall clock.** Throughput was not verified, so time is given as a formula: `calls × (TTFT + output_tokens / throughput) / concurrency`. Measure TTFT and tokens/s during the 60-logbook pilot and substitute. At concurrency 8, in minutes:

| Reasoning tok | 40 tok/s | 80 tok/s | 150 tok/s |
|---|---|---|---|
| 0 | 42.5 | 22.2 | 12.8 |
| 1,000 | 91.0 | 46.5 | 25.7 |
| 3,000 | 188.1 | 95.0 | 51.6 |
| 8,000 | 430.8 | 216.4 | 116.3 |

Plan for a single working session at concurrency 8–16 under any of these; the run does not need to be broken across days. Budget separate time for re-fetching 466 logbook snapshots, which is network-bound and independent of inference.

**Requirement 5, operationally.** Set `temperature` to the harness value and do not pin a seed. Disable any response-level caching at the client and, if the provider offers it, send a cache-control header that forbids completion reuse; vary a nonce in request metadata (never in the prompt body, which must stay byte-identical). Prompt/KV-prefix caching is *input*-side and does not reuse a completion, but for the primary arm disable it too — it costs little at these volumes and removes the question entirely. Log the full response object including any `cached`/`usage` fields, and assert that no two responses for the same logbook are byte-identical: at mean 835 output tokens, exact repetition indicates cache contamination, not agreement.

---

## 6. What the result resolves, and what gets a v4

**Primary endpoint.** α_retest (nominal, 4 unordered categories), equal-weight and post-stratified, with bootstrap CI resampling **logbooks** — not claims and not pairs — since the logbook is the sampling and clustering unit.

**Secondary endpoints, free with the same calls.** (i) α_retest by m-band, the direct test of whether the band decline is a chance-baseline artifact; (ii) test–retest reliability of `quality`, a 3-level *ordinal* field, so use ordinal-weighted α — a second independent instrument on the same logbook; (iii) fresh-vs-archived agreement, which measures retest variance and six-week drift jointly and is therefore a bound, not a decomposition; (iv) hard-contradiction rate (verified↔falsified) under retest, the direct comparator to the 2.19% per-pair corpus rate.

**Decision rules, fixed in advance.**

| Outcome | Reading |
|---|---|
| α_retest ≥ 0.667 | Judge is reliable under fixed input. The §5 reframing in `results_evidence_strata.md` is confirmed on adequate n. Headline becomes reproduction-pipeline non-determinism. |
| 0.40 ≤ α_retest < 0.667 | Both mechanisms contribute. Neither "unreliable judge" nor "unreliable pipeline" is sufficient alone; the poster must report the decomposition. |
| α_retest < 0.40 | The n = 34 result was an artifact of its non-random groups. Within-judge instability is real and the original framing is substantially rehabilitated. |
| Control arm (a) ≪ (b) | Protocol infidelity. Report nothing; return to §0. |

**Artifact updates.** Four documents currently carry claims that this experiment can move:

1. **`results_evidence_strata.md` → v2.** The substantive rewrite under every outcome. §4a's n = 34 becomes corroborating detail; the powered α replaces it as the primary identical-input figure. §6 ("The limit on all of §4") is deleted and replaced by the realised design and CI. §5's reframing is either confirmed, qualified, or withdrawn per the decision rules.
2. **`results_krippendorff_alpha.md` → v4.** §6.1's superseded banner is rewritten from "resolved against the within-judge framing (n = 34)" to the powered result. §1, §3 and §5 stand as computed regardless — they are arithmetic on stored data and no re-judgment can change them. If α_retest ≥ 0.667, strengthen the §5 statement that 0.229 belongs to the composite logbook+judge instrument rather than to the judge.
3. **`addendum_within_judge_reframing.md` → v2.** Its measurement-issue ranking put the logbook-versus-test-retest confound first. That issue is now closed with a number; re-rank the remainder and mark the first as resolved.
4. **`llm_judge_reliability_review.md` → v3.** The comparator table needs a unit-matched row for our own test–retest α. Critically, the Anghel et al. comparison must be re-labelled: that study held input fixed and perturbed only presentation order, so it is a comparator for α_retest, **not** for the 48.06% cross-logbook figure. Under the first outcome the review gains a genuine apples-to-apples row it currently lacks.

New artifacts from the run: `rejudgment_verdicts.json` (raw responses, both runs, full response objects), `rejudgment_pairs.csv`, `rejudgment_alpha.json`, `rejudgment_by_band.csv`, `rejudgment_control.json`, and a v2 of `fig5_evidence_strata.png` with the powered CI replacing the n = 34 interval.

**What this cannot resolve.** Re-judgment measures the judge's stability under fixed input. It says nothing about the judge's *validity* — whether `verified` means what a domain expert would call verified. That needs human adjudication on a sampled subset and is a separate instrument-validity study, not an extension of this one.
