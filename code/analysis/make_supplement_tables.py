#!/usr/bin/env python3
"""
make_supplement_tables.py — regenerate all data-driven Supplementary tables
from the raw confirmatory artifacts. Reproducibility-first: every number in the
Supplementary LaTeX tables traces to a file under data/confirmatory_PRIVATE/.

Run from the repo root:
    python3 code/analysis/make_supplement_tables.py

Inputs (raw, versioned):
  data/confirmatory_PRIVATE/analysis/judge_scores_confirmatory.jsonl   (9,251 scores, gpt-5-mini-2025-08-07 judge)
  data/confirmatory_PRIVATE/analysis/country_corpus_measures.json      (Wikidata/Wikipedia coverage per country)
  data/confirmatory_PRIVATE/analysis/ground_truth_registry_verified.jsonl (T1 official-source registry)

Embedded constants (with provenance, NOT invented):
  ROSTER  mirrors code/benchmark/config.py  (LLMS tuple: api_model_string, tier, vendor, venue, params)
  COV     mirrors code/analysis/formal_tests.py COV/COV_EXT (HDI: UNDP HDR 2023-24, 2022 data; Joshi: Joshi et al. 2020)

Outputs: latex/supplement/tables/*.tex
"""
import json, os, collections, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANA  = os.path.join(ROOT, "data", "confirmatory_PRIVATE", "analysis")
OUT  = os.path.join(ROOT, "latex", "supplement", "tables")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# Provenance constants
# ---------------------------------------------------------------------------
# Model roster — mirrors code/benchmark/config.py (LLMS, full_scope models only).
# (display, vendor, tier_letter, api_model_string, venue, params_B)
ROSTER = {
 "gpt5":            ("GPT-5",            "OpenAI",    "E", "gpt-5",                                   "OpenAI API",       None),
 "gpt5_mini":       ("GPT-5-mini",       "OpenAI",    "D", "gpt-5-mini",                              "OpenAI API",       None),
 "deepseek_v3":     ("DeepSeek-V3",      "DeepSeek",  "A", "deepseek-chat",                           "DeepSeek API",     671.0),
 "gemini_flash":    ("Gemini 2.5 Flash", "Google",   "D", "gemini-2.5-flash",                        "Google AI (free)", None),
 "claude_haiku":    ("Claude Haiku 4.5", "Anthropic","D", "claude-haiku-4-5",                        "Anthropic API",    None),
 "qwen3_32b":       ("Qwen3 32B",        "Alibaba",   "B", "qwen/qwen3-32b",                          "Groq (free)",      32.0),
 "command_rp":      ("Command R+",       "Cohere",    "A", "command-r-plus-08-2024",                  "Cohere (trial)",   104.0),
 "llama33_70b":     ("Llama 3.3 70B",    "Meta",      "A", "llama-3.3-70b-versatile",                 "Groq (free)",      70.0),
 "gpt_oss_120b":    ("GPT-OSS 120B",     "OpenAI",    "A", "openai/gpt-oss-120b",                     "Groq (free)",      120.0),
 "phi4_14b":        ("Phi-4 14B",        "Microsoft", "B", "phi4",                                    "Ollama (local)",   14.7),
 "qwen3_14b":       ("Qwen3 14B",        "Alibaba",   "B", "qwen3:14b",                               "Ollama (local)",   14.0),
 "llama4_scout":    ("Llama 4 Scout",    "Meta",      "A", "meta-llama/llama-4-scout-17b-16e-instruct","Groq (free)",     17.0),
 "llama31_8b":      ("Llama 3.1 8B",     "Meta",      "C", "llama-3.1-8b-instant",                    "Groq (free)",      8.0),
 "cabra_mistral_7b":("Cabra-Mistral 7B", "botbot-ai", "C", "cabra-mistral-7b",                        "Ollama (local)",   7.0),
}
TIER_LABEL = {"A":"A (open frontier)","B":"B (open mid)","C":"C (open small/regional)",
              "D":"D (closed accessible)","E":"E (closed frontier)"}

