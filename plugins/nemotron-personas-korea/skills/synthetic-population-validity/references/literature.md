# Literature: synthetic / LLM survey data vs. real populations

The published evidence base behind this skill. Read it when you need a citable
basis for a claim, a second method beyond the bundled metrics, or to reassure a
reader that a failure mode is documented and general, not idiosyncratic to one run.

**Citation note:** a few entries are preprints/working papers whose venue or year
may have moved since this was written (flagged inline). Author lists are
abbreviated. Verify the exact reference before formal publication use.

---

## The convergent finding (what the whole field agrees on)

**Means align, higher moments don't.** Across political science, psychology,
marketing, and NLP, LLM-simulated samples reproduce population *means / marginals*
reasonably but:

1. **Under-disperse** — distinct synthetic units answer too alike (variance
   collapse), and the deficit is *structural*, not a temperature knob.
2. **Distort joint / subgroup structure** — between-unit correlations and
   between-group contrasts are flattened or sign-flipped; a single learned
   correlation gets over-applied.
3. **Skew toward majority / aligned / WEIRD views**, worst for minority and
   sensitive cells.

The named **mechanism** is alignment (RLHF/SFT compresses output diversity and
flattens contrasts). The deficit is **not** fixed by more queries, higher
temperature, or mean-matching fine-tuning. The honest scope is **interpolation
between human-anchored points and relative/ordinal claims — not discovery, not
absolute levels.** Every section below is a facet of this.

---

## Foundational: silicon sampling & algorithmic fidelity

**Argyle, Busby, Fulda, Gubler, Rytting & Wingate (2023). "Out of One, Many: Using
Language Models to Simulate Human Samples." *Political Analysis* 31(3):337–355**
(arXiv:2209.06899).
- Defines **algorithmic fidelity** — the synthetic source mirrors the *pattern of
  relationships* across human subpopulations, not just surface marginals. Bias is
  "fine-grained and demographically correlated," so conditioning on a real backstory
  sub-selects the right conditional (a Simpson's-paradox structure: unconditioned
  output ≠ the conditional mixture). → the named target construct behind the skill's
  whole stack; motivates composition-vs-skew.
- **Four fidelity criteria** (metric-agnostic): social-science Turing test, backward
  continuity (can infer the conditioning input), forward continuity, and **pattern
  correspondence** (association structure matches — validated at the full Cramér's-V
  matrix level, mean Δ −0.026). Best evidence is *repeated support across sources*,
  not one threshold. → level 3b; a concrete diagnostic (compare full association
  matrices, check the model neither flattens nor inflates associations uniformly).
- Scope: silicon samples are for **hypothesis generation, triage, finding confounds
  pre-deployment** — explicitly *not* a replacement for confirmatory human data, and
  *not* individual-level fidelity. → the skill's "honest deliverable."

**Lyman et al. (2025). "Balancing Large Language Model Alignment and Algorithmic
Fidelity in Social Science Research." *Sociological Methods & Research* 54(3):1110–
1155.**
- **Alignment is the mechanism of under-dispersion.** RLHF reduces calibration,
  consistency, and *output variability*; steerability rises but further narrows
  variety (steerable ≠ faithful). → the citation for the σ_between / dehomogenization
  work and the "direct-LLM Likert under-disperses" pitfall.
- Aligned models **compress tails and erase subgroup contrasts** (flatten the human
  party-asymmetry) — "less biased" yet *less representative*. → tells you *where* to
  look for alignment damage: extremity, the negative tail, between-group contrast.
- **Refusals / moralizing are non-random missingness** correlated with the very
  attitude or subgroup measured — silently censors the negative tail. → add a
  refusal/hedge-rate audit and check it isn't correlated with the construct.
- Prompting is brittle and non-transferable across models; run a per-model
  task-completion/refusal pre-flight before any study. → extends reproducibility.

**Bail (2024). "Can Generative AI improve social science?" *PNAS* 121(21):e2314021121.**
- Canonical distortion signature: means ≈ human, **variance understated** *while*
  **extreme attitudes exaggerated**, plus **acquiescence bias** on yes/no items; some
  subgroups (65+, women, minorities) far worse. → variance can be wrong in *both*
  directions; add an item-format (acquiescence) guard.
- **Temporal model drift** is a first-class threat: a pinned-name model is silently
  re-tuned, so a validated recipe decays with no code change; plus intra-model
  stochasticity and prompt-wording sensitivity. → pin version/date, re-validate.
- The **dispersion-vs-reproducibility trade**: lowering temperature to stabilize
  results suppresses the very variance you may be measuring.

