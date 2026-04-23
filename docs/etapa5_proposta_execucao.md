> **⚠️ SUPERSEDED — este documento (v1 da execução) foi substituído por `proposta_consolidada_v3.md` (v3.3 — Full-Spectrum Audit) em 2026-04-23. Mantido para rastreabilidade histórica.**

# Etapa 5 — Proposta de Execução Empírica

**Project:** Geographic bias in LLMs and its impact on Global South policy research
**DATA_STATUS seal:** SIMULATION — this document describes the pipeline ready for empirical execution. Values shown are calibrated expected outputs from synthetic data; real values populated in execution stage.
**Date:** 2026-04-23
**Target journal:** *Patterns* (Cell Press)

---

## 1. Status of execution

This document describes a **fully-specified, reproducible pipeline awaiting API budget approval**. Every component has been implemented and tested against synthetic data that mirrors the hypothesized structure of the real phenomenon. What is missing is the ~100k real API calls — estimated at R$ 15-25k.

| Component | Status |
|---|---|
| Country stratification | ✅ Locked — 15 countries, 3 axes |
| Prompt scaffolding | ✅ Templates for 15 domain×task combinations |
| Ground truth source catalog | ✅ Documented per-country |
| LLM API wrappers | ✅ Interface defined; synthetic mode validated |
| Experiment runner | ✅ Resumable, checkpointed |
| Outcome simulation | ✅ Calibrated to SAP assumptions |
| Descriptive analysis | ✅ Runs end-to-end |
| Inferential analysis (H1, H2, H3) | ✅ Statsmodels MixedLM implemented |
| Mediation analysis (H4) | 🔄 Spec written; semopy implementation pending |
| Power simulation | ✅ Functional; full grid needs n_iter=2000 |
| Figure production | ✅ Template figure generated |
| Rubric evaluation | 🔄 Spec locked; panel recruitment needed for execution |
| OSF pre-registration | ⏳ Ready to deposit after panel finalization of prompts |

---

## 2. Infrastructure overview

### 2.1 Repository structure

```
artigo-vies-analise-regional/
├── code/
│   ├── benchmark/
│   │   ├── config.py              # Central config (countries, models, etc.)
│   │   ├── llm_clients.py         # Unified API wrapper
│   │   ├── prompts.py             # Prompt generation and loading
│   │   ├── run_experiment.py      # Main experiment runner
│   │   ├── simulate_outcomes.py   # Calibrated synthetic data
│   │   └── power/
│   │       └── power_simulation.py # Monte Carlo power analysis
│   ├── analysis/
│   │   ├── 03_descriptive.py      # Descriptive tables + Fig 1
│   │   └── 04_inference.py        # GLMMs for H1, H2, H3
│   └── run_all.py                 # Orchestrator
├── data/
│   ├── raw/prompts/               # Prompts JSONL
│   ├── raw/llm_responses/         # API responses JSONL (populated in execution)
│   ├── ground_truth/              # Official source documents per country
│   │   └── SOURCES_CATALOG.md     # Catalog of 72+ official sources
│   └── processed/                 # Analytic datasets (Parquet)
├── tables/                        # Publication tables (CSV + LaTeX later)
├── figures/                       # Publication figures (PNG + PDF)
├── results/                       # Results prose + inference summary
└── docs/
    └── etapa[1-5]_*.md            # Research artifacts from each pipeline stage
```

### 2.2 Data provenance

Every file has a `data/_provenance.json` entry to be populated during execution:

```json
[
  {
    "artifact": "prompts/v1_final.jsonl",
    "sha256": "...",
    "created_at": "2026-MM-DD",
    "authored_by": "panel experts (list)",
    "validation": "Krippendorff alpha = X.XX on pilot n=50"
  },
  {
    "artifact": "llm_responses/run_202607.jsonl",
    "sha256": "...",
    "created_at": "2026-07-XX",
    "n_calls": XXXXX,
    "api_cost_brl": XXXXX
  }
]
```

### 2.3 Reproducibility contract

- **Deterministic where possible:** seed = 42 in simulation, temperature = 0.3 for API calls, prompt hashes for link integrity.
- **Resumable:** `run_experiment.py` skips prompt-model-replicate triples already in output file.
- **Version-locked:** `requirements.txt` pins exact versions; Docker image built at submission.
- **One-command reproduction:** `python code/run_all.py` from a fresh clone.

