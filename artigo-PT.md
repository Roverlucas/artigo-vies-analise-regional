# Viés geográfico e linguístico em LLMs para política de poluição do ar: um benchmark de 25 países, 14 modelos, 4 idiomas e 5 tarefas

> **Versão em português para leitura interna** (tradução fiel do manuscrito em inglês, pós-revisão). Termos técnicos, nomes de modelos e valores numéricos preservados.

---

## Resumo

Gestores ambientais públicos no Sul Global recorrem cada vez mais a grandes modelos de linguagem (LLMs) para perguntar sobre padrões de qualidade do ar vinculantes, concentrações medidas e evidências de saúde — um domínio em que uma resposta errada pode moldar um parecer regulatório ou uma resposta de emergência. Se esses sistemas atendem o Sul Global com a mesma confiabilidade que o Norte Global, e se o enquadramento do prompt altera a resposta, não havia sido medido para um domínio aplicado de política com ground truth verificável. O PM₂.₅ é o principal fator de risco ambiental para mortalidade prematura, e seu ônus recai desproporcionalmente sobre o Sul Global *(GBD 2019; OMS 2021; Joshi et al. 2020; Mohamed et al. 2020)*.

Avaliamos **25 países, 14 LLMs, quatro idiomas e cinco tipos de tarefa** (recall normativo, dados medidos locais, síntese de evidência em saúde, instrumentos de política e recomendação aplicada) no domínio de política de poluição do ar, contra ground truth oficial, com um fator persona intra-sujeito (neutro versus gestor ambiental público) e um contraste intra-país inglês/idioma-nativo. O desenho foi pré-registrado para 15 países; em seguida o estendemos *post hoc* para 25 (sete a mais do Norte Global, três a mais do Sul Global) para ganhar poder, reportando cada efeito ao lado de seu valor pré-registrado de 15 países.

A partir de escores compostos por LLM-como-juiz, encontramos uma **lacuna de *tier*** Norte/Sul de **+6,2 pp** (IC bootstrap 95% [+3,7, +8,6]). Um **gradiente de desenvolvimento** aparece na amostra de 25 países (Spearman ρ=0,51 com o IDH, p=0,004; Mann-Kendall p=0,018; robusto a *leave-one-out*). Ele era indetectável no n=15 pré-registrado (ρ=0,14) e fica **abaixo do nosso limiar de tamanho de efeito pré-registrado de 0,55**, e segue o desenvolvimento, não a classe de recurso linguístico (Joshi nulo). Três danos são robustos: (a) prompts no idioma nativo **reduzem** a acurácia (−2,1 pp no geral, p=2×10⁻³; −7,8 pp para o hindi), então o idioma local não ajuda e pode prejudicar; (b) a acurácia despenca no recall de padrão técnico e dado local (T1, T2 ≈ 0,37 vs 0,64 nas demais; δ=−0,64), um piso de corte regulatório; (c) o modelo regional em português brasileiro é o pior de todos (δ=−0,51). Três correções intuitivas falham juntas: nem uma persona de gestor local (permutação p=0,26), nem o idioma local, nem um modelo regional fecham a lacuna.

Sobre o **mecanismo**: o proxy de corpus pré-registrado (tamanho da Wikipédia) é nulo; um proxy de cobertura-do-país (sitelinks da Wikidata) correlaciona-se com a acurácia (ρ=0,54, p=0,005, sobrevivendo à correção por multiplicidade), mas **atenua para não-significância após ajuste por desenvolvimento (p=0,13)** — por isso reportamos a cobertura-do-país como um canal **sugestivo e exploratório** (melhor que o tamanho do corpus-do-idioma, como esperado para uma lacuna medida em inglês), e **não** como mecanismo estabelecido. A confiabilidade entre juízes, em um painel de quatro fornecedores, é forte (ICC da média do painel = 0,89), e o ground truth está ancorado em fontes oficiais primárias para todos os 25 países; o estudo usa um único juiz primário validado por painel e uma auditoria documental do ground truth, sem camada de padrão-ouro humano. Protocolo, prompts e código de análise serão liberados na publicação.

---

## 1. Introdução

Os grandes modelos de linguagem (LLMs) passaram de curiosidade de pesquisa a infraestrutura operacional da administração pública em menos de cinco anos: um levantamento da OCDE sobre funções centrais de governo documenta a adoção de IA generativa em formulação de políticas e prestação de serviços públicos, incluindo implantações que ajudam servidores a buscar regulações e redigir resumos técnicos *(OCDE 2024)*. Agências ambientais, secretarias municipais e analistas de política aplicada cada vez mais redigem sínteses técnicas, traduzem normas regulatórias, localizam dados oficiais de monitoramento e caracterizam arcabouços institucionais com esse auxílio. A política de poluição do ar é um domínio em que essa adoção tem implicações diretas para a saúde pública. O material particulado fino (PM₂.₅) é o principal fator de risco ambiental para mortalidade prematura no mundo *(GBD 2019; OMS 2021)*, e o ônus recai desproporcionalmente sobre o Sul Global *(GBD 2019)*. Quando um gestor ambiental público em São Paulo, Lagos ou Jakarta pergunta a um LLM sobre um padrão de qualidade do ar, um prazo de atendimento ou a evidência epidemiológica por trás de uma intervenção, uma resposta imprecisa não é um erro benigno. Ela pode se propagar para um parecer regulatório, uma decisão de compra ou uma resposta de emergência durante um episódio de poluição.

A pergunta deste artigo é se os LLMs servem à política de poluição do ar do Sul Global com a mesma confiabilidade com que servem ao Norte Global, e se a forma como uma consulta é enquadrada altera a resposta. Duas linhas recentes de evidência tornam essa pergunta urgente, não hipotética.

**O viés factual geográfico é real e mensurável.** Moayeri et al. (2024) documentaram taxas de erro factual 1,5× maiores para países da África Subsaariana em relação a países da América do Norte, em 20 modelos e 11 indicadores do Banco Mundial. Manvi et al. (2024) mostraram que avaliações zero-shot de LLMs em tópicos subjetivos correlacionam-se fortemente com o nível de renda (ρ até 0,70). Mirza et al. (2024) verificaram que o GPT-4 privilegia sistematicamente afirmações sobre o Norte Global em tarefas de verificação factual. Esses resultados estabelecem o fenômeno, mas nenhum mira um único domínio aplicado de alto risco com ground truth oficial verificável, e nenhum pergunta se o viés pode ser modulado pelo enquadramento do prompt.

