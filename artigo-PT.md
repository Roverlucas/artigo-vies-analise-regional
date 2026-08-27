# Versão em português — arquivo movido

Este arquivo era a versão de leitura em português do manuscrito. Ele foi
**substituído** e não deve mais ser citado: a versão em português vive agora em
LaTeX, junto com a inglesa, e é gerada do mesmo congelamento de resultados.

| o que você quer | onde está |
|---|---|
| manuscrito em português | [`latex/main-PT.tex`](latex/main-PT.tex) → `latex/main-PT.pdf` |
| seções em português | [`latex/sections-PT/`](latex/sections-PT/) |
| suplemento em português | [`latex/supplement-PT.tex`](latex/supplement-PT.tex) |
| números canônicos | `data/processed/freeze_all_effects.json`, seção `corrigido` |

## Por que ele saiu

O conteúdo anterior era de junho de 2026 e ficou para trás em duas frentes.

Primeiro, os números. Ele reportava a pontuação **anterior** à reconstrução do
gabarito de T2/T3 e à passagem da adjudicação para código, e anterior ao colapso
das células com pontuação repetida. Os efeitos mudaram: a lacuna Norte/Sul, o
gradiente de IDH e a penalidade de idioma nativo têm hoje outros valores, todos
em `freeze_all_effects.json`.

Segundo, o estatuto do plano. O texto anterior falava em resultado
"pré-registrado" e em "extensão pós-registro". O plano de análise foi fixado antes
da coleta, mas **nunca foi depositado publicamente**, e por isso o manuscrito não
reivindica pré-registro e se reporta como exploratório do início ao fim.

O histórico completo continua no git (`git log -- artigo-PT.md`).
