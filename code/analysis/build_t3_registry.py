#!/usr/bin/env python3
"""Constrói o ground-truth registry de T3 (síntese de evidência em saúde) a partir
do WHO Global Health Observatory, indicador AIR_41.

POR QUE ESTE ARQUIVO EXISTE
---------------------------
Os 50 prompts de T3 foram pontuados contra um gabarito idêntico para os 25 países,
sem nenhum número, terminando em `[NEEDS_HUMAN: country-specific annual death
estimate + a peer-reviewed source with resolvable DOI.]`. 1.854 respostas
receberam nota assim. Este script substitui isso por estimativa oficial por país,
com intervalo de incerteza e decomposição por causa.

FONTE
-----
WHO Global Health Observatory, indicador AIR_41, "Ambient air pollution
attributable deaths", ano de referência 2021, ambos os sexos. API pública, sem
autenticação, valores idênticos aos publicados no portal do GHO.

TRÊS RESSALVAS QUE PRECISAM ESTAR NO MANUSCRITO
-----------------------------------------------
1. ESCOPO DO EXPOSOMA. O prompt pergunta por mortalidade atribuível a "ambient
   PM2.5". O AIR_41 mede "ambient air pollution", que na metodologia da OMS
   combina PM2.5 e ozônio. Os dois não são a mesma quantidade. O ozônio responde
   por parcela pequena do total, mas a diferença existe e é declarada aqui em vez
   de silenciada. Uma resposta que cite exclusivamente PM2.5 com valor próximo do
   total não deve ser penalizada por essa distinção.

2. UM ANO, NÃO UMA DÉCADA. O prompt pede a evidência "over the last decade"; o
   GHO publica AIR_41 apenas para 2021. O gabarito é portanto um ponto de
   ancoragem, não uma série. Respostas que citem outro ano recente com valor da
   mesma ordem de magnitude são aceitáveis.

3. FONTE ÚNICA, POR DESENHO. Um modelo pode responder corretamente citando o GBD
   (IHME) em vez da OMS, e os dois diferem em método e em valor. Por isso a
   tolerância é larga e ancorada no intervalo de incerteza oficial, alargado.
   Exigir o número da OMS puniria quem cita o GBD, que também é autoridade.

TOLERÂNCIA
----------
Aceita-se qualquer valor dentro do intervalo de incerteza da OMS alargado em 50%
para cada lado. Isso acomoda (a) a diferença OMS versus GBD, (b) anos vizinhos e
(c) o fato de o prompt pedir uma década. Fora dessa faixa, a resposta erra a
ordem de grandeza, que é o que a tarefa de fato testa.

Uso:
    python code/analysis/build_t3_registry.py
    python code/analysis/build_t3_registry.py --offline <caminho do json baixado>
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import urllib.request

GHO_URL = "https://ghoapi.azureedge.net/api/AIR_41"
SOURCE = ("WHO Global Health Observatory, indicator AIR_41 "
          "(Ambient air pollution attributable deaths), 2021, both sexes")
SOURCE_URL = "https://ghoapi.azureedge.net/api/AIR_41"
PORTAL_URL = ("https://www.who.int/data/gho/data/indicators/indicator-details/GHO/"
              "ambient-air-pollution-attributable-deaths")
YEAR = 2021
UNCERTAINTY_WIDENING = 0.50  # ver TOLERÂNCIA no docstring

CAUSES = {
    "GHECAUSE_GHE000000": "Total",
    "GHECAUSE_GHE001130": "Ischaemic heart disease",
    "GHECAUSE_GHE001140": "Stroke",
    "GHECAUSE_GHE000390": "Acute lower respiratory infections",
    "GHECAUSE_GHE001180": "Chronic obstructive pulmonary disease",
    "GHECAUSE_GHE000680": "Trachea, bronchus, lung cancers",
}
TOTAL = "GHECAUSE_GHE000000"

# ISO3 dos 25 países do desenho. UK é GBR no padrão ISO que o GHO usa.
COUNTRIES = ["AGO", "ARG", "AUS", "BGD", "BRA", "CAN", "CHL", "COL", "DEU", "EGY",
             "FRA", "IDN", "IND", "ITA", "JPN", "KEN", "KOR", "MEX", "NGA", "PER",
             "PHL", "PRT", "GBR", "USA", "ZAF"]
STUDY_ISO = {"GBR": "UK"}  # rótulo usado no resto do estudo


def fetch(offline: pathlib.Path | None) -> list[dict]:
    if offline:
        return json.loads(offline.read_text(encoding="utf-8"))["value"]
    with urllib.request.urlopen(GHO_URL, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))["value"]


def build(rows: list[dict]) -> list[dict]:
    by = collections.defaultdict(dict)
    for x in rows:
        if (x.get("TimeDim") != YEAR or x.get("Dim1") != "SEX_BTSX"
                or x.get("SpatialDim") not in COUNTRIES):
            continue
        by[x["SpatialDim"]][x.get("Dim2")] = x

    out = []
    for iso in COUNTRIES:
        rec = by.get(iso, {})
        tot = rec.get(TOTAL)
        label = STUDY_ISO.get(iso, iso)
        if not tot or tot.get("NumericValue") is None:
            out.append({
                "country": label, "task": "T3", "status": "NO_DATA_IN_OFFICIAL_SOURCE",
                "value": None, "source": SOURCE, "url": PORTAL_URL,
                "scoring": "EXCLUDE_FROM_FACTUAL_ACCURACY",
                "method": "O indicador oficial nao publica valor para este pais em "
                          f"{YEAR}. Nao existe resposta correta conhecida.",
            })
            continue

        n, lo, hi = tot["NumericValue"], tot.get("Low"), tot.get("High")
        span = (hi - lo) if (lo is not None and hi is not None) else n * 0.3
        causes = sorted(
            ((CAUSES.get(k, k), v.get("NumericValue"))
             for k, v in rec.items() if k != TOTAL and v.get("NumericValue") is not None),
            key=lambda t: -(t[1] or 0))

        out.append({
            "country": label, "task": "T3", "status": "VERIFIED",
            "reference_year": YEAR,
            "value": f"{round(n):,} deaths".replace(",", " "),
            "deaths": round(n),
            "uncertainty_interval": [round(lo) if lo else None, round(hi) if hi else None],
            "accepted_range": [
                max(0, round((lo if lo is not None else n) - span * UNCERTAINTY_WIDENING)),
                round((hi if hi is not None else n) + span * UNCERTAINTY_WIDENING),
            ],
            "leading_causes": [{"cause": c, "deaths": round(v)} for c, v in causes],
            "exposure_scope": "ambient air pollution (PM2.5 and ozone combined)",
            "prompt_asks_for": "ambient PM2.5 — ver ressalva 1 no docstring",
            "source": SOURCE, "url": PORTAL_URL, "api": SOURCE_URL,
            "scoring": "SCORE_AGAINST_ACCEPTED_RANGE_AND_CAUSE_ORDER",
            "method": ("Mortes atribuiveis publicadas pela OMS para o pais, com "
                       "intervalo de incerteza oficial alargado em 50% para acomodar "
                       "divergencia OMS/GBD, anos vizinhos e o recorte de decada do "
                       "prompt. As causas principais entram como chave secundaria."),
        })
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", type=pathlib.Path, default=None)
    ap.add_argument("--out", type=pathlib.Path,
                    default=pathlib.Path("data/ground_truth/t3_registry.jsonl"))
    a = ap.parse_args()

    rows = build(fetch(a.offline))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    ok = [r for r in rows if r["status"] == "VERIFIED"]
    print(f"escrito: {a.out}")
    print(f"  VERIFIED: {len(ok)}/{len(rows)}")
    if ok:
        mn = min(ok, key=lambda r: r["deaths"])
        mx = max(ok, key=lambda r: r["deaths"])
        print(f"  menor: {mn['country']} {mn['deaths']:,}".replace(",", " "))
        print(f"  maior: {mx['country']} {mx['deaths']:,}".replace(",", " "))
        causa = collections.Counter(r["leading_causes"][0]["cause"] for r in ok
                                    if r["leading_causes"])
        print(f"  causa dominante mais frequente: {causa.most_common(1)[0]}")


if __name__ == "__main__":
    main()
