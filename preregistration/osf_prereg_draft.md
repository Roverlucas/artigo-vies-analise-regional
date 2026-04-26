# OSF Pre-Registration — Geographic and Tier-Related Performance Gaps in Large Language Models for Global South Applied Policy Research

**Template:** OSF Standard Pre-Registration
**Study type:** Pre-registered confirmatory benchmark study with declared exploratory components
**Pre-registration timing:** prior to confirmatory data collection
**Estimated execution window:** 2026-Q2 / Q3

---

## Section 1 — Study Information

### 1.1 Title

> *Geographic and Tier-Related Performance Gaps in Large Language Models for Global South Applied Policy Research: A 15-Country Pre-Registered Audit With Mechanism Analysis*

**Short title:** *Geographic Bias and Tier Gaps in LLMs for Global South Policy Research*

### 1.2 Authors

1. **Lucas Rover** — Federal University of Technology — Paraná (UTFPR), Brazil — `lucasrover@alunos.utfpr.edu.br` — *corresponding author*
2. **Dr. Eduardo Tadeu Bacalhau** — Federal University of Paraná (UFPR), Brazil — `bacalhau@ufpr.br`
3. **Dra. Yara de Souza Tadano** — Federal University of Technology — Paraná (UTFPR), Brazil — `yaratadano@utfpr.edu.br`

### 1.3 Research Questions

**Confirmatory primary:**
- **RQ1.** Across a continuous gradient of country-level digital and developmental conditions (Joshi linguistic-resource class; HDI; Common Crawl + Wikipedia representation), do Large Language Models exhibit systematically lower factual accuracy on applied policy research tasks?
- **RQ2.** Does country-level training-corpus representation (Wikipedia article counts as primary proxy; Common Crawl tokens as secondary, with three operationalizations) account for the country-level accuracy gradient, after controlling for HDI and GDP per capita?

**Confirmatory secondary:**
- **RQ3.** Does a regional Brazilian-Portuguese-instruction-tuned open-weight model (Cabra-Mistral 7B v3) reduce the Portuguese-language accuracy gap for Brazil relative to a scale-matched globally-trained open model (Llama 3.1 8B), or displace the gap onto other Lusophone contexts where comparable data are available?

**Declared exploratory:**
- **RQ4.** Does the open-weight vs closed-accessible tier distinction predict accuracy on Global South applied research tasks, after stratifying by model scale and data-cutoff?
- **RQ5.** Do prompt language and country-level conditions interact non-additively?

### 1.4 Hypotheses

All hypotheses are directional and pre-specified. **H1 and H4 are co-primary confirmatory.** H3 is secondary confirmatory. H2 and H5 are explicitly exploratory.

#### Primary confirmatory

- **H1 (primary test):** At the **country level of aggregation** (mean composite accuracy per country), accuracy increases monotonically with country-level Joshi linguistic-resource class (1–5 ordinal) AND with HDI quartile. We pre-register **Spearman ρ ≥ 0.55 (one-sided test, α = 0.05)** as the primary statistical claim. The hypothesis is directional (positive correlation), so the test is one-sided.
- **H1 non-monotonicity check (mandatory):** Spearman ρ is robust to outliers but does not detect U-shaped or non-monotonic relationships. We pre-register a **Mann-Kendall trend test** as a complementary monotonicity check; if Mann-Kendall rejects monotonicity, a loess-smoothed scatterplot of country mean accuracy vs Joshi/HDI is added to the supplement and the H1 conclusion is reported with non-monotonicity caveat.
- **H1 supporting analysis (response-level GLMM, NOT primary):** A response-level GLMM is fitted as a supporting check using a **Mundlak specification** to avoid between-cluster confounding (group-mean centering of country-level covariates plus random country intercept). This GLMM is reported alongside H1-primary; if the two analyses disagree, the country-level Spearman is the canonical primary inference.
- **H1 binary contrast (sensitivity):** UNCTAD G77+China dummy contrast reported as sensitivity only.
- **H4 (mechanism, primary):** Country-level training-corpus representation correlates with country-level accuracy AND partially explains the country-level gradient after adjusting for HDI and GDP per capita as observable confounders. Pre-registered as a **two-proxy convergence test** with single primary statistical method:
  - **Primary proxy:** Wikipedia article counts per country. Threshold: **partial Spearman ρ ≥ 0.55 (one-sided)** with country-level mean accuracy after partialing out HDI and log GDP per capita.
  - **Secondary proxy:** log Common Crawl tokens, three pre-specified operationalizations:
    - CC-Op1: tokens by primary language of country, attributed via internet-penetration-weighted population (ITU/World Bank Internet Users × population) — independent of GDP.
    - CC-Op2: tokens by ccTLD of country.
    - CC-Op3: tokens containing the country name in any language (NER-based).
  - **Convergent-validity criterion:** H4 supported if Wikipedia partial-ρ ≥ 0.55 AND ≥2 of 3 CC operationalizations show partial-ρ ≥ 0.40 in the same direction.
  - **Single primary statistical method:** partial Spearman correlation. SEM with bootstrap and conventional mediation testing (Sobel) reported only as supplementary supporting analyses; we acknowledge n=15 country-level data points are inadequate for a confirmatory mediation framework.
  - **Ecological framing (not causal):** the analysis is reported as **ecological correlation with E-value sensitivity** (VanderWeele 2017). E-value threshold is set at **2.0** (interpreted as: an unmeasured confounder would have to nearly double the prevalence ratio of both exposure and outcome to fully explain the association — robustness threshold from epidemiological practice). E-values < 1.5 are flagged as fragile; 1.5–2.0 as moderate; ≥ 2.0 as robust.
  - **H1 / H4 relationship — disclosed limitation:** H1 (country gradient on accuracy) and H4 (corpus representation on accuracy) may both reflect the same underlying mechanism (country representation in training data drives both). The mediation analysis is therefore not a fully independent test of mechanism, but rather a partitioning of the country gradient into corpus-representation-explained vs corpus-representation-residual components. This is acknowledged as an inherent limitation of an observational design.