**A assimetria linguística e de corpus é estrutural.** Joshi et al. (2020) mapearam uma hierarquia de seis classes de disponibilidade de recursos linguísticos em PLN, mostrando que os idiomas da maioria dos países do Sul Global ocupam as classes inferiores subatendidas. A sub-representação no corpus de treinamento é a explicação dominante para o viés geográfico a jusante. Essa assimetria não é incidental; reproduz padrões duradouros de infraestrutura digital e epistêmica desigual que a literatura decolonial analisou para sistemas de IA.

Identificamos três lacunas que o trabalho atual deixa em aberto para um domínio como a política de poluição do ar:

- **Lacuna 1: nenhum benchmark mira a política de poluição do ar com ground truth oficial.** As avaliações existentes usam recall numérico do Banco Mundial (WorldBench), avaliações subjetivas (Manvi et al.), checagem jornalística (Global-Liar) ou conhecimento cultural cotidiano (BLEnD). Nenhuma mede as tarefas de recall e síntese que um gestor ambiental de fato delega a um LLM.

- **Lacuna 2: o enquadramento por persona não é examinado como alavanca experimental.** Praticantes rotineiramente prefixam consultas com um papel ("Como secretário municipal de meio ambiente, …") — um padrão de prompt documentado *(White et al. 2023)*. Se adotar a persona de um gestor ambiental público *reduz* a lacuna de acurácia do Sul Global (ao orientar o modelo para respostas conformes à regulação) ou a *amplifica* (ao convidar a fabricação confiante de especificidades regulatórias que o modelo nunca aprendeu) não foi testado em um desenho pré-especificado.

- **Lacuna 3: o mecanismo de representação de corpus é afirmado, não testado para este domínio.** O elo entre representação de corpus e acurácia é assumido, mas raramente medido contra confundidores, e raramente separado em seus dois canais. Distinguimos o **tamanho do corpus-do-idioma** (volume de tokens mC4, tamanho do OSCAR, classe de Joshi) da **amplitude de cobertura-do-país** (cobertura na Wikipédia e Wikidata), e testamos qual prediz a acurácia em política de poluição do ar após ajuste pelo IDH — uma distinção que importa porque a lacuna geográfica é medida em inglês.

**Contribuições deste trabalho.** Apresentamos um benchmark desenhado para essas lacunas, com hipóteses, amostragem e plano de análise pré-especificados antes da coleta, executado em 15 países e depois estendido a 25:

1. **Um conjunto de tarefas de política de poluição do ar com ground truth verificável** — cinco tipos de tarefa mapeados a atividades reais de decisão de um gestor ambiental (T1 recall de padrões; T2 concentrações medidas; T3 síntese de evidência em saúde; T4 instrumentos de política e agências; T5 recomendação aplicada com rubrica).
2. **Prompting por persona como fator experimental pré-especificado** — manipulado intra-sujeito (neutro vs. gestor ambiental público), testando como hipótese coprimária (H6) se a condição persona reduz a lacuna.
3. **Amostragem de países triangulada teoricamente** — estratificada por eixos independentes (Norte/Sul da UNCTAD, taxonomia de Joshi, indicadores de desenvolvimento), depois estendida a 25 para ganhar poder. Mostramos, como subproduto metodológico, que o gradiente de desenvolvimento é subpoderado a n=15 mas significativo a n=25.
4. **Teste mecanístico separando os dois canais de corpus** — o proxy de tamanho-do-idioma pré-registrado é nulo; um proxy de cobertura-do-país é uma pista sugestiva mas confundida com desenvolvimento, que reportamos como exploratória.

**Enquadramento teórico.** Interpretamos os achados no arcabouço da *colonialidade do conhecimento* e suas articulações de dados e infraestrutura. Os LLMs são resumos estatísticos comprimidos de corpora produzidos sob infraestrutura digital e acesso à publicação desiguais. Os idiomas e regiões que Joshi et al. situam nas classes subatendidas são precisamente aqueles onde a poluição do ar mais mata. Isso posiciona nosso trabalho empírico como teste de um elo num ciclo teorizado de reprodução (assimetria de corpus → assimetria de conhecimento do LLM → assimetria de decisão de política), e a manipulação de persona como teste de se o enquadramento interrompe esse elo.

---

## 2. Trabalhos relacionados

Organizamos o trabalho prévio em quatro fios: a descoberta e medição do viés factual geográfico; extensões multilíngues e culturais; tentativas de alinhamento e mitigação; e uso de LLMs em contextos de decisão de política e saúde.

**Viés factual geográfico.** Manvi et al. (2024) estabeleceram que LLMs de fronteira carregam vieses sistemáticos contra regiões de menores condições socioeconômicas (ρ até 0,70 com renda per capita). Moayeri et al. (2024) introduziram o WorldBench, documentando erro relativo absoluto 1,5× maior para a África Subsaariana vs. América do Norte. Mirza et al. (2024, Global-Liar) estenderam a questão à estabilidade temporal, mostrando que versões mais novas do GPT-4 não melhoram monotonicamente e que o privilégio de afirmações do Norte Global persiste. Esses estudos estabelecem que o fenômeno existe e é mensurável; nenhum isola um domínio aplicado com ground truth oficial verificável, nem trata o enquadramento como fator manipulável.

**Extensões multilíngues e culturais.** Myung et al. (2024, BLEnD) cobriram 16 países e 13 idiomas em conhecimento cultural cotidiano, com o achado de que LLMs se saem melhor em idiomas nativos de culturas de alto recurso — motivando nossa hipótese exploratória de idioma (H2). Benchmarks regionais proliferaram (BRoverbs para provérbios brasileiros, TiEBe para eventos históricos regionais, ALBA e AMALIA para português europeu), documentando falhas concretas mas sem tratar de uso aplicado em política. O trabalho sobre construção de corpus em português ressalta como snapshots do Common Crawl sub-representam conteúdo lusófono — a assimetria que nosso H4 testa.

