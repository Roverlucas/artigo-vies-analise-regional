# Pilot Findings — Exploratory Analysis (v3.3 Pilot)

> **PILOT — exploratory, not confirmatory.** Heuristic rubric scoring, not the confirmatory LLM-as-judge or human rating.

**Total responses analyzed:** 240
**Distinct models:** 3
**Countries:** 4

## 1. Composite score by model (averaged across all prompts)

| Model | N | Mean | SD | Min | Max |
|---|---:|---:|---:|---:|---:|
| claude_haiku | 80 | 0.758 | 0.09 | 0.554 | 0.85 |
| gemini_flash | 80 | 0.515 | 0.141 | 0.24 | 0.85 |
| gpt5_mini | 80 | 0.399 | 0.157 | 0.225 | 0.85 |

## 2. Composite score by country (averaged across all models)

| Country | N | Mean | SD | Min | Max |
|---|---:|---:|---:|---:|---:|
| USA | 60 | 0.586 | 0.197 | 0.225 | 0.85 |
| IND | 60 | 0.558 | 0.214 | 0.225 | 0.85 |
| BRA | 60 | 0.548 | 0.195 | 0.225 | 0.85 |
| NGA | 60 | 0.538 | 0.193 | 0.225 | 0.85 |

## 3. Composite score by model × country (pilot H1 signal check)

| Model | BRA | NGA | IND | USA | Range (max−min) |
|---|:-:|:-:|:-:|:-:|:-:|
| claude_haiku | 0.747 | 0.736 | 0.785 | 0.764 | 0.049 |
| gemini_flash | 0.487 | 0.515 | 0.523 | 0.533 | 0.046 |
| gpt5_mini | 0.41 | 0.361 | 0.365 | 0.461 | 0.1 |

## 4. Composite score by task

| Task | N | Mean | SD |
|---|---:|---:|---:|
| T1 | 48 | 0.57 | 0.195 |
| T2 | 48 | 0.571 | 0.218 |
| T3 | 48 | 0.61 | 0.197 |
| T4 | 48 | 0.487 | 0.146 |
| T5 | 48 | 0.55 | 0.221 |

## 5. Signal check — Global South vs Global North

- **Global South mean (BRA + NGA + IND):** 0.548 (n=180)
- **Global North mean (USA):** 0.586 (n=60)
- **Gap (GN − GS):** +0.038
- **Pilot Cohen's d (direction: GN vs GS):** +0.19
- **Interpretation:** Positive d = GN better than GS (consistent with H1)

## 6. Infrastructure metrics

- Median latency: 5002 ms
- Mean latency:   6992 ms
- Total prompt tokens:   12,136
- Total response tokens: 84,197

## 7. Caveats

- **Heuristic scoring** — the pilot rubric uses keyword overlap and simple pattern matching; it does not replace the confirmatory LLM-as-judge or human rating.
- **Single-rater authoring** — prompts authored by one researcher, not expert-panel validated.
- **Small N** — statistical tests between countries are descriptive only; confirmatory inference awaits the 15-country pre-registered run.
- **Pilot purpose** — infrastructure validation, SESOI calibration, rubric stress-test. Not inferential.
