# Geographic Bias Across the LLM Spectrum: A Full-Spectrum Open-Weight Audit for Global South Policy Research

**Research project in progress** — the first Q1-targeted benchmark auditing geographic factual bias across the complete LLM spectrum, from 7B open-weight regional models to 671B MoE open frontier and closed SOTA, applied to 15 countries stratified along three theoretical axes.

**Target journal:** *Patterns* (Cell Press, IF 7.4, Q1)
**Institution:** Programa de Pós-Graduação em Planejamento Urbano e Ambiental, UTFPR
**Status:** Design v3.3 locked (14 models, 5 tiers, open-science-first); ready for pilot execution
**Canonical proposal:** [`docs/proposta_consolidada_v3.md`](docs/proposta_consolidada_v3.md)

---

## Research question

Across the full LLM spectrum — from 7B open-weight regional models to 671B MoE frontier open and closed SOTA — where are the geographic factual gaps in applied policy research about the Global South, and what roles do (i) model scale, (ii) prompt language, (iii) training openness, and (iv) corpus representation play in shaping bias?

## Hypotheses

- **H1:** Global South countries receive lower LLM accuracy on applied-research tasks than Global North countries (Cohen's *d* ≥ 0.5).
- **H2:** Prompt-language and country interact non-additively: native-language prompts help for high-resource languages and hurt for low-resource ones.
- **H3a/b:** A regional open-weight LLM (Lince-Mistral 7B, PUCRS) either closes the Portuguese-language gap (H3a) or displaces it onto other Lusophone contexts (H3b).
- **H4:** Training-corpus token representation (Common Crawl) correlates with country-level accuracy, mediating the Global South effect.
- **H5 (new in v3):** Open-weight frontier models (70B+) close the gap versus closed frontier (GPT-5) in applied factual tasks for the Global South.

## Design summary (v3.3 — full-spectrum audit)

- **15 countries** stratified along three theoretically-grounded axes (UNCTAD, Joshi et al. 2020, World Bank income groups).
- **14 LLMs across 5 tiers:**
  - **Tier A (open-weight frontier, full scope):** Llama 4 70B, Qwen 3 72B, DeepSeek-V3, Mixtral 8×22B, Command R+
  - **Tier B (open-weight mid, full scope):** Gemma 3 27B, Qwen 3 14B, Phi-4 14B
  - **Tier C (open-weight small/regional, full scope):** Llama 4 8B, Lince-Mistral 7B
  - **Tier D (closed accessible, full scope):** Gemini 2.5 Flash, GPT-5-mini
  - **Tier E (closed frontier SOTA, full scope):** GPT-5
  - **Reserve:** Claude Opus 4.7 (not executed unless reviewer requests)
- **780 prompts** in 3 domains (public policy, socioeconomic, environmental) × 5 task types, with sparse multilingual matrix (4+ languages).
- **Pre-registered SAP** with GLMM, Bayesian robustness, and mediation analysis.
- **Budget:** ~US$ 16 planned (OpenAI + DeepSeek) + free tiers + local Ollama; R$ 255 in strategic reserve for reviewer response.

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
| 5 | Empirical execution (v1) | 🗃️ superseded | `docs/etapa5_proposta_execucao.md` |
| 5 | Consolidated proposal (v2) | 🗃️ superseded | `docs/proposta_consolidada_v2.md` |
| **5** | **Consolidated proposal (v3.3)** | ✅ | **`docs/proposta_consolidada_v3.md`** |
| 5.1 | Pilot Calibration Study | ⏳ next | `data/pilot_202604/` |
| 5.2 | OSF pre-registration | ⏳ | `preregistration/` |
| 5.3 | Confirmatory execution (full-spectrum) | ⏳ | `data/raw/llm_responses/` |
| 6 | Article writing + 6-agent audit | 🔄 draft v1 | `latex/main.tex` |
| 7 | Publication strategy | ⏳ | — |
| 8 | Language revision | ⏳ | — |
| 9 | Final formatting | ⏳ | — |
| 10 | Internal review board | ⏳ | — |

## Budget (v3.3)

- **Planned API spend:** ~US$ 16 total (OpenAI US$ 14.82 for GPT-5 + GPT-5-mini; DeepSeek US$ 1.38)
- **Free tier execution:** Groq (Llama 4 70B, Mixtral, Gemma 3 27B), OpenRouter/DeepInfra (Qwen 3 72B), Cohere (Command R+), Gemini 2.5 Flash
- **Local execution:** Ollama on Apple M4 24GB (Qwen 3 14B, Phi-4, Llama 4 8B, Lince-Mistral)
- **Strategic reserve:** US$ 10 Anthropic (Opus 4.7 if reviewer requests) + R$ 200 cash + US$ 3 buffer ≈ **R$ 255** total reserve

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
