# Verificação de referências — estado final desta rodada

Gate SA-QG-010 (HOUSE-RULES R1): citar exige fichamento com leitura registrada.

## Cobertura

**44 referências citadas · 44 fichadas.** Nem toda fichada é "lida na íntegra" —
a profundidade está declarada em cada arquivo e resumida abaixo. Antes desta
rodada não havia nenhum fichamento; o que existia era checagem de sintaxe
(chave citada ↔ entrada no `.bib`).

| profundidade | quantas | o que significa |
|---|---|---|
| texto integral / fonte primária | 11 | PDF ou API oficial lidos |
| abstract ou metadados conferidos | 26 | a alegação que atribuímos está no trecho conferido |
| **não verificadas** | **4** | fonte inacessível ou não consultada |

### As 4 não verificadas — e por quê

- **`unctad2024classification`** — `unctadstat.unctad.org` devolve HTTP 403 a
  ferramentas automatizadas. **É a mais séria da lista**: a divisão Norte/Sul da
  UNCTAD é a espinha dorsal do desenho amostral e do achado principal. Precisa de
  conferência manual.
- **`who2021aqg`** — repositório IRIS da OMS devolve 403. A afirmação que ela
  sustenta também se apoia em `gbd2019risk`, que foi confirmado.
- **`patton2015qualitative`** — livro, sem localizador digital.
- **`opuszko2026unraveling`** — capítulo Springer atrás de paywall; o título
  sustenta o tema, não o achado específico que lhe atribuímos.

Parciais que merecem nota: **`kozlakidis2026medical`** (o abstract confirma o
tema, não a frase específica sobre ambientes regulatórios; o texto é aberto na
Frontiers e cabe numa próxima rodada) e **`vanderweele2017evalue`** (paywall; a
definição e a prática de reportar dois E-values foram confirmadas por fontes que
descrevem o método).

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
