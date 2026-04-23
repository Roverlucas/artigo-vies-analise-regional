"""
run_pilot.py — Pilot Calibration Study executor (v3.3).

Reads prompts from data/pilot_202604/prompts_skeleton.jsonl, dispatches to
specified pilot models via llm_clients.call_llm, and writes responses to
data/pilot_202604/responses/run_{timestamp}.jsonl.

**Maximum transparency for reproducibility** — writes a run manifest
(`manifest_run_{timestamp}.json`) with:
- git commit hash at run time
- python version, platform, hostname
- timestamp UTC start/end
- config snapshot (temperature, max_tokens, models used)
- prompts SHA-256 hash for linking

Resumable: checks existing responses; only dispatches missing (model, prompt, rep) tuples.

Usage:
    python -m code.benchmark.run_pilot                     # all 4 pilot models, 40 prompts, 2 reps
    python -m code.benchmark.run_pilot --models claude_haiku,gpt5_mini,gemini_flash
    python -m code.benchmark.run_pilot --dry-run           # print plan only, no calls
"""

from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .config import DATA_PILOT, EXPERIMENT, LLMS
from .llm_clients import call_llm, passes_quality_gate, LLMResponse


# Default pilot models — 4 models chosen for pilot scope
DEFAULT_PILOT_MODELS = ["claude_haiku", "gpt5_mini", "gemini_flash", "lince_mistral"]
PILOT_N_REPS = 2


# =========================================================================
# UTILITIES — reproducibility metadata
# =========================================================================


def _git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).parent.parent.parent, stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except Exception:
        return "unknown"


def _git_dirty() -> bool:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=Path(__file__).parent.parent.parent, stderr=subprocess.DEVNULL
        )
        return bool(out.decode().strip())
    except Exception:
        return True


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# =========================================================================
# PILOT RUN
# =========================================================================


def load_prompts(path: Path) -> list[dict]:
    prompts = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                prompts.append(json.loads(line))
    return prompts


