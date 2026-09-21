---
chave: kassner2021mlama
titulo: "Multilingual LAMA: Investigating Knowledge in Multilingual Pretrained Language Models"
localizador: arXiv:2102.00894v1 · EACL 2021 · doi:10.18653/v1/2021.eacl-main.284
read_depth: full-text (PDF arXiv, íntegra incl. apêndices)
data_leitura: 2026-09-21
leitor: Claude (rodada 13, parecer de painel)
---

## O que o manuscrito atribui a esta fonte

Tradução de TREx/GoogleRE para 53 idiomas; mBERT recorda fatos com desempenho
razoável em 21 idiomas e abaixo de 60% do inglês em 32; viés do idioma da
consulta (perguntar em italiano favorece a Itália); sem tendência clara entre
tamanho da Wikipédia do idioma e desempenho.

## Verbatim conferido no texto completo

> "mBERT performs reasonably well for 21 languages, but for 32 languages rel-p1 is less than 0.6" (§4.3)
> "when queried in Italian, it tends to predict Italy as the country of origin" (abstract; §4.4)
> "Scatter plot of p1 TyQ and number of articles in the corresponding Wikipedia. There is no clear trend visible." (Apêndice C, Fig. 6)
> Hindi entre os idiomas de rel-p1 baixo (Fig. 3).

## Veredito

CONFIRMA. A ausência de tendência entre tamanho da Wikipédia e desempenho
(Fig. 6) é o antecedente direto do nulo do proxy de corpus do idioma em H4.
