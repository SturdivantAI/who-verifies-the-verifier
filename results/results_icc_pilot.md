# ICC pilot — 60 logbooks, 120 judgments, executed 2026-09-12

Run as authorized. `zai-org/GLM-5.2:baseten`, provider pin honoured on 120/120 calls.
Measured cost **$1.21**. Both conditions attached to the recommendation were applied:
stratified draw (15 per band), provider pinned.

## Headline: the retest condition is NOT deterministic

**32 of 305 claim comparisons disagree — 10.49%** on *byte-identical input*.

| quantity | value | 95% interval |
|---|---|---|
| retest disagreement | **10.49%** (32/305) | 7.29–14.49% Clopper-Pearson; **4.71–17.47%** cluster bootstrap |
| Krippendorff α (retest, 4-cat nominal) | **0.8477** | 0.7457–0.9313 (cluster bootstrap) |
| ICC(1), agreement indicator | **0.5415** | — |
| design effect at mean cluster 5.08 | **3.211** | — |

This overturns the pre-run expectation directly. The executed control arm's 0/48 licensed
an upper bound of ≤0.97% had the pilot also come back clean. It did not: the measured rate is
**10.8× that bound**. Under the pilot's rate, the control's perfect 0/48 had probability
**0.0049** — so the control set was not a small sample of the same process, it was an
unrepresentative one.

The design question I flagged before the run is now answered empirically rather than left
open: decode stochasticity is real and large enough to matter. A "clean pilot" outcome —
which would have made the primary arm a confirmation of determinism — did not occur.

## Disagreement is strongly clustered, which is what the ICC was for

All 32 disagreements fall in **12 of 60 logbooks**. The remaining 48 are perfectly stable.
Whole logbooks flip together: `SabaPivot/repro-human-ai-collaborative-uncertainty-quantification`
went 5/5 `toy`→`verified`; `Srishti280992/repro-diffusion-flow-matching-…` went 5/5
`verified`→`toy`. The judge is not making independent per-claim coin flips — it is settling
into one of two readings of the whole logbook.

Measured ICC(1) is **0.5415**, against the **0.424** standing in `cluster_design.json`. That
0.424 came from the archived cross-judge condition, a different quantity; carrying it into the
primary arm would have understated the design effect by ~22%. This is the specific error the
pilot existed to prevent.

Per band (no significance test performed):

| band | claims | disagreements | rate |
|---|---|---|---|
| m=2 | 77 | 12 | 15.58% |
| m=3-5 | 70 | 8 | 11.43% |
| m=6-10 | 82 | 6 | 7.32% |
| m>10 | 76 | 6 | 7.89% |

Marginals are essentially unchanged between replicates (`verified` 111→115, `toy` 107→106,
`inconclusive` 68→68, `falsified` 19→16), so this is symmetric noise, not a drift toward a label.

## What this does to the 70.1% headline

The instrument has a **measured within-judge disagreement floor of 10.5%** and a test-retest
reliability ceiling of **α = 0.848**. Any cross-judge coefficient must be read against that
ceiling: the judge cannot agree with another judge more reliably than it agrees with itself.
I am not reporting a decomposition of the 70.1% — that needs a model this pilot does not
supply — but the floor is now a measured quantity rather than an assumption.

## Second finding: the archive does not reproduce

Fresh judgments agree with the archived verdicts **76.7%** (rep1) and **76.1%** (rep2) of the
time; α = 0.660 against the archive versus 0.848 retest. Since retest α is *higher* than
archive α, the archive differs from fresh output by more than decode noise alone.

This is the sharper version of the control-arm problem: on the 10 control logbooks, fresh runs
reproduced the archive **48/48, exactly**. On these 60, they reproduce it 76.7% of the time.
Two runs of the same instrument, two very different reproduction rates — the control set is
not representative of the corpus, and any claim resting on it (including the control arm's
"pass") is scoped to those 10 logbooks.

## Why the archive doesn't reproduce — and why that is not protocol infidelity

`mem_60a6cdd2f322` fixed a rule in advance: if the control arm's fresh-vs-fresh α fell well
below its archived-vs-archived α, that would be protocol infidelity — report nothing and
re-recover the prompt. That clause is **not triggered**: the control's fresh runs reproduced its
archived verdicts 48/48 exactly, through the same prompt builder the pilot uses.

