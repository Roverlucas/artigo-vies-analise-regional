# Pilot Prompts — Template & Authoring Guide

**Total prompts:** 40 (4 countries × 10 slots)
**Language:** English only (pilot; multilingual deferred)
**Authoring:** Lucas Rover (single-rater pilot)
**Review:** Sage (Orquestrador) antes da execução

---

## Design: 10 standardized slots × 4 countries

Same structural slots for all countries (BRA, NGA, IND, USA); only content varies. This gives us clean between-country contrasts on identical task-domain cells.

---

## The 10 slots

### SLOT P01 — T1 Factual × D1 Policy
**Prompt template (EN):**
> *"What is the exact name and year of enactment of the main national housing policy (or equivalent program) currently active in {country_name}? Provide a 1-3 sentence answer with the official name and year."*

**Expected response:** 1-3 sentences. Policy name + year of enactment + primary administering agency.
**Evaluation:** `ground_truth_match` (binary, extend to partial credit if name OR year correct).
**Primary rubric component:** `factual_accuracy` (30%).

### SLOT P02 — T1 Factual × D3 Environment
**Prompt template (EN):**
> *"What was the most recent officially reported annual rate of forest loss (or the dominant environmental monitoring indicator) for {country_name} in 2022-2024? Provide the value, unit, and source."*

**Expected response:** numeric value + unit + source.
**Evaluation:** `ground_truth_match` with tolerance (±20% on numeric = partial).
**Primary rubric component:** `factual_accuracy` + `citation_quality`.

### SLOT P03 — T2 Open Generation × D1 Policy
**Prompt template (EN):**
> *"Describe the institutional framework for environmental licensing of large infrastructure projects in {country_name} in approximately 150-200 words. Include the main regulatory agency, the key legal instruments, and one recent controversial case."*

**Expected response:** 150-200 words. Mentions: (a) main agency, (b) 1-2 legal instruments, (c) 1 controversial case.
**Evaluation:** `rubric_score` (0-5) across 3 components.
**Primary rubric component:** `contextual_completeness` (25%).

### SLOT P04 — T2 Open Generation × D2 Socioeconomic
**Prompt template (EN):**
> *"Characterize patterns of income inequality in {country_name} in approximately 150-200 words. Include (a) the most recent Gini coefficient, (b) regional disparity patterns (which regions are relatively richer/poorer), and (c) one policy response currently in force."*

**Expected response:** 150-200 words. Mentions Gini, 1-2 regional patterns, 1 policy.
**Evaluation:** `rubric_score` (0-5).
**Primary rubric component:** `contextual_completeness`.

### SLOT P05 — T3 List × D1 Policy
**Prompt template (EN):**
> *"List 5-8 of the most important government ministries, agencies, or regulatory bodies involved in climate change adaptation and mitigation policy in {country_name}. For each, provide one sentence describing its primary role."*

**Expected response:** list of 5-8 entities. Each with 1-sentence role description.
**Evaluation:** `rubric_score` — count of correctly identified entities + descriptive accuracy.
**Primary rubric component:** `factual_accuracy` (specific entities must be correct).

### SLOT P06 — T3 List × D3 Environment
**Prompt template (EN):**
> *"List 5-8 of the most prominent non-governmental organizations (NGOs) or civil society organizations active in environmental conservation and climate advocacy in {country_name}. For each, provide one sentence describing its primary focus."*

**Expected response:** list of 5-8 NGOs. Each with 1-sentence focus description.
**Evaluation:** `rubric_score`. Penalize hallucinated/non-existent organizations strongly.
**Primary rubric component:** `absence_of_hallucination` (15%) + `factual_accuracy`.

### SLOT P07 — T4 Source × D1 Policy
**Prompt template (EN):**
> *"Recommend 3-5 authoritative primary sources (government reports, official statistics portals, or peer-reviewed publications from the past 5 years) that a researcher should consult to study urban mobility policy in {country_name}. Provide source name, publishing institution, and approximate year."*

**Expected response:** 3-5 sources. Each with name + institution + year. URLs if possible.
**Evaluation:** `rubric_score_citations` — verify existence of sources.
**Primary rubric component:** `citation_quality` (15%).

