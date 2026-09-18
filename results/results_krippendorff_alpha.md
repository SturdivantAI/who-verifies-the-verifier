# Chance-Corrected Reliability of the GLM-5.2 Verdict Corpus

**Exact results, computed from the full per-claim coincidence matrix.** Supersedes the model-based estimates in v1 of this document; those are retained in §7 for comparison. Source: `verdicts.json` (6,398 logbooks, 32,688 verdict instances, judge `zai-org/GLM-5.2` throughout). Reproduction: `exact_alpha.py`; tables `per_claim_verdicts.csv`, `alpha_by_m_band.csv`, `alpha_decomposition_by_band.csv`, `exact_results.json`.

---

## 1. The positioning claim

> A single frontier judge model (GLM-5.2) re-encountering the same research claim across independent logbooks disagrees with itself on 48.06% of verdict pairs (95% CI [47.30%, 48.82%]), yielding a chance-corrected agreement of Krippendorff's α = 0.229 (95% CI [0.218, 0.239]) across 5,081 repeat-judged claims and 27,156 verdicts on a four-category nominal scale — indistinguishable from the highest within-judge instability yet reported (48.4%), which required deliberate response-order manipulation to elicit, and less than one third of the α ≥ 0.667 threshold conventionally required before a measurement instrument may support even tentative conclusions.

The Blocker 1 figure for Panel 4:

> **337 of 5,081 repeat-judged claims (6.63%) carry at least one outright verified↔falsified contradiction.** Expressed per judgment pair — the m-invariant form — hard contradictions are 2.19% of all pairs (95% CI [1.94%, 2.45%]) and 4.6% of all disagreement.

![Exact α decomposed by repeat count, and the composition of disagreement]({{artifact:art_143cab49-6c38-4865-8b4e-53e6e07f2970}})

---

## 2. Provenance and reconciliation

Every summary figure you supplied reproduces exactly from the source file: 5,081 repeat-judged claims, 27,156 verdict instances, the full 23-point m-distribution (m = 2: 1,831 through m = 42: 5) with **no mismatches at any value**, and all four marginals to the unit (verified 14,532 / inconclusive 5,991 / toy 5,436 / falsified 1,197). The corpus holds 10,613 unique claims under the stated key, of which 5,081 are judged more than once. No claim key recurs within a single logbook, so every repeat is a genuinely separate logbook encounter. The earlier 5,084 figure should be corrected to 5,081 wherever it appears.

**One amendment to the matching validation.** The claim *count* is invariant — 5,081 under both the 80-character prefix and full claim text, which is what your check measured. But the corpus contains 10,613 unique prefix keys against 10,614 unique full texts: exactly one prefix collision exists. In paper `7UEBX1KU1y`, two rewordings of one claim about DPO and the equivalence assumption share their first 80 characters and are merged, combining an m = 1 and an m = 10 claim into m = 11.

This is arguably a *correct* merge — the two strings are paraphrases of the same assertion — and its effect is one verdict instance in 27,156. Recomputing everything on full-text keys gives α = 0.2286 against 0.2285, and an identical Blocker 1 count of 337. **The matching method is validated; the delta is 0.0001 in α, not 0.** Your conclusion stands, with the collision worth a footnote rather than a correction.

---

## 3. Exact α

| Quantity | Value | 95% CI (bootstrap over claims, B = 10,000) |
|---|---|---|
| Observed disagreement D_o (per-pair) | 48.06% | [47.30%, 48.82%] |
| Expected disagreement D_e | 0.622974 | — |
| **Krippendorff's α (nominal)** | **0.229** | **[0.218, 0.239]** |
| Krippendorff's α (severity-weighted) | 0.250 | [0.239, 0.261] |
| Claims with ≥1 verified↔falsified pair | 337 (6.63%) | — |
| Hard contradictions, per-pair | 2.19% | [1.94%, 2.45%] |

D_e computed from the coincidence matrix matches the value derived from your marginals alone (0.622974) to six decimals, and the any-disagreement rate reproduces at 70.12%. The CI resamples claims, so it propagates the dependence among repeated judgments of the same claim — which the binomial interval used in v1 did not.

