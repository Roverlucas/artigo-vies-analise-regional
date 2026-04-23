# Supplementary Material S2 — Models Catalog

**Project:** Geographic Bias Across the LLM Spectrum: A Full-Spectrum Open-Weight Audit for Global South Policy Research
**Supplement for:** Main manuscript, submitted to *Patterns* (Cell Press)
**Version:** 1.0 (2026-04-23)

---

## S2.1 Inclusion and exclusion criteria

Models were selected following the pre-registered protocol; the criteria below are documented verbatim as submitted at OSF prior to confirmatory execution.

### Inclusion criteria

A candidate LLM is included in the study if it satisfies all of the following:

1. **Public API availability** OR **public open-weight availability** allowing reproducible execution (Moayeri et al. 2024 precedent).
2. **Release date** between 2023-01-01 and 2026-04-23 (study window).
3. **Parameter count** ≥ 7B (to exclude small-model baselines that are not reasonable policy-research tools).
4. **At least one** documented multilingual capability OR documented focus on English (for EN-primary evaluation).
5. **Deterministic inference** possible (temperature support, reproducible sampling when available).
6. **Vendor diversity** — no more than 2 models from the same vendor per tier, enforcing cross-vendor coverage per Liu et al. (2023).

### Exclusion criteria

- Models not accessible via API nor open weights (e.g., vendor-internal models).
- Deprecated models (GPT-3.5, Claude 2 family, Llama 2, Gemini 1.0) — exclude vintage of 2022 and earlier.
- Models whose pricing structurally exceeds the project budget (Claude Opus 4.7 included only as **reserve** for reviewer response).
- Research-only models without stable release tags (excludes most Hugging Face community fine-tunes lacking version control).

---

## S2.2 Complete catalog — 14 models in 5 tiers

### S2.2.1 Tier A — Open-weight frontier (5 models, full scope 15 countries × 2 reps)

#### A1. Llama 4 70B Instruct

- **Vendor:** Meta AI
- **API model string:** `llama-4-70b-instruct` (as exposed on Groq Cloud, release tag pinned at experiment time)
- **Release date:** 2025 Q3 (v1.0 of Llama 4 family)
- **License:** Llama 4 Community License (open weights, permissive for research)
- **Parameter count:** 70 billion (dense)
- **Context window:** 131,072 tokens
- **Multilingual:** yes (trained on ~25% non-English tokens per Meta technical report)
- **Execution venue:** Groq Cloud (free tier, ~1,000 calls/day)
- **Rationale:** Canonical open-weight frontier reference; Meta's flagship for 2025-2026 open models; widely used in Global South research per Hugging Face download statistics.

#### A2. Qwen 3 72B

- **Vendor:** Alibaba Cloud / Qwen Team
- **API model string:** `qwen/qwen3-72b-instruct` (OpenRouter) / `Qwen/Qwen3-72B-Instruct` (HuggingFace)
- **Release date:** 2025 Q4
- **License:** Apache 2.0 (fully open weights)
- **Parameter count:** 72 billion (dense)
- **Context window:** 128,000 tokens
- **Multilingual:** strong — explicit multilingual training with ~100 languages
- **Execution venue:** OpenRouter (free credit slots) with DeepInfra as fallback
- **Rationale:** Leading multilingual open frontier as of 2026; specifically strong on low-resource Asian languages (Hindi, Bengali, Indonesian, Filipino) per Qwen team benchmarks; novel vendor perspective (Chinese origin training corpus) as independent check on Western-vendor bias.

#### A3. DeepSeek-V3

- **Vendor:** DeepSeek AI
- **API model string:** `deepseek-chat` (DeepSeek API) / `deepseek-ai/DeepSeek-V3` (HuggingFace)
- **Release date:** 2024 Q4 (V3 base), ongoing fine-tune updates
- **License:** DeepSeek License v1 (open weights with commercial restrictions; permissive for research use)
- **Parameter count:** 671 billion total (Mixture-of-Experts, ~37B active per token)
- **Context window:** 128,000 tokens
- **Multilingual:** strong (EN + CN primary, multilingual capable)
- **Execution venue:** DeepSeek paid API (US$ 1.99 existing credit, ~3,500 calls possible)
- **Rationale:** Largest-scale open-weight frontier model available as of 2026 by total parameters; represents non-Western training corpus; notable for strong mathematical and reasoning benchmarks at fraction of closed-frontier inference cost.

#### A4. Mixtral 8×22B

