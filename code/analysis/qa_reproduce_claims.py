"""Reproducao da LINHA DE BASE PRE-CORRECAO (historica).

ATENCAO AO ESCOPO — este script NAO valida os numeros do manuscrito atual.

Ele recomputa, a partir de judge_scores_confirmatory.jsonl, os valores da analise
ORIGINAL: lacuna de camada +6.2 pp, H1 rho=0.512, H2 -2.1 pp. Esses numeros foram
substituidos quando o gabarito de T2/T3 foi reconstruido, a adjudicacao passou
para codigo e a unidade de analise virou a celula deduplicada. O manuscrito hoje
relata +5.4 pp, rho=0.41 e -4.8 pp.

Por isso o "ALL CLAIMS REPRODUCED" daqui significa apenas que a linha de base
historica continua reproduzivel — util para documentar de onde o estudo saiu, e
inutil como prova de que o artigo submetido esta correto. Uma auditoria externa
leu este script como gate dos numeros atuais e concluiu, com razao, que ele era
falso-positivo nesse papel.

O gate dos numeros do manuscrito e consistency_gate.py, que deriva tudo de
freeze_all_effects.json["corrigido"].
"""
#!/usr/bin/env python3
"""
qa_reproduce_claims.py — reproducible integrity QA for the manuscript + supplement.

For every headline number asserted in the paper, recompute it from the RAW data
(or by re-running the committed analysis scripts) and assert it matches the value
stated in the .tex sources, within tolerance. This is the M4 (label/data error)
and M5 (impossible arithmetic) defense: no reported number is taken on trust.

Run from repo root:
    python3 code/analysis/qa_reproduce_claims.py
Exit code 0 = all claims reproduced; 1 = at least one mismatch.
"""
import json, os, subprocess, sys, re, collections, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANA  = os.path.join(ROOT, "data", "confirmatory_PRIVATE", "analysis")
SCORES = os.path.join(ANA, "judge_scores_confirmatory.jsonl")

results = []  # (ok, claim, expected, got, source)
def check(claim, expected, got, source, tol=0.001):
    if isinstance(expected,(int,float)) and isinstance(got,(int,float)):
        ok = abs(expected-got) <= tol
    else:
        ok = (str(expected)==str(got))
    results.append((ok, claim, expected, got, source))

# ---------------------------------------------------------------------------
# A. Recompute descriptive statistics from raw judge scores
# ---------------------------------------------------------------------------
rows = [json.loads(l) for l in open(SCORES)]
rows = [r for r in rows if not r.get("error")]
def is_en(r): return r["prompt_id"].split("_")[-1] in ("neutral","env")
en = [r for r in rows if is_en(r)]

# counts (main Results: 9,251 total / 7,580 English / 1,671 native)
check("N total scored", 9251, len(rows), "04_results.tex:26 / supplement S0")
check("N English",      7580, len(en),   "04_results.tex:26 / supplement S0")
check("N native",       1671, len(rows)-len(en), "00_abstract / supplement S0")

# per-model N + mean (main Table tab:conf-model / supplement Table S1)
EXP_MODEL = {
 "gpt5":(780,0.647),"gpt5_mini":(777,0.626),"deepseek_v3":(500,0.625),
 "gemini_flash":(490,0.604),"claude_haiku":(490,0.597),"qwen3_32b":(498,0.546),
 "command_rp":(500,0.509),"llama33_70b":(474,0.506),"gpt_oss_120b":(298,0.485),
 "phi4_14b":(500,0.485),"qwen3_14b":(500,0.474),"llama4_scout":(500,0.473),
 "llama31_8b":(777,0.424),"cabra_mistral_7b":(496,0.320),
}
bym = collections.defaultdict(list)
for r in en: bym[r["model_id"]].append(r["composite"])
for m,(eN,eMean) in EXP_MODEL.items():
    check(f"model {m} N", eN, len(bym[m]), "tab:conf-model / S1", tol=0)
    check(f"model {m} mean", eMean, round(statistics.mean(bym[m]),3), "tab:conf-model / S1", tol=0.0005)

# per-task N + mean (main Table tab:conf-task)
EXP_TASK = {"T1":(1529,0.367),"T2":(1530,0.368),"T3":(1519,0.567),
            "T4":(1494,0.574),"T5":(1508,0.773)}
byt = collections.defaultdict(list)
for r in en: byt[r["task"]].append(r["composite"])
for t,(eN,eMean) in EXP_TASK.items():
    check(f"task {t} N", eN, len(byt[t]), "tab:conf-task", tol=0)
    check(f"task {t} mean", eMean, round(statistics.mean(byt[t]),3), "tab:conf-task", tol=0.0005)

# tier gap GN-GS (main: +6.2 pp); recompute country-mean then tier mean
GN = {"USA","DEU","JPN","UK","CAN","AUS","KOR","FRA","ITA","PRT"}
byc = collections.defaultdict(list)
for r in en: byc[r["country_iso3"]].append(r["composite"])
cmean = {c:statistics.mean(v) for c,v in byc.items()}
gn = statistics.mean([cmean[c] for c in cmean if c in GN])
gs = statistics.mean([cmean[c] for c in cmean if c not in GN])
check("tier gap GN-GS (pp)", 6.2, round((gn-gs)*100,1), "04_results.tex H1 / S11", tol=0.15)

