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
]


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
        ("H4 dentro do pais",     "0.026",                              RES),
        ("H5",                    fmt(c["h5_pp"], 1),                   RES),
        ("LOCO tier gap min",     fmt(c["loo_gap_min"], 1),             RES),
        ("LOCO rho min",          fmt(c["loo_rho_min"], 2),             RES),
        ("alpha do painel",       "0.527",                              RES_SUP),
        ("ICC(2,3)",              "0.791",                              RES_SUP),
        ("bayesiano",             "-0.052",                             RES_SUP),
        ("E-value no limite",     "1.31",                               RES_SUP),
        ("OR de T1",              "0.22",                               RES),
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

    total = falhas + ausentes
    print(f"\n{'GATE LIMPO' if total == 0 else f'GATE FALHOU: {total} problema(s)'}")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
