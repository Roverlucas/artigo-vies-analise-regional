# OSF Pre-Registration — Geographic and Persona-Modulated Performance Gaps in Large Language Models for Global South Air Pollution Policy

**Template:** OSF Standard Pre-Registration
**Version:** 7.0 (full) — supersedes v6 draft (`osf_prereg_draft.md`, 2026-04-26)
**Study type:** Pre-registered confirmatory benchmark study with declared exploratory components
**Pre-registration timing:** prior to confirmatory data collection
**Estimated execution window:** 2026-Q2 / Q3

> **Provenance note.** v6 was never deposited at OSF. v7 supersedes v6 entirely; no amendment is required because no public record exists. The Brazil (BRA) data already collected under the v6 three-domain design (839 responses, 2026-04-28) is reclassified as an **extended pilot** in v7 and is excluded from confirmatory inference (see §3.1).

---

## Section 1 — Study Information

### 1.1 Title

> *Geographic and Persona-Modulated Performance Gaps in Large Language Models for Global South Air Pollution Policy: A 15-Country Pre-Registered Audit With Mechanism Analysis*

**Short title:** *Geographic Bias, Persona Effects, and Mechanism in LLMs for Air Pollution Policy*

**What changed from v6.** The scope narrows from three generic domains (public policy, socioeconomic, environmental) to a single theory-driven domain: **air pollution (AP) policy**. This ties every outcome to officially anchored ground truth (WHO, CONAMA, CETESB, and national regulatory equivalents) and matches the domain expertise of the co-supervising author. A within-subject **persona manipulation** (neutral query vs public environmental manager) is added, supporting a new co-primary hypothesis (H6).

### 1.2 Authors

1. **Lucas Rover** — Federal University of Technology — Paraná (UTFPR), Brazil — `lucasrover@alunos.utfpr.edu.br` — *corresponding author* — ORCID 0000-0001-6641-9224
2. **Dr. Eduardo Tadeu Bacalhau** — Federal University of Paraná (UFPR), Brazil — `bacalhau@ufpr.br`
3. **Dra. Yara de Souza Tadano** — Federal University of Technology — Paraná (UTFPR), Brazil — `yaratadano@utfpr.edu.br`

Validation, supervision, results review, and writing review are shared CRediT roles of Dr. Eduardo Tadeu Bacalhau and Dra. Yara de Souza Tadano (see §7.4).

### 1.3 Research Questions

**Confirmatory primary:**

- **RQ1.** Across a continuous gradient of country-level digital and developmental conditions (Joshi linguistic-resource class; HDI; Common Crawl + Wikipedia representation), do Large Language Models exhibit systematically lower factual accuracy on **air pollution policy** tasks?
- **RQ2.** Does country-level training-corpus representation (Wikipedia article counts as primary proxy; Common Crawl tokens as secondary, with three operationalizations) account for the country-level accuracy gradient on AP policy tasks, after controlling for HDI and GDP per capita?
- **RQ3 (new in v7).** Does **persona prompting** — presenting the query as coming from a public environmental manager — reduce or amplify the country-level accuracy gradient on AP policy tasks?

**Confirmatory secondary:**

- **RQ4.** Does a regional Brazilian-Portuguese instruction-tuned open-weight model (Cabra-Mistral 7B v3) reduce the Portuguese-language accuracy gap for Brazil on AP policy tasks, relative to a scale-matched globally-trained open model (Llama 3.1 8B), or displace the gap onto other Lusophone contexts where comparable ground truth exists?

**Declared exploratory:**

- **RQ5.** Does prompt language interact with country-level conditions on AP policy accuracy?
- **RQ6.** Does the open-weight (frontier) vs closed-frontier tier distinction predict AP policy accuracy, after stratifying by model scale and data cutoff?

### 1.4 Hypotheses

All hypotheses are directional and pre-specified. **H1, H4, and H6 are co-primary confirmatory.** H3 is secondary confirmatory. H2 and H5 are explicitly exploratory.

#### Primary confirmatory

**H1 (country gradient, primary).** At the **country level of aggregation** (mean composite accuracy per country, n=15), accuracy increases monotonically with country-level Joshi linguistic-resource class (1–5 ordinal) AND with HDI quartile. The primary statistical claim is **Spearman ρ ≥ 0.55 (one-sided, α = 0.05)**. Because the hypothesis is directional (positive correlation), the test is one-sided.

- **Non-monotonicity check (mandatory).** Spearman ρ is robust to outliers but cannot detect U-shaped or non-monotonic relationships. A **Mann-Kendall trend test** is pre-registered as a complementary monotonicity check. If Mann-Kendall rejects monotonicity, a loess-smoothed scatterplot of country mean accuracy vs Joshi/HDI is added to the supplement and the H1 conclusion is reported with a non-monotonicity caveat.
- **Supporting variance partitioning (not a gradient test).** A response-level GLMM is fitted **without** between-country covariates as fixed effects, solely to estimate variance components (ICC_country, ICC_model, residual). Country-level covariates (`joshi_class`, `hdi`) are strictly between-country and have no within-country variation; entering them as fixed effects alongside `(1|country)` would induce between/within-cluster confounding and would not produce interpretable gradient estimates. Mundlak group-mean centering is therefore not applicable. The canonical primary gradient test is exclusively the country-level Spearman ρ.
- **Binary contrast (sensitivity).** A UNCTAD G77+China dummy contrast at the country level (Mann-Whitney U) is reported as sensitivity only.

**H4 (mechanism, primary).** Country-level corpus representation correlates with country-level accuracy AND partially explains the country-level gradient after adjusting for HDI and log GDP per capita as observable confounders. Pre-registered as a **two-proxy convergence test** with a single primary statistical method:

- **Primary proxy:** Wikipedia article counts per country. Threshold: **partial Spearman ρ ≥ 0.55 (one-sided)** with country-level mean accuracy after partialing out HDI and log GDP per capita.
- **Secondary proxy:** log Common Crawl tokens, three pre-specified operationalizations:
  - CC-Op1: tokens by primary language of country, attributed via internet-penetration-weighted population (ITU/World Bank internet users × population), independent of GDP.
  - CC-Op2: tokens by ccTLD of country.
  - CC-Op3: tokens containing the country name in any language (NER-based).
- **Convergent-validity criterion:** H4 supported if Wikipedia partial-ρ ≥ 0.55 AND ≥ 2 of 3 CC operationalizations show partial-ρ ≥ 0.40 in the same direction.
- **Single primary statistical method:** partial Spearman correlation. SEM with bootstrap and Sobel mediation are reported only as supplementary supporting analyses; n=15 country-level points are inadequate for a confirmatory mediation framework.
- **Ecological framing (not causal).** Reported as ecological partial correlation with **E-value sensitivity** (VanderWeele & Ding 2017). E-value threshold = **2.0** (an unmeasured confounder would have to nearly double the prevalence ratio of both exposure and outcome to fully explain the association). E-values < 1.5 are flagged as fragile; 1.5–2.0 as moderate; ≥ 2.0 as robust.
- **Disclosed H1/H4 relationship.** H1 (country gradient on accuracy) and H4 (corpus representation on accuracy) may both reflect the same underlying mechanism (country representation in training data driving both). The mechanism analysis is therefore not a fully independent test; it is a partitioning of the country gradient into corpus-representation-explained and corpus-representation-residual components. This is an inherent limitation of an observational design.

**H6 (persona effect, NEW co-primary).** The persona condition (`public_manager_env`) **reduces** the country-level accuracy gap for Global South countries by at least **0.05 on the [0,1] composite (equivalently, 5 percentage points of absolute accuracy)** relative to the neutral condition. This unit convention — the composite is scored in [0,1], so 0.05 = 5 pp — is used consistently throughout (§4.3, §5.2).

- **Primary test:** country-level difference-in-differences (DiD) of mean accuracy.

  Let Δ_GS = mean(persona accuracy, Global South) − mean(neutral accuracy, Global South) and Δ_GN = mean(persona accuracy, Global North) − mean(neutral accuracy, Global North). The H6 statistic is **Δ_GS − Δ_GN**. The persona is hypothesized to close the gap, so the test is **one-sided** for gap reduction at α = 0.05. H6 is supported if Δ_GS − Δ_GN ≥ 0.05 with p ≤ 0.05.
- **Effect-size thresholds:** absolute gap reduction ≥ 5 pp is treated as meaningful; ≥ 10 pp as substantial.
- **Direction is theory-relevant, both ways.** Persona prompting may *reduce* bias if instruction following and RLHF emphasized helpful policy-relevant responses (the **Norm-Compliance** hypothesis), or may *amplify* bias if the model's representation of a "Global South public manager" lacks training signal and the authoritative framing increases confident fabrication of regulatory specifics (the **Persona-Vacuum** hypothesis). H6 tests Norm-Compliance against the alternative. The amplification direction (Δ_GS − Δ_GN < 0) is scientifically informative and is reported transparently if observed, via a two-sided secondary test.
- **Manipulation check (mandatory).** Persona adherence is verified independently of accuracy (see §3.4). H6 inference is interpreted only on the subset where the manipulation check passes; the full-sample result is reported as sensitivity.

#### Secondary confirmatory

**H3 (regional model, secondary).** Cabra-Mistral 7B v3 (BR-Portuguese instruction-tuned open-weight) reduces the Portuguese-language accuracy gap for Brazil on AP policy tasks relative to a scale-matched globally-trained open model (Llama 3.1 8B). Pre-registered as a one-sided contrast in the GLMM (α = 0.05) with a Bayesian companion (Bayes Factor under default Cauchy(0, 0.707) prior; sensitivity priors Cauchy(0, 0.354) and Normal(0, 1) reported separately). **Exploratory companion:** whether Cabra-Mistral closes or displaces the gap onto other Lusophone contexts (Lusophone Africa) where AP policy ground truth exists.

#### Declared exploratory

- **H2 (exploratory).** Prompt language × country interaction on AP policy accuracy. Reported descriptively; if formal tests are applied they enter the F3 family at BH q = 0.10. The sparse language matrix limits inferential power.
- **H5 (exploratory).** Open-weight frontier (Tier A) vs closed-frontier (Tier E) on AP policy accuracy. Reported descriptively, decomposed by scale, cutoff, and vendor.

### 1.5 Contribution Statement

This study makes four contributions distinct from prior work.

1. **First pre-registered audit of LLM geographic factual bias scoped to air pollution policy**, a domain with officially anchored, verifiable ground truth (national ambient air-quality standards, official monitoring data, peer-reviewed health-burden estimates). Existing geographic-bias benchmarks evaluate macroeconomic indicators (Moayeri et al. 2024, WorldBench), subjective ratings (Manvi et al. 2024), journalistic fact-checking (Mirza et al. 2024), everyday cultural knowledge (Myung et al. 2024, BLEnD), or standardized medical exams (Paiola et al. 2025). None evaluate the policy-relevant tasks a public environmental manager actually delegates to an LLM.
2. **Persona prompting as a pre-registered confirmatory variable (H6).** Prior work treats the query frame as fixed. We declare persona as a within-subject manipulation and test, with a difference-in-differences design plus permutation inference, whether a "public manager" frame reduces or amplifies the Global South accuracy gap. He et al. (2025) showed LLM policymaking exhibits context-blind rigidity and under-alignment with Global South experts; we test whether an explicit professional persona shifts that behavior.
3. **Pre-registered mechanism analysis** of the corpus-representation hypothesis using two independent proxies (Wikipedia + Common Crawl with three operationalizations) and explicit E-value sensitivity for unmeasured confounding (VanderWeele & Ding 2017).
4. **Multi-judge ensemble with external blind annotators** for outcome scoring: three LLM judges from non-overlapping vendor families plus external human annotators blind to the study hypotheses, with formal agreement statistics, structurally addressing documented single-judge self-enhancement bias.

