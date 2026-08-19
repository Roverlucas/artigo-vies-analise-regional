"""
formal_tests.py — Pre-specified formal hypothesis tests (H1, H4, H6).

Country-level analysis on English-prompt confirmatory composites.
DEFAULT n=25 (reported sample); `--n15-prespecified` for the pre-specified subset:
  H1: Spearman rho(accuracy, HDI) and (accuracy, Joshi class), one-sided, plus Mann-Kendall.
  H4: Spearman rho(accuracy, log Wikipedia size) and PARTIAL rho controlling HDI (mechanism).
  H6: difference-in-differences (persona-neutral, GS vs GN) with 5000-permutation inference.
  Multiplicity: Bonferroni-Holm across the primary family {H1, H4, H6}.

Covariate sources (official): HDI = UNDP HDR 2023-24 (2022 data); Wikipedia article
counts = Wikimedia (List_of_Wikipedias, 2026); Joshi class = Joshi et al. 2020 by
dominant official language. Stdlib only; deterministic permutation seed.
"""
from __future__ import annotations
import json, math, random, statistics
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SCORES = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_scores_confirmatory.jsonl"
GS = {"BRA","MEX","ARG","PER","NGA","ZAF","KEN","EGY","IND","IDN","BGD","PHL"}
GN = {"USA","DEU","JPN"}
# Post-registration expansion (10 new countries). GS: COL, CHL, AGO. GN: rest.
GS_EXT = {"COL","CHL","AGO"}
GN_EXT = {"UK","CAN","AUS","KOR","FRA","ITA","PRT"}

# Official covariates (HDI: UNDP HDR23-24; Wiki: Wikimedia, millions of articles; Joshi: dominant official lang)
COV = {
 "USA":(0.927,7.19,5),"DEU":(0.950,3.13,5),"JPN":(0.920,1.51,5),
 "BRA":(0.760,1.17,4),"MEX":(0.781,2.12,5),"ARG":(0.849,2.12,5),"PER":(0.762,2.12,5),
 "IND":(0.644,7.19,5),"IDN":(0.713,0.78,3),"EGY":(0.728,1.32,5),"BGD":(0.670,0.19,3),
 "NGA":(0.548,7.19,5),"ZAF":(0.717,7.19,5),"KEN":(0.601,7.19,5),"PHL":(0.710,7.19,5),
}
# Expansion covariates (HDI: UNDP HDR23-24 2022; Wiki: language-edition millions; Joshi class)
COV_EXT = {
 "UK":(0.940,7.19,5),"CAN":(0.935,7.19,5),"AUS":(0.946,7.19,5),
 "FRA":(0.910,2.60,5),"ITA":(0.906,1.88,4),"KOR":(0.929,0.68,4),
 "COL":(0.758,2.12,5),"CHL":(0.860,2.12,5),"PRT":(0.874,1.17,4),"AGO":(0.591,1.17,4),
}


def rank(xs):
    order=sorted(range(len(xs)),key=lambda i:xs[i]); r=[0.0]*len(xs); i=0
    while i<len(xs):
        j=i
        while j+1<len(xs) and xs[order[j+1]]==xs[order[i]]: j+=1
        avg=(i+j)/2+1
        for k in range(i,j+1): r[order[k]]=avg
        i=j+1
    return r

def pearson(x,y):
    n=len(x); mx=sum(x)/n; my=sum(y)/n
    num=sum((a-mx)*(b-my) for a,b in zip(x,y))
    dx=math.sqrt(sum((a-mx)**2 for a in x)); dy=math.sqrt(sum((b-my)**2 for b in y))
    return num/(dx*dy) if dx and dy else float('nan')

def spearman(x,y):
    return pearson(rank(x),rank(y))

def partial_spearman(x,y,z):
    rxy=spearman(x,y); rxz=spearman(x,z); ryz=spearman(y,z)
    den=math.sqrt((1-rxz**2)*(1-ryz**2))
    return (rxy-rxz*ryz)/den if den else float('nan')

def p_from_r(r,n,partial=0):
    df=n-2-partial
    if abs(r)>=1 or df<=0: return 0.0
    t=r*math.sqrt(df/(1-r**2))
    # two-sided t-dist p via incomplete beta approx (use normal for df>=10 acceptably; here exact-ish)
    # simple: survival of t via regularized incomplete beta
    x=df/(df+t*t)
    return _betai(df/2,0.5,x)

def _betai(a,b,x):
    if x<=0: return 0.0
    if x>=1: return 1.0
    lbeta=math.lgamma(a)+math.lgamma(b)-math.lgamma(a+b)
    front=math.exp(a*math.log(x)+b*math.log(1-x)-lbeta)/a
    # continued fraction
    c=1.0; d=1-(a+b)*x/(a+1); d=1e-30 if abs(d)<1e-30 else 1/d; h=d
    for m in range(1,200):
        m2=2*m
        aa=m*(b-m)*x/((a+m2-1)*(a+m2))
        d=1+aa*d; d=1e-30 if abs(d)<1e-30 else 1/d
        c=1+aa/c; c=1e-30 if abs(c)<1e-30 else c; h*=d*c
        aa=-(a+m)*(a+b+m)*x/((a+m2)*(a+m2+1))
        d=1+aa*d; d=1e-30 if abs(d)<1e-30 else 1/d
        c=1+aa/c; c=1e-30 if abs(c)<1e-30 else c; de=d*c; h*=de
        if abs(de-1)<1e-10: break
    return front*h

def mann_kendall(y):
    n=len(y); S=0
    for i in range(n):
        for j in range(i+1,n):
            S+=(y[j]>y[i])-(y[j]<y[i])
    var=n*(n-1)*(2*n+5)/18
    if S>0: Z=(S-1)/math.sqrt(var)
    elif S<0: Z=(S+1)/math.sqrt(var)
    else: Z=0
    p=2*(1-0.5*(1+math.erf(abs(Z)/math.sqrt(2))))
    return S,Z,p

