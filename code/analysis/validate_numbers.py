#!/usr/bin/env python3
"""validate_numbers.py — CENSO dos números do manuscrito contra os artefatos.

Regra da casa: número sem caminho reproduzível é defeito. Este script:
  1. constrói o conjunto CANÔNICO de números a partir dos artefatos JSON
     (freeze, sensibilidade T1/onda, H4 dentro do país, pré-15, confiabilidade,
     freeze_comparison) e do log do pipeline (GLMM, bayesiano, E-values,
     ponderações, taxonomia, robustez de H2, censo de back-translation);
  2. extrai TODO número dos PDFs (texto) de main, supplement, main-PT, supplement-PT;
  3. casa cada número com o canônico (arredondamento a 1–3 casas; sinal ignorado);
  4. lista os que NÃO casam, com contexto, para adjudicação humana;
  5. compara EN × PT: números que estão em um e não no outro.
Uso: python code/analysis/validate_numbers.py [--log run_all.log]
"""
import json, re, sys, subprocess, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parents[2]
LATEX = ROOT / "latex"
log_path = ROOT / "data" / "processed" / "last_run.log"
if "--log" in sys.argv:
    log_path = pathlib.Path(sys.argv[sys.argv.index("--log") + 1])

def flat(o, out):
    if isinstance(o, dict):
        for v in o.values(): flat(v, out)
    elif isinstance(o, (list, tuple)):
        for v in o: flat(v, out)
    elif isinstance(o, bool):
        pass
    elif isinstance(o, (int, float)):
        out.append(float(o))

canon = []
for f in ["freeze_all_effects.json", "t1_wave_sensitivity.json", "h4_within_country.json",
          "pre15_corrigido.json", "panel_reliability_full.json", "freeze_comparison.json",
          "duplicate_policy.json", "h4_with_gdp.json", "cluster_inference.json",
          "cabra_sanity/summary.json"]:
    p = ROOT / "data" / "processed" / f
    if p.exists():
        flat(json.loads(p.read_text()), canon)
for f in ["three_judge_reliability.json", "judge_panel_reliability.json"]:
    p = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / f
    if p.exists():
        flat(json.loads(p.read_text()), canon)
# tabelas GERADAS por script (suplemento e corpo): seus numeros vem dos artefatos
for tdir in (ROOT / "latex/supplement/tables", ROOT / "latex/sections/tables"):
    for tf in tdir.glob("*.tex"):
        for tok in re.findall(r"\d+(?:[.,]\d+)?", tf.read_text(encoding="utf-8")):
            try:
                canon.append(float(tok.replace(",", ".")))
                canon.append(float(tok.replace(",", "").replace(".", "")))
            except ValueError:
                pass
# valores em pp (x100) e OR/percentuais
canon_ext = set()
for v in canon:
    for m in (v, v * 100):
        for d in (0, 1, 2, 3):
            canon_ext.add(round(abs(m), d))
if log_path and log_path.exists():
    for tok in re.findall(r"[-+]?\d+(?:[.,]\d+)?(?:e[-+]?\d+)?", log_path.read_text(errors="ignore")):
        try:
            v = abs(float(tok.replace(",", ".")))
        except ValueError:
            continue
        for d in (0, 1, 2, 3):
            canon_ext.add(round(v, d))
            canon_ext.add(round(v * 100, d))

def pdf_text(name):
    out = subprocess.run(["pdftotext", "-layout", str(LATEX / f"{name}.pdf"), "-"], capture_output=True, text=True,
                         env={"PATH": "/opt/homebrew/bin:/usr/local/bin:/Users/lucasrover/Library/TinyTeX/bin/universal-darwin:/usr/bin:/bin"})
    return out.stdout

NUM = re.compile(r"(?<![\w.])[-−+]?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?(?:\s*[×x]\s*10[-−]?\d+)?(?![\w])")
def numbers(txt):
    res = []
    for line in txt.splitlines():
        # numeracao de linha do modo [review] (elsarticle): "123   texto"
        line = re.sub(r"^\s*\d{1,4}\s{2,}", "", line)
        for m in NUM.finditer(line):
            s = m.group(0).replace("−", "-").replace(" ", "")
            if "×" in s or "x10" in s:
                continue  # notação científica: p pequenos, checados à parte
            raw = s
            # separador de milhar vs decimal: "1,614" e "8.244" sao milhares; "0.617"
            # e "1.71" sao decimais. Quando ambiguo (>=1 com grupo de 3 digitos),
            # guardamos as DUAS leituras e aceitamos se qualquer uma for canonica.
            cands = []
            if re.fullmatch(r"[-+]?\d{1,3}(?:[.,]\d{3})+", raw) and not raw.lstrip("-+").startswith("0"):
                cands.append(float(re.sub(r"[.,]", "", raw)))
            cands.append(float(raw.replace(",", ".")))
            res.append((tuple(abs(c) for c in cands), raw, line.strip()[:110]))
    return res

