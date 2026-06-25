#!/usr/bin/env python3
"""
bayesian_reestimation.py — Bayesian re-estimation of the geographic effects with
weakly informative priors (pre-specified robustness analysis), executed for real.

Hierarchical Gaussian model on the English-prompt composite:
    composite_i ~ Normal(mu_i, sigma)
    mu_i = a + b * is_south_i + u_country[c_i] + v_model[m_i]
    u_country ~ Normal(0, sigma_c) ; v_model ~ Normal(0, sigma_m)
Weakly informative priors: a~N(0.5,0.5), b~N(0,0.5), sigmas~HalfNormal(0.5).
Reports the posterior mean and 94% HDI for the Global South effect b, and P(b<0).

Run with the venv:  .venv/bin/python code/analysis/bayesian_reestimation.py
"""
import json, os
import numpy as np
import pymc as pm
import arviz as az

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCORES = os.path.join(ROOT, "data/confirmatory_PRIVATE/analysis/judge_scores_confirmatory.jsonl")
GN = {"USA","DEU","JPN","UK","CAN","AUS","KOR","FRA","ITA","PRT"}

rows = [json.loads(l) for l in open(SCORES)]
rows = [r for r in rows if not r.get('error') and r['prompt_id'].split('_')[-1] in ('neutral','env')]
y   = np.array([r['composite'] for r in rows])
cc  = np.array([r['country_iso3'] for r in rows]); countries = sorted(set(cc))
mm  = np.array([r['model_id'] for r in rows]);     models    = sorted(set(mm))
ci  = np.array([countries.index(c) for c in cc])
mi  = np.array([models.index(m) for m in mm])
south = np.array([0.0 if c in GN else 1.0 for c in cc])

with pm.Model() as model:
    a   = pm.Normal("a", 0.5, 0.5)
    b   = pm.Normal("b_south", 0.0, 0.5)
    sc  = pm.HalfNormal("sigma_country", 0.5)
    sm  = pm.HalfNormal("sigma_model", 0.5)
    sig = pm.HalfNormal("sigma", 0.5)
    u   = pm.Normal("u_country", 0.0, sc, shape=len(countries))
    v   = pm.Normal("v_model",   0.0, sm, shape=len(models))
    mu  = a + b*south + u[ci] + v[mi]
    pm.Normal("y", mu, sig, observed=y)
    idata = pm.sample(1000, tune=1000, chains=2, cores=1, target_accept=0.9,
                      random_seed=42, progressbar=False)

chains = idata.posterior["b_south"].values            # (chain, draw)
post = chains.ravel()

def hdi(s, prob=0.94):
    s = np.sort(s); n = len(s); k = int(np.floor(prob*n))
    w = s[k:] - s[:n-k]; i = int(np.argmin(w)); return s[i], s[i+k]

def rhat(x):                                          # split-chain Gelman-Rubin
    m, n = x.shape
    W = x.var(1, ddof=1).mean()
    B = n * x.mean(1).var(ddof=1)
    return float(np.sqrt(((n-1)/n*W + B/n) / W))

lo, hi = hdi(post, 0.94)
print("="*70)
print("BAYESIAN RE-ESTIMATION — Global South effect on composite (weakly inf. priors)")
print("="*70)
print(f"  posterior mean b_south = {post.mean():+.4f}")
print(f"  94% HDI                = [{lo:+.4f}, {hi:+.4f}]")
print(f"  P(b_south < 0)         = {(post < 0).mean():.3f}")
print(f"  (negative => Global South lower; compare frequentist MixedLM beta=-0.077, p=0.007)")
print(f"  R-hat(b_south) = {rhat(chains):.3f}  (convergence; should be ~1.00)")
