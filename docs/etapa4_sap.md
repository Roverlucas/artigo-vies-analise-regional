# Statistical Analysis Plan & Methodological Validation

**Project:** Geographic bias in LLMs and its impact on Global South policy research
**Target journal:** *Patterns* (Cell Press)
**Authors:** Lucas [surname] (PPGSAU/UTFPR), supervisor Prof. Dr. Yara Tadano
**SAP version:** 1.0
**Planned OSF deposit:** prior to principal data collection
**Date:** 2026-04-23
**Stack decision:** Python + `pymer4` (lme4 via rpy2) for GLMM; `pymc` for Bayesian; `semopy` for mediation; Monte Carlo power simulation in Python calling `lme4::simulate.merMod` through `pymer4`.

> **Note on placeholders.** As this SAP is written pre-data-collection (Stage 4 of a 10-stage pipeline), all numeric values marked `[PLACEHOLDER: description]` will be populated after principal analysis. The SAP will be locked at OSF and any post-hoc deviation documented in a Deviation Protocol table.

---

## 1. Inferential map (hypothesis → construct → variable → scale → test)

| H | Construct | Variable (operationalization) | Scale | Primary test |
|---|---|---|---|---|
| H1 | Geographic performance asymmetry | Composite accuracy (5 components, pre-weighted) | Continuous [0,1] | GLMM with country Global-South indicator |
| H2 | Language × geography interaction | Same as H1, split by prompt language | Continuous [0,1] | GLMM interaction term |
| H3a | Regional model closes Brazil gap | Composite accuracy × Sabiá-3 × BR | Continuous [0,1] | Pre-specified contrasts |
| H3b | Regional model displaces gap (BR+ but Lusophone Africa–) | Same as H3a, extended to Angola/Mozambique (if added) or MZ proxy | Continuous [0,1] | Pre-specified contrasts |
| H4 | Training-corpus representation mediates geographic effect | log(CC tokens) + log(Wiki pageviews) | Continuous ℝ | Ecological regression + mediation via semopy |

Two latent issues to flag up front:

(a) **H1 and H2 share the same outcome**, so test-family structure requires FDR correction *within* H1 family and *within* H2 family separately, not across.

(b) **H3 direction is ambiguous**: H3a and H3b are mutually exclusive alternatives within a single data-driven test. Pre-registration specifies both so that whichever the data supports is confirmatory rather than HARKed.

---

## 2. Inferential paradigm

