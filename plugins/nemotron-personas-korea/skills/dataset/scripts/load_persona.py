"""Load a single Korean persona from the Nemotron-Personas-Korea dataset.

Bundled with the nemotron-personas-korea skill. Standalone — no dependency
on any project-specific Python package, just `datasets` + pandas.

Reads from the HuggingFace cache governed by $HF_HOME. If the dataset is
not yet cached at that location it will download (~5.76 GB) — set HF_HOME
first if you want it somewhere specific.

Usage
-----
    # by uuid (exact match):
    python load_persona.py --uuid 112c58020319428cb94a7b8c69cd3ff2

    # by demographic filter (random pick within filter, deterministic with --seed):
    python load_persona.py --filter "sex=여자,age>=30,age<=45,province=서울" --seed 42

Output: every persona-relevant field in a `=== <fieldname> ===` block
format, suitable for piping into a prompt builder or reading verbatim.
"""
from __future__ import annotations

import argparse
import sys

REPO = "nvidia/Nemotron-Personas-Korea"

FIELDS = [
    "uuid", "sex", "age", "province", "district",
    "education_level", "marital_status", "family_type",
    "housing_type", "occupation",
    "persona",
    "professional_persona", "sports_persona", "arts_persona",
    "travel_persona", "culinary_persona", "family_persona",
    "cultural_background", "skills_and_expertise",
    "hobbies_and_interests", "career_goals_and_ambitions",
]


def parse_filter(spec: str) -> list[tuple[str, str, str]]:
    """`sex=여자,age>=30,province=서울` → list of (col, op, val) triples.
    Recognized ops: `=` `==` `>=` `<=` `>` `<`."""
    items = []
    for clause in spec.split(","):
        clause = clause.strip()
        if not clause:
            continue
        for op in (">=", "<=", "==", ">", "<", "="):
            if op in clause:
                col, val = clause.split(op, 1)
                items.append((col.strip(), op, val.strip()))
                break
    return items


def apply_filter(df, items):
    """`df` filtered down to rows satisfying every (col, op, val) clause."""
    import pandas as pd
    for col, op, val in items:
        if col not in df.columns:
            sys.exit(f"unknown column: {col!r} (available: {list(df.columns)})")
        series = df[col]
        if op in ("=", "=="):
            df = df[series.astype(str) == val]
        elif op == ">=":
            df = df[series >= type(series.iloc[0])(val)]
        elif op == "<=":
            df = df[series <= type(series.iloc[0])(val)]
        elif op == ">":
            df = df[series > type(series.iloc[0])(val)]
        elif op == "<":
            df = df[series < type(series.iloc[0])(val)]
    return df


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--uuid", help="exact uuid match")
    ap.add_argument("--filter", help='comma-separated clauses, e.g. "sex=여자,age>=30,province=서울"')
    ap.add_argument("--seed", type=int, default=0, help="seed for random pick within filter (default 0)")
    args = ap.parse_args()

    if not args.uuid and not args.filter:
        ap.error("provide --uuid or --filter")

    from datasets import load_dataset
    ds = load_dataset(REPO, split="train")
    df = ds.to_pandas()

    if args.uuid:
        hits = df[df["uuid"] == args.uuid]
        if hits.empty:
            sys.exit(f"no persona found with uuid={args.uuid}")
        row = hits.iloc[0]
    else:
        items = parse_filter(args.filter)
        hits = apply_filter(df, items)
        if hits.empty:
            sys.exit(f"no persona matches filter: {args.filter}")
        row = hits.sample(n=1, random_state=args.seed).iloc[0]

    for f in FIELDS:
        print(f"=== {f} ===")
        print(row[f])
        print()


if __name__ == "__main__":
    main()
