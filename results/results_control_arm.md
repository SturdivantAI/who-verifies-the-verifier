# Positive control arm — executed result

**Verdict: PASS, with a corrected baseline and a stated power limit.** All 48 claim-instances reproduce the archived verdict exactly, in two independent fresh replicates, 45 days after the archived judgments. Reproduced α = 1.000 on the 24 reproducible claim-pairs.

---

## 1. The arm is 10 logbooks, not 26

The design calls for 26 logbooks in 13 duplicate-`sha` groups. **Only 5 groups (10 logbooks, 24 claim-pairs) are runnable.** The other 8 were excluded before any call, for two distinct reasons:

| Exclusion reason | Groups | Logbooks | Archived claim-pairs lost |
|---|---|---|---|
| One logbook of the pair **deleted from the Hub** (corpus decay) | 3 | 3 unfetchable | 10 |
| Byte-identical logbooks judged against **disjoint claim lists** (claim-set drift) | 5 | 10 | 0 (no pair ever existed) |
| **Runnable** | **5** | **10** | **24** |

The 5 drift groups are not a loss of pairs — no claim-pair existed in the archive for them, because `active_claims_map()` resolved a different claim list at each judging time, so the two logbooks were never asked the same questions. The 3 deleted-logbook groups are a real loss, and they are unrecoverable.

**Replicate 1 was already paid for.** The 10 runnable control logbooks are *exactly* the set staged for the schema gate, so the gate run is a complete fresh replicate of this arm. It was reused rather than repeated; only replicate 2 was newly executed (10 calls).

## 2. Per-logbook verdicts, prompt-index order (archived / rep1 / rep2)

| orid | `sha` | logbook | claim verdicts |
|---|---|---|---|
| 29sn1uqWn3 | `09a801d6fb` | repro-why-linear-rnns-more-parallelizable | inco/inco/inco · toy/toy/toy · toy/toy/toy · toy/toy/toy · toy/toy/toy · inco/inco/inco |
| | | vimarsh/…-parallelizable | inco/inco/inco · toy/toy/toy · toy/toy/toy · toy/toy/toy · toy/toy/toy · inco/inco/inco |
| 2iDtIht7W4 | `0c20cb898d` | repro-13581-nb2-lr-optimization | veri ×6, all three conditions |
| | | …sketch-and-project-analysis… | veri ×6, all three conditions |
| iEtOxzAs51 | `1d17d5fa14` | ICML…/repro-sgera-stein-guided-ecg… | toy/toy/toy · toy/toy/toy · toy/toy/toy |
| | | bsenst/repro-sgera-stein-guided-ecg… | toy/toy/toy · toy/toy/toy · toy/toy/toy |
| IalpB5Mzaz | `6b4db58ff5` | bsenst/working | toy/toy/toy · inco/inco/inco · veri/veri/veri |
| | | bsenst/Time-Conditioned-Foreseeing… | toy/toy/toy · inco/inco/inco · veri/veri/veri |
| iJDJCO4mji | `cf6521b3d3` | …mmbert-annealed…-revision | veri/veri/veri · veri/veri/veri · veri/veri/veri · toy/toy/toy · toy/toy/toy · toy/toy/toy |
| | | arthrod/repro-mmbert-annealed… | veri/veri/veri · veri/veri/veri · veri/veri/veri · toy/toy/toy · toy/toy/toy · toy/toy/toy |

48 claim-instances (24 claims × 2 logbooks). **archived == rep1: 48/48. archived == rep2: 48/48. rep1 == rep2: 48/48.** Label distribution identical in all three conditions: `toy` 22, `verified` 20, `inconclusive` 6.

Full table: `control_per_logbook_verdicts.csv`.

## 3. Aggregate α

Cluster bootstrap over the 5 groups, B = 10,000. Implementation validated by reproducing the recorded archived figure: my α on the full 34 archived pairs is **0.9534** against the recorded 0.953.

| Condition | n pairs | agree | α | 95% CI |
|---|---|---|---|---|
| archived, full 34 pairs (recorded baseline) | 34 | 33 | 0.9534 | [0.840, 1.000]* |
| **archived, same 24 runnable pairs** | 24 | 24 | **1.0000** | [1.000, 1.000] |
| reproduced rep1, cross-logbook | 24 | 24 | **1.0000** | [1.000, 1.000] |
| reproduced rep2, cross-logbook | 24 | 24 | **1.0000** | [1.000, 1.000] |
| rep1 vs rep2, same logbook | 48 | 48 | 1.0000 | [1.000, 1.000] |
| archived vs rep1, same logbook | 48 | 48 | 1.0000 | [1.000, 1.000] |
| archived vs rep2, same logbook | 48 | 48 | 1.0000 | [1.000, 1.000] |

\* recorded CI from the archived analysis.

## 4. The stated pass criterion needs correcting — the arm passes either way

The criterion as given was "reproduced α within CI of the archived α = 0.953 for the same pairs." **0.953 is not the archived α for the same pairs.** It is the α for all 34 archived pairs, and the 10 pairs that are not reproducible contain **the only archived disagreement in the entire duplicate-`sha` stratum** — `verified` vs `inconclusive` in orid `2iFauBXg7Y`, whose second logbook has been deleted from the Hub.

