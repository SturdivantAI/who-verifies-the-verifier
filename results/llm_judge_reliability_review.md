# LLM-as-Judge Reliability and Evaluation-Instrument Validity in Automated Research Assessment

**A structured review of the 2025–2026 literature, with comparators for a 70.1% disagreement rate across 5,084 multiply-judged claims**

> **Superseded in part.** The design specification received after drafting establishes that the 70.1% figure is *within-judge* instability (one judge model, GLM-5.2, re-encountering the same claim across logbooks), not inter-judge disagreement. The panel-inflation argument in Section 2 and the comparator framing in Section 1 are withdrawn and replaced by `addendum_within_judge_reframing.md`. Sections 3-8 and the comparator table are unaffected: they characterise the literature, not the corpus.

---

## Scope and a note on the "high impact factor" criterion

The request was for high-impact-factor papers from the last 18 months. That criterion does not partition this literature well, and saying so is part of the finding. The methodological core of LLM-as-Judge reliability research is published on arXiv and in ACL/NeurIPS-family proceedings, not in journals with assigned impact factors. Of the 30 studies in the flagged comparator table, 6 are peer-reviewed at the time of retrieval — among them *npj Digital Medicine*, *JMIR AI*, *PACM on Software Engineering*, and ACM SIGIR/CIKM proceedings — and 24 are preprints. Restricting to indexed journals would have excluded almost every study that reports the quantities you need, including the largest judge meta-evaluation retrieved (~541,000 judgments) and every direct analogue to automated research-claim verification.

I therefore ranked by citation velocity, venue tier, and presence of extractable reliability statistics rather than by impact factor, and I have marked peer-review status per row so the evidentiary weight is visible. Retrieval covered March 2025 to September 2026 across OpenAlex, arXiv, and Crossref; the screening funnel and the ranking are described in the method note at the end.

---

## 1. The headline: your 70.1% is not an outlier, but it is not directly comparable either

Two things are true at once, and separating them is the most useful thing this review can do for your poster.

**First, on the raw numbers, 70.1% disagreement sits well above the pairwise band the field reports.** Across the studies retrieved, cross-judge and judge–human agreement clusters between roughly 51% and 82%, implying disagreement of 18–49%. Yagubyan (2026) reports cross-judge agreement of 76% (κ = 0.51) on open-ended QA; Soumik (2026) reaches 71.0% agreement (κ = 0.549) with the best bias-mitigated configuration; Dussert (2026) spans 51.5% to 69.1% across open models on runtime compliance monitoring; Verma et al. (2026) find that on hard queries without ground truth, six judges of widely different scale all converge into a narrow 77–82% band. Only the hardest tasks fall lower: on evidence-based research agents, L. Wang et al. (2026) report best-model accuracies below 55%, with the worst performance on evidence verification specifically.

**Second, the comparison is almost certainly not like-for-like, and the direction of the artefact is knowable.** A pairwise agreement rate and a panel-level "at least one judge disagreed" rate are different quantities, and they diverge fast in the number of judges. If your 5,084 claims were each seen by k judges and a claim counts as disagreed when any pair diverges, then even excellent pairwise agreement produces a high panel rate. Under an independence assumption — indicative rather than exact, since judge errors are correlated — 76% pairwise agreement yields 56.1% at k = 3 and 80.7% at k = 4; 82% pairwise yields 69.6% at k = 4. Your 70.1% is squarely inside that region.

![Positioning the 70.1% disagreement rate against the 2025–2026 literature. Left: reported disagreement rates, with LLM judges in dark grey and human rater panels in blue; ranges show reported spans across models or conditions. Right: the probability that at least one pair of judges disagrees on a claim, as a function of panel size, for three levels of pairwise agreement (independence assumed).]({{artifact:art_a27a7dd8-8fe6-4af1-b10e-c348ec55beb4}})

The practical implication for the poster is a single sentence in your methods: state the panel size and the disagreement definition. If it is any-pair disagreement at k ≥ 3, then 70.1% corresponds to pairwise agreement in the high seventies to low eighties — which is to say, squarely at the field's current state of the art rather than below it. If it is a genuine pairwise rate at k = 2, it is an unusually low-agreement corpus and that itself is the finding, most plausibly attributable to construct subjectivity (Section 3).

---

## 2. Chance correction, and why raw agreement rates flatter judges

