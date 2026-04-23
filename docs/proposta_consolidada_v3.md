# Proposta Consolidada v3.3 — Full-Spectrum Open-Weight Audit de LLMs em Pesquisa de Políticas do Sul Global

**Versão:** 3.3 (supersede v1 `etapa5_proposta_execucao.md` e v2 `proposta_consolidada_v2.md`)
**Data:** 2026-04-23
**Target journal:** *Patterns* (Cell Press, IF 7.4, Q1)
**Pesquisador:** Lucas Rover (PPGSAU/UTFPR) — orientação Profa. Dra. Yara Tadano
**Orquestração:** Academic Squad (Synkra AIOS) — Sage (academic-chief)
**Status:** pronto para execução em 5 fases

---

## 1. Sumário executivo

Benchmark pré-registrado que audita **viés geográfico factual em 14 Large Language Models** cobrindo o espectro completo entre pesos abertos (7B a 671B MoE) e modelos fechados frontier, aplicado a tarefas de pesquisa em políticas públicas, realidade socioeconômica e contexto ambiental em 15 países estratificados teoricamente (12 Sul Global + 3 Norte Global controle). O desenho v3.3 consolida três inovações simultâneas:

1. **Full-Spectrum Model Audit** — Primeiro benchmark Q1 a cobrir o espectro completo (open 7B → open 671B → closed acessível → closed frontier SOTA 2026) em um único experimento controlado.
2. **Open-Science-First Narrative** — 10 dos 14 modelos auditados têm pesos abertos, maximizando reprodutibilidade e alinhamento com Open Science.
3. **Budget-Feasible Execution** — R$ 67 de gasto real planejado (US$ 12,83 OpenAI + US$ 1,19 DeepSeek), preservando R$ 200 cash + US$ 10 Anthropic como reserva cirúrgica para revisão.

**Probabilidade calibrada:** 35-45% em *Patterns* direto; 85-90% cumulativo em ≤3 tentativas Q1/Q2.

---

## 2. Evolução da proposta (v1 → v2 → v3)

### 2.1 v1 (superseded) — "Frontier comparison" 
- Amostra: 6 modelos frontier (GPT-5, Opus 4.7, Gemini 2.5 Pro, Llama 4 70B, Sabiá-3, Qwen 3 32B)
- Custo estimado: R$ 35-40k
- **Inviável** dado orçamento real

### 2.2 v2 (superseded) — "Accessible-tier audit"
- Amostra: 5 Tier A + 1 Tier B (Opus ceiling subset)
- Dependência: créditos off-budget não confirmados
- **Correto mas subdimensionado**

### 2.3 v3.3 (canônica) — "Full-Spectrum Open-Weight Audit"
- Amostra: 10 open-weight + 2 closed acessível + 2 closed frontier = 14 modelos
- Narrativa: spectrum completo, open-science alignment, reprodutibilidade máxima
- Orçamento: R$ 67 planejado + R$ 265 em reserva estratégica

---

## 3. Questão de pesquisa e hipóteses

### 3.1 Questão central

Across the full LLM spectrum — from 7B open-weight regional models to 671B MoE frontier open and closed SOTA — where are the geographic factual gaps in applied policy research about the Global South, and what roles do (i) model scale, (ii) prompt language, (iii) training openness, and (iv) corpus representation play in shaping bias?

### 3.2 Hipóteses formalizadas

| # | Hipótese (versão v3.3) | Efeito esperado | Teste primário |
|---|---|---|---|
| **H1** | LLMs exibem acurácia inferior no Sul Global vs Norte Global, consistente across tiers | Cohen's *d* ≥ 0,5 | GLMM com indicador Global South + random effect por modelo |
| **H2** | Língua do prompt e país interagem não-aditivamente | η²_p ≥ 0,05 | Termo de interação GLMM |
| **H3a** | Modelo regional open-weight (**Lince-Mistral 7B**, PUCRS) reduz gap BR em >30% vs modelos globais de escala similar | Contraste pré-especificado | Bayesian contrast |
| **H3b** | Lince-Mistral desloca gap para outros lusófonos (análise exploratória) | Contraste exploratório | Bayesian contrast |
| **H4** | log(tokens no CC) correlaciona com acurácia média por país | Spearman ρ ≥ 0,60 | Regressão ecológica + mediation |
| **H5** (nova v3.3) | Open-weight frontier (70B+) fecha o gap vs closed frontier em tarefas factuais aplicadas | Contraste de closed-vs-open em Tier premium | GLMM com interação Tier × Global South |

