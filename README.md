# Geographic and Linguistic Bias in LLMs for Air Pollution Policy

**A 25-Country, 14-Model, 4-Language, 5-Task Benchmark**

Pre-specified, factorial benchmark of geographic and persona-modulated bias in
large language models on **air pollution policy** tasks relevant to public
environmental management in the Global South, scored against official ground truth.

**Target journal:** *Patterns* (Cell Press)
**Institution:** Programa de Pós-Graduação em Sustentabilidade Ambiental Urbana, UTFPR
**Status:** Confirmatory analysis complete (25 countries); manuscript + Supplementary
drafted; reproducible QA gate passing (59/59 headline numbers recomputed from raw data).
**Manuscript:** [`latex/main.tex`](latex/main.tex) → `latex/main.pdf` (29 pp)
**Supplementary:** [`latex/supplement.tex`](latex/supplement.tex) → `latex/supplement.pdf` (12 pp)

---

## Research question

Do LLMs serve Global South air pollution policy as reliably as they serve the
Global North; does the way a query is framed (persona) change the answer; and what
mechanism drives any gap?

## Hypotheses and headline findings

| # | Hypothesis | Finding | Evidence status |
|---|---|---|---|
| **H1** | Geographic gap (tier + development gradient) | Tier gap **+6.2 pp** (95% CI [+3.7, +8.6]); HDI gradient **ρ=0.51** (p=0.004) at n=25 | Supported; gradient below pre-registered 0.55 threshold |
| **H2** | Native-language prompting modulates accuracy | **−2.1 pp** overall (Hindi −7.8); the local language does not help and can hurt | Effect supported; mechanism descriptive (n=3 langs) |
| **H3** | Regional model narrows the gap | Cabra-Mistral 7B is the **weakest** of all (δ=−0.51) | Supported (opposite of optimistic framing) |
| **H4** | Corpus representation is the mechanism | Wikipedia-size proxy **null**; Wikidata sitelinks ρ=0.54 but attenuates with HDI (p=0.13) | Pre-registered proxy not supported; country-coverage **exploratory** |
| **H5** | Open frontier closes the gap vs closed | Closed advantage **+14.1 pp** | Descriptive |
| **H6** | Persona narrows the gap | DiD **+0.4 pp** (permutation p=0.26) | Not supported |

The design was **pre-registered for 15 countries** and extended **post registration
to 25**; every effect is reported alongside its pre-registered 15-country value.

## Design summary

- **25 countries** — 15 pre-registered (stratified along UNCTAD North/South, Joshi
  et al. 2020 linguistic-resource class, World Bank income) plus 10 post-registration
  extension (7 Global North references + 3 Global South native-pair countries).
- **14 LLMs across 5 access tiers**, evaluated *as served* through fixed access stacks
  (vendor API or pinned inference endpoint):
  - **Tier A (open-weight frontier):** Llama 4 Scout, Llama 3.3 70B, DeepSeek-V3, GPT-OSS 120B, Command R+
  - **Tier B (open-weight mid):** Qwen3 32B, Qwen3 14B, Phi-4 14B
  - **Tier C (open-weight small/regional):** Llama 3.1 8B, Cabra-Mistral 7B (BR-PT, H3)
  - **Tier D (closed accessible):** Claude Haiku 4.5, Gemini 2.5 Flash, GPT-5-mini
  - **Tier E (closed frontier):** GPT-5
- **One domain (air pollution policy)** × **5 task types** — T1 technical standard,
  T2 local measured datum, T3 health-evidence synthesis, T4 policy instruments,
  T5 applied recommendation.
- **2 persona conditions** (neutral vs public environmental manager) × **4 languages**
  (English + native Portuguese/Spanish/Hindi for 9 countries).
- **9,251 judge-scored responses** (7,580 English-prompt, 1,671 native-language).
- **Scoring:** LLM-as-judge with primary judge `gpt-5-mini-2025-08-07`, validated by a
  four-vendor reliability panel (GPT-5-mini, Claude Sonnet 4.6, Gemini 2.5 Pro,
  DeepSeek-V3; panel-mean ICC(2,4)=0.89). Ground truth anchored to official primary
  sources by documentary audit; **no human-gold layer** (stated as a limitation).