The largest meta-evaluation retrieved makes this the central methodological point. Norman et al. (2026) ran 21 judges across nine providers over 118 experimental runs and roughly 541,000 judgments on MT-Bench, JudgeBench, and RewardBench, and found that moving from exact-match agreement to Cohen's κ deflates measured judge performance by 33–41 percentage points on MT-Bench. Any raw agreement figure — yours included — carries this inflation when the label distribution is skewed.

The same study documents what it calls a consistency–bias dissociation: judges achieve test–retest reliability above 0.95 while simultaneously exhibiting position bias above 0.10. A judge can be almost perfectly repeatable and still systematically wrong in the same direction every time. This is the single most important caution against reading high self-consistency as evidence of validity.

Two further studies decompose disagreement into components that behave differently. Y. Wang et al. (2025) separate protocol-induced logical inconsistency from genuine judgment disagreement, measuring a Score-Comparison inconsistency rate of 23.32% and a Pairwise Transitivity inconsistency rate of 15.22% under a Llama-3.1-70B judge, and reducing them to 14.89% and 4.40% respectively with a modified scoring protocol. Yagubyan (2026) separates between-judge from within-judge variation: preferences flip on 13.6% of items on average across repeated runs, 28% of questions exceed a 20% flip rate, and the worst reaches 56%; paraphrasing the prompt alone changes the majority verdict in 25% of cases.

**For your corpus:** report both a raw disagreement rate and a chance-corrected coefficient, and if you have any repeated judgments, report a within-judge flip rate separately from the between-judge rate. The literature now expects that decomposition, and reporting only the raw figure invites the reviewer question that Norman et al. (2026) were written to answer.

---

## 3. Reliability without validity: the dominant theme of 2026

The field's centre of gravity has moved from "do judges agree with humans?" to "does agreement mean anything?" Four independent lines of evidence converge.

Mukherjee et al. (2026) evaluated 42 judges across four domains and eight languages and found that judges agree with each other about as much as humans agree with each other — but reach only 58–66% of human agreement levels on subjective rubrics. Inter-LLM consensus, they argue, is not human alignment; it is a shared prior.

Keith (2025), in *Electronics*, provides the cleanest quantitative form of the dissociation: intraclass correlation above 0.92 among LLM judges, but Pearson correlation with the ground-truth construct of at most 0.65. The judges are reliable with respect to each other and only moderately valid with respect to the thing being measured.

J. Chen et al. (2026) attack the construct directly. Holding invariance matched, judges average a sensitivity score of 0.945 but a robustness score of 0.319 — and, most damningly, surface-only predictors that never see the substantive content reproduce 55–67% of judge labels across five public label sets, including 67.4% of MT-Bench human votes. A majority of what looks like agreement is agreement about surface form.

Baumann et al. (2026) show the failure mode operationally in peer review. Comparing human- and AI-generated ICLR 2026 reviews, they identify a hivemind effect of excessive agreement within and across papers that collapses perspective diversity, and demonstrate that AI review scores are gameable through paper laundering: prompting an LLM to rewrite a paper raises AI reviewer scores without changing the science. High inter-judge agreement is compatible with — and here partly caused by — a shared insensitivity to substance.

**For your corpus:** this reframes a high disagreement rate as potentially reassuring. Low agreement among judges is a problem only if you have independent evidence that the construct is objectively determinable. If a substantial share of judge agreement in the literature is surface-form artefact, then a corpus that resists easy agreement may be measuring something harder and more real. The defensible claim is about the instrument, not the judges.

---

## 4. Where the disagreement actually lives: the human ceiling

This is the strongest argument available to you, and it is not made often enough.

The human baseline for judging scientific merit is very weak. Mao (2026) ran a seven-rater study on astronomy research questions with two blinded human raters and five judge models; the two careful humans agree at Cohen's κ = 0.17, and every judge model matches the professional annotator as well or better (κ = 0.17–0.26). Modgil (2026) had three trained annotators apply a single rubric to a 56-action trajectory and obtained a Krippendorff's α of +0.047 for intervention location, with a best pairwise Cohen's κ of +0.349 — agreement barely distinguishable from chance on a construct the annotators had been trained on.

Y. Chen et al. (2025), in *JMIR AI*, give the most direct disagreement-rate comparator in the retrieved set: average agreement of 19.2% among all experts on medical text summarisation quality, rising to 54% among groups of three, while GPT-4 agreed with at least one expert 83.06% of the time. An 80.8% disagreement rate among human domain experts exceeds your 70.1% by more than ten points.