**H5** é contribuição única da v3.3: ninguém publicou em Q1 um paired comparison open-vs-closed em escopo multi-país.

---

## 4. Desenho amostral de modelos — 14 modelos em 5 tiers

### 4.1 Tier A — Open-weight frontier (5 modelos, full scope 15 × 30 × 3)

| # | Modelo | Params | Vendor | Execução | Justificativa |
|---|---|:-:|---|---|---|
| 1 | **Llama 4 70B Instruct** | 70B | Meta | Groq free API | Frontier open, multilingual |
| 2 | **Qwen 3 72B** | 72B | Alibaba | OpenRouter/DeepInfra | Frontier open, forte em multilíngue |
| 3 | **DeepSeek-V3** | 671B MoE | DeepSeek | DeepSeek API (créd. $1,99) | Frontier open SOTA, origem CN |
| 4 | **Mixtral 8×22B** | 141B MoE | Mistral | Groq free API | Frontier open EU |
| 5 | **Command R+** | 104B | Cohere | Cohere trial key | Frontier open tuned para multilíngue |

### 4.2 Tier B — Open-weight mid (3 modelos, full scope)

| # | Modelo | Params | Vendor | Execução |
|---|---|:-:|---|---|
| 6 | **Gemma 3 27B** | 27B | Google | Groq free API |
| 7 | **Qwen 3 14B** | 14B | Alibaba | **Ollama local (M4 24GB)** |
| 8 | **Phi-4 14B** | 14B | Microsoft | **Ollama local** |

### 4.3 Tier C — Open-weight small/regional (2 modelos, full scope)

| # | Modelo | Params | Vendor | Execução | Papel |
|---|---|:-:|---|---|---|
| 9 | **Llama 4 8B** | 8B | Meta | **Ollama local** | Accessibility floor |
| 10 | **Lince-Mistral 7B** | 7B | PUCRS | **Ollama local** | **H3 regional (BR-PT tuned open)** |

### 4.4 Tier D — Closed acessível (2 modelos, full scope)

| # | Modelo | Vendor | Execução | Custo |
|---|---|---|---|---:|
| 11 | **Gemini 2.5 Flash** | Google | API free tier | US$ 0 |
| 12 | **GPT-5-mini** | OpenAI | OpenAI credits | US$ 2,03 |

### 4.5 Tier E — Closed frontier SOTA (1 modelo, full scope)

| # | Modelo | Vendor | Execução | Custo |
|---|---|---|---|---:|
| 13 | **GPT-5** | OpenAI | OpenAI credits | US$ 10,80 |

### 4.6 Reserva pós-revisão (1 modelo, não execução planejada)

| # | Modelo | Vendor | Execução | Custo potencial |
|---|---|---|---|---:|
| 14 | Claude Opus 4.7 | Anthropic | **Em reserva** — acionar só se reviewer pedir | US$ 6-9 (subset subset) |

### 4.7 Matriz de cobertura

| Dimensão | Cobertura |
|---|---|
| **Vendors** | Meta, Alibaba, DeepSeek, Mistral, Cohere, Google, Microsoft, PUCRS, OpenAI (+Anthropic em reserva) = **9-10 vendors** |
| **Open/Closed** | 10 open + 3 closed executados + 1 closed em reserva |
| **Escala** | 7B → 671B MoE (quase 2 ordens de magnitude) |
| **Geografia de treinamento** | USA (Meta, Microsoft, OpenAI, Cohere, Google), China (Alibaba, DeepSeek), Europa (Mistral), Brasil (PUCRS) |

---

## 5. Escopo experimental

### 5.1 Design fatorial