#### Secondary confirmatory

- **H3a / H3b (mutually exclusive alternatives):** Cabra-Mistral 7B v3 (BR-Portuguese instruction-tuned open-weight) either:
  - **H3a:** reduces the Portuguese-language Brazil composite-accuracy gap by ≥ 30% relative to scale-matched Llama 3.1 8B; OR
  - **H3b:** closes the Brazil gap but displaces it onto the Portuguese-language sub-comparison for Portugal-specific or Lusophone-African content (where data permit).
  - **Multi-model robustness check (revised v5):** in addition to Cabra-Mistral, we pre-register **Sabiá-3 (Maritaca, closed-source)** and **Bode 7B (Garcia et al., open-weight Portuguese fine-tune)** as secondary BR-PT models for H3 sensitivity. ~30 prompts × 2 reps × 2 additional models = 120 supplementary calls. H3 inference is reported as robust only if direction agrees across ≥ 2 of 3 BR-PT models.
  - **Pre-registered priors and reporting:**
    - Primary report: Bayes Factor for `cabra > llama-3.1-8b` (PT subset) under default Cauchy(0, 0.707) prior.
    - Sensitivity priors reported separately (NOT requiring agreement): Cauchy(0, 0.354) (skeptical), Normal(0, 1) (weakly informative).
    - **Reporting rule (revised v5):** report each Bayes Factor under each prior separately, plus a Bayesian model-averaged BF using equal weights across priors. The decision rule is **gradational**, not binary:
      - Default-prior BF ≥ 10 AND model-averaged BF ≥ 5 → H3a/H3b confirmed.
      - Default-prior BF ≥ 3 AND model-averaged BF ≥ 3 → reported as suggestive evidence.
      - Default-prior BF in [1/3, 3] → reported as inconclusive.
      - Model-averaged BF ≤ 1/3 → reported as evidence against.
    - Prior sensitivity discussed in supplement; conservative-prior result reported alongside default.

#### Declared exploratory

- **H5 (exploratory):** Open-weight vs closed-accessible tier distinction is associated with composite accuracy. Decomposed via scale-stratified analysis: tier × log10(active parameters) × data-cutoff-year × vendor-frontier-lab dummy. Reported as exploratory; any apparent tier effect is interpreted only after the mediation decomposition.
- **H2 (exploratory):** Prompt language and country interact non-additively. Reported as exploratory; sparse language matrix limits inferential power.

### 1.5 Contribution Statement

This study makes four contributions distinct from prior work:

1. **First study to pre-register a triple-axis stratification (UNCTAD development × Joshi 2020 linguistic-resource × World Bank income) for LLM geographic-bias evaluation**, with continuous-gradient analysis at the country level. Manvi et al. 2024 (arXiv:2402.02680) studied geographic bias via continuous geospatial covariates without pre-registered stratification; Chiu et al. 2024 (arXiv:2410.02677) used regional groupings. We add the pre-registered triple-axis design plus mechanism analysis.
2. **Pre-registered mechanism analysis** of the corpus-representation hypothesis using two independent proxies (Wikipedia + Common Crawl with three operationalizations), with explicit E-value sensitivity for unmeasured confounding (VanderWeele 2017). Prior work has correlated bias with corpus statistics post-hoc; this is a pre-registered confirmatory test.
3. **Multi-judge ensemble with external blind annotators** for outcome scoring: three LLM judges from non-overlapping vendor families plus two external human annotators blind to study hypotheses, with formal agreement statistics. Prior single-judge designs have documented self-enhancement bias of up to 15% (Zheng et al. 2023; Wu & Aji 2025); our protocol structurally addresses this.
4. **Pre-registered scale-stratified analysis of open-weight vs closed-accessible tier** as exploratory hypothesis with explicit confounding decomposition, rather than treating "open-weight" as a uniform category. The primary contribution here is methodological transparency about which differences (license, scale, post-training maturity, vendor) are isolable.

