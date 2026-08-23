#!/usr/bin/env python3
"""
weighting_and_evalue.py — two pre-specified analyses executed for real on the
confirmatory data (replacing previously-described-but-unrun methods):

  1. Composite-weighting sensitivity: recompute the headline effects under three
     weightings of the five judge subcomponents —
       (a) author-specified (the primary composite actually used): 0.30/0.25/0.15/0.15/0.15
       (b) equal weights: 0.20 each
       (c) PCA-derived: first principal component loadings (normalised, sign-aligned)
     A conclusion is robust only if it holds across all three.

  2. E-value sensitivity (VanderWeele & Ding 2017): how strong an unmeasured
     confounder would have to be to explain away each key association.

Pure numpy/scipy. Run from repo root:  python3 code/analysis/weighting_and_evalue.py
"""
import json
import sys, os, math
import numpy as np
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCORES = os.path.join(ROOT, "data/confirmatory_PRIVATE/analysis/judge_scores_corrected.jsonl" if "--original" not in sys.argv else "judge_scores_confirmatory.jsonl")

# HDI per country — UNDP HDR 2023-24 (2022 data); mirrors code/analysis/formal_tests.py
HDI = {"USA":0.927,"DEU":0.950,"JPN":0.920,"BRA":0.760,"MEX":0.781,"ARG":0.849,
 "PER":0.762,"IND":0.644,"IDN":0.713,"EGY":0.728,"BGD":0.670,"NGA":0.548,"ZAF":0.717,
 "KEN":0.601,"PHL":0.710,"UK":0.940,"CAN":0.935,"AUS":0.946,"FRA":0.910,"ITA":0.906,
 "KOR":0.929,"COL":0.758,"CHL":0.860,"PRT":0.874,"AGO":0.591}
GN = {"USA","DEU","JPN","UK","CAN","AUS","KOR","FRA","ITA","PRT"}
SUBS = ['factual_accuracy','contextual_completeness','citation_quality','calibration','absence_of_hallucination']

rows = [json.loads(l) for l in open(SCORES)]
rows = [r for r in rows if not r.get('error')]
def is_en(r): return r['prompt_id'].split('_')[-1] in ('neutral','env')
en = [r for r in rows if is_en(r)]
X = np.array([[r[s] for s in SUBS] for r in en])          # subcomponents
iso = np.array([r['country_iso3'] for r in en])
task = np.array([r['task'] for r in en])
model = np.array([r['model_id'] for r in en])

# ---- weightings ----
W_author = np.array([0.30,0.25,0.15,0.15,0.15])
W_equal  = np.array([0.20]*5)
# PCA on standardized subcomponents -> first PC loadings, normalised, positively oriented
Xs = (X - X.mean(0)) / X.std(0)
cov = np.cov(Xs, rowvar=False)
vals, vecs = np.linalg.eigh(cov)
pc1 = vecs[:, np.argmax(vals)]
if pc1.sum() < 0: pc1 = -pc1
W_pca = pc1 / pc1.sum()
WEIGHTINGS = {"author-specified (primary)": W_author, "equal": W_equal, "PCA-derived": W_pca}

def effects(comp):
    # country means
    cm = {c: comp[iso==c].mean() for c in set(iso)}
    gn = np.mean([cm[c] for c in cm if c in GN]); gs = np.mean([cm[c] for c in cm if c not in GN])
    cs = sorted(cm)
    rho,_ = stats.spearmanr([cm[c] for c in cs], [HDI[c] for c in cs])
    # task floor T1+T2 vs T3-T5 (Cliff's delta)
    a = comp[(task=='T1')|(task=='T2')]; b = comp[(task=='T3')|(task=='T4')|(task=='T5')]
    delta_floor = cliffs(a, b)
    # H3 cabra vs rest
    ca = comp[model=='cabra_mistral_7b']; rest = comp[model!='cabra_mistral_7b']
    delta_h3 = cliffs(ca, rest)
    return dict(tier_gap_pp=(gn-gs)*100, rho_hdi=rho, floor_delta=delta_floor, h3_delta=delta_h3)

def cliffs(a, b):
    # Cliff's delta via rank-sum (efficient)
    n1, n2 = len(a), len(b)
    U,_ = stats.mannwhitneyu(a, b, alternative='two-sided')
    return 2*U/(n1*n2) - 1

def evalue_from_d(d):
    # VanderWeele & Ding (2017) approximation: RR ~ exp(0.91*d); E = RR + sqrt(RR*(RR-1))
    rr = math.exp(0.91*abs(d))
    return rr + math.sqrt(rr*(rr-1))

