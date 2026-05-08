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

    # by substring across descriptive text fields plus occupation/degree field:
    python load_persona.py --filter "sex=여자,xsubstr=요리" --seed 42

Output: every persona-relevant field in a `=== <fieldname> ===` block
format, suitable for piping into a prompt builder or reading verbatim.
"""
from __future__ import annotations

import argparse
import operator
import sys
from functools import reduce

import pandas as pd

REPO = "nvidia/Nemotron-Personas-Korea"

PROVINCE_ALIASES = {
    "서울특별시": "서울",
    "부산광역시": "부산",
    "인천광역시": "인천",
    "대구광역시": "대구",
    "대전광역시": "대전",
    "광주광역시": "광주",
    "울산광역시": "울산",
    "경기도": "경기",
    "강원도": "강원",
    "강원특별자치도": "강원",
    "충청북도": "충청북",
    "충청남도": "충청남",
    "전라북도": "전북",
    "전북특별자치도": "전북",
    "전라남도": "전라남",
    "경상북도": "경상북",
    "경상남도": "경상남",
    "제주특별자치도": "제주",
    "제주도": "제주",
    "세종특별자치시": "세종",
}
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

DESCRIPTIVE_FIELDS = [
    "persona", "professional_persona", "sports_persona", "arts_persona",
    "travel_persona", "culinary_persona", "family_persona",
    "cultural_background", "skills_and_expertise",
    "hobbies_and_interests", "career_goals_and_ambitions",
    "occupation", "bachelors_field", "family_type",
]

NUMERIC_OPS = {
    ">=": operator.ge,
    "<=": operator.le,
    ">":  operator.gt,
    "<":  operator.lt,
}


def parse_filter(spec):
    """List of (col, op, val) triples parsed from `sex=여자,age>=30,xsubstr=요리`.
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


def province_mask(cells, val):
    """Boolean mask of rows whose province cell equals or substring-matches `val` under official-name alias normalization (so 서울 and 서울특별시 both hit)."""
    requested = PROVINCE_ALIASES.get(val, val)
    text = cells.astype(str)
    return (
        (text == requested)
        | text.str.contains(val, regex=False, na=False)
        | text.apply(lambda actual: actual in val)
    )


def xsubstr_mask(df, val):
    """Boolean mask of rows where `val` (case-insensitive) appears as a substring in any DESCRIPTIVE_FIELDS cell."""
    needle = val.lower()
    fields = df[DESCRIPTIVE_FIELDS].fillna("").astype(str)
    return fields.apply(lambda col: col.str.lower().str.contains(needle, regex=False, na=False)).any(axis=1)


def clause_mask(df, col, op, val):
    """Boolean mask of rows in `df` satisfying the single clause (col op val)."""
    if col == "xsubstr":
        return xsubstr_mask(df, val)
    if col == "province" and op in ("=", "=="):
        return province_mask(df[col], val)
    if op in ("=", "=="):
        return df[col].astype(str) == val
    return NUMERIC_OPS[op](df[col], type(df[col].iloc[0])(val))


def validate_items(df, items):
    """First structural problem with `items` against `df`, or None if every clause is well-formed."""
    for col, op, _ in items:
        if col == "xsubstr":
            if op not in ("=", "=="):
                return "xsubstr only supports '=' or '==' operators"
            missing = [f for f in DESCRIPTIVE_FIELDS if f not in df.columns]
            if missing:
                return f"xsubstr fields missing from dataset: {missing}"
        elif col not in df.columns:
            return f"unknown column: {col!r} (available: {list(df.columns)})"
    return None


def apply_filter(df, items):
    """`df` restricted to rows where every clause's mask holds."""
    masks = (clause_mask(df, *item) for item in items)
    keep = reduce(operator.and_, masks, pd.Series(True, index=df.index))
    return df.loc[keep]


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--uuid", help="exact uuid match")
    ap.add_argument("--filter", help='comma-separated clauses, e.g. "sex=여자,age>=30,province=서울,xsubstr=요리"')
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
        issue = validate_items(df, items)
        if issue:
            sys.exit(issue)
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