## Repository structure

```
.
├── code/
│   ├── benchmark/      # prompts, model registry (config.py), runners, clients
│   └── analysis/       # formal_tests.py, robust_tests.py, h4_corpus_mechanism.py,
│                       # make_supplement_tables.py, qa_reproduce_claims.py
├── latex/
│   ├── main.tex + sections/   # manuscript
│   ├── supplement.tex         # Supplementary Information
│   └── supplement/tables/     # auto-generated data-driven tables
├── data/
│   └── confirmatory_PRIVATE/  # raw scores/registry (git-ignored; released on publication)
├── docs/               # design rationale, supplement source, writing framework
├── figures/ tables/ results/ preregistration/
└── RESULTS_25.md       # canonical 15-vs-25 results summary
```

## Reproduction

```bash
git clone https://github.com/Roverlucas/artigo-vies-analise-regional.git
cd artigo-vies-analise-regional
pip install -r code/requirements.txt

# Confirmatory reproduction from committed judge scores:
#   re-runs formal + robust tests, regenerates Supplementary tables,
#   and runs the integrity QA gate (recomputes every headline number).
python3 code/run_all.py --confirmatory
```

> **Data availability.** The raw confirmatory artifacts live under
> `data/confirmatory_PRIVATE/` and are **git-ignored** pending release on
> publication. With those files present, `make_supplement_tables.py` regenerates
> every data-driven Supplementary table and `qa_reproduce_claims.py` verifies that
> each number in the manuscript and Supplementary matches the value recomputed from
> the raw scores (exit 0 = all reproduced).

## Reproducibility & integrity

- **`code/analysis/make_supplement_tables.py`** — regenerates all 7 data-driven
  Supplementary tables (roster, acquisition window, coverage, covariates, ground
  truth, native pairs) from the raw scores. No number is hand-entered.
- **`code/analysis/qa_reproduce_claims.py`** — integrity gate: recomputes 59
  headline numbers from raw data (and by re-running the analysis scripts) and
  asserts they match the paper. Exit 1 on any mismatch.
- **Acquisition window:** confirmatory collection ran 2026-04-26 → 2026-06-12 (UTC);
  per-provider windows and API-documentation links are in Supplementary Table S2.
- **Writing framework:** [`docs/FRAMEWORK_ESCRITA_NATCOMMS.md`](docs/FRAMEWORK_ESCRITA_NATCOMMS.md)
  — the academic-writing checklist distilled from the companion Nature Communications
  revision, applied to this manuscript.

## Licensing

- **Code** (`code/`): MIT License
- **Documentation, prompts, ground truth, figures:** Creative Commons Attribution 4.0 (CC-BY-4.0)

## Data provenance and ethics

- All T1/T2/T4 ground truth from official government or international sources, verified
  by documentary audit against the primary text (registry: Supplementary Table S7).
- No personal data from end-users were collected; only model outputs to public policy
  questions are analysed.
- LLM provider terms of service were reviewed and respected; responses are
  redistributed solely for research reproducibility.

## Contact

Corresponding author: **Lucas Rover** — UTFPR — `lucasrover@alunos.utfpr.edu.br`

**Authors (signature order) and affiliations:**
1. **Lucas Rover** — Federal University of Technology — Paraná (UTFPR), Brazil — `lucasrover@alunos.utfpr.edu.br`
2. **Dr. Eduardo Tadeu Bacalhau** — Federal University of Paraná (UFPR), Brazil — `bacalhau@ufpr.br`
3. **Dra. Yara de Souza Tadano** — Federal University of Technology — Paraná (UTFPR), Brazil — `yaratadano@utfpr.edu.br`

Validation, supervision, and writing review are shared by Dr. Eduardo Tadeu Bacalhau (UFPR) and Dra. Yara de Souza Tadano (UTFPR).

## Citation

To be added on first preprint deposit.
