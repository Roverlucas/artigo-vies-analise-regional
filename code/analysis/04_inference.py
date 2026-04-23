"""
04_inference.py — Primary inferential models (H1, H2, H3).

Implements the GLMM specifications from the SAP (docs/etapa4_sap.md §2-3)
using statsmodels.MixedLM (Python-native) as primary. In execution stage,
cross-validate with pymer4 (lme4 via rpy2) — agreement logged as sanity check.

Why statsmodels.MixedLM primary here:
    - No rpy2/R dependency for pipeline validation
    - Adequate for our design (balanced-ish, Gaussian-transformed)
    - pymer4 agreement check documented in 05_robustness.py

Tests:
    H1: Is global-south indicator β significantly negative?
    H2: Is country × language interaction significant?
    H3: Sabiá-3 × BR vs frontier × BR contrast.

Outputs:
    tables/h1_glmm.csv
    tables/h2_interaction.csv
    tables/h3_contrasts.csv
    results/inference_summary.md  (auto-generated)
"""

from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from benchmark.config import DATA_PROCESSED, TABLES_DIR, RESULTS_DIR


# =========================================================================
# HELPERS
# =========================================================================

def format_ci(est: float, se: float, conf: float = 0.95) -> tuple[float, float]:
    from scipy import stats
    z = stats.norm.ppf((1 + conf) / 2)
    return (est - z * se, est + z * se)


def report_fixed_effect(result, term: str) -> dict:
    est = result.params[term]
    se = result.bse[term]
    ci_lo, ci_hi = format_ci(est, se)
    # Approximate Wald p-value
    z = est / se
    from scipy import stats
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    return {
        "term": term,
        "estimate": round(est, 4),
        "std_error": round(se, 4),
        "ci95_low": round(ci_lo, 4),
        "ci95_high": round(ci_hi, 4),
        "z_value": round(z, 3),
        "p_value": round(p, 4),
    }


# =========================================================================
# H1 — Global South vs Global North
# =========================================================================

def test_h1(df: pd.DataFrame) -> pd.DataFrame:
    """GLMM: composite_accuracy ~ unctad + (1|country) + (1|model_id) + (1|prompt_id)

    Note: statsmodels MixedLM supports one level of random effect grouping;
    for a nested/crossed structure we use country as primary grouping.
    Full three-level random effects cross-validated with pymer4.
    """
    print("=" * 60)
    print("H1: Global South vs Global North")
    print("=" * 60)

    df = df.copy()
    df["is_south"] = (df["unctad"] == "south").astype(int)
    df["prompt_id"] = (df["country_iso3"] + "_" + df["domain_id"] +
                      "_" + df["task_id"] + "_" + df["variant_idx"].astype(str))

    model = smf.mixedlm(
        "composite_accuracy ~ is_south + C(model_id) + C(domain_id) + C(task_id)",
        data=df,
        groups=df["country_iso3"]
    )
    fit = model.fit(reml=True, method=["lbfgs"])

    rows = [report_fixed_effect(fit, "is_south")]
    out = pd.DataFrame(rows)
    out.to_csv(TABLES_DIR / "h1_glmm.csv", index=False)
    print(out.to_string(index=False))
    print(f"\nICC(country) = {fit.cov_re.iloc[0,0] / (fit.cov_re.iloc[0,0] + fit.scale):.3f}")
    return out


# =========================================================================
# H2 — Language × geography interaction
# =========================================================================

