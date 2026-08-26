# Validação de localizadores — 2026-08-26

Passo anterior à leitura: a referência aponta para algo que existe e é o que dizemos?

## DOIs (CrossRef) — 28 verificados

**26 resolvem com título e ano coerentes.** Duas divergências:

- `oecd2024governing` — CrossRef dá **2025**, o `.bib` registrava 2024. **Corrigido.**
- `xue2021mt5` — sinalizado pelo meu comparador, mas é falso positivo: o título
  resolvido é "mT5: A Massively Multilingual Pre-trained Text-to-Text Transformer",
  idêntico. O comparador falhou porque "mT5" tem menos de 4 letras.

## arXiv (DataCite) — 4 verificados

Deram 404 no CrossRef porque o arXiv deposita no DataCite, não no CrossRef. Todos
existem e conferem na API do arXiv:

| chave | arXiv | título retornado |
|---|---|---|
| almeida2025tiebe | 2501.07482 | TiEBe: Tracking Language Model Recall of Notable Worldwide Events Through Time |
| alba2026 | 2603.26516 | ALBA: A European Portuguese Benchmark… |
| amalia2026 | 2603.26511 | AMALIA Technical Report: A Fully Open Source LLM for European… |
| lecoz2025policymaking | 2509.03827 | What Would an LLM Do? Evaluating Large Language Models for Policymaking… |

## Sem localizador no `.bib` (9)

`abadji2022oscar`, `almeida2025portuguese`, `kozlakidis2026medical`, `myung2024blend`,
`opuszko2026unraveling`, `patton2015qualitative`, `quijano2000coloniality`, `semopy`,
`pymc` (este tem DOI e foi validado).

Não têm DOI nem URL registrados, então a verificação de existência depende de busca
manual. Ficam na fila de leitura com prioridade, porque referência sem localizador é
a mais fácil de estar errada e a mais difícil de o revisor conferir.

## Removida

`zenodo2026dataset` era citada no texto e descrevia um depósito **"to be deposited on
publication"** — ou seja, uma citação a algo que não existe. Eu a havia inserido para
silenciar um aviso de "entrada não citada", o que foi um erro: resolvi um alerta
mecânico criando um problema de integridade. Citação removida de `main.tex` e
`main-PT.tex`.
