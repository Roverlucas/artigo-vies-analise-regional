# FRAMEWORK DE ESCRITA ACADÊMICA MELHORADO
## Extraído do Paper NatComms "Same Prompt, Different Answer" (Major Revision — maio/junho 2026)

**Objetivo:** Um framework acionável para reescrever outro artigo (benchmark de viés em LLMs) incorporando todas as lições, correções, críticas dos revisores e feedbacks dos coautores acumulados neste paper.

**Status do paper-mãe:** Submitted to Nature Communications (março 2026) → Major Revision (maio 2026) → Revision finalizada 13 maio 2026.

---

# PARTE 1: CRÍTICAS DOS REVISORES (R1, R2, R3) E RESPOSTAS

## Mapping das críticas substantivas → changes no manuscript

### REVIEWER 1 (15 pontos substantivos — todos respondidos)

#### R1.1: Reframe central — "Deployment Stack" como unidade de análise
**Crítica original:**
> "The paper frames the testing as testing of different models, what is being tested is actually APIs and associated infrastructure stacks. Specifically, the same model served by a different API may have different degrees of non-determinism. Could this framing be corrected?"

**Resposta dada:**
- Redefiniu a unidade de análise de **model** → **deployment stack** (tupla: model weights, provider, serving infrastructure, API layer)
- O resultado Together AI (mesmo LLaMA 3 8B com EMR 0.993 local vs 0.780 Together) prova que a stack, não o modelo abstrato, é o portador da variação
- **Mudanças concretas no manuscript:**
  - Abstract: substitui "API-served models" → "API-served deployment stacks"
  - Introdução: novo parágrafo (~80 palavras) definindo o conceito
  - Methods: nova subseção "Unit of analysis: deployment stacks" (~150 palavras)
  - Todas as tabelas/figuras: atualizar legends e labels
  - Discussion: novo parágrafo conectando Together AI ao insight central

**Lição para seu artigo:** A unidade de análise precisa estar cristalina DESDE O ABSTRACT. Não é suficiente dizer "testamos LLMs"; há sempre uma stack específica (provider, versão de snapshot, infraestrutura) sendo testada. Especifique sempre a tupla completa.

---

#### R1.2: Comparabilidade entre provedores com superfícies de parâmetros diferentes
**Crítica original:**
> "The authors write that 'all providers expose the same user-facing deterministic parameters (temperature zero, fixed seed where supported)' yet later note that the settings each specific API offers vary. How does this affect comparability?"

**Resposta dada:**
- Reconheceu que não há **igualdade de parâmetros**, mas sim "**máxima configuração de determinismo que cada provedor documenta**"
- Introduziu campo `seed_status` no Run Card: `sent`, `logged-only-not-sent`, ou `not-supported`
- Exemplo: Anthropic não aceita seed parameter em nenhum ponto → seed_status="logged-only-not-sent-to-api" para transparência auditável
- **Adição no Methods §Supplementary S4:** novo parágrafo "Comparability across providers"

**Lição para seu artigo:** Quando comparar sistemas heterogêneos (diferentes LLMs, diferentes condições), seja explícito sobre O QUE é comparável e O QUE não é. A comparabilidade não é "igualdade de inputs" — é "máxima configuração documentada por cada sistema". Registre esse metadado em um run card ou log estruturado.

---

#### R1.3: Perplexity Sonar — claim sem suporte experimental direto
**Crítica original:**
> "Line 103 states that 'Perplexity Sonar's particularly low reproducibility reflects its search-augmented architecture...' — it is unclear whether this claim is directly supported by the paper's experiments. If not, the statement should either be supported by appropriate citation or explicitly framed as informed speculation."

**Resposta dada:**
- Reframed como "**informed hypothesis**" em vez de claim causal direto
- Adicionou 3 referências (lewis2020rag, perplexitysonar2024, gao2024rag)
- Texto agora lê: "A plausible mechanism is... We did not perform a controlled retrieval-isolation experiment... so this mechanism is offered as an **informed hypothesis rather than a demonstrated cause**."

**Lição para seu artigo:** Calibre força de claims. Use:
- "We demonstrate..." ← resultado direto dos seus experimentos
- "We observe that... is consistent with..." ← compatível com dados mas não prove causa
- "A plausible mechanism is... [cite literature]. We did not test this directly, so this is an informed hypothesis." ← hipótese suportada por priors e lógica, não por seu estudo
- Nunca faça causal claims sem evidência isolada. Se não pode isolar causa, use "is consistent with" ou "implicates".

---

#### R1.4: Cloud vs. Production-serving infrastructure — distinção fuzzy
**Crítica original:**
> "The distinction between 'cloud deployment itself' and 'production serving infrastructure' is currently fuzzy... it is not clear that it is comprehensive enough to support the strong conclusions being drawn. What additional factors might be at play?"

**Resposta dada:**
- Adicionou parágrafo de abertura em Methods §"Sources of non-determinism in distributed inference" explicitamente separando dois factor classes:
  - **Cloud deployment factors:** latency, request routing, shared hardware, multi-tenancy
  - **Production serving infrastructure factors:** tensor parallelism, FlashAttention, dynamic batching, speculative decoding, mixed-precision BF16/FP16, prefix caching
- Together AI result licencia a inferência: mantém cloud factors, reduz infrastructure complexity → EMR sobe de 0.220 (API) para 0.780 (Together) → não é a cloud, é a infrastructure

**Lição para seu artigo:** Quando fizer uma claim mecanística ("X causa Y"), liste EXPLICITAMENTE:
1. Todas as variáveis que poderiam afetá-la
2. Quais você controla, quais você observa, quais você deixa variar
3. O quasi-isolation experiment (ou análise contrastiva) que disambigua a causa específica
Isso torna a argumentação rastreável e refutável.

---

#### R1.5: Field-level analysis — resolução de uma contradição aparente
**Crítica original:**
> "Line 172 states that 'The key result field diverges in 67% of groups, and method in 57%'. However, it is not clear whether differences in these fields implies substantive changes in content... Given the reported high semantic similarity and low text edit distance, these differences might reflect minor wording variations than meaningful semantic changes."

