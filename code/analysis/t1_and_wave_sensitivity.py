#!/usr/bin/env python3
"""t1_and_wave_sensitivity.py — análises pedidas pelo parecer externo de 2026-09-21.

Tudo lê judge_scores_corrected.jsonl (base única, 8.300 células, T1 por código).
Saída: data/processed/t1_wave_sensitivity.json + impressão legível.

  A. OR(GS/GN) de "devolveu o valor do registro" em T1, modelo binomial misto
     (mesma especificação de glmm_and_manipcheck.py), em quatro amostras:
       todos os países com chave · sem os 5 GS de chave não padrão
       (AGO, ARG, NGA sem padrão; BGD, EGY parcialmente verificadas — EGY já
       está fora por não ter chave) · chave estrita vs escada oficial
       (confusão de etapa/versão não é fabricação) · só os 15 pré-especificados.
  B. Tier gap do composto (pp) nos 15 pré-especificados (3 GN vs 12 GS) e
     dentro da onda 2 (7 GN vs COL, CHL, AGO), com IC bootstrap por país.
  C. Sensibilidade à seleção da resposta duplicada (T1/T2/T3 por código):
     primeira em ordem de arquivo (a que o juiz viu) vs média de todas.
  D. H2 (língua nativa) separado por instrumento: células adjudicadas por
     código vs pelo painel vs juiz original, com a composição de cada uma.
  E. T1 por juiz original × tier (o confundimento que o código elimina).
"""
from __future__ import annotations
import collections, json, os, statistics as st, sys, random
import numpy as np, pandas as pd
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from code.analysis.code_verdicts import carregar, todos, FACTUAL  # noqa: E402
from code.analysis.nonparametric import wilcoxon_p  # noqa: E402

ANA = os.path.join(ROOT, "data/confirmatory_PRIVATE/analysis")
GN = {"USA","DEU","JPN","UK","CAN","AUS","KOR","FRA","ITA","PRT"}
PRE15 = {"BRA","MEX","ARG","PER","NGA","ZAF","KEN","EGY","IND","IDN","BGD","PHL","USA","DEU","JPN"}
WAVE2 = {"COL","CHL","AGO","UK","CAN","AUS","KOR","FRA","ITA","PRT"}
NONSTD = {"AGO","ARG","NGA","EGY"}  # BGD saiu em 2026-09-21: chave 35 (2022) verificada
out = {}

rows = [json.loads(l) for l in open(os.path.join(ANA, "judge_scores_corrected.jsonl"))]
rows = [r for r in rows if not r.get("error")]
orig = {}
for l in open(os.path.join(ANA, "judge_scores_confirmatory.jsonl")):
    r = json.loads(l)
    if r.get("error") or "composite" not in r: continue
    orig.setdefault((r["prompt_id"], str(r["model_id"]), int(r.get("replicate_idx", 0))), r)

def key(r): return (r["prompt_id"], str(r["model_id"]), int(r.get("replicate_idx", 0)))
t1_code = {k: v for k, v in todos(("T1",)).items()}

def or_model(df, label):
    df = df.copy(); df["allone"] = 1
    m = BinomialBayesMixedGLM.from_formula("y ~ is_south", {"country": "0+C(country)", "model": "0+C(model)"}, df)
    f = m.fit_vb()
    i = list(f.model.exog_names).index("is_south")
    b = f.fe_mean[i]; se = f.fe_sd[i]
    res = {"n": int(len(df)), "n_countries": int(df.country.nunique()),
           "rate_gn": float(df[df.is_south == 0].y.mean()), "rate_gs": float(df[df.is_south == 1].y.mean()),
           "OR": float(np.exp(b)), "ci": [float(np.exp(b - 1.96 * se)), float(np.exp(b + 1.96 * se))]}
    print(f"  {label:58s} n={res['n']:4d} GN {res['rate_gn']:.3f} GS {res['rate_gs']:.3f}  OR {res['OR']:.2f} [{res['ci'][0]:.2f},{res['ci'][1]:.2f}]")
    return res

