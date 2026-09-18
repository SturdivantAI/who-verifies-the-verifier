# Identical-Evidence Stratification: Blocker 1 Resolution

> **Correction 2026-09-11 — pair count 112,390 → 112,380.** The original pairing keyed claims on a truncated claim string. For one paper (`7UEBX1KU1y`) that prefix key merged a legacy-era claim with a *different* anchored-era claim sharing its opening words, generating **10 spurious pairs** that compared two distinct claims. Rebuilt on full claim text: **112,380 pairs across the same 5,081 claims**. Nothing else moves — claim-level α = 0.2286 [0.2183, 0.2387] (was reported 0.229), hard contradictions 2,893 pairs / 337 claims, and the headline 70.12% (3,563/5,081) are all unchanged at reported precision. Corrected figures in `alpha_corrected.json`; substitute "112,380" wherever "112,390" appears below.

Source: `verdicts.json`, 5,081 repeat-judged claims, 112,390 within-claim verdict pairs. Reproduction: `evidence_pairs.csv` (pair-level, one row per pair), `evidence_strata_results.json`, `strata_verification.json`, `evidence_strata_summary.csv`.

**Construction.** Strata A and B are defined on *pairs*, not claims, so each stratum's coincidence matrix is built by treating every qualifying pair as a two-judgment unit. That is exactly Krippendorff's α in the m = 2 case and is literally the test–retest unit. Bootstrap resamples claims, not pairs, because pairs within a claim are not independent.

---

## 1. Raw numbers as requested

| # | Quantity | Value |
|---|---|---|
| 1 | Claims with ≥1 identical-evidence pair | **0** |
| 1 | Claims with only differing-evidence pairs | **5,081** (100%) |
| 2 | Krippendorff's α, Stratum A only | **undefined — stratum is empty** |
| 3 | Delta (Stratum A α − pooled 0.229) | **undefined** |
| 4 | Hard contradictions (verified↔falsified), Stratum A | **0 pairs, 0 claims** (stratum empty) |
| 5 | Stratum B: pairs | **112,390** (100% of all pairs) |
| 5 | Stratum B: Krippendorff's α (pair-level) | **0.141**, 95% CI [0.130, 0.153] |
| 5 | Stratum B: D_o | 0.4789 |
| 5 | Stratum B: hard contradictions | **2,893 pairs; 337 claims** |

Stratum A contains **zero of 112,390 pairs**. Every repeat-judged claim falls entirely into Stratum B. Consequently items 2, 3 and 4 are not computable as specified, and item 5 reduces to the whole corpus.

---

## 2. Why Stratum A is empty

The `evidence` field is not the evidence *presented to* the judge. It is the judge's own free-text justification for the verdict it issued.

- 32,664 distinct evidence strings across 32,688 verdict instances. The only repeats are 16 empty strings and two boilerplate "no experiments were executed" sentences.
- Mean pairwise similarity between two evidence texts for the same claim is 0.086 (median 0.057; 9 of 9,041 sampled pairs exceed 0.80).
- Length 70–600 characters, median 307 — prose, not a retrieved passage.
- The texts reference logbook-specific artefacts: job IDs, seed counts, measured values, specific hyperparameters.

Three of the 42 evidence texts for one claim in `5nNNVY8NW4` illustrate it: one logbook ran modular addition with an MLP instead of the ridge regression the theorem requires (→ inconclusive), another ran at paper scale with 8 seeds and reported confirmatory numbers (→ verified), a third attempted no formal verification at all (→ inconclusive). These are descriptions of *different work*, written by the judge.

So exact-match stratification on this field cannot separate identical-input retests from differing-input judgments: the field varies with the input, and also with the judge's own generation. An empty Stratum A is the correct result, not a defect.

---

## 3. A weighting caveat before any comparison

Stratum B's α = 0.141 must **not** be read as lower than the headline 0.229. Nothing changed about the data — only the weighting. Three defensible weightings of the same 5,081 claims:

| Weighting | α | 95% CI | Claim weight |
|---|---|---|---|
| All pairs equally | 0.141 | [0.130, 0.153] | ∝ m(m−1)/2 |
| Krippendorff, 1/(m−1) — the headline | 0.229 | [0.218, 0.239] | ∝ m |
| One random pair per claim | 0.290 | [0.277, 0.303] | ∝ 1 |

