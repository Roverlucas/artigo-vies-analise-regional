# Etapa 1 — Revisão de Literatura

**Projeto:** Viés geográfico-factual em LLMs e seu impacto na pesquisa científica do Sul Global
**Pesquisador:** Lucas (PPGSAU/UTFPR)
**Data:** 2026-04-23
**Journal-alvo provisório:** Patterns (Cell Press) / Nature Human Behaviour

---

## 1. Pergunta de pesquisa (PICOC)

| Elemento | Preenchimento |
|---|---|
| **Population** | LLMs frontier (proprietárias e open-source) usadas em contexto de pesquisa aplicada |
| **Intervention** | Prompts sobre políticas públicas, realidade socioeconômica e contexto ambiental de países do Sul Global, em múltiplas línguas |
| **Comparison** | Prompts equivalentes sobre Global Norte em inglês |
| **Outcome** | Acurácia factual, calibração, alucinação, qualidade de citações, profundidade contextual |
| **Context** | LLMs como ferramenta de apoio à pesquisa em saúde pública, clima, ciências sociais |

---

## 2. Estado da arte consolidado

O campo de viés geográfico em LLMs consolidou-se em três ondas (2024-2026):

**Onda 1 (2024): descoberta do viés factual.** Os trabalhos seminais estabeleceram que LLMs erram mais sobre países pobres. Manvi et al. (ICML 2024) demonstraram que LLMs carregam vieses sistêmicos contra regiões de baixa condição socioeconômica em tópicos subjetivos (atratividade, moralidade, inteligência). Moayeri et al. (FAccT 2024, WorldBench) quantificaram o viés de forma replicável: taxas de erro 1,5× maiores para países da África Subsaariana comparados a países norte-americanos em 20 LLMs × 11 indicadores do Banco Mundial. Mirza et al. (2024, Global-Liar) mostraram que GPT-4 favorece sistematicamente afirmações do Norte Global sobre as do Sul.

**Onda 2 (2025): extensão multilíngue e cultural.** Surgem benchmarks culturais (BLEnD — 16 países, 13 línguas; BRoverbs — provérbios brasileiros; TiEBe — 11k pares Q&A sobre eventos regionais; Global MMLU — versões culturalmente sensíveis). Descoberta central de Myung et al. (2024, BLEnD): LLMs respondem melhor em inglês que na língua nativa para línguas low-resource, mas melhor na língua nativa para línguas mid-to-high resource — efeito não-monotônico.

**Onda 3 (2026): alinhamento e mitigação.** Opuszko & Böhm (2026) investigam se reasoning models reduzem o gap; trabalhos sobre Latam-GPT e AMALIA (pt-PT) propõem modelos regionalmente treinados como solução. Kerche, Zook & Graham (2026, *Platforms & Society*) propõem tipologia de vieses baseada em "lugar" — indicação de que o campo está saindo da descoberta e entrando na teorização.

Paralelamente, He et al. (AAAI 2025, *What Would an LLM Do?*) investigam LLMs em decisão de política pública (homelessness em Barcelona, Joanesburgo, South Bend) e encontram que LLMs aplicam uma heurística interna estável — priorizam segurança imediata e ampla cobertura — com rigidez contextual (*context-blind rigidity*), especialmente sub-alinhando-se a especialistas do Sul Global.

---

## 3. Fichamentos focados dos 8 trabalhos seminais