But the pilot raises a question the rule did not anticipate, and it needs settling before any
archive comparison is reported. Two *independent draws from one stationary process* must
disagree at the same rate no matter which pair you compare. They don't:

| comparison | disagreement |
|---|---|
| fresh vs fresh (retest) | 10.49% |
| fresh vs archive | **23.28%** |

Ratio **2.22**. The archive is therefore not a draw from the same distribution as current
output. Three candidate explanations were tested:

1. **Model/served-build drift over calendar time — refuted.** `judged_at` does not predict
   archive divergence (Spearman ρ = 0.010, p = 0.94 across 60 logbooks), and the control's
   judging dates (2026-07-20 to 07-27) sit *inside* the pilot's range (07-18 to 08-02). Same
   dates, same model string, one set reproduces perfectly and the other diverges at 23%.
2. **Prompt infidelity — refuted.** The identical builder reproduced the control's archived
   verdicts 48/48. A broken reconstruction would break there too.
3. **The control set is different in kind — supported.** P(0/48 | 23.28%) = **3.0×10⁻⁶**. The
   control's perfect archive reproduction is not a small sample of the pilot's process; it is a
   different process. The leading explanation is item-level degeneracy: the control's logbooks
   are precisely those whose *two archived verdicts already agreed*, which is direct evidence
   their verdict distributions are concentrated. For a point-mass item, any two draws agree
   regardless of regime. Consistent with this, only **23 of 60** pilot logbooks agree with both
   themselves and the archive on every claim, against 10/10 for the control.

I am not claiming this selection is demonstrated. The direct test — archived self-agreement of
duplicate-sha groups that entered the control arm (0/24) versus those that did not (1/10, i.e.
10.0%, close to the pilot's 10.49%) — points the right way but is not significant at this n
(Fisher exact p = 0.294). It is the leading explanation, not a established one.

**The mechanism cannot be identified from the corpus.** `verdicts.json` records only
`zai-org/GLM-5.2` as the model string and carries no provider, endpoint, or served-build field
(logbook-level keys: `claims`, `judged_at`, `model`, `orid`, `overall`, `paper_title`,
`quality`, `sha`, `space_id`). The archive was generated through the *unpinned* router, which
eight providers serve; this pilot pinned baseten. Provider heterogeneity in the archive and
served-build drift predict the same observable and the corpus cannot separate them.

Consequences, stated plainly:

- **The 10.49% retest floor is unaffected.** It is measured fresh-vs-fresh on one pinned route
  within one session. Nothing above bears on it.
- **Archive-comparison claims are not clean.** Any fresh-vs-archive figure conflates decode
  noise with an unidentified regime difference. The paper should not assert "the archive
  reproduces" or quote a reproduction rate as a property of the judge.
- **The control arm's "pass" is narrower than it looked.** It certifies the harness and prompt
  path, which is what a positive control is for. It does not certify that the archive is
  reproducible, and it cannot: its items were incapable of showing the difference.

## Applying the pre-registered decision rule

`mem_60a6cdd2f322`: α_retest ≥ 0.667 confirms the pipeline-non-determinism reframing on
adequate n; 0.40–0.667 means both mechanisms contribute; < 0.40 means within-judge instability
is real.

Measured **α_retest = 0.8477**, cluster-bootstrap CI **0.7457–0.9313**. The threshold is
cleared **even at the lower confidence bound** — so the reframing holds and is not sensitive to
the pilot's precision. The 48.06% cross-logbook figure is driven by genuinely different
reproduction attempts, not by judge instability.

One correction to the record this forces: `mem_02e6e950bd85` states that "verdicts reproduce
exactly under identical input." That was inferred from the control's 48/48 and is **false** —
reproduction under identical input is 89.5%, not 100%. The reframing survives; the claim of
exact determinism does not, and the poster must not make it.

## Schema failure: the silent-backfill defect, caught live

Replicate 2 scored **59/60**. `abhishekkataria16/claim-4ltyJqAHMg-logbook` returned 3 claim
objects for a 4-claim prompt. Under the harness's own semantics (`app.py`: absent index →
`inconclusive`, evidence `""`) that omission would have been **silently backfilled as
`inconclusive` — which matches rep1's verdict for that claim, manufacturing a spurious
agreement**. The defect does not merely lose data; it biases agreement upward. Rate: 1/120
calls (0.83%).

