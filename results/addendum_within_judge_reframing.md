# Addendum: The 70.1% Figure Is Within-Judge Instability, Not Inter-Judge Disagreement

**Revision to `llm_judge_reliability_review.md`, Sections 1–2 and the panel-inflation argument.**

---

## 1. What the design specification changed

The review as first drafted positioned 70.1% against the **inter-judge** literature — studies measuring whether *different* judges agree. The actual design is different in kind:

> A single judge model (GLM-5.2) issues verdicts on the same claim across different logbooks. A claim counts as disagreeing if **any two** of its verdicts differ. 70.1% is the proportion of 5,084 multiply-judged claims with at least one such pair. No chance correction. Four-category nominal label set: verified, falsified, inconclusive, toy.

This is **within-judge instability** — the test–retest / intra-rater construct — not inter-rater disagreement. The two are separate reliability coefficients measuring separate things, and the published values differ by roughly an order of magnitude. Cross-judge agreement in this literature clusters at 51–82%; within-judge instability, where reported, clusters at 13–48%. Anchoring to the wrong one understates the severity of the finding at low repeat counts and overstates it at high ones.

The panel-inflation argument from the original review is **withdrawn**. It modelled k distinct judges voting on one item. Replace it with the calculation below, which has the same combinatorial shape but a different denominator and a different comparator class.

---

## 2. The decisive unknown: repeat count per claim

Because a claim is flagged when *any* pair of its verdicts differs, the number of pairs — and therefore the flag probability — grows quadratically in the number of repeat judgments *m*. Under independence, per-pair agreement *s* implies an any-pair disagreement rate of 1 − s^C(m,2). Inverting at the observed 70.1%:

| Repeat judgments *m* | Pairs C(m,2) | Implied per-pair disagreement |
|---|---|---|
| 2 | 1 | **70.1%** |
| 3 | 3 | **33.1%** |
| 4 | 6 | **18.2%** |
| 5 | 10 | **11.4%** |
| 6 | 15 | 7.7% |
| 8 | 28 | 4.2% |
| 10 | 45 | 2.6% |

Against the retrieved within-judge comparators — Yagubyan (2026) at a 13.6% mean flip rate, Wang et al. (2025) at 23.32% score-comparison inconsistency, Anghel et al. (2025) at a 48.4% mirrored-order reversal rate — the reading inverts across this table:

- **At m = 2**, the implied 70.1% per-pair instability exceeds every value in the retrieved literature, including the 56% worst-case single question in Yagubyan (2026). That is a genuinely novel and alarming result.
- **At m = 3–4**, the implied 33.1% and 18.2% fall *inside* the published band. The corpus would then be corroborating existing findings at scale rather than contradicting them.
- **At m ≥ 6**, the implied instability is *better* than most published judges, and the headline figure would be largely an artifact of the any-pair rule.

**This is not a caveat to be noted in passing — it determines whether the poster reports an outlier or a replication.** The number of logbooks per claim, and its distribution across the 5,084, must be in the methods.

![Implied per-pair instability and chance-corrected agreement as a function of repeat count]({{artifact:art_3733036e-6fe3-478f-9dd7-70cc6cc44018}})

---

## 3. Chance correction on a four-category scale

With no chance correction and a four-category nominal label set, the raw rate is close to uninterpretable, because expected-by-chance agreement depends entirely on the verdict marginals. Cohen's κ implied by the 70.1% figure:

| | uniform (Pe = .25) | mild skew (Pe = .30) | moderate skew (Pe = .39) | strong skew (Pe = .53) |
|---|---|---|---|---|
| m = 2 | 0.065 | 0.006 | **−0.140** | **−0.476** |
| m = 3 | 0.558 | 0.530 | 0.461 | 0.303 |
| m = 4 | 0.757 | 0.741 | 0.704 | 0.616 |
| m = 5 | 0.848 | 0.839 | 0.815 | 0.761 |

At m = 2 with a realistically skewed verdict distribution — most claims landing in one category, which is typical of automated verification corpora — **κ is negative**: the judge agrees with itself *less* often than random assignment with those marginals would. At m ≥ 4, κ is substantial under every marginal considered. Norman et al. (2026) found chance correction deflated measured judge performance by 33–41 percentage points across ~541,000 judgments; that magnitude of correction is entirely consistent with the swing shown here, and it is why the uncorrected rate should not be the headline number.

---

## 4. Three measurement issues specific to this design

**4.1 Heterogeneous repeat counts inflate the rate mechanically.** If claims appear in differing numbers of logbooks, those appearing in more are more likely to be flagged for reasons that have nothing to do with judge reliability. A single pooled 70.1% mixes these strata. Report disagreement stratified by *m*, or use a statistic invariant to it — mean pairwise disagreement per claim, or Fleiss' κ treating the repeated verdicts as raters. Either is defensible; the pooled any-pair rate is not.

**4.2 The four categories are not equidistant.** A verified/falsified pair is a hard contradiction; a verified/inconclusive pair is a confidence shift. Collapsing both into "disagreement" discards the distinction that matters most for a verification system. Separate the hard-contradiction rate from the confidence-shift rate, or apply Krippendorff's α with a custom distance matrix over the four labels — α also handles the unequal-*m* problem in 4.1 natively, which makes it the single best fit for this design.

