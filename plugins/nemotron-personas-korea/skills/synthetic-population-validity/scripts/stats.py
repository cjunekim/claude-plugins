"""Domain-agnostic statistics for comparing a synthetic response distribution to
a real reference population.

Every function IS a pure map from data (and a reference) to a fidelity number.
No instrument, trait set, or dataset is baked in — callers pass their own bins,
columns, and reference distribution. I/O, labeling, and table-rendering live in
the caller, not here.

The three levels of the validity stack map onto these functions:
  1. marginal/shape ......... cohen_w, chi_square_vs_reference, effect_size_tier
  2. between-unit dispersion . sd_ratio, variance_components
  3. joint structure ........ correlation_distortion
  fallback (rank fidelity) .. signal_correlation
  reliability (separate axis) cronbach_alpha, krippendorff_alpha

Reliability is NOT a fourth level of the validity stack — it is a different axis
(is the measurement internally consistent / reproducible?) that the synthetic
source should also reproduce. See SKILL.md "Reliability is a different axis."
"""
from __future__ import annotations

import numpy as np
from scipy import stats


def cohen_w(observed_counts, reference_pct) -> float:
    """Cohen's w IS the effect-size distance between an observed K-bin count
    vector and a reference distribution: sqrt(sum((p_obs - p_ref)^2 / p_ref)).

    `reference_pct` is any non-negative weights (percentages or proportions) and
    is renormalized to a probability vector. w is independent of N, so it is the
    shape distance you can compare across samples of different size — unlike
    chi-square, which grows with N and therefore always 'rejects' once N is large
    (and a synthetic N is arbitrary)."""
    observed = np.asarray(observed_counts, dtype=float)
    p_obs = observed / observed.sum()
    p_ref = np.asarray(reference_pct, dtype=float)
    p_ref = p_ref / p_ref.sum()
    return float(np.sqrt(np.sum((p_obs - p_ref) ** 2 / p_ref)))


def chi_square_vs_reference(observed_counts, reference_pct):
    """The chi-square test of an observed K-bin count vector against a reference
    distribution IS the triple (chi2, p, w). Expected counts are the reference
    renormalized to sum to the observed N exactly, which absorbs the rounding of a
    reference quoted in whole percentages so the test stays exact.

    p is reported for completeness, but read w (effect size), not p: with a
    synthetic population you can make N arbitrarily large, so p is not meaningful.
    """
    observed = np.asarray(observed_counts, dtype=float)
    n = observed.sum()
    p_ref = np.asarray(reference_pct, dtype=float)
    expected = p_ref / p_ref.sum() * n
    chi2 = float(np.sum((observed - expected) ** 2 / expected))
    dof = observed.size - 1
    p = float(stats.chi2.sf(chi2, dof))
    w = float(np.sqrt(chi2 / n))
    return chi2, p, w


W_TIERS = (
    (0.10, "excellent (<0.10)"),
    (0.30, "small (0.10-0.30)"),
    (0.50, "medium-low (0.30-0.50)"),
    (0.80, "medium (0.50-0.80)"),
    (float("inf"), "large (>0.80) — document as a gap, do not use for claims"),
)


def effect_size_tier(w: float) -> str:
    """The usability verdict for a Cohen's w IS the first tier whose ceiling it
    falls under. These tiers are the campaign's fidelity ladder, NOT Cohen's
    generic small/medium/large cutoffs (those are calibrated for statistical
    power, not for how usable a synthetic distribution is)."""
    return next(label for ceiling, label in W_TIERS if w < ceiling)


def sd_ratio(synth, real):
    """The between-unit dispersion ratio IS column-wise SD(synth)/SD(real) on two
    (n, K) arrays of per-unit scores. A ratio below ~0.85 signals homogenization:
    distinct synthetic units answer too alike, collapsing toward a shared mean.
    Sample SD (ddof=1). Returns a length-K array aligned with the columns."""
    s = np.std(np.asarray(synth, dtype=float), axis=0, ddof=1)
    r = np.std(np.asarray(real, dtype=float), axis=0, ddof=1)
    return s / r


def variance_components(draws):
    """The one-way random-effects variance decomposition of a (n_units, K_draws)
    array IS {sigma2_between, sigma2_within, icc, sd_between}, where each unit was
    measured K>=2 times (replicate draws).

    ICC near 1 means the pipeline is near-deterministic — one draw per unit
    suffices and a multi-draw factorial only re-proves sigma2_within ~ 0. It also
    locates the dispersion defect: only sigma2_between (spread of unit means) is
    the thing a homogenized generator gets wrong; within-unit levers (temperature,
    multi-draw averaging) move sigma2_within and cannot touch it."""
    a = np.asarray(draws, dtype=float)
    n, k = a.shape
    unit_means = a.mean(axis=1)
    grand = a.mean()
    ms_between = k * np.sum((unit_means - grand) ** 2) / (n - 1)
    ms_within = np.sum((a - unit_means[:, None]) ** 2) / (n * (k - 1))
    sigma2_between = max((ms_between - ms_within) / k, 0.0)
    total = sigma2_between + ms_within
    icc = sigma2_between / total if total > 0 else 0.0
    return {
        "sigma2_between": float(sigma2_between),
        "sigma2_within": float(ms_within),
        "icc": float(icc),
        "sd_between": float(np.sqrt(sigma2_between)),
    }