# ---------- A. T1 por código ----------
print("A. T1 — odds GS/GN de devolver o valor do registro (binomial misto, RE país+modelo)")
t1 = [r for r in rows if r["task"] == "T1" and r.get("score_source") == "code" and r["prompt_id"].split("_")[-1] in ("neutral", "env")]
def frame(sel, ladder=False):
    recs = []
    for r in sel:
        k = key(r); g = t1_code.get(k)
        if not g: continue
        first = next((x for x in g if x["verdict"] in FACTUAL), None)
        if not first: continue
        y = FACTUAL[first["verdict"]]
        if ladder and first["verdict"] in ("INCORRECT",) and first.get("ladder_hit"):
            y = 1.0
        recs.append({"y": int(y), "country": r["country_iso3"], "model": r["model_id"], "is_south": int(r["country_iso3"] not in GN)})
    return pd.DataFrame(recs)
# escada por tier (auditoria DeepSeek, rodada 15): o "um terco" agrupado esconde
# que a confusao de degrau e um modo de falha do NORTE — e o Norte e que tem
# instrumentos escalonados. Sem separar, o numero do abstract descreve uma
# populacao que nao existe.
_esc_por, _esc_hit = collections.Counter(), collections.Counter()
for _k, _g in t1_code.items():
    _f = next((x for x in _g if x["verdict"] in FACTUAL), None)
    if not _f or _f["verdict"] != "INCORRECT":
        continue
    _t = "GN" if _f["country"] in GN else "GS"
    _esc_por[_t] += 1
    _esc_hit[_t] += bool(_f.get("ladder_hit"))
out["ladder_by_tier"] = {t: {"incorrect": _esc_por[t], "ladder_hit": _esc_hit[t],
                             "share": _esc_hit[t] / _esc_por[t] if _esc_por[t] else None}
                         for t in ("GN", "GS")}
print("\nA2. Escada por tier — que fracao das respostas ERRADAS de T1 cita um degrau oficial")
for _t in ("GN", "GS"):
    _d = out["ladder_by_tier"][_t]
    print(f"  {_t}: {_d['ladder_hit']}/{_d['incorrect']} = {100*_d['share']:.0f}%")

out["A"] = {
    "all_keyed": or_model(frame(t1), "todos os países com chave (24; EGY fora)"),
    "excl_nonstandard": or_model(frame([r for r in t1 if r["country_iso3"] not in NONSTD]), "sem AGO/ARG/NGA (sem padrão) → 21 países"),
    "ladder": or_model(frame(t1, ladder=True), "chave ESCADA (qualquer degrau oficial conta)"),
    "ladder_excl": or_model(frame([r for r in t1 if r["country_iso3"] not in NONSTD], ladder=True), "escada + sem chave não padrão"),
    "pre15": or_model(frame([r for r in t1 if r["country_iso3"] in PRE15]), "só os 15 pré-especificados (3 GN)"),
}
# escada: quanto do "erro" é confusão de etapa
inc = [x for g in t1_code.values() for x in g[:1] if x["verdict"] == "INCORRECT"]
out["A"]["ladder_share_of_incorrect"] = {"incorrect": len(inc), "ladder_hit": sum(1 for x in inc if x.get("ladder_hit"))}
print(f"  INCORRECT que batem num degrau oficial (confusão de etapa/versão): {out['A']['ladder_share_of_incorrect']['ladder_hit']}/{len(inc)}")
por_pais = collections.defaultdict(list)
for x in (g[0] for g in t1_code.values()):
    if x["verdict"] in FACTUAL: por_pais[x["country"]].append(FACTUAL[x["verdict"]])
out["A"]["t1_rate_by_country"] = {c: round(st.mean(v), 3) for c, v in sorted(por_pais.items())}
# países sem padrão: distribuição dos vereditos (primeira resposta por célula) — citada no texto (168/256, 33, 31)
nostd = collections.Counter(g[0]["verdict"] for g in t1_code.values() if g[0]["country"] in ("AGO", "ARG", "NGA"))
out["A"]["no_standard_verdicts"] = dict(nostd); out["A"]["no_standard_cells"] = sum(nostd.values())
print("  países sem padrão, vereditos:", dict(nostd), "total", sum(nostd.values()))
print("  taxa T1 por país:", " ".join(f"{c}:{st.mean(v):.2f}" for c, v in sorted(por_pais.items())))