**Park et al. (2024). "Generative Agent Simulations of 1,000 People."** (Stanford /
DeepMind; arXiv 2024.)
- **Normalize by the human's own test–retest, not by 100%** — agents reached 0.85 of
  the human self-consistency ceiling. → the "second floor" (human reliability ceiling)
  complementing the perfect-respondent sampling floor.
- **Rich interview transcripts beat demographic-only and self-written persona
  paragraphs — and the gain is *information content, not prose*** (survives 80%
  ablation and a transcript→bullets conversion). → resolves the tension with Li et al.
  below: real informational grounding helps; LLM-invented flourish hurts.
- More conditioning detail **reduces** subgroup-accuracy disparity (DPD), contra the
  "richer persona = more stereotyping" worry. Effect-size replication can be near-
  perfect (r=0.98) even when individual prediction is weak → validity is
  construct-specific.

---

## Psychometrics, validity & response biases

**Ye, Jin, Xie, Zhang & Song (2025). "Large Language Model Psychometrics: A
Systematic Review…" arXiv:2505.08245 (v3).** (Peking University.)
- **Reliability ≠ validity, and α alone is insufficient for LLMs**: a "dual
  instability" (both instrument and subject vary) means high internal consistency can
  hide low *parallel-forms* reliability (prompt sensitivity). Pair Cronbach's α with a
  prompt-perturbation check. → shapes the skill's reliability subsection.
- **LLM-as-population vs LLM-as-individual** changes what α/ICC *mean* — generating a
  population of personas makes α a *population* internal-consistency, not test–retest.
- **Response-set biases** (option-position favoring "A", endorsing both an item and
  its reverse, consistent high/low preference) can produce a marginal that matches by
  artifact; de-biasing position effects once turned political responses into uniform
  noise. → the Step-0 response-set guard.
- Social-desirability skew is directional (inflates extraversion, suppresses
  neuroticism); over-correcting risks homogenization. Forced-choice vs free-form
  diverge → supports comparative/Thurstonian elicitation. IRT/DIF is the endorsed but
  "largely untapped" path for unifying human + LLM on one scale.

**Demszky, Yang, Yeager et al. (2023). "Using large language models in psychology."
*Nature Reviews Psychology* 2:688–701.**
- LLM-derived scores need **construct + predictive/external validity** (cognitive
  pretesting, factor analysis, convergent validation) — passing a CS benchmark ≠
  construct validity. → the theory behind the three-level stack; predictive validity
  is a higher bar (the PPI fallback).
- **Model stochasticity, don't eliminate it** — temp=0 discards legitimate response
  variance; carry it into the analysis as sampling error.
- **Alignment guardrails can hide bias from the validator** (false "unbiased"
  reading) → validate with indirect/behavioral probes, not self-report-of-bias.

---

## Persona pitfalls & diversity collapse

**Li, Chen, Namkoong & Peng (2025). "LLM Generated Persona is a Promise with a
Catch." NeurIPS 2025 (Position Paper Track).**
- **More LLM-authored persona detail → monotonically more bias** (a Meta→Tabular→
  Descriptive ladder drifted a simulated electorate progressively left; universal
  across six base models including Nemotron). → directly relevant to appending
  narrative facets; augmentation can worsen population validity.
- Mechanism: **positive-sentiment homogenization in the persona corpus itself**
  (descriptive personas skew optimistic; life-challenge terms absent). → cheap
  upstream diagnostic: sentiment polarity + word distribution of the persona corpus,
  *before* validating responses.
- Marginals can't reconstruct the true **joint** distribution; LLM augmentation
  invents the missing joint structure *with bias*. → independent corroboration of the
  three-level stack. Report per-topic: variance concentrates on controversial items.

**Wang, Morgenstern & Dickerson (2025). "Large language models that replace human
participants can harmfully misportray and flatten identity groups." *Nature Machine
Intelligence* 7:400–411** (arXiv:2402.01908).
- **Flattening**: sampled LLM responses are less diverse than human in-group
  responses across 4 models and ~all diversity metrics (GPT-4 covers only 3/5 options
  in 100 samples); mechanism = cross-entropy/mode-seeking training. **Raising
  temperature does not fix it** — diversity matches only where output is incoherent.
- **Coverage ≠ diversity** (distinct options produced vs how different they are). →
  a clean name for why marginals can pass while dispersion fails.
- **Misportrayal**: identity-prompted output resembles *out-group imitation*, not
  in-group self-representation, worst for marginalized identities — and *exaggerates*
  between-group differences. With Brand et al. (flattened magnitudes), the common
  thread is **distorted, not absent, group structure — always validate it against
  humans**, don't assume the direction.
