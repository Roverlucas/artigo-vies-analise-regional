# Orchestrator Signoff — OSF Pre-Registration v3.1

**Artifact:** `preregistration/osf_prereg_draft.md` (v3.1) and corresponding PDF
**Document hash:** Git commit `b71c8c4` (and any subsequent corrections committed before deposit)
**Orchestrator:** Sage (academic-chief), executed by Lucas Rover
**Date of signoff:** 2026-04-26 17:30 UTC

---

## CVP Gate execution summary

| Gate | Agent | Status | Log |
|---|---|:-:|---|
| 1 | Citation Sentinel Stage 1 | ✅ **PASS** (4/4 OK) | `audit_trail/verification_log_stage1_20260426T172530Z.csv` |
| 2 | Citation Sentinel Stage 2 | ✅ **PASS** (9/9 OK, 0 FABRICATED) | `audit_trail/verification_log_stage2_20260426T172930Z.csv` |
| 3 | Project Auditor sweep | ✅ **ALL CLEAR** (P0 = 0) | `audit_trail/project_audit_20260426T172604Z.md` |
| 4 | Orchestrator manual review | ✅ **THIS DOCUMENT** | (this signoff) |

---

## Disclosed protocol deviation: same-session execution

**Strict CVP requirement:** Stage 1 and Stage 2 must be invoked in **different sessions / time windows**.

**Actual execution:** Both stages executed within the same orchestration session (~5 minutes apart) on 2026-04-26 between 17:25 and 17:30 UTC.

**Mitigation rationale (why this is acceptable for v3.1):**
1. **Independent API queries.** Stage 2 issued fresh arXiv API calls; it did NOT cache or reuse data from Stage 1.
2. **Independent claim extraction.** Stage 2 read claims directly from the document (`preregistration/osf_prereg_draft.md`) and the citations YAML (`citations/osf_prereg_v3_1.yaml`), not from Stage 1 outputs.
3. **Numerical match enforced.** Each numeric claim was searched verbatim or to within ±5% in the freshly-fetched source abstract; this is mechanical, not interpretive.
4. **Explicit user authorization.** The user (Lucas Rover, project lead) explicitly authorized same-session execution after being informed of the strict requirement.

**Acknowledgement of residual risk:** Some forms of pollution that cross session boundaries are not addressable by mechanical re-querying — for example, a fabricated number that happens to also appear in the abstract of a different paper. We mitigate this by requiring `match_type=NUMERICAL` plus `text_match=True` simultaneously (i.e., the number AND surrounding paraphrase must both match the same source). All 7 numerical claims in v3.1 satisfy both conditions.

**Future-proofing:** For the next artifact (manuscript submission), Stage 1 and Stage 2 will be executed in separate sessions per the strict invariant. This deviation is logged once for the OSF pre-registration deposit specifically.

---

## Orchestrator manual review (claim-by-claim)

I (Sage, executing on behalf of Lucas Rover) read each citation in `preregistration/osf_prereg_draft.md` § 1.4 and confirm the following:

### chiu2024culturalbench (arXiv:2410.02677) — CulturalBench

- **Claim 1:** "Reports best-frontier-LM accuracy on the Hard subset ranging from 28.7% to 61.5% across 45 regions"
  - **Verification:** arXiv abstract confirms: *"the hard version of CulturalBench is challenging even for the best-performing frontier LMs, ranging from 28.7% to 61.5% in accuracy"* and *"covering 45 global regions"*. **VERIFIED.**
- **Claim 2:** "Documented under-performance on questions about North Africa, South America, and Middle East"
  - **Verification:** arXiv abstract confirms: *"models under-perform on questions related to North Africa, South America and Middle East"*. **VERIFIED.**

### romanou2024include (arXiv:2411.19799) — INCLUDE

- **Claim 1:** "Constructs an evaluation suite of 197,243 QA pairs from local exam sources... 44 languages"
  - **Verification:** arXiv abstract confirms: *"we construct an evaluation suite of 197,243 QA pairs from local exam sources... across 44 written languages"*. **VERIFIED.**

### manvi2024geographic (arXiv:2402.02680) — Geographically Biased

- **Claim 1:** "Spearman rho up to 0.89 for factual variables"
  - **Verification:** arXiv abstract confirms: *"strong monotonic correlation with ground truth (Spearman's $ρ$ of up to 0.89)"*. **VERIFIED.**
- **Claim 2:** "Bias against lower-socioeconomic locations on subjective topics, Spearman rho up to 0.70"
  - **Verification:** arXiv abstract confirms: *"LLMs are clearly biased against locations with lower socioeconomic conditions... such as attractiveness, morality, and intelligence (Spearman's $ρ$ of up to 0.70)"*. **VERIFIED.**

### naous2023beer (arXiv:2305.14456) — CAMeL / Having Beer after Prayer

- **Claim 1:** "Multilingual and Arabic monolingual LMs exhibit bias toward Western culture"
  - **Verification:** arXiv abstract confirms: *"multilingual and Arabic monolingual LMs exhibit bias towards entities associated with Western culture"*. **VERIFIED.**
- **Claim 2:** "Introduces CAMeL framework"
  - **Verification:** arXiv abstract confirms: *"We introduce CAMeL"*. **VERIFIED.**

---

## SESOI defense check

The SESOI = 7pp defense in v3.1 § 1.4 is framed as **decision-theoretic**, not as a copied number from any specific paper. The cited literature (Chiu, Romanou, Manvi) is used to establish that *region-level gaps in the tens of percentage points are documented* — and 7pp is positioned as a conservative lower-bound. This framing is honest and does not attribute invented medians to any source.

**Manual confirmation:** the v3.1 § 1.4 explicitly states *"We do not claim that any of the cited papers reports a 'median 7pp' or 'median 8pp' or 'median 12pp' — those specific point estimates are not in those papers and were incorrectly attributed in a prior draft (v3.0)."* This disclosure is appropriate.

---

## Composite weights check

The v3.1 § 4.2 declares author-specified weights (0.30/0.25/0.15/0.15/0.15) **as such**, not as derived from any prior framework. PCA-derived and equal-weights are pre-registered as primary; the author-specified weights are sensitivity. **Honest framing confirmed.**

---

## CC operationalizations check

CC-Op1 ("internet-penetration-weighted population") replaces the v3.0 tautological "GDP share". The new operationalization uses ITU/World Bank Internet Users statistic, which is independent of the country GDP that we are also using as a covariate in H4. **No tautology confirmed.**

---

## Final verdict

**ALL FOUR CVP GATES PASS.** Pre-registration v3.1 is **cleared for OSF deposit and supervisor approval distribution.**

Sage (academic-chief) signs off on this artifact for distribution.

— Sage, executing the Citation Verification Protocol on behalf of Lucas Rover, 2026-04-26
