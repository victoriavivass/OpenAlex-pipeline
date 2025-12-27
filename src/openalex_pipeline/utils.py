"""
Utility functions for the OpenAlex pipeline.

These helpers keep the pipeline modular and reproducible.
"""

from __future__ import annotations

import re
from typing import Iterable, Optional, List, Dict

import pandas as pd
from pyalex import Works, Sources

# A) Abstract functions

def decompress_abstract(inverted_index: dict) -> str:
    if inverted_index is None:
        return None

    max_pos = max(max(positions) for positions in inverted_index.values())
    words = [""] * (max_pos + 1) # create a list with the size of the abstract

    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word

    return " ".join(words)

ACRONYM_PATTERNS = {
    r"\bLLM(s)?\b",
    r"\bGPT\b",
    r"\bBERT\b",
    r"\bLSTM\b",
    r"\bAI\b",
}

def keyword_in_abstract_strict(query_label: str, abstract: str) -> bool:
    if not abstract or not query_label:
        return False
    # Acronyms are matched case-sensitively; other keywords are case-insensitive
    flags = 0 if query_label in ACRONYM_PATTERNS else re.IGNORECASE

    try:
        return re.search(query_label, abstract, flags=flags) is not None
    except re.error:
        return False
    
# B) OpenAlex: Search and download functions

def get_journal_id_by_issn_or_name(journal_name, issn_field):
    """
    Returns: (openalex_id, display_name, matched_issn)
    Tries ISSN first, then journal name.
    """
    # Try ISSNs if available
    if pd.notna(issn_field) and issn_field not in ["", "nan", "NaN"]:
        issns = [i.strip() for i in str(issn_field).split(",")]
        for issn in issns:
            if not issn:
                continue
            results = Sources().filter(issn=issn).get()
            if results:
                best = results[0]
                return best["id"], best["display_name"], issn

    # Fallback: search by journal name
    results = Sources().search(journal_name).get()
    if results:
        best = results[0]
        return best["id"], best["display_name"], None

    return None, None, None

def get_all_works_since_2010(journal_id: str) -> List[Dict]:
    """
    Retrieve all OpenAlex works associated with a given journal
    published from 2010 onwards.

    The query filters works by the journal OpenAlex identifier and
    applies pagination to iterate through all available result pages.

    Returns:
        List[Dict]: List of OpenAlex works, each represented as a dictionary.
    """
    works_pages = (
        Works()
        .filter(
            locations={"source": {"id": journal_id}},
            from_publication_date="2010-01-01"
        )
        .paginate(per_page=200)
    )

    all_works: List[Dict] = []
    for page in works_pages:
        # Each page contains a list of works
        all_works.extend(page)

    return all_works


def total_articles_journal_per_year(
    works: List[Dict],
    journal_name: str
) -> pd.DataFrame:
    """
    Aggregate the total number of works per publication year for a journal.

    Works without a publication year are excluded from the aggregation.

    Returns:
        pd.DataFrame: DataFrame with columns
            - journal_input
            - year
            - n_articles_total
    """
    rows: List[Dict] = []

    for w in works:
        year = w.get("publication_year")
        if year is None:
            continue

        rows.append({
            "journal_input": journal_name,
            "year": int(year)
        })

    if not rows:
        return pd.DataFrame(
            columns=["journal_input", "year", "n_articles_total"]
        )

    return (
        pd.DataFrame(rows)
        .groupby(["journal_input", "year"])
        .size()
        .reset_index(name="n_articles_total")
    )

# C) Metadata extraction 

def extract_metadata(work: dict, journal_label: str, query_label: str) -> dict:
    """
    Extract selected metadata fields from a single OpenAlex work.
    Reconstruct the abstract and check whether the keyword appears
    as a full word in the abstract.
    """

    doi = work.get("doi")
    year = work.get("publication_year")
    title = work.get("title")

    # Extract journal name from locations
    journal = None    # journal name as in OpenAlex
    locations = work.get("locations") or []
    for loc in locations:
        src = loc.get("source")
        if src and src.get("display_name"):
            journal = src["display_name"]
            break

    # Extract authors safely (avoid None)
    authors_raw = work.get("authorships", [])
    authors = []
    for auth in authors_raw:
        author_dict = auth.get("author", {}) or {}
        name = author_dict.get("display_name")
        if isinstance(name, str):   # Only accept valid strings
            authors.append(name)

    authors_str = "; ".join(authors)

    # Rebuild abstract
    abstract_idx = work.get("abstract_inverted_index")
    abstract = decompress_abstract(abstract_idx) if abstract_idx else None

    # Strict keyword match
    keyword_in_abstract = keyword_in_abstract_strict(query_label, abstract)

    return {
        "journal_input": journal_label,
        "query": query_label,
        "doi": doi,
        "year": year,
        "title": title,
        "journal_openalex": journal,
        "authors": authors_str,
        "abstract": abstract,
        "keyword_in_abstract": keyword_in_abstract
    }

# D) Filtering function
def filter_by_keyword_locally(
    works: list[dict],
    keyword: str,
    journal_name: str
) -> list[dict]:
    """
    Process a list of OpenAlex works and return only those for which
    the specified keyword appears in the abstract.

    The function relies on extract_metadata() to reconstruct abstracts
    and evaluate keyword presence.

    Returns:
        List of metadata dictionaries for works matching the keyword.
    """
    filtered_rows = []

    for work in works:
        metadata = extract_metadata(work, journal_name, keyword)

        if metadata["keyword_in_abstract"]:
            filtered_rows.append(metadata)

    return filtered_rows