Thakur et al. (2025), in SIGIR proceedings, report that on TREC 2024 RAG support assessment an independent human judge correlates better with GPT-4o than with another human judge. Meisenbacher et al. (2025), across ten datasets, thirteen LLMs and 677 human participants, locate the problem in the construct rather than the rater: inter-human agreement on textual privacy perception is generally low.

The background anchor is worth citing even though it predates the window. Cortes and Lawrence (2021), revisiting the 2014 NeurIPS consistency experiment, determine that 50% of the variation in reviewer quality scores was subjective in origin, and that for accepted papers there is no correlation between quality scores and eventual citation impact. Aczél et al. (2025), in *PNAS*, frame the systemic version of the same problem and note that fair assessment of peer review requires more comprehensive data than the community currently has.

**For your corpus:** the comparator that matters is not "how well do judges agree with each other" but "how well would human experts agree on these same 5,084 claims". The literature suggests the honest answer is: probably not much better, and possibly worse. If you can hand-adjudicate even a small stratified sample with two independent human raters and report a κ, that single number will do more for the poster's argument than any additional judge configuration.

---

## 5. Bias: what replicates and what does not

**Position bias** is the most consistently replicated. Norman et al. (2026) measure it above 0.10 in production judges even at test–retest reliability above 0.95. Yagubyan (2026) finds a first-position preference producing an A-majority in 72% of items (p = .024).

**Language and locale bias** is large and largely invisible to agreement metrics. Zhou et al. (2026) report evaluators exceeding 90% pairwise accuracy while producing up to a 43-percentage-point difference in acceptance rate across languages. KC (2026) finds order consistency of 0.480 — near-random — for Swahili agent trajectories. Fernandes et al. (2026), on Portuguese legal retrieval, find only fair-to-moderate pair-level agreement (κ = 0.32–0.53) with human assessors, yet system-level rankings survive at Kendall's τ ≥ 0.90 for nDCG@10 and MRR.

**Self-preference bias** is real but contested in magnitude. Pombal et al. (2026) show it survives fully objective rubrics: on IFEval and LiveCodeBench, judges are more than 50% more likely to incorrectly mark a failed programmatic rubric as satisfied when the output is their own. Roytburg et al. (2026), however, re-analyse prior self-preference findings against an evaluator-quality null and find that only 51% of examples retain significance, covering 89.6% of the self-preference probability mass. Cite both; the honest summary is that self-preference exists and has been overstated.

**For your corpus:** the Fernandes et al. (2026) result is the one to hold onto. Item-level disagreement of the magnitude you observe can coexist with stable aggregate rankings. If your downstream use is comparative rather than absolute, demonstrate rank stability under judge resampling and the 70.1% becomes a bounded, reportable limitation rather than a threat to the conclusions.

---

## 6. Automated research assessment specifically

This is the closest cluster to your testbed, and it is small.

Zhao et al. (2026) built a battle-style arena for literature-review agents with approximately 3,000 expert judgments across five review-specific criteria. Off-the-shelf LLM judges correlate with experts at Spearman ρ = 0.467, with the misalignment concentrated on synthesis-heavy criteria such as paper structure and research suggestions; a calibrated judge trained on the arena data reaches ρ = 0.78, comparable to inter-expert consistency. Calibration, not model scale, closed the gap. The same study puts the underlying task in perspective: the strongest current systems win only 23.0% of decisive matches against human-written drafts on overall utility.

Ravideshik and Kejriwal (2026) benchmarked three LLM reviewers (GPT-5.4, Gemini, Claude) over 60 papers generated by four autonomous AI-scientist frameworks plus 15 benchmark papers, across four dimensions, and found the disagreement is dominated by which judges are paired: Gemini and Claude correlate at ρ = 0.907 (p < .001), while GPT-5.4 diverges at ρ ≈ 0.32. Z. Chen et al. (2026), on LLM-generated research ideas assessed against expert battle-style preferences, find a best-judge soft accuracy of 72.56% on overall quality.

Pisupati et al. (2026) show that agreement fractures by sub-construct rather than uniformly: with human inter-annotator agreement at Krippendorff's α = 0.78, the strongest judge reaches roughly 88% agreement on *where* an error occurred but only about 65% on *reasoning quality* — a 23-point spread within one task.

