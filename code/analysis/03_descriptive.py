"""
03_descriptive.py — Descriptive statistics and balance checks.

Generates descriptive tables and figures for the sample and outcome:
    - Sample composition by country/continent/income/Joshi class
    - Outcome distributions by main factors
    - Raw group means with confidence intervals (pre-inferential)

Output:
    tables/descriptive_sample.csv
    tables/descriptive_outcomes.csv
    figures/fig1_sample_composition.{png,pdf}
"""

from __future__ import annotations
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from benchmark.config import DATA_PROCESSED, TABLES_DIR, FIGURES_DIR


def main():
    df = pd.read_parquet(DATA_PROCESSED / "analytic_synthetic.parquet")
    print(f"# 03_descriptive.py — N={len(df):,}")

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # ----- Table 1: sample composition -----
    sample = (df.groupby(
        ["country_iso3", "continent", "unctad", "income_group", "joshi_class"]
    ).size().reset_index(name="n_observations"))
    sample.to_csv(TABLES_DIR / "descriptive_sample.csv", index=False)
    print(f"Wrote sample composition: {TABLES_DIR / 'descriptive_sample.csv'}")

    # ----- Table 2: outcome by key factors -----
    def ci95(x):
        return 1.96 * x.std() / np.sqrt(len(x))

    outcome = (df.groupby(["unctad", "model_category"])
               .agg(mean_acc=("composite_accuracy", "mean"),
                    sd_acc=("composite_accuracy", "std"),
                    n=("composite_accuracy", "count"),
                    ci95=("composite_accuracy", ci95))
               .reset_index())
    outcome.to_csv(TABLES_DIR / "descriptive_outcomes.csv", index=False)
    print(f"Wrote outcome table: {TABLES_DIR / 'descriptive_outcomes.csv'}")
    print(outcome.to_string(index=False))

    # ----- Figure 1: outcome by country, colored by UNCTAD -----
    fig, ax = plt.subplots(figsize=(7.2, 4), dpi=150)
    order = (df.groupby("country_iso3")["composite_accuracy"].mean()
             .sort_values().index.tolist())
    colors = {"north": "#0072B2", "south": "#D55E00"}  # Okabe-Ito

    means = []
    errs = []
    cols = []
    for iso in order:
        sub = df[df.country_iso3 == iso]
        m = sub["composite_accuracy"].mean()
        e = 1.96 * sub["composite_accuracy"].std() / np.sqrt(len(sub))
        means.append(m)
        errs.append(e)
        cols.append(colors[sub["unctad"].iloc[0]])

    positions = np.arange(len(order))
    ax.errorbar(positions, means, yerr=errs, fmt="o", color="#333",
                ecolor="#999", capsize=3, markersize=5, zorder=3)
    for pos, m, col in zip(positions, means, cols):
        ax.scatter(pos, m, color=col, s=40, zorder=4, edgecolor="white", linewidth=0.5)

    ax.set_xticks(positions)
    ax.set_xticklabels(order, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Composite accuracy (95% CI)", fontsize=9)
    ax.set_xlabel("Country (ISO3)", fontsize=9)
    ax.set_title("Mean composite accuracy by country [SIMULATION]", fontsize=10)
    ax.grid(axis="y", alpha=0.3, linewidth=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Legend
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(color=colors["north"], label="Global North (UNCTAD)"),
        Patch(color=colors["south"], label="Global South (UNCTAD)"),
    ], loc="lower right", fontsize=8, frameon=False)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "fig1_sample_composition.png", dpi=300, bbox_inches="tight")
    plt.savefig(FIGURES_DIR / "fig1_sample_composition.pdf", bbox_inches="tight")
    plt.close()
    print(f"Wrote Figure 1: {FIGURES_DIR / 'fig1_sample_composition.png'}")


if __name__ == "__main__":
    main()
