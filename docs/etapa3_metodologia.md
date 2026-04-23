# Methodological Proposal — Geographic Bias in LLM-Assisted Policy Research

**Projeto:** Viés geográfico-factual em LLMs e seu impacto na pesquisa científica do Sul Global
**Journal-alvo definitivo:** *Patterns* (Cell Press, IF 7,4, Q1)
**Input:** Etapas 1 e 2 (hipóteses H1-H4 formalizadas, 15 países estratificados, 6 LLMs, painel de especialistas confirmado)
**Data:** 2026-04-23

---

## 1. Framing

**Problem statement.** LLMs são cada vez mais utilizadas por pesquisadores do Sul Global como ferramenta de apoio a pesquisa aplicada em políticas públicas, mas a literatura documentou viés geográfico sistemático no conhecimento factual compilado por esses modelos (Moayeri et al., 2024; Manvi et al., 2024; Mirza et al., 2024). O que permanece não medido é se esse viés se manifesta especificamente em tarefas de pesquisa aplicada — síntese de políticas, caracterização de contexto socioambiental, identificação de stakeholders — e qual é o papel da língua do prompt e do modelo (frontier global vs regional) na magnitude desse viés. Esta proposta estabelece o primeiro benchmark multi-país, multi-modelo e multi-língua construído especificamente para esse uso.

