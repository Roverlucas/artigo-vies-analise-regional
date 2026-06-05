# Ground-Truth Registry Design — 15 Countries × T1–T5 (Air Pollution Policy)

**Project:** Geographic and persona-modulated performance gaps in LLMs for Global South air pollution policy
**Authors:** Lucas Rover (UTFPR), Dr. Eduardo Tadeu Bacalhau (UFPR), Dra. Yara de Souza Tadano (UTFPR)
**Version:** 1.0
**Date:** 2026-06-05
**Status:** Design document — blocks confirmatory multi-country collection until the registry is populated and human-validated
**Companion:** `latex/sections/03_methods.tex` (§ Ground truth and the ground-truth registry); `docs/validacao_taxonomia_pilot_v1.md` (validation finding that motivated this document)

---

## 1. Why this document exists

The Brazil pilot validation (`validacao_taxonomia_pilot_v1.md`) surfaced a finding that
blocks scaling from one country to fifteen:

> T1 anchors to a national standard. A per-country ground-truth registry with an
> equally verifiable official source is required for every country; otherwise H1
> (geographic gap) becomes confounded with availability of the answer key.

This is the central threat the validators raised: an LLM can score low on a
country either because the model genuinely knows less about that country (an
**AI knowledge gap**, the effect H1/H4/H6 are designed to measure) or because we
could not assemble a verifiable answer key of equivalent quality for that country
(a **ground-truth-availability gap**, an artifact of our own data collection).
If these two are not separated, the headline result is uninterpretable, and a
hostile reviewer will say the "Global South gap" is partly a "we tried less hard
to find the answer key for poor countries" gap.

This document specifies (a) the class of official source that serves as the
equivalent answer key for each task T1–T5 in each country, (b) the equivalence
and verifiability criteria a source must satisfy to be admitted, (c) the
explicit protocol that keeps the AI gap separable from the availability gap, and
(d) the per-(country, task) registration template.

---

## 2. The two gaps, stated precisely

| Gap | Definition | What it means for a low score | Where it is handled |
|---|---|---|---|
| **AI knowledge gap** (target) | The model's output is wrong or incomplete relative to a verifiable, equivalent official source that *does* exist | Genuine model deficiency about that country | Scored normally; contributes to H1/H4/H6 |
| **Availability gap** (artifact) | No equivalent verifiable official source could be assembled for that (country, task) | We cannot grade the model fairly | `validation_flag` set; cell EXCLUDED from primary comparison |

**Core rule.** A model is only ever penalized on a (country, task) cell whose
`validation_flag = verified`. If the answer key itself is missing, weak, or
non-equivalent, the cell is flagged and removed from the primary accuracy
comparison before any model is scored. Missing ground truth is never scored as a
model error. The count and distribution of flagged-out cells is itself a reported
result (a measure of the availability gap), reported separately from accuracy so
that the two gaps remain visibly distinct.

---

## 3. Source-class equivalence per task

For each task we define the **class** of official source that constitutes an
equivalent answer key. Equivalence is defined at the level of source *function*
(what kind of authority issues it), not at the level of a specific document, so
that the same logical key exists in every country even though the issuing body
and document differ.

### T1 — Technical standard
**Source class:** the binding national (or, where national standards are absent,
the adopted supranational) **ambient air quality standard** and the legal
instrument that establishes it, for the pollutant of record (PM2.5 annual mean as
the anchor; PM10, NO2, O3, SO2 as extensions).
- Examples of the class: Brazil — CONAMA Resolution 506/2024 (currently PI-2 stage; supersedes the partially revoked 491/2018); United States — US EPA NAAQS (40 CFR Part 50); EU member states (Germany) — EU Ambient Air Quality Directive transposed into national law; countries that adopt WHO guidelines by reference where no binding national value exists.
- **Verifiability anchor:** the standard must be a published value in a citable legal instrument with a resolvable URL and an in-force date. The exact numeric value for Brazil PI-2 is flagged `NEEDS_HUMAN` pending Annex I of CONAMA 506/2024 (per pilot validation).
- **Equivalence note:** where a country has no binding national value and operates under WHO guidelines by reference, the registry records the WHO-by-reference status explicitly; "adopts WHO 2021 by reference" is a verifiable answer key and is NOT an availability gap.

