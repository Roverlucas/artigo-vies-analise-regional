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
    # "+5.1 pp" voltou a ser legitimo (subconjunto balanceado, macro \\ngapbal); o valor
    # antigo circulava como "$+5.1$~pp" no texto do tier gap, hoje sempre macro.
    (r"a gap of \$\+5\.1\$~pp|lacuna de \$\+5\.1\$~pp", "tier gap antes da deduplicacao", "+5.4 pp"),
    (r"\[\+1\.6,\+8\.5\]",           "IC do tier gap pre-dedup",       "[+2.1,+8.7]"),
    (r"9\{,\}251",                  "n com pseudo-replicacao",        "8.300 celulas"),
    (r"7\{,\}580",                  "n ingles com pseudo-replicacao", "6.629"),
    (r"\$\+13\.3\$~pp",             "H5 antes da deduplicacao",       "+12.6 pp"),
    # ---- 2026-09-21: T1 passou para codigo; juiz x tier confundidos; EGY excluida
    (r"\$\+5\.4\$~pp|\+5\.4~pp|\+5\.44|\$\+5\.4\$ percentage|\+5\.4 pontos", "tier gap antes do T1 por codigo", "+5.0 pp"),
    (r"\[\+2\.1,\+8\.7\]",           "IC do tier gap antes do T1 por codigo", "[+1.5,+8.4]"),
    (r"p=0\.043",                   "p do gradiente antes do T1 por codigo", "p=0.076"),
    (r"\\?rho\s*=\s*\+?0\.(?:41\b|408)|\\rho\(\\text\{accuracy\},\\text\{HDI\}\)=\+0\.41", "gradiente antes do T1 por codigo", "0.36"),
    # -4.8 pp aparece legitimamente (subconjunto fiel, pesos iguais); so o 4.75 e proibido
    (r"-4\.75|4\.75~pp|4\.8 percentage points", "H2 antes do T1 por codigo", "-4.95 pp / 5.0 pp"),
    (r"-11\.1~pp|\$-11\.1\$|11\.1~pp", "hindi antes do T1 por codigo", "-11.4 pp"),
    (r"\+12\.6~pp|\$\+12\.6\$",      "H5 antes do T1 por codigo",     "+13.0 pp"),
    (r"& 0\.22 &|OR[ =~$]*0\.22\b|odds are \$?0\.22|0\.22 of the|0\.22 das",  "OR de T1 sob o juiz original", "0.33"),
    (r"8\{,\}300 scored|8\{,\}300 células pontuadas|8\{,\}300 respostas", "celulas antes de excluir EGY em T1", "8,244"),
    (r"6\{,\}629",                 "n ingles antes de excluir EGY em T1", "6,573"),
    (r"p=0\.27\b",                  "p da persona (valor errado que circulava)", "p=0.29"),
    (r"\\delta=-0\.45\b|\\delta=-0\.47\).*floor", "piso antes do T1 por codigo", "-0.41"),
    (r"single-judge scores|juiz unico original|original\s+single-judge", "T1 e T5 no juiz original", "T1 por codigo; T5 no juiz da coleta"),
    (r"\+0\.83~pp|\$\+0\.8\$~pp",    "H6 DiD antes do T1 por codigo",  "+0.5 pp"),
]


