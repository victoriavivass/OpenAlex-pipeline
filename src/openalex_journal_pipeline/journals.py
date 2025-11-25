from __future__ import annotations
from typing import Optional, Tuple
import pandas as pd
from pyalex import Sources


def get_journal_id_by_issn_or_name(
    journal_name: str,
    issn_value: Optional[str],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Searches OpenAlex for a journal using its ISSN(s) or its name.
    Returns (openalex_id, display_name, matched_issn).
    """
    # Try ISSNs first
    if pd.notna(issn_value) and str(issn_value).strip():
        issns = [i.strip() for i in str(issn_value).split(",")]
        for issn in issns:
            if not issn:
                continue
            result = Sources().filter(issn=issn).get()
            if result:
                src = result[0]
                return src["id"], src["display_name"], issn

    # Fallback: search by name
    if journal_name:
        result = Sources().search(journal_name).get()
        if result:
            src = result[0]
            issns = src.get("issn_l") or src.get("issn") or []
            matched_issn = issns[0] if isinstance(issns, list) and issns else None
            return src["id"], src["display_name"], matched_issn

    return None, None, None


def build_journal_table(input_df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds df_journals from an input table with 'journal_name' and 'issn'.
    """
    rows = []

    for _, row in input_df.iterrows():
        name = row["journal_name"]
        issn = row["issn"]
        jid, display_name, matched_issn = get_journal_id_by_issn_or_name(name, issn)

        rows.append({
            "input_name": name,
            "input_issn": issn,
            "openalex_id": jid,
            "openalex_name": display_name,
            "matched_issn": matched_issn,
            "found": jid is not None,
        })

    return pd.DataFrame(rows)