**Alinhamento e mitigação.** Opuszko et al. (2026) investigaram se modelos de raciocínio reduzem o viés geográfico, achando que o raciocínio ajuda no agregado mas não elimina disparidades. Kerche et al. (2026) propuseram uma tipologia de vieses baseada em lugar. Essas contribuições são conceituais e agregadas; adicionamos um teste empírico pré-especificado e específico de domínio, e introduzimos a persona como alavanca candidata de mitigação.

**LLMs em contextos de decisão de política e saúde.** He et al. (2025) avaliaram recomendações de política de LLMs para sem-teto em quatro cidades, achando "rigidez cega ao contexto". Kozlakidis et al. (2026) argumentam que alucinações de LLMs carregam risco agudo em ambientes regulatórios com capacidade técnica limitada. A política de poluição do ar fica na interseção desse risco com o ônus de mortalidade do GBD, o que torna o recall acurado de padrões e evidência de saúde uma preocupação de saúde pública.

**Persona e condicionamento por papel.** Evidência sistemática é desanimadora: em quatro famílias de LLMs e 2.410 questões factuais, adicionar personas de especialista aos prompts de sistema não melhorou a acurácia sobre um controle sem persona, e em 162 papéis *reduziu* ligeiramente a acurácia em média (Zheng et al., 2024); uma replicação independente também conclui que personas de especialista não melhoram a acurácia factual. Tratamos a persona como fator experimental pré-especificado e testamos tanto a hipótese de Conformidade-à-Norma (persona reduz a lacuna) quanto a de Vácuo-de-Persona (persona a amplifica).

**Posicionamento.** Nosso desenho difere do prévio em quatro formas concretas: (i) um único domínio aplicado de alto risco com ground truth oficial verificável; (ii) persona como fator experimental intra-sujeito pré-especificado; (iii) amostragem de países guiada por teoria em eixos independentes; e (iv) um teste explícito de mecanismo de representação de corpus. Nenhum estudo prévio combina um domínio regulado de saúde pública, uma manipulação de persona e um teste de mecanismo pré-especificado.

---

## 3. Métodos

**Desenho da pesquisa.** Especificamos um experimento-benchmark fatorial multipaís para quantificar viés geográfico e modulado por persona em 14 LLMs em tarefas de política de poluição do ar. O desenho pré-registrado cruza 15 países (estratificados em três eixos), 14 LLMs em cinco *tiers* de acesso, um domínio, 5 tipos de tarefa e 2 condições de persona, com 2 replicações estocásticas por célula; uma extensão *post-registration* amplia a amostra para 25 países. O conjunto de estímulos cruza as cinco tarefas e duas personas de cada país em inglês, mais uma renderização no idioma nativo para os nove países com idioma-alvo.

**Seleção de países.** Países selecionados por amostragem teórica triangulada em três classificações independentes: classificação Norte/Sul da UNCTAD (operacionalizando a colonialidade), a taxonomia de seis classes de Joshi et al. (recurso linguístico), e grupos de renda do Banco Mundial. A amostra pré-registrada de 15 países — Brasil, México, Argentina, Peru; Nigéria, África do Sul, Quênia, Egito; Índia, Indonésia, Bangladesh, Filipinas; e EUA, Alemanha, Japão (referência do Norte) — cobre quatro regiões, cinco classes de Joshi e quatro grupos de renda.

**Expansão amostral confirmatória (post-registration).** Após a análise pré-registrada de 15 países, e *transparentemente reportada aqui como extensão post-registration, não parte do protocolo travado*, a amostra foi ampliada para **25 países** para aumentar o poder estatístico dos testes de gradiente (H1) e mecanismo (H4) e multiplicar os pares de idioma para H2. Dez países foram adicionados sob procedimentos idênticos. Seis são referências do **Norte Global** escolhidas puramente para ampliar o extremo de alto recurso do gradiente — Reino Unido, Canadá, Austrália, Coreia do Sul, França e Itália. Quatro são países de **par de idioma nativo** que adicionam contrastes em espanhol (Colômbia, Chile) e português (Portugal, Angola); destes, Portugal também é Norte Global, enquanto Colômbia, Chile e Angola são Sul Global. Por *tier*, a extensão adiciona sete países do Norte Global (as seis referências mais Portugal), elevando a célula do Norte de três para dez, e três do Sul Global. A Angola, como a Nigéria e a Argentina, **não** tem padrão nacional de PM₂.₅, fornecendo casos adicionais "sem padrão" em que um modelo fiel deve recusar-se a declarar um limiar inexistente em vez de fabricá-lo.

**Covariáveis de país.** **IDH** (PNUD, Relatório de Desenvolvimento Humano 2023–24, dados de 2022) e **PIB per capita** indexam a posição de desenvolvimento e entram como covariáveis de ajuste. As exposições de representação de corpus são organizadas em dois canais: **medidas de corpus-do-idioma** (tokens mC4 por idioma [Xue et al. 2021, Tabela 6]; tamanho deduplicado do OSCAR-2301 [Abadji et al. 2022]; classe de Joshi) — candidatas ao mecanismo da penalidade de idioma nativo (H2); e **medidas de corpus-do-país** (tamanho em bytes do artigo da Wikipédia em inglês; número de edições linguísticas da Wikipédia com artigo sobre o país [sitelinks da Wikidata]; número de declarações da Wikidata) — candidatas ao mecanismo da lacuna geográfica (H1/H4). Como a lacuna geográfica é medida **em inglês**, uma diferença Norte/Sul residual não pode ser efeito de corpus-do-idioma; assim, o H4 isola o canal de representação-do-país para H1 e o canal de corpus-do-idioma para H2.

**Seleção de modelos.** Catorze LLMs em cinco *tiers* de acesso, abrangendo ~duas ordens de magnitude em contagem de parâmetros e quatro geografias de dados de treino. Tier C inclui um modelo aberto ajustado para português brasileiro (Cabra-Mistral 7B v3) para o teste de modelo regional (H3) contra um modelo aberto treinado globalmente, pareado em escala.

**Taxonomia de domínio e tarefas.** Cinco tipos de tarefa: T1 padrão técnico; T2 dado factual local; T3 síntese de evidência em saúde; T4 instrumentos de política; T5 recomendação aplicada. T1, T2 e T4 admitem ground truth verificável e carregam o sinal de acurácia primário; T3 e T5 são pontuados por rubrica.

