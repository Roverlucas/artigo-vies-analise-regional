#!/usr/bin/env python3
"""make_readme_numbers.py — os números do README vêm de latex/numbers.tex, não da mão.
Substitui o bloco entre <!-- numbers:begin --> e <!-- numbers:end --> no README.md.
"""
import re, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
M = dict(re.findall(r"\\newcommand\{\\(n[a-z]+)\}\{((?:[^{}]|\{[^{}]*\})*)\}", (ROOT / "latex/numbers.tex").read_text(encoding="utf-8")))
def v(k): return M[k].replace("{,}", ",").replace("\\times10^{", "e").replace("}", "")
block = f"""<!-- numbers:begin  (gerado por code/analysis/make_readme_numbers.py a partir de latex/numbers.tex — não editar à mão) -->
| # | Hypothesis | Finding | Evidence status |
|---|---|---|---|
| **H2** | Native-language prompting modulates accuracy | **{v('nnativasigned')} pp** (Wilcoxon p={v('nnativap')}, n={v('nnpares')} cells; mixed model with a random intercept per country p={v('nhtwomixedcountryp')}; {v('nhtwocneg')}/9 countries negative, t-test p={v('nhtwoctp')}); Hindi {v('nnativahi')}, Spanish {v('nnativaes')}, Portuguese {v('nnativapt')}, all significant. Native prompts return a register-checkable value {v('nverifnat')}% of the time vs {v('nverifen')}% in English ({v('nverifdiff')} pp, sign test p={v('nverifp')}; Hindi {v('nverifhi')}, Spanish {v('nverifes')}, Portuguese {v('nverifpt')}) | **Principal finding.** Survives leave-one-out over countries and models, every task, every weighting, every scoring instrument (code {v('nhtwocode')}, panel {v('nhtwopanel')}), and a back-translation census of all 90 native prompts |
| **H3** | Regional model narrows the gap | Cabra-Mistral 7B (a community 7B fine-tune) is the **weakest** of all 14 (δ={v('nregdelta')}); it also trails its scale-matched peer Llama 3.1 8B on Portuguese-language Brazilian prompts ({v('nhthreebra')} vs {v('nhthreebrallama')}, n=20 each) | Supported (opposite of optimistic framing); the narrow pre-specified test is small and descriptive |
| **H1** (tier) | Global North/South gap | **{v('ntiergap')} pp** (bootstrap 95% CI {v('ntiergapci')}; permutation p={v('ntiergapperm')}); same size within the extension wave alone ({v('ntiergapwave')}) and on the pre-specified 15 ({v('ntiergappre')}, 3 GN). On the code-adjudicated outcomes alone the country-level gap is {v('ncodegap')} pp (perm p={v('ncodegapp')}), so it is not a judge artefact. Concentrated: on the binding national standard, scored by code, Global South odds are **{v('nort')}** {v('nortci')} of Global North odds ({v('nortexcl')} without the three no-standard countries; {v('nortladder')} under a ladder-tolerant key); no gap on the one task with no register value | Supported, but only under the conventional UNCTAD partition — partitions on HDI alone do not reproduce it |
| **H1** (gradient) | Monotonic development gradient | ρ={v('nrho')} with HDI (p={v('nrhop')}); ρ={v('nrhopre')} at the pre-specified n=15; never reaches 0.55 in any leave-one-out or weighting | **Not supported.** Design has {v('npower')}% power at the pre-specified ρ=0.55, so a strong gradient is excluded; a weak one is not |
| **H4** | Corpus representation is the mechanism | Between countries, neither channel separates from development (sitelinks ρ={v('nhfoursite')}, p={v('nhfoursitep')}; partial p={v('nhfourpartialp')}). Within countries, coverage predicts the specificity deficit (β={v('nhfourbeta')}, p={v('nhfourp')}) and the language-corpus channel does not (β={v('nhfourlang')}, p={v('nhfourlangp')}); but coverage and HDI correlate at ρ={v('nrhocobhdi')}, and with HDI×dependence in the same model HDI survives (β={v('nhfourjhdi')}, p={v('nhfourjhdip')}) and coverage does not (β={v('nhfourjcob')}, p={v('nhfourjcobp')}) | **Identified only up to the pair coverage-or-development.** Rules out the language channel; not causal |
| **H5** | Open frontier closes the gap vs closed | Closed advantage **{v('nhfive')} pp** | Descriptive |
| **H6** | Persona narrows the gap | DiD **{v('ndid')} pp** (permutation p={v('npersonap')}) | Not supported |
<!-- numbers:end -->"""
p = ROOT / "README.md"; s = p.read_text(encoding="utf-8")
if "<!-- numbers:begin" in s:
    s = re.sub(r"<!-- numbers:begin.*?<!-- numbers:end -->", block, s, flags=re.S)
else:
    i = s.index("| # | Hypothesis | Finding | Evidence status |"); j = s.index("\n\n", i)
    s = s[:i] + block + s[j:]
p.write_text(s, encoding="utf-8"); print("README: bloco de hipóteses regenerado")