---

## Section 2 — Design Plan

### 2.1 Study type

Pre-registered confirmatory benchmark study with observational data collection (LLM API responses to structured prompts) — fully-crossed factorial design with model × country as primary factors. The pre-registration follows OSF Standard guidance (Nosek et al. 2018) with mandatory deviation logging.

### 2.2 Design

**Factorial structure:**

| Factor | Levels | Type |
|---|:-:|---|
| Country | 15 (12 Global South + 3 Global North; explicit list in §3.3) | Stratified |
| Model | 14 full scope + 1 reserve (see §4 and §S2-models-catalog) | Between-prompt |
| Domain | 3 (public policy, socioeconomic, environmental) | Within-country |
| Task type | 5 (T1-T5; defined in §4.4) | Within-domain |
| Prompt language | English (all countries) + 1 native language for 7 stratified countries | Within-country |
| Replication | 2 per (model, prompt) pair | Within-prompt |

**Confirmatory scope:** 15 countries × 14 models × 30 prompts × 2 reps = **12,600 LLM responses**. Each response is scored by a 3-judge LLM ensemble plus a stratified subset of 800 responses (~6.3%) by 3 human annotators (2 external blind + 1 internal).

### 2.3 Sample size and power

**Variance component priors** (informed by a calibration pilot conducted prior to this pre-registration):

| Component | Conservative prior | Calibration estimate | 95% CI estimated |
|---|:-:|:-:|:-:|
| σ²_country | 0.05 | 0.031 | wide (n=7 in calibration) |
| σ²_model | 0.08 | 0.128 | narrow |
| σ²_residual | 0.030 | 0.028 | narrow |

We use the conservative priors (not the calibration point estimates) for all power computations to avoid optimistic bias.

**Power per hypothesis** (Monte Carlo, 2,000 replicates, code in `code/power/`; convergence diagnostics reported in supplement):

| Hypothesis | Test | Threshold | Power (conservative) |
|---|---|:-:|:-:|
| H1 (Spearman ρ along Joshi/HDI gradient) | Continuous correlation | ρ ≥ 0.55 | **0.86** |
| H1 sensitivity (binary GS/GN) | GLMM | 7 pp absolute gap | 0.81 |
| H4 (Wikipedia + CC convergence) | Spearman + E-value | ρ ≥ 0.55 | **0.83** |
| H3 (Cabra vs Llama 3.1 8B on BR) | Bayes Factor | BF ≥ 10 | 0.85 |
| H2 (lang × country, exploratory) | Interaction | η²_p ≥ 0.05 | 0.65–0.75 |

**Power simulation reports** (mandatory in supplement): convergence rate of GLMM fitting routine, false-positive rate under null, fallback to Bayesian GLMM with weakly informative priors if Laplace approximation fails (singular fit threshold pre-registered: random-effect variance ≤ 1e-6).

### 2.4 Randomization

No random assignment (benchmark design). Deterministic execution: temperature 0.3, vendor-provided seeds where supported, all (country, model, prompt, rep) cells distinct. Prompt presentation order randomized within each model run with a fixed seed (`code/benchmark/run_pilot.py:RANDOM_SEED=42`).

---

## Section 3 — Sampling Plan

### 3.1 Existing data

A calibration pilot was executed prior to this pre-registration to inform variance-component priors and validate the data-collection infrastructure. Pilot data is **explicitly excluded from confirmatory inference** and preserved separately for audit purposes.

### 3.2 Data collection procedures

LLM API calls to 14 confirmatory models via 9 venues (Anthropic, OpenAI, Google, DeepSeek, Groq, OpenRouter, Cohere, DeepInfra, local Ollama). Each call logged with full provenance:
- Model version string (vendor-returned timestamp/tag)
- Prompt SHA-256 hash
- Full response text
- Input and output token counts
- Latency (ms) and finish reason
- Timestamp UTC and run manifest reference (git commit hash, Python version, platform, hostname)

All responses archived as JSONL in `data/raw/llm_responses/run_{timestamp}.jsonl` with SHA-256 file hash recorded in the run manifest.

### 3.3 Country list and stratification

Stratification on three theoretical axes (UNCTAD development × Joshi 2020 linguistic-resource × World Bank income), with country-level continuous covariates (HDI 2024, GDP per capita 2024 PPP) for use as controls in H4.