# Country covariates — mirrors code/analysis/formal_tests.py COV + COV_EXT.
# (HDI, Joshi class of dominant official language); HDI = UNDP HDR 2023-24 (2022 data).
HDI_JOSHI = {
 "USA":(0.927,5),"DEU":(0.950,5),"JPN":(0.920,5),"BRA":(0.760,4),"MEX":(0.781,5),
 "ARG":(0.849,5),"PER":(0.762,5),"IND":(0.644,5),"IDN":(0.713,3),"EGY":(0.728,5),
 "BGD":(0.670,3),"NGA":(0.548,5),"ZAF":(0.717,5),"KEN":(0.601,5),"PHL":(0.710,5),
 "UK":(0.940,5),"CAN":(0.935,5),"AUS":(0.946,5),"FRA":(0.910,5),"ITA":(0.906,4),
 "KOR":(0.929,4),"COL":(0.758,5),"CHL":(0.860,5),"PRT":(0.874,4),"AGO":(0.591,4),
}
# Pre-registered original 15-country set (everything else is the post-registration extension).
PREREG_15 = {"USA","DEU","JPN","BRA","MEX","ARG","PER","IND","IDN","EGY","BGD","NGA","ZAF","KEN","PHL"}
# Tier classification (UNCTAD Global North/South). GN_EXT mirrors formal_tests.py.
GN = {"USA","DEU","JPN","UK","CAN","AUS","KOR","FRA","ITA","PRT"}
NATIVE_LANG = {"pt":"Portuguese","es":"Spanish","hi":"Hindi"}

NAMES = {  # ISO3 -> display
 "USA":"United States","DEU":"Germany","JPN":"Japan","BRA":"Brazil","MEX":"Mexico",
 "ARG":"Argentina","PER":"Peru","IND":"India","IDN":"Indonesia","EGY":"Egypt",
 "BGD":"Bangladesh","NGA":"Nigeria","ZAF":"South Africa","KEN":"Kenya","PHL":"Philippines",
 "UK":"United Kingdom","CAN":"Canada","AUS":"Australia","FRA":"France","ITA":"Italy",
 "KOR":"South Korea","COL":"Colombia","CHL":"Chile","PRT":"Portugal","AGO":"Angola",
}

def tex_escape(s): return s.replace("&","\\&").replace("_","\\_").replace("%","\\%").replace("+","+")

# ---------------------------------------------------------------------------
# Load raw data
# ---------------------------------------------------------------------------
rows = [json.loads(l) for l in open(os.path.join(ANA,"judge_scores_confirmatory.jsonl"))]
rows = [r for r in rows if not r.get("error")]
corpus = json.load(open(os.path.join(ANA,"country_corpus_measures.json")))
gt = [json.loads(l) for l in open(os.path.join(ANA,"ground_truth_registry_verified.jsonl"))]

def lang_of(r):
    suf = r["prompt_id"].split("_")[-1]
    return suf if suf in NATIVE_LANG else "en"
def is_en(r): return lang_of(r) == "en"

JUDGE = rows[0]["judge_model"]
N_TOTAL = len(rows)
N_EN = sum(1 for r in rows if is_en(r))
N_NATIVE = N_TOTAL - N_EN

# ---------------------------------------------------------------------------
# Table S: model roster + realized coverage (English) + mean composite
# ---------------------------------------------------------------------------
by_model_en = collections.defaultdict(list)
for r in rows:
    if is_en(r): by_model_en[r["model_id"]].append(r["composite"])

lines = [
 r"% AUTO-GENERATED by code/analysis/make_supplement_tables.py — do not edit by hand",
 r"\begin{longtable}{p{2.6cm}llp{4.4cm}lrr}",
 r"\caption{Deployment-stack roster. Each model is evaluated \emph{as served} through a fixed access stack; the API/tag string and execution venue are part of what each label denotes. Parameter counts are vendor-reported (dense or total for MoE; closed-frontier counts undisclosed). $N$ and mean are realized English-prompt confirmatory coverage.\label{tab:s-roster}}\\",
 r"\toprule",
 r"Model & Vendor & Tier & API / tag string & Venue & $N$ & Mean \\",
 r"\midrule \endfirsthead",
 r"\toprule Model & Vendor & Tier & API / tag string & Venue & $N$ & Mean \\ \midrule \endhead",
]
# order by tier then mean desc
for mid,(disp,vendor,tier,api,venue,p) in sorted(
        ROSTER.items(), key=lambda kv:(kv[1][2], -statistics.mean(by_model_en[kv[0]]))):
    vals = by_model_en[mid]
    lines.append("%s & %s & %s & \\texttt{%s} & %s & %d & %.3f \\\\" % (
        tex_escape(disp), vendor, tier, tex_escape(api), venue, len(vals), statistics.mean(vals)))