**Resposta dada — MUITO IMPORTANTE:**
- Computou EMR, NED, ROUGE-L, BERTScore F1 **separadamente por campo** (objective, method, key_result, model_or_system, benchmark)
- Resultado: **BERTScore saturado** (F1 ≈ 0.978–0.979 em ambos grupos), mas **EMR divergente** (conclusion-relevant fields: 0.455 vs metadata fields: 0.684; Cohen's d = +1.41)
- Interpretação: BERTScore é **estruturalmente incapaz** de discriminar divergência substantiva de cosmética em outputs extraídos
- A aparente contradição ("textual não-semântico" vs "conteúdo substantivo") prova que o **three-level reproducibility framework** (bitwise → structural → semantic) é necessário

**Lição para seu artigo — CRÍTICA:**
Quando seu output é estruturado (JSON, table, list), não confie em métricas de similaridade semântica de propósito geral (BERTScore, BLEU, etc.). Essas métricas **saturam** em campos pequenos/estruturados e ocultam divergência real. Em vez disso:
- Compute reproducibility **por campo semântico** (objective, method, result, conclusion)
- Use métricas **field-aware**: EMR para campos discretos, NED para campos numéricos, custom rubrics para campos semânticos críticos
- Sempre reporte a divergência structural (bits, campos, tokens) ao lado de métricas semânticas
- Se semântica-métrica e structural-métrica discordam, invoque o three-level framework e investigue por quê

---

#### R1.6: Propagação — textual differences affect automated processing
**Crítica original:**
> "'Where outputs are parsed programmatically rather than read by humans, even minor lexical differences can propagate'. Paired with the next paragraph, the point seems to be that these very minor, mostly textual differences can nonetheless affect automated processing... This is a key part of the argument..."

**Resposta dada:**
- Reescreveu o parágrafo para tornar a **chain of propagation logic** explícita:
  1. Outputs feed automated parsers (regex, JSON schema) → single-char differences cause divergent records
  2. Downstream pipelines aggregate records em statistics (means, counts, effect sizes) → cada divergência lexical é um data-point distinto
  3. Per-field EMR drop em key_result é onde propagação é mais consequente (porque evidence-synthesis pipelines agregam esse field)
- Companion paper PM2.5 shows directly: 23 distinct effect estimates appear/disappear dependo de qual run do LLM é usado

**Lição para seu artigo:**
Se seu paper envolve **extração estruturada e agregação downstream**, mostre a cadeia:
- Saída do modelo (texto livre ou JSON)
- Parsing automático → structured record
- Agregação (média, contagem, efeito estatístico) → metricamente alterado
Cada passo amplifica noise/divergência. Quantifique a propagação, não só o output-level difference. Demonstre um caso end-to-end onde divergência pequena de output → resultado grande de agregação.

---

#### R1.7: Figure 1 caption — "8 vs 5 vs 10 deployments" inconsistência
**Crítica original:**
> "Fig 1. The caption refers to 8 model deployments but the figure appears to show 5 or 10 depending on how 'deployment' is defined... Additionally, the results for deepseek and perplexity are not shown."

**Resposta dada:**
- Reescreveu caption para enumerar **explicitamente** todos os 8 stacks shown: 3 local + Together AI + 4 API
- Explicou por quê algumas stacks faltam em alguns figures (coverage variation por task due to API-quota constraints)
- Added coverage matrix explicitamente em captions de todas as figuras com subsets

**Lição para seu artigo:**
Captions de figuras não são resumos — são **especificações técnicas**. Todo número em um caption deve ser:
- Exato (não "roughly", não "approximately" sem CI)
- Auditável (deve aparecer em uma tabela no paper ou no supp)
- Explicado se houver subset/variação (por quê falta tal stack em tal figura)
- Cross-referenciado (Methods §X para lista completa de stacks/tasks)
Erros em captions são red flags para desk-reject porque sugerem manuscrito não foi cuidadosamente verificado.

---

#### R1.8: Code generation e math reasoning — expandir além de summarization
**Crítica original:**
> "As one of the limitations, the authors specify that code generation and mathematical reasoning are excluded... running experiments on code generation and mathematical reasoning could greatly strengthen the results because these are domains where minor differences in text actually can completely make or break the functionality of the output."

**Resposta dada — EXPERIMENTAL EXPANSION:**
- Rodou HumanEval (30 problems, 5 reps, 8 stacks): local/Together ≥ 0.92; Claude 0.39; gpt-4o 0.84; deepseek 0.84
- Rodou GSM8K (30 problems, 5 reps, 8 stacks): local/Together ≥ 0.84; Claude 0.063; gpt-4o 0.27; deepseek 0.37
- **Resultado crítico:** EMR não melhora em domains de "high stakes" — na verdade piora em math (Claude cai de 0.20 → 0.063)

**Lição para seu artigo:**
Se seu claim é "este fenômeno é geral/universal", você **precisa demonstrar em múltiplos domínios**:
- Pelo menos 2–3 tasks distintas
- Diferentes tipos de estrutura de output (JSON vs free text vs code vs numerical)
- Diferentes complexidades (single-turn vs multi-step vs RAG)
- Diferentes "stakes" (quando acurácia textual importa — code, math — e quando não — paraphrase, summary)
Não confie apenas em um domínio. Editor e revisores VÃO pedir "but does it hold for X?". Antecipe com dados.

---

#### R1.9: PM2.5 experiment — falta de ênfase na aplicação
**Crítica original:**
> "The applied experiment (line 270–277) is crucial for the paper's central claim... Could the authors clarify why this part is not given greater emphasis within the overall study?"

**Resposta dada — REFRAME MAJOR:**
- Promoveu PM2.5 a uma **dedicated Results subsection:** "Applied impact in evidence synthesis: an out-of-AI/ML probe"
- Adicionou **two layers of self-contained in-paper evidence**:
  1. Probe direto: 10 PubMed abstracts (PM2.5), 5 reps × 8 stacks
  2. Independent two-judge LLM-as-judge (Claude Opus 4.7 + gpt-4o) em 30 novos casos com 3 pré-registrados critérios (direction, magnitude ±20%, CI overlap)
- Claude Opus 4.7: 22/30 truly contradictory (Wilson 95% CI 56–86%); gpt-4o: 27/30 (74–97%); κ=0.29

**Lição para seu artigo — CRITICAL POSITIONING:**
Se você tem um **applied/real-world validation** ou **downstream impact case**, não o deixe no rodapé. Estruture assim:
- **Main text Results subsection** dedicado (não just "additional validation")
- **Self-contained evidence** dentro do paper (não "see companion paper")
- **Multiple layers**: quantitative (EMR, divergence rate) + qualitative (expert judgment, LLM-judge triangulation)
- **Explicit claim**: "For practitioners, this means..." — tornar o insight acionável
Isso torna o paper não apenas "é um problema" mas "é um problema que importa para uso real".

---

#### R1.10: Protocol scope — client-side vs provider-side observability
**Crítica original:**
> "Protocol design described in line 310 'Run Cards capture the complete execution context'... Could the authors clarify whether they envision proprietary API providers adopt this, for example, documenting details such as the weights hash and environment fingerprint to enable provenance tracking?"

**Resposta dada:**
- Insériu novo parágrafo titled "Scope: client-side observability"
- Clarificou que o protocolo é **intencionalmente client-side**: documenta o que é observável do lado do cliente (request payload, resolved model ID, response headers, API response ID, latency, input/output hashes)
- **Não requer** weight hashes ou full infrastructure disclosure (inacessível para closed-source)
- Valor operacional: (i) differential diagnosis (quando mesmo prompt produz outputs diferentes, hashes provam divergência é na stack); (ii) provider-agnostic minimum standard (funciona com qualquer stack)

**Lição para seu artigo:**
Se seu protocolo/método tem limitações técnicas (por exemplo, não pode acessar internals de um sistema), **seja explícito**:
- O quê seu método **pode** observar/auditar
- O quê fica fora de escopo e por quê
- Qual é o valor mesmo com essas limitações (diagnóstico diferencial? auditability? reproducibility?")
Isso transforma limitação técnica em design choice defensável.

---

#### R1.11: Anthropic seed clarification
**Crítica original:**
> "Line 363 states 'For API models, the seed parameter is advisory (OpenAI), absent (Anthropic), or empirically insufficient (Gemini)'. For Anthropic, does this imply that even under the C1 condition, the seed may not in fact be fixed, and could therefore be a source of non-determinism?"

**Resposta dada:**
- Anthropic Messages API não aceita seed parameter em nenhum ponto
- Run Card registra `seed: 42` com `seed_status: "logged-only-not-sent-to-api"`
- Não-determinismo observado em Claude é **attributable to production infrastructure, não seed variation**
- Adicionou parágrafo "Anthropic seed handling" em Methods §Experimental conditions

**Lição para seu artigo:**
Quando documentar conditions experimentais, especifique por provider:
- Qual parâmetro foi **requested** pelo experimenter
- Qual foi **honored** pela API
- O que isso implica para attribution causal de variação
Não assuma que "temperature=0" significa a mesma coisa em todos os LLMs. Documente o call exato, a response, o que foi logged.

---

#### R1.12: Concrete examples of observed differences
**Crítica original:**
> "It would have been helpful if the authors included concrete examples of the observed differences to supplement the metrics."

**Resposta dada:**
- Adicionou **Box 1** com 3 exemplos lado-a-lado de Run Cards reais:
  1. GPT-4 extraction abstract_001 benchmark field — "comma vs and" (cosmético)
  2. Claude RAG abstract_001 (reps 0 vs 1) key_result — "parallelizability + 8 GPUs" vs "training time + constituency parsing" (substantivo)
  3. Same group, method field — fully reformulated wording (substantivo)
- Diff highlights com bold colorido marcando divergências
- Run IDs citados para auditabilidade

**Lição para seu artigo:**
Não confie em métricas sozinhas para transmitir magnitude de divergência. Mostre **pelo menos 2–3 exemplos concretos** de:
- Outputs divergentes (cosmético — rephrasing, punctuation)
- Outputs divergentes (substantivo — diferentes claims, números, conclusões)
- Explicar por que cada um importa para seu use case
Isso torna o paper legível por leitores que não são especialistas em métricas, e fornece credibilidade ("vi os dados brutos").

---

#### R1.13: W3C PROV definition (line 319)
**Crítica original:**
> "Line 319 could benefit from an additional sentence defining what W3C PROV is and why it's being used."

**Resposta dada:**
- Adicionou definição on first use na Introdução (~linha 107):
  > "the W3C Provenance (PROV) Data Model [w3cprov2013] — a W3C Recommendation that defines an interoperable standard for representing the entities, activities, and agents involved in producing a piece of data..."
- Reference: Moreau, L. & Missier, P. PROV-DM: The PROV Data Model. W3C Recommendation (2013). https://www.w3.org/TR/prov-dm/

**Lição para seu artigo:**
Qualquer standard/framework/sigla técnica que não seja de domínio comum (como "LLM", "API") deve ter uma:
- **Definição breve** on first use (~1 sentence, apositivo)
- **Citação** a uma referência autoritária
- **Justificativa de por que você a escolheu** (por que PROV em vez de outro standard?)
Isso economiza tempo de revisores e melhora acessibilidade.

---

#### R1.14: Reporting Summary — "deployment mode" clarification
**Crítica original:**
> "The Reporting summary, in 'A description of all covariates tested' lists 'deployment mode'. Could the authors clarify whether this refers to the decoding mode and where they vary the prompt format?"

**Resposta dada:**
- "Deployment mode" = local vs API (stack-level covariate, not a per-run varying parameter)
- Distingue de: decoding mode (greedy at t=0), prompt format (controlado em Supp §S7)
- Revised Reporting Summary entry para ser explícito

**Lição para seu artigo:**
Em checklists e reporting summaries:
- Sempre diferencie entre **stack-level** covariates (fixed por grupo, não varia dentro do grupo) vs **run-level** parameters (varia per request)
- Separe explicitamente: input parameters (prompt, seed), model parameters (temperature, top-p), infrastructure parameters (deployment mode, batch size)
- Isso torna o design experimental auditável e replicável.

---

#### R1.15: API documentation links em Supplementary §S4
**Crítica original:**
> "S4 in the Supplementary Information could benefit from adding a link to each API's official documentation."

**Resposta dada:**
- Adicionou Supplementary Table S2 com hyperlinks a cada provider:
  - OpenAI: https://platform.openai.com/docs/api-reference/chat
  - Anthropic: https://docs.anthropic.com/en/api/messages
  - Google Gemini: https://ai.google.dev/api/rest
  - DeepSeek: https://api-docs.deepseek.com
  - Perplexity: https://docs.perplexity.ai
  - Together AI: https://docs.together.ai/reference/chat-completions
  - Ollama: (local)

**Lição para seu artigo:**
Quando descrever API/sistema externo, sempre forneça:
- Link oficial à documentação (com access date)
- Versão/snapshot date se aplicável
- Se a API mudou depois, nota no Limitations
Isso permite verificação point-in-time e torna o paper mais "living" — leitores podem comparar seu resultado com versões futuras.

---

### REVIEWER 2
- Co-reviewer (Early Career Researcher training)
- **Nenhum comentário independente fornecido**
- Apenas agradecimento no point-by-point

**Lição:** Quando um co-reviewer não comenta, isso **não é um endosso silencioso** — é simplesmente falta de engagement. Não suponha concordância. O resto dos revisores ainda vão examinar tudo.

---

### REVIEWER 3 (6 pontos substantivos)

#### R3.1: More creative/open-ended tasks
**Crítica original:**
> "The primary conclusions are drawn from scientific summarization and JSON extraction. More creative or open-ended tasks (code generation, math, creative writing) should be included to verify the extent of 'hidden' variation in those critical domains."

**Resposta dada:**
Same as R1.8 — HumanEval + GSM8K expansion. Não foram capazes de adicionar creative writing dentro do budget.

**Lição:** Quando expandir domínios experimentais, priorize domains onde o resultado **matters mais**:
- High-stakes (math, code — erro textual = funcional erro)
- Real-world (saúde, legal, engineering)
- Controverso (creative, subjective — onde bias importa)
Creative writing é importante mas menos urgente que math/code.

---

#### R3.2: Quasi-isolation scope — "não aplicável a proprietary stacks"
**Crítica original:**
> "'Cloud deployment does not preclude reproducibility' was tested with LLaMA 3 model via Together AI's cloud endpoint. Strictly speaking, this proof is not complete without verifying with 'Smarter' APIs (GPT-4, Claude, Gemini). Since they are closed-source and proprietary, they cannot be locally deployed to compare against the cloud version."

**Resposta dada — MUITO IMPORTANTE:**
- Reconheceu limitação fundamental: quasi-isolation argument **não é aplicável a proprietary stacks**
- Reformulou claim de "cloud deployment does not preclude reproducibility" (strong) para "cloud deployment is **not a sufficient cause** of non-determinism" (weak, defensível)
- Added explicit Limitations paragraph: 
  > "The Together AI quasi-isolation result also has scope limits... The probe demonstrates that cloud deployment is not a sufficient cause of LLM non-determinism... We do not claim, and the result does not warrant claiming, that the proprietary stacks behind GPT-4, Claude, and Gemini could achieve the same level of reproducibility..."
- Mantém o result como "partial existence proof" e evidência para claim mais fraca

**Lição para seu artigo — CRITICAL:**
Quando sua evidência é **contrastiva ou quasi-experimental**, seja explícito sobre o quê ela **não prova**:
- "This demonstrates that X is not a sufficient cause of Y"
- "This is consistent with Z but does not prove Z is the only mechanism"
- "We cannot test this hypothesis directly because..."
- "The result applies to [open-source/accessible systems]. For [proprietary/opaque systems], the result is partial evidence for..."
Isso torna claims defensáveis e refuta pre-emptively a crítica de "but you didn't test X".

---

#### R3.3: Multi-turn coverage extension to gpt-4o and DeepSeek
**Crítica original:**
> "While five major API providers are tested, only two API providers (Claude and Gemini) are included in the more complex multi-turn and RAG experiments... It is suggested to extend the multi-turn and RAG evaluations to OpenAI (GPT-4) and DeepSeek..."

**Resposta dada:**
- Rodou three-turn refinement em gpt-4o (EMR 0.090 [0.02, 0.16]) e deepseek-chat (EMR 0.350 [0.13, 0.60])
- Confirmou que near-zero reproducibility em multi-turn é **universal across major cloud stacks**, não Claude/Gemini-specific
- Não estendeu RAG a gpt-4o/deepseek dentro do orçamento; acknowledged explicitamente no Limitations
- Mas single-turn EMRs (gpt-4o 0.42, deepseek 0.66) predizem RAG seria ainda pior

**Lição:** Quando não pode fazer experimento completo, mostre **análise contrastiva**:
- Single-turn EMRs são 0.42 (gpt-4o) e 0.66 (deepseek)
- Claude/Gemini single-turn: 0.20 e 0.10
- Claude/Gemini RAG: 0.00 e 0.07
- → Predict: gpt-4o/deepseek RAG seria ≥ 0.00
Isso torna a limitação menos crítica porque você mostrou **por que o resultado é plausível** mesmo sem dados novos.

---

#### R3.4: Limited domain — only 30 AI/ML abstracts
**Crítica original:**
> "The study relies on 30 AI/ML abstracts... this limited domain may not reflect how non-determinism manifests in non-English texts or less structured fields."

**Resposta dada:**
- Adicionou 10 PubMed PM2.5/respiratory health abstracts (different domain, same language)
- Resultado: local/Together EMR 0.96–1.00; API: deepseek 0.66, gemini 0.49, gpt-4o 0.42, **Claude 0.010**
- **Padrão replicou**: não é corpus-specific, é domain-transferable
- Acknowledged que non-English coverage ainda é limitação; futuro work

**Lição:**
Quando limitação é "only tested on domain X", **mínimo defensável** é:
- 1 additional domain fora de X (même language, structure similar ou different)
- Mostrar que resultado **replicou** (mesmo pattern de stack-wise ranking)
- Ser honesto sobre limites restantes (non-English, non-Western fields, etc.)
Isso transforma "limited study" em "proof-of-concept on X with replication on Y".

---

#### R3.5: Mechanism mapping per stack — explicit table
**Crítica original:**
> "While the paper lists six potential mechanisms for non-determinism, the manuscript would benefit from a more explicit discussion of which specific mechanisms are likely active in the Together AI 'quasi-isolation' case versus the OpenAI/Anthropic cases."

**Resposta dada:**
- Adicionou **Methods Table 3** mapping 6 mechanisms × 5 stacks:
  - Non-associative FP arithmetic
  - Mixed-precision BF16/FP16
  - Tensor parallelism
  - FlashAttention kernel
  - Dynamic batching
  - Speculative decoding
- Cells labeled: ✓ (documented), "likely", "possible", --- (absent), △ (mitigated by design)
- Footnote explicitamente states attribution é inferential para closed-source
- Together AI result implicates mechanisms 1–2; proprietary stacks também 3–6

**Lição:**
Quando sua contribuição inclui **attribution causal ou mecanismo**, crie uma **mechanism-by-condition matrix**:
- Rows: mecanismos possíveis (de literature)
- Columns: stacks/conditions/treatments seu paper testa
- Cells: evidência que mecanismo está "active" naquela condição
- Include confidence: checkmark (provável), "likely" (inferido), "possible" (hipotético)
- Footnote caveats sobre o que pode/não pode ser testado
Isso torna o raciocínio causal transparente e refutável.

---

#### R3.6: Validation — "são os 23 PM2.5 effects realmente contraditórios?"
**Crítica original:**
> "The use of specific model snapshots (e.g., gpt-4-0613) means the exact EMR values may be 'point-in-time' estimates that change as providers update their underlying infrastructure. Since the authors found high BERTScore F1 > 0.97 despite low EMR, they should include a human evaluation or LLM-as-a-judge step to confirm if the 23 'disappearing' effect estimates in the PM2.5 study are truly contradictory or just semantically varied."

**Resposta dada — VALIDATION PROTOCOL (MULTI-LAYERED):**
- Layer 1 (PRIMARY, in-paper): Two-judge LLM-as-judge (Claude Opus 4.7 + gpt-4o) em 30 **novos** casos (distinct dos 23 do companion paper)
  - 3 pré-registered critérios: direction, magnitude ±20%, CI overlap
  - Claude: 22/30 truly_contradictory (Wilson 95% CI 56–86%), 3 semantically_equivalent, 5 ambiguous
  - gpt-4o: 27/30 truly_contradictory (74–97%), 3 semantically_equivalent, 0 ambiguous
  - Inter-judge κ = 0.29 (fair), concordância 76.7%, PABAK = 0.53
  - Ambas lower bounds (56%, 74%) excluem interpretação cosmética com BERTScore > 0.97
  - Cost: USD 1.30 (60 API calls) — negligível overhead
- Layer 2 (CONTEXT): Companion paper (500 abstracts, silver-standard validation vs DeepSeek-R1, não reproduced aqui)
- Layer 3 (SNAPSHOT DRIFT): gpt-4o-2024-11-20 current-snapshot check (confirma padrão persiste)

**Lição para seu artigo — CRITICAL VALIDATION DESIGN:**
Se seu claim é "divergências são substantivas não cosmética", construa um **3-layer validation**:
1. **Quantitative-structural** (seu paper): field-level EMR, divergence rate, per-field analysis
2. **Qualitative-sample** (sua paper): multiple judges (2–3) independentes com rubric pré-registrado, blind setup
3. **Larger-corpus-context** (literatura, papers relacionados): cite evidence que padrão replicou em outras escalas
Não confie em uma camada. Cada camada tem viés (structural-only oculta semântica; single-judge é BIAS-PRONE; larger-corpus pode ser confounder).

---

## Sumário: Mapeamento Críticas → Manuscript Changes

| Crítica | Tipo | Mudança no Manuscript | Impacto |
|---------|------|----------------------|---------|
| R1.1 (reframe stack) | Conceitual | Abstract, intro, methods, tables, discussion reframed | Central ao contribution |
| R1.2 (comparability) | Clarificação | Novo parágrafo §Methods; campo `seed_status` | Defensibilidade |
| R1.3 (Perplexity mechanism) | Calibração | Claim "informed hypothesis" + citations | Humildade científica |
| R1.4 (cloud vs infra) | Conceitual | Novo parágrafo Methods §Sources; dois factor-classes explicit | Mechanistic clarity |
| R1.5 (per-field analysis) | Análise NOVA | Tabela nova com EMR/NED/ROUGE-L/BERTScore por field | Resolução contradição |
| R1.6 (propagation logic) | Reframe | Cadeia explícita: output → parsing → aggregation → impact | Relevância para practitioners |
| R1.7 (figure captions) | Especificação | Captions rewritten; coverage matrix explícita | Auditabilidade |
| R1.8 (code/math) | Experimental | HumanEval + GSM8K: 30 problems, 5 reps, 8 stacks | Generalidade |
| R1.9 (PM2.5 emphasis) | Reframe | Novo Results subsection "Applied impact"; prominence major | Relevância real-world |
| R1.10 (protocol scope) | Clarificação | Novo parágrafo "Scope: client-side observability" | Honestidade limitações |
| R1.11 (Anthropic seed) | Clarificação | Parágrafo Methods §Experimental conditions | Auditabilidade |
| R1.12 (concrete examples) | Novo conteúdo | Box 1 com 3 exemplos lado-a-lado de Run Cards | Credibilidade |
| R1.13 (PROV definition) | Clarificação | Definição intro + citação autoritária | Accessibility |
| R1.14 (deployment mode) | Clarificação | Revised Reporting Summary | Reproducibility |
| R1.15 (API links) | Novo conteúdo | Tabela S2 com hyperlinks a documentação | Auditability ponto-in-tempo |
| R3.1 (creative tasks) | Experimental | Mesmo que R1.8 | Generalidade |
| R3.2 (quasi-isolation scope) | Calibração | Limitations paragraph; claim reformulado weak | Honestidade |
| R3.3 (multi-turn extension) | Experimental | gpt-4o + deepseek multi-turn; ~100 runs novas | Universalidade claim |
| R3.4 (domain transfer) | Experimental | 10 PM2.5 abstracts; resultado replicou | Domain transfer |
| R3.5 (mechanism mapping) | Análise NOVA | Methods Table 3; 6 mechanisms × 5 stacks | Mechanistic clarity |
| R3.6 (validation) | Validação NOVA | Two-judge LLM-as-judge; 30 cases; κ=0.29 | Confiabilidade substantive-divergence claim |

---

# PARTE 2: FEEDBACK DOS COAUTORES (Profa. Yara Tadano)

## Princípio de Ouro de Yara

**Regra inviolável:** "Quem lê o artigo publicado nunca pode saber que houve revisão."
- Tudo adicionado deve parecer "como se fizesse parte do texto desde o início"
- Menções a revisores ficam SOMENTE em:
  - Carta ao editor
  - Point-by-point response
  - Reporting summary (quando couber)

## Ocorrências Removidas do Manuscrito

### No Manuscrito Principal

| Página | Trecho problematoso | Ação tomada | Princípio |
|--------|-------------------|----------|----------|
| p.12 | "...were added in revision per reviewer request R3.3 and..." | Remover. Nunca cite que algo foi adicionado por pedido do revisor | Never signal revision in manuscript |
| p.19 | "The Revision... extensions paragraph below describes... **added in revision**" | Reescrever sem citar revisão. Ex: "To ensure... three additional tests were conducted..." | Make addition look native |
| p.19 | "Following reviewer requests during major revision (R3.3, R3.4, R3.6)," | Deletar abertura | Never cite reviewer IDs |
| p.22 | "A private reviewer URL is provided... in the Cover Letter..." | Remover do artigo (fica apenas na carta ao editor) | Reader should not know about review process |

### No Suplementar

| Página | Trecho | Ação | Princípio |
|--------|--------|------|----------|
| p.20 | "**The Reviewer 3 (item 6) request was for** 'human evaluation or LLM-as-a-judge'..." | Reescrever: "To confirm whether the PM2.5 divergences are truly..., we conducted a cross-provider two-judge..." | Phrase as design choice, not reviewer demand |
| p.21 | "...**Reviewer 1's request (R1.5)**..." | **Deletar** | Never cite reviewer source |
| p.22 | "**Reviewer 1 identified**..." | **Deletar** | Never credit reviewer for findings |

### Nota Implícita de Yara (02/06)
> "No material suplementar também está citando que algo foi feito por questionamento do revisor. Acho que isso pode estar no reporting summary, mas não no artigo e no material suplementar."

---

## Feedback na Carta aos Revisores (Point-by-Point)

**Princípio central:** O revisor não pode precisar abrir o manuscrito. Tudo que ele precise ver está dentro da própria carta.

### Específicas

1. **Trocar "~xx-word paragraph" pelo texto literal acrescentado** (multiple pages)
   - Não diga "we added a 50-word paragraph"; COLE o parágrafo inteiro
   - Útil porque: revisor não precisa abrir manuscrito; prova exatidão; impede "wait, that's not what I saw in the revised file"

2. **Referências novas → listar com dados completos na carta** (não só "ver item X na bibliografia")
   - Apresentar como: **[lewis2020rag]** Lewis, P. et al. Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems* **33**, 9459–9474 (2020). https://arxiv.org/abs/2005.11401
   - Com DOI clicável
   - Se quiser ler, clica na carta; não precisa acessar manuscript

3. **Legendas de figura** — colar EXATAMENTE como ficaram no manuscript final

4. **Figuras dentro da carta** — inserir em alta resolução (ou ao menos screenshots)

5. **Não remeter revisor para outra resposta** 
   - Nunca: "Please see the response to R1.8..."
   - Sempre: Responda de novo aqui, na íntegra (mesmo que seja repetição)

6. **Tabelas com numeração do PDF final, não LaTeX**
   - Não: `Table \ref{tab:apidocs}`
   - Sim: "Table 3 (Mapping of non-determinism mechanisms)" com número exato que aparece no PDF

7. **Aspas/reticências — sempre feche**
   - "...text here..." ← errado
   - "...text here...." ou "...text here." (com contexto) ← certo

8. **Trocar "paper" por "manuscript"** em ponto-a-ponto

9. **Anonimização da point-by-point**
   - Remover lista de autores + afiliações (documento vai aos revisores)
   - Mas Yara flagrou: "para revisão, precisa estar sem identificação"

---

## Anonimização (Cegar para Revisão)

- **Manuscrito, suplementar, point-by-point:** remover bloco de autores + afiliação na p.1
- Isso é específico para revisão cega (Nature Communications)
- Mas Yara reforçou em múltiplos pontos

---

## Feedback sobre Checklists e Reporting Summary

### 07_ml_checklist (p.3)
- "Está em negrito?" — conferir formatação/negrito
- Uniformidade de fonte

### 08_reporting_summary (p.2, p.4)
- Uniformizar fonte do bloco (Python 3.14.3 / stacks)
- Deletar "(R3.6 revision)" — menção a revisor
- Remover bloco "NOTES FOR FILLING THE PDF" (lembrete operacional)

### 09_code_software_checklist (p.1, p.6)
- Tag "v1.1-natcomms-revision1" — decidir se muda para versão pública
- Checar identificação/anonimização também aqui

### Geral (todos extras)
- **Garantir que nenhuma figura quebre entre páginas** (página inteira por figura, sem split)

---

## Feedback Cover Letter

- **Figshare DOI** (10.6084/m9.figshare.31653373) **não abria** para ela
- Dúvida: "Esse link não está aberto. Qual é a ideia desse link? O que difere do que está no GitHub?"
- Ação: verificar se Figshare está acessível; explicar diferença Figshare (dados/figs com DOI) vs GitHub (código)

---

## Errata e Pendências Detectadas por Yara

| Item | Localização | Problema | Ação |
|------|-------------|---------|------|
| Referência numeração | "extraction[26]" | Se numérica, tem que ser ordem de aparição | Conferir estilo; corrigir |
| Título tabela | Texto longo no título | É assim em Nature? | Mover notas para footnote |
| Seção 3 | "§3" | Cross-ref quebrada | Verificar referência cruzada |
| Figshare availability | "will be made public at acceptance" | Supõe aceitação | Reescrever afirmativo |
| "Private Figshare" | Menção no artigo | URL privada não deve estar no corpo | Tirar, deixar só na cover letter |
| Table ?? | Supp p.21 | Referência cruzada quebrada | Gerar/resolver |
| Per-field table | Supp p.22 | Tabela ausente | Gerar arquivo .tex |
| Paths truncados | Supp p.19, p.21 | "g. .json", "outputs/revision/t3_judge", "d results. .json" | Revisar formatação |
| ML_checklist | p.7 | "Items still pending final number insertion" | Inserir números finais |
| Pass_at_1, paths | p.5, p.6 | Incompletos | Verificar completude |

---

## Próximos Passos Recomendados (Ordem de Yara)

1. **Varredura global** no manuscrito + suplementar removendo TODA menção a "reviewer/revision/Rx.x"
   - Regex sugerida: `revision|reviewer|R[13]\.\d`
   - Reescrever cada trecho como design choice/conteúdo nativo

2. **Anonimizar** manuscrito, suplementar, point-by-point (remover autores/afiliações)

3. **Reescrever point-by-point** colando texto literal + refs completas com DOI + figuras/tabelas embutidas

4. **Resolver pendências técnicas** (Table ??, tabela per-field, números finais)

5. **Cover letter**: validar Figshare access + explicar diferença vs GitHub

6. **Checklists/reporting**: uniformizar fonte, conferir negrito, decidir nome da tag

7. **Enviar para Yara** dar "aquela passada de olho rápida" antes de submeter (pedido explícito dela)

---

# PARTE 3: LIÇÕES "MUST-FIX", "SHOULD-FIX" DO PAINEL CRÍTICO

## 7 MUST-FIX Críticas (Bloqueantes)

Fonte: `/Users/lucasrover/paper-experiment/CRITICAL_REVIEW_PANEL.md`

### M1: Citação He et al. 2025 (falta de engagement com literatura recente)
**Problema:** Paper "Defeating Nondeterminism in LLM Inference" (Thinking Machines, 2025) ataca tese mecanística; não citado.
**Solução:** Posicionar como complementar
- Eles = provider-side em stacks abertos (open-weight)
- Você = quantificação cross-provider em APIs fechadas + protocolo client-side
**Lição:** Sempre scan literatura recente 6 meses antes de submeter. Se paper recente ataca sua tese, **cite e posicione**. Nunca ignora porque "ele não contradiz, só trabalha um problema relacionado".

### M2: Calibração causal — "implicates production infrastructure, **not** cloud"
**Problema:** Abstract/Intro/Discussion fazem afirmação muito forte
- Seu texto: "implicates production infrastructure, not cloud"
- Correto: "is consistent with production infrastructure complexity rather than the cloud medium itself"
**Solução:** Downgrade de causal claim para consistency claim
**Lição:** "Implicates" é causal forte; "is consistent with" é inferencial fraco. Together AI quasi-isolation é **evidência**, não **prova**. Confound potencial: escala × complexity ambos variam entre L-LLaMA3 e C-LLaMA3. Mantenha claim defensável.

### M3: Contradição BERTScore — ">0.97 across all models"
**Problema:** Main text (L210) says ">0.97 across all models/conditions". Supp S13 contradiz (vários <0.97; legenda S13 diz ">0.94").
**Solução:** Qualificar: "aggregate (whole-output) >0.97; per-field >0.94"
**Lição:** **QUALIFIQUE MÉTRICAS AGREGADAS.** Não diga "BERTScore > 0.97" sem especificar:
- Qual nível de agregação (per-output? per-field? per-stack?)
- Qual é o minimum observado (não só média)
- Quando a métrica satura vs quando discrimina
Isso é especialmente crítico quando sua tese é "inconsistências não-documentadas minam reprodutibilidade" — não podes ter uma métrica inconsistentemente documentada no próprio paper.

### M4: ERRO DE DADO — GPT-4 EMR "on RAG"
**Problema:** Supp S3 L196 reporta "GPT-4 EMR=0.230 on RAG" — mas **GPT-4 nunca rodou RAG**. É a EMR de summarisation, mal-rotulada.
**Solução:** Trocar por Claude RAG=0.000 / Gemini RAG=0.070
**Lição:** **AUDITORIA GRANULAR DE DADOS.** Antes de submeter:
1. Cross-ref toda tabela/figura contra source data
2. Se um valor parece outlier, rastreie até o Run Card original
3. Se há stack×task coverage matrix, valide contra cada combinação reportada
Um erro de rótulo como esse é exatamente o tipo que "erosão de confiança" causa em reviewers. Pior ainda para um paper sobre reproducibility.

### M5: Aritmeticamente impossível — discordâncias inter-juiz
**Problema:** Texto diz que as 7 discordâncias inter-juiz caem todas numa célula, mas Claude só tem 5 "ambiguous" (supp L871, main L258).
**Solução:** Suavizar p/ "5 de 7" + matriz de confusão 3×3
**Lição:** Quando relatar agreement metrics (Cohen's κ, etc.), **sempre mostre a matriz de confusão completa**. Não resuma em uma frase. Números não bate = red flag para desk-reject.

### M6: Mismatch cover-letter ↔ manuscript
**Problema:** Cover letter L55 promete "pass@1 for code and final-answer accuracy for math" — o manuscrito reporta **só EMR**. 
**Solução:** Adicionar a linha de pass@1/accuracy (dados já existem) OU reescrever a frase cover letter
**Lição:** **COVER LETTER PRECISA MATCH O MANUSCRITO EXATAMENTE.** Antes de enviar:
- Toda claim na cover letter tem que ter evidence correspondente no manuscript
- Se adicionar novos dados/análises na revisão, **atualiza AMBOS**: manuscript E cover letter
- Se não pode adicionar dados, remova a claim da cover letter

### M7: "GPT-4.1" não está no estudo
**Problema:** Main L255, L483 menciona "GPT-4.1" — não é um dos 9 stacks. É snapshot do companion paper, importado sem sinalizar.
**Solução:** Clarificar inline que é external context
**Lição:** **QUANDO CITAR RESULTADOS EXTERNOS,** sempre indique fonte:
- "In our accompanying paper (Rover & de Souza Tadano, 2026, OSF), gpt-4.1 [model description] achieved..."
- Não misture stacks seu estudo com stacks external papers sem etiqueta
- Torna impossível reproduzir se reader não sabe qual stack é qual

---

## 10 SHOULD-FIX Críticas (Fortalece Materialmente)

### S1: Honestidade do "four-fold gap"
**Problema:** "4× local-vs-API gap" é verdade só para GPT-4+Claude; "4-stack" é ~3×
**Solução:** Liderar com o 3.1× [2.48–3.61] do subsample balanceado
**Lição:** Quando effect size varia muito por subgroup, **sempre reporte o efeito principal equilibrado ALÉM do efeito não-equilibrado**. Isso torna honest a magnitude do fenômeno. Em code/math, δ agregado é +0.266 (small efeito), dirigido pelo pior stack — declare isso também.

### S2: Atenuar dependência do LLM-as-judge
**Problema:** κ=0.29 "fair", n=30, sem ground-truth humano, juízes não-repetidos
**Solução:** Mover peso retórico para per-field EMR (Cohen d=+1.41), que não depende de juiz
**Lição:** **LLM-as-judge é ferramenta, não prova.** Se seu juiz é outro LLM:
- Reporte agreement metrics completos (κ, PABAK, matriz confusão)
- Reconheça viés: LLMs podem concordar por razões erradas
- Não use LLM-judge como única evidência; acumule evidence layers (structural, quantitative, qualitativo, cross-provider)
- Nomear o paradoxo de κ alta-prevalência (κ deprime quando categoria é dominante) + report PABAK também

### S3: Janela de coleta ausente
**Problema:** Por sua própria tese, resultado de API é reproduzível relativo à época (snapshot drift). Não documentou datas por provedor.
**Solução:** Adicionar datas de medição por provedor (já estão nos Run Cards)
**Lição:** **SEMPRE DOCUMENT ACQUISITION WINDOW.** Para qualquer dados de API/online:
- Data da primeira e última coleta
- Se houve downtime, mudança de versão, rollout
- Isso torna claro que "EMR=0.220" é ponto-em-tempo, não universal
- Num companion paper/update, pode replicar com novas datas e mostrar "drift" de EMR

### S4: Tabela 1 mistura C1/C2 sem rótulo claro
**Problema:** Main L123 diz "with fixed seeds GPT-4=0.443" — mas esse número é C2 (variable seed, OpenAI advisory)
**Solução:** Corrigir rótulos/legendas de tabela
**Lição:** **SEMPRE ROTULE CONDIÇÕES EXPERIMENTAIS EM TABELAS.** Exemplo formato:
- "Table 1: Exact Match Rate (EMR) under greedy decoding (C1: fixed seed) or variable-seed (C2: as advised by provider)"
- Footnote: "OpenAI seed is advisory (C2); all other stacks use C1"
- Per-row or per-cell indicators se houver mixing

### S5: Cross-ref quebrada — Environment/provenance
**Problema:** Backmatter L713 promete "(S10) Environment/provenance" — mas §S10 é outra coisa
**Solução:** Resolver todas cross-refs; documentar environment_hash e versões de client-libs
**Lição:** Antes de submeter, **rode check de refs:**
```bash
grep -r "§S[0-9]\|S[0-9]\|Figure [0-9]\|Table [0-9]" manuscript.tex | \
  while read line; do
    ref=$(echo $line | grep -o "§S[0-9]*\|S[0-9]*\|Figure [0-9]*\|Table [0-9]*" | head -1)
    # Check if ref exists in supplementary/main
  done
```
Ou manualmente: lista todas as refs, cross-check contra numeração final do PDF.

### S6/S7: HumanEval/GSM8K IDs não enumerados
**Problema:** Cross-ref "full lists in S11" quebrada; prompt verbatim do juiz em S12 ausente
**Solução:** Enumerar todos IDs; colar prompts verbatim
**Lição:** **SEMPRE INCLUA PROMPT VERBATIM.** Se um revisor quer verificar "esse juiz era imparcial?", ele precisa ler o prompt exato. Não confie em "see supplementary" — **COLE O PROMPT INTEIRO**, mesmo que seja longo. Para juízes de LLM, inclua também parâmetros de decoding (temperature, top-p, max tokens).

### S8: Não contar "deployment stack" como novidade se já existe em literatura
**Problema:** Risco de ser accused de "not novel, just terminology from [atil2024]"
**Solução:** Rebaixar ou clarificar que novidade é aplicação systematic dessa lente a reproducibility
**Lição:** **CLARIFY O QUÊ É NOVEL VS O QUÊ É FRAMEWORK/TERMINOLOGY.** Exemplo:
- "Prior work has identified that [atil2024] that inference can be non-deterministic. Our contribution is to: (1) quantify this systematically across 7,004 experiments and 9 stacks; (2) show it persists in high-stakes regimes (code, math, RAG); (3) provide a client-side audit protocol (W3C PROV-based) that makes it visible."
Isso torna claro que terminologia pode existir, mas sua aplicação + protocol + scale é nova.

### S9: Companion paper "23 effects" em destaque — flag como preregistered not-yet-peer-reviewed
**Problema:** Companion paper (OSF, não-revisado) sustenta "23 effects" em destaque
**Solução:** Flag inline "preregistered, not yet peer-reviewed"; deixar §Applied impact carregar significância nos dados deste paper
**Lição:** **QUANDO CITAR WORK UNDER REVIEW,** sempre declare status:
- "Our preregistered companion analysis (OSF: 10.17605/OSF.IO/VR934, not yet peer-reviewed) quantifies this on a 500-abstract corpus, finding up to 23 study-level effect estimates appear/disappear. The present manuscript's in-paper validation (two-judge LLM-as-judge on 30 new cases) provides self-contained evidence independent of the companion paper."
Isso torna claro que companion paper é context, não load-bearing.

### S10: FWER só cobre Tasks 1-2; claims code/math são descritivos mas parecem inferenciais
**Problema:** Família-wise error rate correction cobre só 2 de 6 tasks; descritive results usam language("widens", "confirms") que parece inferencial
**Solução:** Adicionar 2ª família corrigida OU declarar descriptive no main
**Lição:** **SEMPRE DECLARE QUANDO RESULTADOS SÃO DESCRIPTIVE vs INFERENTIAL.** Exemplo:
- Inferential (hypothesis test, FWER correction): "We tested whether code generation exhibits the same reproducibility pattern as extraction (n=30 problems, 5 reps, 8 stacks; Holm-Bonferroni α=0.05). We find [result]."
- Descriptive (pilot, proof-of-concept): "As a proof-of-concept, we examined [task] (n=30 problems, pilot sample). Results show [descriptive statistic]. These findings are illustrative and require replication with pre-registered hypothesis tests."
Se misturar, você abre a si mesmo para crítica de "cherry-picking".

---

## Críticas OPCIONAIS (Polimento)

- CIs degenerados [1.00, 1.00] → usar Clopper-Pearson/Wilson em vez de simple binomial
- Power analysis a-priori em vez de post-hoc
- Reconciliar contagens de runs (3,904 vs 4,104 vs 7,004) com uma linha explicativa
- Seed do bootstrap (está hardcoded? reproduzível?)
- Box 1 — mostrar que Claude run com "seed=42" não foi honrado
- "Eight stacks" — Perplexity também tem Tasks 1-2, ser mais preciso sobre count
- Refs: Cliff 1993 + Vargha-Delaney para thresholds de δ; model cards corretos (Claude versão exata)
- Abstract: "domain sweep" (code, math, extraction, RAG, etc.) vs "dados realmente testados" — ser consistente
- Tell patterns: "not X but Y" aparece 5×+; "per se" / "itself" ~12×; repetição "local-vs-API local--API" (L797) — tighten prose
- Display items: ~11 no main; considerar mover Methods Table 3 (6 mechanisms) para Extended Data para liberar espaço

---

# PARTE 4: PRINCÍPIOS DE ESCRITA/ESTRUTURA DO MANUSCRIPT

## Estrutura de Seções — Order e Conteúdo

**Arquivo principal:** `article/ncomms_main.tex` (28–29 páginas)

### Abstract (~150 palavras, unreferenced)
**Estrutura:**
1. Motivation (1–2 sentences): "Large language model APIs serve research... under settings documented as deterministic. We show this guarantee fails."
2. Methods snapshot (1 sentence): "Across 7,004 experiments on nine deployment stacks and six task families..."
3. Key finding (2 sentences): "API-served stacks reproduce their own outputs as little as 1% under temperature-zero greedy decoding... while local-stack averages reach 93–98%."
4. Invisibility problem (1 sentence): "The variation is invisible: outputs appear semantically equivalent (BERTScore F1 > 0.97) but diverge textually..."
5. Validation (1 sentence): "Two blinded LLM judges classify the majority (73–90%) as truly contradictory."
6. Quasi-isolation mechanism finding (1 sentence): "A quasi-isolation experiment with identical LLaMA 3 8B weights shows cloud deployment alone does not preclude reproducibility..."
7. Solution/contribution (1 sentence): "We release a W3C PROV-based provenance protocol (< 1% overhead) making hidden variation auditable."

**Lição:** Abstract é um **mini-paper**:
- Setups o problema em contexto (why should anyone care?)
- Métodos em 1 line (enough to understand scope)
- Resultados numerados (sempre com ranges/CIs, não só points)
- So what? (downstream impact, practitioner relevance)
- Solution (what do readers take away?)

---

### Opening paragraphs (No heading — "Introduction" em Nature é unnamed)

**Padrão:**
1. **Motivation (2 paras):** LLMs now standard research instruments; trust based on "deterministic" API docs; our experiments show this guarantee fails
2. **Reproducibility context (1 para):** 70% researchers can't reproduce; AI field has only 6% papers with sufficient reproducibility info; yet inference reproducibility is unexamined
3. **Gap in tools (1 para):** MLflow etc. designed for training, not inference-time text-generation provenance
4. **This work summary (1 para):** 7,004 controlled experiments, 9 stacks, 6 task families; local 95.6% vs API 22.1% EMR
5. **Hidden variation problem (1 para):** Non-determinism is invisible to users (BERTScore > 0.97 but textually different)
6. **Compounding in agentic pipelines (1 para):** As LLMs move into multi-agent systems, variation compounds at every step
7. **Central conceptual insight (1 para):** Deployment stack (weights, provider, infrastructure, API) is unit of analysis, not abstract model
8. **Five contributions (1 para):** (i) systematic quantification, (ii) persistence in multi-turn/RAG, (iii) quasi-isolation result, (iv) code/math extension, (v) W3C PROV protocol

**Lição:** Introdução em Nature é **story**, não literature review.
- Comece com problema concreto (não abstract theory)
- Mostre por quê importa (não confie em "readers will know")
- Cite trabalho PRIOR ao estabelecer gap ("while prior work has noted X [cit], the scale/systematic quantification/mechanism was unknown")
- Termine com 5 contributions **numeradas** (não prose) para que editor/reviewer possam contar

---

### Results (5–6 subsections, ~10 páginas)

#### Subsection 1: "API-served deployment stacks fail to reproduce outputs under deterministic settings"
- **Content:** Table 1 heatmap; local EMR (Gemma, LLaMA, Mistral); API EMR (GPT-4, Claude, Perplexity)
- **Metrics reported:** EMR + 95% bootstrap CI; Holm-Bonferroni correction across 68 tests; Cliff's delta effect sizes
- **Control experiment:** Chat format control (200 runs) confirma prompt format não contribui variação
- **Key claim:** "fewer than one in four API output pairs are identical under conditions documented as deterministic"
- **Size:** ~3 páginas

#### Subsection 2: "Non-determinism varies substantially across providers"
- **Content:** 80-fold range (DeepSeek EMR 0.800 vs Perplexity 0.010); mechanism for Perplexity (retrieval augmentation)
- **Key insight:** Task structure mediates reproducibility (JSON extraction > free-text summary)
- **Size:** ~1.5 páginas

#### Subsection 3: "Cloud deployment does not preclude reproducibility" [Quasi-isolation]
- **Content:** Together AI result; L-LLaMA3 (0.987) vs C-LLaMA3 (0.780) vs API-GPT4 (0.443)
- **Interpretation:** Cloud factors ≠ infrastructure factors; production infrastructure is the culprit
- **Caveat:** Cannot test this on proprietary stacks (non-local)
- **Size:** ~1 página

#### Subsection 4: "Outputs diverge textually but not semantically" [Per-field analysis]
- **Content:** Per-field EMR, NED, ROUGE-L, BERTScore F1; conclusion-relevant (0.455) vs metadata (0.684) EMR; BERTScore saturated
- **Key insight:** Three-level reproducibility framework needed (bitwise → structural → semantic)
- **Example:** Gemini RAG key_result: EMR=0.10 but BERTScore=0.969
- **Size:** ~1 página

#### Subsection 5: "Applied impact in evidence synthesis: an out-of-AI/ML probe"
- **Content:** 10 PubMed PM2.5 abstracts; pattern replicates (Claude EMR 0.010); two-judge LLM-as-judge on 30 new cases
- **Validation metrics:** κ=0.29, Cohen's PABAK=0.53, 76.7% agreement
- **Key finding:** 73–90% of divergences are truly contradictory per judges
- **Downstream logic:** Single divergence → parsing → aggregation → 23 effects appear/disappear
- **Size:** ~2–2.5 páginas

#### Subsection 6: "Coding and math reasoning"
- **Content:** HumanEval (30 problems) + GSM8K (30 problems), 5 reps, 8 stacks
- **Results:** Local/Together ~0.92–1.00; API: Claude worst (0.39 code, 0.063 math)
- **Key insight:** Gap **widens** on tasks where textual difference alters functionality
- **Size:** ~1 página

---

### Methods (~8 páginas)

#### Subsection: "Unit of analysis: deployment stacks"
- Define deployment stack = (weights, provider, infrastructure, API layer)
- Explain why same weights on two stacks = two distinct experimental objects
- Together AI quasi-isolation as evidence
- **Length:** ~200 palavras

#### Subsection: "Deployment stacks evaluated"
- Table listing all 9 stacks with full tuple specification
- Per-stack parameter exposure (temperature, seed, etc.) + seed_status
- **Length:** ~300 palavras

#### Subsection: "Tasks and datasets"
- 6 task families: extraction (JSON), summarization (free text), multi-turn, RAG, code (HumanEval), math (GSM8K)
- Data sources (30 AI/ML abstracts, 10 PM2.5 abstracts, 30 HumanEval, 30 GSM8K)
- Structured extraction fields (objective, method, key_result, etc.)
- **Length:** ~200 palavras

#### Subsection: "Experimental conditions"
- C1 (greedy, fixed seed) vs C2 (greedy, variable seed)
- Per-stack seed handling (OpenAI advisory, Anthropic absent, Gemini empirically insufficient)
- **Anthropic seed handling:** explicit paragraph
- Warm-up / cache state control
- **Length:** ~200 palavras

#### Subsection: "Sources of non-determinism in distributed inference"
- **Opening:** Cloud deployment factors vs production serving infrastructure factors (distinguished explicitly)
- 6 mechanisms: FP non-associativity, mixed-precision, tensor parallelism, FlashAttention, dynamic batching, speculative decoding
- **Table 3** (Methods): mechanism × stack mapping (verifiable, likely, possible, mitigated)
- Together AI result licenses inference re: cause attribution
- **Length:** ~400 palavras + Table 3

#### Subsection: "Protocol design"
- **Scope: client-side observability** (separate subheading)
- W3C PROV standard; Run Cards; SHA-256 hashing
- What is observable (request, response, latency, hashes)
- What is not (weight hashes, kernel-level traces)
- **Length:** ~250 palavras

#### Subsection: "Metrics"
- EMR (exact match rate), NED (normalized edit distance), ROUGE-L, BERTScore F1
- Why three-level framework: bitwise vs structural vs semantic
- Per-field computation
- Bootstrap CIs (10,000 resamples, Holm-Bonferroni correction for Tasks 1-2)
- **Length:** ~250 palavras

---

### Discussion (~5 páginas)

#### Subsection: "Deployment stack as carrier of variation"
- Reframe finding through lens of quasi-isolation result
- Same weights, different stacks → different reproducibility
- Implication: research docs should name deployment stack, not "the model"
- **Length:** ~200 palavras

#### Subsection: "Invisibility as a source of error propagation"
- Chain: textual divergence → parsing → aggregation → statistical impact
- 23 effects example from PM2.5
- Implication for evidence synthesis, regulatory submissions
- **Length:** ~200 palavras

#### Subsection: "Limitations"
- Quasi-isolation only for open-weight stacks (cannot test proprietary)
- 30 abstracts, English only (non-English coverage remains open)
- LLM-as-judge has bias; need human validation (future work)
- Point-in-time EMR values (snapshot drift as providers update)
- **Length:** ~250 palavras

#### Subsection: "Recommendations for practice"
- For researchers: log deployment stack + Run Cards
- For API providers: consider reproducibility-prioritized execution modes
- For journals/policy: require stack specification + run-level provenance
- For LLM-based evidence synthesis: treat non-determinism as parameter, not noise
- **Length:** ~200 palavras

---

### Supplementary Information (S1–S13, ~23–25 páginas)

| Section | Content | Pages |
|---------|---------|-------|
| S1 | Extended Methods (experimental protocol detail) | 2 |
| S2 | Per-stack parameter listings (full API calls) | 3 |
| S3 | Model snapshots and versioning | 2 |
| S4 | Comparability across providers + Table S2 (API links) | 2 |
| S5 | W3C PROV specification adapted for Run Cards | 1.5 |
| S6 | Task definitions (extraction schema, summarization rubric) | 2 |
| S7 | Chat format control experiment (200 runs, detailed) | 1.5 |
| S8 | Holm-Bonferroni correction details (68 tests, α=0.05) | 1.5 |
| S9 | Statistical power analysis (post-hoc, MDE) | 1.5 |
| S10 | Coverage matrix (which stack × which task) + rationales | 1.5 |
| S11 | Revision-batch tasks (HumanEval, GSM8K, PubMed details) | 3 |
| S12 | Two-judge LLM-as-judge protocol (prompts, verdicts, κ, PABAK) | 3 |
| S13 | Per-field reproducibility table (EMR/NED/ROUGE-L/BERTScore by field) | 2 |

**Lição:** Supplementary Information é **where you prove you didn't cheat**.
- Método detail cukup detail untuk diberikan ke graduate student untuk replicate
- Semua prompts verbatim (bahkan panjang)
- Semua covariates, semua parameter exposure
- Statistical reasoning (tidak hanya hasil, tapi why you chose that test)

---

## How Claims Were Calibrated — Overclaiming vs Underselling

### Claim Calibration Examples

| Original Claim | Issue | Calibrated Claim | Evidence |
|---|---|---|---|
| "Cloud deployment causes non-determinism" | Causal, unwarranted (confound: scale + infrastructure) | "Cloud deployment alone is not a sufficient cause; production infrastructure complexity is consistent with the gap" | Together AI result (0.78 vs 0.22 with same cloud access) |
| "We prove the quasi-isolation for all stacks" | Cannot test proprietary locally | "Quasi-isolation tested for open-weight LLaMA 3 8B; proprietary stacks remain opaque" | Acknowledges L-/C-/API contrast but not L-/C-/proprietary |
| "BERTScore > 0.97 shows semantic equivalence" | Metric saturates on small fields | "Aggregate BERTScore > 0.97 but per-field analysis reveals conclusion-relevant fields have EMR 0.455; BERTScore is structurally unable to discriminate substantive divergence" | Per-field table S13; Gemini RAG example |
| "23 effects disappear due to non-determinism" | Depends on companion paper (under review) | "Up to 23 effects appear/disappear in our companion paper (Rover & de Souza Tadano, 2026, preregistered OSF). In-paper validation on 30 new cases with two independent judges confirms 73–90% are substantive" | In-paper two-judge data |
| "Non-determinism is universal across all domains" | Limited to English, AI/ML + health abstracts | "Pattern replicates across extraction, summarization, code, math, and out-of-AI/ML health domain (all English). Non-English and low-resource domain generalization remains open" | Explicit in Limitations |

**Lição:** **Claim calibration is an art, not a rule.** Ask:
1. Qual é a EVIDENCE mais forte que tenho? (quasi-isolation = local result, não universal)
2. O quê isso realmente prova? (not "X causes Y" but "X is consistent with Z" ou "not-X is implausible")
3. Onde são as gaps onde reviewers podem atacar? (proprietary stacks, human judgment, non-English) → acknowledge upfront
4. Como posso communicate incerteza sem weakening contribution? (use "in this sample", "consistent with", "suggests" em vez de "proves")

---

## Tratamento de Limitações — Honestidade vs Defensibilidade

### S2 Example: LLM-as-judge limitations
**Weak framing:** "We used LLM-as-judge for validation."
**Strong framing:**
> "We validated substantive divergence through a multi-layered approach: (1) structural analysis (per-field EMR), which does not depend on any judge; (2) quantitative two-judge LLM-as-judge on 30 new cases with inter-judge κ=0.29 (fair agreement, Landis-Koch scale); (3) cross-provider judges (Claude Opus 4.7, gpt-4o) to address LLM-on-LLM bias. The κ value is depressed by high prevalence of truly_contradictory category (PABAK=0.53); both judges' lower bounds on truly_contradictory proportion (56% Claude, 74% gpt-4o) exclude cosmetic interpretation."

**Why this works:**
- Acknowledges judge bias explicitly
- Reports uncertainty (κ, CI)
- Provides structural escape hatch (per-field EMR doesn't need judge)
- Explains κ paradox (high prevalence depresses Cohen's κ but not PABAK)
- Quantifies what "disagreement" means (both agree majority is contradictory; differ on ambiguous edge cases)

---

## Pré-Registro vs Post-Hoc — Como Sinalizar Cada Um

### Example from Paper

**Pré-registrado (OSF companion paper):**
> "Our preregistered companion analysis (Rover & de Souza Tadano, 2026, OSF: 10.17605/OSF.IO/VR934) reports a 500-abstract systematic pairwise reproducibility analysis, silver-standard validation, and meta-analytic propagation."

**In-paper (post-hoc):**
> "To validate our findings, we conducted a post-hoc two-judge LLM-as-judge protocol on 30 new cases sampled from the same PM2.5 corpus but distinct from the 23 study-level effects in the companion paper."

**Lição:** Sempre declare quando é cada um:
- **Pré-registrado:** "Our OSF-preregistered analysis (link) found..."
- **Confirmatory (post-hoc mas specified a priori):** "To test the hypothesis that [pré-registered claim], we conducted [test] finding [result]"
- **Exploratory:** "As an exploratory analysis, we examined [post-hoc question] and found [result, descriptive]"

Isso faz muito difícil para alguém acusar "cherry-picking" porque você foi transparente sobre ordem de discovery.

---

## Uso de Boxes/Tabelas/Figuras — Mecanismo × Hipótese

### Box 1: Concrete Examples
**Purpose:** Make outputs visible to reader who hasn't read supplementary
**Content:** Side-by-side pairs; cosmetic divergence (1 exemplo) + substantive divergence (2 exemplos)
**Format:** Colored diff highlighting; Run IDs for auditability
**Position:** After Figure 5, before Discussion
**Size:** Full-width, 1–1.5 páginas

**Lição:** Boxes são real estate — use para:
- Concrete examples (não resumen abstratos)
- Case studies que illustration key insight
- Provenance/methodological transparency (como um run card looks)

### Table 1: Main Results
**Structure:** Stack (rows) × Task (columns)
**Content:** EMR + 95% CI; stacks in order: locals, Together, APIs
**Color coding:** Heatmap (green=high, red=low)
**Caption:** ~150 palavras, enumerate stacks shown, explain absent ones
**Lição:** Tabelas principais não devem ter footnotes nos titles. Keep captions clean. Relegue details a Supplementary Table.

### Table 3 (Methods): Mechanism × Stack
**Structure:** 6 mechanisms (rows) × 5 stacks (columns)
**Cells:** ✓, "likely", "possible", ---, △
**Purpose:** Transparent attribution causal (which mechanism implicates which stack)
**Footnote:** "For closed-source stacks, attribution is necessarily inferential"
**Lição:** Mechanism tables são **argumentative instruments**. Cada cell documenta uma step de logical inference. Não deixe cells blank sem explicar por quê.

### Figure 1: Heatmap (EMR by stack × task)
**Content:** 9 stacks (rows) × 4 tasks (columns); EMR values + CIs in color
**Caption:** Enumerate stacks shown; explain absences (e.g., Gemini only on Tasks 3–4)
**Legend:** Color scale from 0 (red) to 1.0 (green)
**Size:** Full-width, 1 página
**Lição:** Heatmaps são "aha!" moments. Readers get pattern instantly. Use when you have many stacks/tasks. But enumerate in caption; don't make reader guess what colors mean.

### Figure 2: Multi-turn/RAG results
**Structure:** Grouped bar chart; 4 API stacks × 3 task types (single-turn extraction, single-turn summarization, multi-turn, RAG)
**Content:** EMR + 95% CI; compare local baseline (horizontal line) to APIs
**Message:** "Near-zero reproducibility widens in complex workflows"
**Size:** Full-width, 1 página

---

## Rastreabilidade de Citações — Anti-Fabricação

### Practice from NatComms Paper

**Rule 1: Toda referência tem que aparecer em bibliography**
```
\cite{he2025defeating} — deve ter correspondente \bibitem{he2025defeating}
```

**Rule 2: Citações ordenadas por ordem de aparição (Vancouver style)**
Antes de submeter, run:
```bash
grep -o '\\cite{[^}]*}' ncomms_main.tex | sort -u > cited.txt
grep -o '\\bibitem{[^}]*}' references.bib | sort -u > bibbed.txt
# Compare; resolver orphans
```

**Rule 3: Qualquer claim numérica precisa de suporte**
- Não diga "BERTScore > 0.97" sem citar tabela ou estudo
- Não diga "23 effects appear/disappear" sem citar companion paper com DOI

**Rule 4: Ao citar outro paper's result, inclua números exatos**
Não: "prior work found non-determinism in LLMs"
Sim: "Atil (2024) reported non-determinism in 15% of API runs under fixed-seed conditions"

**Lição:** **Reproducibility papers têm credibilidade zero se citações são não-verificáveis.** Você quer ser bulletproof. Triple-check refs.

---

# PARTE 5: ERROS E ARMADILHAS A EVITAR

## Erros Críticos (de `CRITICAL_REVIEW_PANEL.md`)

| Erro | Tipo | Impacto | Prevenção |
|------|------|--------|----------|
| M1: Missing recent paper que ataca tese | Citation gap | Desk-reject possible (editor vê paper recente que não foi citado) | Scan arXiv/scholar mensalmente nos 6 meses antes de submeter; set up Google Scholar alerts |
| M2: Causal claim sem suficiente evidência | Overclaiming | Reviewer demands downgrade ou rejection | Sempre use "is consistent with" unless você tem quasi-experiment ou RCT |
| M3: Métrica reportada inconsistentemente | Data integrity | Red flag; erosão confiança no paper | Qualifique toda métrica agregada: "per-field", "aggregate", "minimum observed" |
| M4: Erro de rótulo (GPT-4 "on RAG" quando nunca rodou RAG) | Data error | FATAL — desk-reject possível | Audit granular: trace cada valor reportado até Run Card original |
| M5: Números aritmeticamente impossíveis | Internal inconsistency | Desk-reject; shows manuscript wasn't proofread | Report matrices completas (confusion matrices, not summaries); validate totals |
| M6: Cover letter promete algo que manuscript não tem | Mismatch | Reviewer abre cover letter, depois abre manuscript, vê inconsistência | Sempre compile cover letter + manuscript juntos; cite manuscript pages/tables em cover letter |
| M7: Mistura stacks seu estudo com stacks external papers sem etiqueta | Confusion | Leitor pode replicar estudo errado; loss of trust | Label every external reference: "In our companion paper...", "In [author, year]..." |

---

## Armadilhas de Redação

### Overclaiming Patterns

**Red flags:**
- "proves that X causes Y" (sem isolate experiment)
- "all / always / never / universally" (sem coverage absoluta)
- "demonstrates" (sem proof; use "shows", "finds", "observes")
- "obviously", "clearly", "trivially" (without evidence)

**Safe alternatives:**
- "is consistent with"
- "suggests that"
- "provides evidence for"
- "in the cases examined"
- "across the stacks tested"

### Invisibility of Overselling

**Temptation:** "Our results show that LLM non-determinism undermines ALL evidence synthesis"
**Problem:** You tested 30 abstracts, not all evidence synthesis
**Better:** "Our results suggest that LLM non-determinism could compromise evidence synthesis; 23 effects appear/disappear in a 500-abstract companion analysis, indicating that current practices lack controls for this source of variation"

---

## Armadilhas de Dados

### Coverage Tracking
**Mistake:** Have data for 8 stacks but report results for 5 because 3 "didn't converge"
**Red flag:** Reviewer asks why Gemini missing from Fig 1; you say "different tasks", but reader wonders "did you selective-report?"
**Solution:** Create **explicit coverage matrix** (Fig. or Table):

| Stack | Extract | Summarize | Multi-turn | RAG | HumanEval | GSM8K |
|-------|---------|-----------|-----------|-----|-----------|-------|
| L-LLaMA3 | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| API-Claude | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| API-Gemini | — | — | ✓ | ✓ | — | — |

Justify in Supp: "Gemini evaluated only on Tasks 3-4 due to API quota constraints; full details in S10"

### Missing Data Imputation
**Mistake:** Have 10/10 results for 8 stacks but only 5/10 for Perplexity, so you exclude Perplexity from aggregate
**Problem:** Selects for stacks with complete data (bias)
**Solution:** Report both: (a) complete-case analysis (all stacks with 8+ tasks), (b) imputed analysis (all stacks, imputation method declared)

---

## Armadilhas de Interpretação

### Simpson's Paradox
**Risk:** "4× gap" is true for GPT-4 (0.443 vs 0.956) and Claude (0.190 vs 0.956), but when you pool all APIs, gap shrinks to 3.1×
**Mistake:** Don't acknowledge Simpson and someone will attack as cherry-picking
**Solution:** Report both (aggregate + subgroup); clarify weighting:
> "The 3.1× gap [2.48–3.61] is based on a balanced 10-abstract subsample. On the full 30-abstract dataset, the aggregate gap is 4.3× (0.956 local vs 0.221 API average, dominated by Claude and GPT-4; Table 1). We report the balanced estimate to avoid over-weighting the worst-case stacks."

### Hawthorne Effect / Demand Characteristics
**Risk:** "Our protocol makes non-determinism visible, so practitioners will avoid it"
**Problem:** Not a finding, a speculation
**Solution:** Acknowledge as limitation, don't claim credit:
> "Once aware of this phenomenon, practitioners might implement compensatory strategies (e.g., repeated runs with vote-aggregation, deterministic-execution guarantees from providers). We have not evaluated effectiveness of such mitigations."

---

## Armadilhas de Compliance

### Model Card Completeness
**Risk:** You say "GPT-4" but never specify snapshot (gpt-4-0613 vs gpt-4-turbo vs gpt-4o)
**Problem:** Impossible to reproduce; desk-reject
**Solution:** Every stack appearance, always include snapshot:
- First mention: "OpenAI's gpt-4-0613 (the model snapshot available during data collection, March 2026)"
- Subsequent mentions: "GPT-4 (gpt-4-0613)" in parentheses
- Methods Table: Column "Model / Snapshot identifier"

### API Documentation Currency
**Risk:** You cite "Anthropic Messages API" but API changed 3 months after you collected data
**Problem:** Someone replicates and gets different behavior
**Solution:** Include access date in every API reference:
> "\cite{anthropic2024} — accessed 2026-03-15. At the time of this writing, Anthropic Messages API v1 did not expose a seed parameter. This may change in future API versions."

---

# PARTE 6: FRAMEWORK ACIONÁVEL PARA REESCRITA

Aqui va u resumo de "como aplicar" ao seu artigo de benchmark de viés.

## Checklist de Escrita Acadêmica (adaptado de NatComms)

### ANTES DE COMEÇAR A ESCREVER

- [ ] **Define unit of analysis** — o quê você testa? (não "um LLM", mas "GPT-4 via OpenAI Chat Completions API with temperature=0, seed=42")
- [ ] **Create coverage matrix** — quais stacks × quais tasks / conditions
- [ ] **List mechanisms/causes** — se sua claim inclui "X causes Y", enumere 5–10 alternative explanations e como você as descarta
- [ ] **Plan validation layers** — quantitative + qualitative + cross-provider/cross-rater if applicable
- [ ] **Identify limitations upfront** — antes de escrever, já saiba: qual é o N? Qual é a domain? Qual é a language?

### DURANTE A ESCRITA

#### Abstract
- [ ] 150 palavras ou menos
- [ ] Motivation (1-2 sent); methods snapshot (1 sent); key findings (2+ sent, with ranges); solution (1 sent)
- [ ] Every number tem 95% CI or range, not point estimates
- [ ] Avoid citing within abstract

#### Introduction
- [ ] Comece problem (concreto); não theory
- [ ] Reproducibility context — cite "70% researchers..." or relevant benchmark
- [ ] Gap statement — "prior work has noted X [cit], yet the [scale / systematic study / mechanism] was unknown"
- [ ] Contributions listed numerically, not prose

#### Results
- [ ] Per subsection: one main insight per subsection
- [ ] Figures AFTER text introducing them (reader knows what to expect)
- [ ] Tables with explicit captions (>100 words, enumerate contents)
- [ ] Every number backed by a table/figure OR supplementary
- [ ] Per-field or per-subgroup analysis if heterogeneity suspected

#### Methods
- [ ] "Unit of analysis" section (define what you're testing)
- [ ] Parameter exposure table (what each provider accepts/rejects)
- [ ] Coverage matrix (which stack × which condition)
- [ ] Mechanism table (if causality is claimed)
- [ ] Per-field metrics (if structured output)

#### Discussion
- [ ] Limitations FIRST (not end) — preempt reviewer concerns
- [ ] Quasi-isolation result (if any) explained clearly
- [ ] Downstream impact / practitioner relevance
- [ ] Future work identified (not vague, but specific)

### ANTES DE SUBMETER

#### Citação Audit
- [ ] Every `\cite{key}` has matching `\bibitem{key}`
- [ ] Every claim of fact/number has a citation or table
- [ ] Bibliography sorted by citation order (Vancouver)
- [ ] No orphan citations

#### Coverage Audit
- [ ] Can reader identify: which stacks tested? which tasks? which conditions? which metrics?
- [ ] Is there a coverage matrix or explicit statement (e.g., "Gemini on Tasks 3-4 only due to API quota")?
- [ ] Are absences explained (not hidden)?

#### Data Integrity Audit
- [ ] Trace 10 random reported numbers back to source data
- [ ] Validate arithmetic (totals, percentages, proportions)
- [ ] Check for Simpson's paradox or other aggregation tricks

#### Overclaim Audit
- [ ] Grep for "proves", "demonstrates" → downgrade to "shows", "suggests", "is consistent with" unless evidence is bulletproof
- [ ] Grep for "all", "always", "never", "universally" → qualify with "in this sample", "across the stacks tested", "at the time of measurement"
- [ ] Grep for "obviously", "clearly", "trivially" → delete or cite support

#### Figure/Table Audit
- [ ] Every figure caption >100 words; states what is shown, what is not, why
- [ ] Every table has explicit row/column labels; no ambiguity
- [ ] Color-coding justified (not just "red is bad")

#### Supplementary Audit
- [ ] All prompts verbatim (full text, not summary)
- [ ] All parameters listed (temperature, top-p, max tokens, seed, seed_status)
- [ ] All metrics explained (why EMR, why not BERTScore alone?)
- [ ] Coverage matrix present

#### Reviewer-Ready Audit
- [ ] No mention of "revision", "reviewer", "response to R1.x" in main text
- [ ] Point-by-point response has verbatim text from manuscript, not references
- [ ] Point-by-point response has figures/tables embedded, not "see Figure 1"
- [ ] Cover letter claims match manuscript claims exactly

---

## Aplicação Ao Seu Artigo (Benchmark de Viés em LLMs)

Exemplo de como estruturar se está fazendo benchmark de viés (e.g., "qual LLM é mais biased?"):

### 1. Define Unit of Analysis Upfront
- Not: "GPT-4, Claude, and Gemini"
- Yes: "(GPT-4 via OpenAI Chat API, gpt-4o-2024-11-20 snapshot, temperature=0) × (Claude 3.5 Sonnet via Anthropic Messages API, temperature=0, no seed parameter) × (Gemini 2.5 Pro via Google AI API, temperature=0, seed=42)"

### 2. Coverage Matrix Explicitly
```
| Benchmark / Bias Type | GPT-4o | Claude 3.5 | Gemini 2.5 | LLaMA Local |
|---|---|---|---|---|
| Gender bias (StereoSet) | ✓ | ✓ | ✓ | ✓ |
| Racial bias (Bias Benchmark) | ✓ | ✓ | — (API limit) | ✓ |
| Stereotype (WordAssoc) | ✓ | ✓ | ✓ | — (not tested) |
```

Justifique absences: "Gemini was tested on StereoSet and Gender bias only due to rate limit constraints; allocation prioritized high-stakes bias types."

### 3. Per-Field / Per-Exemplar Analysis
If bias manifests differently by:
- **Demographic group** (gender M/F/NB; race A/B/C): report bias per group + aggregated, highlight subgroup disparities
- **Exemplar type** (occupations with male/female connotation): show which are most biased across stacks
- **Scale** (0-100 bias score): report distribution, not just mean; histogram or boxplot

**Lição:** Viés é inherently heterogeneous. "GPT-4 is more biased than Claude" is oversimplification if true on gender but false on race. Show the full matrix.

### 4. Validation Layers
- **Quantitative:** Bias score (WEAT, StereoSet, etc.) + direction (toward A or B group)
- **Qualitative:** Human raters (blinded) judge outputs on bias rubric; Cohen's κ
- **Cross-provider:** If bias pattern replicates across providers, it's not artifact of one API
- **Robustness:** Paraphrase prompts; does bias persist or vanish?

### 5. Mechanism Table
| Potential Cause of Bias | GPT-4o | Claude | Gemini | Evidence |
|---|---|---|---|---|
| Training data composition | likely | likely | likely | Public commitments re: debiasing in trainning; but no audit |
| RLHF alignment (different constitutions) | possible | possible | possible | Different public values; biasing direction differs across providers |
| Instruction-following (model obeys adversarial prompt?) | — | — | — | All stacks use same standard prompt; no adversarial jailbreak attempted |
| Tokenization artifacts | unlikely | unlikely | unlikely | Same English text; different tokenizers shouldn't affect semantics |

### 6. Example Outputs (Box equivalent)
Show 2-3 verbatim model outputs:
- One where GPT-4 is biased, Claude is not (or vice versa)
- One where both agree (neutral)
- One where both are biased (common issue, not stack-specific)

**Lição:** Readers want to see the evidence raw. Don't just report "GPT-4 male-bias score 67%". Show the actual outputs that received that score.

---

# FINAL SUMMARY

A framework completa de escrita acadêmica melhorada, extraída do paper NatComms, consiste em:

1. **Críticas dos revisores endereçadas sistematicamente** (R1.1–R1.15, R3.1–R3.6) → cada crítica mapeia a uma ou mais mudanças no texto/análises
2. **Feedback dos coautores aplicado**: nunca cite revisão no texto final; ponto-a-ponto com verbatim; cover letter precisa match manuscript exatamente
3. **Painel crítico multiagente**: 7 MUST-FIX (data integrity, citação, claims calibration) + 10 SHOULD-FIX (honestidade efeito size, documentação, cross-refs)
4. **Princípios de redação:**
   - Unit of analysis cristalina (deployment stack, não "model")
   - Coverage matrix explícita
   - Per-field / per-subgroup análise quando heterogeneidade existe
   - Three-level validation (quantitative + qualitative + cross-provider/rater)
   - Mecanismo table (causa × condição)
   - Concrete exemplos (Box com dados brutos)
5. **Estrutura de seções:**
   - Abstract: problem → methods snapshot → findings (ranges) → solution
   - Intro: motivation → gap → contributions (numbered)
   - Results: 5–6 subsections, cada um com one main insight
   - Methods: unit of analysis + parameter table + coverage matrix + mechanism table + metrics
   - Discussion: limitations first → downstream impact
   - Supp: verbatim prompts + per-field analysis + coverage matrix + mechanism mapping
6. **Checklist pré-submissão:**
   - Citação audit
   - Coverage audit
   - Data integrity audit
   - Overclaim audit
   - Reviewer-ready audit (sem menções a revisão no texto final)

Esta framew

ork é diretamente aplicável ao seu artigo de benchmark de viés. Adapte conforme necessário, mas mantenha estrutura e rigor.