# ---------- B. tier gap do composto por amostra ----------
print("\nB. Tier gap do composto (pp), média por país, IC bootstrap por país (10k)")
cells = collections.defaultdict(list)
for r in rows:
    if r["prompt_id"].endswith(("_pt", "_es", "_hi")): continue
    cells[r["country_iso3"]].append(r["composite"])
acc = {c: st.mean(v) for c, v in cells.items()}
def gap(countries, label):
    gn = [acc[c] for c in countries if c in GN]; gs = [acc[c] for c in countries if c not in GN]
    rng = random.Random(20260921); difs = []
    for _ in range(10000):
        a = [rng.choice(gn) for _ in gn]; b = [rng.choice(gs) for _ in gs]
        difs.append((st.mean(a) - st.mean(b)) * 100)
    difs.sort()
    # permutação do rótulo de tier
    pool = gn + gs; obs = st.mean(gn) - st.mean(gs); cnt = 0
    for _ in range(10000):
        rng.shuffle(pool); cnt += abs(st.mean(pool[:len(gn)]) - st.mean(pool[len(gn):])) >= abs(obs)
    res = {"n_gn": len(gn), "n_gs": len(gs), "gap_pp": (st.mean(gn) - st.mean(gs)) * 100, "ci": [difs[250], difs[9750]], "perm_p": cnt / 10000}
    print(f"  {label:40s} GN={len(gn)} GS={len(gs)}  gap {res['gap_pp']:+.2f} pp  IC [{res['ci'][0]:+.2f},{res['ci'][1]:+.2f}]  perm p={res['perm_p']:.3f}")
    return res
out["B"] = {"all25": gap(set(acc), "25 países"), "pre15": gap(PRE15, "15 pré-especificados"), "wave2": gap(WAVE2, "onda 2 (extensão)")}

# ---------- C. seleção da resposta duplicada ----------
print("\nC. Vereditos de código: primeira resposta (a que o juiz viu) vs média de todas as armazenadas")
d1, _, _ = carregar(selecao="primeira"); d2, _, _ = carregar(selecao="media")
comum = set(d1) & set(d2)
dif = sum(1 for k in comum if abs(d1[k] - d2[k]) > 1e-9)
out["C"] = {"cells": len(comum), "cells_where_rule_changes_verdict": dif, "mean_first": st.mean(d1[k] for k in comum), "mean_all": st.mean(d2[k] for k in comum)}
print(f"  células com veredito de código: {len(comum)} · muda com a regra: {dif} ({100*dif/len(comum):.1f}%) · média primeira {out['C']['mean_first']:.4f} vs todas {out['C']['mean_all']:.4f}")

# ---------- D. H2 por instrumento ----------
print("\nD. H2 (língua nativa − inglês, pareado por (prompt, modelo) como no congelamento, pp) por instrumento")
cel = collections.defaultdict(lambda: {"en": [], "nat": [], "src": collections.Counter()})
for r in rows:
    pid = r["prompt_id"]; base, lang = pid, "en"
    for suf in ("_pt", "_es", "_hi"):
        if pid.endswith(suf): base, lang = pid[: -len(suf)], "nat"
    c = cel[(base, str(r["model_id"]))]
    c[lang].append(r["composite"])
    if lang == "nat": c["src"][r.get("score_source")] += 1
out["D"] = {}
for src in ("code", "panel", "original", "todos"):
    pares = [st.mean(c["nat"]) - st.mean(c["en"]) for c in cel.values()
             if c["en"] and c["nat"] and (src == "todos" or c["src"].most_common(1)[0][0] == src)]
    if len(pares) < 10: continue
    p = wilcoxon_p(pares)
    out["D"][src] = {"n": len(pares), "pp": st.mean(pares) * 100, "p": p}
    print(f"  {src:9s} n={len(pares):4d}  {st.mean(pares)*100:+.2f} pp  Wilcoxon p={p:.2g}")

