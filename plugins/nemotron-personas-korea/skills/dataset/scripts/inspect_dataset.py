"""Inspect the nvidia/Nemotron-Personas-Korea dataset and dump findings.

Bundled with the nemotron-personas-korea skill. Re-run on first contact in
a new project (or whenever the dataset SHA may have changed) to verify the
snapshot in references/inspection-snapshot.md against the live dataset.

Usage:
    python inspect_dataset.py [output.md]

Default output: ./nemotron-personas-korea-inspection.md in the cwd.

Set HF_HOME first if you want the dataset cache (~5.76 GB on disk) somewhere
specific. Otherwise it lands at HuggingFace's default — on Windows that is
%USERPROFILE%\\.cache\\huggingface.
"""
from __future__ import annotations

import sys
from contextlib import redirect_stdout
from pathlib import Path

import pandas as pd
from datasets import load_dataset
from huggingface_hub import HfApi

REPO = "nvidia/Nemotron-Personas-Korea"
DEFAULT_OUT = Path.cwd() / "nemotron-personas-korea-inspection.md"

# Columns the snapshot's findings rest on. If any of these go missing, the
# schema has drifted and the snapshot is stale.
CORE_COLUMNS = [
    "persona", "sex", "age", "province", "district",
    "education_level", "marital_status", "family_type",
    "housing_type", "occupation",
]


def age_band(age) -> str:
    try:
        a = int(age)
    except (TypeError, ValueError):
        return str(age)
    if a < 19:    return "<19"
    if a <= 29:   return "19-29"
    if a <= 44:   return "30-44"
    if a <= 59:   return "45-59"
    return "60+"


def banner(title: str) -> None:
    print(f"\n## {title}\n")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT

    with out_path.open("w", encoding="utf-8") as f, redirect_stdout(f):
        banner("dataset SHA")
        sha = HfApi().dataset_info(REPO).sha
        print(f"sha = `{sha}`")

        banner("loading dataset")
        ds = load_dataset(REPO, revision=sha, split="train")
        df = ds.to_pandas()
        print(f"rows = {len(df):,}")

        banner("schema")
        print("```")
        print(df.dtypes)
        print("```")
        print(f"\ncolumns ({len(df.columns)}):")
        print("```")
        print(df.columns.tolist())
        print("```")

        banner("core columns present?")
        missing = [c for c in CORE_COLUMNS if c not in df.columns]
        extra = [c for c in df.columns if c not in CORE_COLUMNS]
        print(f"- missing core columns: `{missing or 'none'}`")
        print(f"- additional columns in dataset (narrative or metadata): `{extra}`")

        banner("`age` column structure")
        print(f"- dtype: `{df['age'].dtype}`")
        print("- head(10):")
        print("```")
        print(df["age"].head(10).to_string())
        print("```")
        if pd.api.types.is_numeric_dtype(df["age"]):
            print("- numeric — `describe()`:")
            print("```")
            print(df["age"].describe())
            print("```")
        else:
            print("- non-numeric — `value_counts()` (top 30):")
            print("```")
            print(df["age"].value_counts().head(30).to_string())
            print("```")

        banner("text-field length comparison")
        print("Identifies the compact `persona` summary vs the long narrative fields.\n")
        text_cols = [c for c in df.columns if df[c].dtype == object]
        print("```")
        for col in text_cols:
            lens = df[col].astype(str).str.len()
            print(f"{col:30s}  mean={lens.mean():8.1f}  median={lens.median():7.1f}  max={lens.max():7d}")
        print("```")

        banner("3 random rows — full dump")
        sample = df.sample(3, random_state=0)
        for i, row in sample.iterrows():
            print(f"\n### row index {i}\n")
            print("```")
            for c in df.columns:
                v = str(row[c])
                cap = 1200 if (c == "persona" or "narrative" in c.lower()) else 200
                print(f"{c:30s}: {v[:cap]}{'...[truncated]' if len(v) > cap else ''}")
            print("```")

        banner("`province` distribution")
        if "province" in df.columns:
            vc = df["province"].value_counts()
            print(f"- distinct: **{len(vc)}**")
            print("```")
            print(vc.to_string())
            print("```")

        banner("sex × age-band marginals + proportional N=300 allocation")
        df["age_band"] = df["age"].apply(age_band)
        cells = (df.groupby(["sex", "age_band"]).size()
                 .rename("n_pop").reset_index())
        cells["pop_share"] = cells["n_pop"] / len(df)
        cells["target_300"] = (cells["pop_share"] * 300).round().astype(int)
        cells["under_floor_25"] = cells["target_300"] < 25
        print("```")
        print(cells.to_string(index=False))
        print("```")
        print(f"\n- total target N before floor-adjust: **{cells['target_300'].sum()}**")
        print(f"- cells under floor of 25: **{cells['under_floor_25'].sum()}**")
        print(f"- smallest target cell: **{cells['target_300'].min()}**, largest: **{cells['target_300'].max()}**")

        banner("done")

    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
