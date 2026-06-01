"""The perfect-respondent sampling floor.

A FLAWLESS respondent still produces a nonzero fidelity metric at finite n, purely
from multinomial sampling noise against the reference. This module IS that floor:
the distribution of Cohen's w you would see if your synthetic source were perfect
and the only error were the size of your sample.

Why it is the single highest-leverage move: a measured score that sits INSIDE this
band is statistically indistinguishable from a perfect respondent — iterating to
push it lower is tuning inside the noise. (A real campaign spent its back half
doing exactly that before the floor was computed.) Costs zero model calls.

Run it BEFORE you iterate, and use the n-power curve to pick a sample size whose
band is narrower than the effect you care about.

CLI:
  python sampling_floor.py --reference ref.json --n 50
  python sampling_floor.py --reference ref.json --power 50,100,150,200
where ref.json is either one reference vector [33,25,25,17] or a dict of them
{"O":[...], "C":[...]} (the mean-across-dimensions floor is reported for a dict).
"""
from __future__ import annotations

import numpy as np


def _w_draws(reference_pct, n, reps, rng):
    """The Cohen's w of `reps` perfect draws of n units from one reference IS a
    length-reps array (vectorized — no Python loop over reps)."""
    p = np.asarray(reference_pct, dtype=float)
    p = p / p.sum()
    props = rng.multinomial(n, p, size=reps) / n
    return np.sqrt(((props - p) ** 2 / p).sum(axis=1))


def perfect_respondent_floor(reference_pct, n, reps=50000, seed=0, band=(2.5, 97.5)):
    """The floor band for one dimension IS the percentile interval (default 95%)
    of Cohen's w over `reps` independent perfect draws of n from the reference."""
    ws = _w_draws(reference_pct, n, reps, np.random.default_rng(seed))
    lo, hi = np.percentile(ws, band)
    return {"n": int(n), "mean": float(ws.mean()), "lo": float(lo), "hi": float(hi), "reps": reps}


def mean_floor(references, n, reps=50000, seed=0, band=(2.5, 97.5)):
    """The mean-across-dimensions floor band IS the percentile interval of the
    mean Cohen's w over D dimensions, each drawn n times from its own reference.
    `references` is a list or dict of reference vectors. Use this when your
    headline metric is the mean w across several variables."""
    refs = list(references.values()) if isinstance(references, dict) else list(references)
    rng = np.random.default_rng(seed)
    per_dim = np.array([_w_draws(p, n, reps, rng) for p in refs])
    mean_w = per_dim.mean(axis=0)
    lo, hi = np.percentile(mean_w, band)
    return {"n": int(n), "mean": float(mean_w.mean()), "lo": float(lo), "hi": float(hi), "dims": len(refs), "reps": reps}


def power_curve(references, ns, reps=20000, seed=0):
    """The floor power curve IS the mean-w floor band at each n in `ns`. Read it to
    pick the smallest n whose band excludes your target effect — below that n the
    sampling noise swallows the gap you are trying to measure."""
    floor = (lambda r, n: mean_floor(r, n, reps=reps, seed=seed)) if _is_multi(references) \
        else (lambda r, n: perfect_respondent_floor(r, n, reps=reps, seed=seed))
    return {int(n): floor(references, n) for n in ns}


def _is_multi(references) -> bool:
    """References ARE multi-dimensional when they are a dict, or a sequence whose
    first element is itself a sequence."""
    return isinstance(references, dict) or (
        len(references) > 0 and np.ndim(references[0]) > 0
    )


def _main():
    import argparse
    import json
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Perfect-respondent sampling floor for Cohen's w.")
    ap.add_argument("--reference", required=True, help="JSON file: one vector or a dict of vectors.")
    ap.add_argument("--n", type=int, help="Sample size to report the floor band at.")
    ap.add_argument("--power", help="Comma-separated n values for a power curve, e.g. 50,100,150.")
    ap.add_argument("--reps", type=int, default=50000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    references = json.load(open(args.reference, encoding="utf-8"))
    multi = _is_multi(references)

    if args.power:
        ns = [int(x) for x in args.power.split(",")]
        curve = power_curve(references, ns, reps=min(args.reps, 20000), seed=args.seed)
        print(f"{'n':>6} {'mean':>8} {'lo':>8} {'hi':>8}  (95% perfect-respondent band)")
        for n, b in curve.items():
            print(f"{n:>6} {b['mean']:>8.3f} {b['lo']:>8.3f} {b['hi']:>8.3f}")
    elif args.n is not None:
        band = (mean_floor if multi else perfect_respondent_floor)(references, args.n, reps=args.reps, seed=args.seed)
        scope = f"mean of {band.get('dims')} dims" if multi else "single dimension"
        print(f"n={band['n']} ({scope}): perfect-respondent w mean={band['mean']:.3f}, 95% band [{band['lo']:.3f}, {band['hi']:.3f}]")
        print("A measured score inside this band is indistinguishable from a perfect respondent.")
    else:
        ap.error("pass either --n or --power")


if __name__ == "__main__":
    _main()
