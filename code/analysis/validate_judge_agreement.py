"""
validate_judge_agreement.py — Inter-judge reliability for the confirmatory study.

The primary judge (gpt5_mini) is inside the 14-model evaluated set (judge-target
overlap). To neutralize that caveat empirically, we re-score a STRATIFIED SAMPLE
of responses with an OUT-OF-SAMPLE judge (claude_sonnet, not among the 14) and
report agreement between the two judges.

Steps:
  1. Load primary judge scores (judge_scores_confirmatory.jsonl, gpt5_mini).
  2. Draw a stratified sample (by country x task x persona) of ~N responses.
  3. Re-judge each with the alternate judge; write judge_scores_<judge>_sample.jsonl
     (resumable: skip already-scored). Aborts after 10 consecutive API errors.
  4. Compute agreement on the composite over paired (model, prompt, rep):
     Pearson r, Spearman rho, ICC(2,1), MAE, and % within +-0.1.
  5. Write agreement_report.md.

Usage:
    python -m code.analysis.validate_judge_agreement --sample-size 800 --judge-model claude_sonnet
"""
from __future__ import annotations
import argparse
import json
import random
import time
from collections import defaultdict
from pathlib import Path

from code.analysis.llm_judge import judge_response

ROOT = Path(__file__).parent.parent.parent
PROMPTS = ROOT / "data" / "confirmatory_PRIVATE" / "prompts_confirmatory.jsonl"
RESPONSES_DIR = ROOT / "data" / "confirmatory_PRIVATE" / "responses"
ANALYSIS = ROOT / "data" / "confirmatory_PRIVATE" / "analysis"
PRIMARY = ANALYSIS / "judge_scores_confirmatory.jsonl"