**Manipulação de persona.** Fator intra-prompt com dois níveis: **neutro** (pedido de informação simples) e **public_manager_env** (um quadro fixo de papel identificando o solicitante como gestor ambiental municipal/regional), mantendo a pergunta substantiva idêntica. Base da hipótese H6.

**Ground truth e o registro de ground truth.** O ground truth das tarefas verificáveis (T1, T2, T4) veio de fontes oficiais de registro. Construímos um registro por país que, para cada par (país, tarefa), registra a classe de fonte oficial, a URL resolvível, o valor-ouro ou chave de rubrica, a data de referência e uma flag de validação. As entradas são versionadas por data de acesso, URL e hash SHA-256.

**Medidas.** A pontuação usou um protocolo LLM-como-juiz com um único juiz primário e um painel de confiabilidade multifornecedor. Toda resposta do conjunto confirmatório foi pontuada pelo **juiz primário** (GPT-5-mini). Para quantificar a sensibilidade ao juiz, uma **amostra fixa estratificada** foi repontuada por um painel diverso. O painel operativo compreende quatro juízes de quatro fornecedores — GPT-5-mini (OpenAI), Claude Sonnet 4.6 (Anthropic), Gemini 2.5 Pro (Google) e DeepSeek-V3 (DeepSeek); um quinto juiz (Llama 3.3 70B, Meta) corrobora no subconjunto que cobriu, e um sexto candidato (Command R+, Cohere) foi tentado mas excluído quando sua cota de provedor esgotou. A confiabilidade é reportada de três formas: α de Krippendorff, ICC(2,1) de juiz único e — a quantidade operativa — a confiabilidade da **média do painel**, ICC(2,k). Este estudo **não** incluiu camada de padrão-ouro humano; o ground truth foi ancorado em fontes oficiais primárias por auditoria documental, e a ausência de pontuação humana independente é declarada como limitação.

**Estratégia analítica.** Os três testes confirmatórios primários são pré-especificados como família única (F1) e corrigidos por Bonferroni-Holm. H1 (gradiente geográfico): ρ de Spearman entre acurácia média do país e o eixo Joshi/IDH, unilateral, com limiar ρ≥0,55, mais Mann-Kendall. H4 (mecanismo de corpus): ρ de Spearman parcial relacionando representação de corpus à acurácia após ajuste por IDH. H6 (efeito persona): diferença-em-diferenças no nível de país com teste de permutação (5.000 permutações).

---

## 4. Resultados

**Amostra e julgamento.** O corpus analisado compreende 9.251 respostas pontuadas no composto [0,1], das quais 7.580 são respostas em inglês nos 25 países. O juiz primário é o GPT-5-mini; três juízes adicionais de fornecedores diversos repontuaram uma amostra fixa estratificada (confiabilidade da média do painel ICC(2,4)=0,89).

### Acurácia por modelo

Sistemas de fronteira (GPT-5, GPT-5-mini, DeepSeek-V3) lideram; modelos abertos pequenos ficam atrás. O resultado relativo a H3 é inequívoco: o modelo regional em português brasileiro **Cabra-Mistral 7B é o mais fraco de todos** (0,320 vs 0,543 dos demais; Mann-Whitney p≈0, δ=−0,51), contradizendo o enquadramento otimista de que um modelo regional compra acurácia de domínio.

| Modelo | N | Média |
|---|---:|---:|
| GPT-5 | 780 | 0,647 |
| GPT-5-mini | 777 | 0,626 |
| DeepSeek-V3 | 500 | 0,625 |
| Gemini 2.5 Flash | 490 | 0,604 |
| Claude Haiku 4.5 | 490 | 0,597 |
| Qwen3 32B | 498 | 0,546 |
| Command R+ | 500 | 0,509 |
| Llama 3.3 70B | 474 | 0,506 |
| GPT-OSS 120B | 298 | 0,485 |
| Phi-4 14B | 500 | 0,485 |
| Qwen3 14B | 500 | 0,474 |
| Llama 4 Scout | 500 | 0,473 |
| Llama 3.1 8B | 777 | 0,424 |
| Cabra-Mistral 7B | 496 | 0,320 |

### Acurácia por tarefa: o piso de recall factual

As duas tarefas mais difíceis são **T1 (recall de padrão técnico, 0,367)** e **T2 (dado medido local, 0,368)** — exatamente as que exigem recuperar um valor vinculante específico. As tarefas de recall factual (T1, T2; média 0,367) ficam muito abaixo das de síntese e recomendação (T3–T5, 0,638); a diferença é grande e inequívoca (Mann-Whitney p≈0, δ=−0,64). É o achado mais robusto do estudo: o piso recai precisamente sobre os valores vinculantes em que um gestor mais precisa confiar.

| Tarefa | N | Média |
|---|---:|---:|
| T5 (recomendação aplicada) | 1.508 | 0,773 |
| T4 (instrumentos de política) | 1.494 | 0,574 |
| T3 (síntese de evidência em saúde) | 1.519 | 0,567 |
| T2 (dado factual local) | 1.530 | 0,368 |
| T1 (padrão técnico) | 1.529 | 0,367 |

### H1 — uma lacuna de tier e (em n=25) um gradiente de desenvolvimento

A **lacuna de tier** se mantém em ambas as amostras: os dez países do Norte Global têm média 0,567 contra 0,505 dos quinze do Sul Global, uma lacuna de **+6,2 pp** cujo IC bootstrap 95% [+3,7, +8,6] pp **exclui o zero** (15 países: +6,7 pp, [+2,8, +10,2]). O **gradiente monotônico** se comporta de forma diferente entre as amostras, e é aqui que a amostra estendida muda o quadro. No n=15 pré-registrado, o gradiente era indetectável (ρ=+0,14, p=0,31; Mann-Kendall p=0,69). Na amostra estendida de n=25, torna-se significativo: ρ(acurácia, IDH)=**+0,51** (p=0,004, unilateral), com tendência de Mann-Kendall significativa (S=102, Z=+2,36, p=0,018). O gradiente é real mas estava **subpoderado a n=15**; as sete referências de alto IDH adicionadas aumentam a densidade de observações de alto desenvolvimento o suficiente para revelá-lo — sem alargar a própria faixa de IDH.

