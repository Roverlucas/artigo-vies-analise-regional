# Pacote para revisão dos coautores — 21/09/2026

**Artigo:** *Whose Regulation Does the Model Know? Reliability of LLM-Recalled Regulatory Information for Public Environmental Management in 25 Countries*
**Autores (ordem de assinatura):** Lucas Rover (UTFPR) · Vitor de Melo Dominski (Descomplica) · Anibal Tavares de Azevedo (Unicamp) · Eduardo Tadeu Bacalhau (UFPR) · Yara de Souza Tadano (UTFPR)
**Alvo:** *Government Information Quarterly* (Elsevier)
**Repositório (público):** https://github.com/Roverlucas/artigo-vies-analise-regional (branch `main`, commit da rodada 13 no `ROUNDS.md`)

## Arquivos

| arquivo | conteúdo | pp |
|---|---|---|
| `...MANUSCRITO-EN` | manuscrito completo, inglês (idioma de submissão) — formato `elsarticle [review]`, espaçamento duplo | 72 |
| `...SUPLEMENTAR-EN` | material suplementar, inglês | 21 |
| `...MANUSCRITO-PT` | versão de leitura em português | 38 |
| `...SUPLEMENTAR-PT` | suplemento em português | 18 |

A versão em inglês é a autoritativa. As 66 páginas são efeito do espaçamento duplo exigido na submissão (13 delas são referências); a métrica que o GIQ avalia é a contagem de palavras, ~11.800 no corpo.

**Versão de 21/09 (v5, após parecer de painel com três revisores, decisão "Major Revision", e pedido de prosa sem traços de IA):** a rodada 13 mudou o que o artigo afirma em três pontos. (1) **Inferência no nível do país**: todo teste antes rodado sobre respostas foi refeito com o país ou o modelo como unidade (`cluster_inference.py`). **H4 deixa de ser "identificado até o par" e passa a "não estabelecido"** (SE agrupado por país p = 0,099; 25 déficits por país ρ = −0,37, p = 0,069). A razão de chances de T1 por tarefa fica marginal com o país como unidade (bruta 0,44, IC [0,18, 1,05], p = 0,062); por isso **o desfecho só-código (+14,7 pp) passa a ser o primário da lacuna Norte/Sul** e a decomposição por tarefa é rotulada exploratória. H6 ganha teste de equivalência (DiD dentro de ±2 pp). (2) **Dois erros de Métodos "como executado" corrigidos**: nenhuma seed foi enviada a provedor algum (o suplemento descrevia um campo `seed_status` inexistente) e nenhum filtro de idioma ou truncamento existe no código; ambos estão na tabela de desvios. (3) **Título passa a "LLM-Recalled"** (não há recuperação; todas as respostas vêm da memória paramétrica), abstract cortado a 229 palavras, "ρ = 0,55 excluído" retirado (o IC de Fisher inclui 0 e 0,55), "monotonically" retirado, cinco referências novas lidas na íntegra (X-FACTR, mLAMA, Dahl 2024, Zheng 2023, Panickssery 2024), Cabra verificado contra o próprio modelo-base nos mesmos itens (serving não explica a posição; só nos valores de registro, Cabra, base e Llama ficam a poucas respostas um do outro), e as sete seções reescritas em EN e PT sem travessões, itálicos de ênfase e frases de anúncio. O texto **cresceu** ~1.100 palavras com as análises que os revisores pediram; o corte de 25–30% que o editor sugere é decisão dos autores sobre o que sai.

**Versão de 21/09 (v4, após rodada de validação):** todos os números-manchete do texto, das tabelas e dos dois suplementos passam a ser gerados dos artefatos (303 macros em `latex/numbers.tex`); tabelas por modelo e por tarefa geradas; pipeline ponta a ponta com censo de 3.325 números, zero sem caminho reproduzível. Nenhum achado mudou; mudou a garantia de que o número impresso é o número computado. **v3:** chave de Bangladesh corrigida na fonte (35, Rules 2022), H2 reportado com o país como unidade de inferência, lacuna Norte/Sul também nos desfechos só de código (+14,7 pp), modelo regional descrito como fine-tune comunitário de 7B, Discussão compactada, hash de versão dos registros. **Versão v2:** incorpora a rodada 10 — T1 adjudicado por código, dois juízes de coleta declarados, chave do Reino Unido corrigida (20, não 10), Egito excluído de T1, H4 rebaixado, Métodos reescritos para o estudo entregue e ~60 números propagados. Descarte o pacote enviado mais cedo no mesmo dia, se o recebeu.

## O que o artigo afirma (todos os números saem de `data/processed/freeze_all_effects.json`, reproduzível com `python code/run_all.py --confirmatory`)

