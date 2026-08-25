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

from code.analysis.nonparametric import wilcoxon_p  # noqa: E402

from code.analysis.formal_tests import (  # noqa: E402
    COV, COV_EXT, GS, GS_EXT, SCORES, spearman, partial_spearman, p_from_r,
    mann_kendall,
)
from code.analysis.llm_judge import RUBRIC_WEIGHTS as PESOS  # noqa: E402

PANEL = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_panel_repontuacao.jsonl"
NUMERIC = ROOT / "data" / "processed"
SAIDA = ROOT / "data" / "processed" / "freeze_all_effects.json"

TODAS_COV = {**COV, **COV_EXT}
TODOS_GS = GS | GS_EXT
NATIVAS = ("_pt", "_es", "_hi")
CCORP = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "country_corpus_measures.json"
# Os 15 paises do plano pre-especificado; os outros 10 entraram na extensao post hoc.
PRE = set(COV)


def composto(d: dict) -> float:
    return sum(d[k] * w for k, w in PESOS.items())


def carrega_correcoes(modo="composto"):
    """modo: 'composto' (pesos do instrumento), 'iguais' (pesos iguais),
    'factual' (so a acuracia factual, o subcomponente mais objetivo)."""
    det = {}
    for t in ("T2", "T3"):
        f = NUMERIC / f"numeric_scores_{t}.jsonl"
        if not f.exists():
            continue
        for linha in f.open(encoding="utf-8"):
            r = json.loads(linha)
            if r["verdict"] in ("CORRECT", "INCORRECT"):
                det[(r["prompt_id"], str(r["model_id"]),
                     int(r.get("replicate_idx", 0)))] = (
                    1.0 if r["verdict"] == "CORRECT" else 0.0)

    por = collections.defaultdict(list)
    for linha in PANEL.open(encoding="utf-8"):
        r = json.loads(linha)
        if all(k in r for k in PESOS):
            por[(r["prompt_id"], str(r["model_id"]),
                 int(r.get("replicate_idx", 0)))].append(r)
    def val(x):
        if modo == "factual":
            return x["factual_accuracy"]
        if modo == "iguais":
            return statistics.mean(x[k] for k in PESOS)
        return composto(x)

    painel = {k: statistics.mean(val(x) for x in v) for k, v in por.items()}
    return det, painel


