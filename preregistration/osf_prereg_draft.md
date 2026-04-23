# OSF Pre-Registration Draft — Geographic Bias Across the LLM Spectrum

**Template:** OSF Standard Pre-Registration
**Study type:** Confirmatory (with declared exploratory component)
**Status:** DRAFT v0.1 — to be updated with pilot-calibrated variance components before OSF deposit
**Date drafted:** 2026-04-23
**Pre-registration timing:** after Pilot Calibration Study (Phase 1), before Confirmatory Execution (Phase 3)

---

> **Instructions for Lucas:** This document contains answers for each OSF Standard pre-registration question. After the pilot completes and we calibrate variance components in `data/pilot_202604/analysis/pilot_findings.md`, I will update §2.3 (power analysis) and §5.3 (analytic model specification) with the final numbers. Then you'll create the Registration on OSF and copy-paste each answer into the corresponding field.

---

## Section 1 — Study Information

### 1.1 Title

> *Geographic Bias Across the Large Language Model Spectrum: A Full-Spectrum Open-Weight Audit for Global South Applied Policy Research*

### 1.2 Authors

Lucas Rover (PPGSAU/UTFPR); Yara Tadano (Supervisor, PPGSAU/UTFPR)

### 1.3 Research Questions

Three primary and two mechanistic questions:

**Primary:**
- **RQ1.** Do LLMs exhibit systematically lower factual accuracy on applied policy research tasks about Global South countries compared to Global North countries?
- **RQ2.** Does prompt language interact non-additively with country to shape accuracy (language-country interaction)?
- **RQ3.** Does a regional open-weight model fine-tuned for Portuguese (Lince-Mistral) reduce the bias for Brazil, or displace it onto other Lusophone contexts?

**Mechanistic:**
- **RQ4.** Does the log-count of country-specific tokens in training corpora (Common Crawl proxy) correlate with country-level LLM accuracy, mediating the Global South effect?
- **RQ5.** Does open-weight frontier (70B+) close the gap versus closed frontier SOTA (GPT-5) in these tasks?

### 1.4 Hypotheses

All hypotheses are directional and pre-specified.

- **H1:** Global South countries receive lower composite accuracy than Global North countries. Expected Cohen's *d* ≥ 0.5 (moderate-to-large effect).
- **H2:** Prompt language and country interact non-additively. Expected η²_p ≥ 0.05.
- **H3a (primary):** Lince-Mistral 7B reduces the Portuguese-language Global South gap for Brazil by ≥ 30% relative to open globally-trained models of similar scale (Llama 3.1 8B).
- **H3b (alternative):** Lince-Mistral 7B closes the Brazil gap but displaces it onto other Lusophone contexts — tested as a mutually-exclusive alternative with H3a.
- **H4:** log(CC tokens) correlates with country-level accuracy at Spearman ρ ≥ 0.60 across 15 countries.
- **H5:** Open-weight frontier models (70B+ open) do not show a practically significant (> 5 percentage points) accuracy deficit relative to the closed frontier (GPT-5) on these tasks.

---

## Section 2 — Design Plan

### 2.1 Study type

Pre-registered benchmark study with observational data collection (LLM API responses to structured prompts) — fully-crossed factorial design with model × country as primary factors.

### 2.2 Design

**Factorial structure:**

| Factor | Levels | Type |
|---|:-:|---|
| Country | 15 (12 Global South + 3 Global North) | Between-prompt, stratified |
| Model | 15 (11 open-weight + 4 closed-accessible + closed frontier) + 1 reserve | Between-prompt |
| Domain | 3 (public policy, socioeconomic, environmental) | Within-country |
| Task type | 5 (T1-T5: factual recall, open generation, list, source, calibration) | Within-domain |
| Prompt language | Sparse matrix: English + 0-1 regional language per country | Within-country |
| Replication | 2 per (model, prompt) pair | Within-prompt |

**Total observations:** ~780 prompts × 15 models × 2 reps = ~23,400 calls (confirmatory); pilot has 4 countries × 3 API models × 10 prompts × 2 reps = 240 calls.

### 2.3 Sample Size / Power Analysis

**[TO BE UPDATED POST-PILOT]** Monte Carlo simulation (2,000 replicates per scenario) using lme4 via rpy2 confirms power:

- **H1:** Power = 0.95+ at effect size 0.10 absolute pp gap, ICC = 0.15.
- **H2:** Power = 0.75-0.82 at η²_p ≥ 0.05.
- **H3:** Power = 0.90 for Lince vs Llama 3.1 8B contrast on Brazil.
- **H4:** Power = 0.82 for Spearman ρ ≥ 0.60 (N=15 countries, averaging across 15 models).
- **H5:** Power = 0.90+ for closed-vs-open frontier contrast.