# ---------- E. T1 original por juiz × tier ----------
print("\nE. T1 no juiz ORIGINAL (antes do código): acurácia factual por juiz × tier — o confundimento")
ej = collections.defaultdict(list)
for k, r in orig.items():
    if r["task"] == "T1" and r["persona"] == "neutral":
        ej[("GN" if r["country_iso3"] in GN else "GS", r["judge_model"][:14])].append(r["factual_accuracy"])
out["E"] = {f"{a}|{b}": {"n": len(v), "factual": st.mean(v)} for (a, b), v in sorted(ej.items())}
for (a, b), v in sorted(ej.items()): print(f"  {a} {b:14s} n={len(v):4d} factual={st.mean(v):.3f}")

# ---------- F. H3 como pré-especificado: Cabra vs Llama 3.1 8B, em português, Brasil ----------
print("\nF. H3 pré-especificado (osf_prereg_draft.md): Cabra-Mistral 7B vs Llama 3.1 8B (escala pareada), prompts em PORTUGUÊS")
def h3(countries, label):
    cab = [r["composite"] for r in rows if r["model_id"] == "cabra_mistral_7b" and r["prompt_id"].endswith("_pt") and r["country_iso3"] in countries]
    lla = [r["composite"] for r in rows if r["model_id"] == "llama31_8b" and r["prompt_id"].endswith("_pt") and r["country_iso3"] in countries]
    resto = [r["composite"] for r in rows if r["model_id"] not in ("cabra_mistral_7b",) and r["prompt_id"].endswith("_pt") and r["country_iso3"] in countries]
    def cliff(a, b):
        return (sum((x > y) - (x < y) for x in a for y in b) / (len(a) * len(b))) if a and b else float("nan")
    res = {"n_cabra": len(cab), "n_llama": len(lla), "mean_cabra": st.mean(cab) if cab else None, "mean_llama": st.mean(lla) if lla else None,
           "delta_vs_llama": cliff(cab, lla), "mean_rest": st.mean(resto) if resto else None, "delta_vs_rest": cliff(cab, resto)}
    print(f"  {label:22s} Cabra {res['mean_cabra']:.3f} (n={len(cab)}) vs Llama 3.1 8B {res['mean_llama']:.3f} (n={len(lla)})  δ={res['delta_vs_llama']:+.2f} · vs resto {res['mean_rest']:.3f} δ={res['delta_vs_rest']:+.2f}")
    return res
out["F"] = {"BRA_pt": h3({"BRA"}, "Brasil, PT"), "lusofonos_pt": h3({"BRA", "PRT", "AGO"}, "BRA+PRT+AGO, PT")}
en_cab = [r["composite"] for r in rows if r["model_id"] == "cabra_mistral_7b" and not r["prompt_id"].endswith(("_pt", "_es", "_hi"))]
en_lla = [r["composite"] for r in rows if r["model_id"] == "llama31_8b" and not r["prompt_id"].endswith(("_pt", "_es", "_hi"))]
out["F"]["all25_en"] = {"mean_cabra": st.mean(en_cab), "mean_llama": st.mean(en_lla)}
print(f"  25 países, EN: Cabra {st.mean(en_cab):.3f} vs Llama 3.1 8B {st.mean(en_lla):.3f}")

# ---------- G. efeito vs variância entre réplicas ----------
print("\nG. H2 (−4.95 pp) contra a variância entre as duas réplicas da MESMA célula")
rep = collections.defaultdict(dict)
for r in rows:
    rep[(r["prompt_id"], str(r["model_id"]))][int(r.get("replicate_idx", 0))] = r["composite"]
difs = [abs(d[0] - d[1]) for d in rep.values() if 0 in d and 1 in d]
sd_within = (st.mean([(d[0] - d[1]) ** 2 for d in rep.values() if 0 in d and 1 in d]) / 2) ** 0.5
out["G"] = {"n_cells_with_2_reps": len(difs), "mean_abs_diff_pp": st.mean(difs) * 100, "sd_within_pp": sd_within * 100,
            "se_of_h2_pp": sd_within * 100 * (2 ** 0.5) / (839 ** 0.5)}
