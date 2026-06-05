# OSF Pre-Registration v7 — SKELETON (declared diffs from v6)

**Version:** 7.0-skeleton
**Date:** May 2026
**Status:** Draft skeleton with declared changes from v6 — awaiting coauthor endorsement before full rewrite + OSF deposit
**Predecessor:** `osf_prereg_draft.md` (v6, 2026-04-26)

---

## Purpose of this skeleton

This document declares **what changes** from pre-registration v6 to v7. It is intended for review by coauthors (Profa. Yara Tadano, Dr. Eduardo Bacalhau) **before** the full v7 manuscript is rewritten. Upon endorsement, `submission-engineer` (Atlas) regenerates the full v7 pre-registration following OSF Standard Pre-Registration template.

**Critical principle:** v6 was never deposited at OSF. v7 supersedes v6 entirely — no amendments needed because no public record exists yet. The BRA data already collected (839 responses, 2026-04-28) is reclassified as **extended pilot** in v7 (declared in §2.4 "Prior data").

---

## §0 — Diff summary (v6 → v7)

| Section | v6 | v7 | Rationale |
|---|---|---|---|
| **Scope** | 3 domains (D1 policy, D2 socioeconomic, D3 environmental) generic | **1 domain**: Air Pollution Policy (single, theory-driven) | Strengthens domain expertise of co-supervisor (Yara, PPGSAU); ties to WHO/CONAMA/CETESB official ground truth; opens environmental policy journals as additional editorial targets |
| **Persona** | Not declared (implicit "neutral query") | **Within-subject manipulation**: neutral vs public_manager_env | Adds H6 confirmatory; turns "design limitation" into "methodological contribution"; addresses live debate on prompt engineering for high-stakes domains |
| **Hypotheses** | H1+H4 co-primary; H3 secondary; H2+H5 exploratory | H1+H4+**H6** co-primary; H3 secondary; H2+H5 exploratory | New H6 declared as confirmatory; rationale in §1.4 |
| **Prompts** | 780 (3 domains × 5 tasks × matrix) | **600** (1 domain × 5 tasks redesigned × 15 countries × ~8 prompts each) | Single-domain focus increases prompts-per-domain and statistical power within the domain |
| **Tasks** | 5 generic (T1-T5) | **5 redesigned for AP Policy** (norma técnica, dado factual local, síntese evidência saúde, instrumentos política, recomendação aplicada) | Each task maps to a real decision activity of a public environmental manager |
| **Total calls** | 21,840 (780 × 14 × 2 reps) | **336,000** (600 × 14 × 2 personas × 2 reps) | Persona within-subject increases by 2×; partly offset by fewer prompts; absorbed by free tiers + Ollama |
| **Cost (paid APIs)** | ~US$ 16 | **~US$ 25-28** | Increase of ~US$ 10-12; covered by R$ 200 cash reserve |
| **Reference model** | Cabra-Mistral 7B v3 (BR-Portuguese) primary; Gemini 2.5 Pro reserve | Unchanged | Cabra-Mistral remains H3 secondary test |
| **Prior data status** | BRA confirmatory (839 responses) | **BRA extended pilot** (reclassified; new confirmatory collection from scratch) | Cleanly preserves confirmatory status; BRA pilot informs prompt calibration |

---

## §1.3 — Research Questions (revised)

**Confirmatory primary:**

- **RQ1.** Across a continuous gradient of country-level digital and developmental conditions (Joshi class, HDI, Common Crawl + Wikipedia representation), do LLMs exhibit systematically lower factual accuracy on **air pollution policy** tasks?
- **RQ2.** Does country-level training-corpus representation account for the country-level accuracy gradient in **air pollution policy** tasks, after controlling for HDI and GDP per capita?
- **RQ3 (NEW).** Does **persona prompting** (presenting the query as coming from a public environmental manager) reduce or amplify the country-level accuracy gradient? In particular, does persona shift LLM behavior toward higher recall of official regulatory information?

**Confirmatory secondary:**

- **RQ4.** Does a regional Brazilian-Portuguese-instruction-tuned open-weight model (Cabra-Mistral 7B v3) reduce the Portuguese-language accuracy gap for Brazil on air pollution policy tasks?

**Declared exploratory:**

- **RQ5.** Open-weight vs closed-accessible tier comparison on air pollution policy accuracy.
- **RQ6.** Prompt language × country interaction on air pollution policy accuracy.

---

## §1.4 — Hypotheses (revised)

### Primary confirmatory

- **H1 (primary test):** Country-level mean accuracy on air pollution policy tasks increases monotonically with Joshi class AND HDI quartile. Spearman ρ ≥ 0.55 (one-sided, α = 0.05) at country level (n=15).
  - Non-monotonicity check: Mann-Kendall trend test (mandatory complementary).
  - Sensitivity: UNCTAD G77+China binary dummy.