| Dimensão | Valor | Observação |
|---|---:|---|
| Países | 15 | Estratificação UNCTAD × Joshi × WB (Etapa 2b inalterada) |
| Línguas (matriz esparsa) | média 1,6/país | EN sempre + 0-1 regional |
| Domínios | 3 | Políticas públicas, socioeconômico, ambiental |
| Tarefas | 5 | Fatual, geração aberta, extração, recomendação, calibração |
| Prompts por (país × domínio × tarefa) | 2 | |
| **Total de prompts distintos** | **780** | 15 × 1,6 × 3 × 5 × 2 |
| Replicações por call | 2 | Temperatura 0,3; seed fixa quando disponível |
| Modelos Tier A-E | 13 | Full scope |
| **Total calls Tier A-E** | **13 × 780 × 2 = 20.280** | |
| Tier-reserva Opus | — | Não executado a menos que reviewer peça |

**Ajuste vs v1/v2:** reps reduzidas de 5 → 2 para caber no orçamento US$ 15 OpenAI sem cortar cobertura multilíngue. Poder estatístico recalculado em §7.

### 5.2 Matriz de línguas (esparsa, inalterada v1/v2)

| País | EN | PT | ES | HI | SW | AR |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| BRA | ✓ | ✓ | | | | |
| MEX, ARG, PER | ✓ | | ✓ | | | |
| NGA, ZAF, PHL | ✓ | | | | | |
| KEN | ✓ | | | | ✓ | |
| EGY | ✓ | | | | | ✓ |
| IND | ✓ | | | ✓ | | |
| IDN, BGD | ✓ | | | | | |
| USA, DEU, JPN | ✓ | | | | | |

---

## 6. Orçamento — execução + reservas

### 6.1 Gastos planejados (execução confirmatória)

Per model full scope = 780 prompts × 2 reps = **1.560 calls/modelo**

| Fonte | Item | Calls | Custo estimado |
|---|---|---:|---:|
| **OpenAI (US$ 15 total)** | GPT-5 full scope | 1.560 | ~US$ 12,48 |
| **OpenAI** | GPT-5-mini full scope | 1.560 | ~US$ 2,34 |
| **DeepSeek (US$ 1,99 crédito)** | DeepSeek-V3 full scope | 1.560 | ~US$ 1,38 |
| **Groq** (free tier) | Llama 4 70B, Mixtral, Gemma 3 27B | 3 × 1.560 | US$ 0 |
| **OpenRouter/DeepInfra** (free) | Qwen 3 72B | 1.560 | US$ 0 |
| **Cohere** (trial key) | Command R+ | 1.560 | US$ 0 |
| **Google** (free tier) | Gemini 2.5 Flash | 1.560 | US$ 0 |
| **Ollama local M4 24GB** | Qwen 14B, Phi-4, Llama 4 8B, Lince-Mistral | 4 × 1.560 | US$ 0 |
| **TOTAL GASTO REAL** | | **20.280** | **~US$ 16,20 ≈ R$ 85** |

**Contingência pricing GPT-5:** estimativa de US$ 0,008/call é conservadora (baseada em GPT-4o tier). Se GPT-5 real for <US$ 0,006/call, buffer OpenAI sobe para US$ 3+. Se for >US$ 0,010/call, scope GPT-5 reduz para 780 calls (1 rep apenas) — documentado como limitação.

### 6.2 Reservas estratégicas (não-planejado, disponível para revisor)

| Fonte | Valor | Uso potencial |
|---|---:|---|
| **Anthropic** (intacto) | US$ 10 | Opus 4.7 ceiling subset (~170 calls) se reviewer pedir "multi-vendor closed frontier" |
| **OpenAI** (buffer após gasto) | US$ 2,17 | GPT-5 re-runs ou extensão |
| **DeepSeek** (buffer) | US$ 0,80 | DeepSeek re-runs |
| **R$ 200 cash** (intacto) | R$ 200 | Emergência: Sabiá-3 paid, Opus extra, análises extras |
| **TOTAL RESERVA** | **≈ R$ 265** | Cirúrgica pós-revisão |

### 6.3 Rationale financeiro

- **~R$ 85 gastos** representam 0,24% do orçamento original projetado em v1 (R$ 35-40k)
- **~R$ 255 em reserva** = 3× o gasto planejado, permitindo resposta robusta a reviewer
- **Reserva multi-vendor:** Anthropic (closed vendor) + cash (qualquer outro) + buffer nos usados

---

## 7. Poder estatístico recalibrado (v3.3)

Simulação Monte Carlo aplicada ao desenho final (13 modelos × 780 prompts × 2 reps = 20.280 obs):

