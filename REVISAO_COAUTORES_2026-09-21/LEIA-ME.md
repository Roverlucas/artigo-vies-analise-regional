# Pacote para revisão dos coautores — 21/09/2026

**Artigo:** *Whose Regulation Does the Model Know? Reliability of LLM-Retrieved Regulatory Information for Public Environmental Management in 25 Countries*
**Autores (ordem de assinatura):** Lucas Rover (UTFPR) · Vitor de Melo Dominski (Descomplica) · Anibal Tavares de Azevedo (Unicamp) · Eduardo Tadeu Bacalhau (UFPR) · Yara de Souza Tadano (UTFPR)
**Alvo:** *Government Information Quarterly* (Elsevier)
**Repositório (público):** https://github.com/Roverlucas/artigo-vies-analise-regional (commit `f08ff3d`)

## Arquivos

| arquivo | conteúdo | pp |
|---|---|---|
| `...MANUSCRITO-EN` | manuscrito completo, inglês (idioma de submissão) — formato `elsarticle [review]`, espaçamento duplo | 66 |
| `...SUPLEMENTAR-EN` | material suplementar, inglês | 18 |
| `...MANUSCRITO-PT` | versão de leitura em português | 35 |
| `...SUPLEMENTAR-PT` | suplemento em português | 16 |

A versão em inglês é a autoritativa. As 66 páginas são efeito do espaçamento duplo exigido na submissão (13 delas são referências); a métrica que o GIQ avalia é a contagem de palavras, ~11.800 no corpo.

**Versão de 21/09 à noite (v2):** incorpora a rodada 10 — T1 adjudicado por código, dois juízes de coleta declarados, chave do Reino Unido corrigida (20, não 10), Egito excluído de T1, H4 rebaixado, Métodos reescritos para o estudo entregue e ~60 números propagados. Descarte o pacote enviado mais cedo no mesmo dia, se o recebeu.

## O que o artigo afirma (todos os números saem de `data/processed/freeze_all_effects.json`, reproduzível com `python code/run_all.py --confirmatory`)

- **Achado principal (H2):** perguntar na língua do país **piora** a acurácia em **−5,0 pp** (Wilcoxon p = 5×10⁻¹⁶, n = 839 pares). Hindi −11,4 pp, espanhol −4,5, português −4,2. Resiste a leave-one-out de país e de modelo, trimming, reponderação do composto e separação por instrumento de pontuação.
- **Lacuna Norte/Sul (H1):** +5,0 pp [+1,5, +8,4] (permutação p = 0,021) sob a partição developing/developed da UNCTAD; mesmo tamanho só dentro da onda de extensão e nos 15 pré-especificados. O gradiente com IDH (ρ = 0,36, p = 0,076) fica **abaixo do critério pré-fixado (ρ ≥ 0,55)** e é exploratório.
- **T1 por código:** no padrão nacional, a chance do Sul Global é **0,33** da do Norte [0,27, 0,40]; 0,39 sem os países de chave não padrão; 0,12 sob chave tolerante à escada (o Norte é que tem escadas). Sob os juízes originais era 0,22 — e os dois juízes estavam divididos pela mesma linha dos tiers.
- **Modelo regional (H3):** o pior dos 14 (δ = −0,48); e perde para o Llama 3.1 8B também em português no Brasil (0,258 vs 0,313, n = 20).
- **Persona de gestor local (H6):** não ajuda (+0,5 pp, p = 0,29).
- **Aberto vs. fechado (H5):** +13,0 pp a favor dos fechados.
- **Piso de recuperação factual:** T1+T2 0,435 contra 0,612 em síntese/recomendação (δ = −0,41); T1 sozinha 0,394.
- **H4 (mecanismo):** dentro do país, cobertura×tarefa e IDH×tarefa são colineares (ρ = 0,65); juntas, o IDH fica (β = +0,027) e a cobertura não (β = +0,012, p = 0,063). O texto agora diz que o mecanismo é identificado só até o par cobertura-ou-desenvolvimento.

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
3. Dizer se concorda com a força da claim principal (H2), com o enquadramento exploratório de H1 e com o rebaixamento de H4 (mecanismo identificado só até o par cobertura-ou-desenvolvimento).
4. Sinalizar qualquer outra ferramenta de IA usada, para a declaração exigida pela Elsevier.

Sem a aprovação explícita dos cinco, não submetemos.

## O que falta antes de submeter, e o pedido concreto

Depois de um parecer externo de duas partes e de uma rodada de correções (rodada 10, `ROUNDS.md`), o manuscrito está internamente consistente: todos os gates mecânicos passam e cada número do texto sai de `freeze_all_effects.json`. O que resta é o que máquina não faz.

**1. Validação humana de ~150 respostas — a pendência que decide.** Todo número do artigo passa por código contra registro ou por um painel de LLMs; nenhuma resposta foi conferida por um humano. Um revisor escreve esse "major" de olhos fechados. Proposta: 150 respostas estratificadas por tarefa × idioma × tier, três avaliadores, a rubrica de cinco itens que já existe, κ entre avaliadores. Uma semana. Resolve de uma vez a objeção de leniência do juiz por idioma (a penalidade de H2 é −8,6 pp nas células do painel e −3,8 nas do código), a prova de que o código não pune resposta certa nas chaves de fonte única (T2/T3) e a confirmação independente do extrator de T1. **Pedimos que dois coautores aceitem ser avaliadores.** O pipeline exporta a amostra e a planilha; o esforço é de leitura, não de análise.

**2. Leitura integral do EN por um humano.** Cerca de 60 números foram trocados por script nesta rodada e três claims foram rebaixadas (H4, H3, T1). Script não vê frase torta.

**3. Congelamento formal dos resultados.** O autor correspondente declara o freeze da rodada 10 após a leitura; a partir dele nenhum número muda sem nova rodada registrada.

O que **não** faremos: re-julgar as respostas duplicadas sob outra regra (muda 0,0001 na média e custa API), acrescentar análises ou países. As decisões pendentes estão em `data/review-log/2026-09-21-artigo-vies-analise-regional-round10.yaml`.
