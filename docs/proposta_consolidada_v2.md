> **⚠️ SUPERSEDED — este documento foi substituído por `proposta_consolidada_v3.md` (v3.3 — Full-Spectrum Audit) em 2026-04-23. Mantido para rastreabilidade histórica.**

# Proposta Consolidada v2 — Multi-Tier Audit de LLMs em Pesquisa de Políticas do Sul Global

**Versão:** 2.0 (supersede `etapa5_proposta_execucao.md`)
**Data:** 2026-04-23
**Target journal:** *Patterns* (Cell Press, IF 7.4, Q1)
**Pesquisador:** Lucas Rover (PPGSAU/UTFPR) — orientação Profa. Dra. Yara Tadano
**Orquestração metodológica:** Academic Squad (Synkra AIOS) — orquestrador Sage
**Status:** pronto para execução em 5 fases

---

## 1. Sumário executivo

Proposta de benchmark pré-registrado que quantifica o viés geográfico-factual de 6 LLMs em tarefas de pesquisa aplicada sobre 15 países, cobrindo 3 domínios (políticas públicas, realidade socioeconômica, contexto ambiental) e uma matriz esparsa de 4 línguas. A v2 reformula o desenho v1 em três pontos:

1. **Reframe narrativo** — de *"frontier comparison"* para *"ecosystem audit"*: quais LLMs pesquisadores do Sul Global de fato podem usar, e como eles se comportam.
2. **Amostra de modelos em dois tiers** — 5 modelos acessíveis rodados em escopo completo (Tier A, narrativa primária) + 1 frontier premium em subset (Tier B, ceiling check).
3. **Orçamento operacional de R$ 200** — viabilizado por combinação de APIs acessíveis (Groq, Together, Maritaca) on-budget + créditos existentes (Anthropic, Google) off-budget.

Probabilidade calibrada de aceite em *Patterns*: **25-32%** após ativação das alavancas editoriais. Probabilidade cumulativa de aceite em Q1/Q2 em ≤3 tentativas (Patterns → EPJ Data Science → AI & Society): **75-80%**.

---

## 2. O que mudou — reframe narrativo (v1 → v2)

### 2.1 Posicionamento anterior (v1)

> *"LLMs frontier (GPT-5, Claude Opus 4.7, Gemini 2.5 Pro) falham em tarefas de pesquisa aplicada sobre o Sul Global."*

**Problema:** exige R$ 35-40k em API (Opus 4.7 a R$0,21/call × 202.500 calls), inviável com orçamento de R$ 200 disponível para o projeto.

### 2.2 Posicionamento v2

> *"Across the LLM ecosystem actually accessible to Global South researchers — regional, open, accessible-frontier, and frontier-premium — where are the geographic gaps, and which tier best serves applied policy research?"*

**Por que v2 é editorialmente MAIS forte:**
- **Policy relevance direta:** pesquisador no Sul Global não compra Opus 4.7 nem GPT-5 para o dia-a-dia; usa Sonnet, Gemini Pro, Llama. Benchmarkar o que é de fato usado é acionável.
- **Ângulo inédito:** WorldBench, BLEnD, GeoMLAMA testam frontier. Ninguém mediu o "tier abaixo" especificamente.
- **Consistência teórica:** o preço do frontier é **ele próprio uma assimetria colonial** — isso amplifica o framework de *coloniality of knowledge*, não enfraquece.
- **Replicabilidade:** outro grupo no Sul Global reproduz com orçamento similar.

### 2.3 O que não mudou

- **Questão de pesquisa** (inalterada)
- **Hipóteses H1-H4** (inalteradas em formulação; H2/H4 têm poder estatístico levemente ajustado)
- **Estratificação dos 15 países** (UNCTAD × Joshi × World Bank — inalterada)
- **SAP confirmatório** (pré-registro OSF; ajustes de variance components após pilot)
- **Framework teórico** (Coloniality of Knowledge + Data Feminism)

---

## 3. Questão de pesquisa e hipóteses

### 3.1 Questão central