**For your corpus:** three concrete moves follow. Report per-dimension disagreement rather than a single pooled 70.1%, since Pisupati et al. (2026) predict wide variation by sub-construct. Report which judge pairs drive the disagreement, since Ravideshik and Kejriwal (2026) show pairing dominates. And note that Zhao et al. (2026) demonstrate calibration recovering ρ from 0.467 to 0.78 — the strongest available evidence that your rate is a property of uncalibrated judges rather than of the task.

---

## 7. What reduces disagreement, and by how much

The remediation literature converges on modest, reproducible gains. Lail and Markham (2026) evaluate ensembling, criteria injection, calibration and escalation on RewardBench 2 and reach up to 85.8% judge accuracy, a gain of 13.5 percentage points over baseline. Mahmood et al. (2026) achieve label-free calibration across seven languages and 10,500 instances of M-RewardBench, raising panel agreement with human gold from 68.7% to 76.6% (+7.9 pp, 95% CI [6.0, 9.9]). Y. Wang et al. (2025) cut protocol-induced inconsistency by roughly a third to two-thirds through scoring-protocol changes alone. Croxford et al. (2025), in *npj Digital Medicine*, mark the practical upper bound with a tightly constrained clinical rubric: ICC 0.818 (95% CI [0.772, 0.854]) against human evaluators, with a median score difference of zero.

The ceiling is real. Verma et al. (2026) show all six judges converging to 77–82% on hard queries regardless of scale, and Zhou et al. (2025) quantify the gap against humans directly on role-play identity: the best LLMs reach about 69% where humans reach 90.8%.

---

## 8. Gaps this review found, and where your work lands

Four gaps are visible in the retrieved corpus, and your poster addresses at least two.

1. **Chance-corrected agreement is rarely reported for multi-judge panels.** Most studies report pairwise agreement or a single κ. Norman et al. (2026) establish that the correction matters by 33–41 points, but panel-level chance correction — Fleiss' κ or Krippendorff's α across k > 2 judges — is almost absent. A corpus of 5,084 multiply-judged claims is exactly the design that could supply it.
2. **Scale.** Most reliability studies run on hundreds to low thousands of judgments on public benchmarks. Aside from Norman et al. (2026), few operate at the scale of 32,688 verdicts on a single applied corpus, and none retrieved does so on research-claim verification.
3. **Temporal stability is unmeasured.** No retrieved study reports test–retest reliability across model *versions* over calendar time, which is the reliability question that matters for any deployed verification pipeline and for the V&V transferability argument in your thesis.
4. **Nothing on judge reliability in multi-step agentic decision support.** The agentic work retrieved — Verma et al. (2026), Pisupati et al. (2026), KC (2026) — evaluates trajectories and tool calls, not the reliability of a verifier embedded in a multi-agent decision loop. This is the gap your MoCo Lantern testbed sits in.

---

The full flagged comparator table — 30 studies with domain, design, metric, reported value, DOI, peer-review status, and a stated reason each is a comparator — is in `llm_judge_reliability_comparators.csv`. The panel-size calculation is in `panel_inflation_bridge.csv`.

---

## Method note

Retrieval ran 10 September 2026 over OpenAlex, arXiv, and Crossref, covering publication dates from 1 March 2025 to 30 September 2026 (an 18-month window plus a short forward margin). Twenty-six topical queries plus a targeted sweep for canonical judge-reliability work and the automated-peer-review cluster returned 411 unique records after title and DOI deduplication. A two-part keyword gate requiring both an evaluator concept and a reliability concept, followed by LLM-assisted triage on 500 candidates and manual review of extracted numeric sentences, produced the 30-study comparator set.

Every quantitative value in this review and in the comparator table was extracted from the retrieved abstract or record, not recalled. Every DOI in the comparator table was verified programmatically by resolving it and confirming the returned title matches the claimed title under normalisation; all 30 resolved correctly. Three records that could not be assigned a verifiable DOI were dropped from the citation set rather than cited on an unverified identifier. Citation counts are OpenAlex counts at retrieval time and are low for 2026 preprints by construction; they were used for ranking, not as a quality claim.

The independence assumption in the panel-inflation calculation of Section 1 is indicative only. Judge errors are positively correlated in practice — Mukherjee et al. (2026) and Baumann et al. (2026) both document shared priors across judges — so the true panel-level disagreement rate for a given pairwise agreement will be *lower* than the curves shown. That makes the inference conservative in your favour: reproducing 70.1% at k = 3–4 requires pairwise agreement at or below the 76–82% band, not above it.

