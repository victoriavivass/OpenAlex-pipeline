from __future__ import annotations
from typing import Dict, List, Optional
import re


def decompress_abstract(inverted_index: Optional[Dict[str, List[int]]]) -> Optional[str]:
    """
    Reconstructs an abstract from OpenAlex's inverted_index format.
    Returns a plain text abstract or None.
    """
    if not inverted_index:
        return None

    max_position = max(max(pos_list) for pos_list in inverted_index.values())
    words = [""] * (max_position + 1)

    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word

    abstract = " ".join(words).strip()
    abstract = re.sub(r"\s+([.,;:?!])", r"\1", abstract)
    return abstract or None


def keyword_in_abstract_strict(keyword: str, abstract: Optional[str]) -> bool:
    """
    Checks whether the full keyword (phrase) appears in the abstract.
    Case-insensitive, exact phrase match.
    """
    if not keyword or not abstract:
        return False

    pattern = re.escape(keyword.lower())
    return pattern in abstract.lower()
