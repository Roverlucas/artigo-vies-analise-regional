#!/usr/bin/env python3
"""cluster_inference.py — inferência no nível do cluster (parecer de painel, 2026-09-21).

A objeção comum a vários itens do parecer: testes rodados sobre 6.573 respostas
tratam como independentes observações aninhadas em 25 países e 14 modelos. Aqui
cada efeito do manuscrito que ainda dependia de um teste no nível da resposta
ganha a versão cujo n é o número de clusters:

  A. H4 dentro do país: a interação cobertura×dependência com erro-padrão
     robusto por cluster de país (OLS com efeitos fixos de país e modelo), sozinha,
     com HDI×dependência, e só nos anglófonos.
  B. ORs por tarefa (Tabela 5): IC bootstrap por país (10k) do OR bruto e
     p de permutação do rótulo de tier com o país como unidade.
  C. Tier gap com a UE como um único cluster (DEU, FRA, ITA, PRT → uma unidade).
  D. Tier gap no subconjunto balanceado de prompts (só prompts respondidos por
     todos os 14 modelos).
  E. H6: efeito principal da persona e TOST do DiD a ±2 pp e ±5 pp, bootstrap por país.
  F. Piso de recall e H3 com o modelo/país como unidade.
  G. IC de Fisher para ρ(acurácia, HDI) em n=25 e n=15.
  H. Respostas vazias por idioma em T1–T3 (não houve exclusão por idioma).

Saída: data/processed/cluster_inference.json
"""
from __future__ import annotations
import collections, json, math, os, random, statistics as st, sys
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from code.analysis.formal_tests import COV, COV_EXT  # noqa: E402
from code.analysis.nonparametric import wilcoxon_p  # noqa: E402

ANA = os.path.join(ROOT, "data/confirmatory_PRIVATE/analysis")
GN = {"USA", "DEU", "JPN", "UK", "CAN", "AUS", "KOR", "FRA", "ITA", "PRT"}
EU = {"DEU", "FRA", "ITA", "PRT"}
PRE15 = {"BRA", "MEX", "ARG", "PER", "NGA", "ZAF", "KEN", "EGY", "IND", "IDN", "BGD", "PHL", "USA", "DEU", "JPN"}
DEP = ("T1", "T2", "T4")
COVS = {**COV, **COV_EXT}
out = {}
rng = random.Random(20260921)

rows = [json.loads(l) for l in open(os.path.join(ANA, "judge_scores_corrected.jsonl"))]
rows = [r for r in rows if not r.get("error") and "composite" in r]
en = [r for r in rows if not r["prompt_id"].endswith(("_pt", "_es", "_hi"))]
cc = json.load(open(os.path.join(ANA, "country_corpus_measures.json")))


def perm_p(a, b, n=10000):
    pool = a + b; obs = st.mean(a) - st.mean(b); cnt = 0
    for _ in range(n):
        rng.shuffle(pool); cnt += abs(st.mean(pool[:len(a)]) - st.mean(pool[len(a):])) >= abs(obs)
    return cnt / n


def boot_gap(gn, gs, n=10000):
    d = sorted([(st.mean([rng.choice(gn) for _ in gn]) - st.mean([rng.choice(gs) for _ in gs])) * 100 for _ in range(n)])
    return [d[int(0.025 * n)], d[int(0.975 * n) - 1]]


# ---------- A. H4 dentro do país, SE robusto por cluster de país ----------
print("A. H4 dentro do país — interação cobertura×dependência, SE agrupado por país")
df = pd.DataFrame([{"y": r["composite"], "pais": r["country_iso3"], "modelo": str(r["model_id"]),
                    "dep": int(r["task"] in DEP), "cob": float(cc[r["country_iso3"]]["wd_sitelinks"]),
                    "hdi": COVS[r["country_iso3"]][0]}
                   for r in en if r["country_iso3"] in COVS and "_AP_" in r["prompt_id"]
                   and isinstance(cc.get(r["country_iso3"], {}).get("wd_sitelinks"), (int, float))])
for c in ("cob", "hdi"):
    df[c + "_z"] = (df[c] - df[c].mean()) / df[c].std()
