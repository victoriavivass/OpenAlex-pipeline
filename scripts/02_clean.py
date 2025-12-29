"""
02_clean.py

Transform raw OpenAlex extraction output into a clean dataset of keyword hits.
- Loads the raw pickle produced by 01_extract.py
- Reconstructs abstracts once per work
- Checks all regex patterns against the abstract
- Outputs:
  - works_keyword_hits_<sheet>.csv (hits only)
  - summary_keyword_hits_<sheet>.csv (journal-keyword-year counts)
"""

import sys
from pathlib import Path
from typing import Any
import pandas as pd

# Make the /src directory importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openalex_pipeline.utils import decompress_abstract, keyword_in_abstract_strict


PATTERN_TO_LABEL = {
    # LLM
    r"\bLLM(s)?\b": "Large Language Model (LLM)",
    r"\blarge language model(s)?\b": "Large Language Model (LLM)",

    # GPT
    r"\bGPT\b": "Generative Pre-trained Transformer (GPT)",
    r"\bgenerative pre-trained transformer\b": "Generative Pre-trained Transformer (GPT)",
    r"\bgenerative pre-trained transformer\s*\(gpt\)\b": "Generative Pre-trained Transformer (GPT)",

    # BERT family
    r"\bBERT\b": "BERT",
    r"\bRoBERTa\b": "RoBERTa",
    r"\bALBERT\b": "ALBERT",
    r"\bDistilBERT\b": "DistilBERT",

    # LSTM
    r"\bLSTM\b": "Long Short-term Memory (LSTM)",
    r"\blong short-term memory\b": "Long Short-term Memory (LSTM)",

    # Language model (general)
    r"\blanguage model(s)?\b": "Language model",

    # Transformer terms
    r"\btransformer(s)?\b": "Transformer",
    r"\bencoder(s)?\b": "Encoder",
    r"\bdecoder(s)?\b": "Decoder",

    # AI
    r"\bartificial intelligence\b": "Artificial intelligence",
    r"(?=.*\b(model)\b).*?\bAI\b": "Artificial intelligence",

    # ML classic
    r"\bmachine learning\b": "Machine learning",
    r"\bclassifier(s)?\b": "Classifier",
    r"\btraining data\b": "Training data",
    r"\bsupport vector machine(s)?\b": "Support vector machine (SVM)",

    # Neural networks
    r"\bneural network(s)?\b": "Neural network",
    r"\bartificial neural network(s)?\b": "Artificial neural network",
}


def main() -> None:
    sheet_name = "Sociology"
    raw_path = ROOT / "outputs" / f"openalex_raw_works_{sheet_name}.pkl"

    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw file not found: {raw_path}\n"
            "Make sure 01_extract.py produced the .pkl output."
        )

    records: list[dict[str, Any]] = pd.read_pickle(raw_path)

    rows: list[dict[str, Any]] = []

    # Progress counters
    total_journals = len(records)

    for j, rec in enumerate(records, start=1):
        journal_input = rec["journal_input"]
        works = rec["works_raw"]

        print(f"[{j}/{total_journals}] Processing {journal_input} ({len(works)} works)")

        for w_i, work in enumerate(works, start=1):
            year = work.get("publication_year")
            title = work.get("title")
            doi = work.get("doi")

            # Skip incomplete entries early
            if year is None or title is None:
                continue

            # Get journal name from locations (optional)
            journal_openalex = None
            for loc in (work.get("locations") or []):
                src = loc.get("source")
                if src and src.get("display_name"):
                    journal_openalex = src["display_name"]
                    break

            # Authors (optional)
            authors = []
            for auth in (work.get("authorships") or []):
                ad = (auth.get("author") or {})
                name = ad.get("display_name")
                if isinstance(name, str):
                    authors.append(name)
            authors_str = "; ".join(authors)

            # Rebuild abstract ONCE
            abstract_idx = work.get("abstract_inverted_index")
            abstract = decompress_abstract(abstract_idx) if abstract_idx else None
            if not abstract:
                continue

            # Check all patterns; keep only hits
            for pattern, label in PATTERN_TO_LABEL.items():
                if keyword_in_abstract_strict(pattern, abstract):
                    rows.append(
                        {
                            "journal_input": journal_input,
                            "journal_openalex": journal_openalex,
                            "doi": doi,
                            "year": int(year),
                            "title": title,
                            "authors": authors_str,
                            "keyword": label,  # clean label
                            "pattern": pattern,  # keep regex for traceability
                        }
                    )

    df_hits = pd.DataFrame(rows)

    out_dir = ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)

    hits_path = out_dir / f"works_keyword_hits_{sheet_name}.csv"
    summary_path = out_dir / f"summary_keyword_hits_{sheet_name}.csv"

    df_hits.to_csv(hits_path, index=False)

    summary = (
        df_hits.groupby(["journal_input", "keyword", "year"])
        .size()
        .reset_index(name="n_keyword_hits")
        .sort_values(["journal_input", "keyword", "year"])
    )
    summary.to_csv(summary_path, index=False)

    print(f"\nSaved keyword hits only: {hits_path}")
    print(f"Saved summary table: {summary_path}")


if __name__ == "__main__":
    main()