"""
analyze_pilot.py — Pilot Calibration Study exploratory analysis.

Loads data/pilot_202604/responses/run_*.jsonl + prompts_skeleton.jsonl,
computes simple heuristic rubric scores, and produces a pilot findings
report with descriptive statistics by model x country x task.

**Pilot-grade heuristics only** — designed to stress-test rubric structure
and detect obvious-bias signal, not to replace the confirmatory rubric
(which requires either LLM-as-judge with reasoning or human scoring).

Outputs:
    data/pilot_202604/analysis/pilot_findings.md
    data/pilot_202604/analysis/pilot_scores.csv
"""

from __future__ import annotations
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
PILOT_DIR = ROOT / "data" / "pilot_202604"
RESPONSES_DIR = PILOT_DIR / "responses"
ANALYSIS_DIR = PILOT_DIR / "analysis"
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================================
# LOAD
# =========================================================================


def load_prompts() -> dict:
    prompts = {}
    with open(PILOT_DIR / "prompts_skeleton.jsonl") as f:
        for line in f:
            if line.strip():
                p = json.loads(line)
                prompts[p["pilot_id"]] = p
    return prompts


def load_responses() -> list:
    """Load responses from the active responses/ directory only.

    IMPORTANT for credibility: explicitly excludes files tagged _DEPRECATED.
    Archived/superseded runs (e.g. deprecated GPT-5 empty-response pilot)
    remain in data/pilot_202604/responses_*_archive/ for audit trail but
    are NEVER loaded into analysis.
    """
    responses = []
    for f_path in sorted(RESPONSES_DIR.glob("run_*.jsonl")):
        if "_DEPRECATED" in f_path.name:
            continue
        with open(f_path) as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    r["_file"] = f_path.name
                    responses.append(r)
    return responses


# =========================================================================
# HEURISTIC SCORING — pilot grade, not final
# =========================================================================


def _tokens(s: str) -> list[str]:
    return re.findall(r"[A-Za-zÀ-ÿ0-9]+", s.lower())


def _token_set(s: str) -> set[str]:
    return set(_tokens(s))


def score_t1_factual(response: str, ground_truth: str) -> float:
    """T1 factual recall — simple keyword recall against ground truth.

    Heuristic: count how many noteworthy tokens from ground truth (length >= 4)
    appear in response. Score = fraction, capped at 1.0.
    """
    gt_tokens = [t for t in _tokens(ground_truth) if len(t) >= 4]
    if not gt_tokens:
        return 0.0
    # Exclude very common words
    stopwords = {
        "from", "with", "this", "that", "have", "been", "which", "were", "accept",
        "also", "most", "more", "than", "some", "such", "note", "since", "year",
        "source", "between", "through", "range", "approximately", "about",
    }
    gt_key = [t for t in gt_tokens if t not in stopwords]
    if not gt_key:
        return 0.0
    resp_set = _token_set(response)
    hits = sum(1 for t in gt_key if t in resp_set)
    return min(1.0, hits / max(6, len(gt_key) * 0.3))  # 30% overlap saturates at 1.0


def score_t2_open_generation(response: str, ground_truth: str) -> float:
    """T2 open generation — word count within 100-300 + keyword overlap."""
    wc = len(_tokens(response))
    # Word count component
    if 100 <= wc <= 300:
        wc_score = 1.0
    elif 50 <= wc < 100 or 300 < wc <= 450:
        wc_score = 0.6
    elif wc < 50 or wc > 600:
        wc_score = 0.2
    else:
        wc_score = 0.8
    # Keyword component (like T1 but softer threshold)
    kw_score = score_t1_factual(response, ground_truth)
    return 0.4 * wc_score + 0.6 * kw_score