---

## Section 2 — Design Plan

### 2.1 Study type

Pre-registered confirmatory benchmark study with observational data collection (LLM API responses to structured prompts). Fully-crossed factorial design with model × country as primary factors and **persona as a within-prompt manipulation**. The pre-registration follows OSF Standard guidance (Nosek et al. 2018) with mandatory deviation logging.

### 2.2 Design

| Factor | Levels | Type |
|---|---|---|
| Country | 15 (12 Global South + 3 Global North; explicit list in §3.3) | Stratified |
| Model | 14 full scope + 1 reserve (see §4.5 and Appendix B) | Between-prompt |
| **Domain** | **1 (air pollution policy)** | Single (was 3 in v6) |
| Task type | 5 (T1–T5; defined in §3.2) | Within-country |
| **Persona** | **2 (neutral, public_manager_env)** | **Within-prompt (NEW)** |
| Prompt language | English (all countries) + 1 native language for stratified countries | Within-country |
| Replication | 2 per (model, prompt, persona) tuple | Within |

**Confirmatory scope.** ~600 unique prompts (15 countries × ~40 prompts/country across 5 tasks and the language matrix) × 14 models × 2 personas × 2 reps = **33,600 LLM responses** (600 × 14 × 2 × 2). The persona manipulation is fully crossed and paired at the prompt level, which is what powers the H6 within-subject contrast (§4.5 power note). Each response is scored by a 3-judge LLM ensemble; a stratified subset is scored by external human annotators (§5.4).

### 2.3 Randomization

No random assignment across countries/models (benchmark design). The **persona condition is randomized in presentation order** within each (model, prompt) run with a fixed seed, so that neutral and persona versions of the same prompt are not always presented in the same order. Deterministic execution otherwise: temperature 0.3, vendor-provided seeds where supported, all (country, model, prompt, persona, rep) cells distinct. Seed fixed in `code/benchmark/run.py:RANDOM_SEED=42`.

---

## Section 3 — Sampling Plan

### 3.1 Prior data (BRA extended pilot)

A BRA collection of 839 responses was executed under the v6 three-domain design (2026-04-28). In v7 it is reclassified as an **extended pilot** and is **excluded from confirmatory inference**. Rationale:

1. v6 was never deposited at OSF — there is no public confirmatory status to preserve.
2. v7 scope is narrower (1 domain vs 3); only a minority of BRA prompts (the former environmental domain) is even partially relevant, and none target air pollution policy specifically.
3. v7 adds the persona manipulation, which the BRA collection does not contain.

The BRA extended pilot informs v7 prompt calibration, instrumentation validation, and variance-component priors for power analysis. Confirmatory collection under v7 starts fresh after OSF deposit, including a re-collection for BRA under the new design. A separate calibration pilot for the persona manipulation and the AP-policy ground-truth registry is documented in Appendix A.

### 3.2 Task taxonomy for air pollution policy (NEW)

Each task maps to a recognizable decision activity of a public-sector environmental manager. The taxonomy structure was validated by the domain experts (Quality Gate SA-QG-003); the ground-truth content was corrected following that review (see §3.5).

| Task | Name (PT) | Description | Example (BRA) | Scoring |
|---|---|---|---|---|
| **T1** | Norma técnica | Recall of binding ambient air-quality standards, emission limits, or regulatory thresholds | Annual mean PM₂.₅ standard currently in force in Brazil | Binary / partial-credit ground-truth match |
| **T2** | Dado factual local | Recall of officially measured air-quality data for a specific city/region/year | Annual PM₂.₅ in the São Paulo metropolitan region (RMSP), 2023, per CETESB | Numeric ±tolerance vs official record |
| **T3** | Síntese de evidência em saúde | Synthesis of peer-reviewed epidemiological evidence on health burden | Mortality attributable to PM₂.₅ in country X | 0–5 rubric (accuracy, completeness, no fabrication) + citation verifiability |
| **T4** | Instrumentos de política | Identification of policy programmes, executing agencies, legal instruments | Federal air-pollution control programmes and ministries | 0–5 rubric (correct items, fabrications, structure) |
| **T5** | Recomendação aplicada | Rubric-scored applied recommendation for a defined operational scenario | Short-term episode response (thermal inversion, PM₂.₅ > 75 µg/m³) | 0–5 rubric (operational validity, feasibility) |

**Ground-truth registry requirement (blocks confirmatory multi-country collection).** T1 and T2 anchor in national instruments. Before scaling from BRA to 15 countries, a **per-country ground-truth registry** is built, with one officially verifiable source per (country, task) cell. Where an equivalent official source is unavailable for a country, that (country, task) cell is dropped and the limitation reported, so that the H1 geographic gap is not confounded with ground-truth availability.

#### 3.2.1 T1 ground-truth correction (CRITICAL — Brazil)

The binding national standard for Brazil is set by **CONAMA Resolution 506/2024**, which partly revoked **CONAMA Resolution 491/2018**. The 506/2024 schedule defines interim standards PI-1 through PI-4 plus a final standard (PF) aligned with the WHO 2021 annual guideline of 5 µg/m³. Under this schedule, the interim standard **PI-2** has been in force since 1 January 2025; therefore the value in force during the confirmatory window (2026) is PI-2, **not** PI-1, and not the 491/2018 value.