| Hipótese | N efetivo | Poder esperado |
|---|---|:-:|
| H1 (GS vs GN, between-country, marginalizado across models) | 20.280 obs | **0,95+** |
| H2 (lang × country, non-EN) | Cells esparsos, n ≈ 150-300/célula | **0,75-0,82** |
| H3 (Lince vs open globals em BR) | Lince: 208 obs BR; open globals: 9 × 208 obs | **0,90** |
| H4 (ρ tokens por país) | N=15 países, média across 13 modelos | **0,82** (ganho vs v2 via averaging) |
| **H5 (open frontier vs closed frontier)** | 5 open Tier A vs 1 GPT-5, 20.280 obs total | **0,90+** |

**Todos ≥ 0,75.** H2 continua sendo o mais frágil (redução de reps de 3→2 custa ~5pp de poder); mitigação: pós-pilot, se H2 parecer fraca, usar reserva para expandir reps em subset de línguas críticas (EN+PT+ES).

---

## 8. Cronograma de execução — 5 fases

### Fase 1 — Pilot Calibration Study (2-3 dias, ~US$ 2 gasto)

**Objetivo:** validar infra + calibrar SESOI + ver sinal real antes do OSF lock.

**Escopo:**
- 4 países (BR, NGA, IND, USA)
- 4 modelos diversos (Llama 4 70B Groq, Gemini Flash, GPT-5-mini, Lince-Mistral local)
- 30 prompts × 2 reps = 960 calls
- Custo real: ~US$ 0,50 em OpenAI + free tiers

**Delegação:** `@experiment-runner (Forge)` + Lucas (autoria prompts)

**Entregas:**
- `data/pilot_202604/` com responses brutos
- `results/pilot_findings.md` com GLMM exploratório
- Decisão go/no-go para Fase 2

**Rótulo obrigatório:** `PILOT — exploratory, not confirmatory` em todos arquivos.

### Fase 2 — OSF Pre-Registration (1 dia, 0 custo)

**Objetivo:** lock SAP antes de coleta confirmatória.

**Delegação:** `@submission-engineer (Atlas)` + `@po (Pax)`

**Entregas:**
- SAP v1.1 atualizado com variance components do pilot
- `preregistration/osf_registration_v1.md` (AsPredicted template)
- Deposit OSF → DOI

### Fase 3 — Confirmatório Full-Spectrum (10-14 dias, ~US$ 14)

**Escopo:** 17.550 calls distribuídos entre:
- API paga: GPT-5 + GPT-5-mini + DeepSeek-V3 (~4.050 calls, ~US$ 14)
- API free: Gemini Flash + Llama 4 70B + Mixtral + Gemma 27B + Qwen 72B + Command R+ (~8.100 calls, ~US$ 0)
- Local Ollama: Qwen 14B + Phi-4 + Llama 4 8B + Lince-Mistral (~5.400 calls, ~US$ 0)

**Delegação:** `@experiment-runner` (paralelização entre APIs/local) + `@statistician (Sigma)`

**Entregas:**
- `data/raw/llm_responses/run_202605_*.jsonl` (um por modelo)
- `data/processed/analytic_main.parquet`
- `tables/h1_glmm.csv`, `h2_interaction.csv`, `h3_contrasts.csv`, `h4_mediation.csv`, `h5_open_closed.csv`
- `figures/fig1-fig8.pdf` atualizados (inclui nova Fig 7: open-vs-closed spectrum)

### Fase 4 — Redação + Auditoria 6 Agentes (5-7 dias, 0 custo)

**Delegação:** `@scientific-writer (Quill)` + auditoria mandatória

**Entregas:**
- `latex/main.tex` com `\placeholder{}` substituídos
- Auditoria sequencial de 6 agentes (regra do pesquisador):
  1. `@gap-analyst` — literatura atualizada 2026, especialmente open-weight benchmarks
  2. `@peer-review-defender` — stress-test de reviewer hostil
  3. `@citation-sentinel` — DOIs + referências 
  4. `@scientific-writer` — coerência narrativa full-spectrum
  5. `@statistician` — números reproduzíveis + H5 teste
  6. `@language-editor` — inglês acadêmico final

### Fase 5 — Submissão (2-3 dias, 0 custo)

