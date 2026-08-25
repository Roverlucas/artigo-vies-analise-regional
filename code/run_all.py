"""
run_all.py — Orchestrator script.

Runs the full pipeline from synthetic data generation through inference
and figure production. Serves as the canonical reproduction entry point.

Usage:
    python run_all.py             # Full synthetic pipeline
    python run_all.py --skip-sim  # Use existing synthetic data
    python run_all.py --real      # Real API execution (requires keys)
"""

from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODE = Path(__file__).resolve().parent


def step(name: str, cmd: list[str], cwd: Path = CODE) -> None:
    print("\n" + "=" * 70)
    print(f"  {name}")
    print("=" * 70)
    print(f"  $ {' '.join(cmd)}")
    print()
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"\n[FAIL] Step {name} failed with code {result.returncode}")
        sys.exit(result.returncode)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-sim", action="store_true",
                    help="Skip synthetic data generation")
    ap.add_argument("--real", action="store_true",
                    help="Run with real API calls (requires keys)")
    ap.add_argument("--quick-power", action="store_true",
                    help="Quick power analysis (n_iter=50); full=2000")
    ap.add_argument("--confirmatory", action="store_true",
                    help="Reproduce the real 25-country confirmatory results from "
                         "committed judge scores, regenerate Supplementary tables, "
                         "and run the integrity QA gate.")
    args = ap.parse_args()

    if args.confirmatory:
        # Confirmatory reproducibility: real committed data -> analyses -> tables ->
        # QA gate -> method audit (process <-> manuscript).
        py = sys.executable  # robust across environments where "python" is absent
        venv_py = ROOT / ".venv" / "bin" / "python"          # for statsmodels-based steps
        glmm_py = str(venv_py) if venv_py.exists() else py
        # ---- Scoring chain -------------------------------------------------
        # These must run first: everything downstream reads the CORRECTED scores.
        # The judge panel itself (analysis/run_judge_panel.py) and the
        # back-translation census (analysis/back_translation_audit.py) are NOT
        # here because they spend API credit; their outputs are committed and
        # these steps consume them.
        step("C1. Deterministic scoring of T2 (value vs official register)",
             [py, "analysis/score_numeric.py", "--task", "T2"])
        step("C2. Deterministic scoring of T3 (value vs official register)",
             [py, "analysis/score_numeric.py", "--task", "T3"])
        step("C3. Export corrected scores (code verdict + panel mean, one rule)",
             [py, "analysis/export_corrected_scores.py"])
        step("C4. Panel reliability on the full re-scored base (ICC, alpha)",
             [py, "analysis/panel_reliability_full.py"])

        # ---- Effects -------------------------------------------------------
        step("C5. Freeze: every published effect, published vs corrected",
             [py, "analysis/freeze_all_effects.py"])
        step("C6. Formal tests (primary family, n=25)",
             [py, "analysis/formal_tests.py", "--n25"])
        step("C7. Robust secondary tests (n=25)",
             [py, "analysis/robust_tests.py", "--n25"])

        # ---- Robustness ----------------------------------------------------
        step("C8. Adversarial attacks on the headline effect (H2)",
             [py, "analysis/robustness_h2.py"])
        step("C9. H2 restricted to verified-faithful translations",
             [py, "analysis/h2_faithful_subset.py"])
        step("C10. H4 with within-country variation (mechanism test)",
             [glmm_py, "analysis/h4_within_country.py"])
        step("C11. Power on the nulls, tier taxonomy, permutation arbiter",
             [py, "analysis/robustness_extra.py"])
        step("C12. Composite-weighting + E-value sensitivity",
             [py, "analysis/weighting_and_evalue.py"])
        step("C13. GLMM (mixed model) + persona manipulation check",
             [glmm_py, "analysis/glmm_and_manipcheck.py"])
        step("C14. Bayesian re-estimation (pymc)",
             [glmm_py, "analysis/bayesian_reestimation.py"])
        step("C15. Exploratory mediation, H4 (semopy)",
             [glmm_py, "analysis/mediation_h4.py"])

        # ---- Outputs and gates ---------------------------------------------
        step("C16. Regenerate Supplementary tables",
             [py, "analysis/make_supplement_tables.py"])
        step("C17. Pre-correction baseline still reproduces (historical, NOT the "
             "manuscript's numbers — see consistency gate at C22)",
             [py, "analysis/qa_reproduce_claims.py"])
        step("C18. Method audit (process <-> manuscript: nothing described that was not executed)",
             [py, "analysis/method_audit.py"])
        step("C19. Journal format gate (GIQ highlights: 3-5 bullets, 85 chars each)",
             [py, "analysis/check_highlights.py"])
        step("C20. Corpus proxies recomputed on the corrected scoring",
             [py, "analysis/h4_proxies_corrigido.py"])
        step("C21. Primary family recomputed on the pre-specified 15 countries",
             [py, "analysis/pre15_corrigido.py"])
        step("C22. Consistency gate (body <-> supplement <-> freeze tell one story)",
             [py, "analysis/consistency_gate.py"])
        print("\n[Confirmatory reproduction complete — QA gate, method audit "
              "and consistency gate passed]")
        return

    # Step 1: Generate synthetic prompts (always)
    step("1. Generate prompts",
         [sys.executable, "-m", "benchmark.prompts"])

    if not args.skip_sim:
        # Step 2: Simulate outcomes (for pipeline validation)
        step("2. Simulate outcomes",
             [sys.executable, "-m", "benchmark.simulate_outcomes"])

    if args.real:
        # Step 3: Real API execution
        step("3. Run real experiment (API calls)",
             [sys.executable, "-m", "benchmark.run_experiment",
              "--output", str(ROOT / "data/raw/llm_responses/real_run.jsonl")])
        # Would continue with real rubric scoring, etc.
    else:
        print("\n[Synthetic mode — using simulated outcomes]")

    # Step 4: Descriptive analysis
    step("4. Descriptive analysis",
         ["python", "analysis/03_descriptive.py"])

    # Step 5: Inferential analysis
    step("5. Inferential analysis (H1, H2, H3)",
         ["python", "analysis/04_inference.py"])

    # Step 6: Power analysis
    if args.quick_power:
        step("6. Power simulation (quick)",
             [sys.executable, "-m", "benchmark.power.power_simulation", "--n_iter", "30"])
    else:
        print("\n[Power grid skipped — use --quick-power or run manually]")

    # Step 7: Self-review
    print("\n" + "=" * 70)
    print("  SELF-REVIEW CHECKLIST")
    print("=" * 70)
    checks = [
        (ROOT / "results/inference_summary.md",     "Inference summary"),
        (ROOT / "tables/h1_glmm.csv",               "H1 results"),
        (ROOT / "tables/h3_contrasts.csv",          "H3 contrasts"),
        # NOTE: as figuras em figures/simulation/ sao de dado SINTETICO (pre-coleta) e
        # nao entram no checklist de artefatos do paper. O manuscrito nao tem figura
        # confirmatoria ainda; quando tiver, apontar aqui.
        (ROOT / "data/processed/analytic_synthetic.parquet", "Synthetic dataset (pipeline validation only)"),
    ]
    for path, label in checks:
        status = "OK" if path.exists() else "MISSING"
        print(f"  [{status}] {label}: {path.relative_to(ROOT)}")

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
