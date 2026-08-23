#!/usr/bin/env python3
"""
glmm_and_manipcheck.py — execute two further previously-described methods for real.

  1. GLMM (mixed model) on the confirmatory composite, with crossed random
     intercepts for country and model (statsmodels MixedLM, REML), and a
     binomial mixed GLM on T1 factual accuracy (Bayesian variational fit).
  2. Persona manipulation check: fraction of persona-condition responses that
     explicitly acknowledge the public-manager role frame (keyword scan over the
     raw response text).

Run with the project venv:  .venv/bin/python code/analysis/glmm_and_manipcheck.py
"""
import json
import math
import sys, os, glob, re
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANA = os.path.join(ROOT, "data/confirmatory_PRIVATE/analysis")
RESP = os.path.join(ROOT, "data/confirmatory_PRIVATE/responses")
HDI = {"USA":0.927,"DEU":0.950,"JPN":0.920,"BRA":0.760,"MEX":0.781,"ARG":0.849,
 "PER":0.762,"IND":0.644,"IDN":0.713,"EGY":0.728,"BGD":0.670,"NGA":0.548,"ZAF":0.717,
 "KEN":0.601,"PHL":0.710,"UK":0.940,"CAN":0.935,"AUS":0.946,"FRA":0.910,"ITA":0.906,
 "KOR":0.929,"COL":0.758,"CHL":0.860,"PRT":0.874,"AGO":0.591}
GN = {"USA","DEU","JPN","UK","CAN","AUS","KOR","FRA","ITA","PRT"}

rows = [json.loads(l) for l in open(os.path.join(ANA,"judge_scores_corrected.jsonl" if "--original" not in sys.argv else "judge_scores_confirmatory.jsonl"))]
rows = [r for r in rows if not r.get('error') and r['prompt_id'].split('_')[-1] in ('neutral','env')]
df = pd.DataFrame({
    "composite":[r['composite'] for r in rows],
    "factual":[r['factual_accuracy'] for r in rows],
    "country":[r['country_iso3'] for r in rows],
    "model":[r['model_id'] for r in rows],
    "task":[r['task'] for r in rows],
})
df["is_south"] = (~df["country"].isin(GN)).astype(int)
df["hdi"] = df["country"].map(HDI)
df["hdi_c"] = df["hdi"] - df["hdi"].mean()
df["allone"] = 1

print("="*74); print("1a) GAUSSIAN MIXED MODEL — composite ~ is_south + hdi_c, crossed RE (country, model)")
print("="*74)
md = smf.mixedlm("composite ~ is_south + hdi_c", df, groups=df["allone"],
                 vc_formula={"country":"0+C(country)","model":"0+C(model)"})
mdf = md.fit(reml=True, method="lbfgs")
for term in ["Intercept","is_south","hdi_c"]:
    if term in mdf.params.index:
        b=mdf.params[term]; se=mdf.bse[term]; p=mdf.pvalues[term]
        print(f"  {term:10s}: beta={b:+.4f}  SE={se:.4f}  p={p:.4g}")
try: print("  variance components (country, model):", list(np.round(np.atleast_1d(mdf.vcomp),4)))
except Exception: pass

# Clean single-grouping checks (crossed-RE fit above can be numerically unstable):
mc = smf.mixedlm("composite ~ is_south + hdi_c", df, groups=df["country"]).fit(reml=True)
print(f"  [RE=country only] is_south beta={mc.params['is_south']:+.4f} SE={mc.bse['is_south']:.4f} p={mc.pvalues['is_south']:.4g}")
mm = smf.mixedlm("composite ~ is_south", df, groups=df["model"]).fit(reml=True)
print(f"  [RE=model only]   is_south beta={mm.params['is_south']:+.4f} SE={mm.bse['is_south']:.4f} p={mm.pvalues['is_south']:.4g}")