IGNORE = set()  # anos, seções, contagens triviais
def trivial(vs, raw, ctx):
    v = vs[0]
    if 1900 <= v <= 2100 and "." not in raw and "," not in raw: return True   # anos
    if v <= 30 and "." not in raw and "," not in raw: return True               # contagens pequenas, seções, T1..T5
    if re.search(r"Table|Tabela|Section|Seção|Fig|S\d|§|pp\.|p\.\s*\d|arXiv|doi|DOI|https?://|ISBN|\bvol|\bno\.|\bn°|\bNo\.|Resolu|Decree|Decreto|Law|Lei|S\.R\.O|Rules|Directive|NOM-|D\.S\.|CONAMA|Act|Regulation|Regul|Gazette|CPCB|EPA|PP No|Lampiran|Schedule|Federal Register", ctx, re.I): return True
    if re.search(r"µg|μg|ug/m|mg/m", ctx) and v in (5,7,8,8.8,9,9.0,10,12,12.0,15,17,20,25,35,40,50,60,65,75,150): return True  # valores de padrão
    if re.search(r"tokens?|GB|bytes|sitelinks|statements|population|HDI|IDH|GDP|PIB|km", ctx, re.I): return True  # covariáveis (tabelas geradas)
    if re.search(r"^\s*\d", ctx) and len(ctx) < 12: return True  # número de página
    if re.search(r"et al\.|\(\d{4}\)|, \d{4}\.|pages? \d|pp\. \d|\d+\(\d+\):|Proceedings|Journal|Annals|Lancet|Springer|Press|Modeling \d", ctx): return True  # referências bibliográficas
    if re.search(r"World Health Organization|uncertainty interval|intervalo de incerteza|deaths in Brazil|mortes no Brasil", ctx): return True  # números da OMS citados (fonte externa, verificada no fichamento)
    if re.search(r"274 scores|274 pontuações|the 274$|as 274|roles \(Zheng|papéis \(Zheng|concordance on the same items", ctx): return True  # histórico do protocolo / citação
    if re.search(r"[A-Z][a-z]+ [A-Z]?[a-z]*,? \d{2,4}:\d+|\d{4}[–-]\d{4}: a systematic|countries and territories", ctx): return True  # volume:página de referência
    return False

report = {}
by_doc = {}
for doc in ["main", "supplement", "main-PT", "supplement-PT"]:
    txt = pdf_text(doc)
    nums = numbers(txt)
    by_doc[doc] = nums
    un = []
    for vs, raw, ctx in nums:
        if trivial(vs, raw, ctx): continue
        ok = any(round(v, d) in canon_ext for v in vs for d in (0, 1, 2, 3))
        if not ok:
            un.append((raw, ctx))
    report[doc] = un
    print(f"\n=== {doc}: {len(nums)} números, {len(un)} SEM caminho reproduzível ===")
    seen = set()
    for raw, ctx in un:
        k = (raw, ctx[:60])
        if k in seen: continue
        seen.add(k)
        print(f"  {raw:>10s} | {ctx}")

total_un = sum(len(v) for v in report.values())
# EN × PT
def sig(nums):
    return collections.Counter(round(vs[-1], 2) for vs, raw, ctx in nums if not trivial(vs, raw, ctx))
for a, b in (("main", "main-PT"), ("supplement", "supplement-PT")):
    ca, cb = sig(by_doc[a]), sig(by_doc[b])
    only_a = sorted(set(ca) - set(cb)); only_b = sorted(set(cb) - set(ca))
    print(f"\n=== {a} vs {b}: só em {a}: {len(only_a)} · só em {b}: {len(only_b)} ===")
    print("  só EN:", only_a[:80])
    print("  só PT:", only_b[:80])

print(f"\nVALIDACAO DE NUMEROS: {'LIMPA' if total_un == 0 else f'{total_un} numero(s) sem caminho reproduzivel'}")
sys.exit(1 if total_un else 0)
