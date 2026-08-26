---
chave: abadji2022oscar
titulo: Towards a Cleaner Document-Oriented Multilingual Crawled Corpus (LREC 2022)
url: https://aclanthology.org/2022.lrec-1.463.pdf · doi:10.63317/579or68a4ybs
read_depth: full-text (PDF)
data_leitura: 2026-08-26
leitor: Claude (verificacao de referencias)
---

## O que o manuscrito atribui a esta fonte

tamanho do corpus OSCAR por idioma (usamos es 429,9 GB, pt 105,0 GB, hi 32,6 GB)

## Verbatim conferido na fonte

> O paper descreve o OSCAR 22.01 e traz na tabela: Spanish 381.9 GB, Portuguese 170.3 GB, Hindi 23.3 GB. Os valores que usamos (429,9 / 105,0 / 32,6) vem do dataset card do OSCAR-2301, versao ORIGINAL.

## Veredito

DOIS PROBLEMAS ENCONTRADOS E CORRIGIDOS.

(1) ATRIBUICAO. O texto citava Abadji et al. 2022 para tamanhos que nao estao
naquele paper: ele descreve o OSCAR 22.01, e nossos numeros sao do OSCAR-2301.
Um revisor que fosse a fonte procurar 429,9 GB encontraria 381,9. O texto agora
credita o corpus ao paper e os valores por idioma ao dataset card, dizendo que
os totais diferem entre as versoes.

(2) ROTULO ERRADO. Chamavamos os valores de 'deduplicated'. O dataset card lista
esses totais para a versao ORIGINAL; a deduplicada nao e tabulada ali. Corrigido
no texto (EN e PT) e em corpus_measures.py, que era a origem do erro.

Nenhum resultado muda: a medida entra como proxy ordinal e a ordem es > pt > hi se
mantem em qualquer das versoes.
