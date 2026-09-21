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
| **H1** (tier) | Global North/South gap (pre-specified sensitivity contrast) | Primary outcome, code verdict only (no judge): Global South returns the register value **{v('ncodegap')} pp** less often (country bootstrap {v('ncodegapci')}, permutation p={v('ncodegapp')}). Composite: {v('ntiergap')} pp (CI {v('ntiergapci')}; p={v('ntiergapperm')}); same size within the extension wave ({v('ntiergapwave')}), on the pre-specified 15 ({v('ntiergappre')}) and with the four EU members as one unit ({v('ngapeu')}, p={v('ngapeup')}). Exploratory decomposition by task: on the binding national standard the raw odds ratio is {v('norrawone')} with country-level CI {v('norrawoneci')} (permutation p={v('norrawonep')}; conditional GLMM {v('nortone')} {v('nortoneci')}); absent on T5 | Supported as a difference between groups (country as the unit); per-task decomposition exploratory, intervals wide |
| **H1** (gradient) | Monotonic development gradient | ρ={v('nrho')} with HDI (p={v('nrhop')}; Fisher 95% CI [{v('nrhocilo')},{v('nrhocihi')}]); ρ={v('nrhopre')} at the pre-specified n=15; never reaches 0.55 in any leave-one-out or weighting | **Not supported.** The interval includes both zero and the pre-specified 0.55: neither established nor excluded |
| **H4** | Corpus representation is the mechanism | Between countries, neither channel separates from development (sitelinks ρ={v('nhfoursite')}, p={v('nhfoursitep')}; partial p={v('nhfourpartialp')}). Within countries the response-level interaction is β={v('nhfourbeta')} (p={v('nhfourp')}), but with standard errors clustered by country p={v('nhfourclp')}, and the 25 country-level deficits correlate with coverage at ρ={v('nhfourctryrho')} (p={v('nhfourctryp')}; partial HDI {v('nhfourctrypartial')}, p={v('nhfourctrypartialp')}); language-corpus channel null (β={v('nhfourlang')}, p={v('nhfourlangp')}) | **Not established** once the country is the unit of inference; direction consistent with coverage; coverage-or-development open |
| **H5** | Open frontier closes the gap vs closed | Closed advantage **{v('nhfive')} pp** | Descriptive |
| **H6** | Persona narrows the gap | DiD **{v('ndid')} pp** (permutation p={v('npersonap')}); 90% country-bootstrap CI {v('ndidcinety')} pp, inside ±2 pp (TOST); persona main effect {v('npersonamain')} pp (p={v('npersonamainp')}) | Not supported; equivalent to no effect within 2 pp |
<!-- numbers:end -->"""
p = ROOT / "README.md"; s = p.read_text(encoding="utf-8")
if "<!-- numbers:begin" in s:
    s = re.sub(r"<!-- numbers:begin.*?<!-- numbers:end -->", block, s, flags=re.S)
else:
    i = s.index("| # | Hypothesis | Finding | Evidence status |"); j = s.index("\n\n", i)
    s = s[:i] + block + s[j:]
p.write_text(s, encoding="utf-8"); print("README: bloco de hipóteses regenerado")
