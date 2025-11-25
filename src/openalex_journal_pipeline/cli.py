from __future__ import annotations
import argparse
from pathlib import Path
from .pipeline import run_pipeline


def parse_args():
    parser = argparse.ArgumentParser(
        description="OpenAlex Journal Keyword Pipeline"
    )
    parser.add_argument("--input", required=True, help="Input Excel file")
    parser.add_argument("--sheet", required=True, help="Sheet name")
    parser.add_argument("--output", required=True, help="Output Excel file")
    parser.add_argument("--keywords", required=True,
                        help="Comma-separated list of keywords")
    parser.add_argument("--from-year", type=int, default=2010,
                        help="Minimum publication year (default 2010)")
    return parser.parse_args()


def main():
    args = parse_args()
    keywords = [k.strip() for k in args.keywords.split(",")]

    run_pipeline(
        input_excel=Path(args.input),
        sheet_name=args.sheet,
        output_excel=Path(args.output),
        keywords=keywords,
        from_year=args.from_year,
    )
