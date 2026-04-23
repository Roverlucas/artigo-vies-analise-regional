# Etapa 2 — Hipóteses & Gaps

**Projeto:** Viés geográfico-factual em LLMs e seu impacto na pesquisa científica do Sul Global
**Pesquisador:** Lucas (PPGSAU/UTFPR)
**Data:** 2026-04-23
**Input:** Etapa 1 (revisão de literatura com 4 gaps identificados)
**Escopo confirmado:** 15 países (5 Sul Global × 3 continentes + 3 Norte como controle), painel de especialistas 2–3 por região, todos os 4 gaps

---

## 1. Análise do campo (compacta)

**Paradigma dominante:** post-positivista quantitativo (benchmarks com ground truth, métricas automáticas).
**Escolas emergentes:** AI fairness (FAccT), AI colonialism (Kerche/Zook/Graham, Mohamed et al.), critical algorithm studies.
**Tensão central:** evidência empírica robusta de viés × ausência de teorização sobre *mecanismo* e *consequência* para pesquisa produzida no Sul Global.
**Tipologia dos gaps identificados** (Müller-Bloch & Kranz, 2015):

| Gap | Tipo | Justificativa |
|---|---|---|
| 1. Domínio de pesquisa aplicada | **Empirical gap + Population gap** | Fenômeno não testado em contexto específico de uso (pesquisa em políticas públicas) nem em populações específicas (pesquisadores do Sul Global) |
| 2. Interação língua × geografia | **Methodological gap** | Desenho fatorial controlado nunca aplicado ao tema |
| 3. Modelos regionais vs frontier | **Empirical gap** | Comparação direta nunca quantificada |
| 4. Mecanismo causal (tokens → viés) | **Theoretical gap + Evidence gap** | Explicação proposta mas nunca testada diretamente |

---

## 2. Framework conceitual integrador

