"""
01_extract.py

Extract raw publication data from the OpenAlex API for a list of journals.
This script retrieves all works published since 2010 and stores the raw
results for downstream processing.
"""

import sys
from pathlib import Path

import pandas as pd

# Make the /src directory importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openalex_pipeline.utils import (
    get_journal_id_by_issn_or_name,
    get_all_works_since_2010,
)


def main() -> None:
    # ------------------------------------------------------------------
    # 1. Load input journals list
    # ------------------------------------------------------------------
    input_path = ROOT / "data" / "top50_Soc_Pol.xlsx"
    sheet_name = "Sociology"  # change to "Political_Science" if needed

    df = pd.read_excel(input_path, sheet_name=sheet_name)

    # Column names in the input file
    journal_col = "Journal Name"
    issn_col = "ISSN"

    records = []

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

    output_path = output_dir / f"openalex_raw_works_{sheet_name}.pkl"
    pd.to_pickle(records, output_path)

    print(f"\nRaw extraction saved to: {output_path}")


if __name__ == "__main__":
    main()


