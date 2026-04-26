# Citation Verification Protocol — Academic Squad Hardening

**Version:** 1.0
**Date:** 2026-04-26
**Trigger:** Pre-registration v3.0 contained 3 fabricated citation attributions. Detected by external auditor before submission. **This protocol exists to ensure that never happens again.**

---

## 1. Mandatory pre-deposit / pre-submission gates

Before ANY artifact (pre-registration draft, manuscript, supplement, cover letter, OSF deposit, response to reviewer) leaves the project, it MUST pass the four-gate citation chain below. **Skipping any gate aborts the submission.**

### Gate 1 — Citation Sentinel Stage 1 (CSS-1)

**Agent:** `@citation-sentinel` running in **stage 1: existence verification**.

**Verifies for every cited reference:**
1. **Identifier exists.** DOI resolves; OR arXiv ID returns valid metadata via arXiv API; OR ISBN resolves on WorldCat. Each verified by direct API call (not memory).
2. **Author surname matches.** Comparison against ground-truth metadata returned by the API.
3. **Year matches.** Published year in metadata matches the year cited.
4. **Title matches.** Substring match (≥80% similarity) between citation title and metadata title.

**Output:** `verification_log_stage1.csv` with one row per cited reference: `[citation_key, doi, arxiv_id, author_match, year_match, title_match, status]` where status ∈ {OK, MISMATCH, NOT_FOUND}.

**Fail criterion:** ANY row with status ≠ OK aborts the gate.

### Gate 2 — Citation Sentinel Stage 2 (CSS-2)

**Agent:** `@citation-sentinel` running in **stage 2: claim verification**, executed by a **different invocation** (different chat / different time window) than Stage 1 to prevent contamination.

**Verifies for every numerical or factual claim attributed to a paper:**
1. The claim's exact text in the document is checked against the actual source text (abstract, full paper text where retrievable).
2. Numbers (percentages, sample sizes, effect sizes, p-values, CI bounds) attributed to a paper are searched verbatim or to within ±5% of the cited value in the source.
3. Methodology attributions (e.g., "X used method Y") are checked against the source's methodology section if accessible.

**Output:** `verification_log_stage2.csv` with one row per attributed claim: `[citation_key, claim_text, source_text_snippet, match_type, status]` where match_type ∈ {EXACT, NUMERICAL, PARAPHRASE, FABRICATED, UNVERIFIABLE}.

**Fail criterion:** ANY claim with status ∈ {FABRICATED, UNVERIFIABLE} aborts the gate.

### Gate 3 — Project Auditor Cleanup Pass

**Agent:** `@project-auditor` (NEW; see §2 below).

**Sweeps the entire project repo:**
1. Detects orphan citations (cited in document but missing from references file).
2. Detects unused references (in `.bib` but never cited).
3. Detects duplicate references with different keys.
4. Detects broken cross-references (e.g., `[Ref-12]` where Ref-12 is undefined).
5. Detects inline TODO / `\placeholder` / `[REDACTED]` markers.
6. Detects sections marked superseded but still active.
7. Cross-checks file modification times against git commit history for consistency.

**Output:** `project_audit_report.md` with all detected issues, classified P0 (must fix) / P1 (should fix) / P2 (nice to fix).

**Fail criterion:** ANY P0 issue aborts the gate.

### Gate 4 — Orquestrador (Sage) Final Review

**Agent:** `@academic-chief` (Sage), executed manually by the orchestrator (Lucas Rover).

**Manually reviews each citation in the document, one by one:**
1. Reads the citation context.
2. Cross-checks against `verification_log_stage1.csv` and `verification_log_stage2.csv`.
3. For any claim not directly verified by Stage 2 (e.g., paraphrases), confirms the paraphrase is faithful.
4. Signs the verification audit trail in `audit_trail/<artifact>_<date>_orchestrator_signoff.md`.

**Fail criterion:** Orchestrator must explicitly sign off in writing. No implicit approval.

---

## 2. NEW: Project Auditor agent specification

A new agent `@project-auditor` is added to the Academic Squad. Profile:

```yaml
agent:
  name: Project Auditor
  id: project-auditor
  title: Final-Pass Cleanup Auditor for Pre-Submission Artifacts
  trigger: invoked AFTER citation-sentinel stage 1 and stage 2; BEFORE orchestrator review
  responsibility: comprehensive sweep of the project to detect and report all
    structural/citation/reference issues before any artifact generation

scope:
  - Scan all .md, .tex, .bib, .json, .yaml files in the project tree.
  - Cross-check between artifact and references repo.
  - Flag inconsistencies between manuscript, pre-registration, supplements,
    and code that could indicate stale text or missed updates.
  - Verify all SHA-256 hashes in run manifests against actual file contents.
  - Verify version numbers and date stamps are consistent across documents.

output:
  - audit_trail/project_audit_<timestamp>.md
  - blocks artifact generation if P0 issues found

instruction_to_orchestrator:
  - "Do not invoke artifact-generating tools (pandoc, latex, OSF deposit,
    submission) until Project Auditor returns ALL CLEAR or P0 issues are
    resolved with new commit + new audit pass."
```

---

## 3. Updated Academic Squad workflow

```
Old workflow:
  Manuscript / pre-reg → Manual orchestrator review → Generate file

New workflow:
  Manuscript / pre-reg
    ↓
  [Gate 1] Citation Sentinel Stage 1 (existence)  → fail blocks
    ↓
  [Gate 2] Citation Sentinel Stage 2 (claims)     → fail blocks
                                                   (different invocation)
    ↓
  [Gate 3] Project Auditor (sweep)                → fail blocks
    ↓
  [Gate 4] Orchestrator manual review (one-by-one) → must sign off
    ↓
  Generate artifact (PDF, OSF deposit, etc.)
```

---

## 4. Citation Verification Standards (CVS)

### What counts as a verified citation?

A citation is considered **verified** only if ALL of the following hold:
- The DOI/arXiv ID/ISBN exists and resolves.
- The metadata (authors, year, title) matches what is in the document.
- Any numerical claim attributed to the paper (a) appears verbatim in the source's abstract/text, OR (b) is a documented summary statistic computed from the source's data, OR (c) is explicitly marked as the author's own derivation/inference (not as the source's claim).

### What is NOT acceptable?

- Citing a "median X" or "average Y" that is **not in the source paper**.
- Citing a paper by a different author than the actual author.
- Citing year that does not match.
- Citing a method/framework as "from X" when X did not introduce it.
- Citing an arXiv ID that returns no metadata.

### Sanctions for non-compliance

If the orchestrator (Sage) detects a fabricated citation post-deposit:
1. **Immediately** withdraw the artifact (e.g., OSF withdraw + corrected version).
2. **Document** in `audit_trail/citation_incident_<date>.md` with full provenance.
3. **Update** Citation Verification Protocol with the specific failure mode.
4. **Reset** the affected pre-registration version number; e.g., v3.0 → v3.1 with explicit note "v3.0 superseded due to citation fabrication, see audit trail".

---

## 5. Citation tooling

The protocol mandates use of these tools where applicable:

- `arXiv API`: `https://export.arxiv.org/api/query?id_list=<id>` — for arXiv preprints.
- `Crossref API`: `https://api.crossref.org/works/<doi>` — for journal articles with DOIs.
- `Semantic Scholar API`: `https://api.semanticscholar.org/graph/v1/paper/<id>` — for cross-source verification.
- `OpenAlex API`: `https://api.openalex.org/works/<id>` — for additional metadata.

A helper script `scripts/verify_citations.py` is committed to the repo with the standard verification routines. Citation Sentinel Stage 1 invokes this script.

---

## 6. Triggering Events

This protocol is triggered for any of the following artifact types:
- OSF Pre-Registration deposit (any version)
- Journal manuscript submission
- Supplementary material deposit
- Conference paper submission
- Pre-print deposit (arXiv, OSF Preprints, etc.)
- Cover letter or rebuttal letter
- Grant proposal or thesis chapter

**It is NOT triggered for:**
- Internal-only working documents
- Personal reading copies (e.g., `*_LEITURA_PESSOAL.md` in `/tmp/`)
- Code comments / docstrings (which should still be accurate but are out-of-scope)

---

## 7. Living document

This protocol is itself subject to revision. Each revision logged:

| Version | Date | Trigger | Changes |
|---|---|---|---|
| 1.0 | 2026-04-26 | v3.0 fabricated citation incident | Initial protocol established with 4 gates + Project Auditor agent |

---

## 8. Acknowledgement

Lucas Rover (orchestrator, project lead) acknowledges receipt and approval of this protocol on the date of v1.0 commit. Profa. Dra. Yara de Souza Tadano and Dr. Eduardo Tadeu Bacalhau, as co-authors, will be notified of this protocol with the v3.1 pre-registration package and asked to confirm understanding by email.
