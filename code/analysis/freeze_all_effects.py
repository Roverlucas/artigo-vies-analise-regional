#!/usr/bin/env python3
"""Congelamento completo: TODOS os efeitos publicados, recomputados com o gabarito corrigido.

Por que este script existe separado de `freeze_recompute.py`: aquele compara H1,
H4 e o tier gap, que sao os efeitos definidos sobre a media por pais. O manuscrito
afirma tambem efeitos definidos sobre a resposta individual — lingua nativa, piso
por tarefa, modelo regional, persona — e uma correcao de gabarito que move H1 pode
mover esses tambem. Fechar so os tres primeiros deixaria o resto do artigo apoiado
em numeros que ninguem recomputou.

REGRA DE SUBSTITUICAO (identica a do freeze_recompute, de proposito)
--------------------------------------------------------------------
1. T2/T3 com veredito deterministico: troca-se APENAS a fatia factual do composto.
   Comparar numero com faixa e exato; o juiz, no melhor caso, reproduz isso com ruido.
2. Resíduo de T2/T3 e T4 inteira: media do painel multi-fornecedor.
3. T1 e T5 entram intactas. T1 sempre teve gabarito oficial e T5 e rubrica, entao a
   diferenca observada vem da correcao do gabarito e nao de um instrumento novo.
"""
from __future__ import annotations

import collections
import json
import math
import pathlib
import random
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.formal_tests import (  # noqa: E402
    COV, COV_EXT, GS, GS_EXT, SCORES, spearman, p_from_r,
)
from code.analysis.llm_judge import RUBRIC_WEIGHTS as PESOS  # noqa: E402

PANEL = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_panel_repontuacao.jsonl"
NUMERIC = ROOT / "data" / "processed"
SAIDA = ROOT / "data" / "processed" / "freeze_all_effects.json"

TODAS_COV = {**COV, **COV_EXT}
TODOS_GS = GS | GS_EXT
NATIVAS = ("_pt", "_es", "_hi")


def composto(d: dict) -> float:
    return sum(d[k] * w for k, w in PESOS.items())


def carrega_correcoes():
    det = {}
    for t in ("T2", "T3"):
        f = NUMERIC / f"numeric_scores_{t}.jsonl"
        if not f.exists():
            continue
        for linha in f.open(encoding="utf-8"):
            r = json.loads(linha)
            if r["verdict"] in ("CORRECT", "INCORRECT"):
                det[(r["prompt_id"], str(r["model_id"]), 0)] = (
                    1.0 if r["verdict"] == "CORRECT" else 0.0)

    por = collections.defaultdict(list)
    for linha in PANEL.open(encoding="utf-8"):
        r = json.loads(linha)
        if all(k in r for k in PESOS):
            por[(r["prompt_id"], str(r["model_id"]),
                 int(r.get("replicate_idx", 0)))].append(r)
    painel = {k: statistics.mean(composto(x) for x in v) for k, v in por.items()}
    return det, painel


def linhas(corrigir: bool):
    """Todas as respostas com o escore publicado ou o corrigido."""
    det, painel = carrega_correcoes()
    saida, trocados = [], 0
    for linha in SCORES.open(encoding="utf-8"):
        if not linha.strip():
            continue
        r = json.loads(linha)
        if "composite" not in r or r.get("error"):
            continue
        if "JUDGE_API_ERROR" in str(r.get("rationale", "")):
            continue
        v = r["composite"]
        k = (r.get("prompt_id"), str(r.get("model_id")), int(r.get("replicate_idx", 0)))
        if corrigir:
            if k in det:
                v = (v - PESOS["factual_accuracy"] * r.get("factual_accuracy", 0)
                     + PESOS["factual_accuracy"] * det[k])
                trocados += 1
            elif k in painel:
                v = painel[k]
                trocados += 1
        pid = r.get("prompt_id") or ""
        saida.append({"v": v, "pais": r.get("country_iso3"), "task": r.get("task"),
                      "modelo": str(r.get("model_id")), "persona": r.get("persona"),
                      "prompt_id": pid, "rep": int(r.get("replicate_idx", 0)),
                      "nativa": pid.endswith(NATIVAS)})
    return saida, trocados


