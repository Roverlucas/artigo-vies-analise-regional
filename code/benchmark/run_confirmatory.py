"""
run_confirmatory.py — Confirmatory data collection executor.

Reads prompts from data/confirmatory_PRIVATE/prompts_confirmatory.jsonl
(gitignored, locally only), dispatches to all 14 confirmatory models per
the pre-registration v6, writes responses to data/confirmatory_PRIVATE/responses/.

Per pre-registration §3.6 #4: the prompts file is private until confirmatory
data collection completes. Public release accompanies Zenodo deposit.

Resumable: checks existing responses; only dispatches missing
(model, prompt, rep) tuples.

Maximum reproducibility metadata:
- Run manifest with git commit, Python version, platform, hostname
- SHA-256 of prompts file
- Model version + finish reason + latency per call
- Provenance per response stored as JSONL

Usage:
    python -m code.benchmark.run_confirmatory                          # all 14 models
    python -m code.benchmark.run_confirmatory --models claude_haiku    # subset
    python -m code.benchmark.run_confirmatory --countries BRA,USA      # subset countries
    python -m code.benchmark.run_confirmatory --dry-run                # plan only
"""

from __future__ import annotations
import argparse
import hashlib
import json
import platform
import socket
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .config import EXPERIMENT, LLMS
from .llm_clients import call_llm, passes_quality_gate, LLMResponse


ROOT = Path(__file__).parent.parent.parent
PROMPTS_PRIVATE = ROOT / "data" / "confirmatory_PRIVATE" / "prompts_confirmatory.jsonl"
RESPONSES_DIR = ROOT / "data" / "confirmatory_PRIVATE" / "responses"

# Confirmatory: 14 models with full_scope=True (excludes reserve)
DEFAULT_MODELS = tuple(m.id for m in LLMS if m.full_scope and m.tier != "reserve")
DEFAULT_REPS = EXPERIMENT.n_replicates_per_call


def _git_commit() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return "unknown"


def _git_dirty() -> bool:
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, stderr=subprocess.DEVNULL)
        return bool(out.decode().strip())
    except Exception:
        return True


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_prompts(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Confirmatory prompts file not found at {path}. "
            "Per pre-registration §3.6 #4, this file is gitignored and must be "
            "authored locally before confirmatory collection."
        )
    prompts = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                prompts.append(json.loads(line))
    return prompts


def load_existing_responses(responses_dir: Path) -> set[tuple[str, str, int]]:
    existing = set()
    if not responses_dir.exists():
        return existing
    for f in responses_dir.glob("run_*.jsonl"):
        if "_DEPRECATED" in f.name:
            continue
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                key = (
                    rec.get("model_id"),
                    rec.get("prompt_id") or rec.get("pilot_id"),
                    int(rec.get("replicate_idx", 0)),
                )
                if all(key):
                    existing.add(key)
    return existing


def build_work_list(
    prompts: list[dict], models: list[str], n_reps: int, existing: set
) -> list[dict]:
    work = []
    for m in models:
        for p in prompts:
            for rep in range(n_reps):
                pid = p.get("prompt_id") or p.get("pilot_id")
                key = (m, pid, rep)
                if key in existing:
                    continue
                work.append({
                    "model_id": m,
                    "prompt_id": pid,
                    "prompt": p["prompt_rendered"],
                    "language": p.get("language", "en"),
                    "country_iso3": p.get("country_iso3"),
                    "domain": p.get("domain"),
                    "task": p.get("task"),
                    "replicate_idx": rep,
                })
    return work