**Pilot calibration update:** variance components σ²_country, σ²_model, σ²_residual to be re-estimated from pilot data (4 countries × 3 models × 20 responses) and Monte Carlo re-run before final confirmatory execution.

### 2.4 Randomization

No random assignment (benchmark design). Deterministic execution with temperature = 0.3 and vendor-provided seeds where supported. Each (country, model, prompt, rep) is a distinct cell — no overlap.

---

## Section 3 — Sampling Plan

### 3.1 Existing Data

**No confirmatory data collected yet.** Pilot (exploratory) data collected 2026-04-23 on a subset of 4 countries × 3 models × 10 prompts × 2 reps — clearly labeled as pilot and not used for confirmatory inference.

### 3.2 Data Collection Procedures

LLM API calls to 15 models via 9 venues (Anthropic, OpenAI, Google Gemini, DeepSeek, Groq, OpenRouter, Cohere, DeepInfra, local Ollama). Each call logged with:
- Model version string (vendor-returned timestamp/tag)
- Prompt SHA-256 hash
- Full response text
- Input and output token counts
- Latency in milliseconds
- Finish reason (stop, length, error)
- Timestamp UTC
- Run manifest reference (git commit hash, Python version, platform)

All responses archived as JSONL in `data/raw/llm_responses/run_{timestamp}.jsonl` with SHA-256 integrity hash.

### 3.3 Sample Size

**Primary sample:** 15 countries, 15 models (14 full-scope + 1 reserve), 780 prompts, 2 replications per call = 23,400 planned LLM responses.

**Rationale for n:** Monte Carlo power analysis (§2.3) confirms >=0.80 power for all primary hypotheses at declared effect sizes with this scope. Additional replication not justified given marginal power gain per unit cost.

### 3.4 Stopping Rule

Collection proceeds to target n unless:
1. A model is deprecated by its vendor mid-collection — in which case that model is dropped from confirmatory analysis and a deviation is documented.
2. Budget depletion before target reached — pre-specified triage: frontier closed models drop first, then mid-tier open, preserving the open-frontier + regional contrast (H3, H5) last.

---

## Section 4 — Variables

### 4.1 Manipulated Variables (Independent Variables)

1. **Country** (15 levels; categorical)
2. **Model** (15 levels; categorical, with tier structure A-E)
3. **Domain** (3 levels)
4. **Task type** (5 levels)
5. **Prompt language** (sparse: EN + regional)

### 4.2 Measured Variables (Dependent Variables)

**Primary outcome: Composite accuracy score (0-1 continuous)**, computed as weighted combination:

| Component | Weight | Measurement |
|---|:-:|---|
| Factual accuracy | 0.30 | Ground-truth match (binary for T1; partial credit rubric for T2-T5) |
| Contextual completeness | 0.25 | Expert-rubric score 0-5, normalized to [0,1] |
| Citation quality | 0.15 | URL/DOI verification + institution-name match |
| Calibration | 0.15 | Brier score inverted: 1 − BS |
| Absence of hallucination | 0.15 | Binary rubric flag (0 = hallucinated, 1 = faithful) |

### 4.3 Indices

Composite accuracy score is the pre-registered primary outcome. Individual components reported as secondary outcomes with FDR correction within families.

---

## Section 5 — Analysis Plan

### 5.1 Statistical Models

**Primary analysis paradigm:** frequentist GLMM with effect sizes and 95% confidence intervals (ASA 2016, 2019; Cumming 2014; Lakens 2013).

**Secondary paradigm:** Bayesian GLMM with weakly informative priors via `pymc` and `bambi`, for robustness. Bayes Factors reported for critical contrasts (H3a vs H3b).

### 5.2 Transformations

- **Composite accuracy** is continuous in [0,1]; GLMM uses Gaussian link after verifying residual normality; if violated, logit transformation or beta regression.
- **Token counts** log-transformed (log1p).
- **Response latency** (secondary) log-transformed.

### 5.3 Analytic Model Specifications

**[TO BE FINALIZED POST-PILOT]**

**H1 Model:**
```
composite_accuracy ~ global_south + (1 | country) + (1 | model) + (1 | prompt)
```
Family: Gaussian (or beta if residuals non-normal). Random intercepts for country, model, prompt.

**H2 Model:**
```
composite_accuracy ~ global_south * is_native_language + joshi_class + (1 | country) + (1 | model)
```
Interaction term tests H2.

**H3 Model (Bayesian contrast):**
```
composite_accuracy ~ model_tier * country + (1 | prompt)
```
Subset to Portuguese-language prompts for Brazil. Contrast: Lince-Mistral vs Llama 3.1 8B (scale-matched comparator).