def load_existing_responses(responses_dir: Path) -> set[tuple[str, str, int]]:
    """Return set of (model_id, pilot_id, replicate_idx) already collected."""
    existing = set()
    if not responses_dir.exists():
        return existing
    for jsonl_file in responses_dir.glob("run_*.jsonl"):
        with open(jsonl_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                key = (
                    rec.get("model_id"),
                    rec.get("pilot_id") or rec.get("_pilot_id"),
                    int(rec.get("replicate_idx", 0)),
                )
                if all(key):
                    existing.add(key)
    return existing


def build_work_list(
    prompts: list[dict], models: list[str], n_reps: int, existing: set[tuple[str, str, int]]
) -> list[dict]:
    work = []
    for m in models:
        for p in prompts:
            for rep in range(n_reps):
                key = (m, p["pilot_id"], rep)
                if key in existing:
                    continue
                work.append(
                    {
                        "model_id": m,
                        "pilot_id": p["pilot_id"],
                        "prompt": p["prompt_rendered"],
                        "language": p.get("language", "en"),
                        "country_iso3": p.get("country_iso3"),
                        "slot_id": p.get("slot_id"),
                        "domain": p.get("domain"),
                        "task": p.get("task"),
                        "replicate_idx": rep,
                    }
                )
    return work


def execute_pilot(
    models: list[str],
    n_reps: int = PILOT_N_REPS,
    dry_run: bool = False,
    output_dir: Path | None = None,
) -> dict:
    output_dir = output_dir or DATA_PILOT
    responses_dir = output_dir / "responses"
    responses_dir.mkdir(parents=True, exist_ok=True)

    prompts_path = output_dir / "prompts_skeleton.jsonl"
    prompts = load_prompts(prompts_path)
    print(f"Loaded {len(prompts)} prompts from {prompts_path.name}")

    existing = load_existing_responses(responses_dir)
    print(f"Found {len(existing)} already-collected (model, prompt, rep) tuples")

    work = build_work_list(prompts, models, n_reps, existing)
    print(f"Work list: {len(work)} calls needed (of {len(prompts) * len(models) * n_reps} total)")

    # Validate all models exist in config
    known_ids = {m.id for m in LLMS}
    unknown = [m for m in models if m not in known_ids]
    if unknown:
        raise ValueError(f"Unknown models: {unknown}. Known: {sorted(known_ids)}")

    # Manifest (reproducibility)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"pilot_{timestamp}"
    manifest = {
        "run_id": run_id,
        "pilot_version": "v3.3",
        "timestamp_start_utc": datetime.now(timezone.utc).isoformat(),
        "timestamp_end_utc": None,
        "git_commit": _git_commit(),
        "git_dirty": _git_dirty(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "hostname": socket.gethostname(),
        "models_requested": models,
        "n_reps": n_reps,
        "n_prompts": len(prompts),
        "n_calls_planned": len(work),
        "prompts_file_sha256": _file_sha256(prompts_path),
        "config": {
            "temperature": EXPERIMENT.temperature,
            "max_tokens_response": EXPERIMENT.max_tokens_response,
            "max_retries": EXPERIMENT.max_retries,
            "api_timeout_seconds": EXPERIMENT.api_timeout_seconds,
        },
        "dry_run": dry_run,
    }
    manifest_path = responses_dir / f"manifest_{run_id}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"Manifest: {manifest_path.name}")

    if dry_run:
        print("\n=== DRY RUN ===")
        for w in work[:5]:
            print(f"  {w['model_id']} {w['pilot_id']} rep={w['replicate_idx']}")
        if len(work) > 5:
            print(f"  ... and {len(work) - 5} more")
        return {"manifest": manifest, "executed": 0}

    # Execute and write incrementally
    output_path = responses_dir / f"run_{run_id}.jsonl"
    print(f"Output:   {output_path.name}")
    print(f"Starting {len(work)} calls...\n")

    successful = 0
    failed = 0
    total_prompt_tokens = 0
    total_response_tokens = 0
    t_start = time.time()

    with open(output_path, "a", encoding="utf-8") as f_out:
        for i, w in enumerate(work, 1):
            print(
                f"  [{i:3d}/{len(work)}] {w['model_id']:16s} {w['pilot_id']:10s} rep={w['replicate_idx']} ",
                end="", flush=True,
            )
            try:
                resp: LLMResponse = call_llm(
                    w["model_id"], w["prompt"], w["language"], w["replicate_idx"]
                )
            except Exception as e:
                print(f"EXCEPTION: {str(e)[:80]}")
                failed += 1
                continue

            # Enrich the record with pilot context for analysis traceability
            record = asdict(resp)
            record["pilot_id"] = w["pilot_id"]
            record["country_iso3"] = w["country_iso3"]
            record["slot_id"] = w["slot_id"]
            record["domain"] = w["domain"]
            record["task"] = w["task"]
            record["run_id"] = run_id

            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            f_out.flush()

            passes, reason = passes_quality_gate(resp)
            if resp.api_error:
                print(f"ERROR {resp.api_error[:60]}")
                failed += 1
            else:
                total_prompt_tokens += resp.prompt_tokens
                total_response_tokens += resp.response_tokens
                print(
                    f"{'OK' if passes else 'LOW'} "
                    f"({resp.prompt_tokens}+{resp.response_tokens}t, {resp.latency_ms}ms)"
                )
                if passes:
                    successful += 1

    elapsed_s = int(time.time() - t_start)
    manifest["timestamp_end_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["elapsed_seconds"] = elapsed_s
    manifest["calls_successful"] = successful
    manifest["calls_failed"] = failed
    manifest["total_prompt_tokens"] = total_prompt_tokens
    manifest["total_response_tokens"] = total_response_tokens
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    print()
    print("=" * 60)
    print(f"Pilot run complete: {run_id}")
    print(f"  Calls successful: {successful}")
    print(f"  Calls failed:     {failed}")
    print(f"  Elapsed:          {elapsed_s}s ({elapsed_s / max(1, successful + failed):.1f}s/call)")
    print(f"  Prompt tokens:    {total_prompt_tokens:,}")
    print(f"  Response tokens:  {total_response_tokens:,}")
    print(f"  Output:           {output_path}")
    print(f"  Manifest:         {manifest_path}")
    return {"manifest": manifest, "executed": successful + failed}


# =========================================================================
# CLI
# =========================================================================


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", default=",".join(DEFAULT_PILOT_MODELS),
                        help="Comma-separated model ids")
    parser.add_argument("--n-reps", type=int, default=PILOT_N_REPS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    execute_pilot(models=models, n_reps=args.n_reps, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