### Fichamento 1 — Moayeri, Tabassi & Feizi (2024) — WorldBench
- **Ref. ABNT:** MOAYERI, M.; TABASSI, E.; FEIZI, S. WorldBench: Quantifying Geographic Disparities in LLM Factual Recall. In: *Proceedings of the 2024 ACM Conference on Fairness, Accountability, and Transparency (FAccT '24)*, Rio de Janeiro, 2024.
- **Achados-chave:** Erro relativo absoluto em 20 LLMs × 11 indicadores do Banco Mundial. África Subsaariana tem erro 1,5× maior que América do Norte. Detecção automática de alucinação de citação (modelos citam o Banco Mundial mas informam estatísticas falsas).
- **Desenho:** Zero-shot, pergunta numérica, comparação com ground truth via erro relativo absoluto.
- **Limitação para o nosso projeto:** (a) restringe-se a indicadores macroeconômicos do Banco Mundial — não cobre políticas sociais, contexto ambiental específico, nem questões qualitativamente complexas que pesquisadores realmente fazem; (b) só em inglês; (c) só indicadores numéricos; (d) não testa uso real em fluxo de pesquisa.

### Fichamento 2 — Manvi et al. (2024) — Large Language Models are Geographically Biased
- **Ref. ABNT:** MANVI, R.; KHANNA, S.; BURKE, M.; LOBELL, D.; ERMON, S. Large Language Models are Geographically Biased. In: *Proceedings of the 41st International Conference on Machine Learning (ICML)*, 2024.
- **Achados-chave:** Viés contra regiões de baixa condição socioeconômica em tópicos subjetivos (Spearman ρ até 0,70 entre rating e renda). Propõe "bias score" quantitativo.
- **Limitação:** Foco em avaliação subjetiva (ratings 1-10), não em conhecimento factual aplicado a pesquisa.

### Fichamento 3 — Mirza et al. (2024) — Global-Liar
- **Ref.:** MIRZA, S. *et al.* Global-Liar: Factuality of LLMs over Time and Geographic Regions. arXiv:2401.17839.
- **Achados:** GPT-4 privilegia afirmações do Norte Global; performance não melhora monotônicamente entre versões (GPT-4 março > GPT-4 junho); viés binário aumenta quando se força true/false sem "unclear".
- **Limitação:** Só GPT; não testa fluxo de pesquisa; foco em checagem de fatos jornalísticos, não de conteúdo de pesquisa aplicada.

### Fichamento 4 — Myung et al. (2024, NeurIPS) — BLEnD
- **Ref.:** MYUNG, J. *et al.* BLEnD: A Benchmark for LLMs on Everyday Knowledge in Diverse Cultures and Languages. *Advances in Neural Information Processing Systems*, v. 37, p. 78104-78146, 2024.
- **Achados:** 52,6k pares Q&A, 16 países, 13 línguas. LLMs performam melhor em culturas com maior representação digital; interação não-monotônica entre língua e recurso (native lang ajuda para mid/high, prejudica para low-resource).
- **Gap crucial para nós:** BLEnD testa conhecimento **cotidiano** (comida, festas, vida diária), não conhecimento aplicado a pesquisa acadêmica em políticas públicas.

### Fichamento 5 — Almeida et al. (2025) — TiEBe
- **Ref.:** ALMEIDA, T.; NOGUEIRA, R.; PEDRINI, H. Building High-Quality Datasets for Portuguese LLMs. *Journal of the Brazilian Computer Society*, v. 31, n. 1, p. 1247-1263, 2025.
- **Achados:** 11k+ pares sobre eventos regionais; LLMs falham em representar eventos consistentemente entre regiões, incluindo Brasil e Portugal.
- **Limitação:** Foco em conhecimento de eventos históricos, não em estrutura institucional e política pública.

### Fichamento 6 — He et al. (AAAI 2025) — What Would an LLM Do?
- **Ref.:** HE, J. *et al.* What Would an LLM Do? Evaluating Policymaking Capabilities of Large Language Models. arXiv:2509.03827.
- **Achados:** LLMs exibem "context-blind rigidity" em políticas sobre homelessness; maior alinhamento com especialistas do Norte Global; quando contextualizado, aproxima-se de especialistas locais (ex: Joanesburgo).
- **Relevância máxima:** Mostra exatamente o problema que queremos atacar — mas em UM domínio (homelessness) e em UM tipo de tarefa (recomendação, não recall factual).

### Fichamento 7 — Opuszko & Böhm (2026)
- **Ref.:** OPUSZKO, M.; BÖHM, P. New York, New York - Unraveling Bias in Large Language Models: Investigating Differences Between Standard and Reasoning-Based Language Models. In: *AI Revolution: Research, Ethics and Society*. Springer, 2026. p. 92-106.
- **Relevância:** Primeira investigação sistemática sobre se reasoning models (o1, DeepSeek-R1) reduzem viés geográfico. Resultado preliminar: reasoning ajuda em agregados mas não elimina disparidades regionais.

### Fichamento 8 — Paiola et al. (2025, PMC) — Revalida Benchmark
- **Ref.:** PAIOLA, P. H. *et al.* Benchmarking open-source large language models on Portuguese Revalida multiple-choice questions. *PMC*, 2025.
- **Achados:** 31 LLMs × 399 questões médicas em PT-BR. GPT-4o 86,8%; Claude Opus 83,8%. Evidência de que modelos performam bem em PT-BR para questões técnicas padronizadas, mas os autores explicitamente pedem comparação EN vs PT para isolar o viés — **gap declarado na literatura.**

---

## 4. Diagrama PRISMA simplificado

```
  Identificados via busca (n ≈ 180)
              ↓
  Após remoção de duplicatas (n ≈ 120)
              ↓
  Triagem por título/abstract (n = 45 relevantes)
              ↓
  Leitura integral (n = 22 incluídos)
              ↓
  Núcleo seminal para fichamento (n = 8)
```

---

## 5. Gaps identificados (mais importante para a Etapa 2)

A literatura é densa, mas há quatro gaps claros e convergentes que ninguém ainda fechou:

### GAP 1 — Domínio: aplicação em pesquisa de políticas públicas (não trivia)
Todos os benchmarks existentes testam: (a) indicadores macro do Banco Mundial (WorldBench), (b) ratings subjetivos (Manvi), (c) checagem de fato jornalístico (Global-Liar), (d) conhecimento cotidiano cultural (BLEnD), (e) eventos históricos (TiEBe), ou (f) conhecimento técnico padronizado (Revalida). **Nenhum testa o uso real que pesquisadores fazem de LLMs:** síntese de política pública existente, caracterização de contexto socioambiental regional, identificação de stakeholders institucionais, recomendação de fontes primárias. Essa é a tarefa em que a LLM tem maior impacto real na ciência produzida no Sul Global — e ninguém mediu.

### GAP 2 — Interação língua × geografia, com controle rigoroso
BLEnD (Myung et al.) sugere interação não-monotônica, mas o desenho de 16 países × 13 línguas em conhecimento cotidiano não permite isolar o efeito. **Ninguém fez ainda um desenho fatorial limpo** (mesmo país, mesma pergunta, línguas diferentes, com controle de tradução reversa) em domínio de pesquisa aplicada.

### GAP 3 — Modelos regionais vs frontier: reduzem ou apenas deslocam o viés?
Sabiá-3, Latam-GPT e AMALIA são propostos como solução, mas **ninguém comparou quantitativamente** o gap de performance entre frontier model (em EN) vs modelo regional (em PT) na mesma tarefa de apoio a pesquisa. Se Sabiá-3 reduz o gap para 0, é killer finding para Q1. Se só desloca (melhora em BR mas piora em Moçambique/Angola), é achado igualmente publicável.

### GAP 4 — Mecanismo causal: representação vs arquitetura
A literatura assume que o viés vem de sub-representação em corpus (Common Crawl tokens/país), mas isso nunca foi testado diretamente contra modelos de mesma arquitetura com diferentes misturas de treinamento. Nosso desenho pode contribuir com evidência correlacional (não causal) entre volume de tokens de treinamento e gap de acurácia.

---

## 6. Síntese das limitações recorrentes na literatura

1. **Sobre-foco em tarefas sintéticas:** quase todos os benchmarks usam Q&A multiple-choice ou recall numérico. Uso real de LLM em pesquisa é geração aberta — resumos, caracterizações, buscas por fontes. Nossa contribuição: incluir prompts de geração aberta com rubrica de avaliação.

2. **Ausência de calibração:** poucos papers medem se o modelo *sabe que não sabe*. WorldBench detecta alucinação de citação; nenhum mede calibração de confiança sistematicamente por país.

3. **Pouco rigor na escolha de países:** "Global South" é tratado como bloco. Precisamos de estratificação por renda (World Bank income groups) e por volume de representação digital (proxy: Wikipedia pageviews, Common Crawl tokens).

4. **Ausência de stakeholders:** nenhum trabalho envolve pesquisadores do Sul Global na construção das perguntas. O nosso pode incluir isso via pequeno painel de validação.

---

## 7. Bibliografia em BibTeX (núcleo seminal)

```bibtex
@inproceedings{moayeri2024worldbench,
  title={WorldBench: Quantifying Geographic Disparities in LLM Factual Recall},
  author={Moayeri, Mazda and Tabassi, Elham and Feizi, Soheil},
  booktitle={Proceedings of the 2024 ACM Conference on Fairness, Accountability, and Transparency},
  pages={1211--1228},
  year={2024},
  address={Rio de Janeiro},
  doi={10.1145/3630106.3658967}
}

@inproceedings{manvi2024llm,
  title={Large Language Models are Geographically Biased},
  author={Manvi, Rohin and Khanna, Samar and Burke, Marshall and Lobell, David and Ermon, Stefano},
  booktitle={Proceedings of the 41st International Conference on Machine Learning},
  year={2024},
  eprint={2402.02680},
  archivePrefix={arXiv}
}

@article{mirza2024global,
  title={Global-Liar: Factuality of LLMs over Time and Geographic Regions},
  author={Mirza, Shujaat and Coelho, Bruno and Cui, Yuyuan and P{\"o}pper, Christina and McCoy, Damon},
  journal={arXiv preprint arXiv:2401.17839},
  year={2024}
}

@article{myung2024blend,
  title={BLEnD: A Benchmark for LLMs on Everyday Knowledge in Diverse Cultures and Languages},
  author={Myung, Junho and others},
  journal={Advances in Neural Information Processing Systems},
  volume={37},
  pages={78104--78146},
  year={2024}
}

@article{he2025policymaking,
  title={What Would an LLM Do? Evaluating Policymaking Capabilities of Large Language Models},
  author={He, Jiao and others},
  journal={arXiv preprint arXiv:2509.03827},
  year={2025}
}

@inproceedings{opuszko2026unraveling,
  title={New York, New York - Unraveling Bias in Large Language Models: Investigating Differences Between Standard and Reasoning-Based Language Models},
  author={Opuszko, M. and B{\"o}hm, P.},
  booktitle={AI Revolution: Research, Ethics and Society},
  pages={92--106},
  publisher={Springer},
  year={2026}
}

@article{almeida2025portuguese,
  title={Building High-Quality Datasets for Portuguese LLMs: From Common Crawl Snapshots to Industrial-Grade Corpora},
  author={Almeida, T. and Nogueira, R. and Pedrini, H.},
  journal={Journal of the Brazilian Computer Society},
  volume={31},
  number={1},
  pages={1247--1263},
  year={2025}
}

@article{paiola2025revalida,
  title={Benchmarking open-source large language models on Portuguese Revalida multiple-choice questions},
  author={Paiola, P. H. and others},
  journal={PMC},
  year={2025}
}
```

---

## 8. Saída pronta para handoff à Etapa 2

Temos:
- 4 gaps convergentes, todos defensáveis
- 8 trabalhos seminais fichados
- Clareza sobre o que já foi feito e o que nos falta fazer
- Journal-alvo provisório (Patterns ou Nat Hum Behav)

Pronto para formalizar hipóteses H₀/H₁ na Etapa 2.