- Portable recipe: Welch's t-test on within- vs across-group embedding distances +
  χ² homogeneity; for free-text, use ≥2 diversity metrics (embedding-covariance
  trace/determinant, Vendi score) and require agreement.

---

## Marketing, economics & causal inference

**Brand, Israeli & Ngwe. "Using LLMs for Market Research." SSRN 4395751** (Harvard
Business School working paper; revisions ongoing).
- **Absolute WTP is unreliable; relative/rank structure sometimes survives** — GPT
  gets the sign/order right for some attributes, but 3× overestimates, wrong-signed
  novel attributes, and badly missed brand premia; *"a researcher lacking a human
  benchmark would have had no basis for identifying which estimates were
  unreliable."* → trust ranking/sign, not absolute levels; failures aren't
  self-diagnosing without a human anchor.
- **Simulating an experiment leaks the design**: expanding the prompt's choice set
  changed LLM WTP (fluoride $4.4→$8.2) but not humans' — the prompt framing is itself
  a treatment. → the "simulated experiment ≠ distribution comparison" confound.
- **Interpolation within a category/population (anchored by human fine-tuning) works;
  cross-category transfer flips signs.** Between-group magnitudes collapse while one
  learned correlation is over-applied; mean-matching fine-tuning doesn't recover
  between-group differences → "train a separate model per segment."
- **Query N is not survey N** — SEs shrink toward zero with more queries without
  improving validity; it's a validity, not precision, problem.

**Suh, Jahanparast, Moon, Kang & Chang (2025). "Language Model Fine-Tuning on Scaled
Survey Data for Predicting Distributions of Public Opinions." ACL 2025 (Long
Papers).**
- **Human sampling lower bound** (bootstrap Wasserstein between two human subsamples)
  + uniform upper bound; report *fraction of the closeable gap closed*. → operationalizes
  the floor + holdout, per-group.
- **Prefer an ordinal earth-mover (Wasserstein) over top-choice accuracy** — accuracy
  discards distributional info and rewards over-confident mode-seeking.
- **Steerability/locality test**: predictions for group A should be closer to A's
  humans when A (not B) is prompted, and the gap should scale with true between-group
  distance — base/zero-shot models fail it (no locality ⇒ can't be steered). → the
  "is the conditioning real?" diagnostic. Distributional alignment **interpolates** to
  unseen groups along a trained axis but doesn't extrapolate off it.

**Motoki, Pinho Neto & Rodrigues (2024). "More human than human: measuring ChatGPT
political bias." *Public Choice* 198:3–23.**
- **Dose–response + placebo battery**: a stronger persona should move the
  distribution monotonically; a null/neutral persona should leave it unchanged. →
  reusable falsification that persona-conditioning is real signal, complementing
  Suh's locality test. (Repeated draws + randomized item order + bootstrap is their
  variance-control protocol — matches standard practice.)

**Chapala, Mironov & Deng (2025). "Mitigating Social Desirability Bias in Random
Silicon Sampling." arXiv:2512.22725.** (Eindhoven.)
- **Direct-Likert under-dispersion has model-dependent *shape***: small model →
  mode-collapse; mid model → over-moderation (near-identical answers); large model →
  pole-over-selection (polarization). → inspect *where* mass concentrates, not just
  total spread.
- **De-biasing can move you away from the target**: when the model's underlying belief
  is wrong, reformulation increases spread yet pushes *further* from human data —
  always re-score vs the reference after any debias; more-diverse ≠ closer. Meta-
  instruction priming ("be analytical/sincere") gave no benefit and increased
  uniformity; only neutral third-person *reformulation* of the item helped.

**Sun et al. (2024). "Random Silicon Sampling…" arXiv:2402.18144** (LREC-COLING 2024
— verify venue).
- Empirical **sample-size floor ≈ 200** for distribution replication (broke at n≈108).
- **"Harmlessness" bias collapses sensitive items onto the safe option**, and KL fit
  is *better* for majority (white/male/Republican) and *worse* for minority cells →
  validate per-cell; expect worst fit where it matters most.

**Bisbee et al. — "Artificially Precise Extremism: How Internet-Informed LLMs
Exaggerate Our Differences"** (cited via Xu et al. 2024, "AI for Social Science and
Social Science of AI: A Survey," arXiv:2401.11839): ChatGPT mean scores ≈ human, but
variance / subgroup structure / inferences diverge enough to flip conclusions — the
named prior for "means align, moments don't." Xu et al. also note open-ended
elicitation can rival rating-scale reliability (Kjell et al.), a second argument for
the measurement-reform direction.
