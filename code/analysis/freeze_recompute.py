#!/usr/bin/env python3
"""Congelamento: recomputa os efeitos com o composto corrigido e compara com o publicado.

O QUE MUDA EM RELAÇÃO AO PUBLICADO
-----------------------------------
1. T2 e T3 deixam de ser pontuadas contra `[NEEDS_HUMAN: ...]`. Onde o valor era
   extraível e plausível, quem decide é código (`score_numeric.py`); o resíduo foi
   ao painel. T4 passa a ser pontuada contra o conjunto de referência do UNEP.
2. O escore deixa de vir de um juiz único que está dentro da amostra avaliada e
   passa a ser a MÉDIA de um painel multi-fornecedor. Isso também faz do ICC do
   painel a quantidade operativa, que o manuscrito reportava sem usar.

O QUE NÃO MUDA, DE PROPÓSITO
-----------------------------
T1 e T5 não foram repontuadas: T1 sempre teve gabarito oficial e T5 é rubrica.
Os escores originais delas entram intactos, para que a diferença observada venha
da correção do gabarito e não de um novo instrumento aplicado a tudo.

COMPOSTO
--------
Mesmos pesos do instrumento original (llm_judge.RUBRIC_WEIGHTS), para que a
comparação isole o efeito da correção. A crítica de que 30% do peso é preenchido
por valor padrão continua válida e é tratada em separado; mudar os pesos aqui
misturaria dois efeitos.
"""
from __future__ import annotations

import collections
import json
import math
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.formal_tests import (  # noqa: E402
    COV, COV_EXT, GS, GS_EXT, SCORES, spearman, partial_spearman, p_from_r, mann_kendall,
)

PANEL = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_panel_repontuacao.jsonl"
NUMERIC = ROOT / "data" / "processed"
PESOS = {"factual_accuracy": 0.30, "contextual_completeness": 0.25,
         "citation_quality": 0.15, "calibration": 0.15,
         "absence_of_hallucination": 0.15}


def composto(d: dict) -> float:
    return sum(d[k] * w for k, w in PESOS.items())


def carregar_novos() -> dict[tuple, float]:
    """Escore novo por (prompt_id, model_id, replicate_idx).

    Prioridade: veredito determinístico de T2/T3 quando existe; senão a média do
    painel. O determinístico vence porque comparar número com faixa é exato e o
    juiz, no melhor caso, reproduz isso com ruído.
    """
    novos: dict[tuple, float] = {}

    # 1. veredito por código (T2, T3)
    for t in ("T2", "T3"):
        f = NUMERIC / f"numeric_scores_{t}.jsonl"
        if not f.exists():
            continue
        for line in f.open(encoding="utf-8"):
            r = json.loads(line)
            if r["verdict"] in ("CORRECT", "INCORRECT"):
                # o codigo decide APENAS a acuracia factual; os demais
                # subcomponentes continuam vindo do juiz original, senao
                # estariamos trocando o instrumento inteiro sem necessidade
                novos[(r["prompt_id"], str(r["model_id"]), 0)] = (
                    1.0 if r["verdict"] == "CORRECT" else 0.0)

    # 2. media do painel
    por = collections.defaultdict(list)
    if PANEL.exists():
        for line in PANEL.open(encoding="utf-8"):
            r = json.loads(line)
            if all(k in r for k in PESOS):
                por[(r["prompt_id"], str(r["model_id"]),
                     int(r.get("replicate_idx", 0)))].append(r)
    painel_fa = {k: statistics.mean(x["factual_accuracy"] for x in v)
                 for k, v in por.items()}
    painel_comp = {k: statistics.mean(composto(x) for x in v) for k, v in por.items()}
    return novos, painel_fa, painel_comp, {k: len(v) for k, v in por.items()}