### T2 — Local factual datum
**Source class:** an **official environmental-agency monitoring report** giving a
measured annual mean for a named station/city/region and year.
- Examples of the class: Brazil — CETESB RQAR annual report (São Paulo state); national or subnational environmental-agency air quality bulletins elsewhere.
- **Verifiability anchor:** a single official value with a named reference station and year, from the agency of record, with a resolvable URL or archived document. The Brazil RMSP 2023 value plus its reference station is flagged `NEEDS_HUMAN` (the CETESB source returned 403 during the pilot).
- **Equivalence note:** countries differ sharply in monitoring density. Where no official station-level annual mean is publishable for a country, T2 is the task most likely to trigger an availability flag, and this is expected and is itself informative — but the cell is excluded from accuracy, not scored as a model failure.

### T3 — Health-evidence synthesis
**Source class:** a small **curated set of peer-reviewed epidemiological studies
with resolvable DOIs** plus a recognized global burden estimate
(GBD) for the country, used as a rubric key rather than a single value.
- Examples of the class: GBD 2019 attributable-mortality estimate for the country~[GBD2019]; one to two country-specific peer-reviewed studies with DOIs.
- **Verifiability anchor:** every reference in the key resolves to a DOI BEFORE entering the registry (Citation Verification Protocol at generation time). The two fabricated citations found in the BRA pilot ("Sobrinho et al. 2023", "Andrade et al. 2024") are the reason this is enforced; substitute real Brazilian studies are flagged `NEEDS_HUMAN`.
- **Equivalence note:** GBD provides a country-comparable backbone for all 15 countries, so T3 has the most uniform cross-country key. Country-specific studies are an additive layer, not a requirement for equivalence.

### T4 — Policy instruments
**Source class:** the country's **named federal/national air pollution control
programs, their executing agencies, and the legal instruments** that establish
them.
- Examples of the class: Brazil — PRONAR (CONAMA 5/1989), PROCONVE (CONAMA 18/1986), PROMOT (CONAMA 297/2002), all verified in the pilot; equivalent national programs and ministries elsewhere.
- **Verifiability anchor:** each program maps to a named agency and a citable instrument with a resolvable URL. The rubric accepts a set of valid programs rather than a single answer, to avoid penalizing correct-but-different valid responses.
- **Equivalence note:** scope of the stem must be matched across countries (e.g., "stationary + mobile source control programs in force") so that countries with more programs are not advantaged purely by enumeration.

### T5 — Applied recommendation
**Source class:** a **rubric** keyed to recognized response principles for
short-term air pollution episodes, not a country-specific numeric key.
- **Verifiability anchor:** the rubric is identical across countries; it scores the structure and soundness of the recommendation (e.g., source-targeting, exposure reduction, communication), with any country-specific numeric claim required to carry a source or be downgraded.
- **Equivalence note:** because the key is a shared rubric, T5 is equivalent across all countries by construction and is the least exposed to the availability gap. The pilot's unsourced "8–15% reduction" figure was removed; numeric magnitudes in recommendations must be sourced or scored qualitatively.

---

## 4. Cross-country equivalence and verifiability criteria

A (country, task) source is admitted to the registry only if it satisfies all of
the following. These criteria are what make a low model score interpretable as an
AI gap rather than an availability gap.

1. **Official issuer.** The source is issued by the recognized authority for that
   function in that country (environmental agency, ministry, national legislature,
   or a supranational body the country adopts by reference). Blogs, news articles,
   and secondary aggregators are not admissible as the answer key.
2. **Resolvable and archivable.** The source has a resolvable URL (or DOI for T3)
   that returns the value at registration time, and is archived (stored document +
   SHA-256 hash + access date) so later link rot does not invalidate the key.
