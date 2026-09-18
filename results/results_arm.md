# Extended re-judgment arm (option B) — 236 logbooks

Executed 2026-09-12. 236 logbooks, 1,225 claim comparisons, 352 new paid calls
(`zai-org/GLM-5.2:baseten`, provider pin honoured on 352/352), 352/352 schema-pass.
Pooled with the 60-logbook pilot, whose 120 calls were reused rather than repeated.

**The precision target is met.** Krippendorff α half-width **0.0375** against the protocol's
**0.0458**. This arm answers the question it was authorized to answer, and no further
re-judgment spend is needed for the reliability estimate.

## Headline estimates

| quantity | estimate | 95% CI (cluster bootstrap, 4,000 reps) |
|---|---|---|
| retest disagreement | **8.41%** (103/1,225) | 6.08% – 11.03% |
| α_retest (nominal) | **0.8737** | 0.8336 – 0.9086 |
| ICC(1), logbook clusters | **0.3503** (n̄ = 5.19) | 0.2330 – 0.4479 |

Logbooks are the clustering unit: **183 of 236 are fully stable**, and 53 carry all 103
disagreements.

## Two corrections to what the pilot reported

The extension was staged as a strict superset — the band pools are walked in the same draw
order, and `stage_arm.py` asserts every one of the pilot's 60 prompts rebuilds byte-identically
before writing anything. All 60 did, so pilot and extension are the same instrument and the
comparison below is a precision comparison, not an instrument comparison.

**1. The ICC finding does not replicate, and my pilot-stage warning was wrong.** The pilot
measured ICC = 0.5415 and I reported that `cluster_design.json`'s assumed 0.424 would
understate the design effect by ~22%. At 236 clusters the ICC is **0.3503 [0.2330, 0.4479]**.
The pilot's 0.5415 falls **outside** that interval; the design's 0.424 falls **inside** it. The
design's assumption was sound and the pilot's ICC was an overestimate from 60 clusters. ICC is
a variance-ratio statistic and is badly behaved at small cluster counts — that is exactly the
failure mode the pilot was too small to avoid, and it argues for treating any single-pilot ICC
as provisional rather than as a design input.

**2. The disagreement rate tightened without moving.** The pilot's 10.49% sits inside the
pooled CI [6.08%, 11.03%], and the pooled α (0.8737) sits inside the pilot's CI
[0.7457, 0.9313]. Both pilot estimates were consistent; only the ICC was misleading.

## The pre-registered decision rule, at final sample size

`mem_60a6cdd2f322` sets α_retest ≥ 0.667 as confirming the pipeline-non-determinism reframing.
Measured **0.8737, lower bound 0.8336** — cleared by a wide margin at 4× the pilot's sample.
The reframing is settled: the 48.06% cross-logbook and 70.1% corpus-level disagreement figures
are driven by genuinely different reproduction attempts, not by judge instability.

What must still not be claimed: **reproduction under identical input is 91.6%, not 100%.** The
poster cannot assert determinism under fixed input.

## Multiplicity band: a gradient that is not established

| band | claims | disagreements | rate | ICC(1) | α |
|---|---|---|---|---|---|
| m=2 | 292 | 33 | 11.30% | 0.2339 | 0.8370 |
| m=3-5 | 303 | 26 | 8.58% | 0.5176 | 0.8751 |
| m=6-10 | 310 | 26 | 8.39% | 0.4540 | 0.8662 |
| m>10 | 320 | 18 | 5.63% | 0.1674 | 0.8953 |

The rate is monotone decreasing in multiplicity, which would be an interesting claim: judgments
on heavily-reproduced papers would be more stable. **It does not reach significance.** GEE logit
of disagreement on band rank, exchangeable correlation clustered by logbook: OR **0.809 per
band [0.627, 1.042], z = −1.64, p = 0.101**. Report it as a descriptive pattern, not a finding.
The per-band ICCs are non-monotone and mutually overlapping, consistent with the instability
of ICC at these cluster counts noted above.

## The archive-regime anomaly replicates

| comparison | pilot (n=305) | extended (n=1,225) |
|---|---|---|
| fresh vs fresh | 10.49% | 8.41% |
| fresh vs archive | 23.28% | **16.33%** |
| ratio | 2.22 | **1.942** [1.435, 2.688] |

The bootstrap ratio interval **excludes 1.0**, so the archive is not a draw from the same
distribution as current output — confirmed at four times the pilot's sample. Every constraint
from the pilot analysis stands unchanged: the corpus records only the model string and carries
no provider, endpoint, or served-build field, the archive ran the *unpinned* router while both
replicates here pinned baseten, and provider heterogeneity and served-build drift predict the
same observable. **Do not quote a fresh-vs-archive reproduction rate as a property of the
judge.** The 8.41% retest floor is unaffected — it is fresh-vs-fresh on one pinned route.

## Harness defect: 1 in 472 calls

Across all 472 executed calls (120 pilot + 352 extension) exactly one returned fewer claim
objects than its prompt listed: `abhishekkataria16/claim-4ltyJqAHMg-logbook`, 3 of 4 in the
pilot's replicate 2. Both extension replicates were 176/176.

This analysis **excludes** the affected claim rather than scoring it. Under production harness
semantics `normalize_verdicts()` would backfill the omission as `inconclusive`, which in this
instance matched the other replicate and would have manufactured a spurious agreement. The
defect inflates measured agreement; it does not merely lose data. At 0.21% incidence its effect
on these estimates is negligible, but the mechanism should be fixed rather than tolerated.

## Corpus decay — a methods-section fact

Staging scanned 250 sampled rows to fill 236 slots:

- **12 logbook Spaces (4.8%) no longer exist** (`RepositoryNotFoundError`)
- 2 ORIDs are absent from the challenge index snapshot
- HEAD has moved since judging on **23 of 236 (9.7%)** of the Spaces that do exist
- 9 of 236 logbooks hit the 120k-character truncation cap

Every fetch was pinned to the sha recorded at judging time, so content drift cannot affect these
results. But the corpus is not archivally stable: a replication attempted later will find less
of it, and any study of this corpus should pin shas and report its own decay rate.

## Cost

| item | tokens | |
|---|---|---|
| prompt | 4,410,612 | 50.7% served from prefix cache |
| completion | 239,899 | 130 tok/claim vs 119 assumed |

baseten's cache billing rate is not exposed in the response metadata, so the realized figure is
bounded rather than known: **$4.10** if cached prompt tokens are not billed, **$7.23** if they
are billed at full rate. Cumulative with the pilot: **$5.31–$8.44 of the $20 credit.**

The pre-run estimate I quoted was $6.80, itself revised up from $5.58 after staging revealed the
deeper draw pulled logbooks 1.25× longer than the pilot's. Both revisions are within the
bounded outcome. Note that heavy caching again did **not** induce determinism: the 8.41% retest
rate was measured with half the prompt tokens served from cache.

## Files

- `arm_per_claim_verdicts.csv` — 1,225 rows: both replicates, archived verdict, band, agreement
- `arm_results.json` — machine-readable estimates, CIs, per-band table, provenance
- `stage_arm.py` — superset staging with the byte-identity assertion on the pilot overlap
- `run_arm.py` — replicate runner; judges only logbooks the pilot had not judged
- `analyze_arm.py` — pooling and estimation; single source for ICC and α
