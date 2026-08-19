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
        step("C1. Formal tests (primary family, n=25)",
             [py, "analysis/formal_tests.py", "--n25"])
        step("C2. Robust secondary tests (n=25)",
             [py, "analysis/robust_tests.py", "--n25"])
        step("C3. Composite-weighting + E-value sensitivity",
             [py, "analysis/weighting_and_evalue.py"])
        step("C4. GLMM (mixed model) + persona manipulation check",
             [glmm_py, "analysis/glmm_and_manipcheck.py"])
        step("C5. Bayesian re-estimation (pymc)",
             [glmm_py, "analysis/bayesian_reestimation.py"])
        step("C6. Exploratory mediation, H4 (semopy)",
             [glmm_py, "analysis/mediation_h4.py"])
        step("C7. Regenerate Supplementary tables",
             [py, "analysis/make_supplement_tables.py"])
        step("C8. Reproducible QA gate (recompute every headline number)",
             [py, "analysis/qa_reproduce_claims.py"])
        step("C9. Method audit (process <-> manuscript: nothing described that was not executed)",
             [py, "analysis/method_audit.py"])
        print("\n[Confirmatory reproduction complete — QA gate + method audit passed]")
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