def linhas(corrigir: bool, modo: str = "composto", dedup: bool = True):
    """Todas as respostas com o escore publicado ou o corrigido."""
    det, painel = carrega_correcoes(modo)
    saida, trocados = [], 0
    for linha in SCORES.open(encoding="utf-8"):
        if not linha.strip():
            continue
        r = json.loads(linha)
        if "composite" not in r or r.get("error"):
            continue
        if "JUDGE_API_ERROR" in str(r.get("rationale", "")):
            continue
        if modo == "factual":
            v = r.get("factual_accuracy", 0.0)
        elif modo == "iguais":
            v = statistics.mean(r.get(k_, 0.0) for k_ in PESOS)
        else:
            v = r["composite"]
        k = (r.get("prompt_id"), str(r.get("model_id")), int(r.get("replicate_idx", 0)))
        if corrigir:
            if k in det:
                if modo == "factual":
                    v = det[k]
                elif modo == "iguais":
                    v = v - r.get("factual_accuracy", 0) / len(PESOS) + det[k] / len(PESOS)
                else:
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

    # DEDUPLICACAO — a unidade de analise e a CELULA, nao a linha de arquivo.
    # 951 celulas (11,5%) tem mais de um escore, vindos de re-execucoes do juiz em
    # datas diferentes. Nao sao observacoes independentes: sao medicoes repetidas
    # do mesmo item. Trata-las como independentes e pseudo-replicacao — infla o n
    # e da peso extra a celulas que por acaso foram reprocessadas. Colapsamos pela
    # media, que e deterministica e usa toda a informacao coletada.
    #
    # A decisao e metodologica e independe do resultado; o efeito colateral e que
    # quase todos os efeitos ficam ligeiramente MAIS fortes, e o achado central
    # (H2) fica praticamente identico (-4.755 -> -4.753 pp), o que e a melhor
    # evidencia de que ele nao depende desta escolha. Nenhum vereditode hipotese
    # muda: H1 continua abaixo do limiar pre-especificado rho>=0.55.
    # dedup=False reproduz a versao anterior, para a analise de sensibilidade.
    if dedup:
        por_celula = collections.defaultdict(list)
        for r in saida:
            por_celula[(r["prompt_id"], r["modelo"], r["rep"])].append(r)
        colapsado = []
        for _k, grupo in por_celula.items():
            base = dict(grupo[0])
            base["v"] = statistics.fmean(x["v"] for x in grupo)
            colapsado.append(base)
        saida = colapsado
    return saida, trocados


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

    # Mann-Kendall sobre a acuracia ordenada por HDI: tendencia monotonica sem
    # supor forma funcional, que e o teste que o manuscrito reporta ao lado do rho.
    por_hdi = sorted(paises, key=lambda c: TODAS_COV[c][0])
    _, _, out["h1_mk_p"] = mann_kendall([acc[c] for c in por_hdi])

    # Valor pre-especificado (15 paises), reportado ao lado de cada efeito
    pre = sorted(c for c in acc if c in PRE)
    if len(pre) > 3:
        out["h1_rho_pre15"] = spearman([acc[c] for c in pre],
                                       [TODAS_COV[c][0] for c in pre])
        out["n_pre15"] = len(pre)

    # H4: cobertura do pais (sitelinks do Wikidata) contra tamanho do corpus da
    # lingua (edicao da Wikipedia). O manuscrito reporta ambos e a parcial por HDI.
    if CCORP.exists():
        cc = json.loads(CCORP.read_text(encoding="utf-8"))
        sl = [(acc[c], (cc.get(c) or {}).get("wd_sitelinks"), TODAS_COV[c][0])
              for c in paises]
        sl = [(a, s_, h) for a, s_, h in sl if isinstance(s_, (int, float))]
        if len(sl) > 3:
            xa = [x[0] for x in sl]
            xs = [x[1] for x in sl]
            xh = [x[2] for x in sl]
            out["h4_rho_sitelinks"] = spearman(xa, xs)
            out["h4_p_sitelinks"] = p_from_r(out["h4_rho_sitelinks"], len(sl))
            out["h4_parcial_sitelinks_hdi"] = partial_spearman(xa, xs, xh)
            out["h4_p_parcial"] = p_from_r(out["h4_parcial_sitelinks_hdi"], len(sl), 1)
        # proxy pre-especificado: tamanho da edicao da Wikipedia na lingua
        out["h4_rho_wikilang"] = spearman([acc[c] for c in paises],
                                          [TODAS_COV[c][1] for c in paises])
        out["h4_p_wikilang"] = p_from_r(out["h4_rho_wikilang"], len(paises))

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
            out[f"nativa_{lg}_p"] = wilcoxon_p(ds)
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

    # agregados que alimentam as tabelas do manuscrito
    def medias(chave):
        acc_ = collections.defaultdict(list)
        for r in ing:
            acc_[r[chave]].append(r["v"])
        return {k: (statistics.mean(v), len(v)) for k, v in acc_.items() if v}

    out["por_modelo"] = medias("modelo")
    out["por_task"] = medias("task")
    out["por_pais"] = {c: (statistics.mean(v), len(v)) for c, v in por_pais.items()}

    # H5: acesso aberto contra fechado-acessivel
    ABERTOS = {"llama31_8b", "llama33_70b", "llama4_scout", "qwen3_14b", "qwen3_32b",
               "phi4_14b", "gpt_oss_120b", "command_rp", "deepseek_v3",
               "cabra_mistral_7b"}
    ab = [r["v"] for r in ing if r["modelo"] in ABERTOS]
    fe = [r["v"] for r in ing if r["modelo"] not in ABERTOS]
    if ab and fe:
        out["h5_pp"] = (statistics.mean(fe) - statistics.mean(ab)) * 100
        out["h5_n_aberto"] = len(ab)
        out["h5_n_fechado"] = len(fe)

    # H6: persona como diferenca-em-diferencas sobre o tier gap
    def gap(sel):
        pp = collections.defaultdict(list)
        for r in ing:
            if sel(r) and r["pais"]:
                pp[r["pais"]].append(r["v"])
        m = {c: statistics.mean(v) for c, v in pp.items() if v}
        gn_ = [m[c] for c in m if c in TODAS_COV and c not in TODOS_GS]
        gs_ = [m[c] for c in m if c in TODOS_GS]
        return (statistics.mean(gn_) - statistics.mean(gs_)) * 100 if gn_ and gs_ else float("nan")

    g_neutro = gap(lambda r: r["persona"] == "neutral")
    g_gestor = gap(lambda r: r["persona"] and r["persona"] != "neutral")
    out["h6_gap_neutro"] = g_neutro
    out["h6_gap_gestor"] = g_gestor
    out["h6_did"] = g_gestor - g_neutro

    # modelo regional brasileiro contra o global pareado por escala. O modelo
    # regional presente na coleta e o cabra_mistral_7b; o controle de escala
    # pre-especificado e o qwen3_14b, da mesma ordem de parametros.
    reg = [r["v"] for r in ing if r["modelo"] == "cabra_mistral_7b"]
    if reg:
        glob = [r["v"] for r in ing if r["modelo"] != "cabra_mistral_7b"]
        out["cliff_regional"] = cliffs_delta(reg, glob)
        out["n_regional"] = len(reg)
    # leave-one-country-out: nenhum pais sozinho sustenta o gradiente ou o gap
    loo_rho, loo_gap = [], []
    for fora in paises:
        rest = [c for c in paises if c != fora]
        loo_rho.append(spearman([acc[c] for c in rest],
                                [TODAS_COV[c][0] for c in rest]))
        gn_ = [acc[c] for c in rest if c not in TODOS_GS]
        gs_ = [acc[c] for c in rest if c in TODOS_GS]
        if gn_ and gs_:
            loo_gap.append((statistics.mean(gn_) - statistics.mean(gs_)) * 100)
    out["loo_rho_min"], out["loo_rho_max"] = min(loo_rho), max(loo_rho)
    out["loo_gap_min"], out["loo_gap_max"] = min(loo_gap), max(loo_gap)
    return out