**4.3 Different logbooks are not a test–retest condition.** This is the most serious threat to the interpretation. Test–retest reliability requires the *same* input presented again. If logbooks carry different evidence about the same claim, a changed verdict may be correct Bayesian updating rather than instability — and the measurement conflates the two. Kiuchi et al. (2026), the closest true repeated-measures design retrieved, controls this by rescoring identical transcripts three times.

To separate the components, identify the stratum of claims where the surrounding evidence was materially identical across logbooks and report its disagreement rate alongside the pooled one. The gap between the two estimates *is* the context-sensitivity effect, and it is a publishable quantity in its own right — no retrieved study measures it.

---

## 5. Revised comparator set

Eight studies in `within_judge_comparators.csv` report within-judge quantities and replace the inter-judge comparators for the headline claim. Three are load-bearing:

- **Anghel et al. (2025)**, in *Information* and the only peer-reviewed member of the set, reports 100% consistency *across* judges alongside a 48.4% verdict reversal rate *within* one judge under mirrored response order. This is the cleanest published demonstration that inter-judge agreement is uninformative about within-judge stability, and it justifies the reframing directly.
- **Kiuchi et al. (2026)** rescored each transcript three times per evaluator system and found single-run ICCs from .33 to .96, with high run-to-run reliability failing to predict closer expert-panel alignment. Reliability and validity are separate axes; a stable judge is not thereby a correct one.
- **Mohammadi (2026)** tested the obvious remedy and found it does not work: a self-consistency ensemble tripled cost while improving nothing. Repeat-and-majority-vote should not be proposed as the fix without citing this.

Sunkavalli (2026) additionally supplies the only retrieved measurement of cross-version drift — severity shifts up to 133 points on a 0–1000 scale across five version contrasts, with one judge deprecated mid-study and caught by identity canaries. If the corpus was collected over a period during which GLM-5.2 was updated, version drift is a confound with the same signature as instability, and the deployment date range belongs in the methods.

---

## 6. What to report

1. The repeat-count distribution, and the disagreement rate stratified by it.
2. Krippendorff's α over the four labels with a severity-aware distance matrix, reported alongside the raw rate rather than instead of it.
3. The hard-contradiction rate (verified ↔ falsified) separately from confidence shifts involving *inconclusive*.
4. The identical-evidence stratum, if one can be constructed, as the clean test–retest estimate.
5. The collection window and whether the judge version was held fixed.

The headline claim that survives all five, if the numbers hold, is a strong one: *a single frontier judge model, re-encountering the same claim, contradicts itself at a rate the published test–retest literature does not anticipate.* That is a better poster than the inter-judge framing, because within-judge instability cannot be explained away as legitimate evaluator diversity.

---

## Method note

All values in Sections 2–3 are computed, not cited: `implied_self_consistency.csv` and `implied_kappa_sensitivity.csv` contain the full grids. The independence assumption across repeat judgments is almost certainly optimistic — a judge's errors on the same claim are positively correlated — which means true per-pair instability is *higher* than the implied values at any given *m*. Every literature value is extracted from the retrieved record, and every DOI resolved and title-matched before citation.


---

## References (studies cited in this addendum)

Anghel, C., Anghel, A. A., Pecheanu, E., Cocu, A., Istrate, A., & Andrei, C. A. (2025). Diagnosing Bias and Instability in LLM Evaluation: A Scalable Pairwise Meta-Evaluator. *Information*. https://doi.org/10.3390/info16080652

Kiuchi, K., Fujimoto, Y., Gotō, H., Hosokawa, T., Nishimura, M., Satō, Y., Sezai, I., & Inoue, T. (2026). Distinct Profiles of Run-to-Run Score Reliability and Expert-Panel Alignment Across Four LLM Evaluators of Simulated Japanese-Language AI-to-AI Counseling. *arXiv*. https://doi.org/10.48550/arXiv.2507.02950

Lau, F. (2026). Same Input, Different Scores: A Multi Model Study on the Inconsistency of LLM Judge. *arXiv*. https://doi.org/10.48550/arxiv.2603.04417

Mohammadi, H. (2026). trajectory-judge: What Outcome-Only LLM Judges Miss on Agent Trajectories. *arXiv*. https://doi.org/10.48550/arXiv.2609.00038

Norman, J. D., Rivera, M. U., & Hughes, D. A. (2026). Reliability without Validity: A Systematic, Large-Scale Evaluation of LLM-as-a-Judge Models Across Agreement, Consistency, and Bias. *arXiv*. https://doi.org/10.48550/arXiv.2606.19544

Sunkavalli, V. K. (2026). LLM Judges as Raters: A Pre-Registered Audit of Severity, Halo, Reliability, and Version Instability in LLM Essay Scoring on Public Corpora. *arXiv*. https://doi.org/10.48550/arXiv.2608.29517

Wang, Y., Song, Y., Zhu, T., Zhang, X., Yu, Z., Chen, H., Song, C., Wang, Q., Wang, C., Wu, Z., Dai, X., & Zhang, Y. (2025). TrustJudge: Inconsistencies of LLM-as-a-Judge and How to Alleviate Them. *arXiv*. https://doi.org/10.48550/arXiv.2509.21117

Yagubyan, A. (2026). The Coin Flip Judge? Reliability and Bias in LLM-as-a-Judge Evaluation. *arXiv*. https://doi.org/10.48550/arXiv.2606.13685
