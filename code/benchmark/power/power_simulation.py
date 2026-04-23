"""
power_simulation.py — Monte Carlo power analysis for primary hypotheses.

Implements the power simulation described in SAP §3. Uses analytical Gaussian
approximation to the GLMM as Python-native implementation; the R-based
pymer4.simulate.merMod path is called in execution stage for cross-validation.

Usage:
    python -m benchmark.power.power_simulation --hypothesis H1
    python -m benchmark.power.power_simulation --hypothesis H1 --grid

Output:
    results/power_h1.csv — power surface over effect size × N countries
    figures/fig_power_h1.{png,pdf}
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from benchmark.config import RESULTS_DIR, FIGURES_DIR


# =========================================================================
# H1 POWER SIMULATION
# =========================================================================

def simulate_h1_once(
    n_south: int, n_north: int, n_models: int, n_prompts: int, n_reps: int,
    effect: float,
    sigma_country: float, sigma_model: float, sigma_prompt: float, sigma_resid: float,
    rng: np.random.Generator,
) -> float:
    """Run one simulation; return p-value for is_south coefficient."""
    n_countries = n_south + n_north

    # Random intercepts
    country_re = rng.normal(0, sigma_country, n_countries)
    model_re = rng.normal(0, sigma_model, n_models)
    prompt_re = rng.normal(0, sigma_prompt, n_prompts)

    # Build long dataframe
    rows = []
    for c in range(n_countries):
        is_south = c < n_south
        fixed = 0.5 + (-effect if is_south else 0.0)
        for m in range(n_models):
            for p in range(n_prompts):
                for r in range(n_reps):
                    y = fixed + country_re[c] + model_re[m] + prompt_re[p] + \
                        rng.normal(0, sigma_resid)
                    y = np.clip(y, 0, 1)
                    rows.append((y, c, m, p, int(is_south)))

    df = pd.DataFrame(rows, columns=["y", "country", "model", "prompt", "is_south"])

    # Fast OLS with cluster-robust SE at country level
    # (Approximation to GLMM; conservative and computationally cheap)
    import statsmodels.api as sm
    X = sm.add_constant(df[["is_south"]])
    fit = sm.OLS(df["y"], X).fit(cov_type="cluster",
                                  cov_kwds={"groups": df["country"]})
    return fit.pvalues["is_south"]


def power_for_params(
    n_iter: int, effect: float, n_south: int = 12, n_north: int = 3,
    n_models: int = 6, n_prompts: int = 50, n_reps: int = 5,
    sigma_country: float = 0.20, sigma_model: float = 0.17,
    sigma_prompt: float = 0.14, sigma_resid: float = 0.39,
    alpha: float = 0.05, seed: int = 42,
) -> float:
    rng = np.random.default_rng(seed)
    detected = 0
    for i in range(n_iter):
        p = simulate_h1_once(n_south, n_north, n_models, n_prompts, n_reps,
                             effect, sigma_country, sigma_model, sigma_prompt,
                             sigma_resid, rng)
        if p < alpha:
            detected += 1
    return detected / n_iter


# =========================================================================
# MAIN
# =========================================================================

def run_grid(output_csv: Path, n_iter: int = 200) -> pd.DataFrame:
    """Run power grid over effect size and sample size configurations."""
    effect_sizes = [0.05, 0.075, 0.10, 0.125, 0.15]
    south_sizes = [8, 10, 12, 15]

    rows = []
    for es in effect_sizes:
        for ns in south_sizes:
            n_north = 3
            pwr = power_for_params(
                n_iter=n_iter, effect=es, n_south=ns, n_north=n_north,
                n_prompts=30  # Reduced for simulation speed
            )
            rows.append({
                "effect_size": es,
                "n_south": ns,
                "n_north": n_north,
                "n_total_countries": ns + n_north,
                "power": pwr,
                "n_iter": n_iter,
            })
            print(f"ES={es:.3f}, N_south={ns}: power={pwr:.3f}")

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    return df


def plot_power_surface(df: pd.DataFrame, output_fig: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)

    for ns in sorted(df["n_total_countries"].unique()):
        sub = df[df["n_total_countries"] == ns]
        ax.plot(sub["effect_size"], sub["power"], marker="o",
                label=f"N countries = {ns}", linewidth=1.5)

    ax.axhline(0.80, color="#999", linestyle="--", linewidth=0.5, label="Power = 0.80")
    ax.axhline(0.90, color="#666", linestyle="--", linewidth=0.5, label="Power = 0.90")

    ax.set_xlabel("Effect size (absolute accuracy gap, Global South vs North)", fontsize=9)
    ax.set_ylabel("Power", fontsize=9)
    ax.set_title("Monte Carlo power for H1 [SIMULATION]", fontsize=10)
    ax.legend(fontsize=8, frameon=False, loc="lower right")
    ax.grid(alpha=0.3, linewidth=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim([0, 1.05])

    plt.tight_layout()
    plt.savefig(output_fig.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.savefig(output_fig.with_suffix(".pdf"), bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--hypothesis", default="H1")
    ap.add_argument("--n_iter", type=int, default=200,
                    help="Number of Monte Carlo replicates per cell (200 for quick test, 2000 for publication)")
    ap.add_argument("--grid", action="store_true", help="Run full grid vs single config")
    args = ap.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    if args.grid:
        out_csv = RESULTS_DIR / f"power_{args.hypothesis.lower()}_grid.csv"
        df = run_grid(out_csv, n_iter=args.n_iter)
        print(f"\nGrid complete. Written to {out_csv}")
        out_fig = FIGURES_DIR / f"fig_power_{args.hypothesis.lower()}"
        plot_power_surface(df, out_fig)
        print(f"Figure: {out_fig}.png / .pdf")
    else:
        # Design-point power at SESOI=0.10, N=15
        pwr = power_for_params(n_iter=args.n_iter, effect=0.10, n_south=12, n_north=3,
                               n_prompts=30)
        print(f"\nH1 power at SESOI=0.10, N=15 countries, n_iter={args.n_iter}: {pwr:.3f}")
