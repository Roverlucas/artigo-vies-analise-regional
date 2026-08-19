#!/usr/bin/env python3
"""Constrói o conjunto de referência de T4 (instrumentos de política) a partir do
Apêndice 1 do UNEP Global Assessment of Air Pollution Legislation (GAAPL).

POR QUE ESTE ARQUIVO EXISTE
---------------------------
T4 foi pontuada como `factual_accuracy_and_completeness` contra um gabarito que
dizia `[NEEDS_HUMAN: enumerate the specific national programs/instruments]`, para
os 25 países. 1.825 respostas receberam nota assim.

A objeção inicial do squad era que T4 não admite gabarito porque a resposta certa
é um conjunto e não existe autoridade que o feche. A objeção estava errada quanto
ao fato: o UNEP publicou, em 2021, uma avaliação da legislação de qualidade do ar
de 194 Estados mais a UE, com metodologia única, e o Apêndice 1 lista, por país,
os instrumentos legais com sua fonte primária.

POR QUE ESTA FONTE E NÃO UMA LISTA NOSSA
-----------------------------------------
Se nós montássemos o conjunto país a país, a completude ficaria correlacionada
com o quanto a legislação de cada país é acessível para nós, ou seja, com o tier
do país, que é a variável sob teste. O GAAPL elimina isso: o esforço de pesquisa
foi do UNEP e foi o mesmo para todos os países. O catálogo correlato do UNEP
acrescenta uma propriedade que nenhum gabarito nosso teria, que é ter sido
submetido aos próprios governos para revisão e correção.

O QUE ESTE CONJUNTO É, E O QUE NÃO É
-------------------------------------
NÃO é a lista completa dos instrumentos de política de poluição do ar de um país.
É o conjunto de instrumentos legais **verificados por uma autoridade
internacional, com fonte primária publicada, na data de corte de 15 de dezembro
de 2020**. O escopo do apêndice são instrumentos que contêm padrões de qualidade
do ar ambiente, que é um subconjunto do que T4 pergunta.

Consequência direta para a pontuação: **não se mede completude**. Mede-se

  COBERTURA  — quantos itens do conjunto de referência a resposta recupera.
               Captura conhecimento, e é o que carrega o gradiente.
  FABRICAÇÃO — dos instrumentos que a resposta cita, quantos não existem.
               Captura risco operacional, e é reportado como desfecho separado.

Medir os dois separados foi decisão do autor, e é mais forte que qualquer um
sozinho: cobertura sem fabricação premiaria a resposta evasiva, que não cita nada
e não erra nada; fabricação sem cobertura não distingue quem sabe de quem cala.

Uso:
    python code/analysis/build_t4_registry.py --gaapl-txt <texto do GAAPL>
    (o PDF do GAAPL não é redistribuído; ver SOURCE_URL)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

SOURCE = ("UNEP, Regulating Air Quality: The First Global Assessment of Air "
          "Pollution Legislation, Appendix 1 (as at 15 December 2020)")
SOURCE_URL = ("https://www.unep.org/resources/report/"
              "regulating-air-quality-first-global-assessment-air-pollution-legislation")
CUTOFF = "2020-12-15"

# Nome no GAAPL -> ISO usado no estudo. Só os 25 do desenho.
NAME_TO_ISO = {
    "Angola": "AGO", "Argentina": "ARG", "Australia": "AUS", "Bangladesh": "BGD",
    "Brazil": "BRA", "Canada": "CAN", "Chile": "CHL", "Colombia": "COL",
    "Germany": "DEU", "Egypt": "EGY", "France": "FRA", "Indonesia": "IDN",
    "India": "IND", "Italy": "ITA", "Japan": "JPN", "Kenya": "KEN",
    "Republic of Korea": "KOR", "Korea (Republic of)": "KOR", "South Korea": "KOR",
    "Mexico": "MEX", "Nigeria": "NGA", "Peru": "PER", "Philippines": "PHL",
    "Portugal": "PRT", "United Kingdom": "UK",
    # o nome ocupa tres linhas no PDF; o parser recupera as duas primeiras
    "United Kingdom of": "UK", "United Kingdom of Great Britain": "UK",
    "United Kingdom of Great Britain and Northern Ireland": "UK",
    "United States": "USA", "United States of America": "USA",
    "South Africa": "ZAF",
}
ALL_ISO = ["AGO", "ARG", "AUS", "BGD", "BRA", "CAN", "CHL", "COL", "DEU", "EGY",
           "FRA", "IDN", "IND", "ITA", "JPN", "KEN", "KOR", "MEX", "NGA", "PER",
           "PHL", "PRT", "UK", "USA", "ZAF"]

ENTRY = re.compile(r"^\s{0,8}(\d{1,3})\.\s{1,8}([A-Z][A-Za-z'’\.\-\(\) ]{2,45}?)\s{2,}(\S.*)$")
NOISE = re.compile(r"(Global Assessment of Air Pollution Legislation|^\s*\d+\s*$|"
                   r"^\s*Country\s|^\s*\[see section|^\s*Where “data not publicly)")


def slice_appendix(lines: list[str]) -> list[str]:
    """Recorta o Apêndice 1. O título aparece duas vezes: no sumário e na seção."""
    ini = next(i for i, l in enumerate(lines)
               if l.strip().startswith("Appendix 1: Legal instruments") and i > 3000)
    fim = next(i for i, l in enumerate(lines)
               if l.strip().startswith("Appendix 2: Global assessment") and i > ini)
    return lines[ini:fim]


# Nomes de país quebram em duas linhas no PDF ("Antigua and" / "Barbuda",
# "Republic" / "of Korea"). Um nome que termina nestes tokens está incompleto.
CONT = re.compile(r"(\band|\bof|\bthe|Republic|Kingdom|United|Democratic|Saint|"
                  r"Great|New|South|North|Central|Bosnia|Trinidad|Papua|Sao|Cote)$", re.I)


def parse(lines: list[str]) -> dict[str, dict]:
    """Cada país abre com 'N. Nome' e segue em linhas de continuação até o próximo.

    Duas complicações do layout: o nome pode quebrar em duas linhas, e a coluna
    de fonte (URLs) é lida pelo pdftotext na mesma linha da coluna de instrumento.
    """
    out, cur = {}, None
    for line in lines:
        m = ENTRY.match(line)
        if m:
            nome = re.sub(r"\s+", " ", m.group(2)).strip()
            cur = {"gaapl_index": int(m.group(1)), "country_name": nome,
                   "raw": [m.group(3)], "_name_open": bool(CONT.search(nome))}
            out[nome] = cur
        elif cur is not None and line.strip() and not NOISE.search(line):
            # completa o nome quando ele quebrou na linha anterior
            if cur.get("_name_open"):
                # a continuacao pode comecar em minuscula ("of Korea", "and Barbuda")
                head = re.match(r"^\s{4,24}((?:of |and |the )?[A-Za-z][A-Za-z'’\.\- ]{1,30}?)(?:\s{2,}|$)", line)
                if head:
                    antigo = cur["country_name"]
                    novo = f"{antigo} {head.group(1).strip()}".strip()
                    out.pop(antigo, None)
                    cur["country_name"] = novo
                    out[novo] = cur
                cur["_name_open"] = False
            cur["raw"].append(line)
    for r in out.values():
        r.pop("_name_open", None)
    return out


def instruments_from(raw: list[str]) -> tuple[list[str], list[str]]:
    """Separa nome do instrumento (coluna 1) das URLs de fonte (coluna 2+)."""
    urls, nomes = [], []
    for l in raw:
        urls += re.findall(r"(?:https?://|www\.)[^\s\]]+", l)
        # coluna 1 termina onde começa a fonte; corta na primeira URL ou em 2+ espaços
        col1 = re.split(r"\s{2,}(?=(?:https?://|www\.|Data not|Anexo|Annex))", l)[0]
        col1 = re.sub(r"(?:https?://|www\.)\S+", "", col1)
        # fragmentos de URL que o pdftotext costura na coluna errada
        col1 = re.sub(r"\S*(?:/|\.pdf|\.html|_publisher|asset_|uploads|wp-content)\S*", "", col1)
        col1 = re.sub(r"\b(?:Yes|No)\b\s*$", "", col1)
        col1 = re.sub(r"\s+", " ", col1).strip(" ;,-")
        if col1 and not col1.lower().startswith(("data not", "yes", "no")):
            nomes.append(col1)
    texto = re.sub(r"\s+", " ", " ".join(nomes)).strip()
    # separa múltiplos instrumentos por ano entre parênteses ou ponto-e-vírgula
    partes = [p.strip(" ;,") for p in re.split(r";|(?<=\)\s)(?=[A-Z])", texto) if len(p.strip()) > 12]
    return partes or ([texto] if texto else []), sorted(set(urls))


# Sinais de que o pdftotext costurou colunas erradas nesta linha. O layout do
# Apêndice 1 é de quatro colunas e o extrator acerta a maioria, não todas. Marcar
# o que saiu sujo é obrigatório: um gabarito com lixo é pior que gabarito nenhum,
# e foi exatamente o que esta rodada existe para consertar.
DIRT = [
    (re.compile(r"\b(containing ambient air quality|primary source unless|"
                r"see section|see Figure|Type of instrument)\b", re.I), "cabecalho de tabela"),
    (re.compile(r"\b(legislation|Policy/guidance|Secondary|National environment act)\s*$", re.I),
     "coluna 'tipo de instrumento' colada"),
    (re.compile(r"[a-z]-[a-z]+-de-|_publisher|\b\d{2}-de-"), "fragmento de URL"),
    (re.compile(r"N°\s*–|N°\s*$|No\.\s*$"), "numero do ato perdido"),
]


def quality(iso: str, itens: list[str], nome_fonte: str) -> tuple[str, list[str]]:
    """Classifica a extração. NEEDS_HUMAN_REVIEW não é falha: é o estado honesto."""
    flags = []
    texto = " ".join(itens)
    for pat, rotulo in DIRT:
        if pat.search(texto):
            flags.append(rotulo)
    # nome do país costurado dentro do instrumento
    for token in nome_fonte.split():
        if len(token) > 3 and re.search(rf"\w\s{token}\s\w", texto):
            flags.append("nome do pais dentro do instrumento"); break
    return ("CLEAN" if not flags else "NEEDS_HUMAN_REVIEW"), sorted(set(flags))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gaapl-txt", required=True, type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path,
                    default=pathlib.Path("data/ground_truth/t4_reference_set.jsonl"))
    a = ap.parse_args()

    lines = a.gaapl_txt.read_text(encoding="utf-8", errors="replace").splitlines()
    todos = parse(slice_appendix(lines))

    by_iso = {}
    for nome, rec in todos.items():
        iso = NAME_TO_ISO.get(nome)
        if iso:
            by_iso[iso] = rec

    rows = []
    for iso in ALL_ISO:
        rec = by_iso.get(iso)
        if not rec:
            rows.append({
                "country": iso, "task": "T4",
                "status": "NOT_LISTED_IN_GAAPL_APPENDIX_1",
                "reference_set": [], "source_urls": [],
                "source": SOURCE, "url": SOURCE_URL, "cutoff": CUTOFF,
                "scoring": "FABRICATION_ONLY",
                "method": ("O pais nao consta do Apendice 1, que lista apenas Estados "
                           "com instrumento legal contendo padroes de qualidade do ar "
                           "na data de corte. Nao ha conjunto de referencia; a celula "
                           "recebe apenas o desfecho de fabricacao."),
            })
            continue
        instrumentos, urls = instruments_from(rec["raw"])
        q, flags = quality(iso, instrumentos, rec["country_name"])
        rows.append({
            "extraction_quality": q,
            "extraction_flags": flags,
            "country": iso, "task": "T4", "status": "REFERENCE_SET_AVAILABLE",
            "country_name_in_source": rec["country_name"],
            "gaapl_index": rec["gaapl_index"],
            "reference_set": instrumentos,
            "reference_set_size": len(instrumentos),
            "source_urls": urls,
            "source": SOURCE, "url": SOURCE_URL, "cutoff": CUTOFF,
            "completeness_claim": "NONE — verified subset, not an exhaustive list",
            "scoring": "COVERAGE_PLUS_FABRICATION",
            "method": ("Conjunto de instrumentos legais verificados pelo UNEP com fonte "
                       "primaria publicada. Cobertura = itens do conjunto recuperados "
                       "pela resposta. Fabricacao = instrumentos citados que nao "
                       "existem, reportada como desfecho separado. Nao se mede "
                       "completude, porque o conjunto nao a alega."),
        })

    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    ok = [r for r in rows if r["status"] == "REFERENCE_SET_AVAILABLE"]
    limpos = [r for r in ok if r.get("extraction_quality") == "CLEAN"]
    print(f"escrito: {a.out}")
    print(f"  extracao limpa            : {len(limpos)}/25")
    print(f"  precisa revisao humana    : {len(ok)-len(limpos)}/25 "
          f"{[r['country'] for r in ok if r.get('extraction_quality') != 'CLEAN']}")
    print(f"  paises no GAAPL Appendix 1 (total): {len(todos)}")
    print(f"  com conjunto de referencia: {len(ok)}/25")
    faltam = [r["country"] for r in rows if r["status"] != "REFERENCE_SET_AVAILABLE"]
    if faltam:
        print(f"  sem conjunto: {faltam}")
    if ok:
        tam = [r["reference_set_size"] for r in ok]
        print(f"  itens por pais: min {min(tam)}, mediana {sorted(tam)[len(tam)//2]}, max {max(tam)}")


if __name__ == "__main__":
    main()