- **H4 (mechanism, primary):** Country-level corpus representation (Wikipedia article counts as primary proxy; Common Crawl with three operationalizations as secondary) correlates with country-level accuracy AND partially explains the country-level gradient after adjusting for HDI and log GDP per capita. Partial Spearman ρ ≥ 0.55 (Wikipedia) AND ≥0.40 in ≥2/3 of CC operationalizations (convergent-validity criterion). E-value sensitivity threshold = 2.0.
- **H6 (persona effect, NEW co-primary):** The persona condition (public_manager_env) **reduces** the country-level accuracy gradient for Global South countries by at least **5 percentage points absolute accuracy** compared to the neutral condition, on the composite primary outcome.
  - **Primary test:** Difference-in-differences (DiD) of country mean accuracy: (persona accuracy in Global South) − (neutral accuracy in Global South) vs (persona accuracy in Global North) − (neutral accuracy in Global North). One-sided test for reduction in gap; α = 0.05.
  - **Effect-size threshold:** Absolute gap reduction ≥ 5 pp considered meaningful; ≥ 10 pp considered substantial.
  - **Alternative-direction sensitivity:** Two-sided test reported as secondary; persona amplification (negative effect) is theoretically possible (e.g., authoritative persona increases hallucination of regulatory specifics) and reported transparently if observed.
  - **Theoretical motivation:** Persona prompting may reduce bias if instruction-following + RLHF training emphasized helpful policy-relevant responses in high-resource countries (Norm-Compliance hypothesis), OR may amplify bias if the model's representation of "Global South public manager" lacks training signal (Persona-Vacuum hypothesis). H6 tests Norm-Compliance against the alternative; both directions are scientifically informative.
  - **Power note:** Within-subject persona manipulation provides high power (n=600 prompts × 15 countries × 14 models × 2 personas, all paired). Minimum detectable effect at α=0.05 / power=0.80 is approximately 2-3 pp absolute gap reduction; the 5 pp threshold is well-powered.

### Secondary confirmatory

- **H3 (Cabra-Mistral regional model):** Cabra-Mistral 7B v3 reduces the Portuguese-language accuracy gap for Brazil on AP policy tasks, relative to scale-matched globally-trained open model (Llama 3.1 8B). Pre-registered as one-sided contrast in the GLMM, α = 0.05. **Exploratory companion:** does Cabra-Mistral close or displace the gap onto other Lusophone contexts (Lusophone Africa) where AP policy ground truth exists?

### Declared exploratory

- **H2:** Prompt language × country interaction (cross-lingual matrix). Reported descriptively + BH FDR q=0.10 if formal tests applied.
- **H5:** Open frontier (Tier A) vs closed frontier (Tier E) on AP policy accuracy. Reported descriptively.

---

## §3 — Design (revised summary)

| Factor | Levels | Type |
|---|---|---|
| Country | 15 (BRA, IND, NGA, MEX, ARG, PER, ZAF, KEN, EGY, IDN, BGD, PHL, USA, DEU, JPN) | Between |
| Model | 14 (Tier A 5 + Tier B 3 + Tier C 2 + Tier D 2 + Tier E 1) | Between |
| **Domain** | **1 (Air Pollution Policy)** | (Single — was 3 in v6) |
| Task | 5 (T1 norma técnica, T2 dado factual local, T3 evidência saúde, T4 instrumentos política, T5 recomendação aplicada) | Within-country |
| **Persona** | **2 (neutral, public_manager_env)** | **Within-prompt (NEW)** |
| Prompt language | English (all countries) + 1 native language for 7 stratified countries | Within-country |
| Replication | 2 per (model, prompt, persona) tuple | Within |

**Total prompts:** ~600 unique (15 countries × ~40 prompts/country across 5 tasks and language matrix).
**Total calls:** ~336,000 (600 × 14 models × 2 personas × 2 reps).

---

## §3.2 — Task taxonomy for Air Pollution Policy domain (NEW)

Each task maps to a recognizable decision activity of a public-sector environmental manager:

| Task | Name (PT) | Description | Example (BRA) |
|---|---|---|---|
| **T1** | Norma técnica | Recall of binding ambient air quality standards, emission limits, or regulatory thresholds | Annual mean PM2.5 standard per CONAMA 491/2018 |
| **T2** | Dado factual local | Recall of officially measured air quality data for a specific city/region/year | Annual PM2.5 in RMSP 2023 per CETESB |
| **T3** | Síntese de evidência em saúde | Synthesis of peer-reviewed epidemiological evidence on health burden | Mortality attributable to PM2.5 in country X, 2015-2024 |
| **T4** | Instrumentos de política | Identification of policy programs, executing agencies, legal instruments | Federal air pollution control programs and ministries |
| **T5** | Recomendação aplicada | Rubric-scored applied recommendation for a defined operational scenario | Short-term episode response (thermal inversion, PM2.5 > 75 µg/m³) |

