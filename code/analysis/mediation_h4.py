#!/usr/bin/env python3
"""
mediation_h4.py — exploratory country-level mediation for H4 (executed for real).

Question: is the development (HDI) -> accuracy relationship mediated by how broadly
the corpus represents a country (Wikidata sitelinks)?
Path model (standardized, n=25 countries):
    log_sitelinks ~ a * HDI
    accuracy      ~ c' * HDI + b * log_sitelinks
Indirect = a*b ; Direct = c' ; bootstrap 95% CI over countries (n=25 is small ->
strictly exploratory, reported as such).

Run with venv:  .venv/bin/python code/analysis/mediation_h4.py
"""
import json, os, math
import numpy as np
import pandas as pd
import semopy

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANA = os.path.join(ROOT, "data/confirmatory_PRIVATE/analysis")
HDI = {"USA":0.927,"DEU":0.950,"JPN":0.920,"BRA":0.760,"MEX":0.781,"ARG":0.849,
 "PER":0.762,"IND":0.644,"IDN":0.713,"EGY":0.728,"BGD":0.670,"NGA":0.548,"ZAF":0.717,
 "KEN":0.601,"PHL":0.710,"UK":0.940,"CAN":0.935,"AUS":0.946,"FRA":0.910,"ITA":0.906,
 "KOR":0.929,"COL":0.758,"CHL":0.860,"PRT":0.874,"AGO":0.591}
GN = {"USA","DEU","JPN","UK","CAN","AUS","KOR","FRA","ITA","PRT"}

rows = [json.loads(l) for l in open(os.path.join(ANA,"judge_scores_confirmatory.jsonl"))]
rows = [r for r in rows if not r.get('error') and r['prompt_id'].split('_')[-1] in ('neutral','env')]
corpus = json.load(open(os.path.join(ANA,"country_corpus_measures.json")))

acc = {}
for r in rows: acc.setdefault(r['country_iso3'], []).append(r['composite'])
iso = sorted(acc)
df = pd.DataFrame({
    "accuracy":      [np.mean(acc[c]) for c in iso],
    "hdi":           [HDI[c] for c in iso],
    "log_sitelinks": [math.log(corpus[c]["wd_sitelinks"]) for c in iso],
})
z = (df - df.mean()) / df.std()   # standardize

DESC = """
log_sitelinks ~ a*hdi
accuracy ~ cp*hdi + b*log_sitelinks
"""
def fit_indirect(data):
    m = semopy.Model(DESC); m.fit(data)
    p = m.inspect()
    g = lambda lab: float(p[(p['lval']!="") & (p.apply(lambda r: r.get('label','')==lab if 'label' in p.columns else False, axis=1))]['Estimate'].iloc[0]) if 'label' in p.columns else None
    # robust extraction by op
    est = {}
    for _,r in p.iterrows():
        est[(r['lval'], r['op'], r['rval'])] = r['Estimate']
    a  = est.get(('log_sitelinks','~','hdi'))
    b  = est.get(('accuracy','~','log_sitelinks'))
    cp = est.get(('accuracy','~','hdi'))
    return a, b, cp

a, b, cp = fit_indirect(z)
indirect = a*b; total = cp + indirect
# bootstrap over countries
rng = np.random.default_rng(42); inds=[]
for _ in range(2000):
    idx = rng.integers(0, len(z), len(z))
    try:
        aa,bb,_ = fit_indirect(z.iloc[idx].reset_index(drop=True))
        inds.append(aa*bb)
    except Exception:
        pass
inds = np.array(inds); lo,hi = np.percentile(inds, [2.5,97.5])

print("="*70)
print("EXPLORATORY MEDIATION (H4), country-level, n=25 (standardized)")
print("="*70)
print(f"  a  (HDI -> sitelinks)        = {a:+.3f}")
print(f"  b  (sitelinks -> accuracy|HDI)= {b:+.3f}")
print(f"  c' (direct HDI -> accuracy)  = {cp:+.3f}")
print(f"  indirect (a*b)               = {indirect:+.3f}   95% boot CI [{lo:+.3f}, {hi:+.3f}]")
print(f"  total (c'+ab)                = {total:+.3f}")
prop = indirect/total if total else float('nan')
print(f"  proportion mediated          = {prop:.2f}")
print("  NOTE: n=25 -> strictly exploratory; CI crossing 0 => mediation not established.")
