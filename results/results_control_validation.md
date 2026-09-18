# Positive-Control Validation and a Second Instrument Change

Prepared while the inference credential was pending. Nothing here required a model call. Inputs: `rejudgment_sample.csv` (control arm, 26 logbooks), `verdicts.json`, harness source `app.py` @ `dc9028d`. Outputs: `gate_set.csv`, `control_logbooks.json`, `control_fetch_meta.json`, `control_validation.json`, `claimset_drift.json`, `alpha_corrected.json`.

## 1. The harness never pinned a revision — but nothing moved

`read_logbook_markdown(space_id)` calls `list_repo_files()` and `hf_hub_download()` at **current HEAD**, not at the `sha` stored in each verdict record. The corpus therefore records a sha it did not actually read from. I re-fetched all 26 control logbooks with `revision=sha` pinned (`fetch_logbooks.py`, harness serialisation reused verbatim) and compared each space's HEAD against its recorded sha:

**0 of 26 spaces have moved since they were judged.** The un-pinned fetch was harmless in practice. Pin anyway for the re-judgment — it converts a lucky property into a guaranteed one.

## 2. Identical-input verification — the control's core premise holds

For the 10 control groups where both members survive, the serialised logbook markdown is **byte-identical between the two spaces** (sha256 of the full serialised string, 10/10). This is the strongest available confirmation that the duplicate-sha stratum is a genuine test–retest condition: identical system message, identical user message, two independent judge calls.

## 3. Three mirrors have been deleted from the Hub

`RepositoryNotFoundError` for three `ICML-2026-agent-repro/*` mirrors: `repro-beyond-accuracy-latent-perturbations-for-cognitive-aware-diagnosis`, `repro-structured-multi-modal-graph-disentanglement-for-psychiatric-diagnosis`, `repro-bioagent-bench-an-ai-agent-evaluation-suite-for-bioinformatics`. Each was one half of a duplicate-sha pair; the surviving `bsenst/*` member fetched cleanly in all three cases. Because the pair shares a sha, the surviving member's pinned content *is* the deleted member's content, so these pairs remain re-runnable — with the caveat that byte-identity is inferred from sha equality rather than verified, as it was for the other ten.

**This is a decay clock.** The corpus is an archive of live Hub spaces; 3 of 26 sampled spaces (11.5%) are already gone roughly six weeks after judging. Re-fetch the full 466-logbook sample before the main run, not after.

## 4. A second instrument change: the claim list, not the prompt

The more consequential finding. `active_claims_map()` (app.py:124) fetches `claims.json` and `claims_anchored.json` from the challenge repo **at judging time**, anchored winning. The claim list is therefore not fixed across the corpus, and it changed independently of the prompt.

Five of the 13 control groups have **identical logbook bytes, the same paper, and completely disjoint claim sets**. Example `68AMoK2YNk`: judged 2026-07-15 with 3 legacy claims, re-judged 2026-07-24 with 5 anchored claims, exact-text intersection **zero**. The anchored sets are rewrites, not additions. All five follow the same chronology — a pre-07-19 member and a post-07-23 member.

Corpus-wide:

| | |
|---|---|
| Papers with >1 logbook | 988 |
| Papers whose claim set changed | **175 (17.7%)** |
| Logbooks in affected papers | **1,623 (25.4% of 6,398)** |
| Switch events | 175, clustered 2026-07-19 → 07-23 (peak 07-20, n=47) |
| Claim-text pairs spanning a claim-set change | **0 of 112,380 (0.00%)** |

**The headline figures are safe**, and for a structural reason worth stating in the paper: pairs are matched on full claim text, and because anchoring rewrote claims wholesale rather than editing them, no pair can straddle the change. The instrument shifted, but it shifted the *items*, and disjoint items never enter the same pair.

Two consequences do follow. First, the effective corpus is two claim-set eras, and 5 of 13 duplicate-sha groups are **not** retest replicates — they are the same logbook judged against different questions. Reporting them as replicates would be wrong. Second, the claim-extraction stage is itself a source of instrument instability upstream of the judge; at 17.7% of multi-logbook papers it deserves a sentence in the limitations, because a reader will otherwise assume the only moving part is the judge.

## 5. Pair-count correction: 112,390 → 112,380

Rebuilding pairs on full claim text gives **112,380**, ten fewer than reported. Cause: the original pairing keyed on a truncated claim string, and for paper `7UEBX1KU1y` that prefix key merged a legacy claim with a *different* anchored claim sharing its opening words ("When the equivalence assumption fails, DPO optimizes relative advantage over the reference policy rather than…", full-text similarity 0.675). That claim then had 11 apparent occurrences instead of 10 — C(11,2) − C(10,2) = **10 spurious pairs**, each comparing two distinct claims.

Recomputed on the corrected set, with claims as units:

| Quantity | Corrected | As published |
|---|---|---|
| Repeat-judged claims | 5,081 | 5,081 |
| Pairs | **112,380** | 112,390 |
| Claim-level α (nominal) | 0.2286 [0.2183, 0.2387] | 0.229 |
| Hard contradictions | 2,893 pairs / 337 claims | identical |
| Pair-level disagreement | 47.9% | — |
| **Headline claim-level disagreement** | **3,563/5,081 = 70.12%** | 70.1% |

Nothing moves at reported precision. The poster's 70.1% is unaffected. `results_evidence_strata.md` carries a correction banner.

## 6. Verified gate set

`gate_set.csv` — **10 logbooks, 5 groups, 24 claim pairs**, every one with pinned content already fetched and byte-identity verified:

| Group | Paper | Claims | Spaces |
|---|---|---|---|
| `09a801d6fb` | `29sn1uqWn3` | 6 | `ICML-2026-agent-repro/…linear-rnns…`, `vimarsh/…linear-rnns…` |
| `0c20cb898d` | `2iDtIht7W4` | 6 | `AceVikings/repro-13581-nb2-lr-optimization`, `AceVikings/…natural-gradient-algorithms` |
| `1d17d5fa14` | `iEtOxzAs51` | 3 | `ICML-2026-agent-repro/…sgera…`, `bsenst/…sgera…` |
| `6b4db58ff5` | `IalpB5Mzaz` | 3 | `bsenst/Time-Conditioned-Foreseeing…`, `bsenst/working` |
| `cf6521b3d3` | `iJDJCO4mji` | 6 | `arthrod/…mmbert-annealed…`, `arthrod/…mmbert-annealed-revision` |

Note group `0c20cb898d`: two spaces under different reproduction titles ("nb2-lr-optimization" and "sketch-and-project analysis") that carry **identical content at the same sha** and were judged against the same paper. The space name is not evidence of what was reproduced — worth a line in the methods.

The 26-logbook control reduces to **20 fetchable logbooks**, of which the 10 above are clean replicates and 10 are same-content-different-questions. Including the three deleted mirrors' surviving halves, the full same-sha stratum's 34 claim pairs decompose as **24 verified + 10 inferred from sha equality** — reconciling exactly with the n = 34 figure in `results_evidence_strata.md`.

## 7. What still requires the credential

Nothing above needed inference. The gate itself does: 10 logbooks × ~1 call each against `router.huggingface.co` with `zai-org/GLM-5.2` at `temperature = 0.1`, inputs already staged in `control_logbooks.json`. Add `HF_TOKEN` and it runs immediately; a revision for the model string still has to be chosen and recorded, since the harness never pinned one.
