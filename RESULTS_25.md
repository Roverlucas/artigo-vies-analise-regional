# Confirmatory Results — 15 vs 25 countries

Generated from `formal_tests.py`, `robust_tests.py`, `h4_corpus_mechanism.py`,
`krippendorff_3judges.py`. Primary judge: gpt5_mini (full, 25 countries).
The 25-country sample is a **post-registration extension**; the pre-registered
15-country result is reported alongside every effect.

## Primary family (Bonferroni-Holm)

| Test | 15 countries (pre-reg) | 25 countries (expansion) |
|------|------------------------|--------------------------|
| **H1** Spearman ρ(acc, HDI) | +0.143 (one-sided p=0.306) ns | **+0.512 (p=0.004)** — rejects H0 under B-H |
| H1 Mann-Kendall (HDI) | S=9, Z=+0.40, p=0.692 | S=102, Z=+2.36, **p=0.018** |
| H1 ρ(acc, Joshi) | +0.028 ns | −0.061 ns (gradient is development, not linguistic) |
| H1 vs pre-reg threshold ρ≥0.55 | not met | **not met** (significant but below the pre-specified effect size) |
| **H4** partial ρ(acc, Wiki-count\|HDI) | +0.218 (p=0.45) ns | +0.036 (p=0.87) ns |
| **H6** DiD persona (GS−GN) | +0.97pp, perm p=0.142 ns | +0.39pp, perm p=0.257 ns |

H1 nulo→significativo is the headline change; H4 (Wikipedia-count) and H6 stay null.

## H4 — corpus mechanism, multi-measure (25 countries)

| Measure | Family | ρ(acc, log measure) | partial \| HDI |
|---------|--------|--------------------|----------------|
| en_wiki_bytes | country | +0.198 (p=0.34) | +0.181 |
| **wd_sitelinks** | country | **+0.539 (p=0.005)** | +0.317 (p=0.13) |
| wd_statements | country | +0.313 (p=0.13) | +0.144 |
| Wikipedia edition count | language | +0.082 ns | +0.036 ns |

H4b (language-corpus → native penalty, n=3 langs, descriptive):
Spearman(penalty, log mC4) = −1.00; hi penalty +7.0pp (mC4 24B) → es +0.4pp (mC4 433B).
→ Country-coverage breadth (sitelinks) predicts accuracy; language-edition size does not.

## Robust secondary findings (25 countries)

| Finding | Statistic |
|---------|-----------|
| **H2** native vs English (all) | Δ=−2.1pp, Wilcoxon z=−3.10, **p=1.96e-3** (n=762) |
| H2 Spanish | Δ=−1.0pp, p=0.15 ns |
| H2 Portuguese | Δ=−2.3pp, **p=0.033** (now sig with PRT/AGO pairs) |
| H2 Hindi | Δ=−7.8pp, **p=0.013** |
| **Tier gap** GN−GS | +6.2pp, 95% CI **[+3.7, +8.6]** (15-country: +6.7 [+2.8,+10.2]) |
| **Task floor** T1+T2 vs T3-T5 | 0.367 vs 0.638, Mann-Whitney δ=**−0.64** |
| **H3** Cabra vs rest | 0.320 vs 0.543, δ=**−0.51** |

## Inter-judge reliability — panel (fixed sample, 131 items)

**Primary panel = 4 strong, vendor-diverse judges** (full 131-item coverage):

| Quantity | Value |
|----------|-------|
| Judges (vendors) | gpt5_mini (OpenAI), claude_sonnet (Anthropic), gemini_2_5_pro (Google), deepseek_v3 (DeepSeek) |
| Krippendorff α (interval) | 0.667 |
| ICC(2,1) single judge | 0.672 |
| **ICC(2,4) panel mean** | **0.891** |
| Pairwise Pearson | 0.61–0.86 (gemini most lenient; deepseek aligns 0.82–0.83) |

**Supplementary 5th judge (corroboration):** llama33_70b (Meta) on the 86 items it
covered before Groq rate-limiting — pairwise Pearson 0.51–0.60 with the four;
the 5-judge mean still gives ICC(2,5)=0.861 but α drops to 0.538 because the
weaker 70B judge adds noise. This empirically confirms that **4 strong judges
beat 5 with a noisier one** — more judges is not automatically safer.

**Excluded:** command_rp (Cohere trial quota exhausted mid-run, 5% coverage).

**Methodological note:** the panel sample must be frozen BEFORE judging, because
the validate_judge_agreement sampler re-draws from the live response base; when
the base grew (15→25 countries) between judging rounds the per-judge samples
desynchronised. `judge_fixed_keys.py` pins the sample to claude∩gemini's 131 items.

## Integrity notes
- 25-country sample is a transparent post-registration extension; 15-country reported alongside.
- H1 significant but below the pre-registered 0.55 effect-size threshold — reported as such.
- Sonnet-generated extra H2 variants (prompts_extra) were NOT collected/judged; H2 uses principal pairs only.
- No human gold layer; ground truth anchored to official primary sources via documentary audit.

## Robustness checks (internal review response)
- **LOCO H1 (HDI gradient)**: rho range [+0.48 (drop NGA), +0.66 (drop IND)] — robust; India ATTENUATES (without it rho=0.66).
- **Range extension**: the 10 added countries fall within the 15-country HDI range [0.548,0.950]; range-restricted rho=0.512 (p=0.009) — density not range.
- **H2 country-level (n=9, fixes pseudo-replication)**: 9/9 negative, mean -2.4pp, Wilcoxon p=0.008.
- **H4 FDR (3 coverage proxies, BH)**: sitelinks rho=0.54 BH-adj=0.016 (sig); statements/bytes ns. BUT partial|HDI p=0.13 → reported as suggestive/exploratory, NOT established mechanism.
- **Tier gap LOCO**: [+5.8, +7.1] pp stable.

## Review-driven integrity edits applied
- H4 softened to exploratory across abstract/intro/results/discussion/conclusion (pre-registered Wikipedia proxy null; sitelinks attenuates with HDI).
- Added robustness subsection (LOCO + range) defending the gradient against the range-extension critique.
- H2 reported at country level (independent unit) in addition to per-cell.
- India outlier explained (coverage account + LOCO).
- Judge panel reconciled to 4 operative + Llama(5th, corroborating) + Command R+ excluded.
- Typo 0.534->0.543; GN count clarified (7 GN-tier + 3 GS); single-domain limitation added.
