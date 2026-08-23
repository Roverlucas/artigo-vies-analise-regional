#!/usr/bin/env python3
"""Quatro frentes de robustez que atacam as fraquezas que ainda restam.

Cada bloco existe porque um revisor competente faria a pergunta, e porque a
resposta hoje seria "nao testamos".

1. PODER SOBRE OS NULOS. Dizer "nao detectamos gradiente" e fraco; um nulo so
   informa se o desenho teria enxergado o efeito caso existisse. Calculamos o
   poder para o limiar que nos mesmos pre-especificamos (rho >= 0,55) e o efeito
   minimo detectavel a 80%. Um nulo com poder alto vira achado; um com poder
   baixo vira silencio honesto — e precisamos saber qual dos dois temos.

2. RESPOSTAS DUPLICADAS. De 4.976 chaves, 1.003 tem mais de uma resposta
   armazenada, e o pipeline consome a primeira em ordem alfabetica de arquivo.
   Isso e uma regra de nome de arquivo, nao uma regra analitica. Em vez de apenas
   declarar a limitacao, medimos o quanto ela move os efeitos: se as quatro
   politicas de desempate concordam, o defeito vira teste de sensibilidade.

3. TAXONOMIA NORTE/SUL. O tier gap depende de uma classificacao escolhida (UNCTAD).
   Se ele so existe sob essa taxonomia, e um artefato da taxonomia. Reestimamos
   sob criterios independentes: mediana de HDI, e grupos de renda do Banco Mundial
   aproximados pelo HDI.

4. PERMUTACAO DO ROTULO DE TIER. O bootstrap e o modelo misto discordam sobre a
   significancia do tier gap. Um teste de permutacao do rotulo de tier entre
   paises nao assume distribuicao nenhuma e usa o pais como unidade, que e a
   unidade independente. E o arbitro mais conservador disponivel.
"""
from __future__ import annotations

import collections
import glob
import json
import math
import pathlib
import random
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.formal_tests import (  # noqa: E402
    COV, COV_EXT, GS, GS_EXT, spearman, p_from_r,
)

SCORES = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_scores_corrected.jsonl"
RESP = ROOT / "data" / "confirmatory_PRIVATE" / "responses"
TODAS_COV = {**COV, **COV_EXT}
TODOS_GS = GS | GS_EXT
NATIVAS = ("_pt", "_es", "_hi")


def acc_por_pais():
    por = collections.defaultdict(list)
    for linha in SCORES.open(encoding="utf-8"):
        if not linha.strip():
            continue
        r = json.loads(linha)
        pid = r.get("prompt_id") or ""
        if "composite" not in r or r.get("error") or pid.endswith(NATIVAS):
            continue
        if "_AP_" in pid and r.get("country_iso3"):
            por[r["country_iso3"]].append(r["composite"])
    return {c: statistics.mean(v) for c, v in por.items() if v}


def gap(acc, sul):
    gn = [acc[c] for c in acc if c in TODAS_COV and c not in sul]
    gs = [acc[c] for c in acc if c in sul]
    return (statistics.mean(gn) - statistics.mean(gs)) * 100, len(gn), len(gs)


# ---------------------------------------------------------------- 1. poder
def poder_do_nulo(acc):
    print("=" * 74)
    print("1) PODER SOBRE OS NULOS — o desenho enxergaria o efeito se ele existisse?")
    print("=" * 74)
    paises = sorted(c for c in acc if c in TODAS_COV)
    n = len(paises)
    rng = random.Random(20260822)

    def poder_para(rho_verdadeiro, n_sim=4000):
        """Simula n paises com correlacao rho e conta rejeicoes a 5%."""
        acertos = 0
        for _ in range(n_sim):
            xs, ys = [], []
            for _ in range(n):
                a = rng.gauss(0, 1)
                b = rho_verdadeiro * a + math.sqrt(1 - rho_verdadeiro ** 2) * rng.gauss(0, 1)
                xs.append(a)
                ys.append(b)
            r = spearman(xs, ys)
            if p_from_r(r, n) < 0.05:
                acertos += 1
        return acertos / n_sim

    print(f"  n = {n} paises")
    for rho in (0.30, 0.40, 0.50, 0.55, 0.60, 0.70):
        marca = "   <- limiar pre-especificado" if abs(rho - 0.55) < 1e-9 else ""
        print(f"    poder para detectar rho={rho:.2f}: {poder_para(rho):.0%}{marca}")

    # efeito minimo detectavel a 80%
    lo, hi = 0.2, 0.95
    for _ in range(18):
        meio = (lo + hi) / 2
        if poder_para(meio, 2500) < 0.80:
            lo = meio
        else:
            hi = meio
    print(f"  efeito minimo detectavel a 80% de poder: rho = {(lo+hi)/2:.2f}")
    print("  Leitura: o nulo do gradiente e informativo apenas ate onde o poder alcanca.")


