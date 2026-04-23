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
| 5 | Execução Empírica | `phd-senior-scientist` | ✅ Concluída (modo especificação) | `docs/etapa5_proposta_execucao.md` + `code/` | 2026-04-23 |
| 6 | Redação do Artigo | — | ✅ Concluída (draft v1, 19pp PDF) | `latex/main.tex` + `sections/*.tex` | 2026-04-23 |
| 7 | Marketing & Estratégia | `journal-publication-strategist` | ⏳ Pendente | `docs/cover_letter.md` + `docs/highlights.md` | — |
| 8 | Revisão de Linguagem | `academic-article-reviser` | ⏳ Pendente | Revisão de `latex/main.tex` | — |
| 9 | Formatação Final | `formatador-cientifico` | ⏳ Pendente | `latex/` pronto para submissão | — |
| 10 | Banca & Editor | `banca-revisores-cientificos` | ⏳ Pendente | `docs/parecer_banca.md` | — |

---

## Decisões Consolidadas

### Escopo do artigo
- **4 hipóteses** formalizadas (H1-H4), uma por gap.
- **15 países** com justificativa teórica em 3 eixos (UNCTAD + Joshi + World Bank):
  - **América Latina (4):** Brasil, México, Argentina, Peru
  - **África (4):** Nigéria, África do Sul, Quênia, Egito
  - **Ásia Sul Global (4):** Índia, Indonésia, Bangladesh, Filipinas
  - **Norte Global controle (3):** EUA, Alemanha, Japão
- **6 LLMs:** GPT-5, Claude Opus 4.7, Gemini 2.5 Pro, Llama 4 (70B), DeepSeek-V3 ou Qwen 3, Sabiá-3.
- **4 línguas:** EN, PT, ES, HI, SW *(matriz esparsa — nem todo país em todas)*.
- **3 domínios factuais:** políticas públicas, realidade socioeconômica, contexto ambiental.
- **Painel validação:** 2-3 especialistas por região via rede PPGSAU/UTFPR.
- **Pré-registro OSF** obrigatório antes da coleta.

### Estrutura do artigo
- Formato: Research Article completo (~8k palavras + supplementary extenso).
- Framework teórico: Coloniality of Knowledge (Mohamed et al., 2020) + Data Feminism (D'Ignazio & Klein, 2020).
- Paradigma: post-positivista com lente crítica.

### Estratégia editorial
1. Submissão primária: Nature Human Behaviour (alto risco, alto reward).
2. Fallback 1: Patterns (Cell Press) — escopo perfeito.
3. Fallback 2: EPJ Data Science.
4. Publicação paralela do dataset como Data Paper em Scientific Data.

### Licenciamento do repositório
- **Texto, documentação, dados:** CC-BY-4.0
- **Código-fonte (subdiretório `code/`):** MIT License *(CC-BY não é recomendada para software)*

---

## Validações pendentes antes da Etapa 3

- [x] ~~Confirmação das 4 hipóteses (H1-H4) como formuladas~~ — confirmadas em 2026-04-23
- [x] ~~Verificar se H3 (Sabiá-3) gera conflito de interesse~~ — sem conflito
- [x] ~~Seleção final dos 15 países~~ — consolidada em `etapa2b_selecao_paises.md`
- [x] ~~Confirmação da estratégia editorial em cascata~~ — **decisão: Patterns direto** (2026-04-23)

---

## Histórico de mudanças

- **2026-04-23:** Pipeline iniciado; Etapas 1 e 2 concluídas; decisão de acumular todos os artefatos em `/home/claude/artigo_llm_bias/` até finalização para empacotamento em ZIP no encerramento.
