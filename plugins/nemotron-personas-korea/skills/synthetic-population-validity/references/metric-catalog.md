# Metric catalog

Per-metric detail behind the helpers in `scripts/stats.py`, `scripts/sampling_floor.py`,
and `scripts/rtm_check.py`. Read the entry for a metric when you need its exact
formula, the data shape it expects, or how to read its value.

All helpers are domain-agnostic: you pass your own bins, columns, and reference.
None of them know about any instrument, trait set, or dataset.

## Contents

- [Level 1–2 · marginal & shape](#level-12--marginal--shape)
  - [cohen_w](#cohen_w) · [chi_square_vs_reference](#chi_square_vs_reference) · [effect_size_tier](#effect_size_tier)
- [Level 3a · between-unit dispersion](#level-3a--between-unit-dispersion)
  - [sd_ratio](#sd_ratio) · [variance_components](#variance_components)
- [Level 3b · joint structure](#level-3b--joint-structure)
  - [correlation_distortion](#correlation_distortion)
- [Fallback · rank fidelity](#fallback--rank-fidelity)
  - [signal_correlation](#signal_correlation)
- [Reliability · a separate axis](#reliability--a-separate-axis)
  - [cronbach_alpha](#cronbach_alpha) · [krippendorff_alpha](#krippendorff_alpha)
- [The sampling floor](#the-sampling-floor)
- [Regression-to-mean](#regression-to-mean)
- [Choosing the statistic](#choosing-the-statistic)

---

## Level 1–2 · marginal & shape

### cohen_w
`cohen_w(observed_counts, reference_pct) -> float`

**Is:** the effect-size distance between an observed K-bin count vector and a
reference distribution, `w = sqrt( Σ (p_obs − p_ref)² / p_ref )` over proportions.

**Input:** `observed_counts` — counts per bin (any K). `reference_pct` — any
non-negative weights (percentages or proportions); renormalized internally.

**Read it as:** the primary shape-distance scalar. Independent of N, so it is
comparable across samples of different size — which χ² is not. Use the fidelity
tiers (see `effect_size_tier`), not p-values.

**Gotchas:** bins with `p_ref = 0` divide by zero — merge or floor empty reference
bins first. Compute on the *same* binning the reference uses (e.g. quartile mass),
not raw scores.

### chi_square_vs_reference
`chi_square_vs_reference(observed_counts, reference_pct) -> (chi2, p, w)`

**Is:** the χ² goodness-of-fit triple against a reference. Expected counts are the
reference renormalized to sum to the observed N *exactly*, which absorbs the
rounding of a reference quoted in whole percentages (so a reference summing to
99–101% still gives an exact test).

**Read it as:** `w` is the takeaway; `chi2`/`p` are reported for completeness.
**Do not read p.** With a synthetic source you can make N arbitrarily large, so χ²
always rejects and p says only "N is big." Significance ≠ fidelity here.

### effect_size_tier
`effect_size_tier(w) -> str`

**Is:** the usability verdict for a w — the first tier whose ceiling it falls under.

| w | tier |
|---|---|
| < 0.10 | excellent |
| 0.10–0.30 | small |
| 0.30–0.50 | medium-low |
| 0.50–0.80 | medium |
| > 0.80 | large — document as a gap, don't build claims on it |

**Note:** these are the *fidelity* tiers from the campaign, deliberately different
from Cohen's generic small/medium/large (0.1/0.3/0.5), which are calibrated for
statistical power, not for how usable a synthetic distribution is.

---

## Level 3a · between-unit dispersion

### sd_ratio
`sd_ratio(synth, real) -> np.ndarray  # length K`

**Is:** column-wise `SD(synth) / SD(real)` on two `(n, K)` arrays of per-unit
scores (sample SD, ddof=1).

**Input:** `synth`, `real` — each `(n_units, K_variables)` of per-unit summary
scores (e.g. each unit's total on each dimension).

**Read it as:** the homogenization diagnostic. ≈1.0 = matched spread; **< ~0.85 ⇒
synthetic units answer too alike** (collapsed toward a shared mean). A generator
can match every marginal mean and still fail here — that's the point of measuring
it. Bootstrap its SE before believing a move (SE≈0.08 at n=50 for one instrument;
needed n≥109 to resolve a 0.15 shift).

### variance_components
`variance_components(draws) -> {sigma2_between, sigma2_within, icc, sd_between}`

**Is:** the one-way random-effects variance decomposition of a `(n_units, K_draws)`
array, where each unit was measured K≥2 times (replicate draws of the same unit).

**Read it as:**
- **ICC near 1** ⇒ the pipeline is near-deterministic: σ²_within ≈ 0, so *one draw
  per unit suffices* and a multi-draw factorial only re-proves it. (One pipeline
  measured ICC 0.977 — the planned 3× multi-draw design was unnecessary.)
- **σ²_between** is the dispersion quantity a homogenized generator gets wrong.
  Within-unit levers (temperature, multi-draw averaging) move σ²_within and
  **cannot** raise σ²_between — don't reach for them to fix under-dispersion.

**Input:** needs replicate draws per unit. If you only have one draw per unit you
can't separate the components — but high ICC elsewhere justifies trusting a single
draw for the between-unit SD.

---

## Level 3b · joint structure

### correlation_distortion
`correlation_distortion(synth, real) -> {mean_abs_dr, sign_flips}`

**Is:** how badly synthetic data warps the joint structure. `mean_abs_dr` is the
mean absolute off-diagonal gap between the synthetic and real inter-column
correlation matrices; `sign_flips` counts column pairs whose correlation reverses
sign.

**Input:** `synth`, `real` — each `(n_units, K_variables)`. Correlation matrices
are computed internally with `np.corrcoef(..., rowvar=False)`.

**Read it as:** the validity bombshell. Marginal-matching is blind to joint
structure by construction, so **any claim about a relationship between two columns
rests entirely on this.** A sign flip means the synthetic source *manufactured or
reversed* a relationship absent in the real population — a synthetic source can be
marginally faithful and still produce wrong-signed regression conclusions. If
distortion is high or any pair flips, restrict valid use to univariate/marginal
claims and rank-ordering.

**Gotcha:** under-dispersion and correlation-distortion are usually the *same*
underlying defect (a low-dimensional entangled manifold). Don't treat a fix to one
as independent of the other.

---

## Fallback · rank fidelity

### signal_correlation
`signal_correlation(a, b, method="spearman") -> float`

**Is:** the cross-unit Spearman (default) or Pearson correlation between two
per-unit score vectors.

**Two uses:**
1. **Signal vs noise** — does added between-unit spread track an *independent*
   oracle rating of the same units (real signal) or not (injected noise)?
2. **Honest fallback claim** — when absolute marginal match is unreachable but the
   source still *orders* units like reality (ρ high, e.g. 0.89), report rank
   fidelity and scope conclusions to relative/ordinal claims.

**Input:** two equal-length per-unit vectors, aligned by unit.

---

## Reliability · a separate axis

Reliability asks *is the measurement internally consistent / reproducible?* — a
different axis from the validity stack (which asks *does the distribution match?*).
The synthetic source should reproduce the real population's reliability too. Compare
synth vs real, never read an LLM's α in isolation.

### cronbach_alpha
`cronbach_alpha(item_scores) -> float`

**Is:** internal-consistency reliability of a k-item scale over an
`(n_respondents, k_items)` array: `(k/(k-1)) · (1 − Σ var(item) / var(total))`.

**Input:** per-respondent item-level scores (not totals), shape `(n, k)`.

**Read it as:** a *comparison* — does the synthetic source reproduce the real
instrument's item-covariance structure? Low-dimensional collapse **inflates** α
(halo: every item answered consistently high/low — the within-scale face of
`correlation_distortion`); independent per-item LLM noise **deflates** it. So synth
α ≫ real α is itself a homogenization signal.

**Gotcha:** with LLMs α is necessary-not-sufficient — high internal consistency
routinely coexists with **low parallel-forms reliability** (the same instrument under
reworded prompts yields a different distribution). Pair α with a prompt-perturbation
check, and label it *population* internal-consistency, not single-unit test–retest.

### krippendorff_alpha
`krippendorff_alpha(reliability_data, level="ordinal") -> float`

**Is:** chance-corrected agreement over a `(raters, units)` matrix (missing as
`np.nan`), `level ∈ {nominal, ordinal, interval}`: `α = 1 − D_observed / D_expected`.
Validated against the canonical Hayes–Krippendorff dataset (nominal 0.743, ordinal
0.815, interval 0.849).

**Two uses:**
1. **Categorical/ordinal analog of ICC** for draw-to-draw reproducibility — raters =
   repeat draws of the same unit. Use this where `variance_components` (which assumes
   interval data) doesn't fit nominal/ordinal Likert.
2. **Per-unit synth-vs-real agreement** — raters = {synthetic, real} — *only* when
   you hold unit-linked ground truth (a real answer for each synthetic unit). A
   stronger claim than distribution match, but a stronger data requirement; for two
   raters Cohen's κ is the special case.

**Gotcha:** report it per-subgroup / per-topic — replicability is conditional, and
pools hide systematic per-cell failure (worst on minority / sensitive cells).
`level` must match the data's measurement level; ordinal uses the marginal-based
difference function, so it depends on the observed value distribution.

**Alternative:** for production use the maintained `krippendorff` PyPI package; the
bundled implementation is self-contained and validated for the common cases.

---

## The sampling floor

`sampling_floor.perfect_respondent_floor(reference_pct, n, ...)` ·
`mean_floor(references, n, ...)` · `power_curve(references, ns, ...)`

**Is:** the distribution of Cohen's w a *perfect* respondent produces at sample
size n, from multinomial sampling noise against the reference alone. The 95% band
is the floor; a measured score inside it is statistically indistinguishable from
perfect.

**Why it's first among equals:** without it you cannot tell signal from noise, and
will optimize inside the noise band. It costs zero model calls — bootstrap from the
reference's own multinomial.

**Use:**
- `perfect_respondent_floor` — one dimension's band at n.
- `mean_floor` — the band of the mean-across-dimensions w (pass a dict/list of
  references) when your headline is a mean over variables.
- `power_curve` — the band at each of several n; pick the smallest n whose band
  *excludes* your target effect. Below that n the noise swallows the gap.

**Example:** one instrument's mean-w floor was [0.148, 0.313] at n=50 (swallowed
all per-dimension results) and narrowed to [0.09, 0.20] at n=123 (finally separated
real gap from luck).

## Regression-to-mean

`rtm_check.conditional_shift(prev, curr)` · `looks_like_rtm(table)`

**Is:** the per-unit shift `(curr − prev)` grouped by each unit's *prior* value, for
a paired before/after comparison aligned by unit.

**Read it as:** the discriminator between a real intervention effect and units
regressing toward the generator's prior. Aggregate distance can't tell them apart —
both move the metric the same direction. **RTM signature:** shifts that reverse
monotonically at the extremes (lowest prior rises, highest falls). That means the
intervention left those units under-specified and the model fell back to the
middle. A real, content-driven effect shifts units consistently regardless of
starting value.

**If RTM:** the fix is an *active anchor* (a concrete behavior / instance /
frequency the unit must express), not another reformulation of the same passive
content.

---

## Choosing the statistic

| You want to know… | Use | At which level |
|---|---|---|
| Does the average match? | Δmean | 1 (necessary only) |
| Is the whole shape right? | `cohen_w` + `effect_size_tier` | 2a |
| Which bin/tail is wrong? | per-bin obs vs ref counts | 2b |
| Do distinct units spread like real? | `sd_ratio` | 3a |
| Is observed spread real or answering noise? | `variance_components` (ICC) | 3a |
| Are cross-variable relationships preserved? | `correlation_distortion` | 3b |
| Does the source reproduce the scale's internal consistency? | `cronbach_alpha` (synth vs real) | reliability axis |
| Do repeat draws / synth-vs-real agree (ordinal/nominal)? | `krippendorff_alpha` | reliability axis |
| If marginals fail, is ordering right? | `signal_correlation` (Spearman) | fallback |
| Is my gap above sampling noise? | `sampling_floor` | gate before iterating |
| Real effect or regression-to-mean? | `rtm_check` | gate before crediting a move |

Climb 1 → 2 → 3; a pass at a lower level never substitutes for the level above.
Reliability is a *separate axis*, not a higher level — a reliable source can be
reliably wrong.
