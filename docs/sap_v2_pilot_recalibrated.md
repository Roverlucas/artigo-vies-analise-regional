# Statistical Analysis Plan v2 — Pilot-Recalibrated

**Project:** The Open-Weight Penalty: Frontier Open Models Underperform Closed-Accessible Models in Global South Applied Research
**Target journal:** *Patterns* (Cell Press)
**Authors:** Lucas Rover (PPGSAU/UTFPR), supervisor Prof. Dr. Yara Tadano
**SAP version:** 2.0 (recalibrated post-Pilot 2.0)
**OSF deposit timing:** prior to confirmatory data collection
**Date:** 2026-04-25
**Supersedes:** `etapa4_sap.md` (v1.0)

> **What changed in v2:**
> 1. H5 elevated from secondary to **co-primary** (with H1) following pilot 2.0 surprise finding
> 2. SESOI for H1 reduced from 0.10 → **0.05** (matches pilot Cohen's d = 0.34)
> 3. Variance components recalibrated from pilot data:
>    - σ²_country: 0.04 → **0.001** (ICC 0.15 → 0.031)
>    - σ²_model: 0.03 → **0.005** (ICC 0.03 → 0.128)
>    - σ²_residual: 0.15 → **0.028**
> 4. Confirmatory scope adjusted: 25 prompts × 2 reps × 14 models × 15 countries = 10,500 calls
> 5. LLM-as-judge protocol locked: Haiku 4.5 on 100% + Opus 4.7 on 200-row IRR subset

---

## 1. Inferential map (hypothesis → construct → variable → scale → test)

| H | Status | Construct | Variable (operationalization) | Primary test |
|---|---|---|---|---|
| **H1** | **Co-primary** | Geographic accuracy asymmetry | Composite accuracy (judge-scored) | GLMM with `global_south` indicator |
| **H5** | **Co-primary** ⬆ | Open-weight penalty | Composite × tier_open vs tier_closed | GLMM with `tier × global_south` interaction; TOST equivalence |
| H3 | Secondary | Regional model effect | Composite × Lince-Mistral × BR | Bayesian contrast |
| H4 | Secondary | Mechanism (corpus tokens) | log(CC tokens) per country | Spearman + mediation |
| H2 | Tertiary | Language interaction | Composite × language × country | GLMM interaction term |

---

## 2. Inferential paradigm (unchanged from v1)

Primary: frequentist GLMM with effect sizes + 95% CIs (Cumming 2014; Lakens 2013).
Secondary: Bayesian GLMM with weakly informative priors via `bambi` (Bürkner 2017).
H5 specifically uses **TOST equivalence** test (Lakens 2017) at SESOI = ±5 percentage points.

---

## 3. Sample size and power — recalibrated

### 3.1 Variance components from pilot 2.0 (n=700)

| Component | v1 assumption | **v2 from pilot** |
|---|:-:|:-:|
| σ²_country | 0.04 | **0.001** |
| σ²_model | 0.03 | **0.005** |
| σ²_residual | 0.15 | **0.028** |
| ICC_country | 0.15 | **0.031** |
| ICC_model | 0.03 | **0.128** |

**Implication:** between-country variance is much smaller than v1 assumed; between-model variance is much larger. Power for H1 is reduced; power for H5 is increased.

### 3.2 Power analysis for H1 (recalibrated, country contrast)

```python
# Recalibrated Monte Carlo power, v2 priors
sigma_country = 0.001
sigma_model = 0.005
sigma_resid = 0.028
SESOI = 0.05  # 5pp, recalibrated from pilot 2.0 Cohen's d = 0.34

# At confirmatory scope: 15 countries × 14 models × 25 prompts × 2 reps = 10,500 obs
# Expected power (analytic estimate): ~0.78 at SESOI = 0.05
# Acceptable; documented as borderline.
```

**Power curve (analytic, recalibrated):**

| SESOI (pp) | Expected power |
|---|:-:|
| 0.10 | > 0.99 |
| 0.07 | 0.92 |
| **0.05** | **0.78** |
| 0.03 | 0.55 |

H1 power = 0.78 at SESOI = 0.05 is borderline. We document this as a limitation; the rich H5 contribution mitigates dependence on H1 alone.

### 3.3 Power analysis for H5 (open vs closed equivalence)

```python
# Pilot 2.0 observed gap: 12.5 pp (open Tier A vs closed accessible)
# SESOI for equivalence: 5 pp
# Confirmatory: 5 open Tier A models × 3 closed accessible × 15 countries × 25 × 2

# Power for TOST rejecting equivalence at SESOI = 5pp, observed gap = 12.5pp:
# Expected power: > 0.99
```

**H5 is the most well-powered hypothesis in the design.** The 12.5pp pilot gap is 2.5× the SESOI; even with downward correction, this should reject equivalence at >99% power.

### 3.4 Power analysis for H3 (Lince-Mistral on BR)

```python
# Lince-Mistral 7B: BR-only test
# Comparator: Llama 3.1 8B (scale-matched open) on BR
# Subset: BR × 25 prompts × 2 reps × 2 models = 100 obs Lince + 100 Llama 3.1
# Expected power: 0.90 for 30% gap reduction
```

### 3.5 Power for H4 (token mediation)

```python
# Country-level: N = 15 with Spearman ρ ≥ 0.60
# Power: 0.82 (no change from v1 — sample size unchanged)
```

### 3.6 Power for H2 (language interaction)

Reduced from v1 due to lower n_reps. Expected power: 0.65-0.75. **Documented as exploratory** in revised SAP.

---

## 4. Analytic models (specifications)

### 4.1 H1 model (frequentist primary)

```r
# R syntax via pymer4 / lme4
composite ~ global_south + (1 | country) + (1 | model) + (1 | prompt)
```

Family: Gaussian on logit-transformed composite (since composite ∈ [0,1]).

### 4.2 H5 model (frequentist primary, TOST equivalence)

```r
# Compare open Tier A vs closed accessible (Tiers D)
composite ~ tier * global_south + (1 | country) + (1 | model) + (1 | prompt)
# Subset to relevant tiers; full vs reduced model comparison
```

TOST: H0_low = (closed - open) ≤ -SESOI, H0_high = (closed - open) ≥ SESOI; reject both for equivalence.

### 4.3 H3 model (Bayesian contrast)

```r
# Subset: country == "BRA", language %in% c("en", "pt")
# Models: Lince-Mistral, Llama 3.1 8B (comparator)
composite ~ model_id + language + (1 | prompt)
```

Bayes Factor for Lince > Llama-3.1-8B in PT subset.

### 4.4 H4 model (ecological + mediation)

```r
# Country-level aggregation
country_accuracy = mean of all responses for that country (across 14 models)
country_accuracy ~ log(cc_tokens) + log(wiki_pageviews) + gdp_per_capita + hdi
```

Mediation via `semopy`:
- `global_south → log(cc_tokens) → country_accuracy`
- Test: indirect effect significant via bootstrap CI

### 4.5 H2 model (exploratory)

```r
composite ~ global_south * is_native_language + joshi_class + (1 | country) + (1 | model)
```

Documented as exploratory due to power constraints in v2.

---

## 5. Outlier handling and exclusion (pre-registered)

(Unchanged from v1 §5)

1. API errors (HTTP non-200 after 3 retries): exclude
2. Empty responses (< 10 chars): exclude
3. Truncated responses (finish_reason=length, content < 50 chars): exclude with documentation
4. Refusals (explicit "I cannot answer"): kept with separate flag, excluded from accuracy scoring
5. Judge errors (parse failures): excluded from analysis

If exclusion rate > 5% on any model, sensitivity analysis reported.

---

## 6. Multiple comparisons

FDR Benjamini-Hochberg q = 0.05 within each hypothesis family:
- H1 family: country effect, country × tier interaction
- H5 family: tier comparison, tier × country interaction, equivalence tests per pair
- H3 family: Lince contrasts (a vs b)
- H4 family: token correlation, mediation indirect/total

---

## 7. Inter-rater reliability (judge calibration)

200-response stratified subset (5 strata × 40 each by model-tier):
- Both Haiku 4.5 and Opus 4.7 score independently
- Krippendorff α target ≥ 0.70 for ordinal composite
- If α < 0.70: Opus replaces Haiku as primary judge for affected subset; full Opus rerun if needed

---

## 8. Sensitivity analyses (pre-specified)

1. **Leave-one-out by country** (drop 1 of 15, refit, compare)
2. **Leave-one-out by model** (drop 1 of 14)
3. **Frequentist vs Bayesian** GLMM convergence
4. **Bootstrap CIs** (1000 resamples, country-stratified)
5. **Subset analysis**: only T1 + T5 (objective tasks) for cleaner H1 effect

---

## 9. Open data / code commitments

- Confirmatory raw responses (~10,500): Zenodo CC-BY-4.0 + DOI
- Judge scores: Zenodo CC-BY-4.0
- Analysis code: GitHub MIT
- Pre-registration: OSF with DOI cited in paper
- All within 60 days of submission acceptance OR 180 days of pre-registration date, whichever earlier

---

## 10. Deviation protocol

Pilot 2.0 already triggered v1 → v2 deviation. Documented in `INCIDENT_REPORT_GPT5_EMPTY_RESPONSES.md` and this SAP v2.

Any further deviations during confirmatory will be:
1. Logged in OSF Project comments (timestamp + hash)
2. Reported in main manuscript Supplementary S5
3. Classified as: pre-specified contingent / pilot-revealed / vendor-issue / other
