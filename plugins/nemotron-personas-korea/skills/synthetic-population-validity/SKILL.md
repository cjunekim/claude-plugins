---
name: synthetic-population-validity
description: >-
  Methodology and statistics for comparing answers from synthetic respondents (LLM
  personas, simulated survey-takers, any generative population) against a real human
  reference population. Use this whenever you validate, calibrate, or interpret how
  faithfully synthetic/simulated data reproduces a real distribution — comparing
  marginals or means, distribution shape (Cohen's w, chi-square), or joint structure
  (between-unit dispersion / sigma_between, ICC, correlation distortion); deciding
  whether a synthetic-vs-real gap is real signal or sampling noise (the
  perfect-respondent floor); holdout-validating a tuned recipe; separating a sample-
  composition gap from generator skew; or checking regression-to-mean before
  crediting an intervention. TRIGGER even when the user never says "validity" — e.g.
  "do my LLM personas match the real survey data", "is this synthetic sample
  representative", "why does the mean match but the shape look off", "compare the
  simulated responses to the benchmark", "are these persona answers realistic",
  "my synthetic data correlations look wrong". Generalizes beyond Big Five or
  personality — any synthetic-vs-real distribution comparison.
---

# Synthetic-population validity

You have answers from a synthetic source — LLM personas, simulated agents, a
generative model of a population — and a real human reference. The question is
always some form of *"how faithfully does the synthetic reproduce the real, and
what can I honestly claim from it?"* This skill is the methodology for answering
that without fooling yourself, distilled from a multi-week validation campaign.

Two failure modes dominate this work, and almost everything here guards against
one of them:

1. **Declaring victory at the mean.** A generator that compresses variance lands
   its central tendency near the reference while the *shape* is badly wrong and
   the *relationships between variables* are distorted or sign-flipped. The mean is
   the moment least sensitive to how synthetic respondents actually fail.
2. **Tuning inside the noise.** Small samples make every metric jump around; most
   of that movement is sampling noise, not your intervention. Without a noise floor
   you will optimize a number that a *perfect* respondent couldn't beat at your n.

**If you do only one thing:** compare the *whole distribution* to the reference with
Cohen's w (an effect size — not the mean, not a p-value), and gate it on the
perfect-respondent sampling floor — a gap that sits inside the floor band at your n
is sampling noise, not a finding. Report w per variable alongside its floor. That one
loop (`scripts/stats.py` + `scripts/sampling_floor.py`) already defuses both failure
modes; everything below differentiates it.

## The core frame: a three-level validity stack

Validity is nested. Each level is necessary for the one above it and tells you
nothing about it. Passing level N licenses you to *look* at level N+1 — never to
declare done.

| Level | The question | Statistic | Helper | Read it as |
|---|---|---|---|---|
| **1 · Marginal** | Does central tendency match? | Δmean, Δquartile-mass | (trivial) | Necessary, never sufficient |
| **2a · Shape** | Is the whole distribution right? | Cohen's w (+ χ²) | `cohen_w`, `chi_square_vs_reference` | Effect-size tiers, not p |
| **2b · Tail** | *Which* bin is wrong? | per-bin obs vs ref | (tabulate) | Name the deficit (e.g. Q4 missing) |
| **3a · Dispersion** | Do distinct units spread like real? | SD ratio; ICC | `sd_ratio`, `variance_components` | <0.85 ⇒ homogenized |
| **3b · Joint** | Are cross-variable relationships preserved? | mean \|Δr\|, sign flips | `correlation_distortion` | a sign flip ⇒ marginal-only claims |
| **Fallback** | If marginals are unreachable, is the *ordering* right? | Spearman ρ | `signal_correlation` | high ρ ⇒ rank/relative claims OK |

Helpers live in `scripts/stats.py` (domain-agnostic — you pass your own bins,
columns, and reference). Detailed formulas, inputs, and interpretation are in
`references/metric-catalog.md`.

The deepest finding of the campaign: **under-dispersion and correlation-distortion
are the same defect seen two ways.** A generator that collapses distinct units onto
a too-similar, low-dimensional manifold both narrows each marginal (3a) and warps
the joint structure (3b). Don't treat them as separate problems.

## Step 0 — Guards, before any number means anything

A distance is "validity" only under these conditions. Skipping them produces
numbers that look like method signal but are artifacts.

- **Same instrument.** Verify both the synthetic run and the reference used the
  *identical* item wording, anchors, and scoring — not just matching question IDs.
  A single reworded item moved a distribution more than seven generation
  iterations combined, and an instrument mismatch once produced a spurious
  "82% → 12%" headline whose true same-instrument value was "17% → 12%." If they
  differ, your comparison is at most "different surveys differ" — retract any
  method claim. Pin instrument wording as a first-order hyperparameter.
- **Same sampling frame.** The reference's demographic frame and your synthetic
  sample's frame must match, or the delta is a demographic gradient, not fidelity.
- **Get the *in-population* reference up front.** Compare to the real target
  population's distribution — not to "uniform," and not to a foreign norm's
  cut-points. Without the right benchmark you can't tell whether a deviation is the
  source's fault or just the real population's actual shape. n≈100–200 reference
  responses give serviceable per-bin estimates.
- **Screen for response-set artifacts.** A marginal that *matches* the reference can
  be an artifact of acquiescence, option-position bias, or social desirability
  rather than trait signal — de-biasing position effects has turned a "matching"
  political distribution into uniform noise (Ye et al. 2025). Before trusting a
  Cohen's w, confirm reverse-coded items aren't both endorsed, and shuffle option
  order to check the marginal is stable.

## Step 1 — Climb the stack, one rung at a time

Don't compute the whole stack at once — climb it one rung at a time, in the stack's
order, because each rung's result is what tells you whether the next is worth looking
at and what to expect there. Work per variable.

**Rung 1 — marginal (Level 1).** Does central tendency match (Δmean, Δquartile-mass)?
Necessary, never sufficient: a *mismatch* is already a finding (the source is off at the
crudest level), but a *match* is the trap, not a pass — it says nothing about shape or
structure, so it never lets you stop. Either way you climb. (This is why "if you do only
one thing" jumps past it to shape: the marginal in isolation misleads.)

**Rung 2 — shape (Level 2).** Compute Cohen's w against the reference and read it with
the fidelity tiers (`effect_size_tier`), not p-values: with a synthetic source N is
arbitrary, so χ² always rejects and p is uninformative. Tiers: `<0.10` excellent ·
`0.10–0.30` small · `0.30–0.50` medium-low · `0.50–0.80` medium · `>0.80` large
(document as a gap, don't build claims on it). Gate every w on its sampling floor
(Step 2) — a w inside the band is noise, not a verdict. Read the per-bin counts beside
it to name *which* bin is off. This is the first *informative* rung.

**Rung 3 — structure (Level 3).** A clean shape *licenses the next look*, it doesn't end
the inquiry: climb to between-unit dispersion (`sd_ratio`, plus `variance_components` for
ICC) and cross-variable joint structure (`correlation_distortion`). Because
under-dispersion and correlation-distortion are the same defect, a variable that passed
shape can still collapse here. Whether a rung passes or fails, climb to the top — a pass
licenses the next look, a failure is a finding — and report each rung as you reach it.

**Per variable, never only the aggregate.** A mean w can improve while one variable is
χ²-rejected, and self-cancelling per-variable effects hide inside a null aggregate. The
accumulation of these per-variable rungs *is* the validity profile you hand over (see
*The honest deliverable*) — you reach it by climbing, not by dumping all the levels in
one shot.

## Step 2 — Establish the sampling floor BEFORE you iterate

This is the highest-leverage step in the whole workflow. A *flawless* respondent
still scores a nonzero w at finite n, purely from sampling noise. Compute that
floor and you know whether your number is even resolvable from perfection.

```
python scripts/sampling_floor.py --reference ref.json --n 50
```

`ref.json` is your reference vector (or a dict of them for a mean-across-dimensions
floor). The script bootstraps the 95% band of w that a perfect respondent produces
at your n. **A measured score inside the band is indistinguishable from perfect —
stop tuning.** (At n=50 one instrument's floor was [0.148, 0.313]; a measured 0.305
sat inside it. The back half of a 14-iteration campaign had been optimizing inside
that band.)

Then size n so the floor is narrower than the effect you care about:

```
python scripts/sampling_floor.py --reference ref.json --power 50,100,150,200
```

Power here means "floor band narrower than the gap." The same instrument's floor
narrowed from [0.148, 0.313] at n=50 to [0.09, 0.20] at n=123 — only then could a
real gap be separated from luck. (An external anchor: distribution replication
tends to need n ≳ 200 — Sun et al. 2024 — converging with survey-methodology
heuristics.)

**Two floors, not one.** The sampling floor bounds error from *your* sample size;
the **human reference has its own reliability ceiling** — you can't expect the
synthetic source to match the reference better than the reference matches *itself*
on retest. Where the reference has repeat measurements, normalize the metric by the
human test–retest value, not by perfect agreement (Park et al. 2024): "reached 0.85
of the human self-consistency ceiling" is the honest framing, not "85% of perfect."

**Query count is not sample size.** More LLM queries shrink your standard errors
toward zero without improving validity — the binding uncertainty is bias against the
reference, not Monte-Carlo precision (Brand et al.). Don't report LLM-query N as if
it were survey N.

## Step 3 — Holdout above the floor; pair for power, not for proof

- **Small-n per-variable scores are noise-dominated.** Below the floor, *all*
  per-variable spread is sampling luck. One campaign's crown-jewel single-variable
  result (w=0.087) was regression-to-mean on one lucky n=50 draw; the identical
  frozen recipe gave 4× worse on a fresh n=123 sample. **The overfitting tell is
  the spread, not the mean:** a wild per-variable range (0.09–0.44) at small n
  collapsed to a tight band (0.30–0.36) at power while the mean barely moved.
- **Holdout-validate.** Re-run the *frozen* recipe verbatim on a fresh,
  independently drawn sample at an n above the floor. Believe a per-variable win
  only if it survives there.
- **Paired design buys power and cost, not proof.** Lock the unit sample and reuse
  the stages a variant doesn't touch (≈40% fewer generation calls at n=50 × 4
  variants); join on a stable unit ID for paired tests that catch Δw≈0.06. But a
  paired small-n delta is still inside the floor band — pair to *detect*, then
  holdout to *believe*. And bound how many sequential decisions you make against
  one sample; many choices fit that sample's quirks (overfitting).
- **Prefer a few large-n runs over many small-n iterations.** The day-1 large run
  is usually most of the signal; small-n iteration has sharply decreasing returns
  and should test a *named mechanism*, not chase the metric.

## Step 4 — When a metric plateaus: the diagnosis playbook

A plateau is a signal to *decompose*, not to iterate again. Write the gap as a sum
of independent sources and bound each with one cheap experiment — this can *prove
you're done* (or prove which lever is dead) for ~50 model calls, instead of more
blind tuning.

`gap ≈ sampling-floor + composition + source-skew + measurement-act`

- **Sampling floor** (Step 2): is the residual even above the noise?
- **Composition vs source-skew** — run the *identical* recipe on (a) a sample
  stratified to the reference's demographics and (b) a raw/unmatched draw. The
  matched-vs-unmatched delta is the composition effect (who's in the sample); the
  matched arm's residual-above-floor is the source-intrinsic skew (how the
  generator renders the construct at fixed demographics). Composition is usually
  real but secondary; source-skew usually dominates and is invariant to who's in
  the sample. *Still check per-variable* — an aggregate near-null can hide two
  large self-cancelling composition effects.
- **Is the conditioning even real?** Before crediting any composition effect, test
  that the model actually conditions on the subgroup rather than regressing to the
  global mean: (a) *locality* — predictions for group A should sit closer to A's
  humans when A (not B) is in the prompt, and the gap should scale with the true
  human between-group distance (Suh et al. 2025); (b) *dose–response + placebo* — a
  stronger persona should move the distribution monotonically, a null/neutral
  persona should leave it unchanged (Motoki et al. 2024). No locality ⇒ the
  demographic label is decorative and the composition arm is measuring nothing.
- **Alternative measurement act (the "oracle")** — score the same units through a
  second, independent measurement (e.g. an external-observer rating vs a
  first-person self-report) with the *same* scoring pipeline, blind to the
  reference. If the oracle beats the respondent on zero variables, the gap is
  source/composition, not respondent error — stop tuning the respondent. High
  per-unit rank ρ between the two acts confirms the locus is the input/source.
- **Regression-to-mean** — before crediting *any* aggregate move to your
  intervention, run the conditional-shift diagnostic:
  ```
  python scripts/rtm_check.py --csv paired.csv --prev prev_run --curr curr_run
  ```
  Shifts that reverse at the extremes (low rises, high falls) are RTM — the
  intervention left units under-specified and the model fell back to its prior. The
  fix is an *active anchor* (a concrete behavior/instance), not another
  reformulation of passive content.
- **Structural vs framing coupling** — if widening one variable contaminates
  another, test whether it's removable: generate two interventions with *opposite
  content* but matched target-variable SD ratio. Equal contamination ⇒ structural
  entanglement (a wall — stop chasing it with content); content-dependent
  contamination ⇒ a removable framing artifact.
- **Design-space layer audit** — at ~5 stalled iterations, enumerate every layer
  (source → construction → response → anchor-mapping → bin cut) and for each write
  "in scope? if fixed, what is the load-bearing reason?" Components filed as "the
  instrument" often hide a one-line lever.
- **Reform the measurement act (comparative / Thurstonian).** If direct-Likert
  compression is the wall — Step 1 shows the mass piling into the middle and no
  content tuning widens it — stop asking the model for an absolute number. Have it
  produce *comparative* judgments instead (rank or pairwise-compare units, or
  extract behavioral evidence), then recover a latent scale with a comparative-
  judgment model (Thurstone's law of comparative judgment / Bradley–Terry–Luce) and
  cut it at the reference's fixed thresholds. Comparative / forced-choice elicitation
  sidesteps the acquiescence and option-position biases that contaminate absolute
  scale-picking, and comparative whole-sample coding empirically beats independent
  absolute coding. The trade: more defensible, but not always directly w-comparable
  to a self-report baseline. This is the constructive form of the "direct-LLM scale
  picking under-disperses" pitfall below — the root-cause fix, not a patch.

## Pitfalls

- **Within-unit noise levers can't fix between-unit homogenization.** Temperature
  and multi-draw raise σ²_within (and multi-draw averaging *shrinks* SD); neither
  widens σ²_between. To raise between-unit spread, change the *inputs* (reach the
  narrative/content, not just demographics) or the answering structure. The
  homogenization is structural, a documented property of alignment — RLHF reduces
  output diversity and flattens subgroup contrasts (Lyman et al. 2025) — and LLM
  output reaches human-level diversity only at temperatures so high the text becomes
  incoherent (Wang et al. 2025). Note *coverage ≠ diversity*: producing all the
  options (marginal level) does not certify matching the spread (dispersion level).
- **Means align, moments don't — and extremes can be *inflated*, not only
  compressed.** The replicated synthetic signature is matched means with understated
  variance, but sometimes *exaggerated* polar mass — variance can be wrong in both
  directions at once (Bisbee et al.; Bail 2024). Chapala et al. (2025) find the
  failure *shape* is model-dependent: mode-collapse vs over-moderation vs
  polarization. Always inspect *where* the mass sits, not just total spread.
- **More LLM-invented persona detail can worsen population validity.** Appending
  model-authored narrative to personas drifts the population — richer "descriptive"
  personas carry a positive-sentiment optimism skew that propagates into responses
  (Li et al. 2025, shown even on Nemotron personas). This does *not* contradict
  "rich conditioning helps": real *informational* grounding (interview transcripts)
  helps via content and survives style-stripping (Park et al. 2024), but
  LLM-*invented* flourish injects bias. Cheap upstream check: audit the persona
  corpus's sentiment polarity and word distribution *before* validating responses.
- **Simulating an experiment leaks the design.** When an LLM "runs" your A/B test or
  conjoint, the prompt's framing of the choice set is itself a treatment — adding
  attributes changed LLM willingness-to-pay but not humans' (Brand et al.). A
  simulated treatment effect can be a prompt artifact; that's a confounding problem,
  distinct from distribution mismatch.
- **De-biasing can move you *away* from the reference.** When the model's underlying
  belief about a group is wrong, a de-bias / anchor-softening step can increase
  spread yet push the distribution *further* from the human target (Chapala et al.
  2025) — re-score against the reference after *any* such intervention; more-diverse
  ≠ closer. (This project's own anchor-symmetry attempts were falsified the same way.)
- **Calibration is not validation.** Rank-mapping or quantile-matching the
  synthetic distribution onto the reference makes marginals match *by construction*
  and is a fine output/diagnostic layer — but it is never evidence the generator
  improved, and a per-variable calibration *worsens* the joint correlation
  structure. To fix joint structure you need a correlation-aware mapper, not
  per-variable matching.
- **Mechanism-free changes backfire.** An intervention without a named causal
  hypothesis ("make it more moderate") is a guess and often reverses the metric.
  Write the mechanism before the change.
- **Model-specific corrections don't transfer.** A respondent-style layer that
  claws back one model's bias can *worsen* another model that lacks it. Re-validate
  per model.
- **Confounded "kitchen-sink" arms teach nothing.** Change one component per arm so
  the delta is attributable.
- **Direct-LLM scale picking under-disperses.** Letting the model emit the final
  scale number compresses variance and overuses the conservative middle. Prefer
  "model produces qualitative evidence / comparative ranks → local psychometric
  calibration maps to the scale" (the constructive form is *Reform the measurement
  act* in the playbook above).
- **Audit-at-small-n can mispredict at scale.** A conditional rule that looks good
  on a rich-content n=10 audit can over-fire on thin-content units at n=300+.
  Confirm at the target n before adopting.

## The honest deliverable

The durable output of a validation campaign is **not a "best" pipeline** — it's a
*characterized validity profile*: for each variable, whether the synthetic source
can support claims about it, and the mechanism (structural ceiling vs rescuable vs
fragile-to-composition). That profile tells future users what the data can and
can't be used for, and it survives long after any "best condition."

When a structural wall makes marginal match unreachable, state the honest claim
rather than chasing an impossible target:
- **Rank fidelity** — report Spearman ρ ("orders units like reality, ρ=0.89") and
  scope conclusions to relative/ordinal claims.
- **Calibration anchoring (PPI)** — use the real responses as a
  prediction-powered-inference anchor so synthetic estimates carry a calibrated CI,
  instead of prompt-engineering the metric toward a target the approach
  structurally can't hit.
- **Interpolation, not extrapolation** — synthetic sources reliably *interpolate
  between dimensions anchored by real data* (unseen demographic cells along a
  trained axis — Suh et al. 2025; within-category willingness-to-pay — Brand et al.)
  and fail to *extrapolate off* them (new categories, un-anchored between-group
  structure, novel parameters). Use them for hypothesis generation, triage, and
  relative/ordinal claims; not for discovery or absolute levels lacking a human
  anchor. In marketing terms: trust the *ranking* of products or the *sign* of a
  price effect, not the absolute WTP.

## Reliability is a different axis

With the validity axis complete — what to compare, whether the gap is real, what you
can claim — there is a second, parallel axis the synthetic source should also
reproduce: reliability (is the measurement internally consistent / reproducible?).
It's **not** a higher level of the stack; a perfectly reliable source can be reliably
wrong. Two checks, both framed as a *synth-vs-real comparison*:

- **Internal consistency** — `cronbach_alpha` on the item scores, synth α vs real
  α. A synthetic source that collapses units onto a low-dimensional manifold
  *inflates* α (everyone answers each item alike — the within-scale face of
  `correlation_distortion`); independent per-item LLM noise deflates it. With LLMs α
  is necessary-not-sufficient: high internal consistency routinely coexists with low
  *parallel-forms* reliability, so pair it with a prompt-perturbation check —
  re-elicit under reworded prompts and see if the distribution moves (Ye et al.
  2025). Label your α as *population* internal-consistency, not single-unit
  test–retest (you generated a population of personas).
- **Agreement** — `krippendorff_alpha` (nominal/ordinal/interval, handles missing).
  Two uses: the categorical/ordinal analog of ICC for draw-to-draw reproducibility
  (raters = repeat draws of a unit); and chance-corrected per-unit synth-vs-real
  agreement when you hold *unit-linked* ground truth (raters = {synth, real}) — a
  stronger claim than distribution match, but it needs a real answer per synthetic
  unit, not just a reference distribution.

The alignment pressure that flattens the distribution can also *defeat naive bias
checks*, so validate with indirect/behavioral probes, not self-report (Demszky et
al. 2023).

## Reproducibility

Persist per run, or comparisons across iterations silently break: generator/model
ID + prompt hash, per-item instrument wording, demographic stratification (target +
realized), seed, and data-source SHA. Pin explicit kwargs in reproduction scripts —
a changed default silently alters re-run artifacts. Pin the model *version/date*,
not just the name: a pinned-name model is silently re-tuned over time, so a
validated recipe can decay with no code change (Bail 2024) — re-validate against the
reference after any model update.

## Grounding in the literature

These methods aren't idiosyncratic to one project — the published record on
synthetic / LLM survey data converges on the same signature: **means align, higher
moments don't.** LLM samples match marginals while under-dispersing, distorting
joint / subgroup structure, and skewing toward majority / aligned views; the
mechanism is alignment (RLHF compresses diversity and flattens contrasts); it is
*not* fixable by more queries, higher temperature, or mean-matching fine-tuning; and
the data is valid for interpolation / triage, not discovery. `references/literature.md`
holds the citations and per-paper takeaways — Argyle's algorithmic-fidelity criteria,
the marketing-WTP and causal-confounding caveats, the reliability-vs-validity
distinction, and the diversity-collapse evidence — and is worth reading when you need
a citable basis or a second method (Cramér's-V matrix comparison, Jensen–Shannon
divergence, embedding-space diversity, the steerability/locality test).

## Bundled resources

- `scripts/stats.py` — the metric menu: `cohen_w`, `chi_square_vs_reference`,
  `effect_size_tier`, `sd_ratio`, `variance_components` (ICC), `correlation_distortion`,
  `signal_correlation`, and the reliability axis `cronbach_alpha`, `krippendorff_alpha`.
  Pure functions over your arrays; import or read for the math.
- `scripts/sampling_floor.py` — the perfect-respondent floor band and n-power curve.
- `scripts/rtm_check.py` — the regression-to-mean conditional-shift diagnostic.
- `references/metric-catalog.md` — per-metric formula, required input shape,
  interpretation thresholds, and gotchas. Read it when you need the detail behind a
  helper or are choosing which statistic fits your data.
- `references/literature.md` — the published evidence base: citations, per-paper
  transferable takeaways, and the convergent failure-mode synthesis.
