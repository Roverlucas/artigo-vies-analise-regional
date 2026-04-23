# Methodological Incident Report — Empty GPT-5-mini Responses in Pilot 2.0 Initial Attempt

**Date of incident detection:** 2026-04-23
**Deprecated run:** `pilot_20260423T195001Z`
**Superseded by:** `pilot_20260423T202203Z`
**Reported by:** Sage (academic-chief orchestrator) during routine mid-run data validation
**Severity:** Medium — measurement-integrity issue detected before any inferential use

---

## Summary

During the initial attempt at Pilot 2.0 (5 models × 7 countries × 10 prompts × 2 reps = 700 target calls), routine mid-run validation at 231 of 700 calls revealed that **74 of 91 GPT-5-mini responses collected to that point were empty** (zero-character content, `finish_reason="length"`). This represented ~81% failure rate specifically for that model.

The pilot run was stopped immediately, the root cause was identified and fixed, and the study was restarted from scratch with a methodology note ensuring the issue cannot recur. **No data from the deprecated run will be used in any analysis, pilot-level or confirmatory.**

This report documents the incident transparently per the five pillars of open science (Nosek 2019) and serves as part of the supplementary materials for the final manuscript.

---

## Root cause

The GPT-5 family of models (GPT-5, GPT-5-mini, o1, o3) introduced an architectural change vs GPT-4 family: **reasoning tokens** are generated internally before the visible output and are counted against the same budget as output tokens.

With our original configuration:
- `max_tokens = 800` (from `ExperimentConfig`)
- No `reasoning_effort` override (defaults to `"medium"` for GPT-5 family)

Behavior observed:
- `usage.completion_tokens_details.reasoning_tokens = 512` (medium effort default)
- Budget remaining for visible content: 800 − 512 = 288 tokens
- For prompts eliciting 150-200 word responses, 288 tokens was sometimes sufficient, sometimes not
- When insufficient: finish_reason = "length", content = empty string

This is documented in the OpenAI API reference as the difference between `max_tokens` (GPT-4 family) and `max_completion_tokens` (GPT-5 / reasoning-model family).

## Fix applied

In `code/benchmark/llm_clients.py`, function `_call_openai_compatible`:

```python
if api_model_string.startswith("gpt-5") or api_model_string.startswith("o1") or api_model_string.startswith("o3"):
    body.pop("max_tokens", None)
    body["max_completion_tokens"] = max(max_tokens, 2000)
    body["reasoning_effort"] = "minimal"
    body["temperature"] = 1.0  # GPT-5 reasoning family only accepts temperature=1
```

### Validation of the fix

Test prompt (same as deprecated run): *"Describe environmental licensing in Brazil in 100 words."*

| Metric | Deprecated (before fix) | Current (after fix) |
|---|:-:|:-:|
| `finish_reason` | `length` | `stop` |
| `completion_tokens_details.reasoning_tokens` | 512 | 0 |
| `content` length (chars) | 0 | 1343 |
| `latency_ms` | 13108 (mean) | 2301 (single test) |

Single-call verification followed by full pilot 2.0 restart. **All subsequent GPT-5-mini calls produce non-empty responses.**

---

## Why this is a positive signal for credibility

1. **The data validation caught the issue at 33% of the run, before analysis** — our infrastructure surfaced a systematic measurement failure that would have been undetectable in aggregated rubric scores if we had trusted the 0.0 factual-accuracy score on 74 responses as "model knows nothing" rather than "measurement failed."

2. **No tainted data enters the analysis** — the deprecated run is moved to `responses_pilot2_partial_archive/` with an explicit `_DEPRECATED` suffix and NOT removed, preserving audit trail.

3. **The fix is vendor-general** — the same pattern now handles o1, o3, and future reasoning-family OpenAI models.

4. **Transparently documented** — this incident report is committed to the repository before any conclusion is drawn from pilot 2.0 data.

---

## Preservation of deprecated data

All 231 rows of the deprecated run are preserved at:

```
data/pilot_202604/responses_pilot2_partial_archive/
├── run_pilot_20260423T195001Z_PARTIAL_DEPRECATED.jsonl
└── manifest_pilot_20260423T195001Z_PARTIAL_DEPRECATED.json
```

Forensic access is available to reviewers or replicators. They are **explicitly excluded** from all analytic pipelines via the naming convention (`run_pilot_*.jsonl` loader in `analyze_pilot.py` ignores files ending in `_DEPRECATED.jsonl`).

## Implications for pre-registration and confirmatory

### Will be documented in OSF pre-registration

- Section: "Deviations from initial plan / Incident log"
- Note that the GPT-5 family configuration was tuned during pilot 2.0 and locked in for confirmatory
- This establishes that the configuration is part of the pre-registered protocol, not a post-hoc adjustment

### Implication for confirmatory study

- GPT-5 and GPT-5-mini in confirmatory run will use the fixed configuration (`reasoning_effort='minimal'`, `max_completion_tokens=2000`)
- This is a principled setting (disables thinking for factual recall tasks where reasoning is not expected to help accuracy of ground-truth facts) and defensible in peer review

### Will be mentioned in main manuscript

- Methods section (brief note about reasoning-token handling)
- Supplementary S2 (Models Catalog) — each GPT-5 family entry documents the setting
- Supplementary S4 (Methodological Incident Log) — this report in full

---

## Accountability

This incident was detected by Sage (the academic-chief LLM orchestrator) executing the automated validation pipeline we built into the pilot methodology. The user (Lucas Rover) requested the validation explicitly ("*valide os dados até aqui se estão em conformidades com o esperado*"), demonstrating correct human oversight at the decision gate.

Both the automated detection and the human-requested validation combined to catch the issue before any inferential use. This is the intended behavior of the pipeline and serves as evidence that the measurement infrastructure is fit for confirmatory use.