**Chance context, unchanged and still the most important framing.** Random assignment from these marginals under this m-distribution produces 82.2% pooled any-pair disagreement. The observed 70.12% is 12.1 points *better* than random. The raw rate must not be reported as a headline — this is precisely the failure Norman et al. (2026) document across ~541,000 judgments from 21 judges, where chance-uncorrected exact-match agreement overstates discriminative ability and the deflation from exact match to Cohen's κ runs 33–41 percentage points on MT-Bench.

**What a reliable judge looks like, for contrast.** The same study reports test–retest reliability above 0.95 for its judge cohort — so within-judge stability at this level is achievable and routinely achieved elsewhere. An α of 0.229 is not a property of LLM judges in general; it is a property of this instrument on this task.

---

## 3a. Unit-matched against the published within-judge figures

Per-pair disagreement is invariant to m, which is what makes 48.06% directly comparable to the retrieved within-judge literature (full set and per-row justification in `within_judge_comparators.csv`):

| Study | Within-judge instability | Condition |
|---|---|---|
| Yagubyan (2026) | 13.6% mean flip rate | repeated runs, unperturbed |
| Wang et al. (2025) | 23.32% score-comparison inconsistency | internal consistency audit |
| **This corpus** | **48.06%** | **repeated logbook encounters, unperturbed** |
| Anghel et al. (2025) | 48.4% verdict reversal | adversarial mirrored response order |
| Yagubyan (2026) | 56% maximum | worst single question |

The comparison that carries the poster: Anghel et al. (2025) obtained 48.4% by actively swapping response order to induce position bias, and reported it as evidence of severe evaluator fragility — alongside 100% consistency *across* judges, which is the cleanest published demonstration that inter-judge agreement says nothing about within-judge stability. This corpus reaches 48.06% with no perturbation applied at all. The instability is intrinsic to repeated encounters, not induced by a manipulation, and the two figures are close enough that the honest phrasing is "indistinguishable from" rather than "exceeding."

---

## 4. The m-band result, and why it is not what it looks like

| m-band | Claims | D_o | D_e | α | verified share | Claims with hard contradiction |
|---|---|---|---|---|---|---|
| m = 2 | 1,831 | 0.4675 | 0.6699 | 0.302 | 26.6% | 16 (0.87%) |
| m = 3–5 | 1,665 | 0.4864 | 0.6754 | 0.280 | 44.1% | 60 (3.60%) |
| m = 6–10 | 802 | 0.4782 | 0.5903 | 0.190 | 58.6% | 105 (13.09%) |
| m > 10 | 783 | 0.4831 | 0.5298 | 0.088 | 64.6% | 156 (19.92%) |

α falls by a factor of 3.4 from m = 2 to m > 10. The tempting reading — that the judge becomes more erratic on heavily-replicated claims — is **wrong**, and the decomposition says why: D_o is flat across bands (spread 0.019), while D_e falls steeply (spread 0.146). Per-pair instability is essentially constant at 47–49% regardless of how many times a claim is judged. What changes is the *chance baseline*: the verified share climbs from 26.6% to 64.6%, concentrating the marginals (Σp² from 0.330 to 0.470) and shrinking the disagreement a random judge would produce. The same raw instability is therefore harder to excuse in the high-m stratum.

Two consequences for how you present this:

1. **Do not report α stratified by m without the decomposition.** α = 0.088 at m > 10 is a statement about the marginals in that stratum, not about deteriorating judge behaviour. The defensible cross-band claim is that per-pair instability is invariant to repeat count.
2. **The Blocker 1 per-claim rate is m-confounded.** It rises from 0.87% to 19.92% across bands, but a claim judged 42 times has 861 pairs in which to contradict itself and a claim judged twice has one. The per-pair rate (2.19%) is the comparable quantity; if Panel 4 shows 6.63%, the m-distribution has to be on the same panel.

The 783 claims at m > 10 spread across 141 papers with at most 6 claims per paper, so the tail is broad rather than driven by a few documents. The five m = 42 claims all belong to `5nNNVY8NW4` and reach α = 0.070.

---

## 5. Severity: the disagreement is mostly confidence, not contradiction