# task floor (T1+T2 vs T3-T5 means, English)
f12 = statistics.mean([byt["T1"]+byt["T2"]][0])
fothers = statistics.mean(byt["T3"]+byt["T4"]+byt["T5"])
check("task floor T1+T2 mean", 0.367, round(f12,3), "robust S11", tol=0.002)
check("task floor T3-T5 mean", 0.638, round(fothers,3), "robust S11", tol=0.002)

# H3 Cabra vs rest (English means)
cabra = statistics.mean(bym["cabra_mistral_7b"])
rest  = statistics.mean([c for m,v in bym.items() if m!="cabra_mistral_7b" for c in v])
check("H3 Cabra mean", 0.320, round(cabra,3), "S11", tol=0.002)
check("H3 rest mean",  0.543, round(rest,3),  "S11", tol=0.002)

# ---------------------------------------------------------------------------
# B. Re-run committed analysis scripts and parse their statistics
# ---------------------------------------------------------------------------
def run(script, *args):
    p = subprocess.run([sys.executable, os.path.join("code","analysis",script), *args],
                       cwd=ROOT, capture_output=True, text=True)
    return p.stdout + p.stderr

ft = run("formal_tests.py","--n25")
def grab(pat, text, cast=float):
    m = re.search(pat, text);  return cast(m.group(1)) if m else None
check("H1 rho(acc,HDI) n=25", 0.512, grab(r"rho\(accuracy, HDI\)\s*=\s*([+\-0-9.]+)", ft), "tab:s-primary", tol=0.002)
check("H1 one-sided p",       0.004, grab(r"HDI\).*?one-sided p=([0-9.]+)", ft), "tab:s-primary", tol=0.001)
check("H1 rho(acc,Joshi)",   -0.061, grab(r"rho\(accuracy, Joshi\)\s*=\s*([+\-0-9.]+)", ft), "tab:s-primary", tol=0.002)
check("H1 Mann-Kendall Z",    2.36,  grab(r"Mann-Kendall.*?Z=\+?([0-9.]+)", ft), "tab:s-primary", tol=0.01)
check("H1 Mann-Kendall p",    0.018, grab(r"Mann-Kendall.*?p=([0-9.]+)", ft), "tab:s-primary", tol=0.001)
check("H4 partial Wiki|HDI",  0.036, grab(r"Wiki \| HDI\)\s*=\s*\+?([0-9.]+)", ft), "tab:s-primary", tol=0.002)
check("H6 DiD (pp)",          0.39,  grab(r"DiD \(GS-GN persona effect\) = \+?([0-9.]+)", ft), "tab:s-primary", tol=0.02)
check("H6 permutation p",     0.257, grab(r"permutation p \(one-sided, 5000\) = ([0-9.]+)", ft), "tab:s-primary", tol=0.02)

rt = run("robust_tests.py","--n25")
check("H2 all delta (pp)", -2.1, grab(r"all: Δ=([+\-0-9.]+)pp", rt), "tab:s-robust", tol=0.05)
check("H2 all Wilcoxon p", 1.96e-3, grab(r"all:.*?p=([0-9.e\-]+)", rt), "tab:s-robust", tol=5e-5)
check("Task floor delta", -0.64, grab(r"Cliff's δ=([+\-0-9.]+)", rt), "tab:s-robust", tol=0.01)
check("Tier gap point (pp)", 6.2, grab(r"point=\+?([0-9.]+)pp", rt), "tab:s-robust", tol=0.05)

# ---------------------------------------------------------------------------
# C. Recompute H4 sitelinks correlation INDEPENDENTLY (supplement Table S10)
# ---------------------------------------------------------------------------
import math
corpus = json.load(open(os.path.join(ANA,"country_corpus_measures.json")))
def rank(xs):
    order=sorted(range(len(xs)),key=lambda i:xs[i]); r=[0.0]*len(xs); i=0
    while i<len(xs):
        j=i
        while j+1<len(xs) and xs[order[j+1]]==xs[order[i]]: j+=1
        for k in range(i,j+1): r[order[k]]=(i+j)/2+1
        i=j+1
    return r
def pear(x,y):
    n=len(x);mx=sum(x)/n;my=sum(y)/n
    num=sum((a-mx)*(b-my) for a,b in zip(x,y))
    dx=math.sqrt(sum((a-mx)**2 for a in x));dy=math.sqrt(sum((b-my)**2 for b in y))
    return num/(dx*dy) if dx and dy else float('nan')
def spear(x,y): return pear(rank(x),rank(y))
cs = sorted(cmean)
acc = [cmean[c] for c in cs]
sl  = [math.log(corpus[c]["wd_sitelinks"]) for c in cs]
check("H4 sitelinks rho (zero-order)", 0.539, round(spear(acc,sl),3), "tab:s-h4", tol=0.01)

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
n_ok = sum(1 for r in results if r[0]); n = len(results)
print(f"\n{'='*72}\nREPRODUCIBLE QA — {n_ok}/{n} claims reproduced from raw data\n{'='*72}")
for ok,claim,exp,got,src in results:
    if not ok:
        print(f"  [FAIL] {claim:32s} paper={exp}  recomputed={got}  ({src})")
print(f"\n{'ALL CLAIMS REPRODUCED ✓' if n_ok==n else f'{n-n_ok} MISMATCH(ES) — investigate above'}")
sys.exit(0 if n_ok==n else 1)
