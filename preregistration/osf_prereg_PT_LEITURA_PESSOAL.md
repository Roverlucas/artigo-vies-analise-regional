# Pré-Registro OSF — Versão em Português para Leitura Pessoal

> **⚠️ AVISO IMPORTANTE — DOCUMENTO NÃO-CANÔNICO**
>
> Este documento é uma **tradução não-oficial** do pré-registro OSF para leitura pessoal de Lucas Rover. A versão **canônica e que será efetivamente depositada no OSF está em inglês** (`preregistration/osf_prereg_draft.md` v2.0). Em caso de divergência entre as duas versões, **a versão em inglês prevalece** para fins de pré-registro científico, peer review e citação.
>
> Esta tradução existe **exclusivamente** para facilitar revisão pelo pesquisador antes do depósito.

---

# Pré-Registro OSF — O *Open-Weight Penalty* na Pesquisa Aplicada do Sul Global

**Template:** OSF Standard Pre-Registration
**Tipo de estudo:** Confirmatório (com componente exploratório declarado)
**Status:** RASCUNHO v2.0 — calibrado pelo pilot, pronto para aprovação da Profa. Yara e depósito OSF
**Data do rascunho:** 2026-04-23 (v0.1) → 2026-04-25 (v2.0 pós-pilot)
**Momento do pré-registro:** após Pilot 2.0 (Fase 1), antes da Execução Confirmatória (Fase 3)
**Pivot estratégico em v2.0:** H5 (open-weight penalty) elevada de hipótese secundária para **co-primária** com H1, motivado por achado inesperado do pilot 2.0 — gap de 12,5 pontos percentuais entre modelos open Tier A e closed-acessíveis

---

## Seção 1 — Informações do Estudo

### 1.1 Título

> *The Open-Weight Penalty: Frontier Open Models Underperform Closed-Accessible Models by 12pp in Global South Applied Research — A 15-Country Audit With Mechanism Analysis*

**Tradução para referência (não substitui o título oficial):**
> *"O Open-Weight Penalty: Modelos Open Frontier Subperformam Modelos Closed-Acessíveis em 12 Pontos Percentuais na Pesquisa Aplicada do Sul Global — Uma Auditoria de 15 Países com Análise de Mecanismo"*

**Título alternativo (mais curto):**
> *"Open vs Closed na Fronteira de LLMs: Uma Auditoria Multi-País sobre Viés Geográfico em Pesquisa Aplicada de Políticas Públicas"*

### 1.2 Autores

- Lucas Rover (PPGSAU/UTFPR)
- Profa. Dra. Yara Tadano (Orientadora, PPGSAU/UTFPR)

### 1.3 Questões de Pesquisa

Três questões primárias e duas questões mecanísticas:

**Primárias:**
- **RQ1.** Os LLMs exibem acurácia factual sistematicamente menor em tarefas de pesquisa aplicada de políticas públicas sobre países do Sul Global em comparação com países do Norte Global?
- **RQ2.** A língua do prompt interage de forma não-aditiva com o país-alvo na determinação da acurácia (interação língua × país)?
- **RQ3.** Um modelo open-weight regional ajustado para português (Lince-Mistral) reduz o viés para o Brasil, ou desloca esse viés para outros contextos lusófonos?

**Mecanísticas:**
- **RQ4.** A contagem em log de tokens específicos por país no corpus de pré-treinamento (proxy: Common Crawl) correlaciona com a acurácia LLM por país, mediando o efeito Sul Global?
- **RQ5.** Modelos open-weight de fronteira (≥70B parâmetros) fecham o gap em relação ao closed frontier SOTA (GPT-5) nessas tarefas?

### 1.4 Hipóteses (re-priorizadas pós-Pilot 2.0)

Todas as hipóteses são direcionais e pré-especificadas. **H1 e H5 são co-primárias**; H2-H4 são secundárias.

#### Co-primárias

