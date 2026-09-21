#!/usr/bin/env python3
"""make_numbers_tex.py — os numeros-manchete do manuscrito como MACROS LaTeX geradas
dos artefatos. O texto escreve \\tiergap, nao "+5.0"; rodou o pipeline, o texto muda.

Por que: em 2026-09-21 tres pareceres seguidos acharam numeros desatualizados no
texto. O gate de consistencia e o censo de numeros sao redes; a unica garantia e
o texto nao carregar o numero. Fontes: freeze_all_effects.json (corrigido),
t1_wave_sensitivity.json, h4_within_country.json, pre15_corrigido.json,
panel_reliability_full.json e data/processed/last_run.log (GLMM, bayesiano,
E-values, ponderacoes, taxonomia, robustez de H2, censo de traducao).
Saida: latex/numbers.tex (EN e PT usam o mesmo arquivo; ponto decimal nos dois).
"""
import json, re, pathlib, math
ROOT = pathlib.Path(__file__).resolve().parents[2]
P = ROOT / "data" / "processed"
c = json.loads((P / "freeze_all_effects.json").read_text())["corrigido"]
S = json.loads((P / "t1_wave_sensitivity.json").read_text())
H = json.loads((P / "h4_within_country.json").read_text())
R = json.loads((P / "panel_reliability_full.json").read_text()) if (P / "panel_reliability_full.json").exists() else {}
log = (P / "last_run.log").read_text(errors="ignore") if (P / "last_run.log").exists() else ""

def g(pat, cast=float, default=None):
    m = re.search(pat, log)
    return cast(m.group(1).replace(",", ".")) if m else default
def pexp(p):
    """p pequeno em notacao 5\\times10^{-16}; p >= 0.001 com 3 casas / 2 casas."""
    if p >= 0.01: return f"{p:.2f}"
    if p >= 0.001: return f"{p:.3f}"
    e = int(math.floor(math.log10(p))); m = p / 10 ** e
    m = round(m); 
    if m == 10: m, e = 1, e + 1
    return f"{m}\\times10^{{{e}}}"
def pp(x, d=1, sign=True): return (f"{x:+.{d}f}" if sign else f"{x:.{d}f}")

M = {}
# --- tier gap
M["tiergap"] = pp(c["tier_gap_pp"]); M["tiergapci"] = f"[{pp(c['tier_gap_ci'][0])},{pp(c['tier_gap_ci'][1])}]"
M["accgn"] = f"{c['acc_gn']:.3f}"; M["accgs"] = f"{c['acc_gs']:.3f}"
M["tiergapperm"] = f"{g(r'gap observado .*? permutacao bilateral p = ([0-9.]+)'):.3f}"
M["loogapmin"] = pp(c["loo_gap_min"]); M["loogapmax"] = pp(c["loo_gap_max"])
B = S["B"]; M["tiergapwave"] = pp(B["wave2"]["gap_pp"]); M["tiergapwaveci"] = f"[{pp(B['wave2']['ci'][0])},{pp(B['wave2']['ci'][1])}]"; M["tiergapwavep"] = f"{B['wave2']['perm_p']:.3f}"
M["tiergappre"] = pp(B["pre15"]["gap_pp"]); M["tiergappreci"] = f"[{pp(B['pre15']['ci'][0])},{pp(B['pre15']['ci'][1])}]"; M["tiergapprep"] = f"{B['pre15']['perm_p']:.2f}"
I = S["I"]; cg = I["country_level_gap"]
M["codegap"] = pp(cg["gap_pp"]); M["codegapci"] = f"[{pp(cg['ci'][0])},{pp(cg['ci'][1])}]"; M["codegapp"] = f"{cg['perm_p']:.3f}"
M["codegn"] = f"{cg['acc_gn']:.2f}"; M["codegs"] = f"{cg['acc_gs']:.2f}"
M["codegapabs"] = f"{abs(cg['gap_pp']):.1f}"
M["codeor"] = f"{I['pooled']['OR']:.2f}"; M["codeorci"] = f"[{I['pooled']['ci'][0]:.2f},{I['pooled']['ci'][1]:.2f}]"
# --- T1 OR
A = S["A"]
M["ort"] = f"{A['all_keyed']['OR']:.2f}"; M["ortci"] = f"[{A['all_keyed']['ci'][0]:.2f},{A['all_keyed']['ci'][1]:.2f}]"
M["ortgn"] = f"{100*A['all_keyed']['rate_gn']:.1f}"; M["ortgs"] = f"{100*A['all_keyed']['rate_gs']:.1f}"
M["ortexcl"] = f"{A['excl_nonstandard']['OR']:.2f}"; M["ortexclci"] = f"[{A['excl_nonstandard']['ci'][0]:.2f},{A['excl_nonstandard']['ci'][1]:.2f}]"
M["ortpre"] = f"{A['pre15']['OR']:.2f}"; M["ortpreci"] = f"[{A['pre15']['ci'][0]:.2f},{A['pre15']['ci'][1]:.2f}]"
M["ortladder"] = f"{A['ladder']['OR']:.2f}"; M["ortladderci"] = f"[{A['ladder']['ci'][0]:.2f},{A['ladder']['ci'][1]:.2f}]"
M["laddergn"] = f"{A['ladder']['rate_gn']:.2f}"; M["laddergs"] = f"{A['ladder']['rate_gs']:.2f}"
M["strictgn"] = f"{A['all_keyed']['rate_gn']:.2f}"; M["strictgs"] = f"{A['all_keyed']['rate_gs']:.2f}"
L = A["ladder_share_of_incorrect"]; M["ladderhit"] = str(L["ladder_hit"]); M["incorrectn"] = str(L["incorrect"])
NS = A.get("no_standard_verdicts", {}); M["nsfab"] = str(NS.get("FABRICATED", "")); M["nsabst"] = str(NS.get("ABSTAIN_CORRECT", "")); M["nsdk"] = str(NS.get("DONT_KNOW", "")); M["nscells"] = str(A.get("no_standard_cells", ""))
M["bgdt"] = f"{A['t1_rate_by_country']['BGD']:.2f}"
for t in ("T1", "T2", "T3"):
    M["orcode" + t.lower()] = f"{I[t]['OR']:.2f}"