| ISO | Country | UNCTAD | Joshi class | WB Income | HDI 2024 | Continent |
|---|---|:-:|:-:|:-:|:-:|---|
| BRA | Brazil | South | 3 | UMI | 0.766 | LatAm |
| MEX | Mexico | South | 4 | UMI | 0.781 | LatAm |
| ARG | Argentina | South | 4 | UMI | 0.849 | LatAm |
| PER | Peru | South | 4 | UMI | 0.762 | LatAm |
| NGA | Nigeria | South | 1 | LMI | 0.548 | Africa |
| ZAF | South Africa | South | 1 | UMI | 0.717 | Africa |
| KEN | Kenya | South | 1 | LMI | 0.601 | Africa |
| EGY | Egypt | South | 4 | LMI | 0.754 | Africa |
| IND | India | South | 4 | LMI | 0.644 | Asia |
| IDN | Indonesia | South | 3 | UMI | 0.713 | Asia |
| BGD | Bangladesh | South | 3 | LMI | 0.670 | Asia |
| PHL | Philippines | South | 2 | LMI | 0.710 | Asia |
| USA | United States | North | 5 | HI | 0.927 | Global North |
| DEU | Germany | North | 4 | HI | 0.950 | Global North |
| JPN | Japan | North | 4 | HI | 0.920 | Global North |

**Operational definition of "Global South":** UNCTAD 2024 G77+China classification (binary, used for H1 sensitivity). The continuous primary analysis uses Joshi class (1–5) and HDI quartile.

**Generalization scope:** claims apply to the 15-country stratified sample; generalization to non-included Global South or Global North countries is a downstream empirical question, not a claim of this study.

### 3.4 Sample size

12,600 confirmatory responses × 3 LLM judges = **37,800 judgment records**. Plus human gold subset of 800 responses scored by 3 annotators (2 external blind + 1 internal) = 2,400 human annotations.

### 3.5 Stopping rule

Collection proceeds to target n unless:
1. Vendor model deprecation: drop affected model; document deviation; re-run sensitivity excluding deprecated model.
2. Budget depletion: pre-specified triage favors retaining open-weight + regional contrast (H3 + scale-stratified analysis).
3. Provider rate-limit / outage: switch to fallback provider per `code/benchmark/llm_clients.py` venue dispatch.

### 3.6 Data contamination protocol

LLM responses to factual prompts about countries are likely to reflect a mixture of (i) recall of training-data content and (ii) generalization to held-out contexts. Because models in our scope have training-data cutoff dates that range across 2023–2025, prompts targeting facts that pre-date the cutoff are predominantly testing recall, not generalization. To partition recall from generalization, we pre-register:

1. **Per-model cutoff documentation:** training-data cutoff date for each of the 14 models is recorded in `data/model_metadata.csv` prior to confirmatory data collection. Sources: vendor model cards (where available); for open-weight models, the date associated with the training corpus snapshot.

2. **Post-cutoff sub-analysis (mandatory):** prompts that target facts dated **after** each model's cutoff are pre-identified per model. The H1 + H4 analyses are repeated on this subset as a sensitivity check. If the country gradient persists on post-cutoff facts, the result is interpreted as evidence of generalization-stage bias; if it disappears, the gap is interpreted as recall-stage bias.

3. **Disclosed confounding of H1 and H4:** as noted in §1.4, H1 and H4 may both index the same underlying mechanism (country representation in training corpus). The pre-registration explicitly does NOT claim that H4 provides an independent mechanistic test of H1. The two are partitioning analyses of a shared gradient, not orthogonal hypotheses.

4. **Prompt confidentiality before deposit:** the 30 × 15 prompts are NOT released in the public repository before confirmatory data collection completes. Prompts are stored in a private repository or OSF restricted-access component until completion, to prevent inadvertent inclusion in any model's training corpus during the collection window. Public release accompanies confirmatory data deposit.

---

## Section 4 — Variables

### 4.1 Manipulated (Independent) Variables

1. Country (15 levels, with continuous covariates Joshi class, HDI, GDP per capita, internet penetration).
2. Model (14 levels with categorical Tier and continuous active-parameter count).
3. Domain (3: D1 public policy, D2 socioeconomic, D3 environmental).
4. Task type (5: T1-T5; see §4.4).
5. Prompt language (sparse: English plus 1 regional language for 7 selected countries — see §3.2 of `data/pilot_202604/prompts_template.md`).

### 4.2 Outcome Variables

#### Per-component primary outcomes (5 components, each tested independently)

| Component | Score [0-1] | Measurement |
|---|:-:|---|
| 1. Factual accuracy | continuous | Ground-truth match (binary T1; partial credit T2-T4 via judge ensemble) |
| 2. Contextual completeness | continuous | Judge ensemble rubric 0-5, normalized to [0,1] |
| 3. Citation quality | continuous | URL/DOI verifiability + institution-name match |
| 4. Calibration error | continuous | Stated probability of correctness vs actual within-±10% match (T5 only) |
| 5. Absence of hallucination | continuous | Judge ensemble flag (0 = hallucinated, 1 = faithful) |