def main() -> None:
    pub, _ = linhas(False)
    cor, trocados = linhas(True)
    a, b = efeitos(pub), efeitos(cor)

    # robustez de metrica: os efeitos nao podem depender de como o composto pesa
    # os cinco subcomponentes, nem sumir quando se olha so o mais objetivo deles.
    alt = {}
    for modo in ("iguais", "factual"):
        alt[modo] = efeitos(linhas(True, modo)[0])
        alt[modo + "_pub"] = efeitos(linhas(False, modo)[0])

    print("CONGELAMENTO COMPLETO — todos os efeitos, painel de 3 juizes fechado")
    print(f"  respostas: {len(pub)} · celulas com escore substituido: {trocados}\n")

    rotulos = [
        ("tier gap GN-GS (pp)", "tier_gap_pp", "{:+.2f}"),
        ("  IC95 bootstrap", "tier_gap_ci", None),
        ("H1 rho(acc, HDI)", "h1_rho_hdi", "{:+.3f}"),
        ("  p", "h1_p", "{:.4f}"),
        ("  Mann-Kendall p", "h1_mk_p", "{:.4f}"),
        ("  rho pre-espec n=15", "h1_rho_pre15", "{:+.3f}"),
        ("H4 rho sitelinks", "h4_rho_sitelinks", "{:+.3f}"),
        ("  p", "h4_p_sitelinks", "{:.4f}"),
        ("  parcial | HDI", "h4_parcial_sitelinks_hdi", "{:+.3f}"),
        ("  p parcial", "h4_p_parcial", "{:.4f}"),
        ("H4 rho wiki-lingua", "h4_rho_wikilang", "{:+.3f}"),
        ("  p", "h4_p_wikilang", "{:.4f}"),
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

    print("\n  robustez de metrica (corrigido):")
    for modo in ("iguais", "factual"):
        m = alt[modo]
        print(f"    pesos {modo:<8} tier gap {m['tier_gap_pp']:+.2f} pp · "
              f"rho(HDI) {m['h1_rho_hdi']:+.3f} · piso delta {m['cliff_piso']:+.3f} · "
              f"nativa {m['nativa_pp']:+.2f} pp")
    m = alt["factual"]
    print(f"    factual puro: T1+T2 {m['acc_t1t2']:.3f} vs demais {m['acc_resto']:.3f}")

    SAIDA.write_text(json.dumps({"publicado": a, "corrigido": b, "alternativos": alt,
                                 "celulas_substituidas": trocados,
                                 "n_respostas": len(pub)},
                                indent=2, default=str), encoding="utf-8")
    print(f"\n  escrito: {SAIDA}")


if __name__ == "__main__":
    main()