# --- H2
M["nativa"] = f"{abs(c['nativa_pp']):.1f}"; M["nativasigned"] = pp(c["nativa_pp"]); M["nativap"] = pexp(c["nativa_p"]); M["npares"] = str(c["n_pares"])
for lg in ("hi", "es", "pt"):
    M["nativa" + lg] = pp(c[f"nativa_{lg}_pp"]); M["nativa" + lg + "p"] = pexp(c[f"nativa_{lg}_p"]); M["npares" + lg] = str(c[f"n_pares_{lg}"])
Hn = S["H"]; M["h2mixedcountry"] = pp(Hn["re_country"]["beta_pp"]); M["h2mixedcountryse"] = f"{Hn['re_country']['se_pp']:.1f}"; M["h2mixedcountryp"] = pexp(Hn["re_country"]["p"])
M["h2mixedmodel"] = pp(Hn["re_model"]["beta_pp"]); M["h2mixedmodelp"] = pexp(Hn["re_model"]["p"])
cl = Hn["country_level"]; M["h2cneg"] = str(cl["neg"]); M["h2cmean"] = pp(cl["mean_pp"]); M["h2cse"] = f"{cl['se_pp']:.1f}"; M["h2ct"] = f"{cl['t']:.1f}"; M["h2ctp"] = f"{cl['t_p']:.3f}"
ml = Hn["model_level"]; M["h2mneg"] = str(ml["neg"]); M["h2mwp"] = f"{ml['wilcoxon_p']:.3f}"
D = S["D"]; M["h2code"] = pp(D["code"]["pp"]); M["h2coden"] = str(D["code"]["n"]); M["h2codep"] = pexp(D["code"]["p"])
M["h2panel"] = pp(D["panel"]["pp"]); M["h2paneln"] = str(D["panel"]["n"]); M["h2panelp"] = pexp(D["panel"]["p"])
M["h2orig"] = pp(D["original"]["pp"]); M["h2orign"] = str(D["original"]["n"]); M["h2origp"] = f"{D['original']['p']:.2f}"
hc = I["h2_code_by_lang"]; M["h2codept"] = pp(hc["português"]["pp"]); M["h2codeptn"] = str(hc["português"]["n"]); M["h2codeptp"] = f"{hc['português']['p']:.3f}"
M["h2codees"] = pp(hc["espanhol"]["pp"]); M["h2codeesn"] = str(hc["espanhol"]["n"]); M["h2codeall"] = pp(hc["todos"]["pp"]); M["h2codealln"] = str(hc["todos"]["n"]); M["h2codeallp"] = f"{hc['todos']['p']:.3f}"
G = S["G"]; M["repdiff"] = f"{G['mean_abs_diff_pp']:.1f}"; M["repsd"] = f"{G['sd_within_pp']:.1f}"
# robustez de H2 (log)
M["loocmin"] = pp(-abs(g(r"efeito mais fraco +([-0-9.]+) pp \(sem [A-Z]{3}\)"))); M["loocmax"] = pp(-abs(g(r"efeito mais forte +([-0-9.]+) pp \(sem [A-Z]{3}\)")))
M["loommin"] = pp(-abs(g(r"efeito mais fraco +([-0-9.]+) pp \(sem [a-z0-9_]+\)"))); M["loommax"] = pp(-abs(g(r"efeito mais forte +([-0-9.]+) pp \(sem [a-z0-9_]+\)")))
M["trim"] = pp(g(r"aparando 5% de cada cauda +([-0-9.]+) pp")); M["trimp"] = pexp(g(r"aparando 5% de cada cauda +[-0-9.]+ pp +p=([0-9.e+-]+)"))
M["verifen"] = g(r"taxa de valor verificavel: ingles ([0-9.]+)%", str); M["verifnat"] = g(r"nativa ([0-9.]+)%\n", str) or g(r"ingles [0-9.]+% · nativa ([0-9.]+)%", str)
M["verifdiff"] = g(r"diferenca pareada ([-0-9.]+) pp", str); M["verifworse"] = g(r"nativa pior em (\d+)/", str); M["verifdisc"] = g(r"nativa pior em \d+/(\d+)", str); M["verifp"] = pexp(g(r"teste de sinais p=([0-9.e+-]+)"))
M["verifes"] = pp(g(r"espanhol +([-+0-9.]+) pp +n=")); M["verifpt"] = pp(g(r"portugues +([-+0-9.]+) pp +n=")); M["verifhi"] = pp(g(r"hindi +([-+0-9.]+) pp +n="))
M["faithful"] = pp(g(r"so traducoes FIEIS +([-0-9.]+) pp")); M["faithfulp"] = pexp(g(r"so traducoes FIEIS +[-0-9.]+ pp +p=([0-9.e+-]+)")); M["faithfuln"] = g(r"so traducoes FIEIS .*?n=(\d+)", str)
M["divergent"] = pp(g(r"so traducoes DIVERGENTES +([-0-9.]+) pp")); M["divergentn"] = g(r"so traducoes DIVERGENTES .*?n=(\d+)", str); M["fidelityp"] = f"{g(r'diferenca fiel-divergente .*? permutacao p=([0-9.]+)'):.2f}"
# --- H1 gradiente
M["rho"] = f"{c['h1_rho_hdi']:.2f}"; M["rhop"] = f"{c['h1_p']:.3f}"; M["rhomkp"] = f"{c['h1_mk_p']:.3f}"; M["rhopre"] = f"{c['h1_rho_pre15']:.2f}"
M["loorhomin"] = pp(c["loo_rho_min"]); M["loorhomax"] = pp(c["loo_rho_max"])
M["rhoequal"] = f"{g(r'(?m)^equal +[-+0-9.]+ +([-+0-9.]+)'):.2f}"; M["rhopca"] = f"{g(r'(?m)^PCA-derived +[-+0-9.]+ +([-+0-9.]+)'):.2f}"
M["gapequal"] = pp(g(r'(?m)^equal +([-+0-9.]+)')); M["gappca"] = pp(g(r'(?m)^PCA-derived +([-+0-9.]+)'))
M["gapfactual"] = pp(g(r"pesos factual +tier gap ([-+0-9.]+) pp")); M["nativaequal"] = pp(g(r"pesos iguais .*? nativa ([-0-9.]+) pp")); M["nativafactual"] = pp(g(r"pesos factual .*? nativa ([-0-9.]+) pp"))
M["power"] = g(r"poder para detectar rho=0.55: (\d+)%", str); M["mde"] = g(r"efeito minimo detectavel a 80% de poder: rho = ([0-9.]+)", str); M["powerweak"] = g(r"poder para detectar rho=0.40: (\d+)%", str)
# taxonomia
M["taxmed"] = pp(g(r"HDI abaixo da mediana .*? ([-+0-9.]+) pp")); M["taxmedp"] = f"{g(r'HDI abaixo da mediana .*? perm p=([0-9.]+)'):.3f}"
M["taxvh"] = pp(g(r"HDI < 0,800 .*? ([-+0-9.]+) pp")); M["taxvhp"] = f"{g(r'HDI < 0,800 .*? perm p=([0-9.]+)'):.3f}"
M["taxlow"] = pp(g(r"HDI < 0,700 +([-+0-9.]+) pp")); M["taxlowp"] = f"{g(r'HDI < 0,700 .*? perm p=([0-9.]+)'):.3f}"
# --- modelos mistos / bayes / E-values
M["mixedbeta"] = f"{g(r'is_south  : beta=([-0-9.]+)'):.3f}"; M["mixedse"] = f"{g(r'is_south  : beta=[-0-9.]+ +SE=([0-9.]+)'):.3f}"; M["mixedp"] = f"{g(r'is_south  : beta=[-0-9.]+ +SE=[0-9.]+ +p=([0-9.]+)'):.3f}"
M["bayes"] = f"{g(r'posterior mean b_south = ([-0-9.]+)'):.3f}"; M["bayeslo"] = f"{g(r'94% HDI += \[([-0-9.]+),'):.3f}"; M["bayeshi"] = f"{g(r'94% HDI += \[[-0-9.]+, ([-0-9.]+)\]'):.3f}"; M["bayesp"] = f"{g(r'P\(b_south < 0\) += ([0-9.]+)'):.3f}"; M["rhat"] = f"{g(r'R-hat\(b_south\) = ([0-9.]+)'):.3f}"
M["evalue"] = f"{g(r'point   : .*? E-value = ([0-9.]+)'):.2f}"; M["evaluelim"] = f"{g(r'CI limit: .*? E-value = ([0-9.]+)'):.2f}"
# --- ORs por tarefa (GLMM)
for t in ("T1", "T2", "T3", "T4", "T5"):
    m = re.search(rf"^  {t} +(\d+) +([0-9.]+)% +([0-9.]+)% +([0-9.]+) +\[([0-9.]+), ([0-9.]+)\]", log, re.M)
    if m:
        M[f"or{t.lower()}gn"] = m.group(2); M[f"or{t.lower()}gs"] = m.group(3); M[f"or{t.lower()}"] = f"{float(m.group(4)):.2f}"; M[f"or{t.lower()}ci"] = f"[{float(m.group(5)):.2f},{float(m.group(6)):.2f}]"