Duas qualificações honestas delimitam o resultado. Primeiro, ρ=0,51 **fica logo abaixo do nosso limiar de tamanho de efeito pré-registrado de ρ≥0,55**: significativo, mas abaixo da magnitude que pré-comprometemos chamar de gradiente forte. Segundo, o gradiente é em **desenvolvimento** (IDH), **não** em recurso linguístico (Joshi ρ=−0,06). A ordenação dos países retém grande heterogeneidade ortogonal aos eixos — a Índia (0,631, Sul Global) ainda lidera todos e a Alemanha (0,535) é o país do Norte de menor escore. Sob Bonferroni-Holm na família primária {H1-gradiente, H4, H6}, H1-por-IDH é o único teste que rejeita seu nulo a n=25 (p=0,004 vs limiar 0,0167).

| País | Tier | Média | | País | Tier | Média |
|---|---|---:|---|---|---|---:|
| Índia | GS | 0,631 | | Alemanha | GN | 0,535 |
| Coreia do Sul | GN | 0,601 | | Chile | GS | 0,528 |
| Japão | GN | 0,588 | | África do Sul | GS | 0,522 |
| Itália | GN | 0,584 | | Angola | GS | 0,506 |
| Estados Unidos | GN | 0,581 | | Bangladesh | GS | 0,503 |
| França | GN | 0,564 | | Filipinas | GS | 0,499 |
| Canadá | GN | 0,562 | | México | GS | 0,496 |
| Austrália | GN | 0,559 | | Peru | GS | 0,496 |
| Reino Unido | GN | 0,554 | | Quênia | GS | 0,488 |
| Portugal | GN | 0,550 | | Nigéria | GS | 0,465 |
| Indonésia | GS | 0,540 | | Egito | GS | 0,465 |
| Colômbia | GS | 0,539 | | Argentina | GS | 0,450 |
| | | | | Brasil | GS | 0,449 |

### H4 — representação de corpus: cobertura do país, não tamanho do idioma

O proxy pré-registrado (contagem de artigos/edição da Wikipédia) é **nulo** em n=15 e n=25 (ρ=+0,08; parcial controlando IDH +0,04, p=0,87): **H4 como pré-registrado não é sustentado**. Explorando *post hoc*: como a lacuna é medida **em inglês**, uma diferença residual não pode refletir quanto texto existe no idioma do país. Entre três proxies de cobertura-do-país, o número de edições da Wikipédia com artigo sobre o país (sitelinks da Wikidata) correlaciona-se com a acurácia no nível de ordem zero (ρ=+0,54, p=0,005, sobrevivendo à correção de Benjamini-Hochberg entre os três proxies, p ajustado=0,016; declarações da Wikidata ρ=+0,31 e bytes do artigo ρ=+0,20 são não-significativos). **Entretanto**, essa associação **atenua para não-significância após ajuste por IDH** (parcial ρ=+0,32, p=0,13), não atendendo ao padrão de correlação parcial que o teste de mecanismo exige. Reportamos, portanto, a amplitude de cobertura-do-país como sinal **sugestivo e exploratório** — consistente com uma lacuna que aparece mesmo quando todo país é consultado em inglês, e uma pista mais promissora que o tamanho do corpus-do-idioma — mas **não** como mecanismo estabelecido: gradiente de desenvolvimento e cobertura-do-país estão emaranhados, e os dados presentes não os separam.

Para a penalidade de idioma nativo (H2), o canal relevante é o tamanho do corpus-do-idioma, com direção como predita (descritivo, com apenas três idiomas): a penalidade por idioma cai monotonicamente com o volume de tokens mC4 e o tamanho do OSCAR (Spearman = −1,00 entre os três) — o hindi, menor corpus (mC4 24B tokens), tem a maior penalidade, e o espanhol (433B) a menor.

### H6 — a persona não estreita a lacuna geográfica

O quadro de gestor ambiental público deixa a lacuna Norte/Sul essencialmente inalterada: +6,4 pp no quadro neutro vs +6,0 pp no quadro de gestor, uma DiD de **+0,4 pp**, muito abaixo do limiar de 5 pp; teste de permutação no nível de país p=0,26. **H6 não é sustentado** em nenhuma amostra (DiD de 15 países +1,0 pp, p=0,14). Isso responde negativamente à pergunta aplicada central — o enquadramento do prompt não é uma correção para o viés geográfico.

### H5 — aberto vs. fechado-acessível

Agrupando por tipo de acesso, modelos fechados-acessíveis têm média 0,623 (n=2.537) contra 0,481 dos de peso aberto (n=5.043), vantagem fechada de +14,1 pp. Vai contra o enquadramento otimista de H5; o braço aberto inclui modelos maiores (Llama 3.3 70B, DeepSeek-V3), então a lacuna não é atribuível apenas à escala. H5 é interpretado descritivamente.

### H2 — prompts no idioma nativo reduzem a acurácia

Nas células (modelo, prompt) pareadas, o prompt no idioma nativo **reduz** a acurácia composta média em 2,1 pp (Wilcoxon p=2×10⁻³, n=762 células). Como essas células são agrupadas dentro de modelos e prompts, confirmamos o efeito no nível de **país**, onde a unidade é independente: agregando a um delta inglês-menos-nativo por país, todos os nove países de par mostram penalidade (9/9 negativos, média −2,4 pp, Wilcoxon p=0,008) — não é artefato de tratar células agrupadas como independentes. O efeito é modulado pelo nível de recurso do idioma: penalidade do espanhol pequena e não-significativa (−1,0 pp, p=0,15), do português agora significativa com os pares Portugal/Angola (−2,3 pp, p=0,033), e do hindi grande (−7,8 pp, p=0,013).

| Idioma nativo (classe Joshi) | Países | Δ (pp) | N pares |
|---|---|---:|---:|
| Espanhol (5) | MEX, ARG, PER, COL, CHL | −1,0 | 412 |
| Português (4) | BRA, PRT, AGO | −2,3 | 284 |
| Hindi (4) | IND | −7,8 | 66 |
| **Geral** | | **−2,1** | 762 |

### Proveniência do ground truth

O alvo de padrão técnico (T1) para todos os 25 países foi ancorado em fontes oficiais primárias por verificação documental. A maioria tem valor lido da regulação oficial (ex.: o padrão anual de PM₂.₅ do Brasil de 17 µg/m³, lido literalmente do Anexo I da Resolução CONAMA 506/2024 no Diário Oficial da União; os 25 µg/m³ da Colômbia, lidos da Tabela 1 da Resolución 2254/2017). Três países **não** têm padrão nacional de PM₂.₅, confirmado do texto oficial — a NESREA da Nigéria fixa só PM10, a Argentina não tem valor federal vinculante, e a Angola não tem legislação nacional de qualidade do ar. Essa proveniência é mais reproduzível que validação por especialista: qualquer leitor pode reverificar cada valor na fonte oficial.

