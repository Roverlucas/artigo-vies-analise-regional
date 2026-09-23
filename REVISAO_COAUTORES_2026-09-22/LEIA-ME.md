# Pacote para revisão dos coautores — 22/09/2026 (v6)

**Artigo:** *Whose Regulation Does the Model Know? Reliability of LLM-Recalled Regulatory Information for Public Environmental Management in 25 Countries*
**Autores (ordem de assinatura):** Lucas Rover (UTFPR) · Vitor de Melo Dominski (Descomplica) · Anibal Tavares de Azevedo (Unicamp) · Eduardo Tadeu Bacalhau (UFPR) · Yara de Souza Tadano (UTFPR)
**Alvo:** *Government Information Quarterly* (Elsevier)
**Repositório (público):** https://github.com/Roverlucas/artigo-vies-analise-regional

## Arquivos

| arquivo | conteúdo | pp |
|---|---|---|
| `...MANUSCRITO-EN` | manuscrito completo, inglês (idioma de submissão), `elsarticle [review]`, espaçamento duplo | 79 |
| `...SUPLEMENTAR-EN` | material suplementar, inglês | 21 |
| `...MANUSCRITO-PT` | versão de leitura em português | 41 |
| `...SUPLEMENTAR-PT` | suplemento em português | 18 |
| `CEGO_*` | versão anonimizada, gerada por script, para submissão double-blind | — |
| `validacao-humana/` | as três planilhas de avaliação e o LEIA-ME de quem for pontuar | — |

## O que mudou nesta versão (rodada 14)

Um segundo parecer de banca leu a revisão anterior e disse, em resumo, que a
inferência estava resolvida e a apresentação não: o corpo já tinha rebaixado
três achados, e o abstract, a Discussão e a Conclusão ainda os vendiam. Corrigi
essa divergência. **Nenhum número novo foi coletado; o que mudou foi o que o
texto afirma.**

1. **H3 muda de afirmação.** Não é mais "o modelo regional é o pior dos catorze"
   — isso é uma frase sobre 7B contra modelos de fronteira, não um achado. O
   achado pré-especificado, e o que interessa a um órgão, é que **o ajuste em
   português não melhora nada em relação ao próprio modelo-base**: nos valores de
   registro, Cabra 47% contra 50% da base Mistral-7B-Instruct-v0.3.
2. **O mecanismo passou a ter um resultado.** No nível do país, quem prevê o
   déficit nas perguntas sobre o próprio país é o **desenvolvimento**
   (β = +0,036, p = 0,027), não a cobertura enciclopédica (p = 0,099). Isso
   estava na tabela do suplemento e não no corpo. Não é o gradiente de H1: o IDH
   não prevê quão bem o modelo responde sobre um país, prevê **quanto pior** ele
   responde às perguntas sobre aquele país. As duas exposições correlacionam a
   0,65 e não se separam nesta amostra.
3. **A concentração da lacuna por tarefa virou "padrão de estimativas
   pontuais".** Todo intervalo por tarefa com o país como unidade inclui 1. O que
   se sustenta é o agregado só-código: **14,7 pp** [5,6; 23,9].
4. **A penalidade de idioma não é silêncio.** O parecer supôs que um terço viria
   de respostas vazias. Medi: excluindo toda célula vazia, a penalidade vai de
   −4,95 para **−5,15 pp**. Fica maior, não menor.
5. **Saiu do texto:** a razão de chances agrupada (ignorava o aninhamento), a
   contagem de votos ("dois de três testes superam o zero"), a razão de T5 (é
   teto: 99,6% contra 99,7%) e a afirmação sem fonte de que agências do Sul não
   teriam capacidade para RAG.
6. **Entraram:** três figuras (a primeira mostra exatamente por que o nível de
   inferência importa), os componentes de variância que explicam o fator cinco
   entre os dois intervalos, H6 recomputada nos 15 pré-especificados, e o
   detalhamento do que cada provedor de fato recebeu (depois do erro do seed, reli
   o cliente inteiro em vez de confiar na descrição).
7. **A versão cega passou a compilar.** O `build_blind.py` existia desde agosto e
   **nunca havia gerado um PDF**: o script deixava uma chave órfã ao remover o
   bloco de autores. Consertado; os dois PDFs cegos estão no pacote e passam pela
   varredura de 11 termos identificadores.

## Auditoria independente em DeepSeek-V3 (rodada 15)

Rodei as 11 lentes do squad em **outro fornecedor**, porque quem gera não fecha.
Notas de 5,0 a 7,0 (mediana 6,5) e 21 achados críticos. Conferi cada um na fonte
antes de mexer no texto; **12 procedem, 4 são falsos e 5 são de apresentação.**

**O mais grave a auditoria encontrou por acidente, e era nosso.** A declaração de
IA dizia que Gemini 2.5 Pro, DeepSeek-V3 e **GPT-5.2-pro** atuaram como revisores
do manuscrito. Fui conferir: `squad_audit_openai.json` tem **zero pareceres
válidos e oito HTTP 429 "no credits"**, e já estava assim no commit de agosto. O
GPT-5.2-pro nunca produziu uma linha sobre este artigo. Era método declarado sem
execução — exatamente o que não pode existir num manuscrito. Corrigido em EN e
PT: a declaração agora nomeia só quem rodou, diz que a execução na OpenAI foi
tentada e não aconteceu, aponta para o artefato da falha, e reenquadra as
passagens como garantia de qualidade interna, não revisão por pares.

**O que mais procede e já está aplicado:**

- **"Todo intervalo por tarefa inclui 1"** era falso para T5, que está no teto e
  não tem intervalo. Agora: "todo intervalo **estimável**".
