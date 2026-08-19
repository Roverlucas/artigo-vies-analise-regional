# T4 — por que esta tarefa não recebe gabarito factual

**Status:** decisão de desenho pendente de ratificação do autor.
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
