"""
04_visualise.py

Create small-multiples (static) plots of keyword prevalence over time.

Input:
- outputs/keyword_prevalence_<sheet>.csv (from 03_analyse.py)
  Required columns:
    - journal_input
    - keyword
    - year
    - n_keyword_hits
    - n_articles_total

Output:
- outputs/figures/keywords_trends_color_<sheet>.png
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def plot_small_multiples_percentage(
    df_all_jyk: pd.DataFrame,
    year_min: int = 2010,
    year_max: int | None = None,
    bert_family: set[str] | None = None,
    bert_min_year: int = 2018,
    drop_all_zero: bool = True,
    order: list[str] | None = None,
    title: str | None = None,
    bw: bool = False,
    save_path: str | None = None,
    n_cols: int = 3,
    fill_alpha: float = 0.22,
):
    df = df_all_jyk.copy()

    # 1) Enforce temporal validity for BERT-family keywords (set to 0 before bert_min_year)
    if bert_family:
        mask = (df["keyword"].isin(bert_family)) & (df["year"] < bert_min_year)
        df.loc[mask, ["n_articles_with_keyword", "percentage"]] = 0

    # 2) Aggregate across journals to get yearly totals per keyword
    yearly = (
        df.groupby(["year", "keyword"], as_index=False)
          .agg(
              n_articles_total=("n_articles_total", "sum"),
              n_articles_with_keyword=("n_articles_with_keyword", "sum"),
          )
    )

    # 3) Restrict year range
    if year_max is None:
        year_max = int(yearly["year"].max()) if not yearly.empty else year_min
    yearly = yearly[(yearly["year"] >= int(year_min)) & (yearly["year"] <= int(year_max))].copy()

    # 4) Compute percentage safely (avoid division by zero)
    yearly["percentage"] = np.divide(
        100.0 * yearly["n_articles_with_keyword"].astype(float),
        yearly["n_articles_total"].astype(float),
        out=np.zeros(len(yearly), dtype=float),
        where=yearly["n_articles_total"].to_numpy() != 0,
    )

    # 5) Build a continuous (year × keyword) grid and fill missing with 0
    years = list(range(int(year_min), int(year_max) + 1))

    if order is not None:
        categories = [k for k in order if k in set(yearly["keyword"])]
    else:
        categories = sorted(yearly["keyword"].unique())

    grid = pd.MultiIndex.from_product([years, categories], names=["year", "keyword"]).to_frame(index=False)
    yearly = grid.merge(yearly[["year", "keyword", "percentage"]], on=["year", "keyword"], how="left")
    yearly["percentage"] = yearly["percentage"].fillna(0.0)

    # 6) Drop keywords that are 0 for all years (optional)
    if drop_all_zero and not yearly.empty:
        keep = yearly.groupby("keyword")["percentage"].max()
        keep = keep[keep > 0].index.tolist()
        yearly = yearly[yearly["keyword"].isin(keep)]
        categories = [k for k in categories if k in keep]

    # 7) Plot small multiples
    n = len(categories)
    if n == 0:
        print("No keywords to plot after filtering.")
        return

    n_rows = (n + n_cols - 1) // n_cols

    palette = [
        "#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e",
        "#e6ab02", "#a6761d", "#1f78b4", "#fb9a99", "#cab2d6",
    ]
    linestyles = ["-", "--", ":", "-."]

    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(4 * n_cols, 3 * n_rows),
        sharex=False,
        sharey=True,
    )
    axes = np.array(axes).reshape(-1)

    for i, (ax, cat) in enumerate(zip(axes, categories)):
        data = yearly[yearly["keyword"] == cat].sort_values("year")

        if bw:
            ax.plot(
                data["year"], data["percentage"],
                color="black",
                linestyle=linestyles[i % len(linestyles)],
                linewidth=2,
            )
            ax.fill_between(
                data["year"], data["percentage"],
                0,
                color="black",
                alpha=fill_alpha,
            )
        else:
            c = palette[i % len(palette)]
            ax.plot(
                data["year"], data["percentage"],
                color=c,
                linewidth=2,
            )
            ax.fill_between(
                data["year"], data["percentage"],
                0,
                color=c,
                alpha=fill_alpha,
            )

        ax.set_title(cat, fontsize=11)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))
        ax.set_facecolor("white")

    for ax in axes[len(categories):]:
        ax.axis("off")

    if title:
        fig.suptitle(title, fontsize=12, y=1.02)

    fig.patch.set_facecolor("white")
    fig.text(
        0.001, 0.5,
        "(%) Percentage of articles with keyword in abstract",
        va="center",
        rotation="vertical",
        fontsize=10,
    )
    fig.subplots_adjust(left=0.08)
    fig.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()


def main() -> None:
    sheet_name = "Sociology"

    root = Path(__file__).resolve().parents[1]
    in_path = root / "outputs" / f"df_all_jyk_{sheet_name}.csv"
    out_dir = root / "outputs" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise FileNotFoundError(f"Missing input file: {in_path}")

    df = pd.read_csv(in_path)

    required = {"journal_input", "keyword", "year", "n_articles_with_keyword", "n_articles_total"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"keyword_prevalence file missing columns: {sorted(missing)}")

    
    df_all_jyk = df.copy()

    df_all_jyk["year"] = pd.to_numeric(df_all_jyk["year"], errors="coerce").astype("Int64")
    df_all_jyk["n_articles_total"] = pd.to_numeric(df_all_jyk["n_articles_total"], errors="coerce").fillna(0)
    df_all_jyk["n_articles_with_keyword"] = pd.to_numeric(
        df_all_jyk["n_articles_with_keyword"], errors="coerce"
    ).fillna(0)

    df_all_jyk["percentage"] = np.divide(
        100.0 * df_all_jyk["n_articles_with_keyword"].astype(float),
        df_all_jyk["n_articles_total"].astype(float),
        out=np.zeros(len(df_all_jyk), dtype=float),
        where=df_all_jyk["n_articles_total"].to_numpy() != 0,
    )

    BERT_FAMILY = {"BERT", "RoBERTa", "ALBERT", "DistilBERT"}
    order = None  # paste your custom order list here if you have one

    save_path = str(out_dir / f"keywords_trends_color_{sheet_name}.png")

    plot_small_multiples_percentage(
        df_all_jyk=df_all_jyk,
        year_min=2010,
        bert_family=BERT_FAMILY,
        bert_min_year=2018,
        order=order,
        title=None,
        bw=False,
        save_path=save_path,
        n_cols=3,
        fill_alpha=0.22,
    )

    print(f"Saved figure: {save_path}")


if __name__ == "__main__":
    main()