- The T1 BRA prompt is **decoupled from any specific resolution number** in its stem; it asks for the standard currently in force, so a model that correctly answers under 506/2024 is not penalized.
- The exact numeric annual PI-2 value for PM₂.₅ under Annex I of CONAMA 506/2024 is **[PENDING HUMAN VALIDATION]** (Anexo I; to be confirmed by Dra. Yara Tadano and Dr. Eduardo Bacalhau against the official text before OSF lock). It is intentionally not stated here to avoid invented numbers.
- **Why this matters for inference.** The 14 models have heterogeneous training cutoffs. A ground truth fixed to an obsolete standard would penalize up-to-date models and confound H1 and H6 (both co-primary). The corrected, cutoff-aware ground truth is therefore a validity requirement, not a stylistic choice. Per-model cutoff handling is specified in §3.6.

### 3.3 Country list and stratification

Stratification on three theoretical axes (UNCTAD development × Joshi 2020 linguistic-resource × World Bank income), with country-level continuous covariates (HDI 2024, GDP per capita 2024 PPP) used as controls in H4.

| ISO | Country | UNCTAD | Joshi class | WB income | HDI 2024 | Region |
|---|---|---|---|---|---|---|
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

> HDI values follow UNDP Human Development Report data. [CITATION NEEDED: exact UNDP HDR edition/year and per-country values to be locked against the official UNDP dataset before OSF deposit.]

**Operational definition of "Global South":** UNCTAD G77+China classification (binary; used for H1 and H6 sensitivity and for the H6 GS/GN partition). The continuous H1 primary analysis uses Joshi class (1–5) and HDI quartile.

**Generalization scope:** claims apply to the 15-country stratified sample; generalization to non-included countries is a downstream empirical question.

### 3.4 Persona protocol (NEW)

The persona manipulation is the experimental basis of H6. Two conditions are applied to every prompt.

**Condition `neutral`.** The question is posed plainly, with no stated requester role.

> Template (EN): *"{question stem}."*
> Example (BRA, T1): *"What is the annual ambient air-quality standard for PM₂.₅ currently in force in Brazil?"*

**Condition `public_manager_env`.** The identical question is prefaced by a fixed professional-role frame.

> Template (EN): *"As a municipal secretary of environment responsible for air-quality policy, I need an accurate answer for an official decision: {question stem}."*
> Example (BRA, T1): *"As a municipal secretary of environment responsible for air-quality policy, I need an accurate answer for an official decision: what is the annual ambient air-quality standard for PM₂.₅ currently in force in Brazil?"*
> Template (PT): *"Como secretário(a) municipal de meio ambiente responsável pela política de qualidade do ar, preciso de uma resposta precisa para uma decisão oficial: {question stem}."*

**Wording rules (fixed before lock).**
- The persona prefix is **identical across all tasks, countries, and languages** except for grammatical translation of the role and request frame. Only the `{question stem}` varies. This isolates the persona effect from question content.
- The persona frame does **not** contain the answer, a hint, or any country-specific cue beyond the role; it does not assert the requester's nationality.
- The native-language persona frame is produced by forward translation plus independent back-translation, with discrepancies adjudicated by a bilingual author, and is locked in the prompt registry before collection.

**Randomization.** For each (model, prompt) pair, the order in which `neutral` and `public_manager_env` are presented is randomized with the fixed run seed, so presentation order does not systematically coincide with condition.