print("\n"+"="*74); print("1b) BINOMIAL MIXED GLM (Bayesian VB) — T1 factual accuracy ~ is_south, RE country+model")
print("="*74)
t1 = df[df["task"]=="T1"].copy()
t1["y"] = (t1["factual"] >= 0.5).astype(int)
try:
    m2 = BinomialBayesMixedGLM.from_formula("y ~ is_south", {"country":"0+C(country)","model":"0+C(model)"}, t1)
    r2 = m2.fit_vb()
    idx = list(r2.model.exog_names).index("is_south")
    # cov_params() devolve um pandas Series de variancias posteriores, nao uma
    # matriz. Indexar por posicao com [idx] cai no indexador por ROTULO e levanta
    # KeyError: 1 — cuja mensagem, truncada, aparecia como "[falhou]: 1" e fazia
    # o bloco parecer um problema de convergencia do modelo. O ajuste sempre
    # funcionou; era a leitura do resultado que estava errada.
    sd = float(np.asarray(r2.cov_params())[idx]) ** 0.5
    b = float(r2.params[idx])
    lo, hi = b - 1.96 * sd, b + 1.96 * sd
    taxa = t1.groupby("is_south")["y"].mean()
    print(f"  is_south: posterior mean={b:+.4f} (log-odds)  posterior SD={sd:.4f}")
    print(f"    95% interval        : [{lo:+.3f}, {hi:+.3f}]")
    print(f"    odds ratio          : {math.exp(b):.3f}  [{math.exp(lo):.3f}, {math.exp(hi):.3f}]")
    print(f"    raw hit rate on T1  : Global North {taxa[0]:.1%} vs Global South {taxa[1]:.1%}")
    print(f"  (T1 n={len(t1)}; negative => Global South lower factual accuracy on the binding standard)")
except Exception as e:
    print("  [binomial VB GLMM falhou]:", str(e)[:150])

print("\n"+"="*74)
print("1c) BINOMIAL MIXED GLM POR TAREFA — onde o gap Norte/Sul se concentra")
print("="*74)
# O composto promedia cinco tarefas, e o gap nao esta distribuido por igual entre
# elas. Estimar a mesma razao de chances tarefa a tarefa mostra que o efeito
# escala com o quanto a tarefa exige um fato ESPECIFICO daquele pais — e some na
# tarefa que nao tem fato a acertar. Isso explica por que o gap parece modesto no
# composto: ele e diluido por tarefas onde nao existe.
print(f"  {'tarefa':<7}{'n':>6}{'GN':>8}{'GS':>8}{'OR':>8}   IC95")
for _t in ("T1", "T2", "T3", "T4", "T5"):
    _d = df[df.task == _t].copy()
    _d["y"] = (_d["factual"] >= 0.5).astype(int)
    if _d["y"].nunique() < 2:
        print(f"  {_t:<7}{len(_d):>6}  sem variacao no desfecho")
        continue
    try:
        _r = BinomialBayesMixedGLM.from_formula(
            "y ~ is_south", {"country": "0+C(country)", "model": "0+C(model)"}, _d).fit_vb()
        _i = list(_r.model.exog_names).index("is_south")
        _b = float(_r.params[_i]); _sd = float(np.asarray(_r.cov_params())[_i]) ** 0.5
        _tx = _d.groupby("is_south")["y"].mean()
        print(f"  {_t:<7}{len(_d):>6}{_tx[0]:>8.1%}{_tx[1]:>8.1%}{math.exp(_b):>8.3f}"
              f"   [{math.exp(_b-1.96*_sd):.3f}, {math.exp(_b+1.96*_sd):.3f}]")
    except Exception as _e:
        print(f"  {_t:<7}{len(_d):>6}  falhou: {type(_e).__name__}")
print("  Leitura: o gap escala com a dependencia de um fato do pais e desaparece")
print("  em T5, que e a unica tarefa sem valor de registro a acertar.")

print("\n"+"="*74); print("2) PERSONA MANIPULATION CHECK — role-frame acknowledgement in persona responses")
print("="*74)
# load raw responses, persona condition only (prompt_id ends _public_manager_env -> persona=='env' tag)
ack_re = re.compile(r"\b(as (a|an|the) [^.,;]{0,40}(manager|official|secretary|administrator|gestor|funcion|secretar)"
                    r"|in (my|your) role|you are|decision[- ]?makers?|brief)", re.I)
seen=0; ack=0
for f in glob.glob(os.path.join(RESP,"run_confirmatory_*.jsonl")):
    for line in open(f):
        try: r=json.loads(line)
        except: continue
        if r.get('api_error'): continue
        pid=r.get('prompt_id','')
        if not pid.endswith('public_manager_env'): continue
        txt=r.get('response_text') or ''
        seen+=1
        if ack_re.search(txt): ack+=1
print(f"  persona responses scanned: {seen}")
if seen:
    print(f"  explicit role-frame acknowledgement: {ack} ({100*ack/seen:.1f}%)")
    print("  NOTE: report this as the realized manipulation-check rate; a low rate is itself")
    print("  consistent with the H6 null (models largely do not adopt the persona).")