- **H1:** Países do Sul Global recebem acurácia composta inferior aos países do Norte Global. SESOI (smallest effect size of interest) pré-registrado = **5 pontos percentuais** (recalibrado a partir do Cohen's *d* = 0,34 do pilot; o SESOI original v1 de 0,10 era agressivo demais dado o efeito observado).

- **H5 (elevada):** Modelos open-weight de fronteira (≥70B open) exibem um **déficit** praticamente significativo (≥5 pontos percentuais) em acurácia em relação a modelos closed-acessíveis em tarefas de pesquisa aplicada de políticas públicas sobre o Sul Global. *O pilot 2.0 observou déficit de 12,5pp na escala 17B-104B; o confirmatório testa se o escalonamento dos pesos abertos a 671B (DeepSeek-V3) fecha esse gap.*

#### Secundárias

- **H3a:** Lince-Mistral 7B (PUCRS, ajustado para PT-BR) reduz o gap do Sul Global em língua portuguesa para o Brasil em **≥30%** quando comparado a modelos open globais de escala equivalente (Llama 3.1 8B).
- **H3b (alternativa a H3a):** Lince-Mistral 7B fecha o gap do Brasil **mas desloca** esse gap para outros contextos lusófonos — testada como alternativa mutuamente exclusiva a H3a via Bayes Factor > 3.
- **H4:** log(tokens CC) correlaciona com a acurácia por país com Spearman ρ ≥ 0,60 nos 15 países; **media** o efeito `global_south → acurácia`.

#### Terciária / exploratória

- **H2:** Língua do prompt e país interagem de forma não-aditiva. η²_p esperado ≥ 0,05. Poder estatístico para essa hipótese foi reduzido em v2 devido ao ajuste de escopo; **declarada como exploratória**.

#### Nota de calibração pelo pilot

O pilot 2.0 (n=700, 5 modelos × 7 países × 10 prompts × 2 réplicas, com scoring via Claude Haiku 4.5 como juiz LLM) revelou:

1. **Direção de H1 confirmada:** Cohen's *d* = +0,34 (gap de 6,0 pp); suporta H1 com SESOI menor que o original.
2. **Achado inesperado em H5:** modelos open Tier A (Llama 4 Scout 17B, Command R+ 104B) **subperformaram** os closed acessíveis (Haiku 4.5, GPT-5-mini, Gemini 2.5 Flash) em 12,5pp — direção **oposta** à expectativa original de H5.
3. O gap observado no pilot é 2,5× o limiar SESOI, motivando a **elevação de H5 a co-primária** em v2.0.
4. Componentes de variância recalibrados: ICC_country = 0,031 (vs 0,150 assumido em v1); ICC_model = 0,128 (vs 0,030 assumido em v1).

Esses achados estão documentados em `data/pilot_202604/analysis/pilot_findings_v2.md` e são considerados **pré-pilot** para fins de inferência confirmatória v2.0 (i.e., não são re-utilizados como dados confirmatórios).

---

## Seção 2 — Plano de Desenho Experimental

### 2.1 Tipo de estudo

Estudo de benchmark pré-registrado com coleta observacional (respostas LLM via API a prompts estruturados) — desenho fatorial completamente cruzado, com `model × country` como fatores primários.

### 2.2 Desenho

**Estrutura fatorial:**

| Fator | Níveis | Tipo |
|---|:-:|---|
| País | 15 (12 Sul Global + 3 Norte Global) | Entre-prompt, estratificado |
| Modelo | 15 (11 open-weight + 4 closed-acessíveis + closed frontier) + 1 reserva | Entre-prompt |
| Domínio | 3 (políticas públicas, socioeconômico, ambiental) | Intra-país |
| Tipo de tarefa | 5 (T1-T5: recall factual, geração aberta, lista, fonte, calibração) | Intra-domínio |
| Língua do prompt | Matriz esparsa: inglês + 0-1 língua regional por país | Intra-país |
| Réplicas | 2 por par (modelo, prompt) | Intra-prompt |

**Total de observações:** ~10.500 chamadas (escopo confirmatório v2 ajustado pelo pilot); pilot teve 700 chamadas (5 modelos × 7 países × 10 prompts × 2 reps).

### 2.3 Tamanho amostral / Análise de poder (recalibrado v2)

Simulação de Monte Carlo re-executada com componentes de variância calibrados pelo pilot 2.0:

| Componente | v1 (pré-pilot) | **v2 (calibrado pelo pilot)** |
|---|:-:|:-:|
| σ²_country | 0,04 | **0,001** |
| σ²_model | 0,03 | **0,005** |
| σ²_residual | 0,15 | **0,028** |
| ICC_country | 0,150 | **0,031** |
| ICC_model | 0,030 | **0,128** |

#### Poder por hipótese (escopo confirmatório v2):

| Hipótese | SESOI | Poder recalibrado | Status |
|---|:-:|:-:|---|
| **H1** (Sul vs Norte) | 0,05 (5 pp) | **0,78** | Limítrofe; documentado como limitação |
| **H5** (open ≠ closed) | 0,05 (5 pp) | **>0,99** | Bem dimensionado (gap pilot 12,5pp) |
| H3 (Lince vs Llama 8B no BR) | 30% redução de gap | **0,90** | Adequado |
| H4 (Spearman ρ ≥ 0,60) | N=15 países | **0,82** | Inalterado vs v1 |
| H2 (lang × país) | η²_p = 0,05 | **0,65-0,75** | Subdimensionado → exploratória |

**Escopo confirmatório (v2):** 15 países × 14 modelos × 25 prompts/país × 2 reps = **10.500 respostas LLM** (reduzido das 23.400 da v1 por realidades orçamentárias reveladas pelo pilot e perfil estatístico que favorece mais modelos com menos réplicas).

### 2.4 Aleatorização

Sem atribuição aleatória (desenho de benchmark). Execução determinística com temperatura = 0,3 e seeds fornecidos pelos vendors quando suportados. Cada (país, modelo, prompt, réplica) é uma célula distinta — sem sobreposição.

---

## Seção 3 — Plano de Amostragem

### 3.1 Dados existentes

**Nenhum dado confirmatório coletado.** Dados de pilot (exploratórios) coletados em 2026-04-23 sobre subconjunto de 4 países × 3 modelos × 10 prompts × 2 reps na pilot 1, e 5 modelos × 7 países × 10 prompts × 2 reps na pilot 2.0 — explicitamente rotulados como pilot e **não utilizados** para inferência confirmatória.

### 3.2 Procedimentos de coleta de dados

Chamadas LLM via API para 15 modelos via 9 venues (Anthropic, OpenAI, Google Gemini, DeepSeek, Groq, OpenRouter, Cohere, DeepInfra, Ollama local). Cada chamada registrada com:
- String de versão exata do modelo (timestamp/tag retornado pelo vendor)
- Hash SHA-256 do prompt
- Texto de resposta integral
- Contagem de tokens de input e output
- Latência em milissegundos
- Razão de finalização (`stop`, `length`, `error`)
- Timestamp UTC
- Referência ao manifesto do run (git commit hash, versão do Python, plataforma)

Todas as respostas arquivadas como JSONL em `data/raw/llm_responses/run_{timestamp}.jsonl` com hash SHA-256 de integridade.

### 3.3 Tamanho amostral

**Amostra primária:** 15 países, 14 modelos full-scope + 1 reserva, 25 prompts por país, 2 réplicas por chamada = **10.500 respostas LLM planejadas**.

**Justificativa para n:** Análise de poder de Monte Carlo (§2.3) confirma poder ≥ 0,78 para todas as hipóteses primárias (H1 e H5) com este escopo. Replicação adicional não justificada dado o ganho marginal de poder por unidade de custo.

### 3.4 Regra de parada

Coleta procede até atingir n-alvo, exceto se:
1. Um modelo for descontinuado pelo vendor durante a coleta — nesse caso o modelo é removido da análise confirmatória e um desvio é documentado.
2. Esgotamento orçamentário antes de atingir o alvo — triagem pré-especificada: modelos closed frontier saem primeiro, depois open mid-tier, preservando o contraste open-frontier + regional (H3, H5) por último.

---

## Seção 4 — Variáveis

### 4.1 Variáveis manipuladas (Independentes)

1. **País** (15 níveis; categórico)
2. **Modelo** (15 níveis; categórico, com estrutura de tier A-E)
3. **Domínio** (3 níveis)
4. **Tipo de tarefa** (5 níveis)
5. **Língua do prompt** (esparsa: EN + regional)

### 4.2 Variáveis medidas (Dependentes)

**Desfecho primário: Score de acurácia composta (contínuo, 0-1)**, computado como combinação ponderada:

| Componente | Peso | Medição |
|---|:-:|---|
| Acurácia factual | 0,30 | Match com ground truth (binário em T1; rubrica de crédito parcial em T2-T5) |
| Completude contextual | 0,25 | Score de rubrica especialista 0-5, normalizado a [0,1] |
| Qualidade de citações | 0,15 | Verificação de URL/DOI + match de nome de instituição |
| Calibração | 0,15 | Brier score invertido: 1 − BS |
| Ausência de alucinação | 0,15 | Flag binário de rubrica (0 = alucinado, 1 = fiel) |

### 4.3 Índices

Score de acurácia composta é o **desfecho primário pré-registrado**. Componentes individuais são reportados como desfechos secundários com correção FDR dentro de famílias de testes.

---

## Seção 5 — Plano de Análise

### 5.1 Modelos estatísticos

**Paradigma analítico primário:** GLMM frequentista com tamanhos de efeito + intervalos de confiança 95% (ASA 2016, 2019; Cumming 2014; Lakens 2013).

**Paradigma secundário:** GLMM Bayesiano com priors fracamente informativos via `pymc` e `bambi`, para robustez. Bayes Factors reportados para contrastes críticos (H3a vs H3b).

### 5.2 Transformações

- **Acurácia composta** é contínua em [0,1]; GLMM usa link Gaussiano após verificar normalidade dos resíduos; se violado, transformação logit ou regressão beta.
- **Contagens de tokens** transformadas em log (log1p).
- **Latência de resposta** (secundário) transformada em log.

### 5.3 Especificações dos modelos analíticos

**Modelo H1 (frequentista primário):**
```
composite_accuracy ~ global_south + (1 | country) + (1 | model) + (1 | prompt)
```
Família: Gaussiana (ou beta se resíduos não-normais). Interceptos aleatórios por país, modelo e prompt.

**Modelo H5 (frequentista primário, equivalência TOST):**
```
composite_accuracy ~ tier * global_south + (1 | country) + (1 | model) + (1 | prompt)
```
TOST: H0_low = (closed − open) ≤ −SESOI; H0_high = (closed − open) ≥ SESOI; rejeitar ambos para concluir equivalência.

**Modelo H3 (contraste Bayesiano):**
```
composite_accuracy ~ model_id + language + (1 | prompt)
```
Subset: `country == "BRA"`, `language ∈ {en, pt}`. Modelos: Lince-Mistral, Llama 3.1 8B (comparador). Bayes Factor para Lince > Llama-3.1-8B no subset PT.

**Modelo H4 (regressão ecológica + mediação):**
```
country_accuracy ~ log(cc_tokens) + log(wiki_pageviews) + gdp_per_capita + hdi
```
Mediação via `semopy`: `global_south → log(CC_tokens) → country_accuracy`.

**Modelo H2 (exploratório):**
```
composite_accuracy ~ global_south * is_native_language + joshi_class + (1 | country) + (1 | model)
```
Documentado como exploratório devido a restrições de poder em v2.

### 5.4 Critérios de inferência

- Testes bicaudais, α = 0,05 primário.
- Correção FDR Benjamini-Hochberg (q = 0,05) dentro de cada família de hipótese.
- Tamanhos de efeito: Cohen's *d*, η²_p, IC 95% reportados em todos os testes.
- H3a vs H3b: Bayes Factor > 3 requerido para favorecer uma sobre a outra.

### 5.5 Regras de exclusão de dados (pré-especificadas)

Critérios de exclusão aplicados **antes** da inferência:

1. **Erro de API** (status HTTP ≠ 200 após 3 retentativas): excluir.
2. **Razão de finalização anormal** (`error`, `content_filter`): excluir.
3. **Comprimento de resposta < 10 tokens** em tarefas de geração aberta (T2-T4): excluir como truncado.
4. **Resposta é recusa explícita** (padrões: "I cannot", "I don't have information"): preservada no dataset com flag de análise separada, **excluída do scoring de acurácia**.
5. **Respostas duplicadas** (response_text idêntico para mesmo (país, modelo, prompt, rep)): deduplicar.

Taxa de exclusão esperada: < 3% das respostas. Se > 10% em algum modelo, esse modelo é flagado para análise de sensibilidade.

### 5.6 Dados ausentes

Ausência ao nível de modelo (modelo falha em > 20% das chamadas) → modelo removido da análise primária; incluído na sensibilidade como tier separado.

Ausência ao nível de prompt (um prompt falha em > 3 modelos) → prompt removido da análise primária; flagado em material suplementar.

---

## Seção 6 — Análises Exploratórias (declaradas não-confirmatórias)

As seguintes análises são **explicitamente exploratórias** e serão reportadas como tais:

1. Análise por vendor (removendo o agrupamento por tier): se algum vendor sistematicamente subperforma.
2. Trade-off latência × acurácia.
3. Clustering por família linguística (Romance, Bantu, Indo-Ariana, Austronésia).
4. Análises sub-domínio dentro de D1 Política Pública (e.g., habitação vs licenciamento ambiental).
5. Interações tipo-de-tarefa × país além do fatorial pré-registrado.

---

## Seção 7 — Outros

### 7.1 Protocolo de desvios

Quaisquer desvios pós-registro deste pré-registro serão documentados em uma tabela "Deviation Protocol" no Material Suplementar do manuscrito principal, contendo:
- O que foi modificado
- Por quê (idealmente: calibração informada pelo pilot, disponibilidade de vendor, rate limits)
- Avaliação de impacto
- Se o desvio afeta a inferência confirmatória

### 7.2 Dados / Código abertos

- **Dados:** Todas as 10.500+ respostas depositadas no Zenodo com DOI (CC-BY-4.0) na publicação ou 18 meses após depósito, o que vier primeiro.
- **Código:** Pipeline de análise em https://github.com/Roverlucas/artigo-vies-analise-regional (licença MIT).
- **Prompts e ground truth:** Zenodo (CC-BY-4.0).
- **Arquivo de pesos abertos:** Hashes SHA-256 dos modelos no momento da execução, documentados em `data/model_checkpoints/HASHES.md`.

### 7.3 Conflitos de interesse

Nenhum. Sem relações financeiras com qualquer vendor de LLM. Financiamento: apoio institucional UTFPR/PPGSAU.

### 7.4 Contribuições de autoria (CRediT)

- **LR (Lucas Rover):** Conceptualization, Methodology, Data Curation, Formal Analysis, Writing — Original Draft.
- **YT (Yara Tadano):** Supervision, Methodology Review, Writing — Review & Editing.

---

## Apêndice A — Estudo Piloto de Calibração (Pilot 2.0)

Estudo piloto concluído em 2026-04-23 com 7 países (BRA, NGA, IND, PER, IDN, USA, DEU) × 5 modelos (Claude Haiku 4.5, GPT-5-mini, Gemini 2.5 Flash, Llama 4 Scout 17B, Command R+ 104B) × 10 prompts × 2 réplicas = 700 chamadas. Scoring via Claude Haiku 4.5 como juiz LLM (framework G-Eval, Liu et al. 2023).

**Propósito:** validação de infraestrutura, calibração de SESOI, stress-test da rubrica.

**Resultados do pilot 2.0** (resumo, ver `pilot_findings_v2.md` para detalhes):
- H1 confirmada na direção esperada: Cohen's *d* = +0,34, gap = 6,0pp
- **H5 surpresa:** open Tier A subperforma closed acessível em **12,5pp**
- ICC_country = 0,031; ICC_model = 0,128
- Ranking de países: USA > DEU > IDN > PER > IND > BRA > NGA (Norte estritamente acima de Sul)

**Resultados do pilot são explicitamente NÃO utilizados para inferência confirmatória** — função é exclusivamente atualizar priors de variance components e detectar direção de sinal. O confirmatório usará prompts e modelos potencialmente sobrepostos mas com inferência independente.

### Sobre o incidente metodológico documentado

Durante a execução inicial do pilot 2.0, foi detectada falha sistemática de medição em GPT-5-mini (74 de 91 respostas vazias devido a esgotamento de reasoning_tokens). O incidente foi detectado por validação programada antes de qualquer uso inferencial, dados deprecated foram preservados em arquivo de auditoria (`responses_pilot2_partial_archive/`), e o pilot foi reiniciado com configuração corrigida (`reasoning_effort='minimal'`, `max_completion_tokens=2000`). Documentação completa em `data/pilot_202604/INCIDENT_REPORT_GPT5_EMPTY_RESPONSES.md`.

Este incidente será disclosado em §Methods do manuscrito e detalhado em Suplemento S4. Demonstra que a infraestrutura de medição é apta para uso confirmatório por superficar falhas antes de contaminação inferencial.

---

## Apêndice B — Política do Modelo de Reserva

Claude Opus 4.7 é explicitamente mantido como modelo **de reserva**, **não executado** na coleta confirmatória primária. Justificativa: restrição orçamentária — Opus 4.7 a $0,058/chamada excederia o orçamento Anthropic de US$ 10 se executado em escopo completo (requereria $78+).

O modelo de reserva pode ser **ativado** apenas mediante:
- Pedido de revisor de peer review por "additional closed frontier vendor"
- Aumento orçamentário permitindo inclusão

Se ativado, Opus 4.7 rodará em subset de 3 países × 25 prompts × 2 reps = 150 chamadas (aproximadamente US$ 8,70). Resultados serão reportados como **análise contingente pré-especificada** com flag adequado de "reviewer-requested addition".

Esta contingência é declarada no pré-registro para **prevenir HARKing** via inclusão post-hoc de modelos.

---

## ❓ Perguntas para Lucas decidir antes do depósito OSF

1. **Aprovação de Yara**: ela leu este documento e aprovou o pivot v2.0 (H5 elevada)?
2. **Co-autoria OSF**: Yara entra como co-registrant na página pública do OSF, ou só como aprovadora documentada por email?
3. **Dúvidas técnicas**: alguma seção que você quer que eu clarifique antes do depósito?
4. **Subset Opus na reserva**: 3 países (BRA + USA + IND) está OK, ou prefere outras combinações se ativado?

---

> **Lembrete final:** Esta é a versão **em português para sua leitura pessoal**. A versão que será efetivamente depositada no OSF (em inglês) está em `preregistration/osf_prereg_draft.md`. Se você identificar mudanças necessárias após ler este documento, eu aplico tanto na versão inglês quanto nesta tradução.