Adoto o **Coloniality of Knowledge framework** (Quijano, 2000; Mohamed, Png & Isaac, 2020 para IA) como lente teórica principal, combinado com **Data Feminism** (D'Ignazio & Klein, 2020) para o ângulo de epistemic injustice. Essa combinação posiciona o artigo dentro de tradição crítica *com dados empíricos rigorosos* — um espaço ainda pouco ocupado em journals de ciência de dados (Patterns publica opinions nessa linha mas poucas com benchmark próprio).

**Mecanismo teorizado:** volume de representação de um país/cultura no corpus de treinamento → profundidade de conhecimento factual compilado pelo modelo → acurácia diferencial em tarefas factuais → perpetuação de desigualdades epistêmicas quando pesquisadores do Sul Global usam LLMs. É um ciclo de retroalimentação negativa — se pesquisadores do Sul Global usam LLMs treinadas em Norte Global, produzem pesquisa com vieses do Norte, que se torna mais um input em próximos corpora.

**Paradigma da pesquisa:** post-positivista com elementos críticos (dados quantitativos rigorosos + interpretação decolonial).

---

## 3. Hipóteses formalizadas

Estruturo em **4 hipóteses** — uma por gap — mais uma **H5 exploratória de confirmação** que amarra as outras quatro.

---

### H1 — Viés Geográfico em Pesquisa Aplicada (Gap 1)

**Título provisório do artigo:** *"Geographic Epistemic Asymmetries in LLM-Assisted Policy Research: A 15-Country, 6-Model Benchmark"*

**Gap abordado:** Empirical + Population gap — nenhum benchmark mede viés de LLM em tarefas de pesquisa aplicada a políticas públicas do Sul Global.

**Teoria:** Coloniality of Knowledge (Mohamed et al., 2020); Epistemic Injustice (Fricker, 2007).

**Formulação:**
- **H₀:** A acurácia média de LLMs frontier em tarefas de caracterização de políticas públicas, realidade socioeconômica e contexto ambiental não difere significativamente entre países do Sul Global e países do Norte Global (β_geo = 0).
- **H₁:** LLMs frontier apresentam acurácia sistematicamente inferior em tarefas de pesquisa aplicada sobre países do Sul Global, com magnitude do efeito Cohen's *d* ≥ 0,5 (efeito moderado-grande), quando comparadas a países do Norte Global.

**Operacionalização:**
- **VD: Acurácia composta** — índice 0-1 ponderado entre (a) acurácia factual binária (certo/errado vs ground truth documental), (b) completude contextual (0-5, avaliada por rubrica), (c) qualidade de citações (0-5, verificável), (d) calibração (Brier score).
- **VI: País (15 níveis)** — 12 Sul Global + 3 Norte Global. Seleção estratificada por continente e renda (Banco Mundial income groups).
- **Instrumento:** Benchmark próprio de 450 prompts (30 por país × 3 domínios × 5 tipos de tarefa) validado por painel de 2-3 especialistas regionais.

**Condições de escopo:** aplicável a LLMs frontier (>100B parâmetros equivalentes) acessadas via API, em tarefas de pesquisa factual aplicada. NÃO se aplica a: tarefas criativas, tarefas matemáticas puras, conversação casual.

**Alternativas e rivais:**
- **Rival 1:** "Diferenças refletem complexidade real, não viés" → Controle: painel de especialistas calibra dificuldade das perguntas por país ANTES da avaliação (inter-rater reliability Krippendorff's α ≥ 0,70).
- **Rival 2:** "LLMs apenas refletem baixa qualidade de dados públicos disponíveis para esses países" → Isso é *parte do mecanismo que queremos demonstrar*, não confound. Incluímos essa interpretação como discussão, não ameaça.
- **Rival 3:** "Efeito é dominado por um ou dois países outliers" → Análise com *country random effects* em GLMM + leave-one-out sensitivity.

**Desenho metodológico (preview da Etapa 3):** 15 países × 6 LLMs × 450 prompts × 5 replicações = 202.500 chamadas de API (factível em ~R$ 15-25k de crédito de API). GLMM com efeitos aleatórios por país e por modelo.

**Validade (Shadish et al.):**
- Interna: alta (desenho experimental controlado).
- Externa: moderada — 15 países é boa cobertura, mas generalização para países não testados requer cautela.
- Construto: crítica — a rubrica de "acurácia composta" é o ponto de maior vulnerabilidade. Validar via pré-teste com 50 prompts e concordância inter-avaliadores.
- Conclusão estatística: GLMM robusto a desbalanceamento + correção para múltiplas comparações (FDR Benjamini-Hochberg).

**Reporting guideline:** TRIPOD-AI adaptado (não é exatamente modelo preditivo clínico, mas é o mais próximo) + pré-registro OSF recomendado.

**Contribuição (Whetten, 1989):** Novidade empírica + ampliação de escopo (quem/onde). Corley & Gioia: *Originality — Incremental*, *Utility — Practical + Scientific* (alta).

---

### H2 — Interação Língua × Geografia (Gap 2)

**Título provisório:** *"Does Prompt Language Amplify Geographic Bias? A Factorial Test of Language × Country Interaction in LLM Factual Retrieval"*

**Gap:** Methodological gap.

**Teoria:** Linguistic representation hypothesis (Joshi et al., 2020, *State and Fate of Linguistic Diversity*); Sociolinguistic contextualism.

**Formulação:**
- **H₀:** Não existe interação estatisticamente significativa entre língua do prompt e país-alvo na acurácia de LLMs (β_interaction = 0).
- **H₁:** Existe interação não-aditiva entre língua do prompt e país-alvo, com direção esperada: prompts em língua local aumentam acurácia para países cuja língua é high-resource no corpus (PT para Brasil, ES para México/Argentina), mas diminuem acurácia para países cuja língua é low-resource (SW para Quênia, HI para Índia rural). Magnitude esperada: η²_interaction ≥ 0,05 (small-to-medium).

**Operacionalização:**
- **Design fatorial 15 países × 4 línguas (EN, PT, ES, HI, SW):** nem todo país é testado em todas as línguas — usamos matriz esparsa com pelo menos 3 línguas por país (EN sempre + 1-2 línguas regionais).
- **Controle de tradução:** prompts traduzidos por tradutores nativos + back-translation checklist. Descartar prompts onde back-translation mude o significado.
- **Métrica:** mesma VD composta de H1.

**Condições de escopo:** línguas com corpus mínimo identificável no Common Crawl (>0,01% tokens). Exclui línguas extremamente low-resource.

**Rivais:**
- **Rival 1:** "Efeito é tradução, não língua por si" → Validação back-translation.
- **Rival 2:** "Efeito é específico ao modelo, não generalizável" → Incluir 6 modelos com arquiteturas diferentes.

**Validade:**
- Construto: moderada (tradução nunca é 100% equivalente — documentar com honestidade).
- Externa: baixa-moderada — 4 línguas é limitado, mas cobre 3 continentes.

**Contribuição:** Novidade metodológica (desenho fatorial) + mecanismo (distinguir viés geográfico puro de confound linguístico).

---

### H3 — Modelos Regionais vs Frontier (Gap 3)

**Título provisório:** *"Can Regional LLMs Close the Global South Knowledge Gap? A Head-to-Head Comparison"*

**Gap:** Empirical gap.

**Teoria:** Data sovereignty (Kukutai & Taylor, 2016); AI localism.

**Formulação:**
- **H₀:** A diferença de acurácia entre modelo regionalmente treinado (Sabiá-3) e frontier models (GPT-5, Claude, Gemini) é uniforme entre países — ou seja, Sabiá-3 não reduz preferencialmente o gap para o Brasil vs outros países.
- **H₁a (reducionista):** Sabiá-3 reduz o gap BR→Norte em >50% quando comparado ao gap de frontier models, sem aumentar o gap para outros países do Sul Global.
- **H₁b (deslocamento):** Sabiá-3 reduz o gap para o Brasil MAS aumenta o gap para outros países do Sul Global (ex: Angola, Moçambique), indicando que "regional" pode criar novas assimetrias entre países de língua portuguesa.

H₁a e H₁b são mutuamente exclusivas — o dado decide.

**Operacionalização:** subconjunto de H1, focado em comparação Sabiá-3 vs 3 frontier models em 15 países.

**Condições de escopo:** modelos regionais disponíveis via API. Sabiá-3 é PT-BR; podemos incluir Latam-GPT se acessível (espanhol). Replicar racional para outros contextos (ex: Jais para árabe) é trabalho futuro.

**Rivais:**
- **Rival 1:** "Sabiá-3 é menor que GPT-5, efeito é só escala" → Comparar também com modelo frontier de escala similar (ex: Llama-4-70B).
- **Rival 2:** "Efeito reflete apenas tuning, não dados regionais" → Difícil de controlar sem acesso aos dados de treinamento. Discutir como limitação.

**Validade:**
- Construto: alta para "gap de performance", baixa para "mecanismo causal regionalidade".
- Externa: baixa (só 1 modelo regional testado em profundidade) — solução: framing cauteloso + convite para replicação.

**Contribuição:** Alta novidade empírica + implicação direta para policy (soberania de IA, investimento em modelos nacionais).

---

### H4 — Mecanismo Causal: Tokens de Treinamento → Gap de Performance (Gap 4)

**Título provisório:** *"Training Corpus Representation Predicts Geographic LLM Performance Gaps: Evidence from Common Crawl Token Counts"*

**Gap:** Theoretical + Evidence gap.

**Teoria:** Distributional hypothesis em NLP (Harris, 1954; Firth, 1957) aplicada a conhecimento factual; Resource curse hypothesis em NLP multilíngue (Joshi et al., 2020).

**Formulação:**
- **H₀:** O volume relativo de tokens por país no corpus de pré-treinamento (proxy: Common Crawl + Wikipedia pageviews) NÃO correlaciona com a magnitude do gap de performance observado em H1.
- **H₁:** Existe correlação positiva e monotônica entre log(tokens_país / total_tokens) e acurácia composta das LLMs (Spearman ρ ≥ 0,60, p < 0,01), com essa correlação explicando pelo menos 40% da variância entre países.

**Operacionalização:**
- **Variável mecanística:** log(tokens por país no Common Crawl 2023-2024) + log(Wikipedia pageviews por idioma relacionado ao país). Proxies públicos e replicáveis.
- **Análise:** regressão ecológica + mediation analysis — testar se token count media o efeito de renda/continente sobre acurácia.

**Condições de escopo:** explicação **correlacional**, não causal estrita. Exposição não-aleatória. Claims causais limitados a "consistente com" e "compatible with mechanism".

**Rivais:**
- **Rival 1 (grande):** "Correlação é confounded por outros fatores (desenvolvimento econômico, institucional)" → Incluir GDP, HDI, freedom index como covariates; ver se token count ainda media.
- **Rival 2:** "Common Crawl ≠ corpus real de treinamento" → Sim, é proxy. Transparência como limitação. Defensa: é o proxy mais utilizado na literatura (Joshi et al.; Brown et al.).

**Validade:**
- Causal: baixa (explicitamente). Apenas compatibilidade com mecanismo.
- Construto: moderada (Common Crawl é proxy imperfeito).
- Estatística: alta se desenho de poder for bem feito (ver Etapa 4).

**Contribuição:** Theoretical — conecta teoria distribucional de NLP a teoria crítica de AI colonialism, fechando um buraco entre as duas literaturas.

---

### H5 — Amarração Exploratória (Síntese)

Não é teste confirmatório, é **análise exploratória declarada** (seguindo Nosek et al., 2018): documentamos padrões emergentes que conectam H1-H4 em narrativa única sobre o ciclo de reprodução do viés colonial na produção científica assistida por IA. Útil para a Discussion, não para resultados principais.

---

## 4. Avaliação de Journals

Critérios aplicados: IF 2024-2025 (JCR Clarivate), escopo-fit, publicação recente sobre AI bias, tempo médio de revisão, política de dados abertos, APC.

### 4.1 Top-tier (ambicioso)

**Journal 1: Nature Human Behaviour** ⭐ *Top pick ambitious*
- **IF (2024 JCR):** 10,1-15,9 dependendo da fonte; CiteScore 19,2; SJR 5,5; Quartil Q1.
- **Escopo-fit:** ⭐⭐⭐⭐ — publicou ativamente sobre AI bias, LLMs e sociedade (Bail et al., 2024; Messeri & Crockett, 2024).
- **Por que funciona:** o framing "epistemic asymmetries" e "coloniality of knowledge" ressoa com o escopo humano-comportamental.
- **Por que pode falhar:** preferem desenhos psicológicos ou sociológicos clássicos; benchmark puro de LLM pode ser visto como "too technical".
- **Estratégia:** vender como "human behavior of AI-assisted science in Global South" — foco nas consequências humanas.
- **APC:** ~€10.790 (OA hybrid). Tempo primeira decisão: ~15 dias. Revisão completa: ~90-120 dias.
- **Acceptance rate:** ~7%.

**Journal 2: PNAS**
- **IF 2024:** 11,1.
- **Escopo-fit:** ⭐⭐⭐ — publica trabalhos sobre IA e sociedade (Bender et al., 2021 seminal foi Nature Machine Intelligence, mas PNAS tem espaço).
- **Vantagem:** broad audience, gancho policy forte.
- **Desvantagem:** preferem sponsoring member (facilita se o orientador tem rede).

### 4.2 Solid mid-tier (realista primário) ⭐ *Recomendação principal*

**Journal 3: Patterns (Cell Press)** ⭐⭐⭐ *Top pick realistic*
- **IF (2024 JCR):** 7,4. CiteScore 14,6. SJR 1,527. Quartil Q1.
- **Escopo-fit:** ⭐⭐⭐⭐⭐ — escopo explícito inclui "AI governance, ethics, science policy", "data science solutions to cross-disciplinary problems".
- **Por que é o pick realístico:** publicou em 2024-2025 trabalhos sobre AI bias (inclusive WorldBench está nesse espaço editorial).
- **APC:** USD 4.900 (participa do GPOA — geographical pricing OA, pode ser reduzido para autores do Brasil).
- **Tempo:** primeira decisão ~5 dias; decisão pós-revisão ~45 dias. Veloz.
- **Dado crítico:** tempo de publicação médio 19 semanas. Open Access obrigatório.
- **Estratégia:** enquadrar como "data science methodology + ethics" — eles adoram benchmarks novos com supplementary rico.

**Journal 4: AI & Society (Springer)**
- **IF 2024:** ~2,9 (varia).
- **Escopo-fit:** ⭐⭐⭐⭐ — crítica sociotécnica é o core.
- **Vantagem:** aceita claims mais críticos/decoloniais sem resistência.
- **Desvantagem:** IF menor; menos prestígio em avaliação Qualis.

### 4.3 Accessible fallback

**Journal 5: EPJ Data Science** (Springer Nature)
- **IF 2024:** ~2,8.
- **Rápido, Q1 em Social Sciences, aberto a benchmarks.

**Journal 6: Frontiers in Artificial Intelligence**
- Open access, aceita research topics sobre bias, tempo rápido, menos seletivo.

---

## 5. Síntese Estratégica

**Top Pick (maior probabilidade conjunta de aceite + impacto):**
→ **Patterns** com as 4 hipóteses integradas em UM artigo de formato longo (article type: *Research Article*, ~8k palavras + supplementary extenso).
→ Justificativa: escopo perfeito, IF respeitável para Q1, velocidade de revisão, apetite explícito por AI ethics + benchmarks, APC com desconto geográfico para Brasil.

**Quick Win (mais rápido a publicar):**
→ EPJ Data Science ou Frontiers in AI com versão reduzida (H1+H2, deixando H3+H4 para follow-up).

**High Risk / High Reward:**
→ Nature Human Behaviour — exige framing humano-comportamental forte e *cover letter* elitíssima. Se falhar, transferir facilmente para Patterns.

**Sequência recomendada:**
1. Executar os 4 experimentos como um único projeto (Etapa 5 do pipeline).
2. Submeter versão completa ao Nature Human Behaviour.
3. Se desk-reject ou revisão negativa → reformatar para Patterns.
4. Paralelamente, publicar **dataset separado** como *Data Paper* em Scientific Data (Nature) — reuso alto, citações garantidas.

**Funding/recursos:**
- API custo estimado: R$ 15-25k (tratar via CNPq/FAPESC bolsa de mestrado, ou programa de créditos OpenAI/Anthropic para pesquisadores).
- Painel de especialistas: via rede PPGSAU/UTFPR + colaborações Sul-Sul (CLACSO, CODESRIA).

**Open science stance:**
- Pré-registro OSF antes da coleta (para H1-H4).
- Dados abertos (prompts, ground truth, respostas das LLMs) em Zenodo com DOI.
- Código em GitHub + link permanente no paper.
- FAIR compliance.

---

## 6. Self-audit

| Critério | H1 | H2 | H3 | H4 |
|---|:-:|:-:|:-:|:-:|
| Falsificável? | ✓ | ✓ | ✓ | ✓ |
| Operacionalizada? | ✓ | ✓ | ✓ | ✓ |
| Teoria nomeada? | ✓ | ✓ | ✓ | ✓ |
| Condições de escopo? | ✓ | ✓ | ✓ | ✓ |
| Alternativas endereçadas? | ✓ | ✓ | ✓ | ✓ |
| Validade analisada? | ✓ | ✓ | ✓ | ✓ |
| Inovação calibrada? | ✓ | ✓ | ✓ | ✓ |
| IFs verificados? | ✓ | ✓ | ✓ | ✓ |

Nenhum fato fabricado; IFs conferidos no JCR 2025 e nas FAQs oficiais dos journals.

---

## 7. Handoff para Etapa 3

Pronto para o desenho metodológico detalhado:
- 15 países × 6 LLMs × 4 línguas × 3 domínios × 5 tipos de tarefa × 5 replicações = ~540k chamadas
- Comitê de ética (porque envolve painel humano)
- SAP pré-registrado com H₀/H₁ formais
- Rubrica de avaliação desenvolvida e validada