# --- piso, H3, H5, H6, tarefas
M["floorrecall"] = f"{c['acc_t1t2']:.3f}"; M["floorrest"] = f"{c['acc_resto']:.3f}"; M["floordelta"] = f"{c['cliff_piso']:.2f}"
M["regdelta"] = f"{c['cliff_regional']:.2f}"; M["hfive"] = pp(c["h5_pp"]); M["did"] = pp(c["h6_did"]); M["didneutral"] = pp(c["h6_gap_neutro"]); M["didmanager"] = pp(c["h6_gap_gestor"]); M["personap"] = f"{c['persona_p']:.2f}"
for t, v in c["por_task"].items(): M["task" + t.lower()] = f"{v[0]:.3f}"; M["ntask" + t.lower()] = f"{v[1]:,}".replace(",", "{,}")
M["cabra"] = f"{c['por_modelo']['cabra_mistral_7b'][0]:.3f}"; M["llamab"] = f"{c['por_modelo']['llama31_8b'][0]:.3f}"; M["deepseek"] = f"{c['por_modelo']['deepseek_v3'][0]:.3f}"
F = S["F"]; M["hthreebra"] = f"{F['BRA_pt']['mean_cabra']:.3f}"; M["hthreebrallama"] = f"{F['BRA_pt']['mean_llama']:.3f}"; M["hthreebradelta"] = f"{F['BRA_pt']['delta_vs_llama']:.2f}"
M["hthreelus"] = f"{F['lusofonos_pt']['mean_cabra']:.3f}"; M["hthreeluslama"] = f"{F['lusofonos_pt']['mean_llama']:.3f}"; M["hthreelusdelta"] = f"{F['lusofonos_pt']['delta_vs_llama']:.2f}"
M["india"] = f"{c['por_pais']['IND'][0]:.3f}"
# --- H4
M["hfourbeta"] = f"{H['interacao_beta']:+.3f}"; M["hfourse"] = f"{H['interacao_se']:.3f}"; M["hfourp"] = pexp(H["interacao_p"]); M["hfourn"] = f"{H['n_respostas']:,}".replace(",", "{,}")
M["hfourcob"] = f"{H['ajuste_mutuo_cob_beta']:+.3f}"; M["hfourcobp"] = pexp(H["ajuste_mutuo_cob_p"]); M["hfourlang"] = f"{H['ajuste_mutuo_lang_beta']:+.3f}"; M["hfourlangp"] = f"{H['ajuste_mutuo_lang_p']:.2f}"
M["hfourjcob"] = f"{H['conjunto_cob_beta']:+.3f}"; M["hfourjcobp"] = f"{H['conjunto_cob_p']:.3f}"; M["hfourjhdi"] = f"{H['conjunto_hdi_beta']:+.3f}"; M["hfourjhdip"] = pexp(H["conjunto_hdi_p"]); M["rhocobhdi"] = f"{H['rho_cobertura_hdi']:.2f}"
M["hfouranglo"] = f"{H['so_anglofonos_beta']:+.3f}"; M["hfouranglop"] = f"{H['so_anglofonos_p']:.3f}"
M["hfourdep"] = f"{H['acc_dependentes']:.3f}"; M["hfourind"] = f"{H['acc_independentes']:.3f}"; M["hfourdeficit"] = f"{H['acc_independentes']-H['acc_dependentes']:.3f}"
M["hfoursite"] = f"{c['h4_rho_sitelinks']:+.2f}"; M["hfoursitep"] = f"{c['h4_p_sitelinks']:.3f}"; M["hfourpartial"] = f"{c['h4_parcial_sitelinks_hdi']:+.2f}"; M["hfourpartialp"] = f"{c['h4_p_parcial']:.2f}"; M["hfourwiki"] = f"{c['h4_rho_wikilang']:+.2f}"; M["hfourwikip"] = f"{c['h4_p_wikilang']:.2f}"
# --- confiabilidade
M["alpha"] = f"{g(r'Krippendorff alpha \(intervalar\) += ([0-9.]+)'):.3f}"; M["icc"] = f"{g(r'ICC\(2,1\) juiz unico += ([0-9.]+)'):.3f}"; M["iccpanel"] = f"{g(r'ICC\(2,3\) media do painel.*?= ([0-9.]+)'):.3f}"
# --- cobertura de código / células
M["cells"] = "8{,}244"; M["cellsen"] = "6{,}573"; M["cellspt"] = "8.244"; M["cellsenpt"] = "6.573"
# pre-15 (familia primaria) e tabelas do suplemento com 2 casas
PR = json.loads((P / "pre15_corrigido.json").read_text())
M["prerho"] = f"{PR['h1_rho_hdi']:+.3f}"; M["prerhop"] = f"{PR['h1_p_hdi']:.2f}"; M["premks"] = str(PR["h1_mk_S"]); M["premkz"] = f"{PR['h1_mk_Z']:+.2f}"; M["premkp"] = f"{PR['h1_mk_p']:.2f}"
M["prejoshi"] = f"{PR['h1_rho_joshi']:+.3f}"; M["prejoship"] = f"{PR['h1_p_joshi']:.2f}"; M["prehfour"] = f"{PR['h4_parcial_cobertura_hdi']:+.3f}"; M["prehfourp"] = f"{PR['h4_p_parcial']:.2f}"
M["rhothree"] = f"{c['h1_rho_hdi']:+.3f}"; M["hfourpartialthree"] = f"{c['h4_parcial_sitelinks_hdi']:+.3f}"
M["taxunctad"] = pp(g(r"UNCTAD \(usado no artigo\) +([-+0-9.]+) pp"), 2); M["taxmedtwo"] = pp(g(r"HDI abaixo da mediana .*? ([-+0-9.]+) pp"), 2); M["taxvhtwo"] = pp(g(r"HDI < 0,800 .*? ([-+0-9.]+) pp"), 2); M["taxlowtwo"] = pp(g(r"HDI < 0,700 +([-+0-9.]+) pp"), 2)
M["gapprimarytwo"] = pp(g(r"(?m)^(?:author|Author)[^\n]*? +([-+0-9.]+) +[-+0-9.]+ +[-+0-9.]+ +[-+0-9.]+", ) or c["tier_gap_pp"], 2)
M["gapequaltwo"] = pp(g(r"(?m)^equal +([-+0-9.]+)"), 2); M["gappcatwo"] = pp(g(r"(?m)^PCA-derived +([-+0-9.]+)"), 2)
M["rhoprimarythree"] = f"{g(r'(?m)^(?:author|Author)[^\n]*? +[-+0-9.]+ +([-+0-9.]+)') or c['h1_rho_hdi']:+.3f}"; M["rhoequalthree"] = f"{g(r'(?m)^equal +[-+0-9.]+ +([-+0-9.]+)'):+.3f}"; M["rhopcathree"] = f"{g(r'(?m)^PCA-derived +[-+0-9.]+ +([-+0-9.]+)'):+.3f}"
M["floorprimary"] = f"{g(r'(?m)^(?:author|Author)[^\n]*? +[-+0-9.]+ +[-+0-9.]+ +([-+0-9.]+)') or c['cliff_piso']:.3f}"; M["floorequal"] = f"{g(r'(?m)^equal +[-+0-9.]+ +[-+0-9.]+ +([-+0-9.]+)'):.3f}"; M["floorpca"] = f"{g(r'(?m)^PCA-derived +[-+0-9.]+ +[-+0-9.]+ +([-+0-9.]+)'):.3f}"
M["hthreeprimary"] = f"{g(r'(?m)^(?:author|Author)[^\n]*? +[-+0-9.]+ +[-+0-9.]+ +[-+0-9.]+ +([-+0-9.]+)') or c['cliff_regional']:.3f}"; M["hthreeequal"] = f"{g(r'(?m)^equal +[-+0-9.]+ +[-+0-9.]+ +[-+0-9.]+ +([-+0-9.]+)'):.3f}"; M["hthreepca"] = f"{g(r'(?m)^PCA-derived +[-+0-9.]+ +[-+0-9.]+ +([-+0-9.]+)'):.3f}"
M["didtwo"] = pp(c["h6_did"], 2); M["personapthree"] = f"{c['persona_p']:.3f}"
M["hfoursitethree"] = f"{c['h4_rho_sitelinks']:+.3f}"; M["hfourwikithree"] = f"{c['h4_rho_wikilang']:+.3f}"
M["bytesrho"] = f"{g(r'English-Wikipedia bytes +n=25 +rho=([-+0-9.]+)'):+.3f}"; M["bytesp"] = f"{g(r'English-Wikipedia bytes .*?\(p=([0-9.]+)\)'):.2f}"; M["bytespartial"] = f"{g(r'English-Wikipedia bytes .*?parcial\|IDH=([-+0-9.]+)'):+.3f}"; M["bytespartialp"] = f"{g(r'English-Wikipedia bytes .*?parcial\|IDH=[-+0-9.]+ \(p=([0-9.]+)\)'):.2f}"
M["stmtrho"] = f"{g(r'Wikidata statements +n=25 +rho=([-+0-9.]+)'):+.3f}"; M["stmtp"] = f"{g(r'Wikidata statements .*?\(p=([0-9.]+)\)'):.2f}"; M["stmtpartial"] = f"{g(r'Wikidata statements .*?parcial\|IDH=([-+0-9.]+)'):+.3f}"; M["stmtpartialp"] = f"{g(r'Wikidata statements .*?parcial\|IDH=[-+0-9.]+ \(p=([0-9.]+)\)'):.2f}"
M["sitepthree"] = f"{c['h4_p_sitelinks']:.3f}"; M["sitepartialp"] = f"{c['h4_p_parcial']:.2f}"
M["medab"] = f"{g(r'a  \(HDI -> sitelinks\) += ([-+0-9.]+)'):+.2f}"; M["medb"] = f"{g(r'b  \(sitelinks -> accuracy\|HDI\)= ([-+0-9.]+)'):+.2f}"; M["medc"] = f"{g(r"c' \(direct HDI -> accuracy\) += ([-+0-9.]+)"):+.2f}"; M["medabx"] = f"{g(r'indirect \(a\*b\) += ([-+0-9.]+)'):+.2f}"; M["medlo"] = f"{g(r'95% boot CI \[([-+0-9.]+),'):+.2f}"; M["medhi"] = f"{g(r'95% boot CI \[[-+0-9.]+, ([-+0-9.]+)\]'):+.2f}"
M["manip"] = g(r"explicit role-frame acknowledgement: \d+ \(([0-9.]+)%\)", str); M["manipn"] = g(r"explicit role-frame acknowledgement: (\d+) ", str)
C = S["C"]; M["dupchange"] = f"{100*C['cells_where_rule_changes_verdict']/C['cells']:.1f}"; M["dupmean"] = f"{abs(C['mean_first']-C['mean_all']):.4f}"
# H4: linhas da tabela dentro do pais (log), juizes, cobertura de codigo, duplicatas, juiz x tier
M["hfourtonevsfive"] = f"{g(r'extremos \(T1 vs T5\) +([-+0-9.]+)'):+.3f}"; M["hfourtonevsfivep"] = pexp(g(r'extremos \(T1 vs T5\) +[-+0-9.]+ +([0-9.e+-]+)'))
M["hfournotfive"] = f"{g(r'sem T5, que tem teto de 99,7% +([-+0-9.]+)'):+.3f}"; M["hfournotfivep"] = pexp(g(r'sem T5, que tem teto de 99,7% +[-+0-9.]+ +([0-9.e+-]+)'))
M["hfournotfour"] = f"{g(r'sem T4, a mais interpretativa +([-+0-9.]+)'):+.3f}"; M["hfournotfourp"] = pexp(g(r'sem T4, a mais interpretativa +[-+0-9.]+ +([0-9.e+-]+)'))
M["hfourplacebo"] = f"{g(r'PLACEBO \(rotulos invertidos\) +([-+0-9.]+)'):+.3f}"
M["judgegemini"] = g(r"gemini_2_5_pro=([0-9.]+)", str); M["judgeclaude"] = g(r"claude_sonnet_4_6=([0-9.]+)", str); M["judgedeepseek"] = g(r"deepseek_v3=([0-9.]+)", str)
E = S["E"]; M["jtgngpt"] = f"{E['GN|gpt-5-mini-202']['factual']:.2f}"; M["jtgsgpt"] = f"{E['GS|gpt-5-mini-202']['factual']:.2f}"; M["jtgnhaiku"] = f"{E['GN|claude-haiku-4']['factual']:.2f}"; M["jtgshaiku"] = f"{E['GS|claude-haiku-4']['factual']:.2f}"
import collections as _c
_rows = [json.loads(l) for l in (ROOT / "data/confirmatory_PRIVATE/analysis/judge_scores_corrected.jsonl").open()]
_by = _c.defaultdict(_c.Counter)
for r in _rows: _by[r["task"]][r.get("score_source")] += 1
for t in ("T1", "T2", "T3"):
    M["codecov" + t.lower()] = f"{100*_by[t]['code']/sum(_by[t].values()):.1f}"
M["codecells"] = f"{sum(1 for r in _rows if r.get('score_source') in ('code','panel')):,}".replace(",", "{,}")
M["tonecodecells"] = f"{_by['T1']['code']:,}".replace(",", "{,}"); M["tonecells"] = f"{sum(_by['T1'].values()):,}".replace(",", "{,}")
M["tonecodecellspt"] = f"{_by['T1']['code']:,}".replace(",", "."); M["tonecellspt"] = f"{sum(_by['T1'].values()):,}".replace(",", "."); M["codecellspt"] = M["codecells"].replace("{,}", ".")
import statistics as _st
M["restmean"] = f"{_st.mean(r['composite'] for r in _rows if r['model_id'] != 'cabra_mistral_7b' and not r['prompt_id'].endswith(('_pt','_es','_hi'))):.3f}"
M["dupresp"] = "21.9"; M["dupscore"] = "11.5"  # medidos em robustness_extra / export (constantes da coleta)

# --- inferencia no nivel do cluster (cluster_inference.json; parecer de painel 2026-09-21)
K = json.loads((P / "cluster_inference.json").read_text())
M["hfourclp"] = f"{K['A']['cob_alone']['dep:cob_z']['p']:.3f}"; M["hfourclse"] = f"{K['A']['cob_alone']['dep:cob_z']['se']:.3f}"
M["hfourjcobclp"] = f"{K['A']['joint_hdi']['dep:cob_z']['p']:.2f}"; M["hfourjhdiclp"] = f"{K['A']['joint_hdi']['dep:hdi_z']['p']:.2f}"
M["hfourhdialonebeta"] = f"{K['A']['hdi_alone']['dep:hdi_z']['beta']:+.3f}"; M["hfourhdialoneclp"] = f"{K['A']['hdi_alone']['dep:hdi_z']['p']:.3f}"
M["hfouranglclp"] = f"{K['A']['anglo']['dep:cob_z']['p']:.2f}"
M["hfourctryrho"] = f"{K['A']['country_level']['rho']:+.2f}"; M["hfourctryp"] = f"{K['A']['country_level']['p']:.3f}"
M["hfourctrypartial"] = f"{K['A']['country_level']['rho_partial_hdi']:+.2f}"; M["hfourctrypartialp"] = f"{K['A']['country_level']['p_partial']:.2f}"
for t in ("T1", "T2", "T3", "T4", "T5"):
    b = K["B"][t]; w = {"T1": "one", "T2": "two", "T3": "three", "T4": "four", "T5": "five"}[t]
    M["orraw" + w] = f"{b['OR_raw']:.2f}"; M["orraw" + w + "ci"] = f"[{b['ci_country_boot'][0]:.2f},{b['ci_country_boot'][1]:.2f}]"; M["orraw" + w + "p"] = f"{b['perm_p_country']:.3f}"
M["gapeu"] = pp(K["C"]["gap_pp"]); M["gapeuci"] = f"[{pp(K['C']['ci'][0])},{pp(K['C']['ci'][1])}]"; M["gapeup"] = f"{K['C']['perm_p']:.3f}"; M["gapeuunits"] = str(K["C"]["n_gn_units"])
M["gapbal"] = pp(K["D"]["gap_pp"]); M["gapbalci"] = f"[{pp(K['D']['ci'][0])},{pp(K['D']['ci'][1])}]"; M["gapbalp"] = f"{K['D']['perm_p']:.2f}"; M["gapbalprompts"] = str(K["D"]["prompts_balanced"]); M["gapbaltotal"] = str(K["D"]["prompts_total"])
M["personamain"] = pp(K["E"]["main_effect_pp"], 2); M["personamainp"] = pexp(K["E"]["main_effect_p"]); M["personamainn"] = f"{K['E']['main_effect_n_pairs']:,}".replace(",", "{,}"); M["personamainctryp"] = f"{K['E']['main_effect_country_t_p']:.3f}"
M["didcinety"] = f"[{pp(K['E']['did_ci90_country'][0])},{pp(K['E']['did_ci90_country'][1])}]"; M["didcininetyfive"] = f"[{pp(K['E']['did_ci95_country'][0])},{pp(K['E']['did_ci95_country'][1])}]"
M["floorbymodel"] = pp(K["F"]["floor_by_model"]["mean_pp"]); M["floorbymodelp"] = pexp(K["F"]["floor_by_model"]["wilcoxon_p"]); M["floorbymodelneg"] = str(K["F"]["floor_by_model"]["neg"])
M["floorbyctry"] = pp(K["F"]["floor_by_country"]["mean_pp"]); M["floorbyctryp"] = pexp(K["F"]["floor_by_country"]["wilcoxon_p"]); M["floorbyctryneg"] = str(K["F"]["floor_by_country"]["neg"])
M["hthreebyctry"] = pp(K["F"]["h3_by_country"]["mean_pp"]); M["hthreebyctryp"] = pexp(K["F"]["h3_by_country"]["wilcoxon_p"]); M["hthreebyctryneg"] = str(K["F"]["h3_by_country"]["neg"])
M["hthreenarrow"] = pp(K["F"]["h3_narrow_by_prompt"]["mean_pp"]); M["hthreenarrowp"] = pexp(K["F"]["h3_narrow_by_prompt"]["wilcoxon_p"]); M["hthreenarrowneg"] = str(K["F"]["h3_narrow_by_prompt"]["neg"]); M["hthreenarrown"] = str(K["F"]["h3_narrow_by_prompt"]["n"])
M["rhocilo"] = f"{K['G']['ci25'][0]:+.2f}"; M["rhocihi"] = f"{K['G']['ci25'][1]:+.2f}"; M["rhoprecilo"] = f"{K['G']['ci15'][0]:+.2f}"; M["rhoprecihi"] = f"{K['G']['ci15'][1]:+.2f}"
M["ttwoyearsgn"] = f"{K['I']['years_gn']:.1f}"; M["ttwoyearsgs"] = f"{K['I']['years_gs']:.1f}"; M["ttwospreadgn"] = f"{K['I']['spread_gn']:.2f}"; M["ttwospreadgs"] = f"{K['I']['spread_gs']:.2f}"
for lg in ("en", "es", "pt", "hi"):
    M["empty" + lg] = f"{K['H'][lg]['pct']:.1f}"; M["empty" + lg + "n"] = str(K["H"][lg]["empty"])

# --- sanity check do Cabra (data/processed/cabra_sanity/summary.json)
CS = json.loads((P / "cabra_sanity" / "summary.json").read_text())
def _rate(k): return CS[k]["rate"]
_c, _b, _l, _co = _rate("cabra_mistral_7b|all"), _rate("mistral_7b_instruct_v03_base|all"), _rate("llama31_8b_reserved|all"), _rate("cabra_mistral_7b_ORIGINAL|all")
M["cabsanitycabra"] = f"{100*_c:.0f}"; M["cabsanitybase"] = f"{100*_b:.0f}"; M["cabsanityllama"] = f"{100*_l:.0f}"; M["cabsanityorig"] = f"{100*_co:.0f}"
M["cabsanityn"] = str(CS["cabra_mistral_7b|all"]["n_factual"])
if _c <= _b + 0.02:
    _s = (f"Re-served, Cabra returns the register value on {M['cabsanitycabra']}\\% of the code-resolved Portuguese items "
          f"({M['cabsanityorig']}\\% in the original collection), its base model on {M['cabsanitybase']}\\% and "
          f"Llama~3.1~8B on {M['cabsanityllama']}\\%. On {M['cabsanityn']} items per model the three are within a few answers of one another: "
          f"the fine-tune does not outperform the base it was trained from, the serving stack does not explain its rank, and the "
          f"composite margin against Llama~3.1~8B comes from the judged tasks and subcomponents rather than from the register values.")
else:
    _s = (f"Re-served, Cabra returns the register value on {M['cabsanitycabra']}\\% of the code-resolved Portuguese items "
          f"({M['cabsanityorig']}\\% in the original collection), its base model on {M['cabsanitybase']}\\% and "
          f"Llama~3.1~8B on {M['cabsanityllama']}\\%: the fine-tune improves on its base on these items, and its rank reflects "
          f"the scale class rather than the serving stack.")
M["cabrasanitysentence"] = _s
if _c <= _b + 0.02:
    _sp = (f"Reservido, o Cabra devolve o valor do registro em {M['cabsanitycabra']}\\% dos itens em português resolvidos por código "
           f"({M['cabsanityorig']}\\% na coleta original), seu modelo-base em {M['cabsanitybase']}\\% e o "
           f"Llama~3.1~8B em {M['cabsanityllama']}\\%. Com {M['cabsanityn']} itens por modelo, os três ficam a poucas respostas um do outro: "
           f"o ajuste fino não supera a base de que foi treinado, a pilha de serviço não explica sua posição, e a margem do composto "
           f"contra o Llama~3.1~8B vem das tarefas e dos subcomponentes julgados, não dos valores de registro.")
else:
    _sp = (f"Reservido, o Cabra devolve o valor do registro em {M['cabsanitycabra']}\\% dos itens em português resolvidos por código "
           f"({M['cabsanityorig']}\\% na coleta original), seu modelo-base em {M['cabsanitybase']}\\% e o "
           f"Llama~3.1~8B em {M['cabsanityllama']}\\%: o ajuste fino supera a base nesses itens, e sua posição reflete "
           f"a classe de escala e não a pilha de serviço.")
M["cabrasanitysentencept"] = _sp
# derivadas de apresentacao
M["verifdiffabs"] = f"{abs(float(M['verifdiff'])):.1f}"
M["taskt1short"] = f"{c['por_task']['T1'][0]:.2f}"; M["floorrestshort"] = f"{c['acc_resto']:.2f}"
M["loorhomaxabs"] = f"{c['loo_rho_max']:.2f}"; M["tiergappermpct"] = f"{100*float(M['tiergapperm']):.1f}"
out = ["% AUTO-GERADO por code/analysis/make_numbers_tex.py — NAO EDITAR. Rodou o pipeline, este arquivo muda e o texto acompanha."]
bad = [k for k, v in M.items() if v is None or "None" in str(v) or "nan" in str(v)]
DIG = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine"}
for k, v in sorted(M.items()):
    name = "".join(DIG.get(ch, ch) for ch in k)   # nomes de macro nao aceitam digitos
    out.append(f"\\newcommand{{\\n{name}}}{{{v}}}")
(ROOT / "latex" / "numbers.tex").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"latex/numbers.tex: {len(M)} macros" + (f" · SEM VALOR: {bad}" if bad else ""))
if bad: raise SystemExit(1)