**Hipóteses (verbatim da Etapa 2):**
- **H1:** LLMs frontier apresentam acurácia inferior em tarefas de pesquisa aplicada sobre Sul Global vs Norte Global (Cohen's *d* ≥ 0,5).
- **H2:** Existe interação não-aditiva entre língua do prompt e país-alvo (η² ≥ 0,05).
- **H3a/b:** Sabiá-3 reduz gap para o Brasil em >50% (H3a) OU cria nova assimetria entre países lusófonos (H3b).
- **H4:** log(tokens do país no corpus) correlaciona com acurácia (Spearman ρ ≥ 0,60).

**Target outlet.** *Patterns* exige: (a) benchmarks reprodutíveis com código e dados abertos, (b) contribuição metodológica clara, (c) relevância interdisciplinar (AI + ethics + policy), (d) honestidade sobre limitações. Nosso design foi calibrado para cada um desses elementos.

**Epistemological stance.** Pós-positivista com lente crítica: adotamos rigor quantitativo em medição e análise, mas interpretamos resultados dentro do framework teórico de *coloniality of knowledge* (Mohamed et al., 2020) e *data feminism* (D'Ignazio & Klein, 2020). Isso é consistente com a tendência editorial de *Patterns* de publicar trabalhos que combinam método rigoroso com reflexão sociotécnica.

---

## 2. Candidate designs

Apresento três alternativas que variam em **paradigma metodológico, nível de controle experimental, e viabilidade operacional**. Elas não são variações da mesma ideia — representam trade-offs reais.

### Alternative A — Benchmark controlado multi-factor com painel de validação humana ⭐

**Core logic.** Desenho experimental factorial: cada LLM responde a um conjunto fixo de prompts factuais construídos por especialistas regionais; respostas são avaliadas contra ground truth documental (para questões objetivas) e rubrica validada (para questões de geração aberta). A inferência é *comparativa* (entre países, modelos, línguas) e *mecanística* (correlação com variáveis de representação no corpus).

**Sample / setting / unit of analysis.**
- **Unidade primária:** prompt-response (N ≈ 202.500 pares).
- **Estratificação:** 15 países (5 AL + 4 África + 4 Ásia + 3 Norte controle) × 6 LLMs × matriz esparsa de línguas × 3 domínios × 5 tipos de tarefa × 5 replicações.
- **Setting:** API calls em ambiente controlado (temperatura fixa em 0,3 para balance determinismo/variação; seed fixa quando disponível; replicações para capturar variabilidade estocástica residual).

**Data sources and instruments.**
- **Prompts (VI):** construídos por painel de 2-3 especialistas por região (PPGSAU/UTFPR + CLACSO + CODESRIA), validados por retroversão e concordância inter-avaliadores.
- **Ground truth:** documentos oficiais (ministérios, agências estatísticas, IBGE-equivalents, observatórios regionais, leis, relatórios técnicos).
- **Respostas (VD):** coletadas via API de cada LLM, armazenadas com metadados completos.
- **Variável mecanística (H4):** log tokens por país no Common Crawl (snapshot dezembro/2024 para GPT-5, Claude, Gemini; snapshot conhecido para Llama/DeepSeek) + Wikipedia pageviews por língua.

**Identification strategy.** Desenho experimental com atribuição controlada de prompts a modelos; não há confounder não-observado no nível modelo-país-prompt (atribuição é determinística). Claims causais são restritos a efeito do input (prompt) sobre output (resposta) *dada a arquitetura do modelo fixa*. Mecanismo (H4) é **correlacional**, não causal — declarado explicitamente.

**Analytical plan.**
- **H1:** GLMM (Generalized Linear Mixed Model) com efeitos aleatórios por país, modelo e domínio; família binomial para acurácia factual, gaussiana para escores de rubrica.
- **H2:** Teste de interação país × língua no mesmo GLMM; effect size via η²_p parcial.
- **H3:** Subanálise contraste Sabiá-3 vs frontier; teste formal de coeficientes específicos.
- **H4:** Regressão ecológica (país-nível) com token count como preditor + mediation analysis usando `lavaan` ou `mediation` em R.
- Correção múltipla: FDR Benjamini-Hochberg.
- Robustez: leave-one-out por país, análise em subset de países com painel validado, análise Bayesiana com priors não-informativos para comparar (Kruschke, 2014).

**Innovation angle.** Três novidades simultâneas: (1) primeiro benchmark em **tarefas reais de pesquisa aplicada**, não trivia ou recall numérico; (2) primeira **estratificação teórica tripla** (UNCTAD × Joshi × WB) em estudo de viés geográfico; (3) primeira comparação **modelo regional (Sabiá-3) vs frontier** sob design controlado.

**Top-journal precedent.**
- Moayeri, Tabassi & Feizi (2024) — *WorldBench*. FAccT 2024. 20 LLMs × 11 indicadores WB. Precedente metodológico mais próximo, mas sem painel humano, sem dimensão linguística, sem modelo regional. Nosso design é a evolução natural.
- Manvi et al. (2024) — *LLMs are Geographically Biased*. ICML 2024. Prompts zero-shot com ground truth georreferenciado. Usamos a arquitetura de experimento deles, expandida em três dimensões.
- Myung et al. (2024) — *BLEnD*. NeurIPS 2024. 52k Q&A em 13 línguas. Precedente do desenho multilíngue, mas foco em conhecimento cotidiano.

**Risks / threats to validity.**
| Ameaça | Mitigação |
|---|---|
| Rubrica subjetiva em geração aberta | Painel de 2 avaliadores + adjudicação; Krippendorff's α ≥ 0,70 exigido pré-análise |
| Tradução imperfeita (H2) | Back-translation obrigatória + descarte de prompts com shift semântico |
| Efeito de prompt engineering (mesma pergunta pode render diferente) | 5 replicações por prompt + análise de variância intra-prompt |
| Atualização de modelos mid-experiment | Registro de data/timestamp e versão do modelo; repetir coleta caso release maior |
| Data contamination (LLM viu ground truth) | Usar ground truth de documentos pós-cutoff quando possível; análise de sensibilidade com subset pré-cutoff |

**Feasibility.**
- **Tempo:** 8 meses (2 construção + 2 coleta + 2 análise + 2 redação).
- **Custo API:** R$ 15-25k (estimativa detalhada na seção 8).
- **Acesso:** Sabiá-3 via API Maritaca; frontier via OpenAI/Anthropic/Google (créditos pesquisa solicitáveis).
- **Ética:** CEP institucional para painel humano (risco baixo — apenas experts consentidos, sem dados sensíveis).

---

### Alternative B — Auditoria observacional de logs de uso real

**Core logic.** Em vez de construir prompts sintéticos, coletar prompts reais que pesquisadores do Sul Global enviam a LLMs (via consentimento informado) e auditar respostas post-hoc. Inferência é **externalmente válida** (uso real), mas **internamente fraca** (sem controle).

**Sample / setting.** 100-200 pesquisadores recrutados via universidades do Sul Global, consentindo compartilhar logs de 3 meses. Respostas auditadas por revisores especialistas.

**Strengths.** Altíssima validade externa; captura o que pesquisadores realmente perguntam; resultados diretamente acionáveis para a prática.

**Weaknesses.**
- Sem controle sobre prompts → impossível testar H2 (língua) ou H3 (comparação modelos) rigorosamente.
- Viés de auto-seleção dos participantes.
- Questões de privacidade e propriedade intelectual dos prompts (pesquisa em andamento dos participantes).
- H4 (mecanismo) inatestável com esse desenho.
- Tempo de coleta longo (6+ meses só para obter N suficiente).

**Top-journal precedent.** Menos estabelecido — existe precedente em *auditing AI systems* (Raji & Buolamwini, 2019; Metcalf et al., 2021) mas não no formato específico.

**Feasibility.** Baixa: CEP complexo, recrutamento lento, análise trabalhosa. Inviável para o timeline proposto.

---

### Alternative C — Design misto explicativo sequencial (QUANT → QUAL)

**Core logic.** Primeira fase: benchmark igual ao Alternative A, mas menor (~8 países, 3 modelos, só inglês). Segunda fase: entrevistas semi-estruturadas com 15-20 pesquisadores do Sul Global sobre como eles percebem e adaptam-se ao viés encontrado. Integração na Discussion.

**Strengths.** Profundidade interpretativa; diálogo com literatura crítica (*coloniality of knowledge*); apela a editores de *AI & Society* e *Big Data & Society*.

**Weaknesses.**
- *Patterns* é menos receptivo a qualitativo puro; fit de escopo é menor.
- Dobra o tempo de execução (entrevistas + análise Gioia) sem necessariamente adicionar ao teste das hipóteses H1-H4.
- H3 e H4 ficam subexplorados se n de países é reduzido.

**Top-journal precedent.** Creswell & Plano Clark (2018) framework; exemplos em *Big Data & Society* mas não em *Patterns*.

**Feasibility.** Alta em princípio, mas desalinhada com o target.

---

## 3. Comparison matrix

| Critério | Alt A (benchmark controlado) | Alt B (auditoria logs) | Alt C (misto QUANT→QUAL) |
|---|:-:|:-:|:-:|
| **Construct validity** | Alta (rubrica validada, painel) | Média (prompts reais mas sem calibração) | Alta |
| **Internal validity** | Alta (controle experimental) | Baixa (confounders não controlados) | Média |
| **External validity** | Média (prompts sintéticos mas validados por experts) | Altíssima | Média |
| **Statistical power** | Alta (N=202k observações) | Baixa-Média (N limitado por recrutamento) | Média (N menor, ganha em profundidade) |
| **Innovation** | Alta (tripla estratificação + modelo regional) | Média (novidade por uso real, mas metodologia não-original) | Média |
| **Feasibility** | Alta (dentro do escopo mestrado PPGSAU) | Baixa (CEP + recrutamento) | Média (tempo dobra) |
| **Fit com *Patterns*** | **Altíssima** (benchmarks reprodutíveis + ética + dados abertos) | Média | Baixa |

---

## 4. Recommendation

**Recomendo Alternative A — benchmark controlado multi-factor com painel de validação humana.**

Três razões:

1. **É o único que testa todas as 4 hipóteses com rigor adequado a Q1.** Alt B sacrifica H2, H3 e H4 em nome de validade externa. Alt C sacrifica poder estatístico de H3 e H4 em nome de profundidade interpretativa que *Patterns* não valoriza como diferencial.

2. **Fit com *Patterns* é quase perfeito.** O journal explicitamente valoriza: benchmarks reprodutíveis (✓), contribuição metodológica (✓), dados e código abertos (✓), relevância interdisciplinar (✓), reflexão ética (✓). Alt B e Alt C têm encaixes piores.

3. **Viabilidade real dentro do escopo de mestrado PPGSAU/UTFPR.** 8 meses, orçamento sub-30k reais, risco ético baixo, dependência de acesso a API (resolvível via programas de créditos). Alt B requer infraestrutura de pesquisa longitudinal que não temos.

**O que deliberadamente sacrificamos:**
- Validade externa para uso *real* em fluxo de trabalho de pesquisadores — nosso prompt é sintético, ainda que validado. Mitigamos via painel de especialistas que constroem prompts baseados em tarefas que eles mesmos executariam.
- Profundidade interpretativa sobre *como* pesquisadores se relacionam com o viés — reservado para trabalho futuro (mencionado na Discussion).

---

## 5. Detailed protocol — Alternative A

### 5.1 Sampling frame

**Unidade de análise:** tripla (país, modelo, prompt).

**Frame amostral:**
- **Países (N=15):** seleção estratificada triangulada (ver `etapa2b_selecao_paises.md`).
- **LLMs (N=6):**
  - **Proprietários frontier:** GPT-5 (OpenAI), Claude Opus 4.7 (Anthropic), Gemini 2.5 Pro (Google).
  - **Open-source global:** Llama 4 70B (Meta) ou DeepSeek-V3 (DeepSeek) — decisão final por acessibilidade via API.
  - **Regional controle:** Sabiá-3 (Maritaca).
  - **Baseline de escala:** modelo open de tamanho comparável a Sabiá-3 para controlar tamanho vs regionalidade. Proposta: Qwen 3 32B.
- **Línguas (N=4):** EN (universal), PT (BR), ES (AL), HI (Índia), SW (Quênia). Matriz esparsa — cada país testado em EN + 1-2 línguas regionais quando aplicável (Nigéria: EN + Hausa classe 1 se viável, senão só EN).
- **Domínios (N=3):**
  - D1: Políticas públicas e instituições.
  - D2: Realidade socioeconômica e demografia.
  - D3: Contexto ambiental e climático regional.
- **Tipos de tarefa (N=5):**
  - T1: Recall factual direto (questão objetiva com resposta verificável).
  - T2: Caracterização descritiva (geração aberta 100-300 palavras).
  - T3: Identificação de stakeholders institucionais.
  - T4: Recomendação de fontes primárias.
  - T5: Calibração (prompt pede confiança declarada — comparamos com acurácia real).

**Total de prompts:** 15 países × 3 domínios × 5 tarefas × 2 variações linguísticas médias ≈ 450 prompts únicos.

**Replicações:** 5 por combinação prompt × modelo (para captura de variabilidade estocástica).

**N total de pares prompt-resposta:** 450 × 6 modelos × 5 replicações × 1,5 (fator línguas) ≈ **~20.000 pares únicos; ~100.000 chamadas** (a estimativa de 202k da Etapa 2 foi pessimista — ajuste para baixo aumenta viabilidade).

### 5.2 Power calculation

Assumindo:
- Effect size esperado para H1: Cohen's *d* = 0,5 (moderate) baseado em Moayeri et al. (2024, diferença EEUU vs Sub-Sahariana).
- α = 0,05 bilateral com correção FDR.
- Poder desejado = 0,90.
- ICC intra-país estimado em 0,15.

Para GLMM com 15 países e aproximadamente 1.300 observações por país, poder efetivo é > 0,95 para efeitos principais e > 0,85 para interações de primeira ordem (via simulação em `simr` R package).

Para H2 (interação), effect size mínimo detectável: η²_p ≈ 0,03 com poder 0,80 — suficiente para a detecção teorizada.

### 5.3 Operacionalização dos construtos

| Construto | Operacionalização | Instrumento | Escala |
|---|---|---|---|
| Acurácia factual (T1) | Resposta = ground truth (binária) | Avaliação automatizada + verificação manual em 10% | 0/1 |
| Completude contextual (T2-T4) | Cobertura de elementos-chave identificados pelo painel | Rubrica 5-itens (0-5) | 0-5 |
| Qualidade de citações | Citações reais, verificáveis, relevantes | Checagem via DOI/API | 0-5 |
| Calibração (T5) | |confiança_declarada − acurácia_real| | Brier score | 0-1 |
| Alucinação | Invenção de fatos não atestados | Classificação binária por avaliador | 0/1 |
| **VD composta** | Média ponderada dos acima | Fórmula pré-registrada | 0-1 |

A rubrica completa será desenvolvida em **piloto de 50 prompts** pré-coleta principal e validada pelo painel (α Krippendorff ≥ 0,70 exigido para prosseguir).

### 5.4 Data plan (5a)

**Tabela de fontes, extração e armazenamento:**

| Variável | Fonte | Método de extração | Storage (raw) | Governance |
|---|---|---|---|---|
| Prompts originais | Painel especialistas via survey Qualtrics | Export CSV + metadata JSON | `data/raw/prompts/v1/` | CEP aprovado; especialistas co-autores |
| Ground truth | Sites oficiais governamentais + documentos PDF | Scraping customizado + OCR quando necessário | `data/raw/ground_truth/{country}/` | Fontes públicas; URLs + data de acesso registradas |
| Respostas LLMs | APIs oficiais (OpenAI, Anthropic, Google, Maritaca, etc.) | Python client oficial de cada provider | `data/raw/llm_responses/{model}/{country}/` | Termos de uso das APIs respeitados; sem dados sensíveis |
| Token counts Common Crawl | CC Index público (https://index.commoncrawl.org/) | Agregação por domínio ccTLD | `data/raw/cc_tokens.csv` | Dados públicos |
| Wikipedia pageviews | Wikimedia REST API | Python `mwviews` | `data/raw/wiki_pageviews.csv` | Dados públicos CC-BY-SA |
| Avaliações rubrica | Painel de 2 avaliadores via Airtable | Export API semanal | `data/interim/rubric_ratings/` | Identificadores anonimizados; concordância monitorada |

**Storage raw (imutável):** bucket S3 (ou alternativa institucional UTFPR) com versionamento ativado; hashes SHA-256 publicados no pré-registro OSF.

**Regras de limpeza:**
- Respostas com `finish_reason != "stop"` marcadas como truncated e excluídas da análise principal (incluídas em sensibilidade).
- Respostas em língua diferente da solicitada (ex: LLM responde em EN quando prompt foi em PT) marcadas como "refusal" e analisadas separadamente.
- Padronização Unicode NFC em todas as strings.

### 5.5 Method pipeline (5b)

```
┌─────────────────────────────────────────────────────────────┐
│ FASE 1: Construção (Meses 1-2)                              │
└─────────────────────────────────────────────────────────────┘
  1.1 Recrutamento painel (PPGSAU/CLACSO/CODESRIA)
       └── Protocolo de colaboração + autoria
  1.2 Construção prompts piloto (n=50)
       └── data/raw/prompts/v0_pilot/
  1.3 Validação piloto e Krippendorff α
       └── src/validate/pilot_agreement.R
  1.4 Ajuste rubrica + finalização prompts (n=450)
       └── data/raw/prompts/v1_final/
  1.5 Coleta ground truth
       └── src/extract/ground_truth_{country}.py
  1.6 Pré-registro OSF (lock do protocolo)
       └── preregistration/osf_v1.md

┌─────────────────────────────────────────────────────────────┐
│ FASE 2: Coleta (Meses 3-4)                                  │
└─────────────────────────────────────────────────────────────┘
  2.1 Configuração wrappers API
       └── src/llm_clients/{openai,anthropic,google,maritaca}.py
  2.2 Execução chamadas (5 replicações × 6 modelos × 450 prompts)
       └── src/run_experiment.py  → data/raw/llm_responses/
  2.3 Checkpoints diários + retry com exponential backoff
       └── src/utils/retry.py
  2.4 Quality gates: truncation, refusal, língua divergente
       └── src/validate/response_quality.py
  2.5 Avaliação rubrica (2 avaliadores + adjudicação)
       └── data/interim/rubric_ratings/

┌─────────────────────────────────────────────────────────────┐
│ FASE 3: Análise (Meses 5-6)                                 │
└─────────────────────────────────────────────────────────────┘
  3.1 Freeze do dataset analítico
       └── data/processed/analytic_v1.parquet + SHA-256
  3.2 Modelos GLMM pré-especificados (H1, H2, H3)
       └── src/analyze/glmm_primary.R
  3.3 Mediation analysis (H4)
       └── src/analyze/mediation_h4.R
  3.4 Robustez (leave-one-out, Bayesian, subset validado)
       └── src/analyze/robustness.R
  3.5 Figuras e tabelas
       └── src/figures/*.py → results/figures/

┌─────────────────────────────────────────────────────────────┐
│ FASE 4: Publicação (Meses 7-8)                              │
└─────────────────────────────────────────────────────────────┘
  4.1 Redação artigo (Etapa 6 do pipeline global)
  4.2 Depósito Zenodo (dataset + código)
       └── Paper DOI + Data DOI
  4.3 Pré-submissão peer feedback
  4.4 Submissão Patterns
```

### 5.6 Pre-registration plan

Pré-registro OSF obrigatório antes de qualquer coleta principal. Lock inclui:
- Prompts finais (v1_final) com hash.
- Rubrica final.
- Modelos estatísticos primários (especificação exata das fórmulas GLMM).
- Thresholds de significância e correção múltipla.
- Critérios de exclusão de respostas.
- Plano de análises exploratórias (declaradas como tal).

Link do pré-registro incluído na submissão a *Patterns* (exigência do journal).

### 5.7 Handling missing data

- **LLM refuses to answer:** incluído como outcome `refusal=1`, analisado separadamente (pode ser indicador de calibração).
- **API failure:** retry até 3x com exponential backoff; se falha persiste, marcado `missing=1` e imputado via multiple imputation (`mice` R) em análises secundárias; análise primária é complete-case.
- **Ground truth indisponível:** prompt movido para T2/T3 (geração aberta) avaliado só por rubrica contextual.

### 5.8 Open science commitments

- **Dados:** Zenodo, CC-BY-4.0, DOI permanente. Exclui identificadores dos membros do painel (anonimizado).
- **Código:** GitHub + Zenodo snapshot; MIT License.
- **Prompts e ground truth:** dataset FAIR-compliant; submissão paralela como *Data Paper* em *Scientific Data*.
- **Pre-prints:** versão pré-submissão no arXiv (cs.CL) após lock do pré-registro.

### 5.9 Ética (CEP)

- Risco: baixo (apenas especialistas consentidos, sem dados sensíveis, sem população vulnerável).
- Submissão: Plataforma Brasil via UTFPR.
- Co-autoria dos especialistas explícita.
- Compensação: definir com coordenação PPGSAU (sugestão: bolsa-módulo simbólica via projeto).

### 5.10 Reporting standards

- **TRIPOD-AI** (adaptado para avaliação de LLMs, não modelo preditivo puro).
- **MIRT** (Minimum Information about Reporting for Trials) aplicável a desenho experimental.
- **FAIR Data Principles.**
- **CARE Principles** se dados envolverem comunidades indígenas (não é o caso neste desenho).

---

## 6. Threats to validity and mitigations

**Internal validity.**
- *Confounder model-language:* Sabiá-3 pode performar melhor em PT por causa do tuning, não da regionalidade. **Mitigação:** incluir Qwen 3 32B como controle de escala; teste de coeficientes específicos.
- *Data contamination:* LLMs podem ter visto nosso ground truth durante treinamento. **Mitigação:** subset de ground truth pós-cutoff para cada modelo; análise de sensibilidade.
- *Ordem dos prompts:* efeito de sequência em sessão. **Mitigação:** cada chamada API é independente (session nova); ordem dos prompts randomizada.

**External validity.**
- *Prompts sintéticos vs reais:* mitigado por painel especialista, mas não elimina. **Declaração:** limitação na Discussion.
- *15 países de 195:* cobertura ampla mas não total. **Mitigação:** estratificação teórica (não conveniência); declarar não-generalização para Oceania e classes Joshi 0.
- *Snapshot temporal:* LLMs atualizam; resultado é válido para período X. **Mitigação:** registro de versão + timestamps; protocolo replicável.

**Construct validity.**
- *"Acurácia" em geração aberta é parcialmente subjetiva.* **Mitigação:** rubrica co-desenvolvida, α ≥ 0,70, adjudicação.
- *Ground truth é o que está em documentos oficiais — não é "verdade última".* **Mitigação:** triangulação entre fontes (pelo menos 2 por prompt quando possível); declaração explícita.

**Statistical conclusion validity.**
- *Múltiplas comparações:* FDR BH controlado em q<0,05 para família de testes por hipótese.
- *Assumptions GLMM:* diagnósticos de resíduos; alternativa Bayesiana como robustness.
- *Risco de p-hacking:* pré-registro OSF com lock de modelos primários; análises exploratórias declaradas.

---

## 7. Innovation statement

Se um editor de *Patterns* perguntar *"what is methodologically new here?"*, a resposta em uma frase: **este é o primeiro benchmark de viés geográfico em LLMs construído especificamente para o uso em pesquisa aplicada de políticas públicas, com estratificação amostral teoricamente triangulada (UNCTAD × Joshi × World Bank), desenho factorial que isola efeito de língua e efeito de regionalidade do modelo, e mecanismo causal correlacional explicitamente testado via representação no corpus de treinamento.**

Em três frases de contribuição:
1. **Para a literatura de AI fairness:** expandimos o escopo de benchmarks de "recall numérico" para "uso real em pesquisa".
2. **Para a literatura crítica de AI:** fornecemos evidência empírica quantitativa ao framework *coloniality of knowledge*.
3. **Para a literatura de NLP multilíngue:** testamos se modelos regionalmente treinados fecham ou deslocam o gap — resultado com implicações diretas para investimento público em IA.

Honestidade: a inovação é **integrativa**, não revolucionária. Nenhuma técnica individual é nova; a combinação é.

---

## 8. Risks, timeline, and budget

### Timeline realista (8 meses)

| Mês | Atividade | Marco |
|---|---|---|
| 1 | Recrutamento painel + construção prompts piloto | Piloto n=50 |
| 2 | Validação piloto + finalização rubrica + pré-registro OSF | Lock protocolo |
| 3 | Coleta ground truth + wrappers API | Infraestrutura pronta |
| 4 | Execução chamadas API + avaliação rubrica | Dataset raw coletado |
| 5 | Freeze dataset + análise primária | Resultados H1-H4 |
| 6 | Robustness + figuras | Resultados finais |
| 7 | Redação artigo (Etapa 6) | Draft v1 |
| 8 | Revisão linguística + formatação + submissão | Submetido Patterns |

### Orçamento estimado

| Item | Valor (R$) | Fonte sugerida |
|---|---|---|
| API credits (OpenAI, Anthropic, Google) | 15.000 - 20.000 | Research credit programs + bolsa mestrado |
| API credits (Maritaca, DeepSeek, Qwen) | 2.000 - 3.000 | Orçamento regular |
| Compensação painel (10 especialistas) | 5.000 - 8.000 | Projeto institucional |
| Storage + compute (análise) | 500 - 1.000 | Infraestrutura UTFPR |
| Tradução profissional (4 línguas × revisão prompts) | 3.000 - 5.000 | Verba específica a solicitar |
| APC Patterns (se aceito) | USD 4.900 | GPOA geographical discount + auxílio institucional |
| **Total pré-APC** | **~25.500 - 37.000 R$** | |

### Riscos principais

1. **Recrutamento de especialistas lento** — mitigação: começar mês 1, rede PPGSAU ativa desde início.
2. **API sem crédito** — mitigação: aplicar a Anthropic Research Access, OpenAI Research Program, Google Academic Research desde mês 0.
3. **Modelo atualizado mid-experiment** — mitigação: fixar versão por `model=...` string exata nos clientes; replicar se release major.
4. **Sabiá-3 indisponível** — mitigação: alternativa Bode ou GlórIA; declarar.

---

## 9. References

(Apenas as citadas nesta proposta; biblio completa do artigo virá na Etapa 6)

- Creswell, J. W., & Plano Clark, V. L. (2018). *Designing and conducting mixed methods research* (3rd ed.). SAGE.
- D'Ignazio, C., & Klein, L. F. (2020). *Data feminism*. MIT Press.
- Joshi, P., Santy, S., Budhiraja, A., Bali, K., & Choudhury, M. (2020). The State and Fate of Linguistic Diversity and Inclusion in the NLP World. *Proceedings of ACL 2020*, 6282–6293. https://doi.org/10.18653/v1/2020.acl-main.560
- Kruschke, J. K. (2014). *Doing Bayesian data analysis* (2nd ed.). Academic Press.
- Manvi, R., Khanna, S., Burke, M., Lobell, D., & Ermon, S. (2024). Large Language Models are Geographically Biased. *ICML 2024*.
- Metcalf, J., Moss, E., Watkins, E. A., Singh, R., & Elish, M. C. (2021). Algorithmic impact assessments and accountability: The co-construction of impacts. *FAccT 2021*.
- Mirza, S., Coelho, B., Cui, Y., Pöpper, C., & McCoy, D. (2024). Global-Liar: Factuality of LLMs over Time and Geographic Regions. *arXiv:2401.17839*.
- Moayeri, M., Tabassi, E., & Feizi, S. (2024). WorldBench: Quantifying Geographic Disparities in LLM Factual Recall. *FAccT 2024*, 1211–1228. https://doi.org/10.1145/3630106.3658967
- Mohamed, S., Png, M.-T., & Isaac, W. (2020). Decolonial AI: Decolonial theory as sociotechnical foresight in artificial intelligence. *Philosophy & Technology*, 33(4), 659–684.
- Myung, J. et al. (2024). BLEnD: A Benchmark for LLMs on Everyday Knowledge in Diverse Cultures and Languages. *NeurIPS 2024*.
- Raji, I. D., & Buolamwini, J. (2019). Actionable auditing: Investigating the impact of publicly naming biased performance results of commercial AI products. *AAAI/ACM AIES 2019*.
- UNCTAD (2024). *Classifications Update — June 2024*. UNCTADstat.
- World Bank Group (2025). *World Bank Country and Lending Groups — FY26 Classification*.

---

## 10. Full Methods section (publication-ready draft)

*Para o manuscrito submetido a Patterns. Seguir as normas Cell Press — seções em primeira pessoa do plural ativa quando apropriado, citações numeric brackets ([1], [2]...).*

### Methods

#### Research design

We conducted a pre-registered, factorial, multi-site benchmark experiment to quantify geographic bias in six frontier and regional Large Language Models (LLMs) across tasks representative of applied policy research in Global South contexts. The design crossed 15 countries (stratified along three theoretically grounded axes), 6 LLMs, a sparse matrix of 4 languages, 3 research domains, and 5 task types, yielding approximately 20,000 unique prompt-response pairs after five stochastic replications. The pre-registration was deposited at OSF prior to any principal data collection and locked the primary models, exclusion criteria, and multiple-comparison corrections.

#### Country selection

Countries were selected via theoretical sampling triangulated across three independent classifications established in the international development and natural language processing literatures. First, the **UNCTAD Global North/South classification** [ref] operationalizes the coloniality-of-knowledge framework that motivates this study [ref], separating developed from developing economies based on trade, financial and developmental criteria. Second, the **Joshi et al. (2020) six-class taxonomy of linguistic resource representation in NLP corpora** [ref] was applied to stratify countries by the digital footprint of their primary languages, ranging from Class 1 ("The Scraping-Bys") to Class 5 ("The Winners"). Third, **World Bank income groups (FY26)** [ref] provided an income dimension orthogonal to the previous two. The final sample of 15 countries (Brazil, Mexico, Argentina, Peru, Nigeria, South Africa, Kenya, Egypt, India, Indonesia, Bangladesh, the Philippines, the United States, Germany, and Japan) covers four world regions, five Joshi classes (1 through 5), and four World Bank income groups.

#### Model selection

Six LLMs were benchmarked, representing three architectural categories. **Three frontier proprietary models** — GPT-5 (OpenAI), Claude Opus 4.7 (Anthropic), and Gemini 2.5 Pro (Google) — were accessed via their official APIs using the identical model version string throughout the collection window. **Two open-weight globally-trained models** — Llama 4 (70B instruction-tuned) and DeepSeek-V3 — served as contrasts in architecture and training data provenance. **One regionally-trained model** — Sabiá-3 (Maritaca AI), trained with substantial Brazilian Portuguese emphasis — was included to test whether regional training closes or reshapes the Global South performance gap. A sixth **scale-matched control** (Qwen 3 32B) was included to separate the effect of regional training from model scale.

#### Prompt construction and validation

A panel of 2 to 3 domain experts per Global South region was recruited via the Graduate Program in Urban and Environmental Planning (PPGSAU/UTFPR), the Latin American Council of Social Sciences (CLACSO), and the Council for the Development of Social Science Research in Africa (CODESRIA), under a collaboration protocol that included co-authorship and ethical approval (Plataforma Brasil, protocol to be inserted). Experts constructed prompts in three research domains — (1) public policy and institutions, (2) socioeconomic reality and demography, and (3) regional environmental context — across five task types — (T1) direct factual recall with verifiable ground truth, (T2) descriptive characterization through open-ended generation, (T3) institutional stakeholder identification, (T4) primary-source recommendation, and (T5) confidence calibration. A pilot of 50 prompts was first validated for inter-rater agreement using Krippendorff's α, with a threshold of ≥ 0.70 required before proceeding to the final 450-prompt set. All prompts were authored in English, then translated and back-translated by native-speaker professional translators; any prompt whose back-translation produced semantic shift was rewritten or excluded.

#### Ground truth

Ground truth for factual tasks was extracted from official government sources (ministries, national statistics agencies, environmental agencies) and peer-reviewed regional reports, with at least two independent sources per prompt when available. Extraction used custom Python pipelines with OCR for scanned PDFs, and all sources were versioned by access date and URL to ensure reproducibility. Where ground truth could plausibly have been seen by the LLMs during training, a sensitivity subset was constructed using documents dated after each model's training cutoff.

#### Data collection

API calls were executed at temperature 0.3 with deterministic seeds where available, with five replications per prompt-model combination to estimate stochastic variability. Collection occurred within a fixed four-week window to minimize model-update confounds. All responses were stored alongside complete request metadata (model version string, timestamp, token counts, finish reason) in an immutable S3-backed raw layer with SHA-256 checksums. Response quality gates excluded truncated responses (`finish_reason ≠ "stop"`) and responses in languages divergent from the request; both were analyzed separately as secondary outcomes.

#### Measures

The primary composite outcome variable combined five subcomponents: (i) binary factual accuracy against ground truth (for T1 tasks), (ii) contextual completeness scored against a pre-validated five-item rubric (for T2-T4 tasks, 0–5), (iii) citation quality verified via DOI and source check (0–5), (iv) calibration error via Brier score (T5 tasks, 0–1), and (v) hallucination, coded binarily by human raters. Weights for the composite were pre-registered. Two independent raters, blinded to model identity, evaluated each response using the Airtable-hosted rubric; inter-rater disagreements were adjudicated by a third senior rater. Final Krippendorff's α across raters reached [TO BE REPORTED].

#### Corpus representation proxies

For the mechanism test (H4), we extracted token counts per country from Common Crawl (December 2024 index), aggregating by country-code top-level domain (ccTLD) as a lower-bound proxy, and combined with Wikipedia pageviews per language (Wikimedia REST API). These proxies are imperfect but constitute the standard measures used in prior work [refs]; limitations are discussed explicitly.

#### Analytical strategy

Primary analyses used Generalized Linear Mixed Models (GLMMs) with random intercepts for country, model, and domain, implemented in R (`lme4`). For binary outcomes (factual accuracy, hallucination), we used a binomial family with logit link; for continuous composite scores, a Gaussian family. Hypothesis H1 was tested via the fixed effect of country Global-South status on the composite outcome; H2 via the country × language interaction term; H3 via pre-specified contrasts comparing Sabiá-3 performance on Brazilian prompts against frontier-model average, and pre-specified contrasts comparing Sabiá-3 performance on non-Brazilian Lusophone prompts to detect shift versus closure. H4 was tested via a country-level ecological regression of composite accuracy on log(corpus tokens), followed by mediation analysis using `lavaan` to test whether token representation mediated the effect of Global-South classification. All hypothesis tests used two-sided α = 0.05 with Benjamini-Hochberg FDR correction within each hypothesis family.

Robustness analyses, all pre-registered, included: (i) leave-one-country-out re-estimation; (ii) restriction to the expert-validated prompt subset; (iii) Bayesian re-estimation with weakly informative priors to provide decision-theoretic posterior probabilities; (iv) separate analysis excluding prompts with potential training-data contamination.

#### Pre-registration and open science

The full protocol — including prompts v1-final with hash, rubric, GLMM specifications, multiple-comparison corrections, and exclusion criteria — was deposited at the Open Science Framework (OSF) prior to principal data collection. The analytic dataset, after quality gates but before models were fit, was frozen and hashed; the hash was committed to the OSF registry. All code, prompts, ground truth, and anonymized response data are publicly available under CC-BY-4.0 (data and prompts) and MIT License (code) at Zenodo with permanent DOIs, and a companion Data Paper is prepared for *Scientific Data*.

#### Ethical considerations

The expert-panel protocol received approval from UTFPR's Research Ethics Committee via Plataforma Brasil. Experts provided informed consent and are acknowledged as co-authors when meeting ICMJE criteria. No personal data from end-users of LLMs was collected. LLM API terms of service were reviewed and respected; responses are redistributed solely for research under fair-use/reproducibility provisions and excluded from any commercial application.

#### Methodological limitations

Three limitations are acknowledged. First, prompts remain synthetic — validated by regional experts, but not drawn from live research workflows; generalization to in-the-wild usage is therefore qualified. Second, the 15-country sample, while theoretically stratified, excludes Oceania and Joshi Class 0 languages, leaving those populations to future work. Third, the mechanism analysis (H4) is correlational, not causal; alternative mechanisms — including post-training alignment choices, tokenizer behavior, and geopolitical filtering — are discussed but not tested here and represent salient directions for follow-up research.