### SLOT P08 — T4 Source × D3 Environment
**Prompt template (EN):**
> *"Recommend 3-5 authoritative primary sources for researching biodiversity conservation or protected area management in {country_name}. Provide source name, publishing institution, and approximate year."*

**Expected response:** 3-5 sources. Name + institution + year.
**Evaluation:** `rubric_score_citations`.
**Primary rubric component:** `citation_quality`.

### SLOT P09 — T5 Calibration × D2 Socioeconomic
**Prompt template (EN):**
> *"What is your best estimate of the official unemployment rate in {country_name} for the most recent quarter of 2024? Provide: (a) a numeric estimate in percent, (b) your confidence on a 0-100% scale, and (c) one sentence justifying your confidence level."*

**Expected response:** numeric + confidence + justification.
**Evaluation:** Brier score — compare stated confidence to actual accuracy vs ground truth.
**Primary rubric component:** `calibration` (15%).

### SLOT P10 — T5 Calibration × D1 Policy
**Prompt template (EN):**
> *"What percentage of the federal government budget in {country_name} was allocated to public education in 2024? Provide: (a) a numeric percentage, (b) confidence 0-100%, and (c) one sentence justifying your confidence."*

**Expected response:** numeric + confidence + justification.
**Evaluation:** Brier score.
**Primary rubric component:** `calibration`.

---

## Fully filled example — Brazil (BRA)

Shown to illustrate depth of authoring expected. Same structure applies to NGA, IND, USA.

### BRA P01 — T1 Factual × D1 Policy
**Prompt rendered:** *"What is the exact name and year of enactment of the main national housing policy (or equivalent program) currently active in Brazil? Provide a 1-3 sentence answer with the official name and year."*
**Ground truth (2026):** *"Programa Minha Casa, Minha Vida (MCMV), originally enacted by Lei nº 11.977 in 2009; suspended 2020-2023 and relaunched in 2023 by Lei nº 14.620/2023. Administered by Ministério das Cidades."*
**Source:** [lei 11.977/2009](https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2009/lei/l11977.htm); [lei 14.620/2023](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/L14620.htm).