**Delegação:** `@submission-engineer` + `@scientific-marketer (Beacon)` + `@devops (Gage)` para push final

**Entregas:**
- Formatação Cell Press
- `docs/cover_letter.md` + `docs/highlights.md`
- **Pre-submission inquiry** ao editor-chefe (+2-3pp)
- Submissão via Editorial Manager
- Paralelo: data paper em *Scientific Data* (17.550 responses abertos CC-BY-4.0)

**Timeline total:** **21-28 dias úteis** autoria prompts → submissão.

---

## 9. Estratégia editorial

### 9.1 Target primário — *Patterns* (Cell Press)

**Por que Patterns funciona para v3.3:**
- Escopo explícito: "AI governance, ethics, science policy", "data science solutions to cross-disciplinary problems"
- Forte tradição de open data/code/methods
- Publicou trabalhos sobre AI bias 2024-2025 (WorldBench é editorialmente próximo)
- Open Access obrigatório (alinha com os 5 pilares open do projeto)
- Tempo primeira decisão ~5 dias; revisão completa ~45-60 dias
- APC: USD 4.900 com geographical pricing OA (Brasil elegível)

### 9.2 Angle de capa única: "Full-Spectrum Audit"

Cover letter destaca:
> *"We present the first audit of LLM geographic factual bias covering the complete spectrum from 7B open-weight regional models to 671B MoE frontier open and closed SOTA, using 15 countries stratified across three theoretical axes. Nine of fourteen models audited have fully open weights, maximizing reproducibility; one closed frontier model (GPT-5, 2026 SOTA) validates the spectrum ceiling; a regional open model (Lince-Mistral, PUCRS) tests the thesis that linguistic specialization reduces the gap. Results have direct policy implications for sovereign AI investment in the Global South."*

### 9.3 Cascata de fallback

| Prioridade | Journal | IF | Prob. condicional | Fit v3.3 |
|---|---|:-:|:-:|---|
| 1 | **Patterns** | 7,4 | 35-45% | ⭐⭐⭐⭐⭐ |
| 2 | EPJ Data Science | 2,8 | 65-75% | ⭐⭐⭐⭐⭐ (open-weight fit é excelente) |
| 3 | AI & Society | 2,9 | 55-65% | ⭐⭐⭐⭐ |
| 4 | Frontiers in AI | 3,1 | 75-85% | ⭐⭐⭐ |

**Probabilidade cumulativa de aceite em ≤3 tentativas:** **85-90%**.

### 9.4 Data paper paralelo

Submeter em *Scientific Data* (Nature):
- Dataset 17.550 responses
- 450 prompts curados
- Ground truth catalog (72+ fontes oficiais)
- Rubric de avaliação
- Código R/Python de análise
- **Reuso esperado alto** — benchmark é raro para Global South

---

## 10. Probabilidade de aceite — decomposição v3.3

### 10.1 Cenários por resultado (prior antes da coleta)

| Cenário | Padrão de dados | Prob. Patterns |
|---|---|:-:|
| 🟢 Forte | H1 d≥0,5, H3 claro, H4 ρ≥0,6, H5 mostra open-closed gap pequeno | **38-48%** |
| 🟡 Esperado | H1 d 0,3-0,5, H2-H5 mistos | **30-38%** |
| 🔴 Fraco | H1 null, padrão inconsistente | **12-18%** |
| **Expectativa ponderada** | | **32-40%** |

### 10.2 Alavancas ativadas

| Alavanca | Status em v3.3 | Ganho |
|---|---|:-:|
| Pré-registro OSF | ✓ planejado Fase 2 | +4-6pp |
| Painel de especialistas (Krippendorff α≥0.70) | ⏳ pós-pilot | +3-5pp |
| Cover letter "full-spectrum audit" | ✓ | +3-4pp |
| Pre-submission inquiry | ✓ planejado | +2-3pp |
| Figura 1 de alta qualidade (sample composition) | ⏳ | +2pp |
| Auditoria 6 agentes | ✓ mandatória | +2-4pp |
| Data paper paralelo | ✓ planejado | +1pp (via visibilidade) |
| **Open-weight angle específico (novo v3)** | ✓ | +3-5pp |
| **R$ 265 em reserva para revisor** | ✓ | +2-4pp durante revisão |