def load_jsonl(p: Path) -> list[dict]:
    out = []
    if not p.exists():
        return out
    for l in open(p, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            out.append(json.loads(l))
        except Exception:
            continue
    return out


def load_responses() -> dict:
    by_key = {}
    if not RESPONSES_DIR.exists():
        return by_key
    for f in sorted(RESPONSES_DIR.glob("run_*.jsonl")):
        if "_DEPRECATED" in f.name:
            continue
        for r in load_jsonl(f):
            txt = (r.get("response_text") or "").strip()
            if not txt:
                continue
            key = (r.get("model_id"), r.get("prompt_id") or r.get("pilot_id"), int(r.get("replicate_idx", 0)))
            by_key[key] = r
    return by_key


def icc_2_1(pairs: list[tuple[float, float]]) -> float:
    """ICC(2,1) two-way random, single measure, absolute agreement. k=2 raters."""
    n = len(pairs)
    if n < 2:
        return float("nan")
    k = 2
    grand = sum(a + b for a, b in pairs) / (n * k)
    row_means = [(a + b) / 2 for a, b in pairs]
    col_means = [sum(a for a, _ in pairs) / n, sum(b for _, b in pairs) / n]
    ss_rows = k * sum((rm - grand) ** 2 for rm in row_means)
    ss_cols = n * sum((cm - grand) ** 2 for cm in col_means)
    ss_total = sum((a - grand) ** 2 + (b - grand) ** 2 for a, b in pairs)
    ss_err = ss_total - ss_rows - ss_cols
    msr = ss_rows / (n - 1)
    msc = ss_cols / (k - 1)
    mse = ss_err / ((n - 1) * (k - 1))
    denom = msr + (k - 1) * mse + (k / n) * (msc - mse)
    if denom == 0:
        return float("nan")
    return (msr - mse) / denom


def _rank(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _corr(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    return num / (dx * dy) if dx and dy else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-size", type=int, default=800)
    ap.add_argument("--judge-model", default="claude_sonnet")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    out_path = ANALYSIS / f"judge_scores_{args.judge_model}_sample.jsonl"
    primary = {(r["model_id"], r["prompt_id"], int(r.get("replicate_idx", 0))): r
               for r in load_jsonl(PRIMARY)
               if "composite" in r and not r.get("error")
               and "JUDGE_API_ERROR" not in str(r.get("rationale", ""))}
    if not primary:
        print("No primary (gpt5_mini) scores yet. Run run_judge_confirmatory first.")
        return
    gt = {p.get("prompt_id"): p for p in load_jsonl(PROMPTS)}
    responses = load_responses()

    # Stratified sample by (country, task, persona)
    strata = defaultdict(list)
    for key, r in primary.items():
        strata[(r.get("country_iso3"), r.get("task"), r.get("persona", "neutral"))].append(key)
    rnd = random.Random(args.seed)
    n_strata = len(strata)
    per = max(1, args.sample_size // max(1, n_strata))
    sample = []
    for s, keys in strata.items():
        rnd.shuffle(keys)
        sample.extend(keys[:per])
    rnd.shuffle(sample)
    sample = sample[:args.sample_size]

    already = {(r["model_id"], r["prompt_id"], int(r.get("replicate_idx", 0))) for r in load_jsonl(out_path)}
    todo = [k for k in sample if k not in already]
    print(f"Strata: {n_strata} | sample: {len(sample)} | already judged: {len(already)} | to judge: {len(todo)}")
    print(f"Alternate judge: {args.judge_model} | output: {out_path.name}")

    consecutive_fail = 0
    with open(out_path, "a", encoding="utf-8") as out:
        for i, key in enumerate(todo, 1):
            mid, pid, rep = key
            resp = responses.get(key)
            p = gt.get(pid)
            if not resp or not p:
                continue
            try:
                scores = judge_response(
                    prompt_text=p.get("prompt_rendered", ""),
                    ground_truth=p.get("ground_truth", ""),
                    response_text=resp.get("response_text", ""),
                    task_id=resp.get("task") or p.get("task", "T1"),
                    judge_model_id=args.judge_model,
                )
                if scores.get("error") or "JUDGE_API_ERROR" in str(scores.get("rationale", "")):
                    consecutive_fail += 1
                    if consecutive_fail >= 10:
                        print("ABORTING: 10 consecutive judge API errors (credit/rate). Resumable.")
                        break
                    continue
                consecutive_fail = 0
                rec = {"model_id": mid, "prompt_id": pid, "replicate_idx": rep,
                       "country_iso3": p.get("country_iso3"), "task": resp.get("task") or p.get("task"),
                       "persona": p.get("persona", "neutral"), **scores}
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.flush()
            except Exception as e:
                consecutive_fail += 1
                print(f"  [{i}/{len(todo)}] {mid} {pid} FAILED: {str(e)[:100]}")
                if consecutive_fail >= 10:
                    break
            if i % 50 == 0:
                print(f"  [{i}/{len(todo)}] scored")

    # Agreement on paired composites
    alt = {(r["model_id"], r["prompt_id"], int(r.get("replicate_idx", 0))): r
           for r in load_jsonl(out_path) if "composite" in r and not r.get("error")}
    pairs = [(primary[k]["composite"], alt[k]["composite"]) for k in alt if k in primary]
    n = len(pairs)
    L = [f"# Inter-Judge Agreement\n",
         f"Primary judge: gpt5_mini (in-sample) · Alternate: {args.judge_model} (out-of-sample)\n",
         f"Paired responses: {n}\n"]
    if n >= 2:
        xs = [a for a, _ in pairs]; ys = [b for _, b in pairs]
        pearson = _corr(xs, ys)
        spearman = _corr(_rank(xs), _rank(ys))
        icc = icc_2_1(pairs)
        mae = sum(abs(a - b) for a, b in pairs) / n
        within = sum(1 for a, b in pairs if abs(a - b) <= 0.1) / n
        L += [f"- Pearson r: **{pearson:.3f}**",
              f"- Spearman rho: **{spearman:.3f}**",
              f"- ICC(2,1) absolute agreement: **{icc:.3f}**",
              f"- Mean absolute difference: **{mae:.3f}**",
              f"- Within +-0.1: **{within*100:.1f}%**",
              "",
              "Interpretation: ICC/rho >= 0.70 indicates the out-of-sample judge",
              "substantively agrees with the primary judge, neutralizing the",
              "judge-target overlap caveat for the reported composites."]
        print("\n".join(L[2:]))
    else:
        L.append("Not enough paired scores yet.")
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    (ANALYSIS / "agreement_report.md").write_text("\n".join(L))
    print(f"\nWrote {ANALYSIS / 'agreement_report.md'}")


if __name__ == "__main__":
    main()
