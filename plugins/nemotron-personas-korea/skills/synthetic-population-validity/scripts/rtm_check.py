"""Regression-to-mean diagnostic for a paired before/after comparison.

When an intervention moves an aggregate metric, the move is either a real effect
or the units regressing toward the generator's prior. Aggregate distance cannot
tell these apart — both shift the metric the same direction. This module IS the
discriminator: the conditional shift of each unit grouped by its PRIOR value.

The RTM signature IS conditional shifts that reverse monotonically at the extremes
— units that were low rise, units that were high fall — which means the
intervention left those units under-specified and the model fell back to the
middle. A real, content-driven effect shifts units in a consistent direction
regardless of where they started.

If you see RTM, the fix is an ACTIVE anchor (a concrete behavior / instance /
frequency the unit must express), not another reformulation of the same passive
content.

CLI:
  python rtm_check.py --csv paired.csv --prev prev_col --curr curr_col
where paired.csv has one row per unit, aligned across the two runs.
"""
from __future__ import annotations

import numpy as np


def conditional_shift(prev, curr):
    """The conditional-shift table IS, for each distinct prior value, the count of
    units that held it and their mean (curr - prev) shift. `prev` and `curr` are
    equal-length per-unit score vectors aligned by unit (row i is the same unit in
    both runs)."""
    prev = np.asarray(prev, dtype=float)
    curr = np.asarray(curr, dtype=float)
    shift = curr - prev
    return {
        float(v): {"n": int((prev == v).sum()), "mean_shift": float(shift[prev == v].mean())}
        for v in np.unique(prev)
    }


def looks_like_rtm(table) -> bool:
    """A conditional-shift table LOOKS LIKE RTM when its lowest prior level shifts
    up and its highest prior level shifts down — the reversing signature. This is a
    coarse boolean heuristic, not a test: always read the full table, because a
    partial reversal still implicates RTM in part of the range."""
    levels = sorted(table)
    return table[levels[0]]["mean_shift"] > 0 and table[levels[-1]]["mean_shift"] < 0


def _main():
    import argparse
    import sys

    import pandas as pd

    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Regression-to-mean conditional-shift diagnostic.")
    ap.add_argument("--csv", required=True, help="One row per unit, aligned across runs.")
    ap.add_argument("--prev", required=True, help="Column holding the prior-run score.")
    ap.add_argument("--curr", required=True, help="Column holding the current-run score.")
    args = ap.parse_args()

    frame = pd.read_csv(args.csv)
    table = conditional_shift(frame[args.prev], frame[args.curr])
    print(f"{'prior':>6} {'n':>5} {'mean_shift':>12}")
    for level in sorted(table):
        row = table[level]
        print(f"{level:>6.2f} {row['n']:>5} {row['mean_shift']:>+12.3f}")
    verdict = (
        "RTM signature present (low rises, high falls) — the move is regression, not a real effect."
        if looks_like_rtm(table)
        else "no clean RTM signature — inspect the table; a consistent-direction shift suggests a real effect."
    )
    print(verdict)


if __name__ == "__main__":
    _main()
