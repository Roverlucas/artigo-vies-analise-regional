"""
run_judge_confirmatory.py — LLM-as-judge scoring on CONFIRMATORY responses.

Reads data/confirmatory_PRIVATE/responses/run_*.jsonl plus the confirmatory
prompts (prompts_confirmatory.jsonl, which carries ground_truth), scores each
response with judge_response(), and writes to
data/confirmatory_PRIVATE/analysis/judge_scores_confirmatory.jsonl.

Resumable: skips (model_id, prompt_id, replicate_idx) already judged.
Incremental writes for crash safety.

Usage:
    python -m code.analysis.run_judge_confirmatory
    python -m code.analysis.run_judge_confirmatory --judge-model claude_haiku --countries BRA
"""
from __future__ import annotations
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from code.analysis.llm_judge import judge_response, JUDGE_MODEL_ID

ROOT = Path(__file__).parent.parent.parent
PROMPTS = ROOT / "data" / "confirmatory_PRIVATE" / "prompts_confirmatory.jsonl"
RESPONSES_DIR = ROOT / "data" / "confirmatory_PRIVATE" / "responses"
ANALYSIS_DIR = ROOT / "data" / "confirmatory_PRIVATE" / "analysis"


def load_jsonl(path: Path) -> list[dict]:
    out = []
    if not path.exists():
        return out
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def load_responses(responses_dir: Path) -> list[dict]:
    out = []
    if not responses_dir.exists():
        return out
    for f in sorted(responses_dir.glob("run_*.jsonl")):
        if "_DEPRECATED" in f.name:
            continue
        out.extend(load_jsonl(f))
    return out


def load_existing(judge_output: Path) -> set[tuple[str, str, int]]:
    existing = set()
    for rec in load_jsonl(judge_output):
        existing.add((rec.get("model_id"), rec.get("prompt_id"),
                      int(rec.get("replicate_idx", 0))))
    return existing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge-model", default=JUDGE_MODEL_ID)
    parser.add_argument("--countries", default=None, help="comma-separated ISO3 filter")
    args = parser.parse_args()

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    judge_output = ANALYSIS_DIR / "judge_scores_confirmatory.jsonl"

    # Ground-truth lookup by prompt_id
    gt = {}
    for p in load_jsonl(PROMPTS):
        pid = p.get("prompt_id") or p.get("pilot_id")
        gt[pid] = p

    countries = set(args.countries.split(",")) if args.countries else None
    responses = load_responses(RESPONSES_DIR)
    existing = load_existing(judge_output)

    work = []
    for r in responses:
        if r.get("api_error"):
            continue
        if len((r.get("response_text") or "").strip()) < 10:
            continue
        pid = r.get("prompt_id") or r.get("pilot_id")
        if pid not in gt:
            continue
        if countries and gt[pid].get("country_iso3") not in countries:
            continue
        key = (r["model_id"], pid, int(r.get("replicate_idx", 0)))
        if key in existing:
            continue
        work.append((r, gt[pid]))

    print(f"Total responses:  {len(responses)}")
    print(f"Already judged:   {len(existing)}")
    print(f"To judge now:     {len(work)}")
    print(f"Judge model:      {args.judge_model}")
    print(f"Output:           {judge_output.name}")

    if not work:
        print("Nothing to do.")
        return

    t0 = time.time()
    ok = fail = 0
    consecutive_fail = 0
    ABORT_AFTER = 10  # stop if the judge API is systematically failing (credit/rate)
    with open(judge_output, "a", encoding="utf-8") as out:
        for i, (r, p) in enumerate(work, 1):
            pid = r.get("prompt_id") or r.get("pilot_id")
            try:
                scores = judge_response(
                    prompt_text=p.get("prompt_rendered", ""),
                    ground_truth=p.get("ground_truth", ""),
                    response_text=r.get("response_text", ""),
                    task_id=r.get("task") or p.get("task", "T1"),
                    judge_model_id=args.judge_model,
                )
                # judge_response returns fallback zeros + JUDGE_API_ERROR on api failure;
                # treat that as a real failure, do NOT persist garbage scores.
                rationale = str(scores.get("rationale", ""))
                if scores.get("error") or "JUDGE_API_ERROR" in rationale:
                    fail += 1
                    consecutive_fail += 1
                    if consecutive_fail <= 3 or consecutive_fail % 50 == 0:
                        print(f"  [{i}/{len(work)}] {r['model_id']} {pid} JUDGE_ERROR: {rationale[:100]}")
                    if consecutive_fail >= ABORT_AFTER:
                        print(f"ABORTING: {consecutive_fail} consecutive judge API errors "
                              f"(likely credit/rate). Fix the judge and re-run (resumable).")
                        break
                    continue
                consecutive_fail = 0
                rec = {
                    "model_id": r["model_id"],
                    "prompt_id": pid,
                    "replicate_idx": int(r.get("replicate_idx", 0)),
                    "country_iso3": p.get("country_iso3"),
                    "task": r.get("task") or p.get("task"),
                    "persona": p.get("persona", "neutral"),
                    **scores,
                }
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.flush()
                ok += 1
            except Exception as e:
                fail += 1
                consecutive_fail += 1
                print(f"  [{i}/{len(work)}] {r['model_id']} {pid} FAILED: {str(e)[:120]}")
                if consecutive_fail >= ABORT_AFTER:
                    print(f"ABORTING: {consecutive_fail} consecutive failures.")
                    break
            if i % 25 == 0:
                dt = time.time() - t0
                print(f"  [{i}/{len(work)}] ok={ok} fail={fail} ({dt:.0f}s, {dt/max(i,1):.1f}s/judg)")

    print(f"DONE. ok={ok} fail={fail} in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
