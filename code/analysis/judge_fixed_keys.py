"""
judge_fixed_keys.py — Score a FIXED key set with a panel judge.

Fixes the panel-sample misalignment: claude_sonnet and gemini_2_5_pro were judged
on a 15-country sample, deepseek_v3/command_rp on a 25-country sample, so their
intersection collapsed. We define the fixed reliability sample as the items BOTH
claude_sonnet AND gemini_2_5_pro already scored, and complete the remaining panel
judges (deepseek_v3, command_rp) on exactly those keys. gpt5_mini (full) already
covers them. Result: all 5 judges on the same items.

Usage:  python -m code.analysis.judge_fixed_keys --judge-model deepseek_v3
"""
from __future__ import annotations
import argparse, json
from code.analysis.validate_judge_agreement import (
    load_jsonl, load_responses, judge_response, ANALYSIS, PROMPTS)

KEY = ("model_id", "prompt_id", "replicate_idx")


def keyset(name):
    fp = ANALYSIS / f"judge_scores_{name}_sample.jsonl"
    s = set()
    for r in load_jsonl(fp):
        if r.get("composite") is not None and not r.get("error"):
            s.add((r["model_id"], r["prompt_id"], int(r.get("replicate_idx", 0))))
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge-model", required=True)
    ap.add_argument("--anchor", nargs=2, default=["claude_sonnet", "gemini_2_5_pro"],
                    help="two judges whose common items define the fixed sample")
    args = ap.parse_args()

    fixed = keyset(args.anchor[0]) & keyset(args.anchor[1])
    print(f"Fixed reliability sample = {args.anchor[0]} ∩ {args.anchor[1]} = {len(fixed)} items")

    out_path = ANALYSIS / f"judge_scores_{args.judge_model}_sample.jsonl"
    already = keyset(args.judge_model)
    todo = sorted(fixed - already)
    print(f"  {args.judge_model}: already {len(already & fixed)}/{len(fixed)} | to judge: {len(todo)}")

    gt = {p.get("prompt_id"): p for p in load_jsonl(PROMPTS)}
    responses = load_responses()

    consec = 0
    done = 0
    with open(out_path, "a", encoding="utf-8") as out:
        for i, key in enumerate(todo, 1):
            mid, pid, rep = key
            resp = responses.get(key); p = gt.get(pid)
            if not resp or not p:
                continue
            try:
                scores = judge_response(
                    prompt_text=p.get("prompt_rendered", ""),
                    ground_truth=p.get("ground_truth", ""),
                    response_text=resp.get("response_text", ""),
                    task_id=resp.get("task") or p.get("task", "T1"),
                    judge_model_id=args.judge_model)
                if scores.get("error") or "JUDGE_API_ERROR" in str(scores.get("rationale", "")):
                    consec += 1
                    if consec >= 10:
                        print("ABORT: 10 consecutive judge errors. Resumable."); break
                    continue
                consec = 0
                rec = {"model_id": mid, "prompt_id": pid, "replicate_idx": rep,
                       "country_iso3": p.get("country_iso3"),
                       "task": resp.get("task") or p.get("task"),
                       "persona": p.get("persona", "neutral"), **scores}
                out.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.flush()
                done += 1
            except Exception as e:
                consec += 1
                print(f"  [{i}/{len(todo)}] {mid} {pid} FAIL: {str(e)[:80]}")
                if consec >= 10:
                    print("ABORT: 10 consecutive errors."); break
            if i % 25 == 0:
                print(f"  [{i}/{len(todo)}] scored ({done} ok)")
    print(f"DONE {args.judge_model}: +{done} scores on fixed sample")


if __name__ == "__main__":
    main()