Do LLMs — across the tiers accessible to Global South researchers — exhibit systematic factual bias when supporting applied policy research about the Global South? If so, what role do (i) prompt language, (ii) regional model training, and (iii) training-corpus representation play in explaining the bias?

### 3.2 Hipóteses formalizadas (verbatim da Etapa 2)

| # | Hipótese | Efeito esperado | Teste primário |
|---|---|---|---|
| **H1** | LLMs exibem acurácia inferior no Sul Global vs Norte Global | Cohen's *d* ≥ 0,5 | GLMM com indicador Global South |
| **H2** | Língua do prompt e país interagem não-aditivamente | η²_p ≥ 0,05 | Termo de interação GLMM |
| **H3a** | Sabiá-3 reduz gap do Brasil em >50% | Contraste pré-especificado | Bayesian contrast |
| **H3b** | Sabiá-3 desloca gap para outros lusófonos | Contraste pré-especificado | Bayesian contrast (H3a e H3b mutuamente exclusivas) |
| **H4** | log(tokens no CC) correlaciona com acurácia | Spearman ρ ≥ 0,60 | Regressão ecológica + mediação |

---

## 4. Desenho amostral de modelos — Tier A / Tier B

### 4.1 Racional

Em vez de amostrar 6 modelos frontier de forma homogênea, estratificamos **explicitamente** a amostra de modelos em dois tiers com propósitos distintos na análise:

| Tier | Propósito | Países | Reps | Uso na inferência |
|---|---|:-:|:-:|---|
| **A — Accessible** | Narrativa primária: o ecossistema que o Sul Global usa | 15 | 5 | H1, H2, H3, H4 |
| **B — Frontier ceiling** | Ceiling check: até onde o tier premium performa | 6 subset | 5 | Análise de sensibilidade + Discussion |

### 4.2 Modelos selecionados

#### Tier A — Accessible (escopo completo, 15 países × 5 reps)

| Modelo | Provedor | Categoria | API | Budget |
|---|---|---|---|---|
| **Claude Sonnet 4.6** | Anthropic | Frontier acessível | `claude-sonnet-4-6` | Off-budget (créditos) |
| **Gemini 2.5 Pro** | Google | Frontier acessível | `gemini-2.5-pro` | Off-budget (créditos) |
| **Llama 4 70B Instruct** | Meta (via Groq) | Open frontier | `llama-4-70b-instruct` | On-budget (~R$ 10) |
| **Sabiá-3** | Maritaca | Regional (PT-BR) | `sabia-3` | On-budget (~R$ 15) |
| **Qwen 3 32B** | Alibaba (via Together) | Scale-control de Sabiá-3 | `qwen3-32b` | On-budget (~R$ 5) |

**Justificativa:** cobre 4 vendors diferentes, 3 regimes de treinamento (proprietary global, open global, regional), e 1 scale-control para isolar efeito "regionalidade" de "tamanho" em H3.

#### Tier B — Frontier ceiling (subset de 6 países × 5 reps)

| Modelo | Provedor | Uso | Budget |
|---|---|---|---|
| **Claude Opus 4.7** | Anthropic | Ceiling check em BR + US + DE + JP + 2 Sul Global estratégicos (IN, NGA) | Off-budget (créditos) |

**Justificativa:** Opus 4.7 é o único frontier premium acessível (OpenAI quota exausta; Gemini Pro já em Tier A). Subset estratégico demonstra que resultados do Tier A não são artefato de "tier acessível = pior" — se Opus também mostrar gap, o achado é robusto.

### 4.3 Modelos **excluídos** (e por quê)

| Modelo | Motivo |
|---|---|
| **GPT-5** | Quota OpenAI exausta; aplicar ao Researcher Access Program em paralelo — se aprovar durante execução, incluir em Tier B |
| **DeepSeek-V3** | Considerar como add-on opcional (custo <R$ 5); decisão pós-pilot |
| **Jais, Latam-GPT, Lince-Mistral** | Escopo 2.0 (trabalho futuro sobre "regional models para além do Brasil") |

---

## 5. Escopo experimental (agregado)