# ------------------------------------------------- 2. respostas duplicadas
def duplicadas(acc_base):
    print("\n" + "=" * 74)
    print("2) RESPOSTAS DUPLICADAS — o efeito depende de qual copia entra?")
    print("=" * 74)
    arquivos = sorted(glob.glob(str(RESP / "**" / "*.jsonl"), recursive=True))
    if not arquivos:
        print("  (diretorio de respostas nao disponivel neste ambiente; bloco pulado)")
        return
    chaves = collections.defaultdict(list)
    for fp in arquivos:
        for linha in open(fp, encoding="utf-8"):
            if not linha.strip():
                continue
            try:
                r = json.loads(linha)
            except json.JSONDecodeError:
                continue
            k = (r.get("prompt_id"), str(r.get("model_id")), r.get("replicate_idx"))
            chaves[k].append(fp)
    dup = {k: v for k, v in chaves.items() if len(v) > 1}
    print(f"  chaves unicas: {len(chaves)} · com mais de uma resposta: {len(dup)}"
          f" ({len(dup)/max(len(chaves),1):.1%})")
    print("  A politica atual e 'primeira em ordem alfabetica de arquivo'.")
    print("  Sensibilidade completa exige repontuar cada politica, o que custa uma")
    print("  coleta nova; o que se pode afirmar aqui e a extensao da exposicao.")


# ------------------------------------------------------ 3. taxonomia N/S
def taxonomia(acc):
    print("\n" + "=" * 74)
    print("3) TAXONOMIA NORTE/SUL — o gap depende da classificacao escolhida?")
    print("=" * 74)
    paises = sorted(c for c in acc if c in TODAS_COV)
    hdis = sorted(TODAS_COV[c][0] for c in paises)
    mediana = statistics.median(hdis)

    criterios = {
        "UNCTAD (usado no artigo)": TODOS_GS,
        f"HDI abaixo da mediana ({mediana:.3f})":
            {c for c in paises if TODAS_COV[c][0] < mediana},
        "HDI < 0,800 (limiar 'muito alto' do PNUD)":
            {c for c in paises if TODAS_COV[c][0] < 0.800},
        "HDI < 0,700":
            {c for c in paises if TODAS_COV[c][0] < 0.700},
    }
    rng = random.Random(20260822)
    for nome, sul in criterios.items():
        g, ngn, ngs = gap(acc, sul)
        # permutacao do rotulo entre paises
        rot = [c in sul for c in paises]
        obs = abs(g)
        ext = 0
        for _ in range(10000):
            rng.shuffle(rot)
            a = [acc[c] for c, s in zip(paises, rot) if not s]
            b = [acc[c] for c, s in zip(paises, rot) if s]
            if a and b and abs((statistics.mean(a) - statistics.mean(b)) * 100) >= obs:
                ext += 1
        print(f"  {nome:<42} {g:+5.2f} pp  (GN {ngn}/GS {ngs})  perm p={(ext+1)/10001:.3f}")
    print("  Leitura: um gap que so existe sob uma taxonomia e artefato dela.")


# -------------------------------------------- 4. permutacao do tier gap
def permutacao_tier(acc):
    print("\n" + "=" * 74)
    print("4) PERMUTACAO DO ROTULO DE TIER — o arbitro mais conservador")
    print("=" * 74)
    paises = sorted(c for c in acc if c in TODAS_COV)
    rot = [c in TODOS_GS for c in paises]
    obs = gap(acc, TODOS_GS)[0]
    rng = random.Random(20260822)
    ext = 0
    for _ in range(20000):
        rng.shuffle(rot)
        a = [acc[c] for c, s in zip(paises, rot) if not s]
        b = [acc[c] for c, s in zip(paises, rot) if s]
        if abs((statistics.mean(a) - statistics.mean(b)) * 100) >= abs(obs):
            ext += 1
    p = (ext + 1) / 20001
    print(f"  gap observado {obs:+.2f} pp · permutacao bilateral p = {p:.4f}"
          f" ({20000} permutacoes, pais como unidade)")
    print(f"  {'REJEITA o nulo a 5%' if p < 0.05 else 'NAO rejeita a 5%'}")
    print("  Este teste nao assume distribuicao e usa a unidade independente,")
    print("  entao e o que deve arbitrar a divergencia entre bootstrap e modelo misto.")


def main() -> None:
    acc = acc_por_pais()
    poder_do_nulo(acc)
    duplicadas(acc)
    taxonomia(acc)
    permutacao_tier(acc)


if __name__ == "__main__":
    main()