print(f"  células com 2 réplicas: {len(difs)} · |Δ| médio {st.mean(difs)*100:.1f} pp · DP intra-célula {sd_within*100:.1f} pp · EP implícito para 839 pares ≈ {out['G']['se_of_h2_pp']:.2f} pp")

# ---------- H. H2 com a dependência declarada ----------
# O Wilcoxon sobre 839 células trata as células como independentes; elas estão
# aninhadas em 9 países e 14 modelos. Aqui a diferença pareada por (prompt, modelo)
# entra num modelo misto com intercepto aleatório de PAÍS (a unidade de
# generalização) e, separadamente, de MODELO; e o país e o modelo entram como
# unidade num teste t / Wilcoxon. (A versão com os dois componentes cruzados numa
# única "group" do statsmodels devolve EP instável com 9 países; não é reportada.)
print("\nH. H2 respeitando o aninhamento (diferença pareada por prompt×modelo)")
import statsmodels.formula.api as smf
from scipy.stats import wilcoxon, ttest_1samp
recs = []
for (base, model), c in cel.items():
    if c["en"] and c["nat"]:
        recs.append({"d": st.mean(c["nat"]) - st.mean(c["en"]), "country": base.split("_")[0], "model": model})
dfh = pd.DataFrame(recs)
out["H"] = {"n_pairs": int(len(dfh))}
for name, grp in (("country", dfh["country"]), ("model", dfh["model"])):
    m = smf.mixedlm("d ~ 1", dfh, groups=grp).fit(reml=True)
    b, se, pv = m.params["Intercept"], m.bse["Intercept"], m.pvalues["Intercept"]
    out["H"][f"re_{name}"] = {"beta_pp": b * 100, "se_pp": se * 100, "p": float(pv)}
    print(f"  intercepto aleatório de {name:7s}: Δ={b*100:+.2f} pp  EP={se*100:.2f}  p={pv:.2g}")
pc = dfh.groupby("country").d.mean(); pm = dfh.groupby("model").d.mean()
t = ttest_1samp(pc, 0)
out["H"]["country_level"] = {"n": int(len(pc)), "neg": int((pc < 0).sum()), "mean_pp": float(pc.mean() * 100), "se_pp": float(pc.std(ddof=1) / len(pc) ** 0.5 * 100), "t": float(t.statistic), "t_p": float(t.pvalue), "wilcoxon_p": float(wilcoxon(pc).pvalue)}
out["H"]["model_level"] = {"n": int(len(pm)), "neg": int((pm < 0).sum()), "mean_pp": float(pm.mean() * 100), "wilcoxon_p": float(wilcoxon(pm).pvalue)}
print(f"  país como unidade (n=9): {int((pc<0).sum())}/9 negativos, média {pc.mean()*100:+.2f} ± {pc.std(ddof=1)/3*100:.2f} pp, t={t.statistic:.2f} p={t.pvalue:.3f}, Wilcoxon p={wilcoxon(pc).pvalue:.3f}")
print(f"  modelo como unidade (n=14): {int((pm<0).sum())}/14 negativos, média {pm.mean()*100:+.2f} pp, Wilcoxon p={wilcoxon(pm).pvalue:.2g}")