- **Vendor:** Mistral AI
- **API model string:** `mixtral-8x22b-instruct-v0.1` (Groq)
- **Release date:** 2024 Q2
- **License:** Apache 2.0
- **Parameter count:** 141B total (Mixture-of-Experts, 8 experts × 22B)
- **Context window:** 64,000 tokens
- **Multilingual:** yes, explicit support for English, French, German, Spanish, Italian
- **Execution venue:** Groq Cloud (free tier)
- **Rationale:** European-vendor open-weight frontier; complements Meta (US) and Alibaba (China) for vendor-geography triangulation; established MoE architecture benchmark.

#### A5. Command R+ 104B

- **Vendor:** Cohere
- **API model string:** `command-r-plus-08-2024` (Cohere API)
- **Release date:** 2024 Q3 update (original Command R+ 2024 Q2)
- **License:** Cohere Community License (open weights for research, restrictions on commercial use)
- **Parameter count:** 104 billion
- **Context window:** 128,000 tokens
- **Multilingual:** explicit multilingual optimization for 10+ languages including Portuguese, Spanish, Japanese, German, French
- **Execution venue:** Cohere trial API key (free-tier credits)
- **Rationale:** RAG-tuned open model — directly relevant to T4 (primary source recommendation); distinctive vendor vs the other 4 Tier A models.

### S2.2.2 Tier B — Open-weight mid (3 models, full scope)

#### B1. Gemma 3 27B

- **Vendor:** Google DeepMind
- **API model string:** `gemma-3-27b-it` (Groq)
- **Release date:** 2025 Q1
- **License:** Gemma License (open weights, research permissive)
- **Parameter count:** 27 billion
- **Context window:** 131,072 tokens
- **Multilingual:** yes
- **Execution venue:** Groq Cloud (free tier)
- **Rationale:** Google's open-weight mid-tier — the accessibility gateway for many Global South labs; same vendor as Gemini 2.5 Flash (Tier D) enables within-vendor open-vs-closed comparison.

#### B2. Qwen 3 14B

- **Vendor:** Alibaba Cloud / Qwen Team
- **API model string:** `qwen3:14b` (Ollama local)
- **Release date:** 2025 Q4
- **License:** Apache 2.0
- **Parameter count:** 14 billion
- **Context window:** 128,000 tokens
- **Multilingual:** strong
- **Execution venue:** Local Ollama on Apple M4 24GB RAM
- **Rationale:** Tests whether scaled-down open-weight preserves the multilingual capability of its frontier sibling (A2); supports full local reproducibility.

#### B3. Phi-4 14B

- **Vendor:** Microsoft Research
- **API model string:** `phi4:14b` (Ollama local)
- **Release date:** 2024 Q4
- **License:** MIT
- **Parameter count:** 14.7 billion
- **Context window:** 16,384 tokens
- **Multilingual:** limited (English-optimized)
- **Execution venue:** Local Ollama on Apple M4 24GB RAM
- **Rationale:** Microsoft small-model reference; heavily English-pretrained — serves as an informative contrast to Qwen 3 14B for isolating the effect of training-corpus multilingualism at fixed parameter count.

### S2.2.3 Tier C — Open-weight small / regional (2 models, full scope)

#### C1. Llama 4 8B

- **Vendor:** Meta AI
- **API model string:** `llama4:8b` (Ollama local)
- **Release date:** 2025 Q3
- **License:** Llama 4 Community License
- **Parameter count:** 8 billion
- **Context window:** 131,072 tokens
- **Multilingual:** yes
- **Execution venue:** Local Ollama on Apple M4 24GB RAM
- **Rationale:** Accessibility floor — the smallest frontier-family open model that remains research-capable; tests lower bound of usability for Global South labs with minimal compute.

#### C2. Lince-Mistral 7B ⭐ (H3 regional model)

- **Vendor:** PUCRS (Pontifícia Universidade Católica do Rio Grande do Sul, Brazil)
- **API model string:** `lince-mistral-7b` (Ollama local custom pull)
- **Release date:** 2024 (Pires et al.)
- **License:** Apache 2.0 (as Mistral base); derivative model is open
- **Parameter count:** 7 billion (Mistral 7B base, fine-tuned on Portuguese corpus)
- **Context window:** 8,192 tokens
- **Multilingual:** Portuguese-primary (fine-tuned)
- **Execution venue:** Local Ollama on Apple M4 24GB RAM
- **Rationale:** **Central to H3.** First major open-weight Portuguese-optimized LLM from a Brazilian institution; operationalizes the "regional model" hypothesis in a way that preserves the study's open-science commitment (Sabiá-3, the original v1 choice, is closed-source). Published in proceedings of STIL 2024 / INTERSPEECH Brazil track.

