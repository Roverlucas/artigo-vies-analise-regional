"""
llm_judge.py — LLM-as-judge rubric scoring for pilot 2.0+.

Uses Claude Haiku 4.5 as the judge model. Given a (prompt, ground_truth,
response, task) tuple, returns structured rubric scores via JSON output.

Pilot 2.0 uses Haiku as judge for cost reasons (~$0.003/judgment, vs
$0.058/judgment for Opus). Confirmatory should upgrade to Opus 4.7 or
human panel.

Judge prompt design follows Liu et al. 2023 G-Eval framework with
explicit rubric components and pre-specified scoring rubrics.
"""

from __future__ import annotations
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from code.benchmark.llm_clients import call_llm, _load_key


JUDGE_MODEL_ID = "claude_haiku"  # Using Haiku 4.5 as judge for pilot cost
JUDGE_TEMPERATURE = 0.1            # Low temperature for consistent scoring
JUDGE_MAX_TOKENS = 800


JUDGE_PROMPT_TEMPLATE = """You are an expert judge evaluating an LLM response against a documented ground truth. You must rate the response on five rubric components, each 0.0 to 1.0.

## Original prompt the LLM was asked:
{prompt_text}

## Ground truth reference (verified against official sources):
{ground_truth}

## Task type:
{task_id} — {task_description}

## LLM response to evaluate:
<response>
{response_text}
</response>

## Scoring rubric

Rate each component 0.0 to 1.0:

1. **factual_accuracy** (0.0 = all key facts wrong; 0.5 = partially right; 1.0 = matches ground truth)
2. **contextual_completeness** (0.0 = missing context; 0.5 = partial; 1.0 = full context covered)
3. **citation_quality** (0.0 = no sources/fake; 0.5 = some sources; 1.0 = specific verifiable sources). Use 0.5 as default if task does not require citations.
4. **calibration** (0.0 = over/underconfident; 1.0 = expresses uncertainty appropriately). Use 0.5 as default if task is not a calibration task.
5. **absence_of_hallucination** (0.0 = contains fabricated facts; 1.0 = all claims defensible against ground truth or documented refusal)

## Output format

Return ONLY a JSON object with exactly these keys. No prose, no markdown, no explanation:

{{"factual_accuracy": 0.0, "contextual_completeness": 0.0, "citation_quality": 0.5, "calibration": 0.5, "absence_of_hallucination": 1.0, "rationale": "one sentence explaining the scores"}}
"""


TASK_DESCRIPTIONS = {
    "T1": "Direct factual recall — brief answer, verify specific facts match ground truth",
    "T2": "Open-ended generation (150-200 words) — assess factual content, context, completeness",
    "T3": "List extraction (5-8 items) — verify each named entity is real and relevant",
    "T4": "Primary-source recommendation (3-5 sources) — verify sources are real and authoritative",
    "T5": "Calibration — extract numeric estimate + confidence; verify estimate against ground-truth range",
}


RUBRIC_WEIGHTS = {
    "factual_accuracy":        0.30,
    "contextual_completeness": 0.25,
    "citation_quality":        0.15,
    "calibration":             0.15,
    "absence_of_hallucination": 0.15,
}


def _parse_judge_response(text: str) -> dict:
    """Extract JSON object from judge response. Handles markdown fences if present."""
    text = text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
    # Find the first JSON object
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"No JSON object in judge response: {text[:200]}")
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parse failed: {e}; text: {m.group(0)[:200]}")


def judge_response(
    prompt_text: str,
    ground_truth: str,
    response_text: str,
    task_id: str,
    judge_model_id: str = JUDGE_MODEL_ID,
) -> dict:
    """Judge a model response against ground truth using LLM-as-judge.

    Returns dict with rubric component scores plus composite, plus raw_judge_response.
    If judge fails after retries, returns fallback heuristic zeros + error flag.
    """
    task_desc = TASK_DESCRIPTIONS.get(task_id, "General task")
    judge_prompt = JUDGE_PROMPT_TEMPLATE.format(
        prompt_text=prompt_text[:3000],
        ground_truth=ground_truth[:2000],
        response_text=response_text[:3000],
        task_id=task_id,
        task_description=task_desc,
    )

    resp = call_llm(
        judge_model_id,
        judge_prompt,
        language="en",
        replicate_idx=0,
        temperature=JUDGE_TEMPERATURE,
        max_tokens=JUDGE_MAX_TOKENS,
    )

    if resp.api_error:
        return {
            "factual_accuracy":         0.0,
            "contextual_completeness":  0.0,
            "citation_quality":         0.0,
            "calibration":              0.0,
            "absence_of_hallucination": 0.0,
            "composite":                0.0,
            "rationale":                f"JUDGE_API_ERROR: {resp.api_error[:200]}",
            "judge_model":              resp.model_version,
            "judge_tokens":             resp.prompt_tokens + resp.response_tokens,
            "judge_latency_ms":         resp.latency_ms,
            "error":                    True,
        }

    try:
        parsed = _parse_judge_response(resp.response_text)
    except ValueError as e:
        return {
            "factual_accuracy":         0.0,
            "contextual_completeness":  0.0,
            "citation_quality":         0.0,
            "calibration":              0.0,
            "absence_of_hallucination": 0.0,
            "composite":                0.0,
            "rationale":                f"JUDGE_PARSE_ERROR: {str(e)[:200]}; raw: {resp.response_text[:200]}",
            "judge_model":              resp.model_version,
            "judge_tokens":             resp.prompt_tokens + resp.response_tokens,
            "judge_latency_ms":         resp.latency_ms,
            "error":                    True,
        }

    # Clip scores to [0, 1]
    def _clip01(x):
        try:
            return max(0.0, min(1.0, float(x)))
        except (TypeError, ValueError):
            return 0.0

    scores = {
        "factual_accuracy":         _clip01(parsed.get("factual_accuracy", 0)),
        "contextual_completeness":  _clip01(parsed.get("contextual_completeness", 0)),
        "citation_quality":         _clip01(parsed.get("citation_quality", 0.5)),
        "calibration":              _clip01(parsed.get("calibration", 0.5)),
        "absence_of_hallucination": _clip01(parsed.get("absence_of_hallucination", 1.0)),
    }
    scores["composite"] = sum(scores[k] * RUBRIC_WEIGHTS[k] for k in RUBRIC_WEIGHTS)
    scores["rationale"] = str(parsed.get("rationale", ""))[:400]
    scores["judge_model"] = resp.model_version
    scores["judge_tokens"] = resp.prompt_tokens + resp.response_tokens
    scores["judge_latency_ms"] = resp.latency_ms
    scores["error"] = False
    return scores


if __name__ == "__main__":
    # Quick test with a synthetic example
    test_result = judge_response(
        prompt_text="What is the capital of Brazil?",
        ground_truth="The capital of Brazil is Brasília (since 1960).",
        response_text="Brasília has been the capital of Brazil since April 21, 1960.",
        task_id="T1",
    )
    print(json.dumps(test_result, indent=2, ensure_ascii=False))