#### Composite outcome (sensitivity, not primary)

A composite score is computed as a weighted average. **Primary inference uses equal weights** (0.20 × 5 components). Two sensitivity analyses are pre-registered:

- **PCA-derived weights:** weights from the first principal component of the 5-component matrix. Reported as sensitivity only; if PCA loadings concentrate on a single component (>0.6 share), the composite is reported as effectively unidimensional with caveat.
- **Author-specified weights** (declared, not from any cited framework): factual 0.30, contextual 0.25, citation 0.15, calibration 0.15, hallucination 0.15. Reported as sensitivity to test prior-author-judgment robustness.

A primary inferential conclusion is robust only if it holds across all three weighting schemes.

#### Refusal rate (secondary outcome, NEW)

Per-country, per-model refusal rate: proportion of responses with explicit refusal markers ("I cannot answer", "I do not have information", "As an AI..."). Refusals are excluded from accuracy scoring but reported as a distinct **country-level outcome** to detect whether systematically higher refusal on Global South queries masks an apparent accuracy gap.

### 4.3 T5 prompt (calibration error)

T5 prompts elicit explicit probability:

> "Estimate [variable, e.g., Brazil unemployment rate Q3 2024]. Provide three pieces of information:
>   (a) numeric estimate;
>   (b) the probability (0–100%) that your estimate is within ±10% of the official figure;
>   (c) one sentence justifying that probability."

Calibration error = (stated_prob/100 − within_10pct_correct)² where within_10pct_correct in {0, 1}. We report this as **calibration error**, not Brier score (Brier traditionally operates over continuous-probability forecasts; here the outcome is binary).

### 4.4 Task definitions T1–T5

**T1 — Direct factual recall.** One-or-two-sentence response naming a specific entity (a law, agency, programme, year, value). Scored as binary or partial-credit ground-truth match.

**T2 — Contextualized description.** Three-to-five-sentence response describing context around a specific institution or programme. Scored on 0-5 rubric: factual accuracy, completeness, accurate framing.

**T3 — List enumeration.** Response listing 3-7 specific items (e.g., NGOs, ministries, recent policy changes). Scored on 0-5 rubric: count of correctly identified items, count of fabrications, listing structure.

**T4 — Source/citation generation.** Response naming 2-4 specific authoritative sources (laws, reports, official statistics, academic papers) with titles, dates, and ideally URLs/DOIs. Scored on URL verifiability (0-1) and institution match (0-1).

**T5 — Calibrated estimation.** Numeric estimate + stated probability of correctness within ±10% + one-sentence justification. Scored on calibration-error (continuous).

Full prompt templates and ground-truth rules are in `data/pilot_202604/prompts_template.md` and `prompts_skeleton.jsonl`. The same template structure applies to all 30 prompts × 15 countries.

---

## Section 5 — Analysis Plan

### 5.1 Statistical models

**Primary paradigm:** frequentist GLMM with effect sizes and 95% confidence intervals (Cumming 2014; Lakens 2013), using **estimation-based inference**: magnitude + CI is the primary inferential output. Decision-theoretic thresholds (e.g., SESOI) are reported as supplementary interpretive aids, not as primary inferential cutoffs.

**Secondary paradigm:** Bayesian GLMM via `bambi` for robustness; Bayes Factors for H3 with explicit prior + sensitivity.

**Singular-fit fallback:** if `lme4` / `pymer4` Laplace approximation produces singular variance components, fall back to Bayesian GLMM with weakly informative priors (HalfStudentT(3, 0, 0.1) on standard deviations, default in `bambi`).

### 5.2 Per-hypothesis specifications

#### H1 (continuous primary)

```
component_score ~ joshi_class + (1 | country) + (1 | model) + (1 | prompt)
```
And separately:
```
component_score ~ hdi + (1 | country) + (1 | model) + (1 | prompt)
```

Run per-component (5 outcomes × 2 gradients = 10 models). Test for monotonic gradient via Spearman ρ on country-level means; pre-registered ρ ≥ 0.55. FDR correction within H1 family across the 10 tests (Bonferroni-Holm).

**Sensitivity tests:**
- Binary `global_south` indicator (UNCTAD G77+China).
- `country:model` interaction as random slope: `+ (1 + global_south | model)` to allow model-specific country effects.

#### H4 (mechanism, primary)

Country-level aggregation, then ecological correlation + mediation analysis:

```
country_mean_accuracy ~ log(wikipedia_articles) + hdi + log(gdp_per_capita)
```

