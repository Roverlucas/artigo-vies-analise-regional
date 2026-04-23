# Framework de Estratificação Amostral — Seleção de Países

**Projeto:** Viés geográfico-factual em LLMs
**Propósito deste documento:** Justificar teoricamente a seleção dos 15 países do benchmark, de forma defensável em peer review Q1.
**Data:** 2026-04-23

---

## 1. Problema de amostragem enfrentado

A literatura em viés geográfico de LLMs (Moayeri et al., 2024; Manvi et al., 2024; Mirza et al., 2024) costuma usar:

- **Amostragem total** (todos os ~195 países) — inviável para benchmark com geração aberta e painel de validação humana.
- **Amostragem por região UNCTAD** (Sul Global vs Norte) — insuficiente porque trata o Sul como bloco homogêneo.
- **Amostragem por conveniência** (países de autores) — baixa validade externa.

Nosso problema: selecionar 15 países (viável) que sejam **representativos das dimensões que a teoria prevê importantes** para viés de LLM. Isso é amostragem por **estratificação teórica** (*theoretical sampling*; Patton, 2015) — cada unidade escolhida por motivo explícito ligado a variável-alvo.

---

## 2. Três eixos teóricos de estratificação (triangulação metodológica)

Combinamos **três classificações internacionais estabelecidas** que capturam dimensões conceitualmente distintas do fenômeno estudado. Cada eixo vem de instituição diferente, fechando ataques de peer review do tipo "vocês só replicam uma variável".

### Eixo 1 — Status de desenvolvimento socioeconômico (UNCTAD, 2024)

**Fundamento:** Classificação oficial das Nações Unidas via UN Trade and Development. Define Global South como "África, América Latina e Caribe, Ásia (excluindo Israel, Japão, Coreia do Sul), e Oceania (excluindo Austrália e Nova Zelândia)".

**Por que importa para o artigo:** A principal hipótese da literatura crítica de IA (Mohamed, Png & Isaac, 2020; Couldry & Mejias, 2019) é que vieses em LLM refletem e reproduzem assimetrias coloniais de produção de conhecimento. A divisão UNCTAD operacionaliza essa assimetria.

**Referência canônica:** UNCTAD (2024). *Classifications Update — June 2024*. UNCTADstat.

### Eixo 2 — Recursos digitais e representação em NLP (Joshi et al., 2020)

**Fundamento:** Taxonomia de 6 classes de representação de línguas em corpus NLP, estabelecida na *state-and-fate* paper da ACL 2020. Classes 0 (*The Left-Behinds*) a 5 (*The Winners*), baseadas em: dados escritos disponíveis, dados não-rotulados, dados rotulados, recursos de NLP, presença em benchmarks.

**Por que importa:** Essa classificação é a **variável independente teorizada** do mecanismo em H4 (volume de tokens → gap de performance). Usar as classes de Joshi é amarrar a seleção ao mecanismo, não fazer escolha arbitrária.

**Mapeamento relevante para nosso estudo:**
- Classe 5: Inglês (EUA, UK)
- Classe 4: Alemão, Espanhol, Francês, Japonês, Mandarim, Árabe
- Classe 3: Português, Hindi, Indonésio
- Classe 2: Vietnamita, Filipino (tagalo), Bengali
- Classe 1: Suaíli, Amárico, Hausa, Iorubá, Zulu
- Classe 0: línguas com menos de 100k falantes representados em corpus

**Referência canônica:** Joshi, P. *et al.* (2020). The State and Fate of Linguistic Diversity and Inclusion in the NLP World. *Proceedings of ACL 2020*, 6282–6293.

### Eixo 3 — Renda per capita (World Bank, 2025)

**Fundamento:** Classificação anual do Banco Mundial baseada em GNI per capita (Atlas method). Quatro grupos: low, lower-middle, upper-middle, high income. FY26 em vigor de julho/2025 a junho/2026.

**Por que importa:** Permite **análise dose-resposta**. Se o gap de acurácia é monotônico com renda (como sugere WorldBench), temos evidência forte de mecanismo. Se não for, mecanismo é outro — e descobrir isso é contribuição.

**Referência canônica:** World Bank (2025). *World Bank Country and Lending Groups — FY26 Classification*.

---

## 3. Critérios adicionais de inclusão

Além dos três eixos, aplicamos quatro critérios filtrando:

| Critério | Justificativa | Implicação prática |
|---|---|---|
| **C1. Ground truth documental disponível** | H1 exige acurácia mensurável contra dados oficiais (ministérios, agências nacionais, sistemas de estatística) | Exclui países em conflito ou com governança estatística comprometida (ex: Síria, Venezuela no momento) |
| **C2. População ≥ 20 milhões** | Poder estatístico: países pequenos têm menos documentação pública agregada | Exclui Caribe pequeno, países insulares |
| **C3. Acesso do pesquisador a especialista regional** | H1 exige validação por painel | Prioriza países com rede acadêmica acessível via PPGSAU/UTFPR, CLACSO, CODESRIA |
| **C4. Diversidade linguística intra-Sul** | H2 testa interação língua × geografia | Cobertura de 4 famílias linguísticas Sul Global: românica (PT/ES), indo-ariana (HI/BN), austronésia (ID/TL), atlântica-congo (SW) |

---

## 4. Seleção final dos 15 países (ajuste de 18 → 15 proposto)

### 4.1 América Latina — 4 países (cortamos 1 da proposta original)

| País | UNCTAD | Renda (WB FY26) | Classe Joshi | Justificativa específica |
|---|---|---|---|---|
| **Brasil** | Sul | Upper-middle | 3 (PT) | Maior economia SG Américas; caso-core para Sabiá-3; língua ≠ EN/ES predominantes |
| **México** | Sul | Upper-middle | 4 (ES) | Segunda maior economia latina; ES é classe 4, contraste com PT classe 3 |
| **Argentina** | Sul | Upper-middle | 4 (ES) | Controle intra-Latam: mesma língua que México, contexto institucional diferente |
| **Peru** | Sul | Upper-middle | 4 (ES)* | Inclui grande pop. indígena (quéchua, classe 1); cobre heterogeneidade |

*Cortamos Colômbia — redundante com México/Argentina para nossas variáveis.*

### 4.2 África Subsaariana + Norte — 4 países

| País | UNCTAD | Renda | Classe Joshi | Justificativa |
|---|---|---|---|---|
| **Nigéria** | Sul | Lower-middle | 1-2 (EN, Hausa, Iorubá) | Maior economia África; inglês oficial + línguas locais classe 1 |
| **África do Sul** | Sul | Upper-middle | 1-3 (EN, Zulu, Xhosa) | Upper-middle em África; inglês dominante na administração |
| **Quênia** | Sul | Lower-middle | 1 (Suaíli, EN) | Suaíli é a língua de classe 1 mais falada; contraste com Nigéria |
| **Egito** | Sul | Lower-middle | 4 (Árabe) | Árabe classe 4 (alta representação digital) mas país da UNCTAD Sul — caso crítico para separar renda de língua |

*Cortamos Etiópia — importante mas documentação estatística em amárico é escassa, viola C1.*

### 4.3 Ásia — 4 países

| País | UNCTAD | Renda | Classe Joshi | Justificativa |
|---|---|---|---|---|
| **Índia** | Sul | Lower-middle | 4 (EN), 3 (HI) | Bilinguismo administrativo oficial — oportunidade única para isolar língua vs contexto |
| **Indonésia** | Sul | Upper-middle | 3 (ID) | Quarta maior população mundial; austronésia (nova família) |
| **Bangladesh** | Sul | Lower-middle | 3 (BN) | Close-neighbor à Índia; mesma classe linguística, renda menor — teste de renda isolada |
| **Filipinas** | Sul | Lower-middle | 2-4 (TL, EN) | Contraste com Indonésia (austronésia classe 2 vs 3) |

*Cortamos Vietnã — Indonésia + Filipinas já cobrem sudeste asiático; Vietnã teria redundância.*

### 4.4 Norte Global — 3 países (controle)

| País | UNCTAD | Renda | Classe Joshi | Justificativa |
|---|---|---|---|---|
| **Estados Unidos** | Norte | High | 5 (EN) | Referência absoluta de corpus training (maior contribuição Common Crawl) |
| **Alemanha** | Norte | High | 4 (DE) | High income + classe 4 (não 5) — desafia narrativa "Norte = classe 5" |
| **Japão** | Norte | High | 4 (JA) | Teste crítico: Ásia high-income com língua classe 4; desacopla geografia de renda |

---

## 5. Justificativa de balanceamento (crítico para reviewer)

O desenho final tem:

- **12 países Sul Global × 3 países Norte** — proporção 4:1 que privilegia o objeto de estudo sem ignorar controle.
- **4 continentes** (se incluirmos Norte América, Europa e Oceania-adjacent como categorias) — cobertura máxima dado n=15.
- **4 grupos de renda WB representados:** high (3), upper-middle (4), lower-middle (7), low (1 se incluirmos Etiópia na análise alternativa).
- **5 classes de Joshi representadas (1 a 5)** — exclui apenas classe 0 por inviabilidade operacional (línguas sem corpus digital).
- **4 famílias linguísticas:** indo-europeia, atlântica-congo, afro-asiática (árabe), austronésia, indo-ariana.

Essa cobertura é **defendível como "intencionalmente heterogênea nos três eixos teóricos que a literatura identifica como mecanismo do viés"** — linguagem que aparece literalmente no Methods do artigo.

---

## 6. Limitações declaradas (transparência Popper)

1. **Ausência de classe Joshi 0 e país low-income puro** — limitação reconhecida; Etiópia seria candidata mas falha C1.
2. **Oceania não coberta** — n=15 não comporta; trabalho futuro.
3. **Mundo árabe sub-representado** — apenas Egito; países do Golfo têm perfil híbrido (UNCTAD Sul mas renda high) que não cabe em nenhuma categoria clean.
4. **Heterogeneidade intra-país não capturada** — Índia é um país mas 22 línguas oficiais; análise agregada oculta essa variação. Limitação a discutir.

---

## 7. Análise de sensibilidade pré-registrada

Para proteger contra acusação de "seleção ad-hoc", pré-registramos três análises de sensibilidade:

1. **Leave-one-out:** remover cada país e re-estimar efeitos principais. Resultado robusto exige que nenhum país sozinho domine o efeito.
2. **Reclassificação para 4 grupos (alta-representação vs baixa-representação):** dicotomiza Joshi em classes 3-5 vs 0-2 e renda em high vs middle/low. Resultados devem replicar.
3. **Análise restrita a países com especialista validador:** subset com validação humana completa (previsto n ≥ 10).

---

## 8. Tabela-resumo para o Methods do artigo

| Eixo | Classificação | Fonte | N de países cobertos |
|---|---|---|---|
| Desenvolvimento | UNCTAD (Global North/South) | UNCTAD (2024) | Norte: 3; Sul: 12 |
| Renda | GNI per capita Atlas | World Bank (FY26, 2025) | High: 3; Upper-middle: 5; Lower-middle: 7 |
| Representação linguística | 6-class taxonomy | Joshi et al. (2020) | Classes 1-5 |
| Continente | — | UN Geoscheme | AL: 4; Afr: 4; Ás: 4; Eur+NA+Oc: 3 |

---

## 9. Referências para a bibliografia

```bibtex
@techreport{unctad2024classification,
  title={UNCTAD Statistical Classifications — June 2024 Update},
  author={{UNCTAD}},
  institution={UN Trade and Development},
  year={2024},
  url={https://unctadstat.unctad.org/EN/Classifications.html}
}

@inproceedings{joshi2020state,
  title={The State and Fate of Linguistic Diversity and Inclusion in the {NLP} World},
  author={Joshi, Pratik and Santy, Sebastin and Budhiraja, Amar and Bali, Kalika and Choudhury, Monojit},
  booktitle={Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics},
  pages={6282--6293},
  year={2020},
  publisher={Association for Computational Linguistics},
  doi={10.18653/v1/2020.acl-main.560}
}

@techreport{worldbank2025classification,
  title={World Bank Country and Lending Groups — FY26 Classification},
  author={{World Bank Group}},
  institution={The World Bank},
  year={2025},
  url={https://datahelpdesk.worldbank.org/knowledgebase/articles/906519}
}

@article{mohamed2020decolonial,
  title={Decolonial {AI}: Decolonial theory as sociotechnical foresight in artificial intelligence},
  author={Mohamed, Shakir and Png, Marie-Therese and Isaac, William},
  journal={Philosophy \& Technology},
  volume={33},
  number={4},
  pages={659--684},
  year={2020},
  doi={10.1007/s13347-020-00405-8}
}

@book{couldry2019costs,
  title={The costs of connection: How data is colonizing human life and appropriating it for capitalism},
  author={Couldry, Nick and Mejias, Ulises A.},
  year={2019},
  publisher={Stanford University Press}
}

@book{patton2015qualitative,
  title={Qualitative research and evaluation methods},
  author={Patton, Michael Quinn},
  year={2015},
  edition={4},
  publisher={SAGE Publications}
}
```