def wilcoxon_p(difs):
    """Wilcoxon signed-rank bilateral, aproximacao normal com correcao de empates."""
    nz = [d for d in difs if d != 0]
    n = len(nz)
    if n < 10:
        return float("nan")
    ordenado = sorted(nz, key=abs)
    postos, i = [0.0] * n, 0
    while i < n:
        j = i
        while j + 1 < n and abs(ordenado[j + 1]) == abs(ordenado[i]):
            j += 1
        medio = (i + j) / 2 + 1
        for k in range(i, j + 1):
            postos[k] = medio
        i = j + 1
    mais = sum(p for p, d in zip(postos, ordenado) if d > 0)
    media = n * (n + 1) / 4
    dp = math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    z = (mais - media) / dp
    return math.erfc(abs(z) / math.sqrt(2))


def cliffs_delta(a, b):
    if not a or not b:
        return float("nan")
    maior = menor = 0
    for x in a:
        for y in b:
            if x > y:
                maior += 1
            elif x < y:
                menor += 1
    return (maior - menor) / (len(a) * len(b))


def boot_ci(a, b, n=10000, semente=20260822):
    """IC bootstrap percentil da diferenca de medias, em pontos percentuais."""
    rng = random.Random(semente)
    difs = []
    for _ in range(n):
        ra = [a[rng.randrange(len(a))] for _ in range(len(a))]
        rb = [b[rng.randrange(len(b))] for _ in range(len(b))]
        difs.append((statistics.mean(ra) - statistics.mean(rb)) * 100)
    difs.sort()
    return difs[int(0.025 * n)], difs[int(0.975 * n)]


def perm_p(a, b, n=10000, semente=20260822):
    rng = random.Random(semente)
    obs = abs(statistics.mean(a) - statistics.mean(b))
    junto = a + b
    extremos = 0
    for _ in range(n):
        rng.shuffle(junto)
        if abs(statistics.mean(junto[:len(a)]) - statistics.mean(junto[len(a):])) >= obs:
            extremos += 1
    return (extremos + 1) / (n + 1)


def efeitos(rows):
    ing = [r for r in rows if not r["nativa"] and "_AP_" in r["prompt_id"]]
    out = {}

    # tier gap Norte/Sul, sobre a media por pais (como no manuscrito)
    por_pais = collections.defaultdict(list)
    for r in ing:
        if r["pais"]:
            por_pais[r["pais"]].append(r["v"])
    acc = {c: statistics.mean(v) for c, v in por_pais.items() if v}
    gn = [acc[c] for c in acc if c in TODAS_COV and c not in TODOS_GS]
    gs = [acc[c] for c in acc if c in TODOS_GS]
    out["tier_gap_pp"] = (statistics.mean(gn) - statistics.mean(gs)) * 100
    out["tier_gap_ci"] = boot_ci(gn, gs)
    out["acc_gn"] = statistics.mean(gn)
    out["acc_gs"] = statistics.mean(gs)

    # H1: gradiente de desenvolvimento. COV mapeia pais -> (HDI, Wiki, Joshi).
    paises = sorted(c for c in acc if c in TODAS_COV)
    out["h1_rho_hdi"] = spearman([acc[c] for c in paises],
                                 [TODAS_COV[c][0] for c in paises])
    out["h1_p"] = p_from_r(out["h1_rho_hdi"], len(paises))
    out["n_paises"] = len(paises)

    # H2: lingua nativa contra o ingles em celulas CASADAS (modelo, prompt,
    # replicata), como no manuscrito — nao diferenca de medias marginais. O
    # pareamento e o que da o teste: sem ele, variacao entre modelos e entre itens
    # entra no erro e o efeito some no ruido.
    # As replicatas sao COLAPSADAS por celula (prompt, modelo) antes de parear.
    # Parear replicata a replicata infla o n por um fator igual ao numero de
    # replicatas e torna o Wilcoxon anticonservador — a mesma pseudo-replicacao
    # ja criticada em H3/H5. A celula e a unidade; a replicata e ruido interno.
    def media_por_celula(rs):
        acc = collections.defaultdict(list)
        for r in rs:
            acc[(r["prompt_id"], r["modelo"])].append(r["v"])
        return {k: statistics.mean(v) for k, v in acc.items()}

    ing_idx = media_por_celula(ing)
    nat_idx = media_por_celula([r for r in rows if r["nativa"]])
    pares, pares_por_lingua = [], collections.defaultdict(list)
    for (pid, modelo), v in nat_idx.items():
        base, lingua = pid.rsplit("_", 1)
        k = (base, modelo)
        if k in ing_idx:
            d = v - ing_idx[k]
            pares.append(d)
            pares_por_lingua[lingua].append(d)
    if pares:
        out["nativa_pp"] = statistics.mean(pares) * 100
        out["nativa_p"] = wilcoxon_p(pares)
        out["n_pares"] = len(pares)
        for lg, ds in pares_por_lingua.items():
            out[f"nativa_{lg}_pp"] = statistics.mean(ds) * 100
            out[f"n_pares_{lg}"] = len(ds)
        if "hi" in pares_por_lingua:
            out["hindi_pp"] = statistics.mean(pares_por_lingua["hi"]) * 100

    # piso por tarefa: T1/T2 contra as demais
    piso = [r["v"] for r in ing if r["task"] in ("T1", "T2")]
    resto = [r["v"] for r in ing if r["task"] not in ("T1", "T2")]
    out["acc_t1t2"] = statistics.mean(piso) if piso else float("nan")
    out["acc_resto"] = statistics.mean(resto) if resto else float("nan")
    out["cliff_piso"] = cliffs_delta(piso, resto)

    # persona
    pm = [r["v"] for r in ing if r["persona"] and r["persona"] != "neutral"]
    ne = [r["v"] for r in ing if r["persona"] == "neutral"]
    if pm and ne:
        out["persona_pp"] = (statistics.mean(pm) - statistics.mean(ne)) * 100
        out["persona_p"] = perm_p(pm, ne)

    # modelo regional brasileiro contra o global pareado por escala. O modelo
    # regional presente na coleta e o cabra_mistral_7b; o controle de escala
    # pre-especificado e o qwen3_14b, da mesma ordem de parametros.
    reg = [r["v"] for r in ing if r["modelo"] == "cabra_mistral_7b"]
    if reg:
        glob = [r["v"] for r in ing if r["modelo"] != "cabra_mistral_7b"]
        out["cliff_regional"] = cliffs_delta(reg, glob)
        out["n_regional"] = len(reg)
    return out