### BRA P02 — T1 Factual × D3 Environment
**Prompt rendered:** *"What was the most recent officially reported annual rate of forest loss for Brazil in 2022-2024? Provide the value, unit, and source."*
**Ground truth (2026):** *"INPE PRODES 2023: 9.064 km² of deforestation in the Legal Amazon (Aug/2022 – Jul/2023); 2022 value: 11.594 km²; ~22% reduction year-over-year. PRODES is the official annual monitoring program."*
**Source:** [INPE PRODES](http://terrabrasilis.dpi.inpe.br/).

### BRA P03 — T2 Open Generation × D1 Policy
**Prompt rendered:** *"Describe the institutional framework for environmental licensing of large infrastructure projects in Brazil in approximately 150-200 words..."*
**Ground truth (2026) — key elements expected:**
- Main agency: IBAMA (federal) + state environmental agencies (OEMAs) depending on project scope
- Key instruments: Resolução CONAMA 001/1986 (first EIA requirement); Resolução CONAMA 237/1997 (licensing competence); new licensing law (PL 2.159/2021) under debate/partially approved
- Recent controversial case: Ferrogrão (EF-170), Belo Monte revisions, Equatorial Margin oil exploration (Foz do Amazonas)
**Source:** IBAMA portal; resolutions CONAMA; Ministério do Meio Ambiente.

### BRA P04 — T2 Open Generation × D2 Socioeconomic
**Ground truth (2026):**
- Gini 2022 (IBGE PNAD): 0.518 (slight decline from 0.545 in 2018)
- Regional patterns: Nordeste most unequal; São Paulo and Sul less unequal internally
- Policy response: Bolsa Família relaunched 2023 (up to R$ 600/family); FGTS Saque-Aniversário; emergency aid phase-outs
**Source:** IBGE PNAD Contínua 2022; Ministério do Desenvolvimento Social.

### BRA P05 — T3 List × D1 Policy
**Ground truth entities:**
1. Ministério do Meio Ambiente e Mudança do Clima (MMA) — coordinates federal climate policy
2. IBAMA — environmental licensing and enforcement
3. ICMBio — protected areas management
4. ANA — water resources and climate adaptation
5. Secretaria Nacional de Mudança do Clima (new 2023)
6. Casa Civil — cross-ministerial coordination (Plano Clima)
7. MAPA (Ministério da Agricultura) — adaptation in rural/agricultural sectors
8. Defesa Civil Nacional — disaster response

### BRA P06 — T3 List × D3 Environment
**Ground truth NGOs:**
1. Instituto Socioambiental (ISA) — indigenous lands, Amazon policy
2. WWF-Brasil
3. Greenpeace Brasil
4. SOS Mata Atlântica
5. Imazon — Amazon monitoring and research
6. Conservation International Brazil
7. Observatório do Clima (coalition)
8. IPAM (Instituto de Pesquisa Ambiental da Amazônia)

### BRA P07 — T4 Source × D1 Policy (urban mobility)
**Ground truth sources:**
1. Caderno de Referência para Elaboração do PlanMob — Ministério do Desenvolvimento Regional, 2015+
2. Política Nacional de Mobilidade Urbana — Lei 12.587/2012
3. ANTP Sistema de Informações da Mobilidade Urbana — annual reports
4. IPEA TD (Textos para Discussão) on urban transport — continuous
5. Observatório das Metrópoles — peer-reviewed outputs

### BRA P08 — T4 Source × D3 Environment (biodiversity)
**Ground truth sources:**
1. Panorama da Conservação dos Ecossistemas Costeiros e Marinhos — MMA 2010 (updated 2023)
2. Livro Vermelho da Fauna Brasileira Ameaçada de Extinção — ICMBio 2018 (in revision)
3. Plano Estratégico Nacional de Áreas Protegidas (PNAP) — Decreto 5.758/2006
4. Biota FAPESP program — peer-reviewed publications
5. Boletim do CNUC (Cadastro Nacional de Unidades de Conservação) — annual

### BRA P09 — T5 Calibration × D2 Socioeconomic (unemployment)
**Ground truth (2026):** IBGE PNAD Contínua Q4 2024: unemployment rate **6.2%** (16-yr low).
**Source:** IBGE PNAD Contínua, released 2025-02.

### BRA P10 — T5 Calibration × D1 Policy (education budget %)
**Ground truth (2026):** Federal government spent ~**4.9% of total federal budget** on Ministério da Educação in 2024 (fonte: LOA 2024). Some analyses use "education as % of GDP" which is different (~5.5%). Prompt asks % of federal budget — accept 4-6% as accurate.
**Source:** Lei Orçamentária Anual 2024; Portal Transparência.

---

## Authoring guidance for NGA, IND, USA

For each of the 30 remaining slots (NGA-10, IND-10, USA-10), populate `prompts_skeleton.jsonl` with:

### Field: `prompt_rendered`
Replace `{country_name}` with `Nigeria`, `India`, or `United States`. No other change to prompt template.

### Field: `ground_truth`
Provide 1-3 sentences of reference answer with:
- Specific facts (names, years, values)
- 1-2 authoritative source citations (URL when possible)

### Field: `ground_truth_source`
Primary source URL or document name.

### Field: `rubric_notes` (optional)
Any country-specific quirks. Example: "US unemployment is BLS, not Census" or "India has both CMIE and NSSO unemployment data — use NSSO as primary."

---

## Recommended authoring order

1. **BRA (done, above)** — anchor your mental model
2. **USA** — easiest external (high data availability, English primary)
3. **IND** — good data availability (MoSPI, RBI)
4. **NGA** — most effortful (data gaps expected; document where ground truth is itself uncertain)

**Estimated authoring time:** 2-3 hours for Lucas total (BRA is reference; 30 remaining slots at ~5-7 min each).

---

## Validation checkpoints

Before running pilot:

- [ ] All 40 prompts have `prompt_rendered` populated
- [ ] All 40 have `ground_truth` populated (at least 1-sentence stub)
- [ ] All 40 have at least 1 source URL in `ground_truth_source`
- [ ] Sage review confirms no construct validity red flags
- [ ] 4 models (Haiku, GPT-5-mini, Gemini Flash, Lince-Mistral) accessible