- **Achado principal (H2):** perguntar na língua do país **piora** a acurácia em **−5,0 pp** (modelo misto com intercepto por país p = 6×10⁻⁷; 8 de 9 países negativos, t = −4,6, p = 0,002; Wilcoxon sobre as 839 células p = 5×10⁻¹⁶). Hindi −11,4 pp, espanhol −4,5, português −4,2. Resiste a leave-one-out de país e de modelo, trimming, reponderação do composto e separação por instrumento de pontuação.
- **Lacuna Norte/Sul (H1):** desfecho primário = só código (nenhum juiz): o Sul devolve o valor do registro **14,7 pp** menos vezes [5,6, 23,9], permutação por país p = 0,012. Composto: +5,0 pp [+1,6, +8,4] (p = 0,019); mesmo tamanho na onda de extensão, nos 15 pré-especificados e com a UE como um cluster (+5,5, p = 0,029). O gradiente com IDH (ρ = 0,36, p = 0,076; IC de Fisher [−0,04, +0,66]) **nem se estabelece nem exclui o critério ρ ≥ 0,55**.
- **T1 por código (exploratório por tarefa):** no padrão nacional, a razão de chances bruta Sul/Norte é **0,44 com IC bootstrap por país [0,18, 1,05]** (permutação p = 0,062); o GLMM condicional dá 0,32 [0,27, 0,39], intervalo irrealista para 24 países. Sob os juízes originais era 0,22, e os dois juízes estavam divididos pela mesma linha dos tiers. A lacuna é concentrada nas tarefas de fato nacional e ausente em T5, mas só o agregado só-código está estabelecido com o país como unidade.
- **Modelo regional (H3):** o pior dos 14 (δ = −0,48; abaixo da média dos demais em 25/25 países); perde para o Llama 3.1 8B em português (20 de 30 prompts, −5,9 pp, p = 0,002). Verificação de serviço: template do Ollama = chat_template publicado; reservido nos 30 prompts PT, Cabra 47%, base Mistral-7B-Instruct-v0.3 50%, Llama 43% nos valores de registro — a margem do composto vem das tarefas julgadas.
- **Persona de gestor local (H6):** não ajuda (+0,5 pp, p = 0,29) e é equivalente a nenhuma persona em até ±2 pp (IC90 por país [−0,4, +1,6]); efeito principal −0,6 pp.
- **Aberto vs. fechado (H5):** +12,8 pp a favor dos fechados.
- **Piso de recuperação factual:** T1+T2 0,435 contra 0,612 em síntese/recomendação (δ = −0,41); T1 sozinha 0,394.
- **H4 (mecanismo): não estabelecido.** A interação cobertura×tarefa tem p = 6×10⁻¹⁰ no nível da resposta, mas p = 0,099 com erro-padrão agrupado por país; os 25 déficits por país correlacionam com cobertura a ρ = −0,37 (p = 0,069) e a −0,16 dado o IDH. A direção é a prevista; nada alcança significância com o país como unidade. Coloquei a lição na Discussão: p no nível da resposta superestima o que 25 países mostram.

## A virada metodológica que define o artigo

Os gabaritos de T2/T3 eram placeholders e a comparação "o valor está na faixa?" era feita por LLM. Reconstruir as chaves a partir dos registros oficiais (WHO AAQD, WHO GHO, UNEP GAAPL) e mover a comparação para código **mudou as conclusões** (gradiente ρ 0,51 → 0,41; penalidade nativa −2,1 → −4,75 pp). Por isso H2 é o achado principal e H1 é exploratório. O manuscrito relata isso explicitamente.

## Transparência

- **Não há pré-registro depositado.** O plano foi fixado antes da coleta (rastro versionado em `preregistration/`), mas nunca depositado. O texto se reporta como exploratório e não reivindica pré-registro.
- **Validação humana do gabarito:** não há camada human-gold; o gabarito é fonte oficial primária + painel de 3 fornecedores de juízes-LLM. Declarado como limitação.
- **Uso de IA:** juízes-LLM produzem os escores; tradução dos prompts por LLM; Claude Code e Codex CLI usados no código e na revisão. Tudo declarado.
- **Referências:** 44 citadas, 36 lidas na íntegra, 7 conferidas em abstract, 1 livro sem localizador.

## O que pedimos a cada coautor

1. Ler o manuscrito em inglês (ou a versão PT) e anotar diretamente no PDF ou por e-mail.
2. Confirmar afiliação, ORCID e **e-mail institucional** (Dominski e Azevedo: ainda não temos).
3. Dizer se concorda com a força da claim principal (H2), com o desfecho só-código como primário da lacuna Norte/Sul, com **H4 relatado como não estabelecido**, com o título "LLM-Recalled" e com manter "as três correções falham" no abstract sendo o modelo regional um fine-tune comunitário de 7B (a alternativa é coletar um Sabiá-3).
4. Sinalizar qualquer outra ferramenta de IA usada, para a declaração exigida pela Elsevier.

Sem a aprovação explícita dos cinco, não submetemos.

## O que falta antes de submeter, e o pedido concreto

Depois de um parecer externo de duas partes e de uma rodada de correções (rodada 10, `ROUNDS.md`), o manuscrito está internamente consistente: todos os gates mecânicos passam e cada número do texto sai de `freeze_all_effects.json`. O que resta é o que máquina não faz.

**1. Validação humana de ~150 respostas — a pendência que decide.** Todo número do artigo passa por código contra registro ou por um painel de LLMs; nenhuma resposta foi conferida por um humano. Um revisor escreve esse "major" de olhos fechados. Proposta: 150 respostas estratificadas por tarefa × idioma × tier, três avaliadores, a rubrica de cinco itens que já existe, κ entre avaliadores. Uma semana. Resolve de uma vez a objeção de leniência do juiz por idioma (a penalidade de H2 é −8,6 pp nas células do painel e −3,8 nas do código), a prova de que o código não pune resposta certa nas chaves de fonte única (T2/T3) e a confirmação independente do extrator de T1. **Pedimos que dois coautores aceitem ser avaliadores.** O pipeline exporta a amostra e a planilha; o esforço é de leitura, não de análise.

**2. Leitura integral do EN por um humano.** Cerca de 60 números foram trocados por script nesta rodada e três claims foram rebaixadas (H4, H3, T1). Script não vê frase torta.

**3. Congelamento formal dos resultados.** O autor correspondente declara o freeze da rodada 10 após a leitura; a partir dele nenhum número muda sem nova rodada registrada.

O que **não** faremos: re-julgar as respostas duplicadas sob outra regra (muda 0,0001 na média e custa API), acrescentar análises ou países. As decisões pendentes estão em `data/review-log/2026-09-21-artigo-vies-analise-regional-round10.yaml`.
