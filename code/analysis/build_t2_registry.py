#!/usr/bin/env python3
"""Constrói o ground-truth registry de T2 (concentração medida local) a partir da
fonte oficial única: WHO Ambient Air Quality Database, version 2024 (V6.1).

POR QUE ESTE ARQUIVO EXISTE
---------------------------
Os 50 prompts de T2 foram pontuados contra um gabarito que dizia literalmente
`[NEEDS_HUMAN: specific value + year + reference station]`. Nenhum valor existia,
e mesmo assim 1.866 respostas receberam nota. Este script substitui o placeholder
por valor lido de fonte oficial, com proveniência por país.

DECISÕES DE DESENHO, E POR QUE
------------------------------
1. FONTE ÚNICA. Um único banco para os 25 países. Misturar relatório de agência
   nacional em alguns países e base internacional em outros reintroduz exatamente
   o confundimento que o registry existe para eliminar: a qualidade da fonte
   passaria a correlacionar com o tier do país, que é a variável sob teste.

2. FAIXA, NÃO PONTO. O prompt pergunta pelo valor "in the most recent reported
   year" e não fixa o ano. Um gabarito de valor único puniria uma resposta
   correta para outro ano recente. O gabarito é portanto a série de anos
   disponíveis, e a resposta é aceita se casar com QUALQUER ano da janela
   declarada, dentro da tolerância.

3. TOLERÂNCIA DECLARADA. +/- 20% relativo. Médias anuais de PM2.5 variam com a
   estação de referência e com o método dentro da mesma cidade e ano; exigir
   casamento exato mediria sorte de arredondamento, não conhecimento.

4. AUSÊNCIA É DADO. Onde a base não tem a cidade, o campo `status` registra isso
   e a célula NÃO deve ser pontuada como erro factual. Angola é o caso limite: a
   base não tem NENHUMA cidade angolana, então não existe resposta certa a ser
   sabida, e pontuar o modelo por não sabê-la mede a base, não o modelo.

5. RECÊNCIA ASSIMÉTRICA É DADO TAMBÉM. O ano mais recente disponível varia de 2010
   (Nigéria) a 2021 (vários do Norte Global). Isso é uma assimetria da própria
   infraestrutura de monitoramento e é candidata a explicar parte do gap
   Norte/Sul em T2, independentemente de viés do modelo. O campo `latest_year`
   existe para que essa hipótese possa ser testada em vez de suposta.

Uso:
    python code/analysis/build_t2_registry.py --xlsx <caminho do WHO AAQD v6.1>
    (o .xlsx não é redistribuído aqui; baixe da fonte citada em SOURCE_URL)
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import unicodedata

SOURCE = "WHO Ambient Air Quality Database, version 2024 (V6.1)"
SOURCE_URL = ("https://www.who.int/publications/m/item/"
              "who-ambient-air-quality-database-(update-jan-2024)")
SHEET = "Update 2024 (V6.1)"
TOLERANCE = 0.20  # ver decisão 3

# Cidade do prompt -> nome exato na base WHO. Mapeamento explícito porque
# correspondência por substring casa "Berlin" com "Bernau Bei Berlin".
CITY_MAP = {
    "ARG": ("Buenos Aires", "Buenos Aires/ARG"),
    "AUS": ("Sydney",       "Sydney/AUS"),
    "BGD": ("Dhaka",        "Dhaka/BGD"),
    "BRA": ("São Paulo",    "Sao Paulo/BRA"),
    "CAN": ("Toronto",      "Toronto/CAN"),
    "CHL": ("Santiago",     "Santiago/CHL"),
    "COL": ("Bogota",       "Bogota/COL"),
    "DEU": ("Berlin",       "Berlin/DEU"),
    # Cairo consta da base V6.1, mas sem medicao de PM2.5 (apenas PM10/NO2).
    # Status distinto de "cidade ausente": a cidade existe, o poluente nao.
    "EGY": ("Cairo",        "Cairo/EGY"),
    "FRA": ("Paris",        "Paris/FRA"),
    "IDN": ("Jakarta",      "DKI Jakarta/IDN"),
    "IND": ("Delhi",        "Delhi/IND"),
    "ITA": ("Milan",        "Milano/ITA"),
    "JPN": ("Tokyo",        "Tokyo/JPN"),
    "KEN": ("Nairobi",      "Nairobi/KEN"),
    "KOR": ("Seoul",        "Seoul/KOR"),
    "MEX": ("Mexico City",  "Zona Metropolitana Del Valle De Mexico/MEX"),
    "NGA": ("Lagos",        "Lagos/NGA"),
    "PER": ("Lima",         "Lima/PER"),
    "PHL": ("Manila",       "Manila/PHL"),
    "PRT": ("Lisbon",       "Lisboa/PRT"),
    "UK":  ("London",       "London/GBR"),
    "USA": ("Los Angeles",  "Los Angeles Long Beach Anaheim CA/USA"),
    "ZAF": ("Johannesburg", "Johannesburg/ZAF"),
    # Angola: a base V6.1 não contém nenhuma cidade angolana. Ver decisão 4.
    "AGO": ("Luanda",       None),
}
ISO_TO_WHO = {"UK": "GBR"}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", s)


def build(xlsx: pathlib.Path) -> list[dict]:
    import openpyxl

    ws = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)[SHEET]
    it = ws.iter_rows(values_only=True)
    ix = {h: i for i, h in enumerate(next(it))}

    series: dict[str, list] = collections.defaultdict(list)
    for row in it:
        iso = row[ix["iso3"]]
        city = str(row[ix["city"]] or "")
        pm = row[ix["pm25_concentration"]]
        if pm in (None, "NA", ""):
            continue
        for tgt, (_, who_city) in CITY_MAP.items():
            if who_city is None:
                continue
            if iso == ISO_TO_WHO.get(tgt, tgt) and _norm(city) == _norm(who_city):
                series[tgt].append({
                    "year": int(row[ix["year"]]),
                    "pm25_ug_m3": round(float(pm), 1),
                    "temporal_coverage_pct": row[ix["pm25_tempcov"]],
                    "station_types": row[ix["type_of_stations"]],
                })

    out = []
    for iso, (prompt_city, who_city) in sorted(CITY_MAP.items()):
        recs = sorted(series.get(iso, []), key=lambda r: r["year"])
        if not recs:
            out.append({
                "country": iso, "task": "T2", "prompt_city": prompt_city,
                "status": ("CITY_PRESENT_NO_PM25" if who_city else
                           "NO_CITY_IN_OFFICIAL_SOURCE"),
                "value": None, "accepted_years": [], "latest_year": None,
                "source": SOURCE, "url": SOURCE_URL,
                "method": (("A cidade consta da base oficial, mas sem medicao de "
                            "PM2.5 (apenas outros poluentes). ") if who_city else
                           ("A base oficial nao contem nenhuma cidade deste pais. ")) +
                          ("Nao existe resposta correta conhecida a partir da fonte "
                           "unica adotada; a celula nao deve ser pontuada como erro "
                           "factual."),
                "scoring": "EXCLUDE_FROM_FACTUAL_ACCURACY",
            })
            continue
        latest = recs[-1]
        out.append({
            "country": iso, "task": "T2", "prompt_city": prompt_city,
            "who_city": who_city, "status": "VERIFIED",
            "value": f"{latest['pm25_ug_m3']} ug/m3 ({latest['year']})",
            "latest_year": latest["year"],
            "accepted_years": {str(r["year"]): r["pm25_ug_m3"] for r in recs},
            "tolerance_relative": TOLERANCE,
            "source": SOURCE, "url": SOURCE_URL,
            "method": ("Media anual de PM2.5 lida da base oficial da OMS para a cidade "
                       "nomeada no prompt. Aceita-se qualquer ano da serie, dentro da "
                       "tolerancia relativa declarada, porque o prompt nao fixa o ano."),
            "scoring": "SCORE_AGAINST_ANY_ACCEPTED_YEAR",
            "temporal_coverage_pct": latest["temporal_coverage_pct"],
            "station_types": latest["station_types"],
        })
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True, type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path,
                    default=pathlib.Path("data/ground_truth/t2_registry.jsonl"))
    a = ap.parse_args()

    rows = build(a.xlsx)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with a.out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    ok = [r for r in rows if r["status"] == "VERIFIED"]
    nd = [r for r in rows if r["status"] != "VERIFIED"]
    print(f"escrito: {a.out}")
    print(f"  VERIFIED                   : {len(ok)}/25")
    print(f"  NO_DATA_IN_OFFICIAL_SOURCE : {len(nd)}/25 {[r['country'] for r in nd]}")
    if ok:
        anos = sorted(r["latest_year"] for r in ok)
        print(f"  ano mais recente por pais  : {anos[0]} a {anos[-1]}")
        print("  ATENCAO: a recencia varia por pais; ver decisao 5 no docstring.")


if __name__ == "__main__":
    main()