### Confiabilidade entre juízes

Uma amostra fixa estratificada de 131 respostas foi repontuada por um painel de fornecedores diversos: GPT-5-mini (OpenAI), Claude Sonnet 4.6 (Anthropic), Gemini 2.5 Pro (Google) e DeepSeek-V3 (DeepSeek). α de Krippendorff = 0,667; ICC(2,1) de juiz único = 0,672; e — quantidade operativa — a confiabilidade da **média do painel**, ICC(2,4) = **0,891**, alta pela relação de Spearman-Brown mesmo com juízes individuais concordando apenas moderadamente. A concordância par-a-par é mais forte entre GPT-5-mini, Claude e DeepSeek (Pearson 0,82–0,86) e menor para o Gemini, sistematicamente mais brando (0,61–0,63); como todos os efeitos são contrastes entre grupos, esse desvio de brandura cancela. Um quinto juiz (Llama 3.3 70B, Meta) corroborou no subconjunto coberto (Pearson 0,51–0,60; ICC(2,5) de cinco juízes = 0,86), mas, sendo um juiz 70B mais ruidoso, *baixou* ligeiramente o α do painel — confirmando empiricamente que quatro juízes fortes são preferíveis a cinco com um mais fraco. Um sexto candidato (Command R+) foi excluído quando sua cota de provedor esgotou.

### Robustez do gradiente de desenvolvimento

Testamos duas ameaças diretamente. **Extensão de faixa.** A preocupação é que adicionar dez países — sete do Norte — fabrique o gradiente esticando o preditor IDH. Não fabrica: os dez caem **dentro** da faixa de IDH já abrangida pelos quinze originais ([0,548, 0,950], da Nigéria à Alemanha), então a extensão aumenta a **densidade**, não a faixa, e a estimativa de Spearman é idêntica no conjunto restrito à faixa (ρ=0,512, p=0,009). **Observações influentes.** A reestimação *leave-one-country-out* dá uma faixa do gradiente IDH de ρ∈[+0,48, +0,66] entre todas as 25 remoções, então nenhum país único o dirige; notavelmente, remover a Índia — o país do Sul Global de maior escore e maior contraexemplo ao gradiente — *eleva* a correlação para ρ=0,66. A Índia, portanto, não sustenta o gradiente, mas o atenua; o mesmo exercício deixa estáveis a lacuna de tier ([+5,8, +7,1] pp) e a correlação exploratória de sitelinks ([+0,50, +0,63]). Lemos a Índia como consistente com — não contrária a — a conta de cobertura-do-país: está entre os países mais documentados em fontes enciclopédicas e multilíngues, exatamente a condição sob a qual o sinal de cobertura prediz maior acurácia.

### Síntese

**Sustentado, com tamanhos de efeito:** lacuna de tier Norte/Sul (+6,2 pp, IC [+3,7, +8,6], exclui zero) e, a n=25, um gradiente de desenvolvimento significativo (ρ=0,51 com IDH, p=0,004; Mann-Kendall p=0,018; rejeita sob Bonferroni-Holm) que era subpoderado no n=15 pré-registrado; uma penalidade de idioma nativo (geral p=2×10⁻³, hindi −7,8 pp, português agora significativo); um piso de recall técnico/local (T1+T2 vs demais, δ=−0,64); e o modelo regional como o pior (δ=−0,51). **Não sustentado (nulos informativos):** o gradiente **não** é de recurso linguístico (Joshi ρ=−0,06) e fica logo abaixo do limiar de 0,55; o proxy de corpus pré-registrado (tamanho da Wikipédia) **não** é o mecanismo (parcial ρ=0,04), e um proxy de cobertura-do-país (sitelinks ρ=0,54, p=0,005) é sugestivo mas **não** robusto ao ajuste por IDH (parcial p=0,13), deixando o mecanismo exploratório; e a persona **não** estreita a lacuna (permutação p=0,26).

---

## 5. Discussão

Propusemo-nos a medir se os LLMs respondem a questões de política de poluição do ar com a mesma confiabilidade para o Sul e o Norte Global, se o enquadramento altera a resposta, e que mecanismo dirige qualquer lacuna. O benchmark retorna um quadro disciplinado e em parte contraintuitivo. Existe uma desvantagem geográfica que, com poder adequado, resolve-se num gradiente de desenvolvimento genuíno; mas seu mecanismo é representação-do-país, não tamanho de corpus-do-idioma, os danos dominantes são linguísticos e específicos de tarefa, e toda correção intuitiva falha.

**A lacuna geográfica é um gradiente de desenvolvimento — visível só com poder.** No n=15 pré-registrado, a lacuna de tier era real (+6,7 pp) mas o gradiente indetectável. Estendendo a 25 países, o gradiente resolve-se em significância (ρ=0,51, p=0,004) — o único teste da família primária que rejeita seu nulo sob Bonferroni-Holm. Somos deliberadamente transparentes de que isto é uma extensão post-registration e que ρ=0,51 fica logo abaixo do limiar de 0,55: a afirmação honesta é que o gradiente é significativo mas de magnitude moderada, e que estava subpoderado, não ausente, no desenho registrado. É uma lição metodológica para o campo — gradientes de viés geográfico entre poucos países são fáceis de perder a n pequeno, e o nulo de n=15 teria sido a conclusão errada.

**Um mecanismo sugestivo: cobertura-do-país sobre tamanho de corpus-do-idioma.** Nosso teste de mecanismo pré-registrado falha: o proxy de tamanho da Wikipédia é nulo. Explorando além, achamos uma pista mais promissora. O candidato que *de fato* acompanha a acurácia é quão amplamente o corpus representa o país — sitelinks da Wikidata correlacionam a ρ=0,54 (p=0,005, sobrevivendo à correção por multiplicidade). Somos deliberadamente cautelosos: a associação **atenua para não-significância após ajuste por desenvolvimento** (parcial ρ=0,32, p=0,13), então cobertura e IDH estão emaranhados e o desenho presente não estabelece que a cobertura *cause* a lacuna. Oferecemos, portanto, o contraste cobertura-do-país-sobre-tamanho-do-idioma como **refinamento sugestivo e testável** — ilustrado pelo caso da Índia (sua altíssima cobertura enciclopédica multilíngue acompanha seu escore máximo em inglês) e mostrado pela análise leave-one-out como não dirigido por país único — em vez de mecanismo estabelecido.