def cl(formula, d, label):
    m = smf.ols(formula, d).fit(cov_type="cluster", cov_kwds={"groups": d["pais"]})
    res = {}
    for t in [k for k in m.params.index if k.startswith("dep:")]:
        res[t] = {"beta": float(m.params[t]), "se": float(m.bse[t]), "p": float(m.pvalues[t])}
        print(f"  {label:34s} {t:10s} beta={m.params[t]:+.4f} SE={m.bse[t]:.4f} p={m.pvalues[t]:.3g}  (clusters={d.pais.nunique()})")
    return res
out["A"] = {"cob_alone": cl("y ~ C(pais) + C(modelo) + dep + dep:cob_z", df, "cobertura sozinha"),
            "joint_hdi": cl("y ~ C(pais) + C(modelo) + dep + dep:cob_z + dep:hdi_z", df, "cobertura + HDI"),
            "hdi_alone": cl("y ~ C(pais) + C(modelo) + dep + dep:hdi_z", df, "HDI sozinho"),
            "anglo": cl("y ~ C(pais) + C(modelo) + dep + dep:cob_z",
                        df[df.pais.isin({"USA", "UK", "CAN", "AUS", "IND", "KEN", "NGA", "PHL", "ZAF"})], "só anglófonos (9)")}
# a versão de 25 pontos: déficit por país contra cobertura (a mesma coisa, sem pseudo-réplica)
dfc = df.groupby(["pais", "dep"]).y.mean().unstack()
deficit = (dfc[0] - dfc[1]); cob = df.groupby("pais").cob.first().loc[deficit.index]; hdi = df.groupby("pais").hdi.first().loc[deficit.index]
r_s, p_s = stats.spearmanr(cob, deficit)
# parcial por HDI (ranks residualizados)
def partial(x, y, z):
    rx = stats.rankdata(x); ry = stats.rankdata(y); rz = stats.rankdata(z)
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz); ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    return stats.pearsonr(ex, ey)
r_p, p_p = partial(cob, deficit, hdi)
out["A"]["country_level"] = {"n": int(len(deficit)), "rho": float(r_s), "p": float(p_s), "rho_partial_hdi": float(r_p), "p_partial": float(p_p)}
print(f"  25 déficits por país: rho(cobertura, déficit)={r_s:+.3f} p={p_s:.3f} · parcial HDI {r_p:+.3f} p={p_p:.3f}")

# ---------- B. ORs por tarefa com o país como unidade ----------
print("\nB. ORs GS/GN por tarefa — bootstrap por país (10k) do OR bruto e permutação do tier")
def y_of(r):
    return int(r["factual_accuracy"] >= 0.5)
out["B"] = {}
for t in ("T1", "T2", "T3", "T4", "T5"):
    sel = [r for r in en if r["task"] == t and r["prompt_id"].split("_")[-1] in ("neutral", "env")]
    if t == "T1":
        sel = [r for r in sel if r.get("score_source") == "code"]
    elif t in ("T2", "T3"):
        pass  # código onde resolvido, painel no resíduo — como na Tabela 5
    per = collections.defaultdict(lambda: [0, 0])
    for r in sel:
        per[r["country_iso3"]][0] += y_of(r); per[r["country_iso3"]][1] += 1
    gn = [c for c in per if c in GN]; gs = [c for c in per if c not in GN]
    def orr(gnl, gsl):
        a = sum(per[c][0] for c in gnl); n1 = sum(per[c][1] for c in gnl)
        b = sum(per[c][0] for c in gsl); n2 = sum(per[c][1] for c in gsl)
        p1, p2 = (a + .5) / (n1 + 1), (b + .5) / (n2 + 1)
        return (p2 / (1 - p2)) / (p1 / (1 - p1))
    obs = orr(gn, gs)
    bs = sorted(orr([rng.choice(gn) for _ in gn], [rng.choice(gs) for _ in gs]) for _ in range(10000))
    # permutação: taxa média por país
    rates_gn = [per[c][0] / per[c][1] for c in gn]; rates_gs = [per[c][0] / per[c][1] for c in gs]
    pp = perm_p(rates_gn, rates_gs)
    out["B"][t] = {"OR_raw": obs, "ci_country_boot": [bs[250], bs[9749]], "perm_p_country": pp,
                   "n_gn": len(gn), "n_gs": len(gs), "n": len(sel)}
    print(f"  {t}: OR bruto {obs:.2f}  IC país [{bs[250]:.2f},{bs[9749]:.2f}]  perm p (país)={pp:.3f}  n={len(sel)}")

