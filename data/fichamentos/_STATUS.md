# Estado da verificação de referências

Gate SA-QG-010 (HOUSE-RULES R1): citar exige fichamento com `read_depth: full-text`.

## Situação

O manuscrito cita **44 referências**. Até 2026-08-26 **nenhuma** tinha fichamento —
a verificação que existia era mecânica (chave citada ↔ entrada no `.bib`), o que
confirma sintaxe e não diz nada sobre o artigo dizer o que lhe atribuímos.

**10 verificadas** nesta rodada, priorizadas por risco: as 4 documentações de
fornecedor (sustentam a interpretação de H6) e as 6 que atribuem número a uma
fonte (o que um revisor confere primeiro).

**34 pendentes.** Enquanto pendentes, são citações não verificadas — não
"provavelmente certas".

## O que a leitura mudou no manuscrito

1. **google2026promptingstrategies** — a doc admite explicitamente o papel na
   system instruction *ou* "at the very beginning of the user prompt". Nossa
   limitação declarada era mais severa do que a fonte sustenta: dizíamos que os
   guias põem o papel no system prompt e que testamos outro canal. Três dos quatro
   põem; o Google admite os dois. Texto refinado em Métodos e Limitações, EN e PT.

2. **anthropic2026systemprompts** — a URL do `.bib` redirecionava (301) e o título
   registrado era o de uma *seção*, não da página. Entrada corrigida com o verbatim
   conferido.

3. **zheng2024helpful** — caso que justifica a exigência de texto completo. O
   abstract diz apenas "does not improve performance"; nossa frase diz que as
   personas reduzem levemente a acurácia. Pelo abstract eu teria enfraquecido uma
   frase correta. O texto completo diz "no or small negative effects" e "might
   actually hurt their performance", que sustenta a redação atual.

## Verificadas

| chave | profundidade | veredito |
|---|---|---|
| anthropic2026systemprompts | full-text | confirma; promete "behavior and tone", nunca acurácia |
| openai2026promptengineering | full-text | confirma; escopo é propósito e estilo |
| google2026promptingstrategies | full-text | confirma com refinamento (ver acima) |
| xai2026chatguide | full-text | confirma o exemplo; não declara efeito |
| moayeri2024worldbench | full-text (PDF) | confirma 1.5×, 20 LLMs, 11 indicadores |
| zheng2024helpful | full-text (PDF) | confirma 4 famílias, 2.410, 162 e efeito negativo pequeno |
| xue2021mt5 | full-text (PDF, Tabela 6) | confirma hindi 24B, es 433B, pt 146B |
| who2026gho_air41 | fonte primária (API) | confirma 88.548 [69.477–108.431] e a ordem das causas |
| manvi2024llm | abstract | confirma ρ até 0.70 |
| mirza2024global | abstract | confirma as duas afirmações |

As duas últimas estão em `abstract`, não `full-text`: a alegação que lhes
atribuímos está no próprio abstract, mas pelo gate isso é triagem. Ficam marcadas
como parcialmente verificadas.