Consequences:

1. **Correct baseline is α = 1.000, not 0.953.** On the 24 runnable pairs the archive had zero disagreements. The marginals are non-degenerate (three labels in use), so α is defined rather than undefined.
2. **The stated criterion is weak.** Requiring only that reproduced α fall inside [0.840, 1.000] would pass a run with 1–2 fresh disagreements out of 24 — it cannot distinguish "perfect reproduction" from "mild degradation."
3. Under the corrected criterion — reproduced α must equal the archived α of **1.000** on the same pairs — the arm still **passes exactly**, with zero disagreements in either replicate.

## 5. Power limit: what this control can and cannot establish

0 disagreements in 24 pairs bounds the true disagreement rate at **≤ 11.7%** (95% one-sided, exact binomial). So the control establishes that the instrument is not broken and has not drifted detectably; it **cannot** establish reliability finer than about 12%. It is a floor, not a precision estimate. Cite it as "no detectable drift, disagreement rate bounded below ~12%," never as "α = 1.0" without the n.

The loss of the 3 deleted-logbook groups cost more than 10 of 34 pairs — it cost the *only* archived disagreement, which was the one case where reproduction would have been informative about the judge's borderline behaviour. That is the substantive damage from corpus decay, and it is worth one sentence in the limitations.

## 6. Provider-side determinism ruled out as an artifact

Both members of a pair receive **byte-identical prompts** (verified for all 5 groups), so perfect within-pair agreement could in principle be response caching rather than independent convergence. It is not:

| Check | Result |
|---|---|
| Evidence prose byte-identical within pair (rep1) | 0 of 5 groups |
| Evidence prose byte-identical within pair (rep2) | 0 of 5 groups |
| `overall` summary identical within pair | 0 of 5 groups, both replicates |
| Evidence prose identical rep1 vs rep2, same logbook | no |
| Archived evidence identical within pair | 0 of 24 pairs |
| Distinct `resp_id` per call | 10/10, both replicates |

Prompt caching *was* active (`cached_tokens` up to 14,976 in rep2) but that is prefix reuse for compute, not response reuse — the generated text differs every time.

**This is the substantive finding of the arm: the verdict label is perfectly reproducible under identical input while the rationale text is never reproduced.** The judge converges on the same four-way label from independently generated reasoning, across a 45-day gap and two providers-of-record. The label is stable; the justification is not.

## 7. Bearing on the headline 70.1% disagreement

The archived control logbooks were judged 2026-07-20 to 2026-07-27; replicates ran 2026-09-11, a 45-day gap. Verdicts reproduce exactly. **Judge stochasticity is therefore not a viable explanation for the corpus-wide 70.1% disagreement rate** — under genuinely identical input this judge does not waver at all, within the resolution this arm affords. The corpus disagreement must be attributed to input variation between the paired logbooks, not to sampling noise in the judge. That is the positive control doing its job.

Note this cuts against an over-strong reading too: perfect label reproduction on 24 pairs of *identical* input says nothing about reliability on *similar* input, which is where the 70.1% lives.

## 8. Execution record

| | rep1 (= gate run) | rep2 |
|---|---|---|
| calls | 10 | 10 |
| schema pass | 10/10 | 10/10 |
| prompt tokens | 69,608 | 69,608 |
| completion tokens | 5,699 | 5,892 |
| cached tokens | 5,920 | 69,376 |
| cost at baseten published rates | $0.1151 | $0.0360 |

**Cost correction (2026-09-11).** An earlier version of this table reported $0.053 and $0.054, computed at $0.60/$2.00 per Mtok. That rate is wrong — it is close to baseten's published rate for GLM **4.7** ($0.60/$2.20), not GLM-5.2. Baseten's published GLM-5.2 rate is **$1.40/M input, $0.14/M cached input, $4.40/M output**. Corrected total for the control arm is **$0.151**, a factor of 1.41 above the figure first reported. Token counts were measured and were never in doubt; only the rate applied to them was wrong.
| retries triggered | 0 | 0 |
| served model | `zai-org/GLM-5.2` | `zai-org/GLM-5.2` |
| routed provider | `baseten` | `baseten` |
| `system_fingerprint` | null | null |

Intended revision `b4734de4facf877f85769a911abafc5283eab3d9` is recorded but **not enforced** — the router rejects revision pinning. Provider is `baseten` for every call in both replicates, so the two replicates do not span a provider change and cannot speak to cross-provider stability.

**Defect fixed during analysis:** `run_control.py` printed each logbook's verdicts in the order the model returned them. The model does not always emit the claims array in index order, which made replicate 2 appear to disagree with replicate 1 on three groups when the indexed verdicts were in fact identical. The print now sorts by claim index. The stored JSON was never affected — only the console summary.

## 9. Next

The 60-logbook pilot to re-estimate ICC. That is the gate on sample size for the main arm: if ICC_pilot > 0.50, the 440-logbook sample must be extended.