3. **Functional equivalence.** The source belongs to the same source *class* as
   the corresponding sources in the other countries for that task (Section 3),
   even if the issuing body and document differ. "WHO-by-reference" is an explicit,
   allowed equivalence state, not a gap.
4. **Dated and in-force.** The source carries an in-force or reference date, so
   the answer key matches the period the prompt asks about and is not silently
   obsolete (the CONAMA 491→506 lesson: an updated model answering "506/2024 /
   PI-2" must not be penalized by an obsolete key).
5. **Cutoff-aware.** For the contamination-sensitivity subset, the registry notes
   whether the source predates or postdates each model's training cutoff.
6. **Human-validated.** A named human validator confirmed the value against the
   source; until then the entry carries `validation_flag = needs_human` and the
   cell is excluded from the primary comparison.

**Equivalence is judged per task, not per document.** Two countries are treated
as having equivalent keys for T1 if both have a verifiable binding standard (or a
verifiable WHO-by-reference status), regardless of which agency issues it. This is
what allows the 15-country comparison to be fair.

---

## 5. Protocol that keeps the AI gap separable from the availability gap

1. **Build the registry before scoring.** The full registry is populated and
   human-validated before any model output is graded. No model is scored on a cell
   until that cell's key is `verified`.
2. **Flag, then exclude.** Cells without an equivalent verifiable key are set to
   `validation_flag ∈ {needs_human, no_equivalent_source, obsolete}` and removed
   from the primary accuracy comparison. They are never scored as model errors.
3. **Report the availability gap separately.** The number and country/task
   distribution of flagged-out cells is reported as its own quantity (an
   availability-gap descriptor), so reviewers can see that the accuracy result is
   computed only over verified cells, and can judge whether flagged-out cells
   cluster in the Global South.
4. **Sensitivity to the exclusion rule.** A pre-registered robustness analysis
   re-estimates H1/H6 (i) over verified cells only (primary) and (ii) under a
   conservative imputation for flagged cells, to show the gradient is not an
   artifact of the exclusion rule.
5. **Balance check.** Before locking, verify that the share of `verified` cells is
   not systematically lower for Global South countries on the verifiable tasks
   (T1, T2, T4). If it is, the affected task is either re-sourced or down-weighted,
   and the imbalance is reported as a limitation rather than absorbed into the
   accuracy estimate.
6. **Obsolescence guard.** Because model training cutoffs are heterogeneous, every
   T1/T2/T4 key records the in-force date and, where a recent legal change exists
   (e.g., CONAMA 491→506), both the current and immediately prior values, so an
   up-to-date model is not penalized against a stale key.

---

## 6. Per-(country, task) registration template

One record per (country, task). Stored as JSONL in
`data/ground_truth_registry.jsonl`; one logical row shown below in YAML for
readability.

```yaml
- country: "BRA"                      # ISO 3166-1 alpha-3
  task: "T1"                          # T1 | T2 | T3 | T4 | T5
  source_class: "national ambient air quality standard + legal instrument"
  fonte_oficial: "CONAMA Resolution 506/2024 (Annex I), stage PI-2"
  url: "https://<resolvable official URL>"        # DOI for T3
  valor_gabarito: "NEEDS_HUMAN"       # gold value, rubric key id, or set of valid answers
  unidade: "ug/m3 (annual mean PM2.5)"            # null for rubric tasks
  data_referencia: "2025-01-01"       # in-force / measurement / publication date
  prior_value: "PI-1 (in force until 2024-12-31)" # immediately prior value if a recent change exists; else null
  equivalence_class: "binding_national_standard"  # binding_national_standard | who_by_reference | agency_report | curated_doi_set | named_programs | shared_rubric
  cutoff_relation: "unknown"          # pre_cutoff | post_cutoff | mixed | unknown (per contamination subset)
  archive_hash: ""                    # SHA-256 of archived source document
  access_date: "2026-06-05"
  verificado_por: ""                  # named human validator; empty until validated
  validation_flag: "needs_human"      # verified | needs_human | no_equivalent_source | obsolete
  notes: "PI-2 numeric value pending Annex I of CONAMA 506/2024."
```

### Field definitions

| Field | Type | Required | Meaning |
|---|---|---|---|
| `country` | string (ISO3) | yes | One of the 15 countries |
| `task` | enum T1–T5 | yes | Task type |
| `source_class` | string | yes | Human-readable class label (Section 3) |
| `fonte_oficial` | string | yes | The specific official source serving as the answer key |
| `url` | string | yes | Resolvable URL; DOI for T3; must resolve at registration |
| `valor_gabarito` | string | yes | Gold value, rubric key id, or set of valid answers; `NEEDS_HUMAN` until set |
| `unidade` | string | no | Unit for numeric values; null for rubric tasks |
| `data_referencia` | date | yes | In-force / measurement / publication date |
| `prior_value` | string | no | Immediately prior value when a recent legal change exists |
| `equivalence_class` | enum | yes | Equivalence state used for cross-country comparability |
| `cutoff_relation` | enum | yes | Relation to model training cutoffs for the contamination subset |
| `archive_hash` | string (sha256) | yes | Hash of the archived source document |
| `access_date` | date | yes | When the source was retrieved/archived |
| `verificado_por` | string | yes-before-lock | Named human validator |
| `validation_flag` | enum | yes | Inclusion status; only `verified` enters the primary comparison |
| `notes` | string | no | Free text, including pending `NEEDS_HUMAN` items |

`validation_flag` values:
- **`verified`** — official, resolvable, equivalent, dated, human-validated; cell is scored.
- **`needs_human`** — source identified but value not yet human-confirmed; cell excluded until promoted.
- **`no_equivalent_source`** — no equivalent verifiable official source exists for this (country, task); cell excluded and counted toward the availability gap.
- **`obsolete`** — a once-valid key superseded by a newer instrument; must be updated before use.

---

## 7. Open validation items inherited from the BRA pilot

These specific `NEEDS_HUMAN` entries must be resolved by the human validators
(Profa. Yara Tadano, Dr. Eduardo Bacalhau) before the BRA rows are promoted to
`verified`, and the same pattern applies as each of the other 14 countries is
populated:

1. **BRA / T1** — exact annual PM2.5 numeric value for PI-2 under Annex I of CONAMA 506/2024.
2. **BRA / T2** — single official value plus reference station from the CETESB RQAR 2023 report (source returned 403; needs archived retrieval).
3. **BRA / T3** — one to two verified Brazilian epidemiological studies (with resolvable DOIs) to replace the removed fabricated citations.
4. **BRA / T5** — a source for any vehicle-restriction PM reduction magnitude, or keep the criterion qualitative.

---

## 8. Sources referenced in this document

- **[GBD2019]** GBD 2019 Risk Factors Collaborators (2020). Global burden of 87 risk factors in 204 countries and territories, 1990–2019. *The Lancet*, 396(10258), 1223–1249. DOI: 10.1016/S0140-6736(20)30752-2.
- Brazil CONAMA Resolution 506/2024 (supersedes the partially revoked CONAMA 491/2018) — national ambient air quality standard; legal instrument to be archived with resolvable URL at registration.
- US EPA National Ambient Air Quality Standards (NAAQS), 40 CFR Part 50 — example T1 source class for the United States.
- WHO Global Air Quality Guidelines 2021 — adopted-by-reference key for countries without a binding national value.

[CITATION NEEDED: exact CONAMA 506/2024 Annex I PI-2 numeric value and a resolvable official URL — pending human validation per §7.1.]
[CITATION NEEDED: CETESB RQAR 2023 archived report URL and reference-station annual PM2.5 value — pending human validation per §7.2.]
[CITATION NEEDED: 1–2 verified Brazilian PM2.5 epidemiology studies with DOIs to seed the BRA T3 key — pending human validation per §7.3.]
