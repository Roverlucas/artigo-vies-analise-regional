"""
run_judge.py — Execute LLM-as-judge scoring on all pilot responses.

Reads data/pilot_202604/responses/run_*.jsonl plus prompts_skeleton.jsonl,
calls judge_response() for each response, writes judge scores to
data/pilot_202604/analysis/judge_scores.jsonl (one record per response).

Resumable: skips (model_id, pilot_id, replicate_idx) triples already judged.
Incremental writes after each call for crash safety.

Usage:
    python -m code.analysis.run_judge
    python -m code.analysis.run_judge --judge-model claude_haiku
"""

from __future__ import annotations
import argparse
import json
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from code.benchmark.config import DATA_PILOT
from code.analysis.llm_judge import judge_response, JUDGE_MODEL_ID


def load_prompts(path: Path) -> dict:
    prompts = {}
    with open(path) as f:
        for line in f:
            if line.strip():
                p = json.loads(line)
                prompts[p["pilot_id"]] = p
    return prompts


def load_responses(responses_dir: Path) -> list[dict]:
    rows = []
    for f in sorted(responses_dir.glob("run_*.jsonl")):
        if "_DEPRECATED" in f.name:
            continue
        with open(f) as fh:
            for line in fh:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def load_existing_judgments(path: Path) -> set[tuple[str, str, int]]:
    existing = set()
    if not path.exists():
        return existing
    with open(path) as f:
        for line in f:
            if line.strip():
                try:
                    r = json.loads(line)
                    key = (r.get("model_id"), r.get("pilot_id"), int(r.get("replicate_idx", 0)))
                    if all(key):
                        existing.add(key)
                except Exception:
                    continue
    return existing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge-model", default=JUDGE_MODEL_ID)
    args = parser.parse_args()

    prompts_path = DATA_PILOT / "prompts_skeleton.jsonl"
    responses_dir = DATA_PILOT / "responses"
    analysis_dir = DATA_PILOT / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    judge_output = analysis_dir / "judge_scores.jsonl"
    manifest_path = analysis_dir / f"judge_manifest_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"

    prompts = load_prompts(prompts_path)
    responses = load_responses(responses_dir)
    existing = load_existing_judgments(judge_output)

    work = []
    for r in responses:
        if r.get("api_error"):
            continue
        if len(r.get("response_text", "")) < 10:
            continue
        key = (r["model_id"], r["pilot_id"], int(r.get("replicate_idx", 0)))
        if key in existing:
            continue
        work.append(r)

    print(f"Total responses: {len(responses)}")
    print(f"Already judged:  {len(existing)}")
    print(f"To judge now:    {len(work)}")
    print(f"Judge model:     {args.judge_model}")
    print(f"Output:          {judge_output.name}")
    print()

    if not work:
        print("Nothing to do. All responses already judged.")
        return

    manifest = {
        "judge_model": args.judge_model,
        "timestamp_start_utc": datetime.now(timezone.utc).isoformat(),
        "timestamp_end_utc": None,
        "n_responses_total": len(responses),
        "n_judgments_planned": len(work),
        "n_judgments_successful": 0,
        "n_judgments_failed": 0,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    t_start = time.time()
    successful = failed = 0

    with open(judge_output, "a", encoding="utf-8") as out:
        for i, r in enumerate(work, 1):
            pid = r["pilot_id"]
            prompt_rec = prompts.get(pid)
            if not prompt_rec:
                print(f"  [{i:4d}/{len(work)}] {r['model_id']:14s} {pid:10s} — SKIP (prompt not found)")
                failed += 1
                continue
            print(
                f"  [{i:4d}/{len(work)}] {r['model_id']:14s} {pid:10s} rep={r.get('replicate_idx', 0)} ",
                end="", flush=True,
            )
            try:
                scores = judge_response(
                    prompt_text=prompt_rec["prompt_rendered"],
                    ground_truth=prompt_rec["ground_truth"],
                    response_text=r["response_text"],
                    task_id=r["task"],
                    judge_model_id=args.judge_model,
                )
            except Exception as e:
                print(f"EXCEPTION: {str(e)[:80]}")
                failed += 1
                continue

            out_record = {
                "model_id":            r["model_id"],
                "pilot_id":            pid,
                "replicate_idx":       int(r.get("replicate_idx", 0)),
                "country_iso3":        r["country_iso3"],
                "slot_id":             r["slot_id"],
                "domain":              r["domain"],
                "task":                r["task"],
                "venue":               r.get("venue", ""),
                **scores,
            }
            out.write(json.dumps(out_record, ensure_ascii=False) + "\n")
            out.flush()

            if scores.get("error"):
                print(f"JUDGE_ERR composite={scores['composite']:.2f}")
                failed += 1
            else:
                print(f"OK composite={scores['composite']:.2f} ({scores['judge_latency_ms']}ms)")
                successful += 1

    elapsed = int(time.time() - t_start)
    manifest["timestamp_end_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["elapsed_seconds"] = elapsed
    manifest["n_judgments_successful"] = successful
    manifest["n_judgments_failed"] = failed
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    print()
    print("=" * 60)
    print(f"Judge run complete")
    print(f"  Successful: {successful}")
    print(f"  Failed:     {failed}")
    print(f"  Elapsed:    {elapsed}s ({elapsed / max(1, successful + failed):.1f}s/call)")
    print(f"  Output:     {judge_output}")


if __name__ == "__main__":
    main()
