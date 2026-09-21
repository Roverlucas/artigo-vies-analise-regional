# Auditoria do extrator de T1 — respostas em idioma nativo classificadas como NO_VALUE

Data: 2026-09-21. Censo, não amostra: todas as 10 respostas em idioma nativo (es/pt/hi)
que `score_numeric.extract_t1` classificou como sem valor extraível, lidas uma a uma.
Auditor: o agente de análise que escreveu o extrator (R7: quem gera não fecha —
confirmação humana pendente, ver ROUNDS.md).

| # | idioma | país | modelo | o que a resposta contém | veredito do extrator correto? |
|---|---|---|---|---|---|
| 1 | es | MEX | cabra_mistral_7b | prosa truncada sem número | sim |
| 2 | es | MEX | cabra_mistral_7b | "15 mg/m³" — unidade errada (mg, não µg); valor não é o padrão | sim (não há valor em µg/m³) |
| 3 | es | MEX | cabra_mistral_7b | idem | sim |
| 4 | hi | IND | cabra_mistral_7b | repete o prompt, sem número | sim |
| 5 | hi | IND | cabra_mistral_7b | texto sem sentido (sânscrito), sem número | sim |
| 6 | hi | IND | cabra_mistral_7b | repete o prompt | sim |
| 7 | hi | IND | cabra_mistral_7b | repete o prompt | sim |
| 8 | es | COL | cabra_mistral_7b | cita lei e norma técnica, sem valor | sim |
| 9 | pt | PRT | cabra_mistral_7b | cita o regulamento, sem valor | sim |
| 10 | pt | PRT | gpt5_mini | pede permissão para verificar antes de responder | sim |

Resultado: 10/10 corretos. Nenhum caso de vírgula decimal, numeral devanágari ou
unidade por extenso foi perdido — os casos desse tipo que existem na base foram
extraídos (testes unitários em `score_numeric.py`: 13/13). O único caso ambíguo
(#2–3, "15 mg/m³") é uma resposta que afirma um valor na unidade errada; tratá-la
como "sem valor comparável" é a leitura conservadora e vale igualmente para inglês.

Os 9 casos com prompt em espanhol/hindi/português vêm de um único modelo
(cabra_mistral_7b, 9/10), cuja saída em idioma nativo é frequentemente degenerada;
isso é parte do achado de H2/H3, não um artefato do extrator.