| Dimensão | Valor |
|---|---:|
| Países | 15 |
| Modelos Tier A | 5 |
| Modelos Tier B (subset) | 1 × 6 países |
| Prompts por país | 40 (30 básicos + 10 línguas regionais) |
| Replicações por call | 5 |
| **Calls Tier A** | 15 × 5 × 40 × 5 = **15.000** |
| **Calls Tier B** | 6 × 1 × 40 × 5 = **1.200** |
| **Total calls** | **16.200** |

### 5.1 Matriz de línguas (esparsa, inalterada da v1)

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

## 6. Orçamento — R$ 200 on-budget + créditos off-budget

### 6.1 Alocação on-budget (R$ 200 total)

| Item | Custo | % |
|---|---:|---:|
| Sabiá-3 (3.000 calls @ R$ 0,005) | R$ 15 | 7,5% |
| Llama 4 70B via Groq (3.000 calls) | R$ 10 | 5,0% |
| Qwen 3 32B via Together (3.000 calls) | R$ 5 | 2,5% |
| **Subtotal execução confirmatória** | **R$ 30** | **15%** |
| Pilot (Fase 1, ver §7) | R$ 15 | 7,5% |
| Buffer de contingência | R$ 155 | 77,5% |
| **TOTAL** | **R$ 200** | **100%** |

### 6.2 Alocação off-budget (créditos existentes)

| Item | Créditos estimados necessários |
|---|---:|
| Claude Sonnet 4.6 (3.000 calls @ $0,009) | ~US$ 27 / R$ 140 (Anthropic) |
| Claude Opus 4.7 subset (1.200 calls @ $0,045) | ~US$ 54 / R$ 280 (Anthropic) |
| Gemini 2.5 Pro (3.000 calls @ $0,007) | ~US$ 20 / R$ 105 (Gemini) |
| **TOTAL off-budget** | **~R$ 525** |

**Nota:** valores dependem de confirmação dos saldos disponíveis. Se Anthropic credits < US$ 80, reduzir subset Opus 4.7 para 4 países (BR + US + DE + IN) cortando custo para ~US$ 36.

### 6.3 Contingências disparadas pelo buffer

| Disparador | Uso do buffer |
|---|---|
| Sinal fraco no pilot (effect size < 0,2) | Expandir pilot para 6 países (R$ 10) |
| API errors > 5% em algum modelo | Re-runs seletivos (R$ 20-30) |
| OpenAI Researcher Access aprovado | Incluir GPT-5-mini no Tier A (R$ 40-50) |
| Análise de sensibilidade com Haiku 4.5 | Tier low-cost (R$ 20) |
| Ampliar reps Sabiá-3 em BR para H3 | +5 reps (R$ 5) |

---

## 7. Cronograma de execução — 5 fases

### Fase 1 — Pilot Calibration Study (2-3 dias, ~R$ 15 on-budget)

**Objetivo:** validar infra + calibrar SESOI + ver sinal real antes do OSF lock.

**Escopo:**
- 4 países (BR, NGA, IND, USA)
- 3 modelos (Sonnet 4.6, Gemini 2.5 Pro, Sabiá-3)
- 40 prompts × 3 reps = **1.440 calls**
- Custo: ~R$ 15 on-budget + ~US$ 10 off-budget

**Delegação:** `@experiment-runner (Forge)` + autor dos prompts (Lucas)

**Entregas:**
- `data/pilot_202604/` com responses brutos
- `results/pilot_findings.md` com GLMM exploratório
- Decisão go/no-go para Fase 2

**Rótulo obrigatório:** `PILOT — exploratory, not confirmatory` em todos os arquivos.

### Fase 2 — OSF Pre-Registration (1 dia, 0 custo)

**Objetivo:** lock do SAP antes de qualquer coleta confirmatória.

**Delegação:** `@submission-engineer (Atlas)` + `@po (Pax)` valida completude

**Entregas:**
- SAP v1.1 atualizado com variance components do pilot
- `preregistration/osf_registration_v1.md` (AsPredicted template)
- Deposit na OSF → obter DOI

### Fase 3 — Confirmatório (7-10 dias, ~R$ 30 on-budget)

**Objetivo:** coleta principal pré-registrada.