**Os danos robustos são linguísticos e específicos de tarefa.** Primeiro, o **piso de recall factual**: as tarefas que exigem um valor vinculante (T1, T2) pontuam ~0,37, muito abaixo de síntese e recomendação (0,64; δ=−0,64). O piso recai precisamente sobre os valores vinculantes em que um gestor mais precisa confiar. Segundo, a **penalidade de idioma nativo**: perguntar no idioma local reduz a acurácia (−2,1 pp; −7,8 pp para o hindi), seguindo o tamanho do corpus-do-idioma entre os três idiomas.

**Três remédios intuitivos, todos falhando.** A **persona de gestor local** não estreita a lacuna (p=0,26). O **idioma local** não ajuda e pode prejudicar. O **modelo regional** (Cabra-Mistral 7B) é o *pior* dos 14 (δ=−0,51). Praticantes rotineiramente usam os três como correções; nenhum sobrevive ao contato com os dados. A mensagem honesta para agências ambientais do Sul Global é que nenhuma dessas soluções baratas substitui verificar o valor vinculante na fonte oficial.

**Por que o domínio importa.** O material particulado fino está entre os principais fatores de risco para mortalidade prematura, e o ônus recai sobre o Sul Global; o GBD atribui da ordem de cinquenta mil mortes/ano só no Brasil à exposição a PM₂.₅. O alinhamento é a parte preocupante: as regiões nas classes inferiores da hierarquia de recursos e com cobertura enciclopédica mais rala são onde a poluição do ar mais mata, então o modelo é menos confiável exatamente onde as consequências são maiores.

**Limitações.** (1) **Juiz primário único** — todos os efeitos usam o composto do GPT-5-mini; endereçamos a sobreposição juiz-alvo com painel de quatro fornecedores (ICC(2,4)=0,89), mas não fazemos média de juízes, e a concordância individual é só moderada (α=0,67). (2) **Sem camada de padrão-ouro humano** — o ground truth é uma auditoria documental de passada única. (3) **Expansão post-registration** — o resultado de 25 países é extensão decidida após a análise registrada; reportamo-lo ao lado dos valores de n=15. (4) **Covariáveis grosseiras e três idiomas nativos** — o mecanismo de corpus-do-idioma para H2 repousa em apenas três idiomas e é descritivo. (5) **Domínio único** — todos os efeitos vêm de um domínio aplicado (política de poluição do ar) e uma família de proxies (Wikimedia); confinamos a linguagem mecanística e de "alavanca tratável" a este domínio, não ao viés geográfico de LLMs em geral; replicação cross-domínio é o passo natural.

**Implicações.** Para agências do Sul Global, a orientação operacional é concreta: tratar saídas de LLMs sobre padrões vinculantes e dados medidos como rascunhos a verificar contra a gazeta oficial; não supor que uma consulta no idioma local ou um modelo pequeno ajustado regionalmente melhore a acurácia; e não confiar no enquadramento de papel para fechar a lacuna. Para desenvolvedores de modelos, o resultado de cobertura-do-país aponta uma alavanca tratável distinta do volume bruto de corpus. Para a comunidade de medição, a reversão de n=15 para n=25 é uma cautela de que gradientes de viés geográfico são facilmente subpoderados.

---

## 6. Conclusão

Os LLMs estão virando infraestrutura operacional da política de poluição do ar, domínio em que uma resposta imprecisa sobre um padrão vinculante, uma concentração medida ou uma resposta operacional carrega implicações diretas de saúde pública no Sul Global, onde o ônus de mortalidade por PM₂.₅ é mais pesado. Medimos viés geográfico e modulado por persona nesse domínio com um benchmark de 25 países, 14 modelos e quatro idiomas, pontuado por um juiz validado por painel contra ground truth ancorado em fontes oficiais primárias.

A desvantagem geográfica é real e, dado poder adequado, resolve-se num gradiente de desenvolvimento significativo (ρ=0,51 com IDH a n=25, indetectável a n=15, robusto a leave-one-out mas abaixo do nosso limiar de tamanho de efeito pré-registrado), ao lado de uma lacuna de tier Norte/Sul estável de +6,2 pp. O mecanismo é mais difícil de fixar: o proxy de corpus pré-registrado é nulo, e um proxy de cobertura-do-país correlaciona-se com a acurácia (ρ=0,54) mas não sobrevive ao ajuste por desenvolvimento — então reportamos a representação-do-país, não o tamanho do corpus-do-idioma, como pista **sugestiva** coerente com uma lacuna medida em inglês, não como mecanismo estabelecido. Os danos dominantes são linguísticos (prompts no idioma nativo reduzem a acurácia, pior para o hindi) e específicos de tarefa (um piso de recall factual nítido sobre padrões e dados medidos, δ=−0,64). E os três remédios intuitivos falham: a persona de gestor local não estreita a lacuna (p=0,26), o idioma local não ajuda e pode prejudicar, e o modelo regional em português brasileiro é o mais fraco de todos (δ=−0,51).

A mensagem honesta para agências ambientais do Sul Global é, portanto, concreta e em grande parte cautelar: saídas de LLMs sobre padrões vinculantes e dados medidos devem ser tratadas como rascunhos verificados contra a gazeta oficial, e nenhuma das soluções baratas de prompt ou modelo — enquadramento de papel, idioma local, modelo pequeno ajustado regionalmente — substitui essa verificação. Para desenvolvedores, o resultado de cobertura-do-país identifica uma alavanca tratável distinta do volume bruto de corpus. Lemos o padrão no arcabouço da colonialidade do conhecimento: as regiões subatendidas nos corpora de treino são as mesmas onde a poluição do ar mais mata, e este estudo transforma dois desses elos — um gradiente de desenvolvimento e uma penalidade de idioma — de preocupações plausíveis em efeitos medidos, localizando um terceiro (cobertura-do-país) apenas sugestivamente. Reportamos também uma cautela metodológica: a reversão de n=15 para n=25 mostra que gradientes de viés geográfico são facilmente subpoderados, e sinalizamos a expansão como extensão post-registration cujo gradiente fica logo abaixo do nosso limiar de tamanho de efeito pré-registrado. Protocolo, prompts, registro de ground truth de fontes oficiais, código de análise e dados de resposta anonimizados são liberados abertamente.