def execute_confirmatory(
    models: list[str] | None = None,
    countries: list[str] | None = None,
    n_reps: int = DEFAULT_REPS,
    dry_run: bool = False,
):
    models = models or list(DEFAULT_MODELS)
    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

    prompts = load_prompts(PROMPTS_PRIVATE)
    if countries:
        prompts = [p for p in prompts if p.get("country_iso3") in countries]

    print(f"Loaded {len(prompts)} prompts from {PROMPTS_PRIVATE.name}")
    print(f"Filter: countries={countries or 'ALL'}; models={models}")

    existing = load_existing_responses(RESPONSES_DIR)
    print(f"Already collected: {len(existing)}")

    work = build_work_list(prompts, models, n_reps, existing)
    target = len(prompts) * len(models) * n_reps
    print(f"Work list: {len(work)} of {target} target")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"confirmatory_{timestamp}"
    manifest = {
        "run_id": run_id,
        "study_phase": "confirmatory",
        "preregistration_version": "v6 (cd17f76+)",
        "timestamp_start_utc": datetime.now(timezone.utc).isoformat(),
        "timestamp_end_utc": None,
        "git_commit": _git_commit(),
        "git_dirty": _git_dirty(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "hostname": socket.gethostname(),
        "models_requested": models,
        "countries_filter": countries or "all",
        "n_reps": n_reps,
        "n_prompts": len(prompts),
        "n_calls_planned": len(work),
        "prompts_file_sha256": _file_sha256(PROMPTS_PRIVATE),
        "config": {
            "temperature": EXPERIMENT.temperature,
            "max_tokens_response": EXPERIMENT.max_tokens_response,
            "max_retries": EXPERIMENT.max_retries,
        },
        "dry_run": dry_run,
    }
    manifest_path = RESPONSES_DIR / f"manifest_{run_id}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"Manifest: {manifest_path.name}")

    if dry_run:
        print("\n=== DRY RUN ===")
        for w in work[:5]:
            print(f"  {w['model_id']} {w['prompt_id']} rep={w['replicate_idx']}")
        if len(work) > 5:
            print(f"  ... and {len(work)-5} more")
        return

    output_path = RESPONSES_DIR / f"run_{run_id}.jsonl"
    print(f"Output: {output_path.name}\n")
    successful = 0
    failed = 0
    t0 = time.time()
    with open(output_path, "a", encoding="utf-8") as f_out:
        for i, w in enumerate(work, 1):
            print(
                f"  [{i:5d}/{len(work)}] {w['model_id']:16s} {w['prompt_id']:12s} rep={w['replicate_idx']} ",
                end="", flush=True,
            )
            try:
                resp = call_llm(w["model_id"], w["prompt"], w["language"], w["replicate_idx"])
            except Exception as e:
                print(f"EXCEPTION: {str(e)[:80]}")
                failed += 1
                continue
            record = asdict(resp)
            record["prompt_id"] = w["prompt_id"]
            record["country_iso3"] = w["country_iso3"]
            record["domain"] = w["domain"]
            record["task"] = w["task"]
            record["run_id"] = run_id
            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            f_out.flush()
            passes, _ = passes_quality_gate(resp)
            if resp.api_error:
                print(f"ERROR {resp.api_error[:60]}")
                failed += 1
            else:
                print(f"{'OK' if passes else 'LOW'} ({resp.prompt_tokens}+{resp.response_tokens}t, {resp.latency_ms}ms)")
                if passes:
                    successful += 1

    elapsed = int(time.time() - t0)
    manifest["timestamp_end_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["elapsed_seconds"] = elapsed
    manifest["calls_successful"] = successful
    manifest["calls_failed"] = failed
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    print()
    print("=" * 60)
    print(f"Confirmatory run complete: {run_id}")
    print(f"  Successful: {successful}")
    print(f"  Failed:     {failed}")
    print(f"  Elapsed:    {elapsed}s")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--models", default=None,
                   help="Comma-separated model ids (default: all 14)")
    p.add_argument("--countries", default=None,
                   help="Comma-separated ISO3 codes")
    p.add_argument("--n-reps", type=int, default=DEFAULT_REPS)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    models = [m.strip() for m in args.models.split(",")] if args.models else None
    countries = [c.strip() for c in args.countries.split(",")] if args.countries else None
    execute_confirmatory(models=models, countries=countries, n_reps=args.n_reps, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