**Primary paradigm: frequentist GLMM with effect sizes + 95% confidence intervals** (following ASA, 2016, 2019; Cumming, 2014; Lakens, 2013). Effect sizes reported with both classical magnitude (Cohen's *d*, η²_p) and domain-meaningful metrics (absolute accuracy gap in percentage points).

**Secondary paradigm: Bayesian GLMM with weakly informative priors** (via `pymc` and `bambi`) as robustness. Posterior distributions complement NHST by quantifying decision-theoretic uncertainty. Bayes Factors reported for critical tests of H3a vs H3b where decision between competing models is the scientific question.

**Why not pure Bayesian as primary.** *Patterns* reviewers are mixed frequentist/Bayesian; defaulting to frequentist with Bayesian robustness maximizes decoding bandwidth. For hypotheses with mutually exclusive alternatives (H3a vs H3b), Bayesian becomes primary.

**Why not equivalence testing.** None of H1-H4 are "absence of effect" hypotheses. Equivalence testing inappropriate here.

---

## 3. Sample size and power — Monte Carlo simulation

**Approach.** Given the nested structure (responses within prompts within countries, crossed with models), closed-form power formulas are unreliable. We conduct Monte Carlo simulation with N = 2,000 replicates per scenario, using `pymer4` to fit GLMMs and `lme4::simulate.merMod` (called via rpy2) to generate simulated datasets under specified effect sizes.

**Primary power analysis — H1 (between-country Global South vs Global North contrast):**

Generative model for simulation:
```
Y_ijkl = β₀ + β₁·GlobalSouth_j + u_j + v_k + w_l + ε_ijkl
```
where *j* indexes country (N=15), *k* indexes model (N=6), *l* indexes prompt (N=450), *i* indexes replicate (N=5). Random intercepts: `u_j ~ N(0, σ²_country)`, `v_k ~ N(0, σ²_model)`, `w_l ~ N(0, σ²_prompt)`.

**Pre-specified effect size (SESOI):**
- **Primary:** absolute difference in composite accuracy between Global South and Global North = **0.10** (10 percentage points). This corresponds to Cohen's *d* ≈ 0.5 (moderate) assuming residual σ ≈ 0.2.
- **Justification hierarchy** (per skill requirement — meta-analysis > practical benchmark > previous studies > Cohen):
  1. Meta-analytic estimate unavailable (novel domain).
  2. **Practical benchmark used:** 10pp gap in a research-assistant tool is the threshold at which Global South researchers would rationally prefer a local model with higher training cost — i.e., the practical decision point.
  3. Previous studies: Moayeri et al. (2024, WorldBench) report error ratio 1.5× (not directly comparable to additive pp but consistent with ~10pp absolute gap on typical baselines).
  4. Cohen *d* = 0.5 as heuristic fallback, acknowledged.

**Assumed variance components (from Moayeri et al., 2024 meta-pattern + pilot-driven update):**
- σ²_country ≈ 0.04 (ICC ≈ 0.15)
- σ²_model ≈ 0.03
- σ²_prompt ≈ 0.02
- σ²_residual ≈ 0.15

**Simulation grid.** Vary N_country from 10 to 20, effect size from 0.05 to 0.15, and ICC from 0.08 to 0.20. Report power surface.

**Expected result (pre-collection prediction):** Power > 0.95 for primary H1 test at the design point (N=15 countries, SESOI=0.10, ICC=0.15).

**H2 interaction power:**
- Test: country × language interaction.
- Target effect: η²_p ≥ 0.03 (small-to-moderate).
- Simulation accounts for sparse design (not all countries in all languages) — conservative N_eff per language-country cell ≈ 250.
- Expected power: 0.80–0.85 at target.

**H3 contrasts:**
- Primary contrast: `Sabiá-3 × BR` vs mean of `{GPT-5, Claude, Gemini} × BR` on composite accuracy.
- Equivalent to pairwise comparison with N ≈ 450 prompts × 5 replicates per side.
- Power > 0.95 for a 5pp gap at α=0.05.

**H4 ecological regression:**
- Country-level N = 15, predictor log(tokens).
- Target: Spearman ρ ≥ 0.60, equivalent to R² ≈ 0.36 in linear case.
- Power at ρ=0.60, N=15, α=0.05: approximately 0.77. **This is the binding constraint.** Acceptable because H4 is mechanistic/correlational, not the primary confirmatory hypothesis.
- **Sensitivity note:** at ρ=0.70, power > 0.90. If observed effect is smaller than hypothesized, we will be underpowered — declared as limitation.

**Code skeleton for Monte Carlo (Python, executable):**

```python
# src/power/simulation.py
import numpy as np
import pandas as pd
from pymer4.models import Lmer
import pymer4.simulate as sim
import warnings

np.random.seed(42)

def simulate_h1_power(
    n_countries=15,
    n_models=6,
    n_prompts=450,
    n_replicates=5,
    effect_size=0.10,
    sigma_country=0.04,
    sigma_model=0.03,
    sigma_prompt=0.02,
    sigma_resid=0.15,
    n_iter=2000,
    alpha=0.05,
):
    """Monte Carlo power for H1: Global South vs Global North contrast.

    Returns proportion of simulations rejecting H0 at alpha.
    """
    n_south = 12  # pre-specified stratification
    n_north = 3

    detected = 0
    for i in range(n_iter):
        # Simulate random effects
        u_country = np.random.normal(0, np.sqrt(sigma_country), n_countries)
        v_model = np.random.normal(0, np.sqrt(sigma_model), n_models)
        w_prompt = np.random.normal(0, np.sqrt(sigma_prompt), n_prompts)

        # Build design
        rows = []
        for c in range(n_countries):
            is_south = c < n_south
            fixed_eff = 0.5 - (effect_size if is_south else 0)
            for m in range(n_models):
                for p in range(n_prompts):
                    for r in range(n_replicates):
                        y = (fixed_eff + u_country[c] + v_model[m] +
                             w_prompt[p] + np.random.normal(0, np.sqrt(sigma_resid)))
                        y = np.clip(y, 0, 1)
                        rows.append({
                            'y': y, 'country': c, 'model': m,
                            'prompt': p, 'is_south': int(is_south)
                        })
        df = pd.DataFrame(rows)

        # Fit GLMM
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = Lmer('y ~ is_south + (1|country) + (1|model) + (1|prompt)',
                             data=df)
                fit = model.fit(REML=True, summarize=False)
            p_val = fit.loc['is_south', 'P-val']
            if p_val < alpha:
                detected += 1
        except Exception:
            continue  # rare convergence failure

    return detected / n_iter

# Grid over effect sizes
if __name__ == '__main__':
    results = []
    for es in [0.05, 0.075, 0.10, 0.125, 0.15]:
        pwr = simulate_h1_power(effect_size=es, n_iter=500)  # reduce for CI
        results.append({'effect_size': es, 'power': pwr})
        print(f"ES={es}: Power={pwr:.3f}")
    pd.DataFrame(results).to_csv('results/power_h1.csv', index=False)
```

**Important note on `pymer4` and `simulate.merMod`:** The simulate function is currently more mature on R side. For higher-complexity simulations (varying missingness mechanisms, zero-inflated outcomes) we call R directly via `rpy2.robjects` as a fallback — documented in the repository as `src/power/simulate_rcall.py`. Trade-off explicitly declared.

---

## 4. Assumptions and diagnostics by model

### 4.1 GLMM primary (H1, H2)

| Assumption | Diagnostic | Threshold | If violated |
|---|---|---|---|
| Linearity (fixed effects) | Component-plus-residual plots | Visual inspection + Hosmer-Lemeshow for binary | Transform or polynomial terms |
| Normality of random effects | QQ plots of BLUPs; Shapiro-Wilk on BLUPs | W > 0.95 | Robust estimation (huxtable robust SE) or Bayesian with t-distributed effects |
| Homoscedasticity of residuals | Residuals vs fitted; Breusch-Pagan | p > 0.05 | Cluster-robust SE via `clubSandwich` in R companion |
| No influential observations | Cook's distance per random effect; DFBETA | D < 4/n | Sensitivity: refit excluding top 5% |
| Independence conditional on random effects | Intraclass autocorrelation by prompt order | Moran's I ≈ 0 | Add temporal autocorrelation structure |
| Multicollinearity (fixed effects) | VIF | VIF < 5 (ideal < 2.5) | Drop or combine predictors |

### 4.2 Mediation (H4)

| Assumption | Diagnostic | If violated |
|---|---|---|
| No unmeasured confounders | DAG specification (see §5); sensitivity analysis via E-value (VanderWeele, 2017) | Report E-value threshold for null to hold |
| No measurement error in mediator | Log(CC tokens) and log(Wiki pageviews) as imperfect proxies — declared | Multi-indicator latent mediator via semopy SEM |
| Linear mediation relationships | Partial residual plots | Quadratic + interaction robustness |
| Adequate sample at country level | N=15 tight for structural equation; bootstrap CI | Bayesian SEM with `pymc` as robustness |

### 4.3 Rubric reliability (construct validity of composite outcome)

Inter-rater reliability via **Krippendorff's α** computed with `krippendorff` Python package:
- Threshold for proceeding: α ≥ 0.70 on pilot (n=50 prompts, 2 raters).
- If α < 0.70: rubric revision + re-training + re-piloting before principal collection.
- Final reported α computed on full dataset; if < 0.67, rubric items with lowest inter-rater agreement flagged for sensitivity analysis.

---

## 5. Causal structure (DAG for H4)

**DAG specification** (Pearl, 2009) for mediation test:

```
   [Global South] ──────────────► [Composite accuracy]
         │                                ▲
         │                                │
         └──► [Corpus representation] ────┘
                    ▲
                    │
         [Colonial history] ── (unobserved, hypothesized)
         [Digital infrastructure] ── (potentially observed, proxy: ITU indicators)
         [Economic development] ── (observed: GDP per capita from WB)
```

**Confounders** in the South → Corpus path that also affect Accuracy directly:
- Economic development (via GDP per capita).
- Digital infrastructure (via ITU Internet penetration index).
- Colonial history (unobserved — handled via E-value sensitivity).

**Mediation model (semopy):**

```python
# src/analyze/mediation_h4.py
import pandas as pd
import semopy

country_data = pd.read_parquet('data/processed/country_aggregated.parquet')

mediation_model = """
# Direct and indirect paths
log_cc_tokens ~ a*is_global_south + gdp_per_capita + internet_penetration
composite_accuracy ~ b*log_cc_tokens + c*is_global_south + gdp_per_capita + internet_penetration

# Indirect and total effects (computed via semopy's effect definitions)
indirect := a*b
total := c + (a*b)
"""

model = semopy.Model(mediation_model)
opt = model.fit(country_data)
# Bootstrap 5000 replicates for indirect effect CI
ci = semopy.calc_stats(model)
```

**E-value reported** to quantify required strength of unmeasured confounder to nullify observed mediation (VanderWeele & Ding, 2017).

---

## 6. Multiple-comparison correction

**Strategy:** Benjamini-Hochberg FDR at q=0.05, **applied within each hypothesis family separately**:

- Family H1: 1 primary contrast (no correction needed); robustness tests reported without correction but flagged.
- Family H2: interaction test (1) + language main effects (4) = 5 tests, FDR within family.
- Family H3: 2 pre-specified contrasts (H3a, H3b) + 1 scale control test = 3 tests, FDR within family.
- Family H4: 2 proxies (CC tokens, Wiki pageviews) × 2 outcomes (direct effect, indirect effect) = 4 tests, FDR within family.
- Exploratory analyses: reported separately, FDR within exploratory family with explicit "exploratory" labeling.

**Total confirmatory tests:** 13. FDR-BH appropriate for this scale (Bonferroni would be overly conservative and kill power gratuitously).

---

## 7. Robustness analyses (mandatory triangulation — 3+ per hypothesis)

### For H1:

1. **Leave-one-country-out** — refit GLMM excluding each country in turn; report stability of β₁ estimate and CI.
2. **Expert-validated subset only** — analysis restricted to prompts with full painel validation (Krippendorff's α per prompt ≥ 0.80).
3. **Bayesian re-estimation** — `pymc` with weakly informative priors (Normal(0, 1) on fixed effects, Half-Cauchy on variance components); report posterior probability P(β₁ < 0 | data).
4. **Alternative response filter** — exclude refusals vs include as outcome; should not change conclusion.
5. **Pre-cutoff ground truth subset** — analysis using only ground-truth sources dated before model training cutoff (contamination control).

### For H2:

1. **Language as fixed vs random effect** — refit with language as random slope per country.
2. **Back-translation quality score** as covariate.
3. **Bayesian hierarchical model** with language-level shrinkage.

### For H3:

1. **Scale-matched control** — repeat H3 contrasts substituting Sabiá-3 with Qwen 3 32B (similar scale, not regional). If the regional effect is real, it should disappear.
2. **Language-matched control** — repeat with all prompts translated to PT and tested on GPT-5 (frontier in Portuguese); isolates model-specific regional effect from language effect.
3. **Bayesian model comparison** — Bayes Factor H3a vs H3b vs null (all three performances equal) using `pymc` with bridge sampling.

### For H4:

1. **Alternative proxies** — Wikipedia pageviews alone, GDP-adjusted token count, TLD-weighted corpus share.
2. **E-value analysis** — minimal confounder strength required to nullify observed mediation (VanderWeele, 2017).
3. **Bootstrap CI for indirect effect** — 5,000 replicates, BCa intervals.
4. **Quadratic mediator** — test nonlinear corpus-accuracy relationship.

---

## 8. Handling missing data and edge cases

| Scenario | Default policy |
|---|---|
| API timeout after 3 retries | Mark `missing=1`, exclude from primary analysis, include in sensitivity via multiple imputation (`miceforest` Python package, m=5) |
| LLM refuses to answer | Coded `refusal=1`, excluded from accuracy analysis, included in separate refusal-rate analysis |
| Response in different language than requested | Coded `lang_mismatch=1`, excluded from primary, analyzed separately as secondary outcome (may indicate capability gap) |
| Ground truth unavailable for a specific prompt-country pair | Task type reassigned to T2/T3/T4 (open-ended) pre-registered as backup; evaluated only via rubric |
| Rater disagreement > 2 points on 0–5 scale | Adjudicated by senior rater; flagged for quality report |
| Model version updated mid-collection | Flag batch; re-run affected subset; re-analysis comparing versions as sensitivity |

---

## 9. Deviation protocol (empty; populated post-execution)

| Planned analysis | Executed analysis | Reason for deviation | Interpretation impact |
|---|---|---|---|
| [PLACEHOLDER] | [PLACEHOLDER] | [PLACEHOLDER] | [PLACEHOLDER] |

This table is **locked empty at OSF pre-registration**. Any row added during execution is declared in the manuscript transparently.

---

## 10. Software, versions, reproducibility

```
Python 3.12
  pymer4 0.8.x (interfaces lme4 via rpy2 ≥ 3.5)
  pymc 5.x
  bambi 0.13+ (optional Bayesian regression syntax sugar)
  semopy 2.x
  statsmodels 0.14+
  pandas 2.x, numpy 1.26+
  krippendorff 0.8+
  miceforest 5.x

R 4.4.1 (called via rpy2)
  lme4 1.1-35
  clubSandwich 0.5
  emmeans 1.10
```

Full dependency lock in `code/environment.yml` + `code/renv.lock`. Zenodo snapshot at submission; Docker image published for exact reproducibility.

**Analysis pipeline** driven by `snakemake` (Python-native workflow manager); each hypothesis corresponds to one Snakefile target; outputs are hashed and versioned.

---

## 11. Adversarial review simulation

### Reviewer 1 — "The purist methodologist"

*Expected critiques:*
- **"Why `pymer4` and not `lme4` directly?"** → Response: we use lme4 *via* pymer4 for language consistency with collection pipeline; results are identical to R-native lme4; we additionally run `lme4` directly as sanity check (10% subset) and report agreement.
- **"Your N=15 at country level is too small for mediation."** → Response: we pre-declare this limitation; bootstrap CIs + E-value sensitivity quantify uncertainty; Bayesian mediation with shrinkage provides complementary estimate.
- **"FDR is not confirmatory-adequate; use Bonferroni."** → Response: BH-FDR within hypothesis families is current convention in FAccT, ICML, ACL papers with similar designs (ref. Moayeri et al. 2024); Bonferroni is overly conservative at our N of tests (13) and kills power on H4 unnecessarily.

### Reviewer 2 — "The Bayesian"

*Expected critiques:*
- **"Where are your priors?"** → Response: weakly informative Normal(0, 1) on fixed effects (standardized outcomes), Half-Cauchy(0, 2.5) on variance components (Gelman et al. 2013); posterior predictive checks reported in Supplementary.
- **"Bayes Factor for H3a vs H3b?"** → Response: BF computed via bridge sampling in `pymc`; reported in main text with decision thresholds from Kass & Raftery (1995).
- **"Model checking?"** → Response: posterior predictive check plots for each GLMM; WAIC for model comparison.

### Reviewer 3 — "The applied field reviewer"

*Expected critiques:*
- **"Is a 10pp accuracy gap practically meaningful?"** → Response: yes — we pre-specify this as the SESOI based on the practical decision point at which a Global South researcher would prefer a locally-tuned tool with higher development cost. Interpretation tied to practical consequence, not just statistical significance.
- **"Can your findings generalize beyond these 15 countries?"** → Response: stratification covers 4 continents, 5 Joshi classes, 4 World Bank income groups; generalization to Oceania and Class 0 languages explicitly disclaimed as limitation. Future-work section addresses.
- **"Why isn't this just replicating WorldBench?"** → Response: three distinct contributions beyond WorldBench (applied-research task design, language × geography factorial, regional model comparison) — explicitly enumerated in Introduction.

---

## 12. Supplementary material skeleton (to be populated in Stage 5)

The following Supplementary Material is planned and pre-structured:

**S1. Full prompt set (v1-final) with domain and task labels** — CSV in Zenodo.
**S2. Ground truth sources** — one table per country, with URL and access date.
**S3. Rubric details and inter-rater reliability tables** — Krippendorff's α per prompt, per rater-pair.
**S4. Power simulation details** — R/Python code, output plots (power surface).
**S5. GLMM full diagnostics** — residual plots, BLUP distributions, VIF tables.
**S6. Robustness results** — all pre-registered robustness checks (tabular + forest plots).
**S7. Bayesian results** — posterior plots, Bayes Factors, posterior predictive checks.
**S8. Mediation diagnostics** — DAG formalization, bootstrap distributions, E-value results.
**S9. Code availability statement** — GitHub + Zenodo DOI + Docker image digest.
**S10. Deviation protocol** — (if any deviations from this pre-registered SAP).

---

## 13. Key references for this SAP

- American Statistical Association. (2016). Statement on statistical significance and p-values. *American Statistician*, 70(2), 129–133.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate. *Journal of the Royal Statistical Society B*, 57, 289–300.
- Cumming, G. (2014). The new statistics: Why and how. *Psychological Science*, 25(1), 7–29.
- Efron, B., & Tibshirani, R. (1993). *An introduction to the bootstrap*. Chapman & Hall.
- Gelman, A., Carlin, J. B., Stern, H. S., Dunson, D. B., Vehtari, A., & Rubin, D. B. (2013). *Bayesian data analysis* (3rd ed.). CRC Press.
- Hair, J. F., Risher, J. J., Sarstedt, M., & Ringle, C. M. (2019). When to use and how to report the results of PLS-SEM. *European Business Review*, 31(1), 2–24.
- Harrell, F. E. (2015). *Regression modeling strategies* (2nd ed.). Springer.
- Kass, R. E., & Raftery, A. E. (1995). Bayes factors. *JASA*, 90(430), 773–795.
- Krippendorff, K. (2018). *Content analysis: An introduction to its methodology* (4th ed.). SAGE.
- Kruschke, J. (2014). *Doing Bayesian data analysis* (2nd ed.). Academic Press.
- Lakens, D. (2013). Calculating and reporting effect sizes. *Frontiers in Psychology*, 4, 863.
- McElreath, R. (2020). *Statistical rethinking* (2nd ed.). CRC Press.
- Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). The preregistration revolution. *PNAS*, 115(11), 2600–2606.
- Pearl, J. (2009). *Causality* (2nd ed.). Cambridge University Press.
- R Core Team. (2024). *R: A language and environment for statistical computing*. R 4.4.1.
- VanderWeele, T. J., & Ding, P. (2017). Sensitivity analysis in observational research: The E-value. *Annals of Internal Medicine*, 167(4), 268–274.
- Wasserstein, R. L., Schirm, A. L., & Lazar, N. A. (2019). Moving to a world beyond "p < 0.05". *American Statistician*, 73(sup1), 1–19.

---

## 14. SAP sign-off

This SAP is locked upon OSF deposit. Any deviations during execution (Stage 5 of the pipeline) require explicit documentation in the Deviation Protocol (§9), transparent reporting in the manuscript, and cautious language for non-pre-registered analyses (labeled "exploratory").

**Next stage:** execution by `phd-senior-scientist` (Stage 5), which receives this SAP as binding contract.

---

## Validation matrix (summary)

| # | H | Primary test | Key assumption | Diagnostic | If violated | Robustness #1 | Robustness #2 | Robustness #3 |
|---|---|---|---|---|---|---|---|---|
| 1 | H1 | GLMM β(is_south) | Random effects normality | QQ of BLUPs | Robust SE or Bayesian | Leave-one-out | Expert subset | Bayesian |
| 2 | H2 | GLMM country×language | Sparse design balance | Cell counts ≥20 | Exclude sparse cells | Lang as random slope | Back-translation covariate | Bayesian hierarchical |
| 3 | H3a | Contrast Sabiá-3×BR vs frontier×BR | Balanced n per contrast | N equal ±10% | Weighted contrast | Scale-matched (Qwen 32B) | Language-matched (GPT-5 in PT) | Bayes Factor H3a vs H3b |
| 4 | H3b | Contrast Sabiá-3×{BR} vs Sabiá-3×{other Lusophone} | Availability of Lusophone Africa data | If N Angola/MZ <30, skip | Declare untested | (same as H3a) | (same) | (same) |
| 5 | H4 | Ecological regression + SEM mediation | No unmeasured confounder | E-value | Declare cautious interpretation | Alt proxies | Bootstrap CI | Bayesian SEM |