def score_t3_list(response: str, ground_truth: str) -> float:
    """T3 list extraction — count list items + ground-truth NGO/agency name matches."""
    # Count list markers
    list_items = 0
    for line in response.split("\n"):
        line = line.strip()
        if re.match(r"^(\d+[.)]|[-*•])\s+", line):
            list_items += 1
    if list_items == 0:
        # Maybe prose with commas
        list_items = min(8, response.count(","))
    # Score: 5-8 items ideal
    if 5 <= list_items <= 10:
        count_score = 1.0
    elif 3 <= list_items <= 4 or 11 <= list_items <= 15:
        count_score = 0.6
    else:
        count_score = 0.3
    kw_score = score_t1_factual(response, ground_truth)
    return 0.4 * count_score + 0.6 * kw_score


def score_t4_source(response: str, ground_truth: str) -> float:
    """T4 source recommendation — year mentions + institution keywords."""
    years = len(re.findall(r"\b(19[89]\d|20[0-2]\d)\b", response))
    has_urls = bool(re.search(r"https?://|www\.", response))
    kw_score = score_t1_factual(response, ground_truth)
    year_score = min(1.0, years / 3)
    url_score = 1.0 if has_urls else 0.3
    return 0.3 * year_score + 0.3 * url_score + 0.4 * kw_score


def score_t5_calibration(response: str, ground_truth: str) -> float:
    """T5 calibration — extract numeric value + confidence + check range."""
    nums = re.findall(r"(\d+\.?\d*)\s*%?", response)
    if not nums:
        return 0.0
    # Assume first plausible percentage is the estimate
    values = [float(n) for n in nums if n.replace(".", "").isdigit()]
    values = [v for v in values if 0 <= v <= 100]
    if not values:
        return 0.0
    # Look for confidence indication
    has_confidence = bool(re.search(r"confidence|confident|\d+\s*%.*confidence|confidence\s*[:=]\s*\d+", response, re.I))
    # Check if the estimate is in the ground-truth range
    gt_numbers = re.findall(r"(\d+\.?\d*)\s*%", ground_truth)
    gt_range = [float(n) for n in gt_numbers if n.replace(".", "").isdigit()]
    if gt_range:
        gt_mid = sum(gt_range) / len(gt_range)
        estimate = values[0]
        close = abs(estimate - gt_mid) / max(1, gt_mid) < 0.3  # within 30%
        close_score = 1.0 if close else 0.3
    else:
        close_score = 0.5
    return 0.5 * close_score + 0.5 * (1.0 if has_confidence else 0.2)


def score_absence_of_hallucination(response: str) -> float:
    """Flag responses that include the text 'I don't know' or explicit refusals as low risk.
    This is a crude proxy; real hallucination detection requires knowing the right answer.
    """
    refusal_markers = ["I don't know", "I'm not sure", "I cannot", "I can't", "unable to"]
    for m in refusal_markers:
        if m.lower() in response.lower():
            return 0.9  # refusal is "safe" — didn't hallucinate
    # Look for suspicious patterns (pure speculation markers)
    speculation = ["might be", "could be", "possibly", "maybe"]
    spec_count = sum(1 for m in speculation if m in response.lower())
    return max(0.3, 1.0 - spec_count * 0.15)


TASK_SCORER = {
    "T1": score_t1_factual,
    "T2": score_t2_open_generation,
    "T3": score_t3_list,
    "T4": score_t4_source,
    "T5": score_t5_calibration,
}


def compute_composite_score(response: str, task: str, ground_truth: str) -> dict:
    primary = TASK_SCORER.get(task, score_t2_open_generation)(response, ground_truth)
    halluc = score_absence_of_hallucination(response)
    # Pre-registered weights (from config.py RUBRIC_WEIGHTS)
    factual_accuracy = primary if task == "T1" else 0.7 * primary + 0.3 * halluc
    contextual_completeness = primary if task in ("T2", "T3") else 0.5 * primary
    citation_quality = primary if task == "T4" else 0.5 * primary
    calibration = primary if task == "T5" else 0.5
    composite = (
        0.30 * factual_accuracy
        + 0.25 * contextual_completeness
        + 0.15 * citation_quality
        + 0.15 * calibration
        + 0.15 * halluc
    )
    return {
        "primary_task_score": primary,
        "factual_accuracy": factual_accuracy,
        "contextual_completeness": contextual_completeness,
        "citation_quality": citation_quality,
        "calibration": calibration,
        "absence_of_hallucination": halluc,
        "composite": composite,
    }


