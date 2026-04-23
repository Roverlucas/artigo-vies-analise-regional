# Pilot Calibration Study — 2026-04 Cohort

> **⚠️ PILOT — exploratory, not confirmatory. Not to be cited as final results. Used solely for SESOI calibration, infrastructure validation, and rubric stress-testing prior to OSF pre-registration.**

## Purpose

This pilot serves 4 functions before the confirmatory study:

1. **Signal detection** — is the Global South vs Global North gap visible in real data at the expected magnitude?
2. **Infrastructure validation** — do all LLM clients (API + local Ollama) return well-formed responses at expected latency?
3. **Rubric stress-test** — where does the 5-component rubric fail on real model outputs?
4. **SESOI calibration** — update variance components in SAP before OSF lock.

## Scope

| Dimension | Value |
|---|---|
| Countries | 4 (BRA, NGA, IND, USA) |
| Languages | English only (pilot; multilingual deferred to confirmatory) |
| Models | 4 (Claude Haiku 4.5, GPT-5-mini, Gemini 2.5 Flash, Lince-Mistral 7B local) |
| Prompts per country | 10 (same 10 slots, country-specific content) |
| Replications | 2 |
| **Total calls** | 4 × 4 × 10 × 2 = **320** |

**Budget impact:** ~US$ 1-2 total (Haiku ~$0.80, GPT-5-mini ~$0.20, Gemini free, Lince local free).

## Design principles

### Same 10 slots across 4 countries

Each country has the **exact same 10 (domain, task) combinations** — only the country-specific content varies. This enables clean between-country contrasts for pilot H1 signal check.

### Slot distribution

| Task | Count | Domains covered |
|---|:-:|---|
| T1 Factual recall | 2 | D1 policy, D3 environment |
| T2 Open generation | 2 | D1 policy, D2 socioeconomic |
| T3 Stakeholder list | 2 | D1 policy, D3 environment |
| T4 Source recommendation | 2 | D1 policy, D3 environment |
| T5 Calibration | 2 | D1 policy, D2 socioeconomic |

**10 prompts total per country.** Task and domain coverage maintained.

### Ground truth sources

For pilot, Lucas authors ground truth by consulting:

- **BRA:** IBGE, Ministério da Fazenda, MMA, ANA, DataSUS (first-hand knowledge)
- **NGA:** National Bureau of Statistics (nigerianstat.gov.ng), Federal Ministry of Environment, CBN
- **IND:** Ministry of Statistics (mospi.gov.in), MoEFCC, RBI
- **USA:** Census Bureau, EPA, BLS, BEA

Full ground truth catalog for pilot in `ground_truth_pilot.md`.

## Files in this directory

| File | Purpose |
|---|---|
| `README.md` | This file |
| `prompts_template.md` | Human-readable guide: 10 slot templates + fully filled BR example + guidance for NGA/IND/USA |
| `prompts_skeleton.jsonl` | Machine-readable: 40 prompts (4 countries × 10 slots) — BR filled, 30 stubs for Lucas to author |
| `ground_truth_pilot.md` | Documented ground truth references (authored with prompts) |
| `responses/` | LLM responses (populated after execution) |
| `analysis/pilot_findings.md` | Pilot results + go/no-go decision (populated after analysis) |

## Author flow

1. Lucas reviews `prompts_template.md` → approves the 10 slot design
2. Lucas fills `prompts_skeleton.jsonl` with content for NGA, IND, USA (BR already filled)
3. Lucas reviews ground truth in `ground_truth_pilot.md` and completes
4. `@experiment-runner` executes with 4 models
5. `@statistician` runs exploratory GLMM
6. Decision gate: proceed to OSF pre-registration or iterate pilot

**Expected time from author-start to decision gate: 3-4 days.**

## Explicit disclaimers

- **Not a confirmatory study.** Prompts authored by single researcher, not panel-validated.
- **Krippendorff α not computed** for pilot (only 1 rater). Formal α ≥ 0.70 applies to confirmatory rubric only.
- **Responses are not publishable** as evidence — only as pilot calibration artifact.
- **Pilot data will be superseded** by confirmatory run; overlap intentional.