lines += [r"\bottomrule", r"\end{longtable}"]
open(os.path.join(OUT,"tab_s_roster.tex"),"w").write("\n".join(lines)+"\n")

# ---------------------------------------------------------------------------
# Table S: coverage matrix model x task (English N)
# ---------------------------------------------------------------------------
tasks = ["T1","T2","T3","T4","T5"]
cov_mt = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    if is_en(r): cov_mt[r["model_id"]][r["task"]] += 1
lines = [
 r"% AUTO-GENERATED by code/analysis/make_supplement_tables.py",
 r"\begin{longtable}{p{2.8cm}rrrrrr}",
 r"\caption{Coverage matrix: realized English-prompt confirmatory responses per model $\times$ task (T1 standard, T2 local datum, T3 health synthesis, T4 instruments, T5 recommendation). No cell is silently dropped; shortfalls are quota-driven (Methods).\label{tab:s-cov-task}}\\",
 r"\toprule",
 r"Model & T1 & T2 & T3 & T4 & T5 & Total \\",
 r"\midrule \endfirsthead",
 r"\toprule Model & T1 & T2 & T3 & T4 & T5 & Total \\ \midrule \endhead",
]
for mid,(disp,*_) in sorted(ROSTER.items(), key=lambda kv:-sum(cov_mt[kv[0]].values())):
    c = cov_mt[mid]; tot = sum(c.values())
    lines.append("%s & %d & %d & %d & %d & %d & %d \\\\" % (
        tex_escape(disp), c["T1"],c["T2"],c["T3"],c["T4"],c["T5"], tot))
# column totals
colt = {t:sum(cov_mt[m][t] for m in ROSTER) for t in tasks}
lines.append(r"\midrule")
lines.append("\\textbf{Total} & %d & %d & %d & %d & %d & %d \\\\" % (
    colt["T1"],colt["T2"],colt["T3"],colt["T4"],colt["T5"], sum(colt.values())))
lines += [r"\bottomrule", r"\end{longtable}"]
open(os.path.join(OUT,"tab_s_cov_task.tex"),"w").write("\n".join(lines)+"\n")

# ---------------------------------------------------------------------------
# Table S: coverage by country (EN + native) and tier
# ---------------------------------------------------------------------------
cov_country = collections.defaultdict(lambda: collections.Counter())
for r in rows:
    cov_country[r["country_iso3"]]["en" if is_en(r) else "native"] += 1
lines = [
 r"% AUTO-GENERATED by code/analysis/make_supplement_tables.py",
 r"\begin{longtable}{llcrrr}",
 r"\caption{Coverage by country: tier (GN/GS), pre-registration status (P = pre-registered 15; E = post-registration extension), and realized confirmatory responses (English, native-language, total).\label{tab:s-cov-country}}\\",
 r"\toprule",
 r"Country & Tier & Set & English & Native & Total \\",
 r"\midrule \endfirsthead",
 r"\toprule Country & Tier & Set & English & Native & Total \\ \midrule \endhead",
]
for iso in sorted(cov_country, key=lambda k:-sum(cov_country[k].values())):
    c = cov_country[iso]; tier = "GN" if iso in GN else "GS"
    st = "P" if iso in PREREG_15 else "E"
    lines.append("%s & %s & %s & %d & %d & %d \\\\" % (
        NAMES[iso], tier, st, c["en"], c["native"], c["en"]+c["native"]))
lines.append(r"\midrule")
lines.append("\\textbf{Total (25)} & & & %d & %d & %d \\\\" % (N_EN, N_NATIVE, N_TOTAL))
lines += [r"\bottomrule", r"\end{longtable}"]
open(os.path.join(OUT,"tab_s_cov_country.tex"),"w").write("\n".join(lines)+"\n")

# ---------------------------------------------------------------------------
# Table S: native-language pairs (H2)
# ---------------------------------------------------------------------------
nat = collections.defaultdict(lambda: collections.Counter())  # lang -> country -> N
for r in rows:
    l = lang_of(r)
    if l != "en": nat[l][r["country_iso3"]] += 1
