# Who Verifies the Verifier?

Measuring LLM-as-judge reliability across 32,688 automated research verdicts.

Edidiong Hector Umoh, M.Res Artificial Intelligence candidate, Capitol
Technology University, Laurel, Maryland. SturdivantAI Lab.

Presented at the AWS-MLU Fall AI Teaching and Research Symposium,
Amazon HQ2, Arlington, Virginia, September 22, 2026.

## What this is

Large language models increasingly score the work of other AI systems.
Published work reports how well such judges agree with human raters. Very
little of it reports whether a judge agrees with itself.

This repository holds the analysis behind a study of one judge model's
self-consistency, using the public verdict log of the 2026 ICML Agent
Reproduction Challenge, plus a controlled re-judgment experiment that
separates instability in the judge from variation in the evidence.

## Findings

Observational arm, from the public verdict log:

- 32,688 claim-level verdicts across 6,398 independent reproduction attempts
- 10,614 unique claims, keyed on paper identifier plus full claim text
- 5,081 claims judged more than once; one claim drew 42 separate verdicts
- 70.1 percent of repeat-judged claims carry at least one disagreeing verdict
- Two readings of one claim differ 48.06 percent of the time, claim-weighted
  (95 percent CI 47.30 to 48.82)
- Claim-weighted Krippendorff's alpha across the four labels is 0.229
  (CI 0.218 to 0.239), against a floor of 0.667 for tentative conclusions

Experimental arm, 236 logbooks re-judged with input held fixed:

- The judge disagreed with itself 8.41 percent of the time
  (CI 6.08 to 11.03), alpha 0.874
- 183 of 236 logbooks were fully stable
- That floor sits 39.6 points below the cross-logbook rate, so most measured
  disagreement is attributable to varying evidence rather than to the judge

## Layout

    analysis/   analysis scripts
    figures/    figures as presented
    artifacts/  derived tables and results the figures and claims rest on
    protocol/   re-judgment protocol, prompts as recovered, prompt-era audit
    results/    written results documents per analysis arm
    data/       pointer to the source corpus, which is not redistributed here
    poster/     presented poster, PDF

## Provenance and attribution

This work analyses artifacts produced by others. The source material is not
the author's own and none of it is redistributed here.

**Verdict corpus.** The 32,688 verdicts were produced by the 2026 ICML Agent
Reproduction Challenge and published at
https://huggingface.co/datasets/ICML-2026-agent-repro/verdicts

Every run in the corpus carries a `judged_at` timestamp. The verdicts
analysed here were issued between 2026-07-08T08:39:09Z and
2026-08-02T01:51:05Z, consistent with the challenge closing August 2 AoE.
The local snapshot used for this analysis dates to 2026-08-30. A pinned
dataset revision will accompany the preprint. The corpus is not committed
to this repository; retrieve it from the source above.

**Judging harness.** The harness that produced the verdicts is the
organizers' code, not the author's, and is not included here:
https://huggingface.co/spaces/ICML-2026-agent-repro/logbook-judge
pinned sha `d0cfe3a7598451aaa02de0b1e25cea3c61e22916`, the commit that
stopped accepting logbooks published or updated after the August 2 AoE
deadline. Architectural claims in the methods section trace to that file.
Readers verifying those claims should read the original rather than a copy.

**Judge prompts.** `protocol/judge_system_verbatim.txt` and
`protocol/recovered_prompt_verbatim.txt` reproduce the organizers' judge
system message and prompt template, recovered as documented in
`protocol/prompt_recovery_report.md`. They are included because a
reliability claim about a judge cannot be checked without the prompt that
drove it. Authorship rests with the challenge organizers.

**Judge model.** `zai-org/GLM-5.2`, called through the Hugging Face router.

## Two properties of the source harness that affect the numbers

**Silent backfill of omitted claims.** When the judge returned no verdict
for a claim, the harness wrote that claim as `inconclusive` with empty
evidence rather than recording an omission. Two runs that both omitted the
same claim therefore register as agreeing, although neither judged it. This
inflates measured agreement, so the disagreement rates reported here are
conservative. The clearest instance is visible in
`figures/fig5_evidence_strata.png`: the stratum where both logbooks ran no
experiments shows 100 percent agreement across 726 verdicts, all
`inconclusive`, with alpha undefined. That cell records the backfill, not
agreement.

**Unpinned claim set.** The harness resolved the claim list at judging time
rather than against a pinned revision, so the item set could change between
judging calls. `protocol/` and `artifacts/prompt_era_check.json` document
what is recoverable about this.

## Corpus integrity

The analysis surfaced defects in the published corpus. 66 of 6,398 runs
carry an empty paper title, and 52 of those hold numeric ICML paper
identifiers where OpenReview identifiers belong. Six claim texts appear
under both identifier forms for the same paper, so a key of paper
identifier plus claim text counts one claim as two.

Excluding all 66 leaves the headline disagreement rate unchanged at two
decimals. Repairing the identifiers instead gives 10,605 unique claims and
5,084 repeat-judged. This repository reports the unrepaired figures, because
the normalization step is not yet implemented or documented. Identifier
normalization is carried forward to the journal submission.

## Reproducibility scope

Read this before cloning. The scripts here are the ones that produced the
committed artifacts, but this is not yet a one-command pipeline. Running the
experimental arm requires Hugging Face credentials and incurs inference
cost, and the observational arm requires the corpus snapshot retrieved
separately. A packaged pipeline with pinned dependencies will accompany the
preprint.

What you can verify today, without credentials: every figure and every
number above against the derived tables in `artifacts/`.

## Citation

Preprint in preparation. Until then, cite the poster:

    Umoh, E. H. (2026). Who verifies the verifier? Measuring LLM-as-judge
    reliability across 32,688 automated research verdicts. Poster presented
    at the AWS-MLU Fall AI Teaching and Research Symposium, Amazon HQ2,
    Arlington, Virginia.

## License

MIT, covering the analysis code and the derived artifacts in this
repository. See LICENSE.

The verdict corpus is not covered by this license. It is the work of the
2026 ICML Agent Reproduction Challenge organizers and is subject to the
terms of the source dataset linked above. The same applies to the judge
prompts reproduced in `protocol/`.