def test_h2(df: pd.DataFrame) -> pd.DataFrame:
    """Test country×language interaction via categorical interaction.

    Proxied by is_native_language × is_south interaction for simplicity;
    full categorical country-level interaction in pymer4 version.
    """
    print("\n" + "=" * 60)
    print("H2: Language × geography interaction")
    print("=" * 60)

    df = df.copy()
    df["is_south"] = (df["unctad"] == "south").astype(int)
    df["is_native_int"] = df["is_native_language"].astype(int)
    df["joshi_high"] = (df["joshi_class"] >= 3).astype(int)

    # Three-way interaction: south × native × joshi_class
    model = smf.mixedlm(
        "composite_accuracy ~ is_south * is_native_int * joshi_high + C(model_id)",
        data=df,
        groups=df["country_iso3"]
    )
    fit = model.fit(reml=True, method=["lbfgs"])

    interaction_terms = [t for t in fit.params.index if ":" in t]
    rows = [report_fixed_effect(fit, t) for t in interaction_terms]
    out = pd.DataFrame(rows)
    out.to_csv(TABLES_DIR / "h2_interaction.csv", index=False)
    print(out.to_string(index=False))
    return out


# =========================================================================
# H3 — Sabiá-3 × Brazil contrast
# =========================================================================

def test_h3(df: pd.DataFrame) -> pd.DataFrame:
    """H3a: Sabiá-3 reduces BR gap vs frontier models.

    Pre-specified contrasts:
        contrast_1 = (Sabiá-3 × BR) vs mean({frontier} × BR)
        contrast_2 = (Qwen32B × BR) vs mean({frontier} × BR)  [scale-matched control]

    If |contrast_1| > |contrast_2|, evidence for regional-training benefit
    beyond scale.
    """
    print("\n" + "=" * 60)
    print("H3: Sabiá-3 × Brazil contrasts")
    print("=" * 60)

    br = df[df.country_iso3 == "BRA"].copy()

    frontier_ids = ["gpt5", "claude_opus", "gemini_25"]
    rows = []
    for comparator in ["sabia3", "qwen3_32b"]:
        comp_scores = br[br.model_id == comparator]["composite_accuracy"]
        front_scores = br[br.model_id.isin(frontier_ids)]["composite_accuracy"]

        diff = comp_scores.mean() - front_scores.mean()
        # Welch SE
        se = np.sqrt(comp_scores.var() / len(comp_scores) +
                     front_scores.var() / len(front_scores))
        ci_lo, ci_hi = format_ci(diff, se)
        from scipy import stats
        t_stat = diff / se
        p = 2 * (1 - stats.norm.cdf(abs(t_stat)))

        rows.append({
            "contrast": f"{comparator}_vs_frontier_on_BR",
            "estimate_pp": round(diff * 100, 2),
            "std_error": round(se, 4),
            "ci95_low_pp": round(ci_lo * 100, 2),
            "ci95_high_pp": round(ci_hi * 100, 2),
            "p_value": round(p, 4),
            "n_comparator": len(comp_scores),
            "n_frontier": len(front_scores),
        })

    out = pd.DataFrame(rows)
    out.to_csv(TABLES_DIR / "h3_contrasts.csv", index=False)
    print(out.to_string(index=False))
    return out


# =========================================================================
# MAIN
# =========================================================================

def main():
    df = pd.read_parquet(DATA_PROCESSED / "analytic_synthetic.parquet")
    print(f"# 04_inference.py — N={len(df):,}  [DATA_STATUS = SIMULATION]")

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    h1 = test_h1(df)
    h2 = test_h2(df)
    h3 = test_h3(df)

    # Summary markdown for results/
    with (RESULTS_DIR / "inference_summary.md").open("w") as f:
        f.write("# Inferential Summary [SIMULATION]\n\n")
        f.write(f"N observations: {len(df):,}\n\n")
        f.write("## H1 — Global South vs Global North\n\n")
        f.write(h1.to_markdown(index=False) + "\n\n")
        f.write("## H2 — Language × geography interactions\n\n")
        f.write(h2.to_markdown(index=False) + "\n\n")
        f.write("## H3 — Sabiá-3 × Brazil contrasts\n\n")
        f.write(h3.to_markdown(index=False) + "\n\n")
    print(f"\nSummary written to {RESULTS_DIR / 'inference_summary.md'}")


if __name__ == "__main__":
    main()