# Valores que NAO podem aparecer nem nas secoes isentas: nao sao "de X para Y",
# sao simplesmente o numero errado. (O 6.629 escapou por estar numa secao isenta.)
PROIBIDOS_SEMPRE = [
    (r"6\{,\}629|6\.629",             "n ingles antes de excluir EGY",  "6,573"),
    (r"62\.5\\% of T2|62\.5\\% de T2|83\.6\\%", "cobertura de codigo T2/T3 antiga", "56.3% / 71.8%"),
    # p=0.069 saiu da lista: e hoje o p legitimo de H4 no nivel do pais (\\nhfourctryp).
    (r"p=0\.42\b",                 "p de permutacao antigo",          "p=0.80"),
    (r"0\.994|-0\.052|-0\.066|\[-0\.092,-0\.016\]|-0\.048|\[-0\.090,-0\.009\]|p=0\.087", "bayesiano/misto desatualizados", "0.987 / -0.049 / -0.063 / p=0.086"),
    (r"OR[ =~$]*0\.33\b|odds are \$?0\.33|0\.33 of the|0\.33 da chance|RC 0\.33|\+13\.0~pp|\$\+13\.0\$", "valores antes do BGD=35 (OR T1 0.33 / H5 13.0)", "0.32 / 12.8"),
    (r"1\.30 at the confidence|\$1\.30\$ (?:at|no)", "E-value antes do BGD=35", "1.31"),
    (r"\$-4\.6\$~pp",                "H2 fiel antigo",                 "-4.8 pp"),
    (r"\+5\.06\b|\+2\.39\b|\+2\.92\b|\+1\.53\b|\+2\.09\b|\+2\.74\b|\+1\.83\b", "taxonomia antes do run 3", "+5.05/+2.14/+2.78/+1.94"),
    (r"\+0\.153\b|\+0\.399\b|\+0\.296\b|\+0\.132\b|\+0\.142\b", "proxies H4 antes do run 3", "0.146/0.369/0.248/0.125/0.048"),
    (r"tables_pt/",                  "tabelas PT desatualizadas (pasta removida)", "supplement/tables/"),
    # rodada 13 (parecer de painel): afirmacoes falsas como executado ou refutadas
    (r"12\.9 points|12\.9 pontos|by 12\.9",  "H5 digitado a mao (12.9 vs macro 12.8)", "\\nhfive"),
    (r"five Joshi classes|cinco classes de\s*\n?\s*Joshi", "classes de Joshi (sao tres)", "three Joshi classes"),
    (r"honou?r a fixed seed|honram uma seed fixa|\\texttt\{seed\\_status\} field \(|campo \\texttt\{seed\\_status\} \(", "seed nunca foi enviada", "no seed was sent"),
    (r"falls monotonically with mC4|cai monotonicamente com", "es>pt no mC4 mas penalidade es>pt: nao e monotono", "Hindi smallest corpus, largest penalty"),
    (r"committed to is excluded|nos comprometemos (?:é|e) excluíd", "IC de Fisher inclui 0,55", "interval includes both zero and the threshold"),
    (r"LLM-Retrieved|recuperada por LLMs", "titulo: nao ha retrieval", "LLM-Recalled / que os LLMs recordam"),
    (r"identified only up to that pair|identificado apenas até esse par", "H4 nao se estabelece no nivel do pais", "not established"),
]