def main():
    import sys
    # DEFAULT = 25 countries, the sample the manuscript reports.
    # `--n15-prespecified` runs the smaller pre-specified subset, which yields the
    # OPPOSITE conclusion for H1 and H4. That subset is a reporting layer, not the
    # headline; running it by accident and quoting its numbers was a real hazard.
    use15 = ("--n15-prespecified" in sys.argv) or ("--n15" in sys.argv)
    use25 = not use15
    if use15:
        print("=" * 78)
        print("  PRE-SPECIFIED SUBSET (n=15) — NOT the values reported in the paper.")
        print("  The manuscript reports n=25. At n=15, H1 is null and the H4 partial")
        print("  correlation points the other way. Quote these only as the layer-1")
        print("  pre-specified result, never as the headline.")
        print("=" * 78)
    cov = {**COV, **COV_EXT} if use25 else dict(COV)
    gs = (GS | GS_EXT) if use25 else set(GS)
    rows=[json.loads(l) for l in open(SCORES) if l.strip()]
    rows=[r for r in rows if 'composite' in r and not r.get('error') and 'JUDGE_API_ERROR' not in str(r.get('rationale',''))]
    # English-only for country-level (exclude native _pt/_es/_hi)
    eng=[r for r in rows if '_AP_' in (r.get('prompt_id') or '') and not (r.get('prompt_id') or '').endswith(('_pt','_es','_hi'))]
    acc={}
    for c in cov:
        v=[r['composite'] for r in eng if r.get('country_iso3')==c]
        if v: acc[c]=statistics.mean(v)
    countries=[c for c in cov if c in acc]
    A=[acc[c] for c in countries]
    HDI=[cov[c][0] for c in countries]
    WIKI=[math.log(cov[c][1]) for c in countries]
    JOSHI=[cov[c][2] for c in countries]
    n=len(countries)

    print(f"=== FORMAL TESTS (country-level, n={n}, English prompts) ===\n")
    # H1
    r_hdi=spearman(A,HDI); p_hdi=p_from_r(r_hdi,n)
    r_jos=spearman(A,JOSHI); p_jos=p_from_r(r_jos,n)
    S,Z,p_mk=mann_kendall([a for _,a in sorted(zip(HDI,A))])
    print("H1 — geographic gradient")
    print(f"  Spearman rho(accuracy, HDI)       = {r_hdi:+.3f}  (two-sided p={p_hdi:.3f}; one-sided p={p_hdi/2:.3f})")
    print(f"  Spearman rho(accuracy, Joshi)     = {r_jos:+.3f}  (p={p_jos:.3f})")
    print(f"  Mann-Kendall (by HDI): S={S}, Z={Z:+.2f}, p={p_mk:.3f}")
    print(f"  threshold rho>=0.55 one-sided: {'MET' if r_hdi>=0.55 and p_hdi/2<0.05 else 'NOT met'}")
    # H4
    r_wiki=spearman(A,WIKI); p_wiki=p_from_r(r_wiki,n)
    pr=partial_spearman(A,WIKI,HDI); p_pr=p_from_r(pr,n,partial=1)
    print("\nH4 — corpus-representation mechanism")
    print(f"  Spearman rho(accuracy, log Wiki)         = {r_wiki:+.3f}  (p={p_wiki:.3f})")
    print(f"  PARTIAL rho(accuracy, Wiki | HDI)        = {pr:+.3f}  (p={p_pr:.3f})")
    print(f"  -> corpus {'retains' if abs(pr)>0.2 else 'loses'} association after controlling development")
    # H6 permutation
    def did(labels):
        gs=[a for a,l in zip(DA,labels) if l]; gn=[a for a,l in zip(DA,labels) if not l]
        return (statistics.mean(gs) if gs else 0)-(statistics.mean(gn) if gn else 0)
    # per-country persona delta
    DA=[]; lab=[]
    for c in countries:
        neu=[r['composite'] for r in eng if r.get('country_iso3')==c and r.get('persona')=='neutral']
        per=[r['composite'] for r in eng if r.get('country_iso3')==c and r.get('persona')=='public_manager_env']
        if neu and per:
            DA.append(statistics.mean(per)-statistics.mean(neu)); lab.append(c in gs)
    obs=did(lab)
    rnd=random.Random(42); ge=0; N=5000
    for _ in range(N):
        pl=lab[:]; rnd.shuffle(pl)
        if did(pl)>=obs: ge+=1
    p_did=ge/N
    print("\nH6 — persona x geography (difference-in-differences)")
    print(f"  observed DiD (GS-GN persona effect) = {obs*100:+.2f} pp")
    print(f"  permutation p (one-sided, 5000) = {p_did:.3f}  -> {'narrows' if obs>0 else 'no narrowing'}, NOT significant" if p_did>0.05 else f"  permutation p = {p_did:.3f} SIGNIFICANT")
    # Bonferroni-Holm on primary family {H1 (HDI), H4 (partial), H6}
    fam=[('H1 accuracy~HDI',p_hdi/2),('H4 partial Wiki|HDI',p_pr),('H6 DiD perm',p_did)]
    fam_sorted=sorted(fam,key=lambda t:t[1]); m=len(fam_sorted)
    print("\n=== Bonferroni-Holm (primary family, alpha=0.05) ===")
    for i,(name,p) in enumerate(fam_sorted):
        thr=0.05/(m-i)
        print(f"  {name}: p={p:.3f} vs {thr:.4f} -> {'reject H0' if p<thr else 'fail to reject'}")

if __name__=="__main__":
    main()
