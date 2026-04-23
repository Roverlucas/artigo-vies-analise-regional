# Geographic Bias Across the LLM Ecosystem: A Multi-Country, Multi-Tier Audit for Global South Policy Research

**Research project in progress** — auditing geographic factual bias across the LLM tiers actually accessible to Global South researchers (regional, open, accessible-frontier, frontier-premium) and its consequences for applied policy research.

**Target journal:** *Patterns* (Cell Press, IF 7.4, Q1)
**Institution:** Programa de Pós-Graduação em Planejamento Urbano e Ambiental, UTFPR
**Status:** Design v2 locked (multi-tier audit, R$ 200 budget-aware); ready for pilot execution
**Canonical proposal:** [`docs/proposta_consolidada_v2.md`](docs/proposta_consolidada_v2.md)

---

## Research question

Across the LLM ecosystem actually accessible to Global South researchers — regional, open, accessible-frontier, and frontier-premium — where are the geographic gaps, and which tier best serves applied policy research?

## Hypotheses

- **H1:** Global South countries receive lower LLM accuracy on applied-research tasks than Global North countries (Cohen's *d* ≥ 0.5).
- **H2:** Prompt-language and country interact non-additively: native-language prompts help for high-resource languages and hurt for low-resource ones.
- **H3a/b:** Regional LLMs (Sabiá-3) either close the gap for their target country (H3a) or displace it onto other linguistically-related countries (H3b).
- **H4:** Training-corpus token representation (Common Crawl) correlates with country-level accuracy, mediating the Global South effect.

## Design summary (v2 — multi-tier audit)

- **15 countries** stratified along three theoretically-grounded axes (UNCTAD, Joshi et al. 2020, World Bank income groups).
- **6 LLMs across two tiers:**
  - **Tier A (accessible, 15-country full scope):** Claude Sonnet 4.6, Gemini 2.5 Pro, Llama 4 70B, Sabiá-3, Qwen 3 32B
  - **Tier B (frontier ceiling, 6-country subset):** Claude Opus 4.7
- **~600 prompts** in 3 domains (public policy, socioeconomic, environmental) × 5 task types, authored by a panel of 10+ Global South experts.
- **4+ languages** in a sparse factorial matrix.
- **Pre-registered SAP** with GLMM, Bayesian robustness, and mediation analysis.
- **Budget:** R$ 200 on-budget (Sabiá-3, Llama, Qwen) + existing Anthropic/Gemini credits off-budget.

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
| 5 | Empirical execution (v1 spec) | 🗃️ superseded | `docs/etapa5_proposta_execucao.md` |
| **5** | **Consolidated proposal (v2)** | ✅ | **`docs/proposta_consolidada_v2.md`** |
| 5.1 | Pilot Calibration Study | ⏳ next | `data/pilot_202604/` |
| 5.2 | OSF pre-registration | ⏳ | `preregistration/` |
| 5.3 | Confirmatory execution | ⏳ | `data/raw/llm_responses/` |
| 6 | Article writing | 🔄 draft v1 | `latex/main.tex` |
| 7 | Publication strategy | ⏳ | — |
| 8 | Language revision | ⏳ | — |
| 9 | Final formatting | ⏳ | — |
| 10 | Internal review board | ⏳ | — |

## Budget

- **On-budget API spend:** R$ 200 (Sabiá-3 via Maritaca + Llama 4 via Groq + Qwen 3 via Together)
- **Off-budget credits (existing):** Anthropic (Sonnet + Opus) + Google (Gemini 2.5 Pro)
- **Projected execution cost:** ~R$ 30 on-budget + ~R$ 525 off-budget equivalent
- **Buffer:** R$ 170 for contingencies (re-runs, extra models, expanded pilot)

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