**Manipulation check (mandatory).** Persona adherence is scored independently of accuracy. For each persona-condition response, the LLM-judge ensemble records a binary `persona_acknowledged` flag (does the response address the stated managerial/decision context, e.g., operational framing, actionability, or explicit reference to the requester's role?) using a fixed rubric in `code/analysis/persona_check.py`. The pre-registered check:
- **Pass criterion:** persona acknowledgement rate in the `public_manager_env` condition is materially higher than in `neutral` (pre-registered minimum absolute difference ≥ 0.20 pooled across models), confirming the manipulation took effect.
- **Primary H6 inference** is run on the manipulation-passed subset; the full-sample H6 result is reported as sensitivity. If the manipulation check fails pooled (difference < 0.20), H6 is reported as **uninterpretable as a persona test** and downgraded to exploratory, with the failure disclosed.

### 3.5 Ground-truth validation status

The taxonomy and ground truth were audited under Quality Gate SA-QG-003 (2026-06-05). Outcome: taxonomy structure PASS; ground-truth content corrected to a CONDITIONAL PASS after the following fixes, which are reflected in this pre-registration and in `data/ap_policy_pilot_bra_v2.jsonl`:

- **T1 (Brazil):** ground truth re-anchored to CONAMA 506/2024 / PI-2 (in force since 2025); the exact PI-2 numeric value is **[PENDING HUMAN VALIDATION]** (§3.2.1).
- **T2 (Brazil):** removed an obsolete reference to the prior interim standard; the single official value and reference station are **[PENDING HUMAN VALIDATION]** against the CETESB RQAR 2023 report.
- **T3 (Brazil):** two fabricated citations that appeared in an earlier ground-truth draft were removed. They are not used anywhere. The GBD 2019 health-burden figure is retained with a verifiable DOI; one to two **verified** Brazilian epidemiological references are **[PENDING HUMAN VALIDATION]** to replace the removed items, and must each carry a resolvable DOI/URL before entering the dataset (Citation Verification Protocol, §7.6).
- **T4 (Brazil):** PRONAR, PROCONVE, and PROMOT confirmed correct and verifiable; the rubric accepts the validated set of programmes.
- **T5 (Brazil):** an unsourced percentage for episode-driven PM reduction was removed; the criterion is kept qualitative.

These four pending items are tracked as Annex I human-validation tasks and must be closed before OSF lock. Any item still open at lock is either marked `[PENDING HUMAN VALIDATION]` in the deposited document or the corresponding (country, task) cell is dropped from confirmatory analysis.

### 3.6 Data contamination and cutoff protocol

LLM responses to AP policy prompts reflect a mix of recall of training content and generalization. Because models in scope have cutoffs spanning 2023–2025, the cutoff-aware design below is required, and is especially important for T1 given the 491/2018 → 506/2024 transition.

1. **Per-model cutoff documentation.** The training-data cutoff for each of the 14 models is recorded in `data/model_metadata.csv` before confirmatory collection (vendor model cards where available; corpus snapshot date for open-weight models).
2. **Regulatory-vintage handling for T1/T2.** For items where the binding standard or the reported official datum changed during the models' cutoff range (notably the Brazil PM₂.₅ standard), the ground truth credits the value in force at the time of collection, and a **vintage-aware sensitivity** scores models additionally against the standard in force at their own cutoff. This separates "outdated but internally consistent" answers from genuine errors.
3. **Post-cutoff sub-analysis (mandatory).** Prompts targeting facts dated after a model's cutoff are pre-identified per model; H1, H4, and H6 are repeated on this subset. Minimum threshold for inclusion: ≥ 5 post-cutoff prompts per model; models below this are dropped from the sub-analysis with the limitation reported.
4. **Prompt confidentiality before deposit.** The ~600 confirmatory prompts (both persona conditions) are not released publicly before confirmatory collection completes; they are held in a restricted-access OSF component to prevent inadvertent training-corpus inclusion during the collection window. Public release accompanies confirmatory data deposit.

### 3.7 Stopping rule

Collection proceeds to target n unless: (1) vendor model deprecation (drop the model, document deviation, re-run sensitivity excluding it); (2) budget depletion (triage favors retaining the persona contrast and the open-weight + regional comparison); (3) provider rate-limit/outage (switch to fallback venue per `code/benchmark/llm_clients.py`).

---

## Section 4 — Variables and Models

### 4.1 Manipulated (independent) variables

1. Country (15 levels; continuous covariates Joshi class, HDI, GDP per capita, internet penetration).
2. Model (14 levels; categorical Tier; continuous active-parameter count; cutoff year).
3. Task type (5: T1–T5; §3.2).
4. **Persona (2: neutral, public_manager_env; §3.4).**
5. Prompt language (sparse: English for all countries + one native language for stratified countries).

### 4.2 Outcome variables

**Per-component primary outcomes (5 components, each scored in [0,1]).**

| Component | Measurement |
|---|---|
| 1. Factual accuracy | Ground-truth match (binary T1; partial credit T2–T4 via judge ensemble; numeric tolerance T2) |
| 2. Contextual completeness | Judge-ensemble rubric 0–5, normalized to [0,1] |
| 3. Citation quality | URL/DOI verifiability + institution-name match |
| 4. Hallucination absence | Judge-ensemble flag (0 = hallucinated, 1 = faithful) |
| 5. Applied validity (T5) | Rubric score for operational recommendation, normalized to [0,1] |

**Composite outcome.** Weighted average. **Primary inference uses equal weights.** Two pre-registered sensitivity weightings: (i) PCA-derived weights estimated on the BRA extended-pilot data (to avoid within-confirmatory-sample double-dipping) and applied as fixed weights; (ii) author-specified weights (factual 0.30, contextual 0.25, citation 0.15, hallucination 0.15, applied 0.15). A primary conclusion is robust only if it holds across all three weightings.

**Persona acknowledgement (manipulation-check outcome).** Binary `persona_acknowledged` per persona-condition response (§3.4).

**Refusal rate (secondary outcome).** Per-country, per-model, per-persona proportion of explicit refusals. Refusals are excluded from accuracy scoring but reported as a distinct country-level outcome, to detect whether systematically higher refusal on Global South queries masks an accuracy gap, and whether persona changes refusal behavior.

### 4.3 Model sample — 14 models in 5 tiers

| Tier | Models | Execution |
|---|---|---|
| A — Open-weight frontier (5) | Llama 4 70B (Meta), Qwen 3 72B (Alibaba), DeepSeek-V3 671B MoE (DeepSeek), Mixtral 8×22B (Mistral), Command R+ 104B (Cohere) | Groq / OpenRouter / DeepInfra free + DeepSeek credits |
| B — Open-weight mid (3) | Gemma 3 27B (Google), Qwen 3 14B (Alibaba), Phi-4 14B (Microsoft) | Groq free + local Ollama |
| C — Open-weight small/regional (2) | Llama 3.1 8B (Meta; H3 scale-matched control), Cabra-Mistral 7B v3 (BR-PT; H3 regional) | Local Ollama |
| D — Closed accessible (2) | Gemini 2.5 Flash (Google), GPT-5-mini (OpenAI) | Free tier + OpenAI credits |
| E — Closed frontier (1) | GPT-5 (OpenAI) | OpenAI credits |
| Reserve (Appendix B) | Gemini 2.5 Pro (Google) | Not executed unless reviewer-requested |

> Model identifiers/tags are locked in `data/model_metadata.csv` before collection. Where a stated reference model (e.g., Cabra-Mistral 7B v3 GGUF) lacks a peer-reviewed model card, this is disclosed as a provenance trade-off accepted in favor of the open-weight requirement.

### 4.4 Country covariates

HDI 2024 and GDP per capita 2024 (PPP) from UNDP and World Bank; Joshi class (1–5) from Joshi et al. (2020); Wikipedia article counts and Common Crawl token operationalizations as in §1.4 (H4). All covariate values are frozen in `data/country_covariates.csv` before OSF lock. [CITATION NEEDED: exact UNDP HDR and World Bank vintages to lock per-country covariate values.]

### 4.5 Sample size and power

**Persona is paired and fully crossed**, which makes H6 the best-powered of the three co-primary tests: every prompt is answered under both persona conditions by the same model, so the DiD operates on within-pair differences.

| Hypothesis | Test | Threshold | Power (conservative) |
|---|---|---|---|
| H1 canonical (country-level Spearman, n=15) | one-sided correlation | ρ ≥ 0.55 | 0.65–0.72 |
| H4 canonical (partial Spearman, n=15) | one-sided correlation | ρ ≥ 0.55 | 0.61–0.68 |
| **H6 (country-level DiD, paired)** | one-sided + permutation | gap reduction ≥ 5 pp | **≥ 0.80** |
| H3 (Cabra vs Llama 3.1 8B, BR-PT) | one-sided contrast / BF | ρ-equiv / BF ≥ 10 | 0.85 |

**H6 power note.** Within-subject persona pairing across 15 countries × 14 models, with ~40 prompts/country answered under both personas and 2 reps, yields a large paired sample for the DiD. Under the BRA extended-pilot variance priors, the minimum detectable gap-reduction at α = 0.05 / power = 0.80 is approximately **2–3 pp absolute**, so the pre-registered 5 pp threshold is well powered. The full power simulation (10,000 Monte Carlo iterations under prior-informed effect sizes) is re-run for the v7 design and reported in the supplement, including family-wise power for the primary trio under Bonferroni-Holm.

**Honest disclosure.** H1 and H4 remain country-level tests at n=15 and are below the conventional 0.80 power floor; this is a structural limitation of country-level inference at this sample size. Effect sizes with 95% CI are the primary inferential output for H1/H4. H6 does not share this limitation because it is a paired within-subject contrast.

---

## Section 5 — Analysis Plan

### 5.1 Statistical models

**Primary paradigm.** Frequentist estimation-based inference: effect-size magnitude + 95% CI is the primary output (Cumming 2014; Lakens 2013). Decision thresholds (5 pp; SESOI) are interpretive aids, not primary cutoffs, except where a hypothesis is explicitly framed around a threshold (H6, where the 5 pp gap reduction is the pre-registered claim, reported alongside the CI).

**Secondary paradigm.** Bayesian GLMM via `bambi` for robustness; Bayes Factors for H3 with explicit prior + sensitivity.

**Singular-fit fallback.** If `lme4`/`pymer4` Laplace approximation yields singular variance components, fall back to Bayesian GLMM with weakly informative priors (HalfStudentT(3, 0, 0.1)) reported as primary and frequentist as sensitivity.

### 5.2 Per-hypothesis specifications

#### H1 (canonical primary: country-level Spearman)

For each component k and the composite:
```
country_mean_score_k = mean(score_k) over all (model, prompt, persona, rep) within country
Test: Spearman ρ(country_mean_score_k, joshi_class) ≥ 0.55, one-sided, α = 0.05
Test: Spearman ρ(country_mean_score_k, hdi)         ≥ 0.55, one-sided, α = 0.05
```
Mann-Kendall non-monotonicity check reported alongside each Spearman ρ. A response-level GLMM `score ~ 1 + (1|country) + (1|model) + (1|prompt)` is fitted for variance partitioning only (not a gradient test). Sensitivity: binary `global_south` Mann-Whitney U; HDI-quartile-stratified re-runs.

#### H4 (mechanism, primary: partial Spearman)

```
Wikipedia (primary): partial-Spearman ρ(country_mean_accuracy, log(wikipedia_articles) | hdi, log(gdp_pc)) ≥ 0.55, one-sided
CC-Op1/2/3 (secondary): partial-Spearman ρ(..., log(cc_tokens_op_k) | hdi, log(gdp_pc)) ≥ 0.40, one-sided
```
H4 supported if Wikipedia partial-ρ ≥ 0.55 AND ≥ 2 of 3 CC operationalizations ≥ 0.40 in the same direction. Conventional mediation (Sobel; SEM with bootstrap BCa) is reported in the supplement only, not as confirmatory. E-value reported per qualifying association (fragile < 1.5; moderate 1.5–2.0; robust ≥ 2.0). Reported as ecological partial correlation, not causal mediation.

#### H6 (persona effect, primary: difference-in-differences + permutation)

**Unit of analysis.** Country × model cell. **Outcome.** Composite accuracy per (country, model, persona) cell on the manipulation-passed subset.

**Point statistic.**
```
Δ_GS = mean(persona accuracy | Global South) − mean(neutral accuracy | Global South)
Δ_GN = mean(persona accuracy | Global North) − mean(neutral accuracy | Global North)
H6 statistic = Δ_GS − Δ_GN
```
**Primary inference.** Country-level **permutation test** for the DiD: 5,000 permutations of the Global-South/Global-North label across the 15 countries, recomputing Δ_GS − Δ_GN under each permutation to build the null distribution; one-sided p for gap reduction. A **paired t-test** on within-country persona differences (GS vs GN) is reported alongside as a parametric companion. H6 supported if Δ_GS − Δ_GN ≥ 0.05 with permutation p ≤ 0.05.

**Secondary.** Two-sided permutation p reported for transparency, so persona amplification (Δ_GS − Δ_GN < 0; Persona-Vacuum) is detectable and reported regardless of direction.

**Supporting GLMM (not the primary inference).** A response-level model with the persona × Global-South interaction is fitted for effect-size context:
```
score ~ persona * global_south + (1|country) + (1|model) + (1|prompt)
```
The interaction coefficient is reported with 95% CI; the confirmatory claim remains the country-level DiD permutation test.

**Robustness.** Per-task H6 (does persona help on recall tasks T1/T2 but not on open tasks T4/T5?) reported as a pre-specified secondary decomposition; persona × tier interaction reported descriptively.

#### H3 (regional model, secondary)

Subset: `country == "BRA"`, `language in {EN, PT}`, `model_id in {cabra-mistral-7b-v3, llama-3.1-8b}`.
```
score ~ model_id + language + persona + (1|prompt)
```
One-sided contrast `cabra > llama-3.1-8b` on the PT subset at α = 0.05, plus Bayes Factor (default Cauchy(0, 0.707); sensitivity Cauchy(0, 0.354), Normal(0, 1) reported separately). Exploratory companion: Lusophone-Africa displacement where ground truth exists.

#### H2, H5 (exploratory)

```
H2: score ~ joshi_class * is_native_language + (1|country) + (1|model)
H5: score ~ tier + tier:log10_active_params + tier:cutoff_year + tier:vendor_frontier + (1|country) + (1|model) + (1|prompt)
```
Reported descriptively; if formal tests are applied they enter F3 at BH q = 0.10.

### 5.3 Inference criteria and multiple-testing correction

- **Sidedness.** H1, H4, H6 are directional and tested one-sided at α = 0.05; two-sided reported as supplementary. H3 one-sided contrast + Bayes Factor.
- **Correction families.**
  - **F1 (primary confirmatory: H1, H4, H6).** **Bonferroni-Holm** across the primary tests. Within H1 and H4, the per-component/per-gradient tests are first combined to a single composite test for the family entry; the full per-component panel is reported with within-panel Bonferroni-Holm as supporting detail. H6 enters F1 as its single composite DiD test. Family-wise power for the H1/H4/H6 trio under Bonferroni-Holm is reported in the supplement under low/mid/high test-correlation scenarios.
  - **F2 (secondary confirmatory: H3).** Unadjusted within-family (single planned contrast + Bayesian companion).
  - **F3 (declared exploratory: H2, H5, persona × task, country × task, refusal-rate, per-vendor).** **Benjamini-Hochberg q = 0.10.**
- **Robustness rule.** A primary conclusion is reported as robust only if it survives the three composite weightings, the leave-one-out checks (§5.5), and, for H6, both the permutation and parametric tests and the manipulation-passed subset.

### 5.4 Multi-judge ensemble + external annotators

**Three independent LLM judges** (different vendor families): Judge A Claude Haiku 4.5 (Anthropic); Judge B GPT-5-mini (OpenAI); Judge C Gemini 2.5 Flash (Google). Primary score = mean across judges per response.

**Inter-rater reliability (Krippendorff α).** Target α ≥ 0.70. If α ∈ [0.55, 0.70): report with caveat and use confidence-weighted averaging. If α < 0.55: drop the task from primary, report as exploratory. Leave-one-judge-out sensitivity: re-run H1, H4, H6 dropping each judge; flag judge-dependent conclusions.

**Human gold subset.** A stratified subset (5 tasks × country quintiles × persona) is scored by external annotators recruited from Brazilian graduate programmes outside UTFPR/PPGSAU, plus one external adversarial annotator instructed to look for evidence against the Global South accuracy gap, plus one internal cross-validation annotator (not counted as blind). Annotators receive a neutral study title and do not see the terms "Global South", "geographic bias", or "persona effect". Model identities are anonymized via stylistic normalization only (preambles/markdown removed; URLs, numbers, and factual claims preserved verbatim) so that citation and applied-validity components remain measurable. Pairwise Cohen's κ is computed for cooperative-vs-cooperative, adversarial-vs-cooperative, internal-vs-cooperative, and LLM-ensemble-vs-cooperative, with the confirmation-bias signal rules and compensation/selection criteria as specified in the v6 protocol (carried forward unchanged).

### 5.5 Outlier handling, exclusions, sensitivity

Exclusions (pre-specified): API errors after 3 retries; empty responses (< 10 chars); truncated (`finish_reason=length` and content < 50 chars); judge parse failure on ≥ 2 of 3 judges. Refusals kept with a flag, excluded from accuracy scoring but reported as a country/persona-level outcome. If exclusion rate > 5% on any model, a sensitivity analysis is reported.

Sensitivity analyses: (1) leave-one-country-out; (2) leave-one-model-out; (3) leave-one-judge-out; (4) frequentist vs Bayesian GLMM; (5) bootstrap CIs (1,000 resamples, country-stratified); (6) objective-task subset (T1+T2) for a cleaner H1/H6 effect; (7) composite weighting comparison; (8) E-value per H4 association; (9) refusal-rate-corrected H1/H6; (10) continuous vs binary GS operationalization; (11) **H6 on full sample vs manipulation-passed subset**; (12) **H6 vintage-aware re-scoring for T1/T2**.

### 5.6 Pre-registration audit trail

Deviations are logged in OSF project comments with timestamp + git commit hash, reported in the manuscript supplement, and classified (pre-specified contingent / pilot-revealed / vendor-issue / other). Confirmatory status is retained if deviations affect ≤ 15% of planned cells; above 15%, the study is reported as exploratory.

---

## Section 6 — Exploratory Analyses (declared non-confirmatory)

1. H5 tier effect with scale-stratified decomposition (license × scale × cutoff × vendor).
2. H2 language × country interaction (sparse-design caveats).
3. **Persona × task interaction** (which task types are most persona-sensitive).
4. **Persona × tier interaction** (do larger/closed models respond more to the manager persona).
5. country × task-type interaction.
6. Per-vendor analysis.
7. Latency × accuracy tradeoff.
8. Refusal-rate × accuracy interaction, by persona.
9. Sensitivity to the operational definition of "Global South" (UNCTAD vs HDI < 0.7 vs Joshi class < 4).
10. Engagement with the live debate on "Global South" as a construct.

---

## Section 7 — Other

### 7.1 Deviation protocol

See §5.6.

### 7.2 Open data / code

- **Pre-deposit privacy.** The ~600 confirmatory prompts (both persona conditions) are not released publicly before confirmatory collection completes; held in a restricted-access OSF component until the collection window closes.
- **Public release accompanies confirmatory data deposit.** Raw responses, the three-judge scores, and the human gold subset (annotator identifiers anonymized) are deposited on Zenodo under CC-BY-4.0 within 60 days of confirmatory completion; analysis code on GitHub under MIT (prompts added at deposit time). The per-country AP-policy ground-truth registry (with official source links and DOIs) is released with the data.

### 7.3 Conflicts of interest

No financial relationships with any LLM vendor. The project receives compute credits from Anthropic, OpenAI, and DeepSeek, used solely to execute model inference. Vendors had no input into design, analysis, or interpretation. The reserve model (Appendix B) is selected from a vendor that does not provide compute credits to the project, to avoid optical bias.

### 7.4 Author contributions (CRediT)

- **Lucas Rover (UTFPR):** Conceptualization, Methodology, Software, Data Curation, Formal Analysis, Investigation, Visualization, Writing — Original Draft, Project Administration.
- **Dr. Eduardo Tadeu Bacalhau (UFPR):** Validation (incl. H6 DiD/permutation specification), Supervision, Writing — Review & Editing, Human Annotation (gold subset).
- **Dra. Yara de Souza Tadano (UTFPR):** Validation (incl. AP-policy task taxonomy and Brazilian air-quality ground truth), Supervision, Writing — Review & Editing, Funding Acquisition, Human Annotation (gold subset).

### 7.5 Engagement with related literature

- **Moayeri, Tabassi & Feizi (2024), WorldBench** — geographic disparity in factual recall on World Bank indicators; we extend to AP policy tasks with official ground truth. DOI 10.1145/3630106.3658967.
- **Manvi et al. (2024)** — geographic bias on subjective ratings; we extend to factual AP policy tasks. arXiv:2402.02680.
- **Mirza et al. (2024), Global-Liar** — Global North favoring in factuality over time/region. arXiv:2401.17839.
- **Myung et al. (2024), BLEnD** — non-monotonic language × resource interaction in everyday knowledge; informs H2 framing. NeurIPS 2024.
- **He et al. (2025)** — LLM policymaking shows context-blind rigidity and under-alignment with Global South experts; directly motivates H6. arXiv:2509.03827.
- **Opuszko & Böhm (2026)** — reasoning models reduce but do not eliminate geographic disparities. Springer.
- **Paiola et al. (2025)** — PT-BR medical benchmark; calls for EN-vs-PT comparison, informing H3. PMC.
- **Joshi et al. (2020)** — linguistic-resource stratification. ACL 2020, DOI 10.18653/v1/2020.acl-main.560.
- **VanderWeele & Ding (2017)** — E-value sensitivity for unmeasured confounding. Annals of Internal Medicine, DOI 10.7326/M16-2607.
- **Nosek et al. (2018)** — the preregistration revolution. PNAS, DOI 10.1073/pnas.1708274114.
- **GBD 2019 Risk Factors Collaborators (2020)** — health burden of PM₂.₅. The Lancet, DOI 10.1016/S0140-6736(20)30752-2.

### 7.6 Citation Verification Protocol (CVP / No Invention)

Every reference in any ground-truth gabarito, prompt, or this document must carry a resolvable DOI or URL verified before inclusion. Two fabricated citations were detected in an earlier T3 ground-truth draft and removed (§3.5); the CVP is now applied at the ground-truth generation stage, not only at manuscript stage, with an automated DOI/URL resolution check in the prompt pipeline. Any reference lacking a verified resolvable identifier is marked `[CITATION NEEDED]` and excluded until verified.

---

## Appendix A — Calibration pilots

1. **BRA extended pilot (v6 design):** 839 responses (2026-04-28), three-domain. Reclassified as extended pilot, excluded from v7 confirmatory inference; used for variance-component priors and prompt calibration (§3.1).
2. **AP-policy + persona pilot (v7 design):** `data/ap_policy_pilot_bra_v1.jsonl` (10 BRA prompts, 5 tasks × 2 personas), corrected to `ap_policy_pilot_bra_v2.jsonl` after Quality Gate SA-QG-003. Used to validate the persona manipulation, the ground-truth registry format, and the manipulation-check rubric. Not used for confirmatory inference. The four Annex I human-validation items (§3.5) close this pilot before OSF lock.

## Appendix B — Reserve model policy

Reserve model: **Gemini 2.5 Pro (Google)**, a frontier model from a non-budget-providing vendor, held in reserve and not executed in primary confirmatory collection. Activation only on explicit reviewer request; if activated, a 4-country × 25-prompt × 2-persona × 2-rep subset is run, reported regardless of direction, and logged as a pre-registered contingent analysis.

## Appendix C — Annex I: pending human-validation items (must close before OSF lock)

1. **T1 (BRA):** exact annual PM₂.₅ PI-2 value under Annex I of CONAMA 506/2024 — **[PENDING HUMAN VALIDATION]**.
2. **T2 (BRA):** single official annual PM₂.₅ value + reference station, CETESB RQAR 2023 — **[PENDING HUMAN VALIDATION]**.
3. **T3 (BRA):** 1–2 verified Brazilian epidemiological references (each with resolvable DOI/URL) to replace removed fabricated citations — **[PENDING HUMAN VALIDATION]**.
4. **T5 (BRA):** source for episode-driven PM-reduction magnitude, or confirm the criterion stays qualitative — **[PENDING HUMAN VALIDATION]**.
5. **Country covariates:** lock UNDP HDR and World Bank vintages and per-country HDI/GDP values — **[CITATION NEEDED]**.

---

> **End of pre-registration v7.** This document supersedes v6 (`osf_prereg_draft.md`) and is deposited at OSF prior to confirmatory data collection, after coauthor sign-off and closure of Annex I human-validation items.