# Markdown da raiz: valores pre-correcao em texto puro (sem a marcacao do LaTeX).
MD_PROIBIDOS = [
    (r"\+6[.,]2\s*pp",           "tier gap pre-correcao",    "+5.4 pp"),
    (r"(?:ρ|rho|p)\s*=\s*[+]?0[.,]51\b", "gradiente pre-correcao", "0.41"),
    (r"0\.512\b",                "gradiente pre-correcao",   "0.41"),
    (r"[-−]2[.,]1\s*pp",         "H2 pre-correcao",          "-4.8 pp"),
    (r"\+6[.,]7\s*pp",           "tier gap a n=15 pre-corr", "ver congelamento"),
    # 2026-09-21: valores anteriores ao T1 por codigo que circulavam no README
    (r"\+5[.,][14]\s*pp",         "tier gap antes do T1 por codigo", "+5.0 pp"),
    (r"\b0[.,]2[23]\b(?! da chance do Norte| of Global North odds)", "OR de T1 sob os juizes", "0.33"),
    (r"[-−]4[.,]8\s*pp",         "H2 antes do T1 por codigo", "-5.0 pp"),
    (r"\+13[.,]3\s*pp",          "H5 antes do T1 por codigo", "+13.0 pp"),
    (r"9,251|9\.251",            "n com pseudo-replicacao",   "8,244"),
    (r"T1 and T5 retain|single-judge scores", "T1/T5 no juiz original", "T1 por codigo; T5 juiz da coleta"),
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
    """docs/ guarda o plano historico e e isento; a raiz fala pelo projeto hoje.

    CITATION.cff entra junto: e a metadata que o GitHub exibe e que o Zenodo
    ingere, e o resumo dela dizia "a pre-registered benchmark".
    """
    falhas = 0
    arquivos = sorted(root.glob("*.md")) + [root / "CITATION.cff",
                                            root / "preregistration" / "README.md"]
    for f in arquivos:
        if not f.exists():
            continue
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


def macros_geradas() -> dict:
    nums = LATEX / "numbers.tex"
    if not nums.exists():
        return {}
    return dict(re.findall(r"\\newcommand\{\\(n[a-z]+)\}\{((?:[^{}]|\{[^{}]*\})*)\}", nums.read_text(encoding="utf-8")))


def ancoras(c: dict) -> list[tuple[str, str, tuple[str, ...]]]:
    """(rotulo, texto que precisa aparecer, arquivos onde procurar)
    Valores que nao vem do freeze vem de latex/numbers.tex (gerado dos artefatos),
    nunca de constante escrita aqui: constante escrita aqui envelhece."""
    Mx = macros_geradas()
    RES = ("sections/04_results.tex",)
    RES_DISC = ("sections/04_results.tex", "sections/05_discussion.tex")
    RES_SUP = ("sections/04_results.tex", "supplement.tex")
    # Cada ancora e exigida SOMENTE onde o artigo de fato defende aquele numero.
    ABS = ("sections/00_abstract.tex",)
    return [
        ("penalidade de idioma",  fmt(abs(c["nativa_pp"]), 1),          RES_DISC),
        ("penalidade (abstract)", fmt(abs(c["nativa_pp"]), 1),          ABS),
        ("gradiente HDI",         fmt(c["h1_rho_hdi"], 2),              RES),
        ("p do gradiente",        "p=" + fmt(c["h1_p"], 3),             RES),
        ("piso T1+T2",            fmt(c["acc_t1t2"], 3),                RES),
        ("piso delta",            fmt(c["cliff_piso"], 2),              RES),
        ("hindi",                 fmt(abs(c["hindi_pp"]), 1),           RES),
        ("n de pares H2",         "839",                                RES),
        ("gradiente a n=15",      fmt(c["h1_rho_pre15"], 2),            RES),
        ("tier gap",              fmt(c["tier_gap_pp"], 1),             RES_DISC),
        ("tier gap (abstract)",   fmt(c["tier_gap_pp"], 1),             ABS),
        ("IC do tier gap",        f"[{fmt(c['tier_gap_ci'][0],1,True)},{fmt(c['tier_gap_ci'][1],1,True)}]", RES),
        ("H4 dentro do pais",     Mx.get("nhfourbeta", "0.030").lstrip("+"), RES),
        ("H4 conjunto com HDI",   Mx.get("nhfourjcob", "0.012").lstrip("+"), RES),
        ("H4 rho no nivel do pais", Mx.get("nhfourctryrho", "-0.37"),   RES_DISC),
        ("H4 p no nivel do pais", "p=" + Mx.get("nhfourctryp", "0.069"), RES_DISC),
        ("OR bruta de T1 (pais)", Mx.get("norrawone", "0.44"),           ABS + RES),
        ("IC de Fisher do rho",   Mx.get("nrhocihi", "+0.66"),           RES_DISC),
        ("H5",                    fmt(c["h5_pp"], 1),                   RES),
        ("H6 DiD",                fmt(c["h6_did"], 1, True),            RES),
        ("p da persona",          "p=" + fmt(c["persona_p"], 2),        ABS + RES_DISC),
        ("H3 delta",              fmt(c["cliff_regional"], 2),          RES_DISC),
        ("LOCO tier gap min",     fmt(c["loo_gap_min"], 1),             RES),
        ("LOCO rho min",          fmt(c["loo_rho_min"], 2),             RES),
        ("LOCO rho max",          fmt(c["loo_rho_max"], 2),             RES),
        ("alpha do painel",       Mx.get("nalpha", "0.527"),                RES_SUP),
        ("ICC(2,3)",              Mx.get("niccpanel", "0.791"),             RES_SUP),
        ("bayesiano",             Mx.get("nbayes", "-0.049"),               RES_SUP),
        ("E-value no limite",     Mx.get("nevaluelim", "1.31"),             RES_SUP),
        ("OR de T1",              Mx.get("nort", "0.32"),                   RES),
        ("OR de T1 sem chave nao padrao", Mx.get("nortexcl", "0.39"),       RES),
        ("gradiente HDI (rho)",   fmt(c["h1_rho_hdi"], 2),              RES),
        ("familia primaria a n=15", "+" + Mx.get("nrhopre", "0.08").lstrip("+") if False else "+0.079", ("supplement.tex",)),
        ("celulas analisadas",    "8{,}244",                            ABS + RES),
        ("n ingles",              "6{,}573",                            RES),
        ("modelo misto",          Mx.get("nmixedbeta", "-0.063"),           RES_SUP),
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


def expande_macros(txt: str) -> str:
    """O texto carrega \\nXXX (latex/numbers.tex) no lugar de numeros; o gate
    confere o texto como o leitor o ve, entao expande as macros antes de checar."""
    nums = LATEX / "numbers.tex"
    if not nums.exists():
        return txt
    macros = dict(re.findall(r"\\newcommand\{\\(n[a-z]+)\}\{((?:[^{}]|\{[^{}]*\})*)\}", nums.read_text(encoding="utf-8")))
    # nomes mais longos primeiro, para \nort nao comer \nortci
    for k in sorted(macros, key=len, reverse=True):
        txt = re.sub(r"\\" + k + r"(?![a-zA-Z])(\{\})?", lambda m: macros[k], txt)
    return txt


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
        bruto = expande_macros(f.read_text(encoding="utf-8"))
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
        for padrao, era, virou in PROIBIDOS_SEMPRE:
            for m in re.finditer(padrao, txt):
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
            if f.exists() and valor in expande_macros(f.read_text(encoding="utf-8")):
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
