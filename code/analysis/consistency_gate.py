#!/usr/bin/env python3
"""Gate de consistencia: corpo, suplemento e congelamento contam a mesma historia?

POR QUE ESTE GATE EXISTE
O estudo tem dois caminhos de calculo. formal_tests.py e h4_corpus_mechanism.py
rodam sobre judge_scores_confirmatory.jsonl, a pontuacao ORIGINAL; freeze_all_effects.py
roda sobre a pontuacao CORRIGIDA, depois que o gabarito de T2/T3 foi reconstruido
e a adjudicacao passou para codigo. O corpo do artigo migrou para os numeros
corrigidos. O suplemento nao migrou, e ficou doze numeros atras — Mann-Kendall
p=0.018 contra p=0.072, modelo misto p=0.007 contra p=0.069, H2 de -2.1 pp contra
-4.8 pp, e assim por diante. Uma auditoria externa leu as duas partes lado a lado
e concluiu, corretamente, que o manuscrito nao estava pronto para revisao.

Nada garantia essa sincronia. Este gate garante.

O QUE ELE VERIFICA
1. VALORES PROIBIDOS: cada numero pre-correcao conhecido nao pode reaparecer em
   nenhum .tex, com uma excecao deliberada — a secao de desvios do plano existe
   justamente para narrar "de X para Y", entao ali o valor antigo e legitimo e o
   gate o ignora.
2. ANCORAS: cada numero canonico do congelamento precisa estar presente onde o
   artigo o defende, na formatacao com que aparece no texto.
3. MARKDOWN DA RAIZ: o repositorio e PUBLICO, e um .md obsoleto contradiz o
   manuscrito com a mesma forca que um .tex. A versao 1 deste gate so varria
   .tex, e por esse ponto cego passaram tres arquivos versionados com numeros
   pre-correcao e com afirmacao de pre-registro — que o manuscrito nega. Os
   documentos de PLANO em docs/ sao isentos por construcao: eles registram o que
   foi pre-especificado, e reescreve-los seria falsificar o registro historico.

Falhar aqui significa que o corpo e o suplemento divergiram de novo. O conserto
nunca e editar o gate: e reconciliar o texto com o congelamento.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
FREEZE = ROOT / "data" / "processed" / "freeze_all_effects.json"
LATEX = ROOT / "latex"

# Secoes em que citar o valor antigo e o proposito do texto, nao um defeito.
ISENTAS = (
    # a nota que EXPLICA a deduplicacao precisa citar as 9.251 pontuacoes brutas
    r"\emph{The unit of analysis is the scored cell",
    r"\emph{A unidade de análise é a célula pontuada",
    r"\section{Deviations from the pre-specified analysis plan}",
    r"\section{Desvios em relação ao plano de análise pré-especificado}",
    r"\subsection{The methodological lesson",
    r"\subsection{A lição metodológica",
)

# (padrao, o que era, o que passou a ser) — todos confirmados contra o congelamento.
PROIBIDOS = [
    (r"\$p=0\.018\$",              "Mann-Kendall pre-correcao",      "p=0.072"),
    (r"-0\.077",                   "modelo misto pre-correcao",      "-0.066"),
    (r"\$p=0\.007\$",              "p do modelo misto pre-correcao", "p=0.069"),
    (r"-0\.065",                   "bayesiano pre-correcao",         "-0.052"),
    (r"-0\.096",                   "HDI bayesiano pre-correcao",     "-0.092"),
    (r"\$5\.37\$",                 "E-value do gradiente",           "nenhum: intervalo inclui o nulo"),
    (r"\+14\.1",                   "H5 pre-correcao",                "+13.3"),
    (r"\+0\.39~pp",                "H6 DiD pre-correcao",            "+0.65 pp"),
    (r"p=0\.257",                  "p de H6 pre-correcao",           "p=0.269"),
    (r"\+0\.539",                  "sitelinks pre-correcao",         "+0.362"),
    (r"\+0\.317",                  "parcial sitelinks pre-correcao", "+0.177"),
    (r"\+5\.8,\+7\.1",             "LOCO tier gap pre-correcao",     "[+4.5,+6.0]"),
    (r"n=762",                     "n de H2 pre-correcao",           "n=839"),
    (r"2\.1 percentage\s*\n?\s*points|\$-2\.1\$~pp|-2\.1~pp|de 2\.1 pontos",
                                   "H2 pre-correcao",                "4.8 pp"),
    (r"131[- ]item|131 respostas|131 responses", "amostra de calibracao", "3.190 itens do painel"),
    (r"ICC\$\(2,4\)",              "ICC da calibracao de 4 juizes",  "ICC(2,3) do painel de 3"),
    (r"Applied validity|Validade aplicada", "subcomponente inexistente", "calibracao"),
    (r"\$0\.23\$\s+of\s+the\s+Global\s+North|é\s+0\.23\s+da\s+chance",
                                   "OR de T1 pre-correcao",          "0.22"),
    (r"& 2\.67 &",                 "OR de T5 pre-correcao",          "3.58"),
    (r"to\s+\$0\.460\$|para\s+0\.460", "T2 pre-correcao",            "0.467"),
    # 0.07248 arredonda para 0.072; 0.073 era arredondamento errado, e circulava
    # em sete pontos entre corpo, suplemento e as duas linguas.
    (r"p=0\.073|p=0\.072",         "p de H1 antes da deduplicacao",  "p=0.043"),
    (r"\$\+5\.1\$~pp",              "tier gap antes da deduplicacao", "+5.4 pp"),
    (r"\[\+1\.6,\+8\.5\]",           "IC do tier gap pre-dedup",       "[+2.1,+8.7]"),
    (r"9\{,\}251",                  "n com pseudo-replicacao",        "8.300 celulas"),
    (r"7\{,\}580",                  "n ingles com pseudo-replicacao", "6.629"),
    (r"\$\+13\.3\$~pp",             "H5 antes da deduplicacao",       "+12.6 pp"),
]


# Markdown da raiz: valores pre-correcao em texto puro (sem a marcacao do LaTeX).
MD_PROIBIDOS = [
    (r"\+6[.,]2\s*pp",           "tier gap pre-correcao",    "+5.4 pp"),
    (r"(?:ρ|rho|p)\s*=\s*[+]?0[.,]51\b", "gradiente pre-correcao", "0.41"),
    (r"0\.512\b",                "gradiente pre-correcao",   "0.41"),
    (r"[-−]2[.,]1\s*pp",         "H2 pre-correcao",          "-4.8 pp"),
    (r"\+6[.,]7\s*pp",           "tier gap a n=15 pre-corr", "ver congelamento"),
]

# O manuscrito declara que o plano nunca foi depositado. Duas regras, porque uma
# so nao basta: a primeira exige a ressalva em qualquer .md que toque no assunto;
# a segunda barra a afirmacao direta mesmo num arquivo que ja traga a ressalva —
# senao bastava uma linha de ressalva no rodape para liberar o resto do texto.
MD_PREREG = r"pré-registrad|pre-registrad|pre-registered|pre-registration|post-registration|pré-registro|pre-registro"
MD_RESSALVA = (
    "no pre-registration", "não reivindica", "nao reivindica",
    "never deposited", "nunca foi depositado", "nunca depositado",
    "claims no pre-registration",
)
MD_AFIRMA = (
    r"(?:is|as) a pre-registered",
    r"conducting a pre-registered",
    r"pre-registered (?:study|benchmark|result|sample|analysis)",
    r"estudo pré-registrado",
    r"post-registration extension",
    r"extensão pós-registro",
)
# Texto entre aspas e citacao — inclusive a citacao que existe para dizer que
# aquilo saiu. Barrar a citacao proibiria explicar a propria correcao.
CITADO = re.compile(r"[\"“][^\"”\n]{0,200}[\"”]")


def checa_markdown_raiz(root: pathlib.Path) -> int:
    """docs/ guarda o plano historico e e isento; a raiz fala pelo projeto hoje."""
    falhas = 0
    for f in sorted(root.glob("*.md")):
        txt = f.read_text(encoding="utf-8", errors="ignore")
        plano = txt.replace("\n", " ")
        for padrao, era, virou in MD_PROIBIDOS:
            for m in re.finditer(padrao, plano):
                linha = txt[:m.start()].count("\n") + 1
                print(f"  FALHA {f.name}:{linha}  {era} -> deveria ser {virou}")
                falhas += 1
        if re.search(MD_PREREG, txt, re.I) and not any(r in txt for r in MD_RESSALVA):
            m = re.search(MD_PREREG, txt, re.I)
            linha = txt[:m.start()].count("\n") + 1
            print(f"  FALHA {f.name}:{linha}  toca em pre-registro sem a ressalva "
                  f"que o manuscrito declara")
            falhas += 1
        # mesmo offset: substituimos a citacao por espacos, nao a removemos
        sem_citacao = CITADO.sub(lambda m: " " * len(m.group(0)), plano)
        for padrao in MD_AFIRMA:
            for m in re.finditer(padrao, sem_citacao, re.I):
                linha = txt[:m.start()].count("\n") + 1
                print(f"  FALHA {f.name}:{linha}  afirma pre-registro "
                      f"(\"{m.group(0)}\") — o plano nunca foi depositado")
                falhas += 1
    return falhas


def fmt(v: float, casas: int, sinal: bool = False) -> str:
    s = f"{v:+.{casas}f}" if sinal else f"{v:.{casas}f}"
    return s


def ancoras(c: dict) -> list[tuple[str, str, tuple[str, ...]]]:
    """(rotulo, texto que precisa aparecer, arquivos onde procurar)"""
    RES = ("sections/04_results.tex",)
    RES_DISC = ("sections/04_results.tex", "sections/05_discussion.tex")
    RES_SUP = ("sections/04_results.tex", "supplement.tex")
    # Cada ancora e exigida SOMENTE onde o artigo de fato defende aquele numero.
    return [
        ("penalidade de idioma",  fmt(abs(c["nativa_pp"]), 1),          RES_DISC),
        ("gradiente HDI",         fmt(c["h1_rho_hdi"], 2),              RES_DISC),
        ("piso T1+T2",            fmt(c["acc_t1t2"], 3),                RES_DISC),
        ("hindi",                 fmt(abs(c["hindi_pp"]), 1),           RES),
        ("n de pares H2",         "839",                                RES),
        ("gradiente a n=15",      fmt(c["h1_rho_pre15"], 2),            RES),
        ("H4 dentro do pais",     "0.028",                              RES),
        ("H5",                    fmt(c["h5_pp"], 1),                   RES),
        ("LOCO tier gap min",     fmt(c["loo_gap_min"], 1),             RES),
        ("LOCO rho min",          fmt(c["loo_rho_min"], 2),             RES),
        ("alpha do painel",       "0.527",                              RES_SUP),
        ("ICC(2,3)",              "0.791",                              RES_SUP),
        ("bayesiano",             "-0.052",                             RES_SUP),
        ("E-value no limite",     "1.31",                               RES_SUP),
        ("OR de T1",              "0.22",                               RES),
        ("gradiente HDI (rho)",   fmt(c["h1_rho_hdi"], 2),              RES),
        ("familia primaria a n=15", "+0.104",                           ("supplement.tex",)),
    ]


def secoes_isentas(txt: str) -> list[tuple[int, int]]:
    faixas = []
    for marca in ISENTAS:
        i = txt.find(marca)
        while i != -1:
            j = txt.find("\\section{", i + len(marca))
            k = txt.find("\\subsection{", i + len(marca))
            fim = min(x for x in (j, k, len(txt)) if x != -1)
            faixas.append((i, fim))
            i = txt.find(marca, i + len(marca))
    return faixas


def main() -> int:
    c = json.loads(FREEZE.read_text(encoding="utf-8"))["corrigido"]
    alvos = sorted(
        list((LATEX / "sections").glob("*.tex"))
        + list((LATEX / "sections-PT").glob("*.tex"))
        + [LATEX / "supplement.tex", LATEX / "supplement-PT.tex",
           LATEX / "main.tex", LATEX / "main-PT.tex", LATEX / "highlights.tex"]
    )

    print("GATE DE CONSISTENCIA — corpo, suplemento e congelamento\n")
    falhas = 0

    print("(A) valores pre-correcao reaparecem?")
    for f in alvos:
        if not f.exists():
            continue
        bruto = f.read_text(encoding="utf-8")
        semcom = re.sub(r"%.*", "", bruto)     # comentarios nao sao o documento
        # LaTeX quebra frases no meio; sem achatar, um defeito escapa so por estar
        # partido em duas linhas. Trocamos \n por espaco, o que preserva os
        # offsets e portanto a contagem de linhas feita sobre `semcom`.
        txt = semcom.replace("\n", " ")
        isentas = secoes_isentas(txt)
        for padrao, era, virou in PROIBIDOS:
            for m in re.finditer(padrao, txt):
                if any(a <= m.start() < b for a, b in isentas):
                    continue
                linha = semcom[:m.start()].count("\n") + 1
                print(f"  FALHA {f.parent.name}/{f.name}:{linha}  {era} -> deveria ser {virou}")
                falhas += 1
    if falhas == 0:
        print("  nenhum")

    print("\n(B) valores canonicos presentes?")
    ausentes = 0
    for rotulo, valor, arquivos in ancoras(c):
        faltam = []
        onde = []
        for rel in arquivos:
            f = LATEX / rel
            if f.exists() and valor in f.read_text(encoding="utf-8"):
                onde.append(rel.split("/")[-1])
            else:
                faltam.append(rel.split("/")[-1])
        if not faltam:
            print(f"  ok    {rotulo:22s} {valor:>8s}  ({', '.join(onde)})")
        else:
            print(f"  FALHA {rotulo:22s} {valor:>8s}  ausente de: {', '.join(faltam)}")
            ausentes += 1

    print("\n(C) markdown da raiz contradiz o manuscrito?")
    md = checa_markdown_raiz(ROOT)
    if md == 0:
        print("  nenhum")

    total = falhas + ausentes + md
    print(f"\n{'GATE LIMPO' if total == 0 else f'GATE FALHOU: {total} problema(s)'}")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
