#!/usr/bin/env python3
"""Familia primaria restrita aos 15 paises pre-especificados, sobre o scoring CORRIGIDO.

POR QUE ESTE SCRIPT EXISTE
O manuscrito prometia, em duas passagens, que todo efeito calculado sobre os 25
paises viria "ao lado do seu valor pre-especificado de 15 paises". Na pratica so
o gradiente de H1 tinha essa contraparte no corpo, e a tabela do suplemento
trazia tres linhas com um "ns" generico, herdado da analise pre-correcao. Ou o
texto cumpria a promessa, ou parava de faze-la.

A decisao foi focar o manuscrito nos 25 paises e deixar a coluna de 15 no
suplemento, completa. Este script produz essa coluna a partir da mesma acuracia
corrigida por pais que alimenta o corpo (freeze_all_effects.json), de modo que os
dois lados da tabela saiam do mesmo lugar.

CUIDADO COM O MANN-KENDALL
mann_kendall() recebe a serie de acuracia JA ORDENADA por IDH, nao pares
(IDH, acuracia). Passar tuplas faz a funcao comparar tuplas e devolver uma
tendencia negativa significativa que nao existe. O teste de sanidade no fim
compara o Spearman e o Mann-Kendall: os dois medem monotonicidade e nao podem
discordar em sinal.
"""
from __future__ import annotations

import json
import math
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.formal_tests import (  # noqa: E402
    COV, spearman, partial_spearman, p_from_r, mann_kendall,
)

FREEZE = ROOT / "data" / "processed" / "freeze_all_effects.json"
CORPUS = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "country_corpus_measures.json"
SAIDA = ROOT / "data" / "processed" / "pre15_corrigido.json"


def main() -> int:
    fz = json.loads(FREEZE.read_text(encoding="utf-8"))["corrigido"]
    acc = {k: v[0] for k, v in fz["por_pais"].items()}
    pre15 = [p for p in COV if p in acc]
    if len(pre15) != 15:
        print(f"AVISO: {len(pre15)} paises pre-especificados com dado, esperados 15")

    hdi = [COV[p][0] for p in pre15]
    a = [acc[p] for p in pre15]
    joshi = [COV[p][1] for p in pre15]

    r_hdi = spearman(hdi, a)
    p_hdi = p_from_r(r_hdi, len(a))
    # a serie precisa entrar ordenada por IDH; ver a nota no topo
    S, Z, p_mk = mann_kendall([x for _, x in sorted(zip(hdi, a))])
    r_joshi = spearman(joshi, a)
    p_joshi = p_from_r(r_joshi, len(a))

    cc = json.loads(CORPUS.read_text(encoding="utf-8"))
    xs, ys, hs = [], [], []
    for p in pre15:
        v = cc.get(p, {}).get("wd_sitelinks")
        if v:
            xs.append(math.log(v))
            ys.append(acc[p])
            hs.append(COV[p][0])
    r_cov = partial_spearman(xs, ys, hs)
    p_cov = p_from_r(r_cov, len(xs) - 1)

    print("Familia primaria nos 15 paises pre-especificados (scoring corrigido)\n")
    print(f"  H1 Spearman(acuracia, IDH)        rho={r_hdi:+.3f}  p={p_hdi:.3f}")
    print(f"  H1 Mann-Kendall (por IDH)         S={S}  Z={Z:+.2f}  p={p_mk:.3f}")
    print(f"  H1 Spearman(acuracia, Joshi)      rho={r_joshi:+.3f}  p={p_joshi:.3f}")
    print(f"  H4 parcial(cobertura | IDH)       rho={r_cov:+.3f}  p={p_cov:.3f}  (n={len(xs)})")

    out = {
        "n_paises": len(pre15),
        "h1_rho_hdi": r_hdi, "h1_p_hdi": p_hdi,
        "h1_mk_S": S, "h1_mk_Z": Z, "h1_mk_p": p_mk,
        "h1_rho_joshi": r_joshi, "h1_p_joshi": p_joshi,
        "h4_parcial_cobertura_hdi": r_cov, "h4_p_parcial": p_cov,
    }
    SAIDA.write_text(json.dumps(out, indent=2), encoding="utf-8")

    # (a) o gradiente aqui tem de bater com o que o congelamento ja publica
    esperado = fz["h1_rho_pre15"]
    ok_freeze = abs(esperado - r_hdi) < 1e-9
    # (b) Spearman e Mann-Kendall medem monotonicidade; discordar em sinal
    #     significa que a serie entrou desordenada
    ok_sinal = (r_hdi >= 0) == (S >= 0)
    print(f"\n  gradiente contra o congelamento: {r_hdi:.6f} vs {esperado:.6f}"
          f" -> {'OK' if ok_freeze else 'DIVERGE'}")
    print(f"  Spearman e Mann-Kendall concordam em sinal -> {'OK' if ok_sinal else 'DIVERGE'}")
    print(f"\n  escrito: {SAIDA}")
    return 0 if (ok_freeze and ok_sinal) else 1


if __name__ == "__main__":
    raise SystemExit(main())