**Escopo:** 16.200 calls (ver §5)

**Delegação:** `@experiment-runner` + `@statistician (Sigma)`

**Entregas:**
- `data/raw/llm_responses/run_202605.jsonl`
- `data/processed/analytic_main.parquet`
- `tables/h1_glmm.csv`, `h2_interaction.csv`, `h3_contrasts.csv`, `h4_mediation.csv` (todos reais, sem seal SIMULATION)
- `figures/fig1-fig6.pdf` atualizados

### Fase 4 — Redação + Auditoria (5-7 dias)

**Objetivo:** manuscrito pronto para submissão com auditoria de 6 agentes.

**Delegação:** `@scientific-writer (Quill)` + auditoria mandatória

**Entregas:**
- `latex/main.tex` com todos os `\placeholder{}` substituídos
- Auditoria sequencial de 6 agentes (regra do pesquisador):
  1. `@gap-analyst` — literatura atualizada 2026
  2. `@peer-review-defender` — stress-test de reviewer hostil
  3. `@citation-sentinel` — DOIs + referências
  4. `@scientific-writer` — coerência narrativa
  5. `@statistician` — números reproduzíveis
  6. `@language-editor` — inglês acadêmico final

### Fase 5 — Submissão (2-3 dias, 0 custo)

**Objetivo:** submissão em *Patterns*.

**Delegação:** `@submission-engineer` + `@scientific-marketer (Beacon)` + `@devops (Gage)` para git push

**Entregas:**
- Formatação template Cell Press
- `docs/cover_letter.md` + `docs/highlights.md`
- **Pre-submission inquiry** ao editor-chefe (+2-3pp)
- Submissão via Editorial Manager
- Paralelo: data paper em *Scientific Data* (dataset + rubric + prompts)

**Timeline total:** **17-24 dias úteis** da autoria dos prompts até submissão.

---

## 8. Estratégia editorial

### 8.1 Target primário — *Patterns*

**Por que Patterns funciona para v2:**
- Escopo explícito inclui "AI governance, ethics, science policy", "data science solutions to cross-disciplinary problems"
- Publicou trabalhos sobre AI bias em 2024-2025 (WorldBench está nesse espaço editorial)
- Aceita supplementary rico (nosso ecosystem audit tem supplementary extenso)
- Open Access obrigatório (alinha com compromisso FAIR do projeto)
- Tempo primeira decisão ~5 dias; revisão completa ~45-60 dias

**APC:** USD 4.900 com geographical pricing OA (redução para autores brasileiros — verificar elegibilidade).

### 8.2 Cascata de fallback

| Prioridade | Journal | IF | Probabilidade condicional | Fit |
|---|---|:-:|:-:|---|
| 1 | **Patterns** | 7,4 | 25-32% | ⭐⭐⭐⭐⭐ |
| 2 | EPJ Data Science | 2,8 | 60-70% | ⭐⭐⭐⭐ |
| 3 | AI & Society | 2,9 | 50-60% | ⭐⭐⭐⭐ |
| 4 | Frontiers in AI | 3,1 | 70-80% | ⭐⭐⭐ |

**Probabilidade cumulativa de aceite em ≤3 tentativas:** **75-80%**.

### 8.3 Data paper paralelo

Submeter em *Scientific Data* (Nature):
- Dataset de 16.200 respostas LLM
- Prompts validados
- Ground truth catalog
- Código de rubric
- **Reuso esperado alto** → citações garantidas

---

## 9. Probabilidade de aceite — decomposição

### 9.1 Cenários por resultado (antes da coleta)

| Cenário | Probabilidade em Patterns |
|---|:-:|
| 🟢 Forte (H1 d≥0,5, H3 claro, H4 ρ≥0,6) | **30-38%** |
| 🟡 Esperado (H1 d 0,3-0,5, H2-H4 mistos) | **22-26%** |
| 🔴 Fraco (H1 null, H2-H4 null) | **8-14%** |
| **Expectativa ponderada (prior)** | **22-28%** |

### 9.2 Alavancas editoriais (acumulativas, +pp em Patterns)

