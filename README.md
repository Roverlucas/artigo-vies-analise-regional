# Geographic and Linguistic Bias in LLMs for Air Pollution Policy

**A 25-Country, 14-Model, 4-Language, 5-Task Benchmark**

Pre-specified, factorial benchmark of geographic and persona-modulated bias in
large language models on **air pollution policy** tasks relevant to public
environmental management in the Global South, scored against official ground truth.

**Target journal:** *Government Information Quarterly* (Elsevier)
**Institution:** Programa de Pós-Graduação em Sustentabilidade Ambiental Urbana, UTFPR
**Status:** Ready for co-author review. Analysis complete and scored against
official registers. The analysis plan was fixed before data collection but never
deposited publicly, so the study claims no pre-registration and is reported as
**exploratory** throughout. Adapted to GIQ requirements: abstract within the
250-word limit, APA author-year citations, and a blinded version for double-blind
review. QA gate, method audit and consistency gate passing.
**Manuscript:** [`latex/main.tex`](latex/main.tex) → `latex/main.pdf` (66 pp,
`elsarticle [review]` double-spaced submission format)
**Supplementary:** [`latex/supplement.tex`](latex/supplement.tex) → `latex/supplement.pdf` (18 pp)
**Blinded:** regenerate with `python latex/build_blind.py` (checks for identifier leaks)

---

## Research question

Do LLMs serve Global South air pollution policy as reliably as they serve the
Global North; does the way a query is framed (persona) change the answer; and what
mechanism drives any gap?

## Hypotheses and headline findings

Ordered by strength of evidence, not by hypothesis number.

<!-- numbers:begin  (gerado por code/analysis/make_readme_numbers.py a partir de latex/numbers.tex — não editar à mão) -->
| # | Hypothesis | Finding | Evidence status |
|---|---|---|---|
| **H2** | Native-language prompting modulates accuracy | **-5.0 pp** (Wilcoxon p=5e-16, n=839 cells; mixed model with a random intercept per country p=6e-7; 8/9 countries negative, t-test p=0.002); Hindi -11.4, Spanish -4.5, Portuguese -4.2, all significant. Native prompts return a register-checkable value 62.5% of the time vs 71.9% in English (-9.4 pp, sign test p=9e-4; Hindi -39.5, Spanish -13.4, Portuguese +3.5) | **Principal finding.** Survives leave-one-out over countries and models, every task, every weighting, every scoring instrument (code -3.8, panel -8.6), and a back-translation census of all 90 native prompts |
| **H3** | Regional model narrows the gap | Cabra-Mistral 7B (a community 7B fine-tune) is the **weakest** of all 14 (δ=-0.48); it also trails its scale-matched peer Llama 3.1 8B on Portuguese-language Brazilian prompts (0.258 vs 0.313, n=20 each) | Supported (opposite of optimistic framing); the narrow pre-specified test is small and descriptive |
| **H1** (tier) | Global North/South gap (pre-specified sensitivity contrast) | Primary outcome, code verdict only (no judge): Global South returns the register value **+14.7 pp** less often (country bootstrap [+5.6,+23.9], permutation p=0.012). Composite: +5.0 pp (CI [+1.6,+8.4]; p=0.019); same size within the extension wave (+5.9), on the pre-specified 15 (+6.1) and with the four EU members as one unit (+5.5, p=0.029). Exploratory decomposition by task: on the binding national standard the raw odds ratio is 0.44 with country-level CI [0.18,1.05] (permutation p=0.062; conditional GLMM 0.32 [0.27,0.39]); absent on T5 | Supported as a difference between groups (country as the unit); per-task decomposition exploratory, intervals wide |
| **H1** (gradient) | Monotonic development gradient | ρ=0.36 with HDI (p=0.076; Fisher 95% CI [-0.04,+0.66]); ρ=0.08 at the pre-specified n=15; never reaches 0.55 in any leave-one-out or weighting | **Not supported.** The interval includes both zero and the pre-specified 0.55: neither established nor excluded |
| **H4** | Corpus representation is the mechanism | Between countries, neither channel separates from development (sitelinks ρ=+0.37, p=0.070; partial p=0.37). Within countries the response-level interaction is β=+0.031 (p=6e-10), but with standard errors clustered by country p=0.099, and the 25 country-level deficits correlate with coverage at ρ=-0.37 (p=0.069; partial HDI -0.16, p=0.44); language-corpus channel null (β=+0.004, p=0.41) | **Not established** once the country is the unit of inference; direction consistent with coverage; coverage-or-development open |
| **H5** | Open frontier closes the gap vs closed | Closed advantage **+12.8 pp** | Descriptive |
| **H6** | Persona narrows the gap | DiD **+0.5 pp** (permutation p=0.29); 90% country-bootstrap CI [-0.4,+1.6] pp, inside ±2 pp (TOST); persona main effect -0.62 pp (p=0.003) | Not supported; equivalent to no effect within 2 pp |
<!-- numbers:end -->