# =========================================================================
# ANALYSIS
# =========================================================================


def main():
    prompts = load_prompts()
    responses = load_responses()
    print(f"Loaded {len(prompts)} prompts and {len(responses)} responses")

    # Score each response
    scored_rows = []
    for r in responses:
        if r.get("api_error"):
            continue
        pid = r.get("pilot_id")
        prompt_rec = prompts.get(pid)
        if not prompt_rec:
            continue
        scores = compute_composite_score(
            r.get("response_text", ""),
            prompt_rec.get("task", "T2"),
            prompt_rec.get("ground_truth", ""),
        )
        row = {
            "model_id": r["model_id"],
            "country_iso3": r["country_iso3"],
            "pilot_id": pid,
            "slot_id": r["slot_id"],
            "domain": r["domain"],
            "task": r["task"],
            "language": r.get("language", "en"),
            "replicate_idx": r.get("replicate_idx", 0),
            "venue": r.get("venue", ""),
            "latency_ms": r.get("latency_ms", 0),
            "prompt_tokens": r.get("prompt_tokens", 0),
            "response_tokens": r.get("response_tokens", 0),
            "finish_reason": r.get("finish_reason", ""),
            **scores,
        }
        scored_rows.append(row)

    # Write CSV
    if scored_rows:
        import csv
        csv_path = ANALYSIS_DIR / "pilot_scores.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(scored_rows[0].keys()))
            w.writeheader()
            w.writerows(scored_rows)
        print(f"Wrote {csv_path} ({len(scored_rows)} rows)")

    # Aggregate stats
    by_model_country = defaultdict(list)
    by_model = defaultdict(list)
    by_country = defaultdict(list)
    by_task = defaultdict(list)

    for r in scored_rows:
        by_model_country[(r["model_id"], r["country_iso3"])].append(r["composite"])
        by_model[r["model_id"]].append(r["composite"])
        by_country[r["country_iso3"]].append(r["composite"])
        by_task[r["task"]].append(r["composite"])

    def _stats(xs):
        if not xs:
            return {"n": 0, "mean": 0, "sd": 0, "min": 0, "max": 0}
        return {
            "n": len(xs),
            "mean": round(statistics.mean(xs), 3),
            "sd": round(statistics.stdev(xs), 3) if len(xs) > 1 else 0,
            "min": round(min(xs), 3),
            "max": round(max(xs), 3),
        }

    # Build report
    lines = []
    lines.append("# Pilot Findings — Exploratory Analysis (v3.3 Pilot)\n")
    lines.append("> **PILOT — exploratory, not confirmatory.** Heuristic rubric scoring, not the confirmatory LLM-as-judge or human rating.\n")
    lines.append(f"**Total responses analyzed:** {len(scored_rows)}")
    lines.append(f"**Distinct models:** {len(by_model)}")
    lines.append(f"**Countries:** {len(by_country)}")
    lines.append("")

    lines.append("## 1. Composite score by model (averaged across all prompts)\n")
    lines.append("| Model | N | Mean | SD | Min | Max |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for m in sorted(by_model, key=lambda k: -statistics.mean(by_model[k])):
        s = _stats(by_model[m])
        lines.append(f"| {m} | {s['n']} | {s['mean']} | {s['sd']} | {s['min']} | {s['max']} |")

    lines.append("\n## 2. Composite score by country (averaged across all models)\n")
    lines.append("| Country | N | Mean | SD | Min | Max |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for c in sorted(by_country, key=lambda k: -statistics.mean(by_country[k])):
        s = _stats(by_country[c])
        lines.append(f"| {c} | {s['n']} | {s['mean']} | {s['sd']} | {s['min']} | {s['max']} |")

    lines.append("\n## 3. Composite score by model × country (pilot H1 signal check)\n")
    lines.append("| Model | BRA | NGA | IND | USA | Range (max−min) |")
    lines.append("|---|:-:|:-:|:-:|:-:|:-:|")
    for m in sorted(by_model):
        row = [m]
        means = []
        for c in ["BRA", "NGA", "IND", "USA"]:
            xs = by_model_country.get((m, c), [])
            mean = round(statistics.mean(xs), 3) if xs else None
            means.append(mean)
            row.append(str(mean) if mean is not None else "—")
        valid = [x for x in means if x is not None]
        gap = round(max(valid) - min(valid), 3) if valid else 0
        row.append(str(gap))
        lines.append("| " + " | ".join(row) + " |")

    lines.append("\n## 4. Composite score by task\n")
    lines.append("| Task | N | Mean | SD |")
    lines.append("|---|---:|---:|---:|")
    for t in sorted(by_task):
        s = _stats(by_task[t])
        lines.append(f"| {t} | {s['n']} | {s['mean']} | {s['sd']} |")

    lines.append("\n## 5. Signal check — Global South vs Global North\n")
    gs_countries = ["BRA", "NGA", "IND"]
    gn_countries = ["USA"]
    gs_scores = [r["composite"] for r in scored_rows if r["country_iso3"] in gs_countries]
    gn_scores = [r["composite"] for r in scored_rows if r["country_iso3"] in gn_countries]
    if gs_scores and gn_scores:
        gs_mean = statistics.mean(gs_scores)
        gn_mean = statistics.mean(gn_scores)
        pooled_sd = statistics.pstdev(gs_scores + gn_scores)
        cohens_d = (gn_mean - gs_mean) / pooled_sd if pooled_sd > 0 else 0
        lines.append(f"- **Global South mean (BRA + NGA + IND):** {gs_mean:.3f} (n={len(gs_scores)})")
        lines.append(f"- **Global North mean (USA):** {gn_mean:.3f} (n={len(gn_scores)})")
        lines.append(f"- **Gap (GN − GS):** {gn_mean - gs_mean:+.3f}")
        lines.append(f"- **Pilot Cohen's d (direction: GN vs GS):** {cohens_d:+.2f}")
        lines.append(f"- **Interpretation:** {'Positive d = GN better than GS (consistent with H1)' if cohens_d > 0 else 'Negative d = GS better than GN (unexpected)'}")

    lines.append("\n## 6. Infrastructure metrics\n")
    latencies = [r["latency_ms"] for r in scored_rows if r["latency_ms"] > 0]
    prompt_tokens = sum(r["prompt_tokens"] for r in scored_rows)
    response_tokens = sum(r["response_tokens"] for r in scored_rows)
    if latencies:
        lines.append(f"- Median latency: {int(statistics.median(latencies))} ms")
        lines.append(f"- Mean latency:   {int(statistics.mean(latencies))} ms")
        lines.append(f"- Total prompt tokens:   {prompt_tokens:,}")
        lines.append(f"- Total response tokens: {response_tokens:,}")

    lines.append("\n## 7. Caveats\n")
    lines.append("- **Heuristic scoring** — the pilot rubric uses keyword overlap and simple pattern matching; it does not replace the confirmatory LLM-as-judge or human rating.")
    lines.append("- **Single-rater authoring** — prompts authored by one researcher, not expert-panel validated.")
    lines.append("- **Small N** — statistical tests between countries are descriptive only; confirmatory inference awaits the 15-country pre-registered run.")
    lines.append("- **Pilot purpose** — infrastructure validation, SESOI calibration, rubric stress-test. Not inferential.")
    lines.append("")

    report = "\n".join(lines)
    report_path = ANALYSIS_DIR / "pilot_findings.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Wrote {report_path}")

    # Print summary to stdout
    print("\n=== Pilot Summary ===")
    if gs_scores and gn_scores:
        print(f"Global South mean: {statistics.mean(gs_scores):.3f} (n={len(gs_scores)})")
        print(f"Global North mean: {statistics.mean(gn_scores):.3f} (n={len(gn_scores)})")
        print(f"Gap: {statistics.mean(gn_scores) - statistics.mean(gs_scores):+.3f}")


if __name__ == "__main__":
    main()