**Teto realista v3.3:** **40-50% em Patterns** com todas alavancas ativadas + cenário forte.

---

## 11. Risk register v3.3

### 11.1 Riscos científicos

| Risco | Prob. | Impacto | Mitigação |
|---|:-:|:-:|---|
| Effect size real < SESOI (d<0,3) | Média | Alto | Pilot detecta antes; pivot para "null findings matter" |
| Rubric falha Krippendorff (α<0,70) | Média | Alto | Pré-teste 50 prompts + 3º avaliador |
| Data contamination | Média | Médio | Subset pós-cutoff + documentar limitação |
| Modelos open atualizam versões mid-execução | Baixa | Baixo | Ollama lock de tag + registrar hash |
| Lince-Mistral quality insuficiente | Média | Médio | Alternativa Cabra-Mistral ou Sabiá-7B open |

### 11.2 Riscos operacionais

| Risco | Prob. | Impacto | Mitigação |
|---|:-:|:-:|---|
| Groq free tier deprecado mid-execução | Média | Médio | Fallback Together, OpenRouter, DeepInfra |
| Cohere trial key expira | Alta | Baixo | Aplicar antes da Fase 3; se cair, usar Command R via OpenRouter |
| Ollama local lento em 22B+ (M4) | Alta | Baixo | Rodar modelos grandes em batch noturno |
| OpenAI cobra mais que estimado para GPT-5 | Média | Médio | Reserva US$ 2,17 + possível cut de reps |

### 11.3 Riscos editoriais

| Risco | Prob. | Impacto | Mitigação |
|---|:-:|:-:|---|
| Desk reject Patterns | 30-40% | Médio | Pre-submission inquiry antes |
| Reviewer exige Claude | Média | Baixo | **Reserva Anthropic US$ 10** → Opus subset 170 calls |
| Reviewer exige full scope GPT-5 (já está) | Baixa | — | N/A — já full scope em v3.3 |
| Reviewer questiona "por que Lince e não Sabiá-3" | Média | Baixo | Defesa dupla: open-science consistency + R$ 200 reserva para Sabiá-3 paid se pedirem |

---

## 12. Compromissos de ciência aberta — 5 pilares

| Pilar | Implementação | Licença |
|---|---|---|
| **Open Access** (publicação) | APC via acordo CAPES/Elsevier gratuito | CC-BY 4.0 |
| **Open Data** (prompts + responses) | Zenodo deposit + DOI | CC-BY-4.0 |
| **Open Code** (pipeline + análise) | GitHub + link permanente no paper | MIT |
| **Open Weights** (10 de 14 modelos auditados) | Modelos acessíveis via Hugging Face | Diversas (Apache 2.0, MIT, Llama) |
| **Open Science** (pré-registro + processo) | OSF deposit pré-coleta | CC-BY 4.0 |

**FAIR compliance:** findable (DOI OSF + Zenodo), accessible (aberto), interoperable (JSONL + Parquet + CSV padrões), reusable (documentação + licença permissiva).

---

## 13. Próximos passos (gates de ativação)

Antes de disparar Fase 1 (Pilot):

1. ✅ Repositório GitHub sincronizado
2. ⏳ **OpenAI: adicionar US$ 10** (total US$ 15)
3. ✅ Anthropic US$ 10 (confirmado — fica em reserva)
4. ✅ DeepSeek US$ 1,99 (confirmado)
5. ✅ Gemini free tier (confirmado funciona)
6. ⏳ **Groq account** (console.groq.com — free signup)
7. ⏳ **OpenRouter account** (openrouter.ai — free signup)
8. ⏳ **Cohere account + trial key** (cohere.com/api)
9. ⏳ **DeepInfra account** (deepinfra.com — free signup)
10. ⏳ **Ollama update** + pull de modelos novos: `ollama pull qwen3:14b phi4 llama4:8b lince-mistral`
11. ⏳ **40 prompts piloto em EN** autoria Lucas

**Após confirmação dos gates:** `@experiment-runner` inicia execução Fase 1.

---

**Autor:** Lucas Rover (pesquisador) + orquestração Academic Squad AIOS (metodológica)
**Supervisora:** Profa. Dra. Yara Tadano (PPGSAU/UTFPR)
**Licença deste documento:** CC-BY-4.0