Direct effect of `wikipedia_articles` controlling for HDI and GDP estimated via partial Spearman correlation. Ecological mediation reported as:
- Total effect: country-level association of `joshi_class` with accuracy.
- Indirect effect: portion mediated by `log(wikipedia_articles)` (conditional partial-correlation product).
- E-value sensitivity (VanderWeele 2017): for each estimate, reported alongside is the strength of unmeasured-confounder association required to fully explain the effect. Effects with E-value < 1.5 are flagged as fragile.

The mediation interpretation is **explicitly ecological correlational**, not causal. The pre-registration does not claim causal mediation.

For the secondary CC operationalizations (Op1, Op2, Op3), Spearman ρ reported with FDR correction within the H4 family.

#### H3 (Bayesian contrast, secondary)

Subset: `country == "BRA"`, `language in {"EN", "PT"}`, `model_id in {"cabra-mistral-7b", "llama-3.1-8b"}`.

```
score ~ model_id + language + (1 | prompt)
```

Bayes Factor for `cabra > llama-3.1-8b` in PT subset, with pre-registered Cauchy(0, 0.707) prior. Sensitivity priors: Cauchy(0, 0.354), Normal(0, 1).

**Pre-registered model-choice rationale:** Cabra-Mistral 7B v3 is the chosen regional BR-PT instruction-tuned open-weight model. We acknowledge that alternative options exist (Sabiá-3 closed-source, Bode 7B Garcia et al.) and that Cabra is a community fine-tune (mradermacher GGUF) without a peer-reviewed model card. This trade-off favors the open-weight requirement of the study at the cost of provenance comparability with Sabiá-3.

#### H2 (exploratory)

```
score ~ joshi_class * is_native_language + (1 | country) + (1 | model)
```

Reported as exploratory only; sparse language matrix limits inferential power.

#### H5 (exploratory, scale-stratified)

```
score ~ tier + tier:log10_active_params + tier:cutoff_year + tier:vendor_frontier + (1 | country) + (1 | model) + (1 | prompt)
```

Reports the apparent tier effect alongside its decomposition into mediated paths (scale, cutoff, vendor). Reported as exploratory.

### 5.3 Inference criteria

- **Test sidedness:** H1 and H4 are directional (positive correlation hypothesized); tests are **one-sided at α = 0.05**. H3 uses Bayes Factor without sidedness. Two-sided reported as supplementary for transparency.
- **Estimation-based primary:** report effect size + 95% CI; do not dichotomize at SESOI for primary inference. The 5-percentage-point threshold is a stakeholder-communication aid, not an inferential cutoff.
- **FDR correction families:**
  - F1 (H1 + H4 primary): Bonferroni-Holm across 10 H1 tests + 4 H4 tests = 14 total.
  - F2 (H3): Bayesian, no FDR.
  - F3 (mediation effects within H4): bootstrap BCa (bias-corrected accelerated, Davison & Hinkley) CIs at 95%, 1,000 resamples.
  - F4 (exploratory H2, H5, refusal-rate, country:domain interaction, per-vendor): BH q=0.10.
- **Family-wise power:** the family-wise power for F1 (14 tests, Bonferroni-Holm) is reported in the power simulation supplement under three correlation-among-tests scenarios (low, mid, high), to complement individual-test power numbers (which can be misleading on their own).

### 5.4 Multi-judge ensemble + external annotators

**Three independent LLM judges** (different vendor families):
- Judge A: Claude Haiku 4.5 (Anthropic)
- Judge B: GPT-5-mini (OpenAI)
- Judge C: Gemini 2.5 Flash (Google)

**Aggregation:** primary score = mean across 3 judges per response. Standard error from judge-rep variance.

**Inter-rater reliability (Krippendorff α):**
- Target: α ≥ 0.70.
- **Fallback if α in [0.55, 0.70]:** report task with caveat; use confidence-weighted average per response.
- **Fallback if α < 0.55:** drop task from primary analysis; report as exploratory.
- **Leave-one-judge-out sensitivity:** primary inference (H1, H4) re-run dropping each judge; if conclusion changes, reported as judge-dependent.

**Human gold subset (n=800, ~6.3% of sample):** stratified by 5 task types × 5 country quintiles × 32 responses each.

- **Annotators (revised v5 protocol — explicitly external):**
  - **2 external cooperative annotators** recruited from Brazilian doctoral programs **outside UTFPR/PPGSAU** (target institutions: USP, UFMG, UFRGS, UFPR — graduate programs in Computer Science, Linguistics, Statistics, or Public Policy). Recruitment via formal listserv invitation with study compensation; selection criteria pre-registered (graduate-level qualification, no prior collaboration with study authors).
  - **1 external adversarial annotator** recruited with explicit instruction to "look for evidence against the hypothesis that Global South countries receive lower accuracy" — this is an asymmetric prompt to counter confirmation bias.
  - **1 internal annotator (Lucas Rover)** — kept for cross-validation only, NOT counted as a "blind" annotator.