def main() -> None:
    pub, _ = linhas(False)
    cor, trocados = linhas(True)
    a, b = efeitos(pub), efeitos(cor)

    print("CONGELAMENTO COMPLETO — todos os efeitos, painel de 3 juizes fechado")
    print(f"  respostas: {len(pub)} · celulas com escore substituido: {trocados}\n")

    rotulos = [
        ("tier gap GN-GS (pp)", "tier_gap_pp", "{:+.2f}"),
        ("  IC95 bootstrap", "tier_gap_ci", None),
        ("H1 rho(acc, HDI)", "h1_rho_hdi", "{:+.3f}"),
        ("  p", "h1_p", "{:.4f}"),
        ("lingua nativa (pp)", "nativa_pp", "{:+.2f}"),
        ("  p Wilcoxon", "nativa_p", "{:.5f}"),
        ("  n pares", "n_pares", "{:.0f}"),
        ("  espanhol (pp)", "nativa_es_pp", "{:+.2f}"),
        ("  portugues (pp)", "nativa_pt_pp", "{:+.2f}"),
        ("  hindi (pp)", "nativa_hi_pp", "{:+.2f}"),
        ("acuracia T1+T2", "acc_t1t2", "{:.3f}"),
        ("acuracia demais", "acc_resto", "{:.3f}"),
        ("Cliff delta piso", "cliff_piso", "{:+.3f}"),
        ("persona (pp)", "persona_pp", "{:+.2f}"),
        ("  p permutacao", "persona_p", "{:.4f}"),
        ("Cliff delta regional", "cliff_regional", "{:+.3f}"),
        ("  n regional", "n_regional", "{:.0f}"),
    ]
    print(f"  {'efeito':<24} {'publicado':>16} {'corrigido':>16}   delta")
    for nome, ch, fmt in rotulos:
        if ch not in a and ch not in b:
            continue
        va, vb = a.get(ch), b.get(ch)
        if fmt is None:
            sa = f"[{va[0]:+.2f},{va[1]:+.2f}]" if va else "-"
            sb = f"[{vb[0]:+.2f},{vb[1]:+.2f}]" if vb else "-"
            print(f"  {nome:<24} {sa:>16} {sb:>16}")
            continue
        num = (int, float)
        sa = fmt.format(va) if isinstance(va, num) else "-"
        sb = fmt.format(vb) if isinstance(vb, num) else "-"
        d = (f"{vb - va:+.3f}" if isinstance(va, num) and isinstance(vb, num)
             and fmt != "{:.0f}" else "")
        print(f"  {nome:<24} {sa:>16} {sb:>16}   {d}")

    SAIDA.write_text(json.dumps({"publicado": a, "corrigido": b,
                                 "celulas_substituidas": trocados,
                                 "n_respostas": len(pub)},
                                indent=2, default=str), encoding="utf-8")
    print(f"\n  escrito: {SAIDA}")


if __name__ == "__main__":
    main()