# ---------- C. UE como um cluster ----------
print("\nC. Tier gap do composto com a UE (DEU, FRA, ITA, PRT) como uma unidade")
acc = collections.defaultdict(list)
for r in en:
    acc[r["country_iso3"]].append(r["composite"])
acc = {c: st.mean(v) for c, v in acc.items()}
units_gn = [acc[c] for c in acc if c in GN and c not in EU] + [st.mean(acc[c] for c in EU)]
units_gs = [acc[c] for c in acc if c not in GN]
gap = (st.mean(units_gn) - st.mean(units_gs)) * 100
out["C"] = {"n_gn_units": len(units_gn), "n_gs": len(units_gs), "gap_pp": gap, "ci": boot_gap(units_gn, units_gs), "perm_p": perm_p(units_gn, units_gs)}
print(f"  GN unidades={len(units_gn)} GS={len(units_gs)} gap {gap:+.2f} pp IC {out['C']['ci']} perm p={out['C']['perm_p']:.3f}")

# ---------- D. subconjunto balanceado de prompts ----------
print("\nD. Tier gap só nos prompts respondidos por todos os 14 modelos")
by_prompt = collections.defaultdict(set)
for r in en:
    by_prompt[r["prompt_id"]].add(str(r["model_id"]))
nm = len({str(r["model_id"]) for r in en})
full = {p for p, ms in by_prompt.items() if len(ms) == nm}
accb = collections.defaultdict(list)
for r in en:
    if r["prompt_id"] in full:
        accb[r["country_iso3"]].append(r["composite"])
accb = {c: st.mean(v) for c, v in accb.items()}
gnb = [accb[c] for c in accb if c in GN]; gsb = [accb[c] for c in accb if c not in GN]
out["D"] = {"prompts_total": len(by_prompt), "prompts_balanced": len(full), "cells": sum(len(v) for v in [[r for r in en if r["prompt_id"] in full]]),
            "gap_pp": (st.mean(gnb) - st.mean(gsb)) * 100, "ci": boot_gap(gnb, gsb), "perm_p": perm_p(gnb, gsb), "n_gn": len(gnb), "n_gs": len(gsb)}
print(f"  prompts balanceados {len(full)}/{len(by_prompt)} · gap {out['D']['gap_pp']:+.2f} pp IC {out['D']['ci']} perm p={out['D']['perm_p']:.3f}")

# ---------- E. H6: efeito principal e TOST ----------
print("\nE. H6 — efeito principal da persona (pareado por prompt×modelo) e TOST do DiD")
pair = collections.defaultdict(dict)
for r in en:
    pid = r["prompt_id"]
    if pid.endswith("_public_manager_env"):
        base, cond = pid[:-len("_public_manager_env")], "env"
    elif pid.endswith("_neutral"):
        base, cond = pid[:-len("_neutral")], "neutral"
    else:
        continue
    pair[(base, str(r["model_id"]))].setdefault(cond, []).append(r["composite"])
d_main = [st.mean(v["env"]) - st.mean(v["neutral"]) for v in pair.values() if "env" in v and "neutral" in v]
per_country = collections.defaultdict(list)
for (base, m), v in pair.items():
    if "env" in v and "neutral" in v:
        per_country[base.split("_")[0]].append(st.mean(v["env"]) - st.mean(v["neutral"]))