---

## References

Aczél, B., Barwich, A., Diekman, A. B., Fishbach, A., Goldstone, R. L., & Gómez, P. (2025). The present and future of peer review: Ideas, interventions, and evidence. *Proceedings of the National Academy of Sciences*. https://doi.org/10.1073/pnas.2401232121

Baumann, J., Pei, J., Koyejo, S., & Hovy, D. (2026). Stop Automating Peer Review Without Rigorous Evaluation. *arXiv*. https://doi.org/10.48550/arxiv.2605.03202

Chen, J., Chen, W., Lin, Z., & Vong, C. M. (2026). A Judge Should Know What Changed:Construct Validity for LLM-as-a-Judge Evaluation. *arXiv*. https://doi.org/10.48550/arXiv.2608.24419

Chen, Y., Wen, B., & Zulkernine, F. (2025). A Multiagent Summarization and Auto-Evaluation Framework for Medical Text: Development and Evaluation Study. *JMIR AI*. https://doi.org/10.2196/75932

Chen, Z., Zhao, K., Fu, J., Liang, D., Wu, Y., Li, J., Xue, H., Zeng, X., Zhen, Y., Xu, F., & Li, Y. (2026). Ideation Arena: Evaluating LLM Generated Research Ideas with Battle-style Human Expert Assessment. *arXiv*. https://doi.org/10.48550/arxiv.2608.29696

Cortes, C., & Lawrence, N. D. (2021). Inconsistency in conference peer review: Revisiting the 2014 NeurIPS experiment. *arXiv*. https://doi.org/10.48550/arXiv.2109.09774

Croxford, E., Gao, Y., First, E., Pellegrino, N., Schnier, M., Caskey, J., Oguss, M., Wills, G., Chen, G., Dligach, D., Churpek, M. M., & Mayampurath, A. (2025). Evaluating clinical AI summaries with large language models as judges. *npj Digital Medicine*. https://doi.org/10.1038/s41746-025-02005-2

Dussert, J. (2026). Who judges the judges? Governance from metrics: a runtime framework for continuous LLM compliance monitoring. *arXiv*. https://doi.org/10.48550/arXiv.2605.24737

Fernandes, L. C., Castro, M. V. B. D., Ribeiro, L. D. S., Pacheco, L. A. D. S., & Sandes, E. F. D. O. (2026). NormasTCU --- A Brazilian Portuguese IR Dataset and an Evaluation of LLM-as-a-Judge for Relevance Assessment. *arXiv*. https://doi.org/10.48550/arXiv.2608.27746

KC, S. (2026). BabelJudge: Measuring LLM-as-a-Judge Reliability Across Languages and Agent Trajectories. *arXiv*. https://doi.org/10.48550/arXiv.2606.22329

Keith, B. (2025). LLM-as-a-Judge Approaches as Proxies for Mathematical Coherence in Narrative Extraction. *Electronics*. https://doi.org/10.3390/electronics14132735

Lail, R., & Markham, L. (2026). On Cost-Effective LLM-as-a-Judge Improvement Techniques. *arXiv*. https://doi.org/10.48550/arXiv.2604.13717

Mahmood, A., Abdaljalil, S., & Kurban, H. (2026). Rank Reversal in Multilingual LLM Judges: A Label-Free Double-Centering Calibrator. *arXiv*. https://doi.org/10.48550/arXiv.2608.22432

Mao, H. (2026). Historical Backtesting for Scientific Question Discovery: A Protocol and Astronomy Pilot. *arXiv*. https://doi.org/10.48550/arXiv.2608.16795

Meisenbacher, S., Klymenko, A., & Matthes, F. (2025). LLM-as-a-Judge for Privacy Evaluation? Exploring the Alignment of Human and LLM Perceptions of Privacy in Textual Data. *arXiv*. https://doi.org/10.1145/3733816.3760760

Modgil, M. (2026). The Saturation Trap and the Subjectivity of Intervention Timing: Why Affect-Based Triggers and LLM Judges Fail to Time Interventions on Autonomous Agents. *arXiv*. https://doi.org/10.48550/arXiv.2606.04296

Mukherjee, S., Hamna, H., Bali, K., & Sitaram, S. (2026). The Geometry of LLM-as-Judge: Why Inter-LLM Consensus Is Not Human Alignment. *arXiv*. https://doi.org/10.48550/arxiv.2606.03043