print("="*74)
print("1) COMPOSITE-WEIGHTING SENSITIVITY (English confirmatory, n=%d responses)"%len(en))
print("="*74)
print("PCA-derived weights:", {s:round(w,3) for s,w in zip(SUBS,W_pca)})
print(f"\n{'weighting':28s} {'tier gap pp':>11s} {'rho(HDI)':>9s} {'floor d':>8s} {'H3 d':>7s}")
res={}
for name,w in WEIGHTINGS.items():
    comp = X@w
    e = effects(comp); res[name]=e
    print(f"{name:28s} {e['tier_gap_pp']:>+11.2f} {e['rho_hdi']:>+9.3f} {e['floor_delta']:>+8.3f} {e['h3_delta']:>+7.3f}")
print("\nRobustness: a conclusion holds if its sign/direction is stable across all three weightings.")
signs = lambda k: {np.sign(res[n][k]) for n in res}
for k,label in [('tier_gap_pp','tier gap > 0'),('rho_hdi','HDI gradient > 0'),
                ('floor_delta','task floor < 0'),('h3_delta','H3 (Cabra worst) < 0')]:
    stable = len(signs(k))==1
    print(f"  {label:24s}: {'ROBUST (sign stable)' if stable else 'NOT stable'} "
          f"[{', '.join(f'{res[n][k]:+.2f}' for n in res)}]")

print("\n"+"="*74)
print("2) E-VALUE SENSITIVITY (VanderWeele & Ding 2017)")
print("="*74)
# tier gap as Cohen's d (response-level GN vs GS)
gnv = (X@W_author)[np.isin(iso, list(GN))]; gsv = (X@W_author)[~np.isin(iso, list(GN))]
sp = math.sqrt(((len(gnv)-1)*gnv.var(ddof=1)+(len(gsv)-1)*gsv.var(ddof=1))/(len(gnv)+len(gsv)-2))
d_tier = (gnv.mean()-gsv.mean())/sp
# O E-value do PONTO estimado nunca deve ser reportado sozinho. VanderWeele &
# Ding (2017) pedem tambem o E-value do limite do intervalo de confianca mais
# proximo do nulo, e e esse que responde a pergunta que interessa: quao forte
# precisaria ser um confundidor para tornar o resultado compativel com nenhum
# efeito. Quando o intervalo ja inclui o nulo, esse E-value e 1,00 — nenhum
# confundidor e necessario — e reportar so o E-value do ponto sugeriria uma
# solidez que o dado nao tem.
cm = {c: (X@W_author)[iso == c].mean() for c in set(iso)}
cs = sorted(cm)


def boot_ci_gap(n=10000, semente=20260822):
    rng = np.random.default_rng(semente)
    gn_ = np.array([cm[c] for c in cs if c in GN])
    gs_ = np.array([cm[c] for c in cs if c not in GN])
    d = [rng.choice(gn_, len(gn_)).mean() - rng.choice(gs_, len(gs_)).mean()
         for _ in range(n)]
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


lo, hi = boot_ci_gap()
gap_pt = np.mean([cm[c] for c in cs if c in GN]) - np.mean([cm[c] for c in cs if c not in GN])
# o d escala com a diferenca de medias, entao o d do limite do IC e proporcional
d_tier_lo = d_tier * (lo / gap_pt) if gap_pt else 0.0

print(f"  H1 tier gap (GN vs GS)")
print(f"    point   : Cohen's d={d_tier:+.3f} -> E-value = {evalue_from_d(d_tier):.2f}")
print(f"    CI limit: 95% CI [{lo*100:+.2f},{hi*100:+.2f}] pp, nearest-null d="
      f"{d_tier_lo:+.3f} -> E-value = {evalue_from_d(d_tier_lo):.2f}")

rho_hdi, p_hdi = stats.spearmanr([cm[c] for c in cs], [HDI[c] for c in cs])
print(f"  H1 HDI gradient")
print(f"    NOT REPORTED as an E-value. rho={rho_hdi:+.3f}, p={p_hdi:.3f}: the")
print(f"    association does not reach significance, so its confidence interval")
print(f"    already includes the null and the nearest-null E-value is 1.00 — no")
print(f"    confounder is needed to explain it away. The exposure is also")
print(f"    continuous and measured at country level, which the risk-ratio")
print(f"    conversion assumes away.")
print("\n(E-value = minimum strength of association an unmeasured confounder would need")
print(" with BOTH tier and accuracy, on the risk-ratio scale, to explain away the effect.)")
