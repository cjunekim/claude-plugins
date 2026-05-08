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
import sys

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


def parse_filter(spec: str) -> list[tuple[str, str, str]]:
    """`sex=여자,age>=30,xsubstr=요리` → list of (col, op, val) triples.
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
        if col == "xsubstr":
            if op not in ("=", "=="):
                sys.exit("xsubstr only supports '=' or '==' operators")
            missing = [field for field in DESCRIPTIVE_FIELDS if field not in df.columns]
            if missing:
                sys.exit(f"xsubstr fields missing from dataset: {missing}")
            needle = val.lower()
            text = df[DESCRIPTIVE_FIELDS].fillna("").astype(str)
            mask = text.apply(lambda s: s.str.lower().str.contains(needle, regex=False, na=False)).any(axis=1)
            df = df[mask]
            continue
        if col not in df.columns:
            sys.exit(f"unknown column: {col!r} (available: {list(df.columns)})")
        series = df[col]
        if op in ("=", "=="):
            if col == "province":
                requested = PROVINCE_ALIASES.get(val, val)
                values = series.astype(str)
                df = df[
                    (values == requested)
                    | values.str.contains(val, regex=False, na=False)
                    | values.apply(lambda actual: actual in val)
                ]
            else:
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