lines = [
 r"% AUTO-GENERATED by code/analysis/make_supplement_tables.py",
 r"\begin{longtable}{llr}",
 r"\caption{Native-language confirmatory responses by language and country (H2 within-country English/native contrast).\label{tab:s-native}}\\",
 r"\toprule Native language (Joshi) & Country & $N$ (native) \\ \midrule \endfirsthead",
 r"\toprule Native language (Joshi) & Country & $N$ (native) \\ \midrule \endhead",
]
joshi_lang = {"pt":4,"es":5,"hi":4}
for l in ["pt","es","hi"]:
    countries = sorted(nat[l], key=lambda k:-nat[l][k])
    for i,iso in enumerate(countries):
        lname = "%s (%d)"%(NATIVE_LANG[l],joshi_lang[l]) if i==0 else ""
        lines.append("%s & %s & %d \\\\" % (lname, NAMES[iso], nat[l][iso]))
    lines.append(r"\addlinespace")
lines += [r"\bottomrule", r"\end{longtable}"]
open(os.path.join(OUT,"tab_s_native.tex"),"w").write("\n".join(lines)+"\n")

# ---------------------------------------------------------------------------
# Table S: country covariates (HDI, Joshi, corpus measures)
# ---------------------------------------------------------------------------
lines = [
 r"% AUTO-GENERATED by code/analysis/make_supplement_tables.py",
 r"\begin{longtable}{llrrrrr}",
 r"\caption{Country covariates. HDI: UNDP HDR 2023--24 (2022 data). Joshi: linguistic-resource class of the dominant official language~\citep{joshi2020state}. Corpus measures from Wikimedia/Wikidata (entity QID resolvable): English-article byte length, Wikidata sitelinks (language editions), and Wikidata statements.\label{tab:s-covariates}}\\",
 r"\toprule",
 r"Country & Tier & HDI & Joshi & EN-wiki bytes & Sitelinks & WD stmts \\",
 r"\midrule \endfirsthead",
 r"\toprule Country & Tier & HDI & Joshi & EN-wiki bytes & Sitelinks & WD stmts \\ \midrule \endhead",
]
for iso in sorted(HDI_JOSHI, key=lambda k:-HDI_JOSHI[k][0]):
    hdi,joshi = HDI_JOSHI[iso]; cm = corpus[iso]; tier = "GN" if iso in GN else "GS"
    lines.append("%s & %s & %.3f & %d & %s & %d & %d \\\\" % (
        NAMES[iso], tier, hdi, joshi,
        format(cm["en_wiki_bytes"], ","), cm["wd_sitelinks"], cm["wd_statements"]))
lines += [r"\bottomrule", r"\end{longtable}"]
open(os.path.join(OUT,"tab_s_covariates.tex"),"w").write("\n".join(lines)+"\n")

# ---------------------------------------------------------------------------
# Table S: ground-truth registry (T1)
# ---------------------------------------------------------------------------
def _units(t):
    """ug/m3 -> simbolo; PM2.5 -> subscrito. So no corpo, nunca em comando LaTeX."""
    if t.lstrip().startswith(("\\begin","\\end","\\toprule","\\midrule","\\bottomrule","%","\\footnotesize","\\normalsize")):
        return t
    return t.replace("ug/m3", "$\\mu$g/m\\textsuperscript{3}").replace("PM2.5", "PM\\textsubscript{2.5}")

lines = [
 r"% AUTO-GENERATED by code/analysis/make_supplement_tables.py",
 r"\footnotesize", 
 r"\begin{longtable}{p{2.0cm}p{3.7cm}p{2.7cm}p{4.6cm}}",
 r"\caption{Ground-truth registry for T1 (binding annual PM\textsubscript{2.5} standard), all 25 countries, anchored to official primary sources by documentary audit. All entries are of source type \emph{official primary} unless noted. Status VERIFIED = value read from the official text; VERIFIED\_NO\_STANDARD = official confirmation that no national standard exists; PARTIALLY\_VERIFIED = a revision is known to exist but its value could not be confirmed in an accessible official source. Full URLs and verbatim excerpts are in the released registry JSONL.\label{tab:s-groundtruth}}\\",
 r"\toprule",
 r"Country & Value & Status & Official source \\",
 r"\midrule \endfirsthead",
 r"\toprule Country & Value & Status & Official source \\ \midrule \endhead",
]
gt_by = {g["country"]:g for g in gt}
for iso in sorted(gt_by, key=lambda k: NAMES.get(k,k)):
    g = gt_by[iso]
    lines.append("%s & %s & %s & %s \\\\" % (
        NAMES.get(iso,iso),
        tex_escape(g.get("value","")),
        tex_escape(g.get("status","")),
        tex_escape(g.get("source",""))))
