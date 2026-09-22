# Validação humana — 150 respostas, 3 avaliadores

Cada planilha tem as mesmas 150 respostas em ordem diferente. Você não
vê qual modelo respondeu, nem a que grupo de países o item pertence, nem a nota
que a máquina deu. Isso é deliberado: a comparação só vale se a sua nota for
independente da dela.

## Como pontuar

Cinco colunas, cada uma de 0 a 1 (use 0, 0,25, 0,5, 0,75 ou 1):

| coluna | pergunta que você responde |
|---|---|
| `factual_accuracy` | O que a resposta afirma bate com o gabarito oficial da linha? |
| `contextual_completeness` | A resposta traz o que a pergunta pediu (valor, fonte, período, órgão)? |
| `citation_quality` | As fontes citadas existem e sustentam o que foi dito? |
| `calibration` | A confiança expressa corresponde ao que a resposta de fato sabe? |
| `absence_of_hallucination` | A resposta evita inventar normas, números ou instituições? |

Regras que evitam divergência boba entre avaliadores:

1. Se o gabarito diz que **não existe** padrão nacional, a resposta correta é
   dizer isso. Afirmar um valor é `factual_accuracy = 0` e
   `absence_of_hallucination = 0`.
2. Um valor de outro ano da série, dentro da faixa aceita, **conta como certo**.
3. Não penalize o idioma, o estilo nem o tamanho. Só o conteúdo.
4. Em dúvida entre dois valores, escreva o motivo em `observacao` e siga.

## O que fazemos com isso

Comparamos sua nota com a da máquina item a item e publicamos a concordância
(κ e ICC) no material suplementar, inclusive se ela for baixa. A amostra é
estratificada por grupo de países, idioma e tarefa; a composição está abaixo,
sem dizer qual item é qual.

| grupo × tarefa | itens |
|---|---|
| GN T1 | 11 |
| GN T2 | 11 |
| GN T3 | 11 |
| GN T4 | 10 |
| GN T5 | 10 |
| GS T1 | 19 |
| GS T2 | 20 |
| GS T3 | 20 |
| GS T4 | 19 |
| GS T5 | 19 |

Chave (modelo, país, nota da máquina): `data/processed/human_validation_key_PRIVATE.jsonl`,
aberta só depois que as três planilhas voltarem.
