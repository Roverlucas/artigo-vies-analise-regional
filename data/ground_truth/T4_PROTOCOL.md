# T4 — por que esta tarefa não recebe gabarito factual

**Status:** DECIDIDO pelo autor em 2026-08-19 — saída (a) com fabricação
como desfecho separado. Conjunto de referência construído. Ver adendo no fim.
**Data:** 2026-08-19 · **Contexto:** rodada 1 de auditoria.

## O problema

O prompt de T4 é, para cada país:

> List the principal national programs or legal instruments for monitoring and
> controlling ambient air pollution in {país}, with the executing agency for each.

O gabarito atual, para os 25 países, é um placeholder:

> `[NEEDS_HUMAN: enumerate the specific national programs/instruments and executing agencies with official sources.]`

E mesmo assim **1.825 respostas foram pontuadas** contra ele, com
`rubric_primary: factual_accuracy_and_completeness`.

## Por que T1, T2 e T3 admitiram gabarito e T4 não

| tarefa | pergunta | resposta certa |
|---|---|---|
| T1 | qual é o limite anual vigente | **um número**, publicado em ato normativo |
| T2 | qual foi a concentração medida | **um número**, publicado em base oficial |
| T3 | quantas mortes atribuíveis | **um número com intervalo**, publicado pela OMS |
| **T4** | **quais são os instrumentos** | **um conjunto**, e não há autoridade que o feche |

Não existe fonte que declare, para 25 países, qual é o conjunto **completo e
correto** de instrumentos nacionais de política de poluição do ar. Um país tem
resolução de padrões, programa de monitoramento, programa de controle veicular,
programa de fontes fixas, plano de emergência, mais os equivalentes subnacionais.
Qual subconjunto conta como "principal" é julgamento, não fato.

Um gabarito construído por nós seria a **nossa** lista, e um revisor de política
ambiental poderia contestá-la item a item, com razão. Pior: como o esforço de
montagem varia por país (a legislação brasileira é mais acessível para nós que a
indonésia), a completude do gabarito ficaria correlacionada com o tier do país,
que é exatamente a variável sob teste. Isso é o confundimento que o registry
existe para eliminar.

## As três saídas

**(a) Rubrica de cobertura contra conjunto de referência.** Monta-se, por país,
um conjunto de instrumentos *verificados em fonte oficial*, sem alegar completude,
e pontua-se por quantos itens da resposta são verificáveis e quantos são
fabricados. Mede alucinação e verificabilidade, não acerto. Exige curadoria de 25
conjuntos e alegação explícita de não completude.

**(b) Desfecho de fabricação apenas.** Não se pergunta se a resposta está
completa, e sim se cada instrumento citado **existe**. Isso é verificável, não
exige conjunto de referência fechado, e mede o que de fato interessa a um gestor:
o sistema inventa programa de política pública? Barato e defensável.

**(c) Retirar T4 do resultado primário** e reportá-la como descritiva.

## Recomendação do squad

**(b)**, com (c) como acompanhamento. A taxa de fabricação é o desfecho de
segurança mais relevante para o público do artigo, é verificável sem construir
uma autoridade que não existe, e não sofre do confundimento de esforço por país.

Sob qualquer das três, a afirmação atual de `03_methods.tex:170`, de que "T1, T2
and T4 admit verifiable ground truth and carry the primary accuracy signal",
precisa ser corrigida: T4 não admite ground truth verificável no sentido em que
T1, T2 e T3 admitem.

## O que fica bloqueado até a decisão

- A repontuação de T4 (1.825 respostas).
- O peso de T4 no composto primário.
- A frase de Methods citada acima.
- A tabela `tab:conf-task`, cuja linha de T4 hoje reporta média contra placeholder.

**Fronteira humana (R7):** a escolha entre (a), (b) e (c) muda o que o artigo
afirma medir, e é do autor, não do squad.


---

# Adendo · 2026-08-19 · decisão tomada e o que foi construído

## A objeção original estava factualmente errada

Este protocolo afirmava que "não existe autoridade que feche o conjunto para 25
países". **Existe.** O UNEP publicou em 2021 o *Regulating Air Quality: The First
Global Assessment of Air Pollution Legislation*, avaliando a legislação de 194
Estados mais a União Europeia com metodologia única, e o Apêndice 1 lista, por
país, os instrumentos legais com fonte primária publicada.

Isso derruba a objeção central, que era o confundimento esforço-por-país: o
esforço de pesquisa foi do UNEP e foi o mesmo para todos.

## A decisão do autor, e por que ela é melhor que a recomendação do squad

O squad recomendou (b), medir apenas fabricação. O autor apontou o modo de falha
que isso cria: sob (b), **a resposta ideal é não dizer nada verificável**. Um
modelo que responde "os instrumentos são administrados pela autoridade ambiental
nacional sob a legislação vigente" tem fabricação zero e nota máxima. Isso
anti-correlaciona com o que o artigo mede, porque premia a evasão justamente onde
o modelo sabe menos, e apagaria o gradiente em T4.

Decidido: **(a) cobertura como desfecho principal, fabricação reportada à parte.**

| desfecho | pergunta | papel |
|---|---|---|
| Cobertura | quantos itens do conjunto a resposta recupera | entra no composto, carrega o gradiente |
| Fabricação | dos instrumentos citados, quantos não existem | desfecho separado, risco operacional |

## O que foi construído

`code/analysis/build_t4_registry.py` → `data/ground_truth/t4_reference_set.jsonl`

| | |
|---|---|
| Países com conjunto de referência | **24 / 25** |
| Extração limpa | **15** |
| Precisa de conferência humana | **9** (AUS, BRA, IDN, IND, KEN, KOR, NGA, UK, USA) |
| Ausente da fonte | **1** (Angola) |

## As três limitações que precisam ir para o manuscrito

**1. O conjunto não alega completude.** É o subconjunto de instrumentos
verificados pelo UNEP com fonte primária publicada. O escopo do Apêndice 1 são
instrumentos que contêm padrões de qualidade do ar, que é mais estreito do que T4
pergunta. Por isso cobertura, e não completude.

**2. Data de corte de 15 de dezembro de 2020.** O conjunto do Brasil traz a
CONAMA 491/2018, que foi parcialmente revogada pela 506/2024. Uma resposta que
cite a 506/2024 está **mais correta que o conjunto de referência**, e a pontuação
precisa aceitá-la. Isso vale para qualquer país que tenha legislado depois de 2020.

**3. Nove países saíram com extração suja.** O layout de quatro colunas do PDF faz
o `pdftotext` costurar colunas erradas: o Brasil perdeu o número da resolução, a
Coreia teve o nome do país injetado dentro do instrumento, o Reino Unido capturou
cabeçalho de tabela. O campo `extraction_quality` marca cada caso e
`extraction_flags` diz o que foi detectado. **Esses nove não devem ser usados como
gabarito antes de conferência contra o PDF**, que é rápido porque são poucos itens
por país.

## Angola, de novo

Angola não consta do Apêndice 1, não tem cidade na base de qualidade do ar da OMS
e não tem padrão nacional no registry de T1. Ausente em três fontes
internacionais independentes. Isso não é lacuna da nossa coleta, é um fato sobre
a infraestrutura de informação ambiental do país, e é material para a Discussão.