lines += [r"\bottomrule", r"\end{longtable}", r"\normalsize"]
lines = [_units(l) for l in lines]
open(os.path.join(OUT,"tab_s_groundtruth.tex"),"w").write("\n".join(lines)+"\n")

# ---------------------------------------------------------------------------
# Table S: per-provider acquisition window + API documentation links
# (computed from responses/run_confirmatory_*.jsonl timestamp_utc, api_error==False)
# ---------------------------------------------------------------------------
import glob
RESP = os.path.join(ROOT, "data", "confirmatory_PRIVATE", "responses")
# venue -> (provider label, official API documentation URL). URLs are public/stable.
VENUE_DOC = {
 "openai_paid":   ("OpenAI API",       "https://platform.openai.com/docs/api-reference/chat"),
 "anthropic_paid":("Anthropic API",    "https://docs.anthropic.com/en/api/messages"),
 "gemini_free":   ("Google AI (free)", "https://ai.google.dev/api"),
 "deepseek_paid": ("DeepSeek API",     "https://api-docs.deepseek.com"),
 "cohere_trial":  ("Cohere (trial)",   "https://docs.cohere.com/reference/chat"),
 "groq_free":     ("Groq (free)",      "https://console.groq.com/docs/api-reference"),
 "ollama_local":  ("Ollama (local)",   "https://github.com/ollama/ollama/blob/main/docs/api.md"),
}
ts_by_venue = collections.defaultdict(list)
for f in glob.glob(os.path.join(RESP, "run_confirmatory_*.jsonl")):
    for line in open(f):
        try: r = json.loads(line)
        except Exception: continue
        if r.get("api_error"): continue
        t = r.get("timestamp_utc"); v = r.get("venue")
        if t and v: ts_by_venue[v].append(t)

acq_lines = [
 r"% AUTO-GENERATED by code/analysis/make_supplement_tables.py",
 r"\begin{longtable}{lp{2.0cm}p{2.0cm}p{5.3cm}}",
 r"\caption{Per-provider acquisition window and official API documentation. Reported accuracies are point-in-time estimates relative to this window; first/last are the earliest and latest non-error call timestamps (UTC) recorded in the run logs. The window spans the pilot, the pre-registered 15-country collection, and the post-registration extension.\label{tab:s-acquisition}}\\",
 r"\toprule",
 r"Provider (venue) & First (UTC) & Last (UTC) & API documentation \\",
 r"\midrule \endfirsthead",
 r"\toprule Provider (venue) & First (UTC) & Last (UTC) & API documentation \\ \midrule \endhead",
]
all_ts = []
for v in sorted(ts_by_venue, key=lambda k: VENUE_DOC.get(k, (k,))[0]):
    ts = sorted(ts_by_venue[v]); all_ts += ts
    label, url = VENUE_DOC.get(v, (v, ""))
    acq_lines.append("%s & %s & %s & \\url{%s} \\\\" % (
        label, ts[0][:10], ts[-1][:10], url))
acq_lines.append(r"\midrule")
if all_ts:
    all_ts.sort()
    acq_lines.append("\\textbf{All providers} & %s & %s & --- \\\\" % (all_ts[0][:10], all_ts[-1][:10]))
acq_lines += [r"\bottomrule", r"\end{longtable}"]
open(os.path.join(OUT,"tab_s_acquisition.tex"),"w").write("\n".join(acq_lines)+"\n")

# ---------------------------------------------------------------------------
# Summary stats sidecar (for prose cross-check)
# ---------------------------------------------------------------------------
summary = {
 "judge_model": JUDGE, "n_total": N_TOTAL, "n_english": N_EN, "n_native": N_NATIVE,
 "n_models": len(ROSTER), "n_countries": len(cov_country),
 "n_ground_truth": len(gt),
 "acquisition_first": (sorted(all_ts)[0][:19] if all_ts else None),
 "acquisition_last":  (sorted(all_ts)[-1][:19] if all_ts else None),
}
json.dump(summary, open(os.path.join(OUT,"_summary.json"),"w"), indent=2)
print("Generated tables in", OUT)
for k,v in summary.items(): print(f"  {k}: {v}")