- **O "um terço cita a escada" escondia o que importa.** Medi por grupo: **56%
  das respostas erradas do Norte** citam um degrau oficial contra **27% das do
  Sul**. Quando o modelo erra um padrão do Norte, confunde a etapa; quando erra um
  do Sul, o valor nem está na escada. Isso afia o argumento, não o enfraquece.
- **A manchete de H2 era o teste errado.** Era o Wilcoxon por célula, que o
  próprio texto admitia ser anticonservador. Agora a manchete é o modelo misto com
  intercepto por país, e é esse número que abstract, discussão e conclusão citam.
- **Havia um descarte silencioso** no pareamento de H2: uma célula nativa sem par
  em inglês sumia sem aviso. São 1 em 840 e não muda nada — mas "não muda nada" só
  se sabe contando, então o número passa a ser publicado.
- **A lacuna estava exagerada.** Dizíamos que ninguém havia feito benchmark de
  informação regulatória com gabarito oficial, citando Dahl 2024, que fez
  exatamente isso. A lacuna real é a versão transnacional, e agora é essa que o
  texto reivindica.
- Mais: tabela nova com os regimes de pontuação (quem decide o quê, por tarefa),
  duas frases em português claro explicando a diferença entre as duas estimativas
  da Tabela 5, e a declaração de dados dizendo o que de fato é publicado.

**O que rejeitei, com a medição que rejeita.** O auditor disse que a bibliografia
era o achado mais danoso possível: referências de 2026 e arXiv `2603.xxxxx` que
"não podem existir". Conferi ao vivo: das 8 entradas de 2026, **6 resolvem no
Crossref** (três delas na própria GIQ) e **2 no DataCite/arXiv**, com títulos
idênticos aos do `.bib`. O modelo tem corte de treino anterior a 2026 e trata o
presente como futuro. Também rejeitei a acusação de que o teste decisivo de H2
não existiria (existe, roda e está no artigo) e a de que haveria quatro números
diferentes para o mesmo efeito (os quatro imprimem −5,0).

A auditoria na OpenAI **não rodou**: a conta está sem crédito. O caminho está
implementado e o preflight barra em três segundos sem gastar nada.

## O que o artigo afirma agora, em uma página

- **Achado principal (H2):** perguntar no idioma do país **piora** a resposta em
  −5,0 pp (modelo misto com intercepto por país, p = 6×10⁻⁷; negativo em 8 de 9
  países) e reduz em 9,4 pp a chance de o modelo devolver qualquer número
  conferível. Vale para os três idiomas, para todos os modelos, não depende de
  juiz nem da qualidade da tradução (censo de retrotradução nos 90 prompts) e
  **não é silêncio**.
- **Piso de recordação:** 0,39 na tarefa que exige o valor legal em vigor contra
  0,61 em síntese e recomendação; e um terço dos erros cita um degrau da escada
  oficial do país — sabem a norma, erram o estágio vigente.
- **Lacuna Norte/Sul:** 14,7 pp menos acertos nos desfechos decididos por código,
  com o país como unidade. No composto, +5,0 pp, marginal sob o modelo misto
  (p = 0,086) e no subconjunto de prompts balanceados (p = 0,32).
- **Persona de gestor público:** equivalente a nenhuma persona em até ±2 pp.
- **Não se sustentam:** o gradiente por IDH (IC de Fisher [−0,04; +0,66] inclui
  zero e o limiar de 0,55) e o mecanismo de cobertura de corpus.
- **Contribuição, em uma frase:** um protocolo para checar se o que um LLM diz
  sobre uma norma bate com o registro oficial, decidido por código onde a
  resposta é um número, mais a demonstração de que as três correções baratas que
  uma agência tentaria não funcionam — e a lição metodológica de que, quando um
  efeito de viés geográfico é frágil, se audita primeiro o gabarito e o nível de
  inferência, não o tamanho da amostra, porque foi trocar esses dois que mudou as
  conclusões sem trocar um dado sequer.

## O pedido concreto a vocês

1. **Dois de vocês para pontuar 150 respostas.** É o bloqueador que os três
   revisores marcaram como P0, e é a única coisa aqui que máquina não faz. A pasta
   `validacao-humana/` tem tudo pronto: três planilhas com o prompt, a resposta e
   o gabarito oficial, **sem** o nome do modelo, sem o grupo de países e sem a nota
   da máquina; o LEIA-ME tem as quatro regras que evitam divergência boba entre
   avaliadores. É leitura, não análise.
2. **Ler o manuscrito em inglês** (ou o PT) e anotar no PDF ou por e-mail.
3. **Confirmar afiliação, ORCID e e-mail institucional** (Dominski e Azevedo:
   ainda não temos).
4. **Dizer se concorda** com: H2 como achado principal; o desfecho só-código como
   primário da lacuna; H4 relatado como interação do desenvolvimento não separável
   da cobertura; H3 reenquadrado como "não supera a própria base"; e o título
   "LLM-Recalled".
5. **Sinalizar qualquer outra ferramenta de IA usada**, para a declaração da
   Elsevier.

Sem a aprovação explícita dos cinco, não submetemos.

## O que ainda falta, e de quem depende

| pendência | de quem | custo |
|---|---|---|
| Pontuar as 150 respostas | dois coautores | ~1 semana de leitura |
| Publicar snapshot anonimizado (Zenodo/OSF) antes de submeter | Lucas | 1 hora |
| Corte de 25–30% do texto (o editor pediu; o texto cresceu com as reanálises) | Lucas decide o que sai | — |
| Repontuar os 4 subcomponentes de T1 pelo painel | decisão | custa API |
| Braço com busca web (3 stacks, T1/T2) | decisão | custa API |
| Análise documental: agências dos 25 países mencionam IA generativa? | decisão | coleta nova |
