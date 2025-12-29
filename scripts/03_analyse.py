"""
03_analyse.py (pipeline-consistent)

Reproduce the logic of collapse_journal_year_keyword_pretty:
- Uses clean labels already applied in 02_clean outputs as 'keyword'
- Creates a unique article_id = work_id if available, else DOI, else title
- Counts unique articles per (journal_input, year, keyword)
- Merges totals per (journal_input, year) from the raw works pickle
- Computes share and percentage

Inputs:
- outputs/works_keyword_hits_<sheet>.csv   (from 02_clean.py)
- outputs/openalex_raw_works_<sheet>.pkl   (from 01_extract.py)

Output:
- outputs/df_all_jyk_<sheet>.csv
"""

import sys
from pathlib import Path
from typing import Any
import argparse
import numpy as np
import pandas as pd

# Make the /src directory importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openalex_pipeline.utils import total_articles_journal_per_year


VALID_SHEETS = ["Sociology", "Political_Science"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyse keyword prevalence by journal and year.")
    parser.add_argument("--sheet", default="Sociology", choices=VALID_SHEETS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sheet_name = args.sheet

    hits_path = ROOT / "outputs" / f"works_keyword_hits_{sheet_name}.csv"
    raw_path = ROOT / "outputs" / f"openalex_raw_works_{sheet_name}.pkl"

    if not hits_path.exists():
        raise FileNotFoundError(f"Missing input: {hits_path} (run 02_clean.py first)")
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing input: {raw_path} (run 01_extract.py first)")

    # -----------------------------
    # 1) Load hits (article-level)
    # -----------------------------
    hits = pd.read_csv(hits_path)

    required_hits = {"journal_input", "year", "keyword", "title"}
    missing = required_hits - set(hits.columns)
    if missing:
        raise ValueError(f"works_keyword_hits file missing columns: {sorted(missing)}")

    hits["year"] = pd.to_numeric(hits["year"], errors="coerce").astype("Int64")
    hits = hits.dropna(subset=["year", "title"])

    # Robust unique article id: work_id > doi > title
    if "work_id" in hits.columns:
        hits["article_id"] = (
            hits["work_id"]
            .astype("string")
            .fillna(hits.get("doi").astype("string") if "doi" in hits.columns else pd.NA)
            .fillna(hits["title"].astype("string"))
        )
    elif "doi" in hits.columns:
        hits["article_id"] = hits["doi"].astype("string").fillna(hits["title"].astype("string"))
    else:
        hits["article_id"] = hits["title"].astype("string")

    # -----------------------------
    # 2) Count unique articles per journal-year-keyword
    # -----------------------------
    df_counts = (
        hits.groupby(["journal_input", "year", "keyword"])["article_id"]
        .nunique()
        .reset_index(name="n_articles_with_keyword")
    )

    # -----------------------------
    # 3) Compute total articles per journal-year (from raw works)
    # -----------------------------
    records: list[dict[str, Any]] = pd.read_pickle(raw_path)

    totals_frames = []
    for rec in records:
        journal_input = rec["journal_input"]
        works = rec["works_raw"]
        totals_frames.append(total_articles_journal_per_year(works, journal_input))

    df_totals_all = pd.concat(totals_frames, ignore_index=True)
    df_totals_all["year"] = pd.to_numeric(df_totals_all["year"], errors="coerce").astype("Int64")
    df_totals_all["n_articles_total"] = (
        pd.to_numeric(df_totals_all["n_articles_total"], errors="coerce").fillna(0).astype(int)
    )

    # -----------------------------
    # 4) Merge + share/percentage
    # -----------------------------
    df_out = df_counts.merge(df_totals_all, on=["journal_input", "year"], how="left")
    df_out["n_articles_total"] = df_out["n_articles_total"].fillna(0).astype(int)

    df_out["share"] = np.divide(
        df_out["n_articles_with_keyword"].astype(float),
        df_out["n_articles_total"].astype(float),
        out=np.zeros(len(df_out), dtype=float),
        where=df_out["n_articles_total"].to_numpy() != 0,
    )
    df_out["percentage"] = df_out["share"] * 100.0

    cols = [
        "journal_input",
        "year",
        "keyword",
        "n_articles_total",
        "n_articles_with_keyword",
        "share",
        "percentage",
    ]
    df_out = df_out[cols].sort_values(["keyword", "journal_input", "year"]).reset_index(drop=True)

    out_path = ROOT / "outputs" / f"df_all_jyk_{sheet_name}.csv"
    df_out.to_csv(out_path, index=False)

    print(f"Saved df_all_jyk table: {out_path}")


if __name__ == "__main__":
    main()
