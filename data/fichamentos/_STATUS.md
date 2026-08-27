# Verificação de referências — estado após a rodada de 27/08/2026

Gate SA-QG-010 (HOUSE-RULES R1): citar exige fichamento com leitura registrada.

## Cobertura

**44 referências citadas · 44 fichadas.** Nem toda fichada é "lida na íntegra" —
a profundidade está declarada em cada arquivo e resumida abaixo. Antes desta
rodada não havia nenhum fichamento; o que existia era checagem de sintaxe
(chave citada ↔ entrada no `.bib`).

| profundidade | quantas | o que significa |
|---|---|---|
| texto integral / fonte primária | 36 | PDF, XML de repositório ou API oficial lidos |
| abstract ou metadados conferidos | 7 | a alegação que atribuímos está no trecho conferido |
| **não verificadas** | **1** | fonte inacessível |

### A não verificada

- **`patton2015qualitative`** — livro, sem localizador digital. Sustenta o termo
  "amostragem teórica", não um número nem um achado.

### As 7 ainda em abstract — e por quê

Quatro são artigos do próprio GIQ (`aoki2024explainable`, `kim2026genai`,
`robinson2026opensource`, `choroszewicz2026crumple`): são open access CC-BY, mas o
ScienceDirect recusa acesso automatizado, e a única versão em repositório
localizada (`robinson2026opensource`, OPUS4) não expõe o arquivo. `requia2024shortterm`
e `opuszko2026unraveling` estão atrás de paywall sem versão verde localizada.
`mollick2025personas` é SSRN, cujo download exige sessão de navegador.

Em todas, o que o manuscrito atribui está no título e no abstract conferidos —
nenhuma sustenta número nosso.

## Correções que saíram da leitura

Nenhuma apareceria numa checagem de `.bib`.

1. **`abadji2022oscar` — atribuição falsa.** O texto creditava ao paper os tamanhos
   es 429,9 / pt 105,0 / hi 32,6 GB. O paper descreve o OSCAR **22.01** e traz
   381,9 / 170,3 / 23,3. Nossos números são do dataset card do **OSCAR-2301** — e
   da versão **original**, não da "deduplicated" como dizíamos. Corrigido no texto
   (EN e PT) e em `corpus_measures.py`, onde o rótulo errado nasceu.
2. **`lecoz2025policymaking` — vocabulário emprestado.** "context-blind rigidity" é
   literal e as quatro cidades conferem, mas *Global North* e *Global South* **não
   aparecem no artigo**. Atribuíamos a eles nossa própria moldura. Reescrito com a
   formulação dos autores.
3. **`bender2021stochastic` — atribuição forte demais.** Chamávamos o Stochastic
   Parrots de "a explicação dominante para o viés geográfico". O artigo argumenta
   contra ingerir a web sem curadoria e documentação. Atribuição reduzida ao que a
   fonte sustenta.
4. **`almeida2025portuguese` — inferência apresentada como achado alheio.** Dizíamos
   que a fonte "evidencia como o Common Crawl sub-representa conteúdo lusófono".
   Ela não afirma isso; afirma que o esforço se concentrou no inglês e que corpora
   eficazes para outros idiomas seguem em aberto. Reescrito.
5. **`mollick2025personas` — não é replicação.** Chamávamos de "replicação
   independente" do Zheng. É estudo independente com outro desenho (seis modelos,
   múltipla escolha de pós-graduação). Reescrito com o desenho real.
6. **`google2026promptingstrategies` — limitação mais severa que a fonte.** A doc
   admite o papel na system instruction **ou** "at the very beginning of the user
   prompt", que é o canal que testamos. Três dos quatro guias põem no system
   prompt; o Google admite os dois. Refinado.
7. **`oecd2024governing`** — ano 2024 → **2025** (CrossRef).
8. **`anthropic2026systemprompts`** — URL redirecionava 301 e o título era o de uma
   seção. Entrada reescrita com o verbatim.
