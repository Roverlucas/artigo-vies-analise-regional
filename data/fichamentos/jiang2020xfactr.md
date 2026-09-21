---
chave: jiang2020xfactr
titulo: "X-FACTR: Multilingual Factual Knowledge Retrieval from Pretrained Language Models"
localizador: arXiv:2010.06189v3 · EMNLP 2020, pp. 5943–5959 · doi:10.18653/v1/2020.emnlp-main.479
read_depth: full-text (PDF arXiv, texto principal §1–8; apêndices lidos em parte)
data_leitura: 2026-09-21
leitor: Claude (rodada 13, parecer de painel)
---

## O que o manuscrito atribui a esta fonte

Sondagem factual multilíngue (cloze) em 23 idiomas: o desempenho é maior em
idiomas de alto recurso, mas baixo em geral (<15% em inglês/espanhol, <5% em
marathi/iorubá); o conhecimento recordado é em grande parte específico do
idioma da consulta.

## Verbatim conferido no texto completo

> "achieving less than 15% on high-resource languages (e.g., English and Spanish) and less than 5% for some low-resource languages (e.g., Marathi and Yoruba)" (§5.1)
> "half of the correctly predicted facts were correct in a single language, indicating little overlap across languages" (§6)
> "facts expressed in English are better learned in the pre-trained model due to training data abundance" (§6.2)
> Exemplo Tencent QQ: correto em chinês, errado em inglês (§6).

## Veredito

CONFIRMA. Modelos são mBERT/XLM/XLM-R e monolíngues (2020), não LLMs
generativos; citar como antecedente da sondagem multilíngue, não como
resultado sobre os modelos deste estudo.