# ---------- I. Desfechos SÓ de código: lacuna de tier e H2 sem juiz nenhum ----------
# Parecer 2 (2026-09-21): o painel de LLMs pode conhecer menos os instrumentos do Sul,
# de modo que o gap nas tarefas julgadas (T4 inteira, resíduo de T2/T3) soma déficit
# do modelo com déficit do juiz. Aqui o desfecho é o veredito de código (T1 todo;
# T2/T3 onde o código resolveu): nenhum juiz toca nele.
print("\nI. Só células adjudicadas por código (T1; T2/T3 resolvidas): tier e idioma sem juiz")
code_rows = [r for r in rows if r.get("score_source") == "code" and r["prompt_id"].split("_")[-1] in ("neutral", "env")]
dfc = pd.DataFrame([{"y": int(r["factual_accuracy"] >= 0.5), "country": r["country_iso3"], "model": r["model_id"], "task": r["task"], "is_south": int(r["country_iso3"] not in GN)} for r in code_rows])
out["I"] = {"pooled": or_model(dfc, "T1+T2+T3 por código, todos os países com chave")}
out["I"]["pooled_excl_nonstd"] = or_model(dfc[~dfc.country.isin(NONSTD)], "idem, sem AGO/ARG/NGA")
for t in ("T1", "T2", "T3"):
    out["I"][t] = or_model(dfc[dfc.task == t], f"só {t} por código")
# lacuna em pp no nível do país (média por país do acerto de código), IC bootstrap por país
pcm = dfc.groupby("country").y.mean()
gn = [pcm[c] for c in pcm.index if c in GN]; gs = [pcm[c] for c in pcm.index if c not in GN]
rng = random.Random(20260921); difs = sorted([(st.mean([rng.choice(gn) for _ in gn]) - st.mean([rng.choice(gs) for _ in gs])) * 100 for _ in range(10000)])
pool = gn + gs; obs = st.mean(gn) - st.mean(gs); cnt = 0
for _ in range(10000):
    rng.shuffle(pool); cnt += abs(st.mean(pool[:len(gn)]) - st.mean(pool[len(gn):])) >= abs(obs)
out["I"]["country_level_gap"] = {"gap_pp": obs * 100, "ci": [difs[250], difs[9750]], "perm_p": cnt / 10000, "acc_gn": st.mean(gn), "acc_gs": st.mean(gs)}
print(f"  lacuna por país (acerto de código): GN {st.mean(gn):.3f} vs GS {st.mean(gs):.3f} = {obs*100:+.2f} pp, IC [{difs[250]:+.2f},{difs[9750]:+.2f}], perm p={cnt/10000:.3f}")
# H2 sem juiz por idioma: veredito de código nativo − inglês, pareado por (prompt, modelo)
celc = collections.defaultdict(lambda: {"en": [], "nat": []})
for r in rows:
    if r.get("score_source") != "code": continue
    pid = r["prompt_id"]; base, lang = pid, "en"
    for suf in ("_pt", "_es", "_hi"):
        if pid.endswith(suf): base, lang = pid[:-len(suf)], "nat"
    celc[(base, str(r["model_id"]))][lang].append(float(r["factual_accuracy"] >= 0.5))
out["I"]["h2_code_by_lang"] = {}
for lg, name in (("pt", "português"), ("es", "espanhol"), ("hi", "hindi"), (None, "todos")):
    ds = [st.mean(c["nat"]) - st.mean(c["en"]) for (b, m), c in celc.items() if c["en"] and c["nat"] and (lg is None or any(k.endswith("_" + lg) for k in [b + "_" + lg]))]
    # filtro por idioma via país
    if lg:
        paises = {"pt": {"BRA", "PRT", "AGO"}, "es": {"MEX", "ARG", "PER", "COL", "CHL"}, "hi": {"IND"}}[lg]
        ds = [st.mean(c["nat"]) - st.mean(c["en"]) for (b, m), c in celc.items() if c["en"] and c["nat"] and b.split("_")[0] in paises]
    if len(ds) >= 10:
        pv = wilcoxon_p(ds) if len(set(ds)) > 1 else float("nan")
        out["I"]["h2_code_by_lang"][name] = {"n": len(ds), "pp": st.mean(ds) * 100, "p": pv}
        print(f"  H2 só código, {name:9s}: n={len(ds):3d}  {st.mean(ds)*100:+.1f} pp  p={pv:.2g}")

json.dump(out, open(os.path.join(ROOT, "data/processed/t1_wave_sensitivity.json"), "w"), indent=1, ensure_ascii=False)
print("\nescrito: data/processed/t1_wave_sensitivity.json")