pc = {c: st.mean(v) for c, v in per_country.items()}
did_obs = (st.mean(pc[c] for c in pc if c in GN) - st.mean(pc[c] for c in pc if c not in GN)) * 100
gnp = [pc[c] for c in pc if c in GN]; gsp = [pc[c] for c in pc if c not in GN]
bs = sorted([(st.mean([rng.choice(gnp) for _ in gnp]) - st.mean([rng.choice(gsp) for _ in gsp])) * 100 for _ in range(10000)])
ci90 = [bs[500], bs[9499]]; ci95 = [bs[250], bs[9749]]
out["E"] = {"main_effect_pp": st.mean(d_main) * 100, "main_effect_n_pairs": len(d_main), "main_effect_p": wilcoxon_p(d_main),
            "main_effect_country_mean_pp": st.mean(pc.values()) * 100, "main_effect_country_t_p": float(stats.ttest_1samp(list(pc.values()), 0).pvalue),
            "did_pp": did_obs, "did_ci90_country": ci90, "did_ci95_country": ci95,
            "tost_pm2_pass": bool(-2 < ci90[0] and ci90[1] < 2), "tost_pm5_pass": bool(-5 < ci90[0] and ci90[1] < 5)}
print(f"  efeito principal: {out['E']['main_effect_pp']:+.2f} pp (n pares={len(d_main)}, Wilcoxon p={out['E']['main_effect_p']:.2g}; por país t p={out['E']['main_effect_country_t_p']:.3f})")
print(f"  DiD {did_obs:+.2f} pp · IC90 país {ci90} · IC95 {ci95} · TOST ±2: {out['E']['tost_pm2_pass']} · ±5: {out['E']['tost_pm5_pass']}")

# ---------- F. piso e H3 no nível do cluster ----------
print("\nF. Piso de recall e H3 com o modelo / país como unidade")
bym = collections.defaultdict(lambda: collections.defaultdict(list)); byc = collections.defaultdict(lambda: collections.defaultdict(list))
for r in en:
    blk = "rec" if r["task"] in ("T1", "T2") else "rest"
    bym[str(r["model_id"])][blk].append(r["composite"]); byc[r["country_iso3"]][blk].append(r["composite"])
dm = [st.mean(v["rec"]) - st.mean(v["rest"]) for v in bym.values()]; dc = [st.mean(v["rec"]) - st.mean(v["rest"]) for v in byc.values()]
out["F"] = {"floor_by_model": {"n": len(dm), "mean_pp": st.mean(dm) * 100, "neg": sum(d < 0 for d in dm), "wilcoxon_p": wilcoxon_p(dm)},
            "floor_by_country": {"n": len(dc), "mean_pp": st.mean(dc) * 100, "neg": sum(d < 0 for d in dc), "wilcoxon_p": wilcoxon_p(dc)}}
print(f"  piso por modelo: {st.mean(dm)*100:+.1f} pp, {sum(d<0 for d in dm)}/{len(dm)} negativos, Wilcoxon p={out['F']['floor_by_model']['wilcoxon_p']:.2g}")
print(f"  piso por país  : {st.mean(dc)*100:+.1f} pp, {sum(d<0 for d in dc)}/{len(dc)} negativos, Wilcoxon p={out['F']['floor_by_country']['wilcoxon_p']:.2g}")
# H3 amplo: Cabra vs média dos outros, por país
cab = collections.defaultdict(list); oth = collections.defaultdict(list)
for r in en:
    (cab if r["model_id"] == "cabra_mistral_7b" else oth)[r["country_iso3"]].append(r["composite"])
d3 = [st.mean(cab[c]) - st.mean(oth[c]) for c in cab if c in oth]
out["F"]["h3_by_country"] = {"n": len(d3), "mean_pp": st.mean(d3) * 100, "neg": sum(d < 0 for d in d3), "wilcoxon_p": wilcoxon_p(d3)}
print(f"  H3 por país (Cabra − demais): {st.mean(d3)*100:+.1f} pp, {sum(d<0 for d in d3)}/{len(d3)} negativos, p={out['F']['h3_by_country']['wilcoxon_p']:.2g}")
# H3 estreito: Cabra vs Llama 3.1 8B, prompts PT, pareado por prompt (réplicas na média)
pp_ = collections.defaultdict(dict)
for r in rows:
    if r["prompt_id"].endswith("_pt") and r["model_id"] in ("cabra_mistral_7b", "llama31_8b"):
        pp_[r["prompt_id"]].setdefault(r["model_id"], []).append(r["composite"])