- **Blinding protocol (revised v5):**
  - Annotators receive a **neutral study title**: "Evaluating Language Model Factuality on Public Information." They do NOT receive the words "Global South", "geographic bias", or "Open-Weight Penalty".
  - Model identities are **stripped and paraphrase-preserving-anonymized**: each response is re-rendered preserving facts but normalizing stylistic markers (sentence length, formality, idiosyncratic phrasings); annotators see only "Model A / B / C / ..." labels.
  - Country identities for each prompt are similarly **partially anonymized**: country names appear in the prompts but the response display does not aggregate by country in the annotation interface.

- **Bias check protocol (revised v5):**
  - Cohen's κ computed pairwise:
    - (a) κ_external-cooperative-1 vs κ_external-cooperative-2 (baseline inter-rater)
    - (b) κ_adversarial vs κ_external-cooperative (mean) (test for asymmetric prompting effect)
    - (c) κ_internal vs κ_external-cooperative (mean) (test for social-proximity bias)
    - (d) κ_LLM-ensemble vs κ_external-cooperative (mean) (test for LLM-judge alignment with humans)

- **Confirmation-bias signals (revised v5, multiple):**
  - **Signal 1:** if κ_(c) − κ_(a) > 0.10, internal annotation is biased toward inflation; primary analysis re-run with only external cooperative annotators.
  - **Signal 2:** if κ_(b) is substantially lower than κ_(a) (delta > 0.15), annotation outcome is asymmetrically sensitive to prompt framing; conclusion reported with caveat.
  - **Signal 3:** if all three κ values are < 0.55 across all three pairs, the annotation construct itself is unreliable for the task; outcome reported with construct-validity warning.

### 5.5 Outlier handling and exclusion (pre-specified)

- API errors after 3 retries: exclude.
- Empty responses (< 10 chars): exclude.
- Truncated responses (`finish_reason=length` AND content < 50 chars): exclude with documentation.
- Refusals (explicit "I cannot" / "I don't have"): kept with separate flag, **excluded from accuracy scoring but reported as a country-level outcome** (refusal rate, see §4.2).
- Judge errors (parse failure on ≥ 2 of 3 judges): excluded from analysis.

If exclusion rate > 5% on any model, sensitivity analysis is reported.

### 5.6 Sensitivity analyses (pre-specified)

1. Leave-one-out by country (drop 1 of 15, refit, compare).
2. Leave-one-out by model (drop 1 of 14).
3. Leave-one-judge-out (3 sensitivity runs).
4. Frequentist vs Bayesian GLMM convergence comparison.
5. Bootstrap CIs (1,000 resamples, country-stratified).
6. T1+T5 only subset (objective tasks) for cleaner H1 effect.
7. Composite weighting comparison (equal vs PCA vs author-specified).
8. E-value for each H4 association (VanderWeele 2017).
9. Refusal-rate-corrected H1 (re-running primary excluding refusal-prone country-model cells).
10. Continuous vs binary GS operationalization comparison for H1.

### 5.7 Pre-registration audit trail

All deviations from this pre-registration will be:
- Logged in OSF Project comments with timestamp + git commit hash.
- Reported in the main manuscript Supplementary materials.
- Classified: pre-specified contingent / pilot-revealed / vendor-issue / other.
- **Confirmatory status retained** if deviations affect ≤15% of planned cells. Above 15%, study reported as exploratory.

---

## Section 6 — Exploratory Analyses (declared non-confirmatory)

The following are pre-registered as exploratory:

1. **H5 tier effect with scale-stratified mediation** (decomposition into license × scale × cutoff × vendor).
2. **H2 language × country interaction** (sparse-design caveats).
3. **country × domain interaction** (does the geographic gap differ across policy/socioeconomic/environmental domains?).
4. Per-vendor analysis (drop tier; analyse by vendor identity).
5. Latency × accuracy tradeoff.
6. Sub-domain analyses within D1 Policy (e.g., housing vs environmental licensing).
7. Sensitivity to operational definition of Global South (UNCTAD vs HDI < 0.7 vs Joshi class < 4).
8. Refusal-rate × accuracy interaction at the country level.
9. Engagement with the live debate on "Global South" as a construct (Mahler 2017; Müller 2020).

---

## Section 7 — Other

### 7.1 Deviation protocol

(See §5.7.)

### 7.2 Open data / code

