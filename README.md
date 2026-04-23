# Geographic Bias in LLMs: A Multi-Country, Multi-Language Benchmark for Policy Research

**Research project in progress** — investigating systematic geographic bias in Large Language Models and its consequences for applied policy research in the Global South.

**Target journal:** *Patterns* (Cell Press, IF 7.4, Q1)
**Institution:** Programa de Pós-Graduação em Planejamento Urbano e Ambiental, UTFPR
**Status:** Methodology locked, pre-registration ready, awaiting execution (Stage 5 of 10)

---

## Research question

Do LLMs exhibit systematic factual bias when supporting applied research about countries in the Global South — and if so, what role do (i) prompt language, (ii) regional model training, and (iii) training-corpus representation play in explaining the bias?

## Hypotheses

- **H1:** Global South countries receive lower LLM accuracy on applied-research tasks than Global North countries (Cohen's *d* ≥ 0.5).
- **H2:** Prompt-language and country interact non-additively: native-language prompts help for high-resource languages and hurt for low-resource ones.
- **H3a/b:** Regional LLMs (Sabiá-3) either close the gap for their target country (H3a) or displace it onto other linguistically-related countries (H3b).
- **H4:** Training-corpus token representation (Common Crawl) correlates with country-level accuracy, mediating the Global South effect.

## Design summary

- **15 countries** stratified along three theoretically-grounded axes (UNCTAD, Joshi et al. 2020, World Bank income groups).
- **6 LLMs** spanning frontier proprietary, open-source global, regional, and scale-matched control categories.
- **~450 prompts** in 3 domains (public policy, socioeconomic, environmental) × 5 task types, authored by a panel of 10+ Global South experts.
- **4+ languages** in a sparse factorial matrix.
- **Pre-registered SAP** with GLMM, Bayesian robustness, and mediation analysis.

## Repository structure

```
.
├── code/               # Analysis pipeline (Python, statsmodels, pymer4 path)
├── data/               # Prompts, ground truth, processed datasets
├── docs/               # Research documentation (stages 1-5)
├── figures/            # Publication figures
├── tables/             # Publication tables
├── results/            # Results prose + appendix
└── preregistration/    # OSF pre-registration materials
```

## Reproduction

```bash
git clone [repo-url]
cd artigo-vies-analise-regional
pip install -r code/requirements.txt
cd code && python run_all.py
```

Full pipeline validates in synthetic mode without API calls. Real execution requires API keys (see `code/benchmark/llm_clients.py`).

## Pipeline stages

| Stage | Description | Status | Document |
|---|---|---|---|
| 1 | Literature review | ✅ | `docs/etapa1_revisao_literatura.md` |
| 2 | Hypotheses | ✅ | `docs/etapa2_hipoteses.md` |
| 2b | Country stratification | ✅ | `docs/etapa2b_selecao_paises.md` |
| 3 | Methodological design | ✅ | `docs/etapa3_metodologia.md` |
| 4 | Statistical Analysis Plan | ✅ | `docs/etapa4_sap.md` |
| 5 | Empirical execution | 🔄 | `docs/etapa5_proposta_execucao.md` |
| 6 | Article writing | ⏳ | — |
| 7 | Publication strategy | ⏳ | — |
| 8 | Language revision | ⏳ | — |
| 9 | Final formatting | ⏳ | — |
| 10 | Internal review board | ⏳ | — |

## Licensing

- **Code** (`code/`): MIT License
- **Documentation, data, prompts, figures**: Creative Commons Attribution 4.0 International (CC-BY-4.0)

## Data provenance and ethics

- All ground truth from official government sources, public domain or openly licensed.
- Expert panel consented via Plataforma Brasil (CEP-UTFPR).
- No personal data collected.
- API terms of service respected; responses redistributed for research reproducibility only.

## Contact

Lucas [surname] — PPGSAU/UTFPR — [contact]
Supervisor: Prof. Dra. Yara Tadano

## Citation

To be added on first preprint deposit.
