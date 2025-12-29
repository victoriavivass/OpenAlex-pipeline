"""
04_visualise.py

Visualisation of keyword prevalence over time.

Modes:
- MODE = "single"   -> one discipline (one df_all_jyk_<sheet>.csv)
- MODE = "combined" -> Sociology + Political_Science together

Outputs:
- Static PNG (small multiples)
- Interactive HTML (all keywords together)
"""

from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import plotly.express as px


# ============================================================
# CONFIG
# ============================================================
MODE = "combined"   # "single" or "combined"

SHEETS = ["Sociology", "Political_Science"]  # used if MODE == "combined"
SINGLE_SHEET = "Sociology"                  # used if MODE == "single"

YEAR_MIN = 2010

BERT_MIN_YEAR = 2018
BERT_FAMILY = {"BERT", "RoBERTa", "ALBERT", "DistilBERT"}

N_COLS = 3
FILL_ALPHA = 0.22


def enforce_bert_min_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Set BERT-family keyword counts to zero before BERT_MIN_YEAR.
    This MUST run before aggregation so it affects both PNG and HTML outputs.
    """
    df = df.copy()

    # Safety: make sure keyword is a clean string
    df["keyword"] = df["keyword"].astype(str).str.strip()

    # Ensure year is numeric so comparisons work
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    mask = (df["keyword"].isin(BERT_FAMILY)) & (df["year"] < BERT_MIN_YEAR)
    df.loc[mask, "n_articles_with_keyword"] = 0

    return df


# ============================================================
# STATIC SMALL MULTIPLES
# ============================================================
def plot_small_multiples_percentage(df: pd.DataFrame, save_path: Path) -> None:
    yearly = (
        df.groupby(["year", "keyword"], as_index=False)
          .agg(
              n_articles_total=("n_articles_total", "sum"),
              n_articles_with_keyword=("n_articles_with_keyword", "sum"),
          )
    )

    yearly["percentage"] = np.divide(
        100 * yearly["n_articles_with_keyword"],
        yearly["n_articles_total"],
        out=np.zeros(len(yearly)),
        where=yearly["n_articles_total"] != 0,
    )

    if yearly.empty:
        print("No data available for plotting.")
        return

    years = range(int(YEAR_MIN), int(yearly["year"].max()) + 1)
    keywords = sorted(yearly["keyword"].unique())

    grid = (
        pd.MultiIndex.from_product([years, keywords], names=["year", "keyword"])
        .to_frame(index=False)
        .merge(yearly[["year", "keyword", "percentage"]], how="left")
        .fillna(0)
    )

    # drop keywords that are always zero
    keep = grid.groupby("keyword")["percentage"].max()
    keywords = keep[keep > 0].index.tolist()
    grid = grid[grid["keyword"].isin(keywords)]

    if not keywords:
        print("All keywords are zero after filtering.")
        return

    n = len(keywords)
    n_rows = (n + N_COLS - 1) // N_COLS

    fig, axes = plt.subplots(
        n_rows, N_COLS,
        figsize=(4 * N_COLS, 3 * n_rows),
        sharey=True,
    )
    axes = np.array(axes).reshape(-1)

    palette = plt.cm.tab10.colors

    for i, (ax, kw) in enumerate(zip(axes, keywords)):
        data = grid[grid["keyword"] == kw]

        ax.plot(data["year"], data["percentage"], color=palette[i % 10], lw=2)
        ax.fill_between(
            data["year"], data["percentage"], 0,
            color=palette[i % 10], alpha=FILL_ALPHA
        )

        ax.set_title(kw, fontsize=11)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    for ax in axes[len(keywords):]:
        ax.axis("off")

    fig.text(0.01, 0.5, "% of articles with keyword in abstract",
             va="center", rotation="vertical")
    fig.tight_layout()

    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()


# ============================================================
# INTERACTIVE (ALL KEYWORDS TOGETHER)
# ============================================================
def plot_interactive(df: pd.DataFrame, save_path: Path) -> None:
    yearly = (
        df.groupby(["year", "keyword"], as_index=False)
          .agg(
              n_articles_total=("n_articles_total", "sum"),
              n_articles_with_keyword=("n_articles_with_keyword", "sum"),
          )
    )

    yearly["percentage"] = np.divide(
        100 * yearly["n_articles_with_keyword"],
        yearly["n_articles_total"],
        out=np.zeros(len(yearly)),
        where=yearly["n_articles_total"] != 0,
    )

    fig = px.line(
        yearly,
        x="year",
        y="percentage",
        color="keyword",
        markers=True,
        title=f"Keyword prevalence over time ({'combined disciplines' if MODE == 'combined' else SINGLE_SHEET})",
        labels={"percentage": "% of articles"},
    )

    fig.write_html(save_path)
    fig.show()


# ============================================================
# MAIN
# ============================================================
def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "outputs" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Load data
    # -------------------------
    if MODE == "single":
        path = root / "outputs" / f"df_all_jyk_{SINGLE_SHEET}.csv"
        df = pd.read_csv(path)

    elif MODE == "combined":
        frames = []
        for sheet in SHEETS:
            path = root / "outputs" / f"df_all_jyk_{sheet}.csv"
            frames.append(pd.read_csv(path))
        df = pd.concat(frames, ignore_index=True)

    else:
        raise ValueError("MODE must be 'single' or 'combined'")

    # enforce numeric
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["n_articles_total"] = pd.to_numeric(df["n_articles_total"], errors="coerce")
    df["n_articles_with_keyword"] = pd.to_numeric(df["n_articles_with_keyword"], errors="coerce")

    # APPLY BERT RULE HERE (affects both plots)
    df = enforce_bert_min_year(df)

    # -------------------------
    # Outputs
    # -------------------------
    suffix = "combined" if MODE == "combined" else SINGLE_SHEET

    static_path = out_dir / f"keywords_trends_color_{suffix}.png"
    html_path = out_dir / f"keywords_trends_interactive_{suffix}.html"

    plot_small_multiples_percentage(df, static_path)
    plot_interactive(df, html_path)

    print(f"Saved static figure: {static_path}")
    print(f"Saved interactive figure: {html_path}")


if __name__ == "__main__":
    main()