d3n = [st.mean(v["cabra_mistral_7b"]) - st.mean(v["llama31_8b"]) for v in pp_.values() if len(v) == 2]
out["F"]["h3_narrow_by_prompt"] = {"n": len(d3n), "mean_pp": st.mean(d3n) * 100, "neg": sum(d < 0 for d in d3n), "wilcoxon_p": wilcoxon_p(d3n)}
print(f"  H3 estreito por prompt PT (Cabra − Llama): n={len(d3n)} {st.mean(d3n)*100:+.1f} pp, {sum(d<0 for d in d3n)} negativos, p={out['F']['h3_narrow_by_prompt']['wilcoxon_p']:.2g}")

# ---------- G. IC de Fisher para rho(acc, HDI) ----------
print("\nG. IC 95% de Fisher para ρ(acurácia, HDI)")
def fisher(rho, n):
    z = math.atanh(rho); se = 1 / math.sqrt(n - 3)
    return [math.tanh(z - 1.96 * se), math.tanh(z + 1.96 * se)]
h = [COVS[c][0] for c in acc]; a = [acc[c] for c in acc]
rho25 = stats.spearmanr(h, a).correlation
a15 = {c: acc[c] for c in acc if c in PRE15}
rho15 = stats.spearmanr([COVS[c][0] for c in a15], list(a15.values())).correlation
out["G"] = {"rho25": float(rho25), "ci25": fisher(rho25, 25), "rho15": float(rho15), "ci15": fisher(rho15, 15)}
print(f"  n=25: rho={rho25:+.3f} IC {out['G']['ci25']} · n=15: rho={rho15:+.3f} IC {out['G']['ci15']}")

# ---------- H. respostas vazias por idioma (T1–T3) ----------
print("\nH. Respostas vazias por idioma nas tarefas pontuadas por código (não houve exclusão por idioma)")
emp = collections.Counter(); tot = collections.Counter()
for t in ("T1", "T2", "T3"):
    for l in open(os.path.join(ROOT, f"data/processed/numeric_scores_{t}.jsonl")):
        v = json.loads(l); pid = v["prompt_id"]; lg = "en"
        for s in ("_pt", "_es", "_hi"):
            if pid.endswith(s): lg = s[1:]
        tot[lg] += 1
        if v.get("reason") == "empty_response": emp[lg] += 1
out["H"] = {lg: {"empty": emp[lg], "responses": tot[lg], "pct": 100 * emp[lg] / tot[lg]} for lg in tot}
for lg in ("en", "es", "pt", "hi"):
    print(f"  {lg}: {emp[lg]}/{tot[lg]} vazias ({100*emp[lg]/tot[lg]:.1f}%)")

# ---------- I. neutralidade de tier da tolerância de T2 ----------
print("\nI. T2: anos aceitos e amplitude da janela (max/min dos valores aceitos) por tier")
t2 = [json.loads(l) for l in open(os.path.join(ROOT, "data/ground_truth/t2_registry.jsonl"))]
t2 = [r for r in t2 if r.get("accepted_years")]
def spread(r):
    v = list(r["accepted_years"].values()); return max(v) / min(v)
gnr = [r for r in t2 if r["country"] in GN]; gsr = [r for r in t2 if r["country"] not in GN]
out["I"] = {"years_gn": st.mean(len(r["accepted_years"]) for r in gnr), "years_gs": st.mean(len(r["accepted_years"]) for r in gsr),
            "spread_gn": st.mean(spread(r) for r in gnr), "spread_gs": st.mean(spread(r) for r in gsr), "n_gn": len(gnr), "n_gs": len(gsr)}
print(f"  anos aceitos GN {out['I']['years_gn']:.1f} vs GS {out['I']['years_gs']:.1f} · amplitude GN {out['I']['spread_gn']:.2f} vs GS {out['I']['spread_gs']:.2f}")

json.dump(out, open(os.path.join(ROOT, "data/processed/cluster_inference.json"), "w"), indent=1, ensure_ascii=False)
print("\nescrito: data/processed/cluster_inference.json")