| Alavanca | Ganho |
|---|:-:|
| Pré-registro OSF | +4-6pp |
| Painel de especialistas (Krippendorff α≥0.70) | +3-5pp |
| Cover letter afinada | +3-4pp |
| Pre-submission inquiry | +2-3pp |
| Figura 1 de alta qualidade | +2pp |
| Auditoria 6 agentes | +2-4pp |
| Data paper paralelo | +1pp (via visibilidade) |

**Teto realista:** **30-38% em Patterns** com todas as alavancas ativadas.

---

## 10. Risk register

### 10.1 Riscos científicos

| Risco | Prob. | Impacto | Mitigação |
|---|:-:|:-:|---|
| Effect size real < SESOI (d<0,3) | Média | Alto | Pilot detecta antes; pivotar para "null findings matter" se necessário |
| Rubrica falha no Krippendorff (α<0,70) | Média | Alto | Pré-teste com 50 prompts; adjudicação por 3º avaliador se necessário |
| Data contamination (LLM viu ground truth) | Média | Médio | Subset pós-cutoff; documentado como limitação |
| Modelos atualizam mid-execução | Baixa | Médio | Registrar timestamp + versão exata; re-run seletivo |

### 10.2 Riscos operacionais

| Risco | Prob. | Impacto | Mitigação |
|---|:-:|:-:|---|
| Créditos Anthropic insuficientes para Opus subset | Média | Médio | Reduzir Tier B de 6 para 4 países |
| Quota OpenAI não reabre | Alta | Baixo | Documentar ausência como limitação; 5 modelos Tier A suficientes |
| Maritaca rate limit | Baixa | Baixo | Spread calls over 2-3 dias |
| Crash do experiment runner | Baixa | Baixo | Checkpoints a cada 100 calls já implementados |

### 10.3 Riscos editoriais

| Risco | Prob. | Impacto | Mitigação |
|---|:-:|:-:|---|
| Desk reject em Patterns | 30-40% | Médio | Pre-submission inquiry antes; cover letter diferenciada |
| Reviewer exige GPT-5 | Alta | Médio | Response: documentamos limitação; oferece Opus 4.7 como frontier ceiling |
| Reviewer crítico com "accessible-tier" framing | Média | Médio | Defesa dupla: empírica (Tier B confirma padrão) + teórica (preço é assimetria) |

---

## 11. Compromissos de ciência aberta

| Item | Repositório | Licença |
|---|---|---|
| Prompts (v1 final) | GitHub + Zenodo | CC-BY-4.0 |
| LLM responses (16.200) | Zenodo | CC-BY-4.0 |
| Ground truth catalog | GitHub | CC-BY-4.0 |
| Rubric + evaluation code | GitHub | MIT |
| Analysis code | GitHub | MIT |
| Pre-registration | OSF | CC-BY-4.0 |
| Manuscript preprint | arXiv | CC-BY-4.0 |

**FAIR compliance:** findable (DOI OSF + Zenodo), accessible (aberto), interoperable (JSONL + Parquet + CSV padrões), reusable (documentação + licença permissiva).

---

## 12. Próximos passos (gates de ativação)

Antes de disparar Fase 1, confirmar:

1. ✅ Repositório GitHub sincronizado — **feito** (2026-04-23)
2. ⏳ Saldo Anthropic API (mínimo US$ 80 para Sonnet + Opus subset)
3. ⏳ Saldo Gemini API (mínimo US$ 25)
4. ⏳ Conta Maritaca (Sabiá-3) criada + R$ 25 carregados
5. ⏳ Contas Groq + Together (gratuito inicial suficiente)
6. ⏳ Autoria pelo pesquisador dos 40 prompts piloto (EN) — baseline para expansão

**Após confirmação dos 6 gates:** `@experiment-runner` inicia execução da Fase 1 em H+0.

---

**Autor desta proposta:** Lucas Rover (pesquisador) + orquestração Academic Squad AIOS (metodológica)
**Supervisora:** Profa. Dra. Yara Tadano (PPGSAU/UTFPR)
**Licença deste documento:** CC-BY-4.0