---

## §3.6 — Prior data status (revised)

**v6 status:** BRA confirmatory collection (839/840 responses, 2026-04-28) under 3-domain design.

**v7 reclassification:** BRA collection is reclassified as **extended pilot** in v7. Rationale:
1. v6 was never deposited at OSF — no public confirmatory status to defend.
2. v7 scope is narrower (1 domain vs 3) — only ~33% of BRA prompts (D3 environmental) are even partially relevant; none are specifically about air pollution policy.
3. v7 adds persona manipulation absent in BRA collection.
4. Cleaner narrative: BRA extended pilot informed v7 prompt calibration and instrumentation validation.

**Confirmatory collection** under v7 starts fresh, post-OSF-deposit, with the new 600-prompt design across all 15 countries (including a re-collection for BRA under the new design).

---

## §4 — Statistical Analysis Plan (changes from v6)

### §4.1 — Primary test of H1 (unchanged from v6)
Country-level Spearman ρ (n=15) on composite accuracy. Threshold ρ ≥ 0.55, one-sided.

### §4.2 — Primary test of H4 (unchanged from v6)
Partial Spearman ρ with two-proxy convergence (Wikipedia + Common Crawl operationalizations) + E-value sensitivity.

### §4.3 — Primary test of H6 (NEW)
**Specification:**
- Unit of analysis: country × model pair.
- Outcome: composite accuracy score per (country, model, persona) cell.
- Primary statistic: country-level DiD —
  Δ_GS = mean(persona_GS) − mean(neutral_GS)
  Δ_GN = mean(persona_GN) − mean(neutral_GN)
  H6 statistic = Δ_GS − Δ_GN
- One-sided test: H6 supported if Δ_GS − Δ_GN ≥ 0.05 (5 pp reduction in gap) with p ≤ 0.05.
- Permutation test for inference (5000 country-level permutations); reported alongside parametric paired-t.

### §4.4 — Multiple-testing correction
- F1 family (primary confirmatory: H1, H4, H6): Bonferroni-Holm across 3 primary tests.
- F2 family (secondary confirmatory: H3): unadjusted within-family.
- F3 family (declared exploratory: H2, H5): BH q=0.10.

### §4.5 — Power simulation
Power simulation (10,000 Monte Carlo iterations under prior-informed effect sizes from BRA extended pilot) is re-run for v7 design. Family-wise power for primary trio (H1, H4, H6) under Bonferroni-Holm reported in supplement.

---

## §5 — What stays from v6 (unchanged sections)

- §1.1 Title (minor revision to mention Air Pollution Policy)
- §1.2 Authors and affiliations
- §2.1 Sample selection (15 countries, stratification)
- §2.2 Model selection (14 LLMs, 5 tiers)
- §2.3 Country covariates (HDI, GDP, Joshi class, Wikipedia, Common Crawl)
- §5.4 Multi-judge LLM-as-judge ensemble + external annotators
- §6 Transparency and reporting standards (CONSORT-AI inspired)
- §7 Timeline, budget, sharing plan
- §8 Limitations
- §9 Citation Verification Protocol (CVP)

---

## §6 — What needs new authoring in full v7

- **§1.1 Title (new):** "Geographic and Persona-Modulated Performance Gaps in Large Language Models for Global South Air Pollution Policy: A Pre-Registered Audit"
- **§1.4 Hypotheses (revised, see above):** H6 + revised H1, H4 framing for AP Policy.
- **§3.2 Task taxonomy (new):** Detailed operationalization of T1-T5 for AP Policy.
- **§3.4 Persona protocol (new):** Exact wording, instruction template, randomization protocol, manipulation check.
- **§3.6 Prior data section (new):** Declaration of BRA extended pilot status.
- **§4.3 H6 SAP section (new):** DiD specification, permutation inference, power simulation.

---

## §7 — Endorsement workflow before OSF deposit

1. **Coauthor review** of this skeleton:
   - Profa. Yara Tadano (UTFPR/PPGSAU) — validate task taxonomy + ground truth quality on environmental domain.
   - Dr. Eduardo Bacalhau (UFPR) — validate statistical specification of H6 (DiD specification, permutation inference).
2. **Pilot prompt validation** — review of `data/ap_policy_pilot_bra_v1.jsonl` (10 BRA prompts, 5 tasks × 2 personas).
3. **Full v7 rewrite** by `submission-engineer` (Atlas), pulling unchanged sections from v6 and authoring new sections per §6 above.
4. **Coauthor sign-off** on full v7 document.
5. **OSF deposit** — upload v7 PDF, lock pre-registration, generate DOI.
6. **Confirmatory collection** under v7 begins (BRA first, replicating v6 BRA infrastructure validation).

---

**Estimated time from coauthor endorsement to OSF deposit:** 5-7 business days (Atlas full rewrite + final coauthor pass).
