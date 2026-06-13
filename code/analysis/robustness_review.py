"""
robustness_review.py — Robustness checks requested by the internal review.

(1) Leave-one-country-out (LOCO) for the three primary effects at n=25:
    HDI gradient (Spearman), tier gap, and the sitelinks correlation — to test
    whether any single country (esp. India) drives them.
(2) H2 native-language penalty aggregated to COUNTRY level (n=9 native-pair
    countries), correcting the pseudo-replication of the per-cell Wilcoxon.
(3) FDR (Benjamini-Hochberg) across the three country-coverage proxies for H4.
(4) HDI-range restriction: re-estimate the HDI gradient on the 15-country HDI
    range, to test the range-extension critique.
"""
from __future__ import annotations
import json, math, statistics
from pathlib import Path
from code.analysis.formal_tests import spearman, p_from_r, COV, COV_EXT
from code.analysis.robust_tests import wilcoxon, base as h2base

A = Path(__file__).parent.parent.parent / "data" / "confirmatory_PRIVATE" / "analysis"
SCORES = A / "judge_scores_confirmatory.jsonl"
CCORP = A / "country_corpus_measures.json"
COV25 = {**COV, **COV_EXT}
GN = {"USA","DEU","JPN","UK","CAN","AUS","KOR","FRA","ITA","PRT"}


def load():
    rows=[json.loads(l) for l in open(SCORES) if l.strip()]
    return [r for r in rows if r.get('composite') is not None and not r.get('error')]


def eng_acc(rows):
    eng=[r for r in rows if '_AP_' in (r.get('prompt_id') or '') and not (r.get('prompt_id') or '').endswith(('_pt','_es','_hi'))]
    acc={}
    for r in eng: acc.setdefault(r['country_iso3'],[]).append(r['composite'])
    return {c:statistics.mean(v) for c,v in acc.items() if v}


def main():
    rows=load(); acc=eng_acc(rows)
    cc=json.loads(CCORP.read_text())
    countries=[c for c in COV25 if c in acc]
    print(f"=== ROBUSTNESS (n={len(countries)} countries) ===\n")

    # (1) LOCO for HDI gradient, tier gap, sitelinks
    def hdi_rho(cs): return spearman([acc[c] for c in cs],[COV25[c][0] for c in cs])
    def tier_gap(cs):
        gn=[acc[c] for c in cs if c in GN]; gs=[acc[c] for c in cs if c not in GN]
        return statistics.mean(gn)-statistics.mean(gs)
    def site_rho(cs):
        cs2=[c for c in cs if (cc.get(c) or {}).get('wd_sitelinks')]
        return spearman([acc[c] for c in cs2],[math.log(cc[c]['wd_sitelinks']) for c in cs2])
    full_hdi=hdi_rho(countries); full_gap=tier_gap(countries); full_site=site_rho(countries)
    print(f"(1) Leave-one-country-out range (full: HDI rho={full_hdi:+.3f}, gap={full_gap*100:+.1f}pp, sitelinks rho={full_site:+.3f})")
    for label,fn,full in (("HDI gradient",hdi_rho,full_hdi),("tier gap",tier_gap,full_gap),("sitelinks rho",site_rho,full_site)):
        vals=[(c,fn([x for x in countries if x!=c])) for c in countries]
        lo=min(vals,key=lambda t:t[1]); hi=max(vals,key=lambda t:t[1])
        scale=100 if "gap" in label else 1; unit="pp" if "gap" in label else ""
        print(f"  {label:14s}: range [{lo[1]*scale:+.3f}{unit} (drop {lo[0]}), {hi[1]*scale:+.3f}{unit} (drop {hi[0]})]")
        noind=fn([x for x in countries if x!='IND'])
        print(f"                  without India: {noind*scale:+.3f}{unit}  (full {full*scale:+.3f}{unit})")

    # (4) HDI-range restriction: restrict 25-country set to the 15-country HDI range
    hdi15=[COV[c][0] for c in COV]; lo15,hi15=min(hdi15),max(hdi15)
    inrange=[c for c in countries if lo15<=COV25[c][0]<=hi15]
    print(f"\n(4) Restrict to 15-country HDI range [{lo15:.3f},{hi15:.3f}]: {len(inrange)} countries, HDI rho={hdi_rho(inrange):+.3f} (p={p_from_r(hdi_rho(inrange),len(inrange)):.3f})")

    # (2) H2 country-level (n=9). Pair EN and native by (model, base prompt).
    en={}; nat={}
    for r in rows:
        pid=r.get('prompt_id') or ''
        key=(r['model_id'], h2base(pid)[0])  # base()[0] = prompt id without lang suffix
        if pid.endswith(('_pt','_es','_hi')): nat[key]=r['composite']
        elif '_AP_' in pid: en[key]=r['composite']
    bycountry={}
    for key in set(en) & set(nat):
        iso=key[1].split('_')[0]
        bycountry.setdefault(iso,[]).append(nat[key]-en[key])
    cdelta={c:statistics.mean(v) for c,v in bycountry.items() if v}
    deltas=list(cdelta.values())
    z,p,_=wilcoxon(deltas)
    print(f"\n(2) H2 country-level (n={len(deltas)} native-pair countries, corrects pseudo-replication):")
    for c,dd in sorted(cdelta.items(),key=lambda t:t[1]): print(f"     {c}: {dd*100:+.1f}pp")
    print(f"     mean={statistics.mean(deltas)*100:+.1f}pp  Wilcoxon z={z:+.2f}, p={p:.3f}  (sign: {sum(1 for d in deltas if d<0)}/{len(deltas)} negative)")

    # (3) FDR across 3 country-coverage proxies
    print(f"\n(3) Country-coverage proxies + Benjamini-Hochberg FDR:")
    ps=[]
    for key in ("wd_sitelinks","wd_statements","en_wiki_bytes"):
        cs=[c for c in countries if (cc.get(c) or {}).get(key)]
        r=spearman([acc[c] for c in cs],[math.log(cc[c][key]) for c in cs])
        p=p_from_r(r,len(cs)); ps.append((key,r,p))
    ps_sorted=sorted(ps,key=lambda t:t[2]); m=len(ps_sorted)
    for i,(key,r,p) in enumerate(ps_sorted):
        bh=p*m/(i+1)
        print(f"     {key:14s} rho={r:+.3f} p={p:.3f}  BH-adj={min(bh,1):.3f}  {'sig' if bh<0.05 else 'ns'}")


if __name__=="__main__":
    main()