Both readings are reported; they barely differ, but only because n is small:

| treatment | claims | disagreements | rate | α |
|---|---|---|---|---|
| omission excluded (used above) | 305 | 32 | 10.49% | 0.8477 |
| harness backfill applied | 306 | 32 | 10.46% | 0.8483 |

## Sample size: the protocol's figure is optimistic, the full arm is not needed

`rejudgment_power.csv` targets an α half-width of 0.0458 and says α≈0.85 needs 400 claims /
800 rejudgments. The pilot measured α = 0.848 — landing on that row — but achieved a
half-width of **0.0906**, twice the target, because the parametric table did not carry the
measured clustering.

The bootstrap half-width scales as 1/√(clusters); I validated this rather than assuming it:

| clusters | observed half-width | 1/√k prediction from k=60 | ratio |
|---|---|---|---|
| 15 | 0.1897 | 0.1812 | 1.05 |
| 30 | 0.1332 | 0.1281 | 1.04 |
| 45 | 0.1041 | 0.1046 | 1.00 |
| 60 | 0.0906 | 0.0906 | 1.00 |

Extrapolating: **235 logbooks** (≈1,195 claims, 470 calls) reach the 0.0458 target — not the
400 claims the protocol assumed, and not the 2,302 the full arm would collect.

| option | logbooks | total calls | additional calls | α half-width | marginal | cumulative |
|---|---|---|---|---|---|---|
| A. stop at pilot | 60 | 120 | 0 | 0.0906 | $0.00 | $1.21 |
| **B. extend to target** | **235** | **470** | **350** | **0.0458** | **$5.58** | **$6.79** |
| C. full primary arm | 440 | 880 | 760 | 0.0335 | $12.18 | $13.39 |

**Recommendation: option B.** It is the smallest run that meets the precision target the
protocol already committed to, and it leaves ~$13 of the $20 unspent. Option C buys a
half-width of 0.0335 — tighter than the protocol asked for — for 2.2× the marginal cost;
worth it only if you want the primary arm reported at its designed 440 for consistency with
the pre-registered protocol, which is a legitimate reason but a presentational one, not a
statistical one.

## Cost model corrected (again)

The preflight caveat I flagged — that logbook-length representativeness could not be checked
without fetching — materialized. Measured input is **9,489 tokens/logbook** against the
6,961 assumed from the gate's 10, a **1.36× underestimate**; the pilot's logbooks are longer
than the control's.

Cost nevertheless landed at $1.21 against the $1.39 cold estimate, because replicate 2 hit
the prefix cache almost completely (539,424 of 565,247 prompt tokens cached, at $0.14/M
instead of $1.40/M). The token estimate was wrong and the cache credit offset it — those are
two separate facts and the second does not validate the first.

Revised full-arm projection on measured lengths, at the known 440 logbooks / 2,302 claims:
**$14.10** cold (preflight said $10.33).

Note for the record: heavy caching in replicate 2 did **not** make outputs deterministic —
the 10.49% disagreement was measured under near-complete prefix cache hits. Caching the
prefix does not cache the sampled continuation.

## Provenance

- Claim lists: archived (`verdicts.json`), original prompt order, instrument held constant.
- Paper metadata: local challenge index snapshot (`index.json`, 6,341 papers). All 60 titles
  match the archived `paper_title`.
- Logbooks fetched at the **pinned sha** from each verdict record. HEAD had moved on **4 of 60**
  Spaces since judging — the pin was load-bearing, not ceremonial.
- 2 of 60 logbooks hit the 120,000-char harness truncation cap, as the original run would have.
- 0 substitutions: all 60 first-choice logbooks fetched and staged.
- System message checksum-gated at import (`run_pilot.py` imports `run_gate.py`).
- Weights revision remains **unpinnable** at the router; provenance-only.
