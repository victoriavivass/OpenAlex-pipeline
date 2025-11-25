from __future__ import annotations
from pathlib import Path
from typing import Sequence
import pandas as pd

from .journals import build_journal_table
from .search import search_all_journals


def run_pipeline(
    input_excel: str | Path,
    sheet_name: str,
    output_excel: str | Path,
    keywords: Sequence[str],
    from_year: int = 2010,
):
    """
    End-to-end pipeline to:
    1. Load journal list
    2. Fetch OpenAlex IDs
    3. Retrieve works matching keywords
    4. Save Excel results
    """
    input_excel = Path(input_excel)
    output_excel = Path(output_excel)

    print(f" Reading journal list: {input_excel}")
    df_input = pd.read_excel(input_excel, sheet_name=sheet_name)

    df_journals = build_journal_table(df_input)
    print(f" Journals found in OpenAlex: {df_journals['found'].sum()}")

    df_results = search_all_journals(df_journals, keywords, from_year=from_year)

    output_excel.parent.mkdir(parents=True, exist_ok=True)
    df_results.to_excel(output_excel, index=False)

    print(f" Results saved to: {output_excel}")
