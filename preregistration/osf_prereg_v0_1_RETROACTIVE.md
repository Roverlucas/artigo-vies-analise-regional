# OSF Pre-Registration v0.1 — RETROACTIVE DEPOSIT

> **⚠️ AUDIT-TRAIL DOCUMENT**
>
> This is the **original** pre-registration draft as it stood on **2026-04-23**, prior to Pilot 2.0 calibration data and prior to the methodological audit of 2026-04-26. It is deposited **retroactively** on 2026-04-26 to maintain pre-registration integrity per OSF best practices on version control (Nosek et al. 2018; Chambers & Tzavella 2022).
>
> The **canonical (current) pre-registration** is `osf_prereg_draft.md` (v3.0), which incorporates corrections from the 2026-04-26 methodological audit. v3.0 supersedes both v0.1 (this document) and v2.0 (which was drafted on 2026-04-25 and withdrawn on 2026-04-26 due to identified pre-registration HARKing).
>
> This v0.1 document is preserved for audit transparency and to allow reviewers to trace the evolution of hypotheses across pilot calibration and audit. **It is not the active pre-registration.**

---

## v0.1 hypotheses as drafted on 2026-04-23 (pre-pilot)

| # | Hypothesis | Status in v0.1 |
|---|---|---|
| H1 | Geographic bias (GS lower than GN, Cohen's d ≥ 0.5) | Primary confirmatory |
| H2 | Language × country interaction (η²_p ≥ 0.05) | Secondary |
| H3a/b | Lince-Mistral 7B reduces or displaces BR gap | Secondary |
| H4 | log(CC tokens) correlates with country-level accuracy (ρ ≥ 0.60) | Secondary mechanism |
| H5 | Open-weight frontier ≥70B does not show practical deficit vs closed (TOST equivalence, ±5pp) | **Secondary** (the same H5 that was elevated to co-primary in withdrawn v2.0; in v0.1 it was secondary, predicting equivalence) |

## v0.1 design parameters (pre-pilot)

- 14 models full scope + 1 reserve
- 15 countries × ~30 prompts × 2 reps × 14 models = ~12,600 calls
- LLM-as-judge: Claude Haiku 4.5 single judge with Opus 4.7 IRR subset
- Variance components prior: σ²_country = 0.04 (ICC=0.150), σ²_model = 0.03 (ICC=0.030)
- SESOI for H1: 0.10 (10 percentage points) — based on Cohen heuristic moderate-effect convention

## What changed in v3.0 vs v0.1

| Element | v0.1 | v3.0 |
|---|---|---|
| H1 SESOI | 0.10 | **0.07** (defended ex-ante via Naous + Romanou + Manvi) |
| H4 mechanism proxy | log(CC tokens) primary | **Wikipedia article counts primary**, CC secondary with 3 operationalizations |
| H5 status | Secondary (predicting equivalence, open ≈ closed) | **Exploratory** (predicting tier effect, declared as pilot-derived) |
| Judge protocol | Single Haiku + Opus IRR subset | **3-judge ensemble** (Haiku + GPT-5-mini + Gemini Flash) + human gold subset (n=800) |
| Composite outcome | Single primary outcome | **Per-component primary**, composite demoted to secondary |
| T5 calibration | Brier on confidence-as-stated | **Brier on explicit probability ±10%** (prompt rewritten) |
| H3 model | Lince-Mistral 7B (Spanish, was misidentified as BR-PT) | **Cabra-Mistral 7B v3** (verified BR-PT instruct) |
| Stratification | Implicit | Explicit table with UNCTAD × Joshi × WB |

## v2.0 (intermediate, WITHDRAWN)

A v2.0 was drafted on 2026-04-25 attempting to elevate H5 to co-primary based on Pilot 2.0 observation of 12.5pp open-weight gap. **This version was withdrawn on 2026-04-26** following methodological audit which identified the elevation as pre-registration HARKing. v2.0 is preserved in git history (commit hashes available) but is not deposited at OSF.

---

## Provenance

| Date | Event | Hash |
|---|---|---|
| 2026-04-23 | v0.1 drafted | (multiple commits in git log preceding 2b7cbdc) |
| 2026-04-25 | v2.0 drafted (WITHDRAWN) | commits ca81855, 4d493ac, 08e7cc2 in git log |
| 2026-04-26 | Methodological audit | (received from reviewer) |
| 2026-04-26 | v0.1 deposited retroactively (this document) | TBD |
| 2026-04-26 | v3.0 deposited as active pre-registration | TBD |

This document is licensed CC-BY-4.0.