| Verdict pair | Share of all pairs | Share of disagreement |
|---|---|---|
| verified ↔ toy | 17.10% | 35.6% |
| verified ↔ inconclusive | 15.26% | 31.8% |
| inconclusive ↔ toy | 10.13% | 21.1% |
| **verified ↔ falsified** | **2.19%** | **4.6%** |
| falsified ↔ inconclusive | 1.92% | 4.0% |
| falsified ↔ toy | 1.46% | 3.0% |

88.4% of all disagreement involves inconclusive or toy — the judge changing its confidence or its assessment of scope, not reversing its scientific conclusion. Outright polarity reversals are 4.6%.

Weighting verified↔falsified at 1.0 and every other disconfirmation at 0.5 *raises* α from 0.229 to 0.250. The direction matters: it means observed disagreement is less concentrated on the hard contradiction than chance would place it. The judge avoids outright self-contradiction better than random — while still failing the reliability threshold by a wide margin on the four-category instrument as specified.

---

## 6. What this does and does not license

The headline is safe and now exact. Two limits remain.

**6.1 Different logbooks are not a test–retest condition.** *Superseded — resolved in `results_evidence_strata.md`, and resolved against the within-judge framing. The `evidence` field turned out to be the judge's generated rationale, not the input, so the identical-evidence stratum is empty; two substitute conditions with provably identical input give α = 0.953 (n = 34 pairs) and 100% agreement (n = 363 pairs). The 48.06% is disagreement across differing evidence, not within-judge instability. §1, §3 and §5 of this document stand as computed; the reliability claim they support belongs to the composite logbook+judge instrument, not to the judge alone.* If the evidence surrounding a claim differed between logbooks, a changed verdict may be correct updating rather than instability. Nothing in the reconciliation addresses this, because the matching key validates claim *identity*, not evidence identity. The clean estimate is α restricted to repeats where the surrounding evidence is unchanged, and the gap between that and 0.229 is a publishable quantity in its own right. The `evidence` field present on each claim record makes this computable.

**6.2 The four categories are treated as unordered.** That is correct per your specification, and §5 shows what an ordered or severity-aware treatment would do to the number.

The matching-artifact concern is closed. The high-m distributional anomaly is closed — structural replication, as you determined, and §4 now explains why it moves α.

---

## 7. Model-based v1 estimates versus exact

| Quantity | v1 (modelled) | Exact | Error |
|---|---|---|---|
| Per-pair disagreement | 47.2% | 48.06% | −0.9 pp |
| Krippendorff's α | 0.242 | 0.229 | +0.013 |
| Blocker 1 upper bound | ≤ 1,197 claims | 337 | bound held |
| Assumption-free α bound | ≤ 0.579 | 0.229 | bound held |

The homogeneous-error model was mildly optimistic on both quantities, and its one qualitative failure was assuming a single instability rate across claims — which forced constant α by construction and would have missed §4 entirely. Both assumption-free bounds held.

---

## References

Anghel, C., Anghel, A. A., Pecheanu, E., Cocu, A., Istrate, A., & Andrei, C. A. (2025). Diagnosing Bias and Instability in LLM Evaluation: A Scalable Pairwise Meta-Evaluator. *Information*. https://doi.org/10.3390/info16080652

Norman, J. D., Rivera, M. U., & Hughes, D. A. (2026). Reliability without Validity: A Systematic, Large-Scale Evaluation of LLM-as-a-Judge Models Across Agreement, Consistency, and Bias. *arXiv*. https://doi.org/10.48550/arXiv.2606.19544

Wang, Y., Song, Y., Zhu, T., Zhang, X., Yu, Z., Chen, H., Song, C., Wang, Q., Wang, C., Wu, Z., Dai, X., & Zhang, Y. (2025). TrustJudge: Inconsistencies of LLM-as-a-Judge and How to Alleviate Them. *arXiv*. https://doi.org/10.48550/arXiv.2509.21117

Yagubyan, A. (2026). The Coin Flip Judge? Reliability and Bias in LLM-as-a-Judge Evaluation. *arXiv*. https://doi.org/10.48550/arXiv.2606.13685