def acc_por_pais(usar_novos: bool):
    det, painel_fa, painel_comp, n_juizes = carregar_novos()
    rows = [json.loads(l) for l in SCORES.open(encoding="utf-8") if l.strip()]
    rows = [r for r in rows if "composite" in r and not r.get("error")
            and "JUDGE_API_ERROR" not in str(r.get("rationale", ""))]
    eng = [r for r in rows if "_AP_" in (r.get("prompt_id") or "")
           and not (r.get("prompt_id") or "").endswith(("_pt", "_es", "_hi"))]

    por_pais = collections.defaultdict(list)
    trocados = 0
    for r in eng:
        k = (r.get("prompt_id"), str(r.get("model_id")), int(r.get("replicate_idx", 0)))
        v = r["composite"]
        if usar_novos:
            if k in det:
                # substitui so a fatia factual do composto
                v = v - PESOS["factual_accuracy"] * r.get("factual_accuracy", 0) \
                      + PESOS["factual_accuracy"] * det[k]
                trocados += 1
            elif k in painel_comp:
                v = painel_comp[k]
                trocados += 1
        por_pais[r.get("country_iso3")].append(v)
    return ({c: statistics.mean(v) for c, v in por_pais.items() if v}, trocados,
            n_juizes)


def bloco(nome, acc, cov, gs):
    paises = [c for c in cov if c in acc]
    A = [acc[c] for c in paises]
    HDI = [cov[c][0] for c in paises]
    WIKI = [math.log(cov[c][1]) for c in paises]
    JOSHI = [cov[c][2] for c in paises]
    n = len(paises)
    r_hdi = spearman(A, HDI)
    r_jos = spearman(A, JOSHI)
    par = partial_spearman(A, WIKI, HDI)
    gn = [acc[c] for c in paises if c not in gs]
    gsv = [acc[c] for c in paises if c in gs]
    gap = (statistics.mean(gn) - statistics.mean(gsv)) * 100
    print(f"\n── {nome} (n={n}) ──")
    print(f"   H1 rho(acc, HDI)      = {r_hdi:+.3f}  p={p_from_r(r_hdi, n):.4f}")
    print(f"   H1 rho(acc, Joshi)    = {r_jos:+.3f}  p={p_from_r(r_jos, n):.4f}")
    print(f"   H4 parcial Wiki|HDI   = {par:+.3f}  p={p_from_r(par, n, partial=1):.4f}")
    print(f"   tier gap GN-GS        = {gap:+.2f} pp   (GN {statistics.mean(gn):.3f} · "
          f"GS {statistics.mean(gsv):.3f})")
    return {"n": n, "rho_hdi": r_hdi, "rho_joshi": r_jos, "partial_wiki_hdi": par,
            "tier_gap_pp": gap}


def main() -> None:
    cov = {**COV, **COV_EXT}
    gs = GS | GS_EXT

    antigo, _, _ = acc_por_pais(usar_novos=False)
    novo, trocados, n_juizes = acc_por_pais(usar_novos=True)

    dist = collections.Counter(n_juizes.values())
    print("CONGELAMENTO — composto corrigido contra o publicado")
    print(f"  celulas com escore substituido: {trocados}")
    print(f"  itens do painel por numero de juizes: {dict(sorted(dist.items()))}")

    a = bloco("PUBLICADO (juiz unico, gabarito placeholder em T2/T3/T4)", antigo, cov, gs)
    b = bloco("CORRIGIDO (codigo + media do painel)", novo, cov, gs)

    print("\n── DIFERENCA ──")
    for k, rot in (("rho_hdi", "H1 rho(HDI)"), ("rho_joshi", "H1 rho(Joshi)"),
                   ("partial_wiki_hdi", "H4 parcial"), ("tier_gap_pp", "tier gap (pp)")):
        print(f"   {rot:<16} {a[k]:+.3f} -> {b[k]:+.3f}   delta={b[k]-a[k]:+.3f}")

    maiores = sorted(((abs(novo[c] - antigo[c]), c, antigo[c], novo[c])
                      for c in novo if c in antigo), reverse=True)[:6]
    print("\n── paises que mais mudaram ──")
    for d, c, x, y in maiores:
        print(f"   {c}  {x:.3f} -> {y:.3f}   ({y-x:+.3f})")

    out = ROOT / "data" / "processed" / "freeze_comparison.json"
    out.write_text(json.dumps({"publicado": a, "corrigido": b,
                               "celulas_substituidas": trocados,
                               "acc_publicado": antigo, "acc_corrigido": novo},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  escrito: {out}")


if __name__ == "__main__":
    main()