Norman, J. D., Rivera, M. U., & Hughes, D. A. (2026). Reliability without Validity: A Systematic, Large-Scale Evaluation of LLM-as-a-Judge Models Across Agreement, Consistency, and Bias. *arXiv*. https://doi.org/10.48550/arXiv.2606.19544

Pisupati, S., Broomfield, H., Choi, E., Calvi, A., Wang, C., Engeler, R., Bartolo, M., & Lewis, P. (2026). Counsel: A Meta-Evaluation Dataset for Agentic Tasks. *arXiv*. https://doi.org/10.48550/arXiv.2606.21627

Pombal, J., Rei, R., & Martins, A. F. T. (2026). Self-Preference Bias in Rubric-Based Evaluation of Large Language Models. *arXiv*. https://doi.org/10.48550/arXiv.2604.06996

Ravideshik, V. L., & Kejriwal, M. (2026). Can AI Evaluate AI Scientists? A Benchmarking Study of Autonomous Research Generation Systems Using Automated Multi-Model Review. *arXiv*. https://doi.org/10.13140/rg.2.2.27158.31045

Roytburg, D., Bozoukov, M., Nguyen, M., Barzdukas, J., Puig-Hall, M., & Oozeer, N. (2026). Are LLM Evaluators Really Narcissists? Sanity Checking Self-Preference Evaluations. *arXiv*. https://doi.org/10.48550/arXiv.2601.22548

Sarkar, D. (2026). A Four-Axis Trustworthiness Benchmark for LLM-as-Judge in Principle-Based Regulation. *arXiv*. https://doi.org/10.48550/arXiv.2608.14329

Soumik, S. K. (2026). Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge Pipelines. *arXiv*. https://doi.org/10.48550/arXiv.2604.23178

Thakur, N., Pradeep, R., Upadhyay, S., Campos, D., Craswell, N., Soboroff, I., Dang, H. T., & Lin, J. (2025). Assessing Support for the TREC 2024 RAG Track: A Large-Scale Comparative Study of LLM and Human Evaluations. *arXiv*. https://doi.org/10.1145/3726302.3730165

Verma, A., Saha, A. K., Subramanian, S., & Aluru, S. H. (2026). AgentJudgeBench: A Multi-Difficulty Benchmark for Evaluating LLM Judges on Agentic Tool-Calling. *arXiv*. https://doi.org/10.48550/arXiv.2608.26623

Wang, L., He, Y., Chen, P., Yehudai, A., Liu, Y., Ying, R., Shmueli-Scheuer, M., & Cohan, A. (2026). Time to REFLECT: Can We Trust LLM Judges for Evidence-based Research Agents?. *arXiv*. https://doi.org/10.48550/arxiv.2605.19196

Wang, R., Guo, J., Gao, C., Fan, G., Chong, C. Y., & Xia, X. (2025). Can LLMs Replace Human Evaluators? An Empirical Study of LLM-as-a-Judge in Software Engineering. *Proceedings of the ACM on software engineering.*. https://doi.org/10.1145/3728963

Wang, Y., Song, Y., Zhu, T., Zhang, X., Yu, Z., Chen, H., Song, C., Wang, Q., Wang, C., Wu, Z., Dai, X., & Zhang, Y. (2025). TrustJudge: Inconsistencies of LLM-as-a-Judge and How to Alleviate Them. *arXiv*. https://doi.org/10.48550/arXiv.2509.21117

Yagubyan, A. (2026). The Coin Flip Judge? Reliability and Bias in LLM-as-a-Judge Evaluation. *arXiv*. https://doi.org/10.48550/arXiv.2606.13685

Zhao, R., Chen, Z. Z., Liu, X., Xue, H., Liang, D., Fu, J., YanBiao, W., Zhen, Y., Xu, F., & Li, Y. (2026). LitReview Arena: Evaluating Literature Review Agents with Battle-Style Peer Review Platform. *arXiv*. https://doi.org/10.48550/arxiv.2608.21374

Zhou, E., Resck, L., Hui, Z., & Korhonen, A. (2026). Lower-Resource, Higher Scores: Language Bias in LLM Evaluators. *arXiv*. https://doi.org/10.48550/arXiv.2607.14480

Zhou, L., Zhang, J., Gao, J., Jiang, M., & Wang, D. (2025). PersonaEval: Are LLM Evaluators Human Enough to Judge Role-Play?. *arXiv*. https://doi.org/10.48550/arXiv.2508.10014