### S2.2.4 Tier D — Closed accessible (2 models, full scope)

#### D1. Claude Haiku 4.5

- **Vendor:** Anthropic
- **API model string:** `claude-haiku-4-5-20251001`
- **Release date:** 2025-10-01
- **License:** Closed-source / API-only
- **Parameter count:** undisclosed
- **Context window:** 200,000 tokens
- **Multilingual:** strong
- **Execution venue:** Anthropic API (US$ 10 existing credit)
- **Rationale:** Anthropic's accessible tier — the closed-source counterpart to Tier B open mid-models in both pricing tier and research-usability profile.

#### D2. GPT-5-mini

- **Vendor:** OpenAI
- **API model string:** `gpt-5-mini`
- **Release date:** 2025 Q4 (aligned with GPT-5 family launch)
- **License:** Closed-source / API-only
- **Parameter count:** undisclosed
- **Context window:** 400,000 tokens (GPT-5 family spec)
- **Multilingual:** strong
- **Execution venue:** OpenAI API (US$ 15 budget including top-up)
- **Rationale:** OpenAI's accessible tier — direct counterpart to Haiku 4.5 at similar price/capability tier. Paired with GPT-5 (Tier E) enables within-vendor paired comparison of accessible-vs-frontier from a single vendor, a design novelty for this benchmark.

#### D3-equivalent Note — Gemini 2.5 Flash

Although listed in the config as closed accessible (`gemini_flash`), Gemini 2.5 Flash technically sits between D (accessible) and B (mid); we classify it D for consistency with the accessible-closed tier concept. Gemini 2.5 Flash is also in full scope (15 countries × 2 reps).

- **Vendor:** Google DeepMind
- **API model string:** `gemini-2.5-flash`
- **Release date:** 2025 Q2
- **License:** Closed-source / API-only
- **Parameter count:** undisclosed
- **Context window:** 1,000,000 tokens
- **Multilingual:** strong
- **Execution venue:** Google AI Studio (free tier — 1,500 requests/day)
- **Rationale:** Google's accessible tier from the Gemini 2.5 family; free-tier access makes it the single model most realistically usable by Global South researchers without budget. Policy-relevance primary.

### S2.2.5 Tier E — Closed frontier SOTA (1 model, full scope)

#### E1. GPT-5 ⭐ (Tier B of H5: closed frontier comparator)

- **Vendor:** OpenAI
- **API model string:** `gpt-5`
- **Release date:** 2025 Q4
- **License:** Closed-source / API-only
- **Parameter count:** undisclosed
- **Context window:** 400,000 tokens
- **Multilingual:** strong
- **Execution venue:** OpenAI API (US$ 15 budget)
- **Rationale:** **Central to H5.** 2026 reference SOTA for closed frontier. Enables the key open-vs-closed contrast at the frontier scale. Full scope across all 15 countries (2 reps) matches Tier A open-frontier models for clean H5 testing.

### S2.2.6 Reserve — not executed unless reviewer requests

#### R1. Claude Opus 4.7

- **Vendor:** Anthropic
- **API model string:** `claude-opus-4-7`
- **Release date:** 2025-12 (Opus 4.7 release)
- **License:** Closed-source / API-only
- **Parameter count:** undisclosed
- **Context window:** 500,000 tokens
- **Multilingual:** strong
- **Execution venue:** Anthropic API (US$ 10 existing credit reserve)
- **Rationale:** RESERVED. Held as contingent inclusion to respond to peer reviewer requests for "second closed frontier vendor." If activated, runs 3-country subset (BR, USA, IND) × 25 prompts × 2 reps = 150 calls ≈ US$ 8.70, leaving budget buffer. Pre-registered as contingent inclusion in OSF protocol.

---

## S2.3 Vendor diversity matrix

| Vendor | Country of origin | Tier A | Tier B | Tier C | Tier D | Tier E | Reserve | Total |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Meta | USA | 1 (A1) | — | 1 (C1) | — | — | — | 2 |
| Alibaba | China | 1 (A2) | 1 (B2) | — | — | — | — | 2 |
| DeepSeek | China | 1 (A3) | — | — | — | — | — | 1 |
| Mistral | France/EU | 1 (A4) | — | — | — | — | — | 1 |
| Cohere | Canada | 1 (A5) | — | — | — | — | — | 1 |
| Google | USA | — | 1 (B1) | — | 1 (D3) | — | — | 2 |
| Microsoft | USA | — | 1 (B3) | — | — | — | — | 1 |
| PUCRS | Brazil | — | — | 1 (C2) | — | — | — | 1 |
| Anthropic | USA | — | — | — | 1 (D1) | — | 1 (R1) | 2 |
| OpenAI | USA | — | — | — | 1 (D2) | 1 (E1) | — | 2 |
| **TOTAL** | — | **5** | **3** | **2** | **3** | **1** | **1** | **15** |

