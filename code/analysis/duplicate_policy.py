#!/usr/bin/env python3
"""Qual resposta entra na analise quando a mesma celula tem varias.

O DEFEITO
De 9.760 chaves (prompt, modelo, replicata), 2.147 tem mais de uma resposta
armazenada, produzidas por re-execucoes em datas diferentes; 951 delas chegaram a
ser pontuadas mais de uma vez. O pipeline consome a PRIMEIRA em ordem alfabetica
de nome de arquivo. Isso e uma regra de sistema de arquivos, nao uma regra
analitica: renomear um arquivo mudaria um numero do artigo.

A CORRECAO
A regra passa a ser a MEDIA dos escores de todas as respostas armazenadas para a
mesma celula. Ela e deterministica, nao depende de ordem de leitura nem de
timestamp (que o arquivo de escores nao guarda), usa toda a informacao coletada
em vez de descartar parte dela, e e trivialmente reproduzivel por qualquer um.

Antes de trocar, porem, e preciso saber se a escolha importa. Este script mede os
efeitos sob quatro politicas. Se concordarem, a divida tecnica vira um teste de
sensibilidade publicavel; se divergirem, o artigo tem um problema maior do que
uma regra mal definida, e melhor descobrir agora.
"""
from __future__ import annotations

import collections
import json
import pathlib
import random
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.formal_tests import COV, COV_EXT, GS, GS_EXT, spearman, p_from_r  # noqa: E402
from code.analysis.nonparametric import wilcoxon_p  # noqa: E402

ANA = ROOT / "data" / "confirmatory_PRIVATE" / "analysis"
ORIG = ANA / "judge_scores_confirmatory.jsonl"
SAIDA = ROOT / "data" / "processed" / "duplicate_policy.json"
TODAS_COV = {**COV, **COV_EXT}
TODOS_GS = GS | GS_EXT
NATIVAS = ("_pt", "_es", "_hi")

POLITICAS = ("primeira", "ultima", "media", "aleatoria")


def carrega_por_politica(politica: str):
    """Uma linha por celula, escolhida segundo a politica."""
    por = collections.defaultdict(list)
    for linha in ORIG.open(encoding="utf-8"):
        if not linha.strip():
            continue
        r = json.loads(linha)
        if "composite" not in r or r.get("error"):
            continue
        if "JUDGE_API_ERROR" in str(r.get("rationale", "")):
            continue
        k = (r.get("prompt_id"), str(r.get("model_id")), r.get("replicate_idx"))
        por[k].append(r)

    rng = random.Random(20260823)
    saida = []
    for k, rs in por.items():
        if len(rs) == 1 or politica == "primeira":
            escolha = rs[0]
        elif politica == "ultima":
            escolha = rs[-1]
        elif politica == "aleatoria":
            escolha = rs[rng.randrange(len(rs))]
        else:  # media
            escolha = dict(rs[0])
            escolha["composite"] = statistics.mean(x["composite"] for x in rs)
        saida.append(escolha)
    return saida


def efeitos(rows):
    ing = [r for r in rows
           if "_AP_" in (r.get("prompt_id") or "")
           and not (r.get("prompt_id") or "").endswith(NATIVAS)]
    por_pais = collections.defaultdict(list)
    for r in ing:
        if r.get("country_iso3"):
            por_pais[r["country_iso3"]].append(r["composite"])
    acc = {c: statistics.mean(v) for c, v in por_pais.items() if v}
    gn = [acc[c] for c in acc if c in TODAS_COV and c not in TODOS_GS]
    gs = [acc[c] for c in acc if c in TODOS_GS]
    paises = sorted(c for c in acc if c in TODAS_COV)
    rho = spearman([acc[c] for c in paises], [TODAS_COV[c][0] for c in paises])

    # H2: pares casados, replicatas colapsadas
    med = collections.defaultdict(list)
    for r in rows:
        pid = r.get("prompt_id") or ""
        if "_AP_" in pid:
            med[(pid, str(r.get("model_id")))].append(r["composite"])
    m = {k: statistics.mean(v) for k, v in med.items()}
    inglês = {k: v for k, v in m.items() if not k[0].endswith(NATIVAS)}
    difs = [v - inglês[(k[0].rsplit("_", 1)[0], k[1])] for k, v in m.items()
            if k[0].endswith(NATIVAS) and (k[0].rsplit("_", 1)[0], k[1]) in inglês]

    piso = [r["composite"] for r in ing if r.get("task") in ("T1", "T2")]
    resto = [r["composite"] for r in ing if r.get("task") not in ("T1", "T2")]
    return {
        "n_celulas": len(rows),
        "tier_gap_pp": (statistics.mean(gn) - statistics.mean(gs)) * 100,
        "rho_hdi": rho,
        "p_hdi": p_from_r(rho, len(paises)),
        "nativa_pp": statistics.mean(difs) * 100 if difs else float("nan"),
        "nativa_p": wilcoxon_p(difs) if difs else float("nan"),
        "acc_piso": statistics.mean(piso),
        "acc_resto": statistics.mean(resto),
    }


def main() -> None:
    por = collections.Counter()
    for linha in ORIG.open(encoding="utf-8"):
        if linha.strip():
            r = json.loads(linha)
            por[(r.get("prompt_id"), str(r.get("model_id")), r.get("replicate_idx"))] += 1
    dup = sum(1 for v in por.values() if v > 1)
    print("POLITICA DE DESEMPATE ENTRE RESPOSTAS ARMAZENADAS")
    print(f"  celulas pontuadas: {len(por)} · com mais de um escore: {dup} "
          f"({dup/len(por):.1%})\n")

    res = {p: efeitos(carrega_por_politica(p)) for p in POLITICAS}
    campos = [("tier gap (pp)", "tier_gap_pp", "{:+7.2f}"),
              ("rho(acc, HDI)", "rho_hdi", "{:+7.3f}"),
              ("  p", "p_hdi", "{:7.3f}"),
              ("lingua nativa (pp)", "nativa_pp", "{:+7.2f}"),
              ("  p", "nativa_p", "{:7.1e}"),
              ("acuracia T1+T2", "acc_piso", "{:7.3f}"),
              ("acuracia demais", "acc_resto", "{:7.3f}")]
    print(f"  {'efeito':<20}" + "".join(f"{p:>10}" for p in POLITICAS))
    for nome, k, fmt in campos:
        print(f"  {nome:<20}" + "".join(f"{fmt.format(res[p][k]):>10}" for p in POLITICAS))

    espalha = max(abs(res[a]["tier_gap_pp"] - res[b]["tier_gap_pp"])
                  for a in POLITICAS for b in POLITICAS)
    espalha_h2 = max(abs(res[a]["nativa_pp"] - res[b]["nativa_pp"])
                     for a in POLITICAS for b in POLITICAS)
    print(f"\n  amplitude entre politicas: tier gap {espalha:.2f} pp · "
          f"lingua nativa {espalha_h2:.2f} pp")
    print("  A politica adotada passa a ser a MEDIA: deterministica, independente")
    print("  da ordem de leitura, e usa toda a informacao em vez de descartar parte.")

    SAIDA.write_text(json.dumps({"n_celulas": len(por), "n_duplicadas": dup,
                                 "politicas": res}, indent=2), encoding="utf-8")
    print(f"\n  escrito: {SAIDA}")


if __name__ == "__main__":
    main()
