"""
robust_tests.py — Formal tests for the ROBUST findings (where the power is).

H2 (language): Wilcoxon signed-rank on native-vs-English paired composites, overall
   and per language; Cliff's delta effect size.
Task floor: Kruskal-Wallis across the 5 tasks; T1+T2 vs others (Mann-Whitney).
H3 (regional model): Cabra-Mistral vs the rest (Mann-Whitney + Cliff's delta).
Tier gap: bootstrap CI for the GS-vs-GN composite gap, resampling countries
   (honest about the 3-GN limitation).

Stdlib only; deterministic seeds.
"""
from __future__ import annotations
import json, math, random, statistics
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SCORES = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_scores_confirmatory.jsonl"
GS = {"BRA","MEX","ARG","PER","NGA","ZAF","KEN","EGY","IND","IDN","BGD","PHL"}
GN = {"USA","DEU","JPN"}


def load():
    rows=[json.loads(l) for l in open(SCORES) if l.strip()]
    return [r for r in rows if 'composite' in r and not r.get('error')
            and 'JUDGE_API_ERROR' not in str(r.get('rationale',''))
            and '_AP_' in (r.get('prompt_id') or '')]

def normal_sf(z): return 1-0.5*(1+math.erf(z/math.sqrt(2)))

def wilcoxon(diffs):
    d=[x for x in diffs if x!=0]; n=len(d)
    if n<1: return float('nan'),float('nan'),0
    ad=sorted(range(n),key=lambda i:abs(d[i]))
    ranks=[0.0]*n; i=0
    while i<n:
        j=i
        while j+1<n and abs(d[ad[j+1]])==abs(d[ad[i]]): j+=1
        avg=(i+j)/2+1
        for k in range(i,j+1): ranks[ad[k]]=avg
        i=j+1
    Wp=sum(ranks[i] for i in range(n) if d[i]>0)
    Wm=sum(ranks[i] for i in range(n) if d[i]<0)
    W=min(Wp,Wm); mu=n*(n+1)/4; sd=math.sqrt(n*(n+1)*(2*n+1)/24)
    z=(W-mu)/sd if sd else 0; p=2*normal_sf(abs(z))
    return z,p,n

def cliffs_delta(a,b):
    gt=sum(1 for x in a for y in b if x>y); lt=sum(1 for x in a for y in b if x<y)
    return (gt-lt)/(len(a)*len(b)) if a and b else float('nan')

def mannwhitney(a,b):
    comb=sorted([(v,0) for v in a]+[(v,1) for v in b])
    ranks=[0.0]*len(comb); i=0
    while i<len(comb):
        j=i
        while j+1<len(comb) and comb[j+1][0]==comb[i][0]: j+=1
        avg=(i+j)/2+1
        for k in range(i,j+1): ranks[k]=avg
        i=j+1
    Ra=sum(ranks[k] for k in range(len(comb)) if comb[k][1]==0)
    na,nb=len(a),len(b); U=Ra-na*(na+1)/2; mu=na*nb/2; sd=math.sqrt(na*nb*(na+nb+1)/12)
    z=(U-mu)/sd if sd else 0; return z,2*normal_sf(abs(z))

def base(pid):
    for s in ('_pt','_es','_hi'):
        if pid.endswith(s): return pid[:-3], pid[-2:]
    return pid,'en'

def main():
    rows=load()
    print("=== ROBUST FINDINGS — formal tests ===\n")

    # H2 paired (native vs English), aggregate by (model, base prompt)
    bykey={}
    for r in rows:
        b,lang=base(r['prompt_id'])
        k=(r['model_id'],b); bykey.setdefault(k,{'en':[],'nat':[],'lang':None})
        if lang=='en': bykey[k]['en'].append(r['composite'])
        else: bykey[k]['nat'].append(r['composite']); bykey[k]['lang']=lang
    pairs=[(k,v) for k,v in bykey.items() if v['en'] and v['nat']]
    print("H2 — native vs English (Wilcoxon signed-rank, paired)")
    for lang in ['all','es','pt','hi']:
        diffs=[statistics.mean(v['nat'])-statistics.mean(v['en']) for k,v in pairs if lang=='all' or v['lang']==lang]
        if diffs:
            z,p,n=wilcoxon(diffs); med=statistics.mean(diffs)*100
            print(f"  {lang}: Δ={med:+.1f}pp  Wilcoxon z={z:+.2f}, p={p:.2e}  (n={n})")
    print()

    # Task floor
    bytask={}
    for r in rows:
        if base(r['prompt_id'])[1]!='en': continue
        bytask.setdefault(r.get('task'),[]).append(r['composite'])
    hard=[v for t in ('T1','T2') for v in bytask.get(t,[])]
    easy=[v for t in ('T3','T4','T5') for v in bytask.get(t,[])]
    z,p=mannwhitney(hard,easy)
    print("Task floor — factual recall (T1,T2) vs synthesis/recommendation (T3,T4,T5)")
    print(f"  T1+T2 mean={statistics.mean(hard):.3f}  vs  others={statistics.mean(easy):.3f}")
    print(f"  Mann-Whitney z={z:+.1f}, p={p:.2e}  Cliff's δ={cliffs_delta(hard,easy):+.2f}")
    print()

    # H3 regional model
    bymodel={}
    for r in rows:
        if base(r['prompt_id'])[1]!='en': continue
        bymodel.setdefault(r['model_id'],[]).append(r['composite'])
    cabra=bymodel.get('cabra_mistral_7b',[])
    rest=[v for m,vs in bymodel.items() if m!='cabra_mistral_7b' for v in vs]
    z,p=mannwhitney(cabra,rest)
    print("H3 — Cabra-Mistral (regional) vs all other models")
    print(f"  Cabra mean={statistics.mean(cabra):.3f}  vs  rest={statistics.mean(rest):.3f}")
    print(f"  Mann-Whitney z={z:+.1f}, p={p:.2e}  Cliff's δ={cliffs_delta(cabra,rest):+.2f}")
    print()

    # Tier gap bootstrap (resample countries — honest about 3 GN)
    bycountry={}
    for r in rows:
        if base(r['prompt_id'])[1]!='en': continue
        bycountry.setdefault(r['country_iso3'],[]).append(r['composite'])
    cmean={c:statistics.mean(v) for c,v in bycountry.items()}
    gs=[c for c in cmean if c in GS]; gn=[c for c in cmean if c in GN]
    obs=statistics.mean([cmean[c] for c in gn])-statistics.mean([cmean[c] for c in gs])
    rnd=random.Random(7); boots=[]
    for _ in range(5000):
        bg=[cmean[rnd.choice(gn)] for _ in gn]; bs=[cmean[rnd.choice(gs)] for _ in gs]
        boots.append(statistics.mean(bg)-statistics.mean(bs))
    boots.sort(); lo=boots[int(.025*len(boots))]; hi=boots[int(.975*len(boots))]
    print("Tier gap (GN-GS), bootstrap over countries (3 GN — limited power, honest CI)")
    print(f"  point={obs*100:+.1f}pp  95% CI [{lo*100:+.1f}, {hi*100:+.1f}] pp")
    print(f"  -> CI {'excludes' if lo>0 else 'includes'} zero")

if __name__=="__main__":
    main()