Effective vendor coverage:
- 10 distinct vendors
- 5 countries of origin (US, China, France, Canada, Brazil)
- Open/closed balance: 10 open-weight + 4 closed (executed) + 1 closed (reserve)

---

## S2.4 Execution venue summary

| Venue | Models executed | Cost (planned, pilot) | Cost (planned, confirmatory) |
|---|---|---:|---:|
| Groq Cloud (free tier) | Llama 4 70B, Mixtral 8×22B, Gemma 3 27B | US$ 0 | US$ 0 |
| OpenRouter (free credit) | Qwen 3 72B (primary) | US$ 0 | US$ 0 |
| DeepInfra (free credit) | Qwen 3 72B (fallback) | US$ 0 | US$ 0 |
| DeepSeek API (paid, existing) | DeepSeek-V3 | US$ 0 (pilot-excluded) | US$ 1.38 |
| Cohere trial | Command R+ | US$ 0 | US$ 0 |
| Google AI Studio (free) | Gemini 2.5 Flash | US$ 0 | US$ 0 |
| Anthropic API (paid, existing) | Haiku 4.5 | US$ 0.20 | US$ 4.05 |
| OpenAI API (paid, US$ 15) | GPT-5-mini, GPT-5 | US$ 0.40 | US$ 14.82 |
| Ollama local (Apple M4) | Qwen 3 14B, Phi-4 14B, Llama 4 8B, Lince-Mistral 7B | US$ 0 | US$ 0 |
| **TOTAL** | | **~US$ 0.60** | **~US$ 20.25** |

---

## S2.5 Version control and reproducibility

### Model version pinning

At the time of each API call, the exact model version string (including date tag where applicable) is captured in the response metadata (`llm_clients.py` `LLMResponse` dataclass, field `model_version`). For open-weight models, the SHA-256 hash of the model weights is recorded via `ollama list --verbose` or equivalent.

### Known vendor-side deprecation risks

- **Closed-source (Tiers D, E, R):** Anthropic, OpenAI, and Google routinely deprecate model versions on 6-12 month timelines. Study results published in *Patterns* after 6 months may not be reproducible on these models if snapshotted versions are removed. This is documented as an inherent limitation of closed-frontier auditing.
- **Open-weight (Tiers A, B, C):** Immutable once pulled. Weights archived in `data/model_checkpoints/` (gitignored by size) with SHA-256 in `data/model_checkpoints/HASHES.md`. Hugging Face repository URLs also pinned.

### Compute environment reproducibility

- **Local models (Ollama):** Apple M4 24GB unified memory, macOS 14.6. Ollama v0.15.5+ (updated during Phase 1 setup). Temperature 0.3, seed 42 where supported.
- **API models:** Temperature 0.3, max_tokens 800. No vendor-side seed guarantees but multiple replications (2) per call quantifies residual stochasticity.

---

## S2.6 Reference list (S2)

- Meta AI (2025). *The Llama 4 Herd: Multimodal and Multilingual Open-Weight Frontier Models*. [Technical report].
- Qwen Team (2025). *Qwen 3 Technical Report*. Alibaba Cloud.
- DeepSeek AI (2024). *DeepSeek-V3 Technical Report*. arXiv:2412.19437.
- Mistral AI (2024). *Mixtral of Experts*. arXiv:2401.04088.
- Cohere (2024). *Command R+: A Scalable Production-Ready Generative Model*. [Model card].
- Google DeepMind (2025). *Gemma 3 Technical Report*.
- Microsoft Research (2024). *Phi-4 Technical Report*. arXiv:2412.08905.
- Pires, R., Malaquias Filho, H., Garcia, M., et al. (2024). Sabiá: Portuguese Large Language Models. *STIL 2024 Proceedings* (reference for family; Lince-Mistral is community adaptation of Mistral 7B to PT-BR).
- Anthropic (2025). *Claude 4 Family Model Card: Opus 4.7 and Haiku 4.5*.
- OpenAI (2025). *GPT-5 System Card*.
- Liu, Y., et al. (2023). G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment. *EMNLP 2023*.
- Moayeri, M., et al. (2024). WorldBench: Quantifying Geographic Disparities in LLM Factual Recall. *FAccT 2024*.
