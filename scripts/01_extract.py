"""
01_extract.py

Extract raw publication data from the OpenAlex API for a list of journals.
This script retrieves all works published since 2010 and stores the raw
results for downstream processing.

Usage examples:
  python scripts/01_extract.py --sheet Sociology
  python scripts/01_extract.py --sheet Political_Science
"""

import sys
from pathlib import Path
import argparse

import pandas as pd

# Make the /src directory importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openalex_pipeline.utils import (
    get_journal_id_by_issn_or_name,
    get_all_works_since_2010,
)


VALID_SHEETS = ["Sociology", "Political_Science"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract OpenAlex works for a journal list.")
    parser.add_argument(
        "--sheet",
        default="Sociology",
        choices=VALID_SHEETS,
        help=f"Excel sheet name to process. Options: {', '.join(VALID_SHEETS)}",
    )
    parser.add_argument(
        "--input",
        default="data/top50_Soc_Pol.xlsx",
        help="Path to input Excel (relative to repo root).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # ------------------------------------------------------------------
    # 1. Load input journals list
    # ------------------------------------------------------------------
    input_path = ROOT / args.input
    sheet_name = args.sheet

    if not input_path.exists():
        raise FileNotFoundError(f"Input Excel not found: {input_path}")

    df = pd.read_excel(input_path, sheet_name=sheet_name)

    # Column names in the input file
    journal_col = "Journal Name"
    issn_col = "ISSN"

    if journal_col not in df.columns or issn_col not in df.columns:
        raise ValueError(
            f"Expected columns '{journal_col}' and '{issn_col}' in the Excel sheet.\n"
            f"Found columns: {list(df.columns)}"
        )

    records: list[dict] = []

    # ------------------------------------------------------------------
    # 2. Query OpenAlex and retrieve works
    # ------------------------------------------------------------------
    for _, row in df.iterrows():
        journal_name = row[journal_col]
        issn_field = row.get(issn_col)

        openalex_id, display_name, matched_issn = get_journal_id_by_issn_or_name(
            journal_name=journal_name,
            issn_field=issn_field,
        )

        if openalex_id is None:
            print(f"[WARNING] Journal not found in OpenAlex: {journal_name}")
            continue

        works = get_all_works_since_2010(openalex_id)

        records.append(
            {
                "sheet": sheet_name,
                "journal_input": journal_name,
                "journal_openalex": display_name,
                "matched_issn": matched_issn,
                "openalex_id": openalex_id,
                "n_works_since_2010": len(works),
                "works_raw": works,  # list of OpenAlex work dictionaries
            }
        )

        print(f"[OK] {journal_name}: {len(works)} works retrieved")

    # ------------------------------------------------------------------
    # 3. Save raw output
    # ------------------------------------------------------------------
    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    # filename-safe (Political_Science already safe, but keep for consistency)
    safe_sheet = sheet_name.replace(" ", "")
    output_path = output_dir / f"openalex_raw_works_{safe_sheet}.pkl"
    pd.to_pickle(records, output_path)

    print(f"\nRaw extraction saved to: {output_path}")


if __name__ == "__main__":
    main()