---

## Referências

*(Fontes citadas no manuscrito; lista canônica completa em `latex/references.bib`. Citações no texto acima em formato (Autor, ano).)*

- **Abadji et al.** (2022). *Towards a Cleaner Document-Oriented Multilingual Crawled Corpus*. Proceedings of the Thirteenth Language Resources and Evaluation Conference (LREC).
- **Abril-Pla et al.** (2023). *PyMC: A Modern and Comprehensive Probabilistic Programming Framework in Python*. PeerJ Computer Science.
- **Almeida & others** (2025). *TiEBe: Temporal and Regional Event Benchmark for LLMs*. arXiv preprint.
- **Almeida et al.** (2025). *Building High-Quality Datasets for Portuguese LLMs: From Common Crawl Snapshots to Industrial-Grade Corpora*. Journal of the Brazilian Computer Society.
- **Authors** (2025). *BRoverbs: Measuring how much LLMs understand Portuguese proverbs*. Journal of the Brazilian Computer Society.
- **Authors** (2026). *ALBA: A European Portuguese Benchmark for Evaluating Language and Linguistic Dimensions in Generative LLMs*. arXiv preprint arXiv:2603.26516.
- **Bates et al.** (2015). *Fitting Linear Mixed-Effects Models Using lme4*. Journal of Statistical Software.
- **Bender et al.** (2021). *On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?*. Proceedings of the 2021 {ACM} Conference on Fairness, Accountability, and Transparency.
- **Benjamini & Hochberg** (1995). *Controlling the false discovery rate: a practical and powerful approach to multiple testing*. Journal of the Royal Statistical Society: Series B.
- **Collaborators}** (2020). *Global burden of 87 risk factors in 204 countries and territories, 1990--2019: a systematic analysis for the Global Burden of Disease Study 2019*. The Lancet.
- **Couldry & Mejias** (2019). *The costs of connection: How data is colonizing human life and appropriating it for capitalism*.
- **D'Ignazio & Klein** (2020). *Data feminism*.
- **Group}** (2025). *World Bank Country and Lending Groups --- FY26 Classification*. The World Bank.
- **He & others** (2025). *What Would an LLM Do? Evaluating Policymaking Capabilities of Large Language Models*. arXiv preprint arXiv:2509.03827.
- **Igolkina & Meshcheryakov** (2020). *semopy: A Python package for Structural Equation Modeling*. Structural Equation Modeling.
- **Jolly** (2018). *pymer4: Connecting R and Python for linear mixed modeling*. Journal of Open Source Software.
- **Joshi et al.** (2020). *The State and Fate of Linguistic Diversity and Inclusion in the NLP World*. Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics.
- **Kerche et al.** (2026). *The silicon gaze: A typology of biases and inequality in LLMs through the lens of place*. Platforms \& Society.
- **Kozlakidis et al.** (2026). *Through the looking glass: ethical considerations regarding LLM-induced hallucinations to medical questions*. Frontiers in Digital Health.
- **Manvi et al.** (2024). *Large Language Models are Geographically Biased*. Proceedings of the 41st International Conference on Machine Learning ({ICML}).
- **Meincke et al.** (2025). *Prompting Science Report 4 --- Playing Pretend: Expert Personas Don't Improve Factual Accuracy*.
- **Mirza et al.** (2024). *Global-Liar: Factuality of LLMs over Time and Geographic Regions*. arXiv preprint arXiv:2401.17839.
- **Moayeri et al.** (2024). *WorldBench: Quantifying Geographic Disparities in LLM Factual Recall*. Proceedings of the 2024 {ACM} Conference on Fairness, Accountability, and Transparency.
- **Mohamed et al.** (2020). *Decolonial AI: Decolonial theory as sociotechnical foresight in artificial intelligence*. Philosophy \& Technology.
- **Myung & others** (2024). *BLEnD: A Benchmark for LLMs on Everyday Knowledge in Diverse Cultures and Languages*. Advances in Neural Information Processing Systems.
- **Nosek et al.** (2018). *The preregistration revolution*. Proceedings of the National Academy of Sciences.
- **Opuszko & B{\"o}hm** (2026). *New York, New York -- Unraveling Bias in Large Language Models: Investigating Differences Between Standard and Reasoning-Based Language Models*. {AI} Revolution: Research, Ethics and Society.
- **Organization}** (2021). *WHO Global Air Quality Guidelines: Particulate Matter (PM2.5 and PM10), Ozone, Nitrogen Dioxide, Sulfur Dioxide and Carbon Monoxide*. World Health Organization, Geneva.
- **Patton** (2015). *Qualitative research and evaluation methods*.
- **Quijano** (2000). *Coloniality of power, Eurocentrism, and Latin America*. Nepantla: Views from South.
- **Requia et al.** (2024). *Short-term air pollution exposure and mortality in Brazil: Investigating the susceptible population groups*. Environmental Pollution.
- **Rover et al.** (2026). *Geographic Bias in LLMs: Benchmark Dataset and Code*.
- **team}** (2026). *AMALIA Technical Report: A Fully Open Source Large Language Model for European Portuguese*. arXiv:2603.26511.
- **VanderWeele & Ding** (2017). *Sensitivity analysis in observational research: introducing the E-value*. Annals of Internal Medicine.
- **White et al.** (2023). *A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT*. arXiv preprint arXiv:2302.11382.
- **Xue et al.** (2021). *mT5: A Massively Multilingual Pre-trained Text-to-Text Transformer*. Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL-HLT).
- **Zheng et al.** (2024). *When ``A Helpful Assistant'' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models*. Findings of the Association for Computational Linguistics: EMNLP 2024.
- **{OECD}** (2024). *Governing with Artificial Intelligence: The State of Play and Way Forward in Core Government Functions*. OECD Publishing, Paris.
- **{UNCTAD}** (2024). *UNCTAD Statistical Classifications --- June 2024 Update*. {UN} Trade and Development.