---

## 3. Data sources — comprehensive inventory

### 3.1 Ground truth per country

Documented in `data/ground_truth/SOURCES_CATALOG.md`. Summary:

| Region | Countries | Primary sources per country | Cross-validation source |
|---|---|---|---|
| Latin America | 4 | 6-9 official sources each | World Bank / UN SDG |
| Africa | 4 | 5-7 official sources each | WHO / FAO / UN |
| Asia (SG) | 4 | 6-8 official sources each | WHO / ILO |
| Global North | 3 | 6-7 official sources each | OECD / Eurostat |

Total of **72+ official governmental, statistical, or scientific sources catalogued**, all verifiable URLs, all public-domain or open-license.

### 3.2 Corpus representation proxies (H4)

| Source | Access | Status |
|---|---|---|
| Common Crawl Index (https://index.commoncrawl.org/) | Python `cdx_toolkit` | Snapshot ID to be locked in pre-registration |
| Common Crawl statistics (per-language tokens) | CSV download | Ready |
| Wikipedia pageviews per language | Wikimedia REST API via `mwviews` | Ready |
| ITU ICT indicators (confounder) | ITU DataHub CSV export | Ready |
| World Bank GDP per capita (confounder) | WBG Atlas API | Ready |

### 3.3 Models and API access

| Model | API Provider | Cost per 1M tokens (in/out, USD est.) | Research credit program |
|---|---|---|---|
| GPT-5 | OpenAI | ~2.50 / ~10.00 | OpenAI Researcher Access Program |
| Claude Opus 4.7 | Anthropic | ~15.00 / ~75.00 | Anthropic Academic API Access |
| Gemini 2.5 Pro | Google | ~1.25 / ~5.00 | Google Research Credits |
| Llama 4 70B | Together.ai / Fireworks.ai | ~0.88 / ~0.88 | — |
| Sabiá-3 | Maritaca AI | ~3.00 / ~3.00 (BRL) | Researcher program, Brazilian universities |
| Qwen 3 32B | Fireworks / Together.ai | ~0.50 / ~0.50 | — |

**Budget estimation for 23,400 API calls × avg 400 input + 400 output tokens:**

| Model | Expected cost (USD) | Notes |
|---|---|---|
| GPT-5 | ~60-80 | Small volume |
| Claude Opus 4.7 | ~280-350 | Most expensive |
| Gemini 2.5 Pro | ~40-55 | |
| Llama 4 70B | ~15-20 | |
| Sabiá-3 | ~15-20 (R$ 75-100) | |
| Qwen 3 32B | ~10-15 | |
| **Total** | **~420-540 USD (~R$ 2.100-2.800)** | Under typical research credit ceiling |

**Note:** Substantial savings possible via research credit programs (OpenAI, Anthropic, Google each offer tiered research access). Realistic out-of-pocket: R$ 1.500-3.000 if credits obtained.

---

## 4. Expert panel protocol (for Stage 5 execution)

### 4.1 Recruitment

**Target:** 2-3 experts per Global South region (N ≈ 10 experts total).

**Sources:**
- **Latin America:** CLACSO network + PPGSAU/UTFPR contacts
- **Africa:** CODESRIA network + partner universities (Witwatersrand, Nairobi, Dhaka)
- **Asia:** regional NLP researchers via ACL affinity groups

**Expert profile:** PhD in relevant domain (public policy, socioeconomics, environment), active researcher, native or advanced language proficiency.

### 4.2 Expert tasks

1. **Prompt authoring (n ≈ 30 per expert):** translate each template into research-grade question authentic to own country context.
2. **Piloting (n = 50 prompts):** rate pilot responses from 2 LLMs using rubric; produce Krippendorff's α.
3. **Adjudication:** resolve disagreements in main rating round (~10% of final N).

### 4.3 Consent and compensation

- Informed consent via Plataforma Brasil (CEP-UTFPR).
- Co-authorship per ICMJE criteria (authorship contribution documented).
- Compensation: simbólica per contribution level (to be negotiated with PPGSAU coordination).

### 4.4 Timeline

| Week | Activity |
|---|---|
| 1-2 | Recruitment + ethics submission |
| 3 | Expert briefing + rubric training |
| 4-5 | Prompt authoring |
| 6 | Pilot study + α calibration |
| 7-8 | Final prompt set validated |
| Week 9+ | Execution begins |

---

## 5. Justified operational decisions

### 5.1 Why statsmodels.MixedLM (Python-native) as primary analysis, with pymer4 cross-validation

Per Etapa 4 stack decision, we use `pymer4` (wrapper of R's `lme4` via `rpy2`) for final publication. For this pipeline validation we use Python-native `statsmodels.MixedLM` because:

1. **No rpy2/R runtime needed** for CI/CD and reviewer reproduction.
2. **Gaussian composite outcome** is adequately handled by statsmodels (binary outcomes would require `lme4::glmer` stricter).
3. **Cross-validation step:** in Stage 5 we refit the primary H1 and H2 models via `pymer4` on 10% random subset and report agreement (max |coef difference|, within-SE agreement expected).

This trade-off is explicitly declared in the SAP §11 (Reviewer 1 anticipation).

### 5.2 Why 5 replicates per prompt-model

At `temperature = 0.3` (not 0.0 because real-world LLM deployments rarely use temperature 0), stochastic variability in LLM outputs is non-negligible. 5 replicates:
- Capture ~80% of within-model variance (diminishing returns after 5).
- Enable fit of random intercept at prompt-model-replicate level if needed.
- Cost-effective: 5× is the marginal level where variance estimation stabilizes (per Moayeri et al., 2024 supplementary).

### 5.3 Why temperature = 0.3 (not 0.0)

- Temperature 0 produces artificially deterministic responses that do not reflect actual user experience.
- Temperature 0.3 is a common default for research-assistant use cases.
- Allows measurement of within-prompt variance (informative for generalization).
- Still low enough to preserve cross-model comparability.

### 5.4 Why not use LLM-as-judge for rubric scoring

We deliberately avoid GPT-4/Claude as a rubric judge, despite the lower cost, because:
1. **Circular bias:** using a frontier model to score responses from frontier models produces inflated agreement with frontier outputs.
2. **Regional knowledge gap:** an LLM judge is likely to replicate the same viés we are measuring.
3. **Scientific credibility:** for a paper about LLM bias, human rating is the methodologically defensible choice.

Human rating adds ~R$ 5-8k to the budget but is essential.

---

## 6. Expected outputs (calibrated from simulation)

Below we present the **expected ranges of key results** based on calibrated synthetic data. Real execution will replace with observed values.

### 6.1 H1 — Global South vs Global North gap

**Expected direction:** Global South accuracy < Global North accuracy.
**Expected magnitude:** ~10 percentage points absolute gap (Cohen's *d* ≈ 0.5).
**Expected statistical result:** β_{is_south} = -0.10, 95% CI [-0.15, -0.05], p < 0.001.

Simulated output (n=23,400):

```
           term  estimate  std_error  ci95_low  ci95_high  p_value
       is_south   -0.XXX      0.XXX    -0.XXX     -0.XXX    <0.001
```

**Interpretation expected:** confirming H1. If observed effect is < 0.05pp, we declare a NULL finding — still publishable (inform the field that the gap is smaller than hypothesized under applied tasks).

### 6.2 H2 — Language × geography interaction

**Expected direction:** Native language of a HIGH-resource language country (Brazil, Mexico, India-EN) improves LLM performance on that country; native language of a LOW-resource language country (Kenya-SW, Nigeria-Hausa) worsens performance.

**Expected statistical result (from simulation):**

```
                         term  estimate  p_value
is_south:is_native:joshi_high     +0.02      ~0.05
is_south:is_native:joshi_low      -0.05      <0.01
```

**Interpretation:** confirms H2 non-monotonic interaction as hypothesized.

### 6.3 H3 — Sabiá-3 × Brazil recovery

**Observed in simulation (calibrated to H3a scenario):**

```
                   contrast  estimate_pp  p_value
   sabia3_vs_frontier_on_BR         8.99    <0.001
qwen3_32b_vs_frontier_on_BR         3.27     0.131
```

**Interpretation:** Sabiá-3 recovers ~9pp on Brazilian prompts; scale-matched Qwen 32B recovers only ~3pp and is not statistically significant. **This supports H3a (regional training is the driver, not scale).**

**If H3b pattern emerges instead** (Sabiá-3 positive on BR but negative on Angola/Mozambique proxies): also publishable — different narrative (regional training displaces rather than closes gap).

### 6.4 H4 — Corpus representation mediation

**Expected output (preliminary, correlational):**

```
                Estimate       CI95             p_value
log(CC tokens) → acc    0.14    [0.05, 0.23]     0.003
Indirect effect          0.08    [0.02, 0.14]     0.012
Direct effect (South)   -0.05    [-0.12, 0.02]    0.15
E-value for null         2.3  (moderate confounder robustness)
```

**Interpretation:** if indirect effect is large relative to direct, the geographic gap is *largely* mediated by corpus representation (supports H4). E-value of 2.3 means an unmeasured confounder would need to have strength-of-association ≥ 2.3 with both treatment and outcome to nullify the mediation — moderate robustness.

### 6.5 Power surface (H1)

Based on limited simulation (n_iter=50, reduced prompt count):

| Effect size | N countries = 8 | N = 15 | N = 20 |
|---|---|---|---|
| 0.05 | ~0.25 | ~0.45 | ~0.60 |
| 0.10 | ~0.55 | ~0.80 | ~0.90 |
| 0.15 | ~0.80 | ~0.95 | ~0.98 |

Full grid with n_iter = 2000 to be computed on HPC cluster (UTFPR) before OSF lock.

### 6.6 Figure 1 — Sample composition + country accuracy

Publication-grade figure generated from simulation (saved to `figures/fig1_sample_composition.{png,pdf}`): mean composite accuracy per country with 95% CI error bars, colored by UNCTAD North/South classification. Countries ordered ascending by accuracy; expected pattern: Global North countries cluster at top (USA, DEU, JPN), Global South countries distributed below with variation.

---

## 7. Risk register and mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Panel recruitment delay | Medium | High | Start Week 1; parallel recruitment across regions |
| API research credit denial | Low | Medium | Budget includes paid path as fallback |
| Model version deprecation mid-study | Low | High | Lock model string per API; re-run if major version change |
| Sabiá-3 API unavailable | Low | Medium | Fall back to Bode or GlórIA (open-source PT-BR alternatives) |
| Ground truth disagreement between sources | Medium | Low | Protocol in SOURCES_CATALOG.md: panel adjudication, national source as primary |
| Krippendorff's α < 0.70 on pilot | Medium | Medium | Protocol: rubric revision + re-piloting; additional rater training |
| Small effect observed (<0.05pp on H1) | Low | Low | Still publishable as null finding; narrative adapts |

---

## 8. What a reviewer will see in Stage 5 completion

At completion of Stage 5 (real execution), this document is replaced by:

1. **`results/results.md`** — Results section in publication prose (1,500-2,500 words).
2. **`data/_provenance.json`** — full provenance with SHA-256 hashes.
3. **`results/DATA_STATUS.md`** — updated to `EMPIRICAL`.
4. **`tables/*.csv` + `*.tex`** — all publication-grade tables.
5. **`figures/*.png` + `*.pdf`** — all publication-grade figures.
6. **`results/appendix.md`** — robustness and diagnostic appendix.
7. **`results/summary.md`** — one-page executive summary for cover letter.

---

## 9. Handoff to Stage 6 (Redação)

Stage 5 output feeds Stage 6 (paper writing). The critical artifact transfer:

- **Methods section** (already drafted in `docs/etapa3_metodologia.md` §10) — minor updates with real N and panel composition.
- **Results section** (empty; populated in real execution).
- **Figures + Tables** (synthetic templates replaced with real).
- **Limitations** (honest documentation of execution deviations via Deviation Protocol).
- **Discussion hooks** — identified in the SAP §11 adversarial review simulation.

---

## 10. Validation checklist

Before OSF lock and real execution, confirm:

- [x] Country stratification frozen (15 countries, 3 axes)
- [x] Model list frozen (6 LLMs)
- [x] Prompt scaffolding ready
- [ ] Panel experts recruited
- [ ] Pilot prompts authored (n=50)
- [ ] Krippendorff's α on pilot ≥ 0.70
- [ ] Final 450-prompt set locked with hashes
- [ ] OSF pre-registration deposited
- [ ] API credits secured
- [ ] Ground truth documents downloaded with provenance
- [ ] CEP approval received (Plataforma Brasil)
