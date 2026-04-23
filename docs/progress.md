# Progresso do Projeto

**Projeto:** Viés geográfico-factual em LLMs e seu impacto na pesquisa científica do Sul Global
**Journal-alvo definitivo:** Patterns (Cell Press, IF 7,4, Q1)
**Pesquisador:** Lucas (PPGSAU/UTFPR), orientação Prof. Dra. Yara Tadano
**Início do pipeline:** 2026-04-23

---

## Pipeline de 10 Etapas

| # | Etapa | Skill | Status | Artefato | Data |
|---|---|---|---|---|---|
| 1 | Pesquisa & Literatura | `pesquisa-academica` | ✅ Concluída | `docs/etapa1_revisao_literatura.md` | 2026-04-23 |
| 2 | Hipóteses & Gaps | `academic-hypothesis-creator` | ✅ Concluída | `docs/etapa2_hipoteses.md` | 2026-04-23 |
| 2b | Estratificação amostral | (extensão da Etapa 2) | ✅ Concluída | `docs/etapa2b_selecao_paises.md` | 2026-04-23 |
| 3 | Design Metodológico | `methodological-design` | ✅ Concluída | `docs/etapa3_metodologia.md` | 2026-04-23 |
| 4 | Validação Estatística | `validacao-metodologica` | ✅ Concluída | `docs/etapa4_sap.md` | 2026-04-23 |
| 5 (v1) | Proposta Execução — especificação inicial | `phd-senior-scientist` | 🗃️ Superseded | `docs/etapa5_proposta_execucao.md` | 2026-04-23 |
| 5 (v2) | Proposta Consolidada — multi-tier audit + R$ 200 | `academic-chief (Sage)` | 🗃️ Superseded | `docs/proposta_consolidada_v2.md` | 2026-04-23 |
| **5 (v3.3)** | **Proposta Full-Spectrum Audit — 14 modelos, 5 tiers, open-science-first** | `academic-chief (Sage)` | ✅ **Concluída** | **`docs/proposta_consolidada_v3.md`** | 2026-04-23 |
| 5.1 | Pilot Calibration Study (4 países × 3 modelos × 1.440 calls) | `experiment-runner (Forge)` | ⏳ Aguardando gates | `data/pilot_202604/` | — |
| 5.2 | OSF Pre-Registration | `submission-engineer (Atlas)` | ⏳ Depende 5.1 | `preregistration/osf_registration_v1.md` | — |
| 5.3 | Execução Confirmatória (15 países × 6 modelos × 16.200 calls) | `experiment-runner (Forge)` | ⏳ Depende 5.2 | `data/raw/llm_responses/` | — |
| 6 | Redação do Artigo (draft v1 existente, aguarda dados reais) | `scientific-writer (Quill)` | 🔄 Draft v1 | `latex/main.tex` + `sections/*.tex` | 2026-04-23 |
| 6.1 | Auditoria 6 agentes (gap, peer-review-defender, citation, writer, stat, lang) | Squad completo | ⏳ Depende 6 | `docs/audit_reports/` | — |
| 7 | Marketing & Estratégia | `scientific-marketer (Beacon)` | ⏳ Pendente | `docs/cover_letter.md` + `docs/highlights.md` | — |
| 8 | Revisão de Linguagem | `language-editor` | ⏳ Pendente | Revisão de `latex/main.tex` | — |
| 9 | Formatação Final | `submission-engineer` | ⏳ Pendente | `latex/` pronto para Cell Press | — |
| 10 | Banca & Editor | `peer-review-defender (Shield)` | ⏳ Pendente | `docs/parecer_banca.md` | — |

---

## Decisões Consolidadas

### Escopo do artigo (v3.3 — canônico)
- **Reframe narrativo:** *"Full-Spectrum Open-Weight Audit"* — primeiro benchmark Q1 cobrindo espectro 7B open → 671B MoE → closed SOTA em desenho único.
- **5 hipóteses** (H1-H4 originais + H5 open-vs-closed novo em v3).
- **15 países** (estratificação UNCTAD × Joshi × WB inalterada).
- **14 LLMs em 5 tiers:**
  - **Tier A (open frontier, 5):** Llama 4 70B, Qwen 3 72B, DeepSeek-V3 (671B MoE), Mixtral 8×22B, Command R+ 104B
  - **Tier B (open mid, 3):** Gemma 3 27B, Qwen 3 14B, Phi-4 14B
  - **Tier C (open small/regional, 2):** Llama 4 8B, **Lince-Mistral 7B** (PUCRS, H3 regional)
  - **Tier D (closed acessível, 2):** Gemini 2.5 Flash, GPT-5-mini
  - **Tier E (closed frontier SOTA, 1):** GPT-5
  - **Reserve (1):** Claude Opus 4.7 (só se reviewer pedir)
- **780 prompts** em matriz esparsa de 4+ línguas × 3 domínios × 5 tarefas.
- **2 replicações** por call (reduzido de 5 para caber em US$ 15 OpenAI).
- **Painel validação:** 2-3 especialistas por região via rede PPGSAU/UTFPR.
- **Pré-registro OSF** obrigatório antes da coleta confirmatória.

