"""
simulate_outcomes.py — Calibrated synthetic outcome generation.

Produces a synthetic analytic dataset reflecting the EFFECTS HYPOTHESIZED in
the SAP (docs/etapa4_sap.md). This serves TWO purposes:

    1. Pipeline validation: analysis scripts can be tested end-to-end without
       real API data.
    2. Pre-registration: the expected output under H1 (true) is simulated so
       reviewers see our predictions concretely.

IMPORTANT: output labeled as SIMULATION (DATA_STATUS = SIMULATION). Real
results replace this in the execution stage.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path

from .config import COUNTRIES, LLMS, DOMAINS, TASKS, EXPERIMENT, DATA_PROCESSED


# =========================================================================
# HYPOTHESIZED EFFECT SIZES (from SAP §3 power analysis)
# =========================================================================

# Baseline accuracy (Global North, English, frontier model): mean composite ~ 0.70
BASELINE_ACCURACY = 0.70

# H1 effect: 10pp gap Global South vs Global North
H1_SOUTH_PENALTY = -0.10

# H2 effect: language × country interaction
#   EN on Global South country: full H1 penalty
#   Native lang (high-resource, class 3-4) on own country: -0.02 extra (small benefit)
#   Native lang (low-resource, class 1-2) on own country: +0.05 extra (penalty)
H2_HIGH_RESOURCE_NATIVE_BONUS = -0.02
H2_LOW_RESOURCE_NATIVE_PENALTY = +0.05

# H3 effect: Sabiá-3 on Brazilian prompts recovers ~70% of gap (H3a scenario)
#           Sabiá-3 on non-Brazilian Lusophone prompts: no benefit or slight displacement
H3A_SABIA_BR_RECOVERY = 0.07   # Recovers 7/10 pp of 10pp gap

# H4 effect: Spearman between log(tokens) and accuracy
#   Assume monotonic relation; simulate via rank-correlated random effects
H4_TARGET_RHO = 0.70

# Variance components (from SAP)
SIGMA_COUNTRY = 0.20
SIGMA_MODEL = 0.17
SIGMA_PROMPT = 0.14
SIGMA_RESID = 0.39  # High — captures prompt-level idiosyncrasy


# =========================================================================
# CORPUS REPRESENTATION PROXIES (public approximations)
# =========================================================================

# Approximate Common Crawl token share by country (ccTLD-based)
# Source approximations from commoncrawl.github.io/cc-crawl-statistics/
# These are ILLUSTRATIVE for simulation; real values extracted in execution.
APPROX_CC_TOKEN_SHARE = {
    "USA": 0.398, "DEU": 0.054, "JPN": 0.043,
    "BRA": 0.041, "MEX": 0.014, "ARG": 0.008, "PER": 0.002,
    "IND": 0.032, "IDN": 0.010, "PHL": 0.003, "BGD": 0.001,
    "NGA": 0.002, "ZAF": 0.005, "KEN": 0.001, "EGY": 0.003,
}


def simulate_analytic_dataset(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Generate country-level random intercepts correlated with log(tokens)
    # so that H4 is built into the DGP.
    countries_iso = [c.iso3 for c in COUNTRIES]
    log_tokens = np.array([np.log(APPROX_CC_TOKEN_SHARE[c]) for c in countries_iso])
    log_tokens_z = (log_tokens - log_tokens.mean()) / log_tokens.std()

    # Country random effect correlated with log_tokens (rho = H4_TARGET_RHO)
    indep = rng.normal(0, 1, size=len(countries_iso))
    country_re = H4_TARGET_RHO * log_tokens_z + np.sqrt(1 - H4_TARGET_RHO ** 2) * indep
    country_re *= SIGMA_COUNTRY

    country_effects = dict(zip(countries_iso, country_re))

    # Model random effects
    model_effects = dict(zip(
        [m.id for m in LLMS],
        rng.normal(0, SIGMA_MODEL, size=len(LLMS))
    ))

    rows = []
    for country in COUNTRIES:
        c_re = country_effects[country.iso3]
        is_south = country.unctad == "south"
        for domain in DOMAINS:
            for task in TASKS:
                for language in country.test_languages:
                    for variant in range(EXPERIMENT.n_prompts_per_country_domain_task):
                        prompt_re = rng.normal(0, SIGMA_PROMPT)
                        is_native_lang = language != "en" and language in country.official_langs
                        high_resource_lang = country.joshi_class_primary >= 3

                        # Language × geography effect
                        h2_effect = 0.0
                        if is_native_lang and is_south:
                            if high_resource_lang:
                                h2_effect = H2_HIGH_RESOURCE_NATIVE_BONUS
                            else:
                                h2_effect = H2_LOW_RESOURCE_NATIVE_PENALTY

                        for model in LLMS:
                            m_re = model_effects[model.id]

                            # H3: Sabiá-3 on Brazilian prompts
                            h3_effect = 0.0
                            if model.id == "sabia3" and country.iso3 == "BRA":
                                h3_effect = H3A_SABIA_BR_RECOVERY

                            for rep in range(EXPERIMENT.n_replicates_per_call):
                                noise = rng.normal(0, SIGMA_RESID)
                                y = (BASELINE_ACCURACY
                                     + (H1_SOUTH_PENALTY if is_south else 0)
                                     + h2_effect
                                     + h3_effect
                                     + c_re
                                     + m_re
                                     + prompt_re
                                     + noise)
                                y = float(np.clip(y, 0, 1))

                                rows.append({
                                    "country_iso3": country.iso3,
                                    "continent": country.continent,
                                    "unctad": country.unctad,
                                    "income_group": country.income,
                                    "joshi_class": country.joshi_class_primary,
                                    "domain_id": domain.id,
                                    "task_id": task.id,
                                    "language": language,
                                    "is_native_language": is_native_lang,
                                    "variant_idx": variant,
                                    "model_id": model.id,
                                    "model_category": model.category,
                                    "replicate_idx": rep,
                                    "log_cc_token_share": np.log(APPROX_CC_TOKEN_SHARE[country.iso3]),
                                    "composite_accuracy": y,
                                    # True binary accuracy (T1-style) from same latent
                                    "factual_correct": int(y > 0.5),
                                })

    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    df = simulate_analytic_dataset(seed=42)
    out_dir = DATA_PROCESSED
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "analytic_synthetic.parquet"
    df.to_parquet(out_path, index=False)

    print(f"Simulated dataset: {len(df):,} rows")
    print(f"Saved to: {out_path}")
    print()
    print("Sanity check — mean composite accuracy by UNCTAD group:")
    print(df.groupby("unctad")["composite_accuracy"].agg(["mean", "std", "count"]))
    print()
    print("Sanity check — Sabiá-3 × Brazil vs others on Brazil:")
    br = df[df.country_iso3 == "BRA"]
    print(br.groupby("model_id")["composite_accuracy"].mean().sort_values(ascending=False))