def signal_correlation(a, b, method: str = "spearman") -> float:
    """The cross-unit correlation between two per-unit score vectors IS their
    Spearman (default) or Pearson r. Two uses: (1) ask whether added spread is
    real signal — does it track an independent oracle rating of the same units —
    rather than injected noise; (2) the honest fallback validity claim (rank
    fidelity) when absolute marginal match is unreachable but ordering is right."""
    x, y = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    r = (
        stats.spearmanr(x, y).statistic
        if method == "spearman"
        else stats.pearsonr(x, y).statistic
    )
    return float(r)


def correlation_distortion(synth, real):
    """Correlation distortion IS how badly synthetic data warps the joint
    structure: {mean_abs_dr, sign_flips} from two (n, K) arrays of per-unit
    scores. mean_abs_dr is the mean absolute off-diagonal gap between the synthetic
    and real inter-column correlation matrices; sign_flips counts column pairs
    whose correlation reverses sign.

    Marginal-matching is blind to this by construction, so ANY claim about a
    relationship between two columns (X predicts Y, A correlates with B) rests on
    this number — a sign flip means the synthetic source manufactured or reversed a
    relationship that is not in the real population."""
    rs = np.corrcoef(np.asarray(synth, dtype=float), rowvar=False)
    rr = np.corrcoef(np.asarray(real, dtype=float), rowvar=False)
    off = ~np.eye(rs.shape[0], dtype=bool)
    mean_abs_dr = float(np.abs(rs - rr)[off].mean())
    sign_flips = int((np.sign(rs[off]) != np.sign(rr[off])).sum() // 2)
    return {"mean_abs_dr": mean_abs_dr, "sign_flips": sign_flips}


# --- reliability (a separate axis from the validity stack) --------------------
# Reliability asks "is the measurement internally consistent / reproducible?",
# not "does the distribution match the reference?". The generic use here is to
# compare the synthetic source's reliability to the real population's: a source
# that collapses units onto a low-dimensional manifold INFLATES internal
# consistency (units answer alike), so synth alpha > real alpha is itself a
# homogenization signal — the within-scale view of correlation_distortion.


def cronbach_alpha(item_scores) -> float:
    """Cronbach's alpha IS the internal-consistency reliability of a k-item scale
    over an (n_respondents, k_items) array: (k/(k-1)) * (1 - Σ var(item) / var(total)).

    Read it as a *comparison*, synth vs real: matching the real instrument's alpha
    means the synthetic respondents reproduce its item-covariance structure. A
    synthetic source under low-dimensional collapse inflates alpha (halo: every item
    answered consistently high/low); independent per-item LLM noise deflates it. With
    LLMs alpha is necessary-not-sufficient — high internal consistency can coexist
    with low parallel-forms reliability (prompt-sensitivity), so pair it with a
    prompt-perturbation check (Ye et al. 2025)."""
    a = np.asarray(item_scores, dtype=float)
    k = a.shape[1]
    item_var = a.var(axis=0, ddof=1).sum()
    total_var = a.sum(axis=1).var(ddof=1)
    return float((k / (k - 1)) * (1 - item_var / total_var)) if total_var > 0 else float("nan")


def krippendorff_alpha(reliability_data, level: str = "ordinal") -> float:
    """Krippendorff's alpha IS chance-corrected agreement over a (raters, units)
    matrix (missing entries as np.nan), for level in {nominal, ordinal, interval}:
    alpha = 1 - D_observed / D_expected.

    Two uses in synthetic-vs-real work: (1) the categorical/ordinal analog of ICC
    (`variance_components`) for draw-to-draw reproducibility of a synthetic
    respondent — raters = repeat draws of the same unit; (2) chance-corrected
    per-unit agreement between synthetic and real answers when you hold unit-linked
    ground truth — raters = {synthetic, real}. The second use needs the stronger
    data (a real answer per synthetic unit), not just a reference distribution."""
    data = np.asarray(reliability_data, dtype=float)
    units = [col[~np.isnan(col)] for col in data.T]
    units = [u for u in units if u.size >= 2]
    values = np.unique(np.concatenate(units))
    idx = {v: i for i, v in enumerate(values)}
    size = values.size

    coincidence = np.zeros((size, size))
    for unit in units:
        weight = 1.0 / (unit.size - 1)
        rows = [idx[v] for v in unit]
        # pair every ordered pair of distinct POSITIONS (same-value pairs land on
        # the diagonal — they are part of the marginals, so don't skip them)
        for p in range(len(rows)):
            for q in range(len(rows)):
                if p != q:
                    coincidence[rows[p], rows[q]] += weight
    marginal = coincidence.sum(axis=1)
    total = marginal.sum()

    if level == "nominal":
        delta = 1.0 - np.eye(size)
    elif level == "interval":
        delta = (values[:, None] - values[None, :]) ** 2
    elif level == "ordinal":
        cum = np.array([
            [marginal[min(c, k):max(c, k) + 1].sum() - (marginal[c] + marginal[k]) / 2.0
             for k in range(size)]
            for c in range(size)
        ])
        delta = cum ** 2
    else:
        raise ValueError(f"level must be nominal/ordinal/interval, got {level!r}")

    d_observed = (coincidence * delta).sum() / total
    d_expected = (np.outer(marginal, marginal) * delta).sum() / (total * (total - 1))
    return float(1 - d_observed / d_expected) if d_expected > 0 else float("nan")
