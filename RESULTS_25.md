# Resultados confirmatórios — arquivo substituído

Este arquivo trazia a tabela de resultados de 15 contra 25 países, gerada em junho
de 2026 a partir de `formal_tests.py` e companhia. Ele **não é mais a fonte** e foi
esvaziado para não contradizer o manuscrito num repositório público.

| o que você quer | onde está |
|---|---|
| **números canônicos** | `data/processed/freeze_all_effects.json`, seção `corrigido` |
| como eles são produzidos | [`code/analysis/freeze_all_effects.py`](code/analysis/freeze_all_effects.py) |
| a família primária nos 15 pré-especificados | [`code/analysis/pre15_corrigido.py`](code/analysis/pre15_corrigido.py) |
| tabelas prontas | [`latex/supplement.tex`](latex/supplement.tex) |
| o gate que impede divergência | [`code/analysis/consistency_gate.py`](code/analysis/consistency_gate.py) |

## Por que ele saiu

Duas razões, e nenhuma é de estilo.

**Os números eram de antes da correção.** `formal_tests.py` roda sobre a pontuação
original; `freeze_all_effects.py` roda sobre a corrigida, depois de o gabarito de
T2/T3 ser reconstruído, de a adjudicação de valores publicados passar para código
e de as células com pontuação repetida serem colapsadas pela média. Manter as duas
tabelas lado a lado no repositório é a divergência que o `consistency_gate.py`
existe para barrar — ele só varria `.tex`, e este arquivo passou pelo ponto cego.

**O estatuto do plano estava errado.** O arquivo descrevia a amostra de 25 países
como "extensão pós-registro" e o resultado de 15 como "pré-registrado". O plano foi
fixado antes da coleta, mas **nunca foi depositado publicamente**: o manuscrito não
reivindica pré-registro e se reporta como exploratório.

O conteúdo anterior continua no git (`git log -- RESULTS_25.md`).