9. **`quijano2000coloniality`** — o DOI localizado pertence à **reimpressão de 2008**
   no livro *Coloniality at Large*, não ao artigo de 2000 no *Nepantla* que a
   entrada declara. Registrado como nota, em vez de fingir que é o DOI do original.
10. **`zenodo2026dataset` — removida.** Era citada no texto e descrevia um depósito
    "to be deposited on publication": citação a algo que não existe. Eu a inseri
    para silenciar um aviso de "entrada não citada".

## Um caso na direção contrária

**`zheng2024helpful`** justifica sozinho a exigência de texto integral. O abstract
diz apenas *"does not improve performance"*; nossa frase afirma que as personas
reduzem levemente a acurácia. **Pelo abstract eu teria enfraquecido uma frase
correta.** O texto completo diz *"no or small negative effects"* e *"might actually
hurt their performance on objective tasks"*. A regra protege nos dois sentidos.

## Localizadores recuperados

Sete entradas não tinham DOI nem URL e foram localizadas no CrossRef:
`abadji2022oscar`, `myung2024blend`, `kozlakidis2026medical`, `opuszko2026unraveling`,
`almeida2025portuguese`, `semopy`, `quijano2000coloniality`. Quatro DOIs do arXiv
davam 404 no CrossRef — não é erro: o arXiv deposita no DataCite. Todos existem.

## Correções da rodada de 27/08/2026 (leitura integral de mais 14 fontes)

11. **`unctad2024classification` — rótulo atribuído à fonte errada.** O texto dizia
    "a divisão Norte/Sul Global da UNCTAD". A UNCTAD **não usa** esses termos: sua
    classificação é *developing (1400) / developed (1500) economies*. O Norte/Sul é
    enquadramento nosso, vindo da colonialidade. Corrigido em corpo e suplemento nos
    dois idiomas. A conferência trouxe também um reforço: a regra verbatim da UNCTAD
    ("developed economies broadly comprise Northern America and Europe, Israel, Japan,
    the Republic of Korea, Australia, and New Zealand") foi aplicada país a país aos
    25 e **não há uma divergência sequer** — Coreia do Sul inclusive, que era o caso
    de risco. A regra foi transcrita no suplemento para o revisor conferir.

12. **`gbd2019risk` — afirmação mais forte que a fonte.** A introdução dizia que o
    material particulado fino é *o* principal fator de risco ambiental. O GBD 2019
    classifica por níveis e o principal fator global de mortes atribuíveis é pressão
    arterial sistólica alta. Corrigido para "entre os principais". A OMS sustenta a
    forma forte para *poluição do ar* ("the leading environmental risk factor
    globally"), não para o material particulado isolado.

13. **`cordella2024regulating` — inferência nossa atribuída aos autores.** O texto
    dizia que eles argumentam que arcabouços neutros "deixam a verificação no ponto
    de uso como o controle operante". Essa segunda metade não existe no artigo.
    Reescrito para o que eles de fato defendem.

14. **`oecd2024governing` — usos não documentados.** Atribuíamos ao relatório
    implantações que ajudam servidores a "buscar normas e redigir sínteses técnicas".
    O relatório documenta o "Albert" francês, que auxilia atendentes a acessar
    informação e as fontes por trás dela. Corrigido para isso.

15. **`vanderweele2017evalue` — rota de conversão não declarada.** O código usa
    RR≈exp(0.91·d), que é exatamente a aproximação prescrita pela fonte para efeitos
    padronizados. Estava correta, mas invisível no manuscrito; agora declarada nos
    métodos junto com a ressalva de que herda os pressupostos da aproximação.

16. **`benjamini1995fdr` — garantia condicional não declarada.** O procedimento é
    provado "for independent test statistics"; nossos testes F3 não são independentes.
    A ressalva foi declarada nos métodos.