### Estrutura do artigo
- Formato: Research Article completo (~8k palavras + supplementary extenso).
- Framework teórico: Coloniality of Knowledge (Mohamed et al., 2020) + Data Feminism (D'Ignazio & Klein, 2020).
- Paradigma: post-positivista com lente crítica.

### Orçamento (v3.3)
- **Gasto planejado:** ~US$ 16 ≈ R$ 85 (OpenAI GPT-5 + GPT-5-mini + DeepSeek-V3)
- **Free tiers:** Groq, OpenRouter/DeepInfra, Cohere, Gemini (6 modelos sem custo)
- **Local Ollama (M4 24GB):** 4 modelos rodando localmente (zero API cost)
- **Reserva estratégica:** US$ 10 Anthropic (Opus se reviewer pedir) + R$ 200 cash + buffers ≈ **R$ 255**
- **Total commitment máximo:** US$ 15 novo (OpenAI top-up) + 0 do R$ 200 cash
- **Ratio reserva/gasto:** 3× — permite resposta robusta a qualquer demanda de reviewer

### Estratégia editorial (v2 revisada)
1. **Submissão primária:** *Patterns* (Cell Press, IF 7,4) — escopo perfeito para "multi-tier audit" + AI ethics + policy
2. **Fallback 1:** EPJ Data Science (IF 2,8, Q1 Social Sciences)
3. **Fallback 2:** AI & Society (IF 2,9)
4. **Fallback 3:** Frontiers in Artificial Intelligence
5. **Paralelo:** Data paper em *Scientific Data* (Nature)
6. **Probabilidade calibrada:** 25-32% em Patterns; 75-80% cumulativo em ≤3 tentativas

### Probabilidade de aceite calibrada (v3.3)
| Cenário | Probabilidade Patterns |
|---|:-:|
| 🟢 Forte (H1 d≥0,5, H3 claro, H5 open frontier competitivo) | 38-48% |
| 🟡 Esperado (H1 d 0,3-0,5, H2-H5 mistos) | 30-38% |
| 🔴 Fraco (H1 null) | 12-18% |
| **Prior ponderado** | **32-40%** |
| **Com todas as alavancas** | **40-50%** |
| **Cumulativo em ≤3 tentativas Q1/Q2** | **85-90%** |

### Licenciamento do repositório
- **Texto, documentação, dados:** CC-BY-4.0
- **Código-fonte (subdiretório `code/`):** MIT License

---

## Validações pendentes antes da Etapa 3

- [x] ~~Confirmação das 4 hipóteses (H1-H4) como formuladas~~ — confirmadas em 2026-04-23
- [x] ~~Verificar se H3 (Sabiá-3) gera conflito de interesse~~ — sem conflito
- [x] ~~Seleção final dos 15 países~~ — consolidada em `etapa2b_selecao_paises.md`
- [x] ~~Confirmação da estratégia editorial em cascata~~ — **decisão: Patterns direto** (2026-04-23)

---

## Gates de ativação para Fase 5.1 (Pilot) — v3.3

Antes de disparar o pilot:

1. ✅ Repositório GitHub sincronizado
2. ⏳ **OpenAI: adicionar US$ 10** (total US$ 15) — usuário em andamento
3. ✅ Anthropic US$ 10 confirmado (permanece em reserva)
4. ✅ Gemini free tier funciona
5. ✅ DeepSeek US$ 1,99 confirmado
6. ⏳ **Groq account** (console.groq.com — free signup)
7. ⏳ **OpenRouter account** (openrouter.ai — free signup)
8. ⏳ **Cohere account + trial key** (cohere.com/api)
9. ⏳ **DeepInfra account** (deepinfra.com — free signup)
10. ⏳ **Ollama update + pull**: `ollama pull qwen3:14b phi4 llama4:8b lince-mistral`
11. ⏳ **40 prompts piloto em EN** (autoria Lucas)

---

## Histórico de mudanças

- **2026-04-23:** Pipeline iniciado; Etapas 1 e 2 concluídas; decisão de acumular todos os artefatos em `/home/claude/artigo_llm_bias/` até finalização para empacotamento em ZIP no encerramento.
- **2026-04-23 (later):** Projeto migrado para `/Users/lucasrover/artigo-vies-analise-regional/` e sincronizado com GitHub. Proposta consolidada v2 criada com reframe narrativo ("multi-tier ecosystem audit"), desenho amostral em Tier A/B, orçamento R$ 200 on-budget + créditos existentes off-budget. Etapa 5 v1 marcada como superseded. Orquestrador Sage (academic-chief) ativo.
- **2026-04-23 (evening):** Verificação real de APIs confirmou Anthropic/OpenAI/Gemini/DeepSeek/Perplexity todas funcionais. Saldos: Anthropic US$ 10, OpenAI US$ 5, DeepSeek US$ 1,99. Proposta reescrita como v3.3 (*Full-Spectrum Open-Weight Audit*) com 14 modelos em 5 tiers, narrativa open-science-first, H5 nova (open frontier vs closed frontier), budget planejado US$ 15 OpenAI + DeepSeek + free tiers + local Ollama. R$ 200 cash + US$ 10 Anthropic mantidos como reserva estratégica (~R$ 255 total). v2 marcada como superseded. Probabilidade calibrada subiu para 32-40% prior / 40-50% com alavancas.
