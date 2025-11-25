from __future__ import annotations
from typing import Iterable, List, Dict, Any
import time
import pandas as pd
from pyalex import Works

from .abstracts import decompress_abstract, keyword_in_abstract_strict


def get_works_for_journal_and_query(
    journal_openalex_id: str,
    keyword: str,
    from_year: int = 2010,
    per_page: int = 200,
) -> List[Dict[str, Any]]:
    """
    Queries OpenAlex for works in a specific journal matching a keyword.
    """
    query = (
        Works()
        .search(keyword)
        .filter(
            host_venue_id=journal_openalex_id,
            from_publication_date=f"{from_year}-01-01",
        )
    )

    results = query.get(per_page=per_page)
    return results


def extract_metadata(
    work: Dict[str, Any],
    journal_input_name: str,
    keyword: str,
) -> Dict[str, Any]:
    """
    Extracts relevant fields from an OpenAlex work.
    """
    authorships = work.get("authorships", [])
    authors = [
        a.get("author", {}).get("display_name", "")
        for a in authorships if isinstance(a, dict)
    ]

    abstract_inv = work.get("abstract_inverted_index")
    abstract = decompress_abstract(abstract_inv)

    return {
        "journal_input": journal_input_name,
        "journal_openalex": (work.get("host_venue") or {}).get("display_name"),
        "title": work.get("title"),
        "doi": work.get("doi"),
        "year": work.get("publication_year"),
        "authors": "; ".join(authors),
        "abstract": abstract,
        "keyword": keyword,
        "keyword_in_abstract": keyword_in_abstract_strict(keyword, abstract),
        "openalex_id": work.get("id"),
    }


def search_all_journals(
    df_journals: pd.DataFrame,
    keywords: Iterable[str],
    from_year: int = 2010,
    pause_seconds: float = 0.5,
) -> pd.DataFrame:
    """
    Full loop over all journals × keywords.
    """
    all_rows = []

    for _, row in df_journals[df_journals["found"]].iterrows():
        jname = row["input_name"]
        jid = row["openalex_id"]

        print(f"\n Journal: {jname} ({jid})")

        for kw in keywords:
            print(f"   → Searching for keyword: {kw}")
            works = get_works_for_journal_and_query(jid, kw, from_year=from_year)

            for w in works:
                all_rows.append(extract_metadata(w, jname, kw))

            time.sleep(pause_seconds)

    df = pd.DataFrame(all_rows)
    if not df.empty:
        df = df.drop_duplicates(subset=["doi", "title"], keep="first")

    return df