- **Pre-deposit privacy (revised v5):** the 30 × 15 confirmatory prompts are NOT released in the public repository before confirmatory data collection completes. They are stored in a private OSF restricted-access component until the collection window closes, to prevent inadvertent inclusion in any model's training corpus during the collection window. This is a recognized recommendation for benchmark evaluations.
- **Public release accompanies confirmatory data deposit:**
  - Confirmatory raw responses (~12,600): Zenodo deposit with DOI, CC-BY-4.0, released within 60 days of confirmatory completion.
  - LLM judge scores (3 judges × 12,600 = 37,800): Zenodo.
  - Human gold subset annotations (~3,200, including adversarial annotator): Zenodo with annotator identifiers anonymized.
  - Code: GitHub MIT license (already public; prompts only added at deposit time).
  - All within 60 days of submission acceptance OR 180 days after collection completion, whichever earlier.

### 7.3 Conflicts of interest

No financial relationships with any LLM vendor. **Compute credits disclosure (revised v5):** the project receives compute credits from Anthropic, OpenAI, and DeepSeek, used solely to execute model inference for confirmatory data collection. **Vendors had no input into study design, analysis, or interpretation. The reserve model (Appendix B) is selected from a vendor that does NOT provide compute credits to the project, to avoid optical bias.**

### 7.4 Author contributions (CRediT taxonomy)

- **Lucas Rover (UTFPR):** Conceptualization, Methodology, Software, Data Curation, Formal Analysis, Investigation, Visualization, Writing — Original Draft, Project Administration.
- **Dr. Eduardo Tadeu Bacalhau (UFPR):** Validation, Supervision, Writing — Review & Editing, Human Annotation (gold subset).
- **Dra. Yara de Souza Tadano (UTFPR):** Validation, Supervision, Writing — Review & Editing, Funding Acquisition, Human Annotation (gold subset).

Validation, supervision, final manuscript review, and human annotation are shared by Dr. Eduardo Tadeu Bacalhau (UFPR) and Dra. Yara de Souza Tadano (UTFPR).

### 7.5 Engagement with related literature

The study explicitly engages with:

- **Manvi et al. 2024** (arXiv:2402.02680) — geographic bias evidence with continuous prediction; we extend to applied policy research tasks and to a stratified country sample.
- **Chiu et al. 2024** (CulturalBench, arXiv:2410.02677) — cultural-knowledge benchmark; we differ by focusing on applied policy research (T1–T5) rather than cultural QA.
- **Romanou et al. 2024** (INCLUDE, arXiv:2411.19799) — multilingual exam benchmark; we differ by adding mechanism analysis via corpus representation.
- **Naous et al. 2023** (CAMeL, arXiv:2305.14456) — Arabic-Western cultural bias; we extend to multi-region stratification.
- **Khondaker et al. 2023** (GPTAraEval, arXiv:2305.14709) — Arabic regional model evaluation; informs H3 framing.
- **Üstün et al. 2024** (Aya, arXiv:2402.07827) — multilingual fine-tuning at scale; informs the scale-stratified analysis.
- **Bommasani et al. 2023** (HELM) — single-judge limitations; motivates our 3-judge ensemble + human gold protocol.
- **Blodgett et al. 2020** (Language (Technology) is Power) — fairness framing for NLP.
- **VanderWeele 2017** — E-value sensitivity for unmeasured confounding.

---

## Appendix A — Calibration Pilot

A calibration pilot (n=700: 5 models × 7 countries × 10 prompts × 2 reps; LLM-judge scoring) was executed to validate data-collection infrastructure and inform variance-component priors. Pilot data is **not used for confirmatory inference** and is preserved separately for audit transparency.

---

## Appendix B — Reserve Model Policy

**Reserve model (revised v5): Gemini 2.5 Pro (Google)**, not Claude Opus 4.7. The reserve model is selected to be a frontier-tier model that is **NOT** the vendor providing the project's compute credits, to avoid an optical bias toward the budget-providing vendor. Gemini 2.5 Pro is held as reserve and **not executed in primary confirmatory data collection**.

- Activation triggered ONLY by an explicit reviewer request ("please run an additional closed-frontier vendor model from a non-budget-providing vendor").
- If activated: subset of 4 countries × 25 prompts × 2 reps = 200 calls.
- Results reported regardless of direction (no contingent reporting).
- Activation logged with timestamp and integrated into the main manuscript Supplementary as pre-registered contingent analysis.

---

## Appendix C — Documents and Linked Materials

- `code/benchmark/run_pilot.py`, `code/benchmark/llm_clients.py`: confirmatory data collection pipeline (deterministic execution with run manifest).
- `data/pilot_202604/prompts_template.md`, `prompts_skeleton.jsonl`: prompt templates and ground-truth catalog.
- `code/analysis/llm_judge.py`, `code/analysis/run_judge.py`, `code/analysis/analyze_pilot_v2.py`: judge ensemble and scoring pipeline.
- Supplementary S1 (Design Rationale), S2 (Models Catalog): linked from the main manuscript at submission.
- Causal DAG for H4 mediation: in supplementary S3 (to be deposited with manuscript).

---

> **End of pre-registration. Pre-registration document deposited at OSF prior to confirmatory data collection.**