The design was **pre-specified for 15 countries** and extended **post hoc to 25**;
the primary family and the tier gap are reported alongside their 15-country values. The plan was never
deposited in a public registry, so we do **not** claim pre-registration.

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
- **8,244 scored cells** (6,573 English-prompt, 1,671 native-language) after collapsing
  repeated judge runs by their mean and removing the 56 Egyptian T1 cells that have no key.
- **Scoring:** each task gets the most reliable instrument it admits.
  - Where the answer is a number in an official register (T1, T2, T3), the verdict is
    computed **by code** against that register — no judge involved. Resolves 99.8% of
    T1 cells, 56.3% of T2 and 71.8% of T3. For the three countries with no national
    standard, code scores whether the answer says so (correct), asserts a value
    (fabricated) or declines.
  - The residual and all of T4 are scored by the **mean of a three-vendor panel**
    (Gemini 2.5 Pro, Claude Sonnet 4.6, DeepSeek-V3). Reliability on the 3,190 items
    that produce the effects: ICC(2,3)=0.79, single-judge ICC(2,1)=0.56, α=0.527.
  - T5 (open recommendation, no register value) retains the collection judge's
    scores. That judge was **not single**: GPT-5-mini for the 15 pre-specified
    countries and Claude Haiku 4.5 for the 10 extension countries (7 of the 10 Global
    North), so judge and tier were confounded in the judged scores — which is why T1
    moved to code (2026-09-21).
  - Registry versions (SHA-256 prefix): t1 `b0e5d9e132aab684` · t2 `703dcd8122f88448` · t3 `902de1bc6af893de` · t4 `77bca4679aedc93a`. The UK key (10→20, limit in force) and the Bangladesh key (15→35, 2022 Rules) were corrected on 2026-09-21 after external review; `run_all.py --confirmatory` prints the hashes it ran against.
  - Ground truth anchored to official primary sources (WHO AAQD v6.1, WHO GHO AIR_41,
    UNEP GAAPL Appendix 1, national gazettes); **no human-gold layer** (stated as a
    limitation).

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

**Authors (signature order) and affiliations** — as in [`latex/main.tex`](latex/main.tex):
1. **Lucas Rover** — Federal University of Technology — Paraná (UTFPR), Brazil — `lucasrover@alunos.utfpr.edu.br`
2. **Vitor de Melo Dominski** — Faculdade Descomplica, Brazil
3. **Prof. Anibal Tavares de Azevedo** — University of Campinas (Unicamp), Brazil
4. **Dr. Eduardo Tadeu Bacalhau** — Federal University of Paraná (UFPR), Brazil — `bacalhau@ufpr.br`
5. **Dra. Yara de Souza Tadano** — Federal University of Technology — Paraná (UTFPR), Brazil — `yaratadano@utfpr.edu.br`

CRediT contributions per author are in the manuscript under *Author contributions*.
Validation, supervision, and writing review are shared by Bacalhau (UFPR) and
Tadano (UTFPR). ORCID iDs for all five are in
[`CITATION.cff`](CITATION.cff); they must match the record in `meusdados.capes`
for the CAPES transformative agreements to apply.

> **Still to fill before submission:** contact e-mails for authors 2 and 3.

## Citation

To be added on first preprint deposit.

## Reproducing the analysis

```bash
python code/run_all.py --confirmatory
```

Runs the full chain from the committed artefacts: deterministic scoring against
the official registers, export of corrected scores, panel reliability, the freeze
of every effect, the robustness battery, and the two gates (headline-number
recomputation and the process-versus-manuscript method audit). The two steps that
spend API credit — the judge panel and the back-translation census — are excluded
by design; their outputs are committed and the pipeline consumes them.

Key scripts, in the order the pipeline calls them:

| script | what it does |
|---|---|
| `score_numeric.py` | compares a returned value with the authorised range, by code |
| `export_corrected_scores.py` | one substitution rule; duplicates resolved by mean |
| `panel_reliability_full.py` | ICC and alpha on the 3,190 items that produce the effects |
| `freeze_all_effects.py` | every published effect, as published versus as corrected |
| `robustness_h2.py` | adversarial attacks on the headline finding |
| `h2_faithful_subset.py` | headline finding restricted to verified-faithful translations |
| `h4_within_country.py` | mechanism test using within-country variation |
| `robustness_extra.py` | power on the nulls, tier taxonomy, permutation arbiter |
| `duplicate_policy.py` | sensitivity of every effect to the duplicate-response rule |
| `squad_audit.py` | independent review by models from other vendors |
