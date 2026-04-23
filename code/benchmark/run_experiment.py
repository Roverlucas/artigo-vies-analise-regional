"""
run_experiment.py — Main experiment runner.

Iterates (prompt × model × replicate), dispatches LLM calls, and writes
results to JSONL with daily checkpoints. Resumable: if interrupted,
re-running skips prompt_hash × model_id × replicate_idx already present
in output file.

Usage (synthetic mode for pipeline validation):
    cd code
    python -m benchmark.run_experiment --output ../data/raw/llm_responses/synthetic_run.jsonl

Usage (real execution, after API keys configured):
    BENCHMARK_SYNTHETIC=0 python -m benchmark.run_experiment \
        --output ../data/raw/llm_responses/run_YYYYMMDD.jsonl

Output: JSONL with one LLMResponse per line.
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from .config import LLMS, EXPERIMENT, DATA_RAW
from .prompts import load_prompts_jsonl
from .llm_clients import call_llm, LLMResponse


def _load_already_done(output_path: Path) -> set[tuple[str, str, int]]:
    """Build set of (prompt_hash, model_id, replicate_idx) already collected."""
    done: set[tuple[str, str, int]] = set()
    if not output_path.exists():
        return done
    with output_path.open(encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
                done.add((d["prompt_hash"], d["model_id"], d["replicate_idx"]))
            except Exception:
                continue
    return done


def run(prompts_path: Path, output_path: Path, dry_run: bool = False) -> None:
    prompts = load_prompts_jsonl(prompts_path)
    n_prompts = len(prompts)
    n_models = len(LLMS)
    n_reps = EXPERIMENT.n_replicates_per_call
    total_calls = n_prompts * n_models * n_reps

    already_done = _load_already_done(output_path)
    print(f"Total prompts:     {n_prompts}")
    print(f"Total models:      {n_models}")
    print(f"Replicates/call:   {n_reps}")
    print(f"Total API calls:   {total_calls}")
    print(f"Already collected: {len(already_done)}")
    print(f"Remaining:         {total_calls - len(already_done)}")

    if dry_run:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Append mode (resumability)
    with output_path.open("a", encoding="utf-8") as f:
        collected = len(already_done)
        for prompt in prompts:
            for model in LLMS:
                for rep in range(n_reps):
                    key = (prompt.sha256[:16], model.id, rep)
                    if key in already_done:
                        continue

                    response = call_llm(
                        model_id=model.id,
                        prompt=prompt.text,
                        language=prompt.language,
                        replicate_idx=rep,
                    )
                    f.write(response.to_jsonl_record() + "\n")
                    f.flush()
                    collected += 1

                    if collected % 100 == 0:
                        pct = 100 * collected / total_calls
                        print(f"[{collected:>6,}/{total_calls:,}] ({pct:.1f}%) "
                              f"{model.id} | {prompt.country_iso3}_{prompt.domain_id}_{prompt.task_id}",
                              file=sys.stderr)

    print(f"Done. Total records: {collected}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", type=Path,
                    default=DATA_RAW / "prompts" / "v0_synthetic.jsonl")
    ap.add_argument("--output", type=Path,
                    default=DATA_RAW / "llm_responses" / "synthetic_run.jsonl")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    run(args.prompts, args.output, dry_run=args.dry_run)
