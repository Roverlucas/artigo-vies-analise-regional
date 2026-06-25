#!/usr/bin/env python3
"""
method_audit.py — process<->manuscript method audit (review-process gate).

Enforces the integrity rule: every method DESCRIBED in the manuscript must have a
real execution artifact, and no method that was NOT executed may appear in the text.

Two checks:
  (A) EXECUTED: each described method maps to a code artifact (script) and, where
      applicable, an output file. The artifact must exist.
  (B) FORBIDDEN: phrases naming methods that were NOT executed must NOT appear in
      latex/sections/*.tex or latex/supplement.tex. If found -> FAIL (remove or
      replace with what was actually done).

Run from repo root:  python3 code/analysis/method_audit.py
Exit 0 = audit clean; 1 = at least one violation.
"""
import os, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def P(*p): return os.path.join(ROOT, *p)

# (A) Described method -> executing artifact(s). All listed files must exist.
EXECUTED = {
    "Spearman / Mann-Kendall / partial / Bonferroni-Holm (H1, H4)": ["code/analysis/formal_tests.py"],
    "Wilcoxon / Mann-Whitney / Cliff's delta / bootstrap (H2, H3, floor, tier gap)": ["code/analysis/robust_tests.py"],
    "Composite 3-weighting sensitivity (equal / author / PCA)": ["code/analysis/weighting_and_evalue.py"],
    "E-value sensitivity (VanderWeele & Ding)": ["code/analysis/weighting_and_evalue.py"],
    "GLMM mixed model (crossed random intercepts country+model)": ["code/analysis/glmm_and_manipcheck.py"],
    "Persona manipulation check (role-frame acknowledgement)": ["code/analysis/glmm_and_manipcheck.py"],
    "Bayesian re-estimation of the geographic effect (pymc)": ["code/analysis/bayesian_reestimation.py"],
    "Exploratory mediation for H4 (semopy)": ["code/analysis/mediation_h4.py"],
    "Judge-panel reliability (ICC, Krippendorff)": ["code/analysis/krippendorff_3judges.py",
                                                    "data/confirmatory_PRIVATE/analysis/judge_panel_reliability.json"],
    "Supplementary data-driven tables (coverage, GT, covariates)": ["code/analysis/make_supplement_tables.py"],
    "Headline-number reproducibility gate": ["code/analysis/qa_reproduce_claims.py"],
}

# (B) Phrases that name NOT-executed methods. They must NOT appear in the manuscript.
#     (GLMM was run via statsmodels MixedLM, NOT pymer4/lme4 -> those R names are forbidden.)
FORBIDDEN = {
    r"pymer4":                         "GLMM was run via statsmodels MixedLM, not pymer4",
    r"lme4|glmer|\blmer\b":            "no R/lme4 fit on confirmatory data; use 'statsmodels MixedLM'",
    r"human-gold-validated subset|human gold-standard layer .*restrict": "no human-gold subset exists",
    r"by native[- ]speaker translators|and back-translated by native|by native speakers;": "native prompts were LLM-translated (Claude Sonnet 4.6), not human",
    r"Primary inference uses equal weights": "primary composite uses author-specified weights 0.30/0.25/0.15/0.15/0.15",
    r"training-data contamination":    "no contamination-flagged sensitivity analysis was executed (unless added)",
    r"10\{,\}000 iterations|10,000 iterations": "verify/realign the power-simulation iteration count actually run",
}

TEX = glob.glob(P("latex","sections","*.tex")) + [P("latex","supplement.tex")]

print("="*74); print("METHOD AUDIT — process <-> manuscript"); print("="*74)
violations = 0

print("\n(A) EXECUTED methods — artifact present?")
for method, files in EXECUTED.items():
    missing = [f for f in files if not os.path.exists(P(*f.split("/")))]
    ok = not missing
    print(f"  [{'OK ' if ok else 'MISS'}] {method}")
    if missing:
        violations += 1
        for m in missing: print(f"         missing artifact: {m}")

print("\n(B) FORBIDDEN method names — absent from manuscript?")
for pat, why in FORBIDDEN.items():
    hits = []
    for t in TEX:
        for i, line in enumerate(open(t, encoding="utf-8"), 1):
            if re.search(pat, line):
                hits.append(f"{os.path.relpath(t, ROOT)}:{i}")
    if hits:
        violations += 1
        print(f"  [FAIL] /{pat}/ -> {why}")
        for h in hits: print(f"         {h}")
    else:
        print(f"  [OK ] /{pat}/ absent")

print("\n" + ("AUDIT CLEAN ✓" if violations==0 else f"{violations} VIOLATION(S) — fix before submission"))
raise SystemExit(0 if violations==0 else 1)
