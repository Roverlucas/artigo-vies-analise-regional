#!/usr/bin/env python3
"""Proxies de corpus do PAIS recomputados sobre o scoring CORRIGIDO.

POR QUE ESTE SCRIPT EXISTE
h4_corpus_mechanism.py roda sobre judge_scores_confirmatory.jsonl, isto e, sobre
a pontuacao ORIGINAL. Depois que o gabarito de T2/T3 foi reconstruido e a
adjudicacao passou para o codigo, os efeitos mudaram, e o corpo do artigo passou
a citar os valores do congelamento (freeze_all_effects.json). A tabela de proxies
do suplemento, porem, continuava com os numeros pre-correcao — o que produzia
contradicao entre corpo e suplemento.

Este script recomputa os tres proxies de cobertura de pais sobre a acuracia
corrigida por pais, que e a mesma que alimenta o corpo. O sitelinks serve de
verificacao: ele tambem e calculado dentro do freeze, e os dois caminhos precisam
devolver o mesmo numero.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.formal_tests import (  # noqa: E402
    COV, COV_EXT, spearman, partial_spearman, p_from_r,
)

FREEZE = ROOT / "data" / "processed" / "freeze_all_effects.json"
CORPUS = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "country_corpus_measures.json"

PROXIES = (
    ("en_wiki_bytes", "English-Wikipedia bytes"),
    ("wd_sitelinks", "Wikidata sitelinks"),
    ("wd_statements", "Wikidata statements"),
)


def main() -> int:
    fz = json.loads(FREEZE.read_text(encoding="utf-8"))
    acc = {k: v[0] for k, v in fz["corrigido"]["por_pais"].items()}
    cc = json.loads(CORPUS.read_text(encoding="utf-8"))
    todas = {**COV, **COV_EXT}

    print("Proxies de corpus do pais sobre o scoring corrigido (n=25)\n")
    saida = {}
    for campo, rotulo in PROXIES:
        xs, ys, hs = [], [], []
        for pais, a in acc.items():
            valor = cc.get(pais, {}).get(campo)
            if valor is None or pais not in todas:
                continue
            xs.append(math.log(valor))
            ys.append(a)
            hs.append(todas[pais][0])
        r = spearman(xs, ys)
        pv = p_from_r(r, len(xs))
        pr = partial_spearman(xs, ys, hs)
        ppv = p_from_r(pr, len(xs) - 1)
        saida[campo] = {"rho": r, "p": pv, "partial_hdi": pr, "p_partial": ppv, "n": len(xs)}
        print(f"  {rotulo:26s} n={len(xs)}  rho={r:+.3f} (p={pv:.3f})"
              f"   parcial|IDH={pr:+.3f} (p={ppv:.3f})")

    # verificacao cruzada: o sitelinks tambem sai do freeze
    esperado = fz["corrigido"]["h4_rho_sitelinks"]
    obtido = saida["wd_sitelinks"]["rho"]
    ok = abs(esperado - obtido) < 1e-9
    print(f"\n  verificacao sitelinks contra o congelamento: "
          f"{obtido:.6f} vs {esperado:.6f} -> {'OK' if ok else 'DIVERGE'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