The ordering follows directly from the established result that α declines with m: the more heavily pair-level weighting favours high-m claims, the lower α goes. **0.229 remains the headline**; it is the standard estimator with the conventional weighting. The 0.290 figure is the right one to quote when comparing against a condition that contributes one pair per claim — which is what §4 does.

---

## 4. Two computable substitutes for the identical-input condition

Since the requested field cannot isolate identical inputs, two other conditions in the corpus can.

**4a. Same logbook snapshot (`sha`).** 13 `sha` values are shared by exactly two logbooks each — 26 logbooks that are byte-identical content snapshots published under different space names (mostly duplicate or renamed reproduction spaces from one author). This yields 34 claim-pairs where the judge saw provably identical input, every pair drawn from two distinct spaces.

- Agreement: **33 of 34 pairs (97.1%)**
- **α = 0.953**, 95% CI [0.840, 1.000]
- Hard contradictions: **0**
- The single disagreement is verified vs inconclusive on one claim in `2iFauBXg7Y`

Note the internal validation: the evidence text differed in **all 34** of these pairs despite provably identical input — independent confirmation of §2, that the field is a generated rationale.

**4b. Both logbooks executed no experiments.** 363 pairs across 174 claims where both evidence texts state that no experiments were run.

- Agreement: **363 of 363 pairs (100%)**
- All 726 verdict instances are `inconclusive`; α is undefined because the marginal is degenerate (D_e = 0), not because agreement is poor
- Hard contradictions: **0**

![α by input condition, and per-pair agreement]({{artifact:art_97249eb9-ff79-4160-ab90-b484f12f7a25}})

---

## 5. Interpretation

**Blocker 1 resolves, but against the current headline.** The threat flagged in §6.1 of the α results was that different logbooks are not a test–retest condition. That threat is now empirically supported rather than merely acknowledged. In the only two conditions where input is identical or near-identical, the judge is reliable — α = 0.953 on identical snapshots and 100% agreement where neither logbook ran experiments — against α = 0.290 on the matched one-pair-per-claim comparison where evidence differs. Across a threshold-relevant range, the same judge moves from above 0.95 to below 0.30 depending only on whether the input is the same.

**What the corpus therefore cannot claim.** The 48.06% per-pair disagreement is not within-judge instability under fixed input. It is disagreement across genuinely different reproduction attempts. The poster's current framing — a judge contradicting itself — is not supported by these strata, and the comparison to Anghel et al.'s 48.4% mirrored-order reversal is no longer apples-to-apples: that study held input fixed and perturbed only presentation order. Ours does not hold input fixed at all.

**What it can claim, and it is stronger.** Independent agentic reproduction attempts on the same research claim reach contradictory automated verdicts at scale — 70.12% of claims carry at least one internal disagreement, 337 carry an outright verified↔falsified contradiction — and this happens while the judge itself is demonstrably stable under fixed input. That relocates the finding from *judge unreliability* to *reproduction-pipeline non-determinism*, measured through a judge that has been independently shown reliable on the same corpus. The instrument is exonerated; the pipeline is indicted.

**The α = 0.229 number keeps a narrower role.** It is a valid reliability coefficient for the composite instrument "logbook + judge" treated as one measurement device — which is the thing a user of such a system actually experiences. It is not a coefficient for the judge alone.

---

## 6. The limit on all of §4

n = 34 pairs from 13 duplicate groups, and those groups are not a random sample — they are mostly one author's duplicated spaces. The CI reaches 1.000. This is a **directionally strong but underpowered** result, adequate to invalidate the within-judge framing, not adequate to publish 0.953 as the judge's test–retest reliability.

The decisive experiment is cheap and fully within reach: re-run the judge on a stratified sample of logbooks it has already scored — same snapshot, same prompt, fresh inference — and compute α on that. A few hundred re-judgments would give a properly powered test–retest figure. Until that exists, §4a should be reported as corroborating evidence with its n stated, and §5's reframing rests on it jointly with §4b's 363 pairs and the §2 field diagnostics, which do not depend on n = 34.
