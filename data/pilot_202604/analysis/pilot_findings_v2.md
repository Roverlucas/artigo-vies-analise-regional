# Pilot 2.0 Findings — LLM-as-Judge Analysis

> **PILOT — exploratory, not confirmatory.** Scoring via Claude Haiku 4.5 as judge (G-Eval framework, Liu et al. 2023). Final confirmatory scoring will use Claude Opus 4.7 or human panel.

**Total judge scores analyzed:** 700
**Models:** 5
**Countries:** 7

## 1. Composite score by model

| Model | N | Mean | SD | Median | Min | Max |
|---|---:|---:|---:|---:|---:|---:|
| gpt5_mini | 140 | 0.668 | 0.173 | 0.719 | 0.075 | 0.922 |
| claude_haiku | 140 | 0.646 | 0.141 | 0.672 | 0.2 | 0.945 |
| gemini_flash | 140 | 0.614 | 0.197 | 0.665 | 0.075 | 0.84 |
| llama4_scout | 140 | 0.536 | 0.156 | 0.578 | 0.12 | 0.835 |
| command_rp | 140 | 0.498 | 0.18 | 0.564 | 0.098 | 0.77 |

## 2. Composite score by country

| Country | Tier | N | Mean | SD | Median |
|---|---|---:|---:|---:|---:|
| USA | GN | 100 | 0.647 | 0.168 | 0.696 |
| DEU | GN | 100 | 0.625 | 0.179 | 0.665 |
| IDN | GS | 100 | 0.606 | 0.169 | 0.647 |
| PER | GS | 100 | 0.58 | 0.173 | 0.61 |
| IND | GS | 100 | 0.574 | 0.183 | 0.62 |
| BRA | GS | 100 | 0.565 | 0.203 | 0.641 |
| NGA | GS | 100 | 0.551 | 0.182 | 0.597 |

## 3. Model × Country matrix (composite mean)

| Model | BRA | NGA | IND | PER | IDN | USA | DEU | Range |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| claude_haiku | 0.68 | 0.58 | 0.66 | 0.55 | 0.65 | 0.71 | 0.7 | 0.16 |
| command_rp | 0.45 | 0.48 | 0.47 | 0.49 | 0.56 | 0.53 | 0.51 | 0.11 |
| gemini_flash | 0.55 | 0.58 | 0.57 | 0.6 | 0.61 | 0.67 | 0.72 | 0.17 |
| gpt5_mini | 0.62 | 0.66 | 0.65 | 0.68 | 0.66 | 0.73 | 0.66 | 0.11 |
| llama4_scout | 0.53 | 0.45 | 0.52 | 0.58 | 0.55 | 0.6 | 0.53 | 0.15 |

## 4. Composite score by task

| Task | N | Mean | SD |
|---|---:|---:|---:|
| T1 | 140 | 0.507 | 0.207 |
| T2 | 140 | 0.624 | 0.09 |
| T3 | 140 | 0.677 | 0.072 |
| T4 | 140 | 0.655 | 0.173 |
| T5 | 140 | 0.499 | 0.229 |

## 5. H1 signal — Global South vs Global North

- **Global South (BRA + NGA + IND + PER + IDN):** mean = **0.575**, n = 500
- **Global North (USA + DEU):** mean = **0.636**, n = 200
- **Gap (GN − GS):** **+0.060** (+6.0 percentage points)
- **Pooled SD:** 0.180
- **Pilot Cohen's d:** **+0.34**
- **Direction:** GN > GS (consistent with H1)
- **Magnitude:** small-to-moderate; may reach significance at confirmatory N

## 6. Variance components (for SAP recalibration)

| Component | Variance | ICC | Notes |
|---|---:|---:|---|
| Total | 0.0330 | 1.000 | Reference |
| Between-country | 0.0010 | 0.031 | H1-relevant |
| Between-model | 0.0042 | 0.128 | Random effect |
| Residual | 0.0278 | 0.841 | Within-cell |

**Implication for SAP:** ICC_country = 0.031; ICC_model = 0.128.
Update Monte Carlo power analysis in `etapa4_sap.md` §3 with these values before OSF deposit.

## 7. H5 signal — Open frontier vs Closed accessible

- **Open frontier mean (Llama 4 Scout + Command R+):** 0.517 (n=280)
- **Closed accessible mean (Haiku + GPT-5-mini + Gemini Flash):** 0.643 (n=420)
- **Gap (closed − open):** +0.125
- **Pilot signal:** **not consistent with H5** (gap of 12.5pp exceeds 5pp threshold)
- *Caveat:* pilot uses Llama 4 Scout 17B (smaller than Tier A target 70B+). Confirmatory will include Llama 3.3 70B and other Tier A frontier open models.

## 8. Caveats

- **Single judge** (Haiku 4.5). For confirmatory, use Claude Opus 4.7 as judge OR add 2nd judge for inter-rater reliability (Krippendorff α ≥ 0.70).
- **Single-author prompts** for non-BRA countries. Confirmatory requires expert-panel validation.
- **Pilot N small** — country-level inference noisy.
- **Self-evaluation flag:** Haiku 4.5 is in the model sample being evaluated. Pilot 2 documents this as limitation; confirmatory uses non-overlapping judge.
- **No multilingual prompts in pilot** — all prompts in EN. Confirmatory adds sparse multilingual matrix.
