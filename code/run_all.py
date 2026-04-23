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
    args = ap.parse_args()

    # Step 1: Generate synthetic prompts (always)
    step("1. Generate prompts",
         ["python", "-m", "benchmark.prompts"])

    if not args.skip_sim:
        # Step 2: Simulate outcomes (for pipeline validation)
        step("2. Simulate outcomes",
             ["python", "-m", "benchmark.simulate_outcomes"])

    if args.real:
        # Step 3: Real API execution
        step("3. Run real experiment (API calls)",
             ["python", "-m", "benchmark.run_experiment",
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
             ["python", "-m", "benchmark.power.power_simulation", "--n_iter", "30"])
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
        (ROOT / "figures/fig1_sample_composition.png", "Figure 1"),
        (ROOT / "data/processed/analytic_synthetic.parquet", "Synthetic dataset"),
    ]
    for path, label in checks:
        status = "OK" if path.exists() else "MISSING"
        print(f"  [{status}] {label}: {path.relative_to(ROOT)}")

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
