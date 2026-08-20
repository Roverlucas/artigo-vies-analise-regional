#!/usr/bin/env python3
"""H4 com o conjunto de controles que o plano especifica: HDI E log GDP per capita.

POR QUE ESTE ARQUIVO EXISTE
---------------------------
`03_methods.tex:326` especifica a correlação parcial de H4 "after adjusting for
HDI *and* log GDP per capita". O código de análise não menciona GDP em lugar
nenhum: `formal_tests.py` ajusta só por HDI. O resultado publicado, portanto, não
é o resultado especificado. Isso foi apontado pela validação em segundo modelo e
confirmado por inspeção do código.

Este script executa a especificação e reporta os dois lados, para que a diferença
fique visível em vez de ser escolhida.

FONTE DO GDP
------------
World Bank, indicador NY.GDP.PCAP.PP.KD (GDP per capita, PPP, constant 2021
international $), ano de referência 2022, para casar com o vintage do HDI já
usado (UNDP HDR 2023-24, dados de 2022). Obtido pela API pública, sem chave.

MÉTODO
------
Correlação parcial de Spearman com dois controles, pela fórmula recursiva:

    r(xy·z1z2) = [ r(xy·z1) - r(xz2·z1) r(yz2·z1) ]
                 / sqrt( (1 - r(xz2·z1)^2)(1 - r(yz2·z1)^2) )

Cada termo de primeira ordem usa a mesma `partial_spearman` do pipeline, de modo
que o número aqui é comparável ao publicado e não vem de outra implementação.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.formal_tests import (  # noqa: E402
    COV, COV_EXT, SCORES, spearman, partial_spearman, p_from_r,
)


def load_country_accuracy() -> dict[str, float]:
    """Media do composite por pais, com o MESMO filtro do formal_tests: descarta
    erro de juiz e usa so prompts em ingles, para nao misturar o efeito de idioma
    no nivel-pais. Replicar o filtro importa: um recorte diferente daria outro
    numero e a comparacao com o publicado deixaria de valer."""
    import json as _json
    import statistics as _st
    rows = [_json.loads(l) for l in open(SCORES, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if "composite" in r and not r.get("error")
            and "JUDGE_API_ERROR" not in str(r.get("rationale", ""))]
    eng = [r for r in rows if "_AP_" in (r.get("prompt_id") or "")
           and not (r.get("prompt_id") or "").endswith(("_pt", "_es", "_hi"))]
    out = {}
    for r in eng:
        out.setdefault(r.get("country_iso3"), []).append(r["composite"])
    return {c: _st.mean(v) for c, v in out.items() if v}

WB_URL = ("https://api.worldbank.org/v2/country/{iso}/indicator/"
          "NY.GDP.PCAP.PP.KD?date=2022&format=json&per_page=100")
WB_SOURCE = ("World Bank, NY.GDP.PCAP.PP.KD (GDP per capita, PPP, constant 2021 "
             "international $), reference year 2022")
STUDY_TO_WB = {"UK": "GBR"}


def fetch_gdp(isos: list[str]) -> dict[str, float]:
    wb = [STUDY_TO_WB.get(i, i) for i in isos]
    with urllib.request.urlopen(WB_URL.format(iso=";".join(wb)), timeout=90) as r:
        d = json.loads(r.read().decode())
    raw = {x["countryiso3code"]: x["value"] for x in d[1] if x.get("value") is not None}
    inv = {v: k for k, v in STUDY_TO_WB.items()}
    return {inv.get(k, k): float(v) for k, v in raw.items()}


def partial_two(x, y, z1, z2) -> float:
    """Parcial de segunda ordem, construída a partir das de primeira ordem."""
    r_xy_z1 = partial_spearman(x, y, z1)
    r_xz2_z1 = partial_spearman(x, z2, z1)
    r_yz2_z1 = partial_spearman(y, z2, z1)
    den = math.sqrt((1 - r_xz2_z1 ** 2) * (1 - r_yz2_z1 ** 2))
    return (r_xy_z1 - r_xz2_z1 * r_yz2_z1) / den if den else float("nan")


def main() -> None:
    cov = {**COV, **COV_EXT}
    acc = load_country_accuracy()
    paises = sorted(c for c in cov if c in acc)

    gdp = fetch_gdp(paises)
    faltam = [c for c in paises if c not in gdp]
    if faltam:
        print(f"  sem GDP: {faltam} — excluídos desta análise")
        paises = [c for c in paises if c in gdp]

    y = [acc[c] for c in paises]
    hdi = [cov[c][0] for c in paises]
    wiki = [math.log(cov[c][1]) for c in paises]
    lgdp = [math.log(gdp[c]) for c in paises]

    print(f"H4 — proxy de corpus (Wikipedia) contra acurácia, n={len(paises)}")
    print(f"  fonte do GDP: {WB_SOURCE}\n")

    bruta = spearman(y, wiki)
    so_hdi = partial_spearman(y, wiki, hdi)
    especificada = partial_two(y, wiki, hdi, lgdp)

    print(f"  {'sem controle':<34} rho={bruta:+.3f}  p={p_from_r(bruta, len(paises)):.3f}")
    print(f"  {'controlando HDI (publicado)':<34} rho={so_hdi:+.3f}  "
          f"p={p_from_r(so_hdi, len(paises), partial=1):.3f}")
    print(f"  {'controlando HDI + log GDP (plano)':<34} rho={especificada:+.3f}  "
          f"p={p_from_r(especificada, len(paises), partial=2):.3f}")
    print(f"\n  diferenca entre o publicado e o especificado: "
          f"{especificada - so_hdi:+.3f}")

    # o mesmo para o proxy exploratório de cobertura, se existir no covariate set
    print("\n  (colinearidade entre os controles)")
    print(f"    rho(HDI, log GDP) = {spearman(hdi, lgdp):+.3f}")

    out = ROOT / "data" / "processed" / "h4_with_gdp.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "n": len(paises), "countries": paises,
        "gdp_source": WB_SOURCE,
        "rho_uncontrolled": bruta,
        "rho_partial_hdi_only_published": so_hdi,
        "rho_partial_hdi_and_log_gdp_as_specified": especificada,
        "rho_hdi_vs_log_gdp": spearman(hdi, lgdp),
        "gdp_per_capita_ppp_2022": gdp,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  escrito: {out}")


if __name__ == "__main__":
    main()