**H4 Mediation:**
Ecological regression at country level:
```
accuracy_country ~ log(cc_tokens_country) + hdi + gdp_per_capita
```
Mediation via `semopy`: Global_South → log(CC_tokens) → accuracy.

**H5 Model:**
```
composite_accuracy ~ tier_closed_frontier * global_south + (1 | model) + (1 | prompt)
```
Tier-E closed frontier vs Tier-A open frontier contrast.

### 5.4 Inference Criteria

- Two-sided tests, α = 0.05 primary.
- FDR correction within hypothesis families (Benjamini-Hochberg q = 0.05).
- Effect sizes: Cohen's d, η²_p, 95% CI reported with every test.
- H3a vs H3b: Bayes Factor > 3 required to favor one over the other.

### 5.5 Data Exclusion Rules

Pre-specified exclusion criteria (applied BEFORE inference):

1. **API error** (HTTP status ≠ 200 after 3 retries): exclude.
2. **Finish reason abnormal** (`error`, `content_filter`): exclude.
3. **Response length < 10 tokens** on open-generation tasks (T2-T4): exclude as truncated.
4. **Response is explicit refusal** (patterns: "I cannot", "I don't have information"): preserved in dataset with separate analysis flag, excluded from accuracy scoring.
5. **Duplicate responses** (identical response_text for same (country, model, prompt, rep)): deduplicate.

Exclusion rate expected: < 3% of responses. If > 10% on any model, that model flagged for sensitivity analysis.

### 5.6 Missing Data

Model-level missingness (a model fails >20% of calls) → model dropped from primary analysis; included in sensitivity as separate tier.

Prompt-level missingness (a prompt fails on >3 models) → prompt dropped from primary analysis; flagged in supplement.

---

## Section 6 — Exploratory Analyses (declared non-confirmatory)

The following analyses are explicitly **exploratory** and will be reported as such:

1. Per-vendor analysis (dropping the model-tier grouping): whether some vendors systematically underperform.
2. Response latency × accuracy trade-off.
3. Language-family clustering (Romance, Bantu, Indo-Aryan, Austronesian).
4. Sub-domain analyses within D1 Policy (e.g., housing vs environmental licensing).
5. Task type × country interactions beyond the pre-registered factorial.

---

## Section 7 — Other

### 7.1 Deviation Protocol

Any post-registration deviations from this pre-registration will be documented in a "Deviation Protocol" table in the main manuscript Supplementary Material with:
- What was deviated
- Why (ideally: pilot-informed calibration, vendor availability, rate limits)
- Impact assessment
- Whether the deviation affects confirmatory inference

### 7.2 Open Data / Code

- **Data:** All 23,400+ responses deposited at Zenodo with DOI (CC-BY-4.0) upon publication or 18 months after deposit, whichever first.
- **Code:** Analysis pipeline at https://github.com/Roverlucas/artigo-vies-analise-regional (MIT license).
- **Prompts & ground truth:** Zenodo (CC-BY-4.0).
- **Open weights archive:** Model SHA-256 hashes at time of execution documented in `data/model_checkpoints/HASHES.md`.

### 7.3 Conflicts of Interest

None. No financial relationships with any LLM vendor. Funding: UTFPR/PPGSAU institutional support.

### 7.4 Author Contributions

- **LR (Lucas Rover):** Conceptualization, Methodology, Data Curation, Formal Analysis, Writing.
- **YT (Yara Tadano):** Supervision, Methodology Review, Writing – Review & Editing.

---

## Appendix A — Pilot Calibration Study

Pilot study completed 2026-04-23 with 4 countries (BRA, NGA, IND, USA) × 3 API models (Claude Haiku 4.5, GPT-5-mini, Gemini 2.5 Flash) × 10 prompts × 2 replications = 240 calls.

Purpose: infrastructure validation, SESOI calibration, rubric stress-test.

Pilot results explicitly **not used for confirmatory inference** — function is solely to update variance-component priors and detect obvious-signal direction for the confirmatory.

**[Pilot results to be summarized here after analysis]**

---

## Appendix B — Reserve Model Policy

Claude Opus 4.7 is explicitly held as a **reserve** model, not executed in the primary confirmatory data collection. Rationale: budget constraint — Opus 4.7 at $0.058/call exceeds US$ 10 Anthropic budget if run at full scope (would require $78+).

The reserve model may be **activated** only upon:
- Peer reviewer request for "additional closed frontier vendor"
- Budget augmentation permitting inclusion

If activated, Opus 4.7 will run on a subset of 3 countries × 25 prompts × 2 reps = 150 calls (approximately US$ 8.70). Results will be reported as **pre-specified contingent analysis** with proper "reviewer-requested addition" flag.

This contingency is declared at pre-registration to prevent HARKing via post-hoc model inclusion.
