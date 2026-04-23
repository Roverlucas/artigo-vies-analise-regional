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
| **5 (v2)** | **Proposta Consolidada — multi-tier audit + R$ 200 budget** | `academic-chief (Sage)` | ✅ **Concluída** | **`docs/proposta_consolidada_v2.md`** | 2026-04-23 |
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

### Escopo do artigo (v2)
- **Reframe narrativo:** de "frontier comparison" para "multi-tier ecosystem audit" — quais LLMs pesquisadores do Sul Global de fato podem usar, e como eles se comportam.
- **4 hipóteses** formalizadas (H1-H4), inalteradas em formulação.
- **15 países** com justificativa teórica em 3 eixos (UNCTAD + Joshi + World Bank):
  - **América Latina (4):** Brasil, México, Argentina, Peru
  - **África (4):** Nigéria, África do Sul, Quênia, Egito
  - **Ásia Sul Global (4):** Índia, Indonésia, Bangladesh, Filipinas
  - **Norte Global controle (3):** EUA, Alemanha, Japão
- **6 LLMs em dois tiers:**
  - **Tier A (acessível, escopo completo):** Claude Sonnet 4.6, Gemini 2.5 Pro, Llama 4 70B, Sabiá-3, Qwen 3 32B
  - **Tier B (frontier ceiling, subset de 6 países):** Claude Opus 4.7
  - **Excluídos:** GPT-5 (quota OpenAI exausta — aplicar Researcher Access); DeepSeek-V3 (add-on opcional)
- **4 línguas:** EN, PT, ES, HI, SW *(matriz esparsa — nem todo país em todas)*.
- **3 domínios factuais:** políticas públicas, realidade socioeconômica, contexto ambiental.
- **Painel validação:** 2-3 especialistas por região via rede PPGSAU/UTFPR.
- **Pré-registro OSF** obrigatório antes da coleta confirmatória.

### Estrutura do artigo
- Formato: Research Article completo (~8k palavras + supplementary extenso).
- Framework teórico: Coloniality of Knowledge (Mohamed et al., 2020) + Data Feminism (D'Ignazio & Klein, 2020).
- Paradigma: post-positivista com lente crítica.

### Orçamento (v2)
- **On-budget:** R$ 200 para Sabiá-3 (Maritaca) + Llama 4 (Groq) + Qwen 3 (Together)
- **Off-budget:** créditos existentes Anthropic (Sonnet + Opus subset) + Google (Gemini 2.5 Pro)
- **Projeção de uso:** ~R$ 30 on-budget; buffer R$ 170 para contingências
- **Custo off-budget equivalente:** ~R$ 525 (coberto por créditos disponíveis)

### Estratégia editorial (v2 revisada)
1. **Submissão primária:** *Patterns* (Cell Press, IF 7,4) — escopo perfeito para "multi-tier audit" + AI ethics + policy
2. **Fallback 1:** EPJ Data Science (IF 2,8, Q1 Social Sciences)
3. **Fallback 2:** AI & Society (IF 2,9)
4. **Fallback 3:** Frontiers in Artificial Intelligence
5. **Paralelo:** Data paper em *Scientific Data* (Nature)
6. **Probabilidade calibrada:** 25-32% em Patterns; 75-80% cumulativo em ≤3 tentativas

### Probabilidade de aceite calibrada
| Cenário | Probabilidade Patterns |
|---|:-:|
| 🟢 Forte (H1 d≥0,5, H3 claro) | 30-38% |
| 🟡 Esperado (H1 d 0,3-0,5) | 22-26% |
| 🔴 Fraco (H1 null) | 8-14% |
| **Prior ponderado** | **22-28%** |
| **Com todas as alavancas** | **30-38%** |

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

## Gates de ativação para Fase 5.1 (Pilot)

Antes de disparar o pilot:

1. ✅ Repositório GitHub sincronizado
2. ⏳ Saldo Anthropic API (mínimo US$ 80 para Sonnet + Opus subset)
3. ⏳ Saldo Gemini API (mínimo US$ 25)
4. ⏳ Conta Maritaca (Sabiá-3) criada + R$ 25 carregados
5. ⏳ Contas Groq + Together (gratuito inicial suficiente)
6. ⏳ Autoria pelo pesquisador dos 40 prompts piloto (EN)

---

## Histórico de mudanças

- **2026-04-23:** Pipeline iniciado; Etapas 1 e 2 concluídas; decisão de acumular todos os artefatos em `/home/claude/artigo_llm_bias/` até finalização para empacotamento em ZIP no encerramento.
- **2026-04-23 (later):** Projeto migrado para `/Users/lucasrover/artigo-vies-analise-regional/` e sincronizado com GitHub. Proposta consolidada v2 criada com reframe narrativo ("multi-tier ecosystem audit"), desenho amostral em Tier A/B, orçamento R$ 200 on-budget + créditos existentes off-budget. Etapa 5 v1 marcada como superseded. Orquestrador Sage (academic-chief) ativo.
