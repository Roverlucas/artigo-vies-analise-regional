"""
config.py — Central experiment configuration (v3.3).

Defines all fixed parameters of the benchmark: countries, languages, models,
domains, tasks. Single source of truth; every script imports from here.

v3.3 changes vs v1/v2:
- LLMS tuple expanded to 14 models across 5 tiers (Tier A-E) + reserve
- Added tier taxonomy: open-weight frontier/mid/small + closed accessible/frontier
- Added execution_venue to indicate API provider or local Ollama
- n_replicates_per_call reduced from 5 to 3 to fit budget-conscious scope
- n_prompts_per_country_domain_task = 2 maintained (~450 prompts ~ 600 with language expansion)

Stratification follows the theoretical triangulation documented in
docs/etapa2b_selecao_paises.md (UNCTAD × Joshi × World Bank).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


# =========================================================================
# COUNTRIES — 15 stratified selection (unchanged from v1)
# =========================================================================

Continent = Literal["LatAm", "Africa", "AsiaSouth", "GlobalNorth"]
IncomeGroup = Literal["low", "lower_middle", "upper_middle", "high"]
UnctadGroup = Literal["south", "north"]


@dataclass(frozen=True)
class Country:
    iso3: str
    name: str
    continent: Continent
    unctad: UnctadGroup
    income: IncomeGroup
    joshi_class_primary: int
    test_languages: tuple[str, ...]
    official_langs: tuple[str, ...]


COUNTRIES: tuple[Country, ...] = (
    Country("BRA", "Brazil",         "LatAm",       "south", "upper_middle", 3, ("en", "pt"), ("pt",)),
    Country("MEX", "Mexico",         "LatAm",       "south", "upper_middle", 4, ("en", "es"), ("es",)),
    Country("ARG", "Argentina",      "LatAm",       "south", "upper_middle", 4, ("en", "es"), ("es",)),
    Country("PER", "Peru",           "LatAm",       "south", "upper_middle", 4, ("en", "es"), ("es", "qu")),
    Country("NGA", "Nigeria",        "Africa",      "south", "lower_middle", 1, ("en",),      ("en",)),
    Country("ZAF", "South Africa",   "Africa",      "south", "upper_middle", 1, ("en",),      ("en", "zu", "xh")),
    Country("KEN", "Kenya",          "Africa",      "south", "lower_middle", 1, ("en", "sw"), ("en", "sw")),
    Country("EGY", "Egypt",          "Africa",      "south", "lower_middle", 4, ("en", "ar"), ("ar",)),
    Country("IND", "India",          "AsiaSouth",   "south", "lower_middle", 4, ("en", "hi"), ("en", "hi")),
    Country("IDN", "Indonesia",      "AsiaSouth",   "south", "upper_middle", 3, ("en", "id"), ("id",)),
    Country("BGD", "Bangladesh",     "AsiaSouth",   "south", "lower_middle", 3, ("en", "bn"), ("bn",)),
    Country("PHL", "Philippines",    "AsiaSouth",   "south", "lower_middle", 2, ("en",),      ("en", "tl")),
    Country("USA", "United States",  "GlobalNorth", "north", "high",         5, ("en",),      ("en",)),
    Country("DEU", "Germany",        "GlobalNorth", "north", "high",         4, ("en", "de"), ("de",)),
    Country("JPN", "Japan",          "GlobalNorth", "north", "high",         4, ("en", "ja"), ("ja",)),
)

assert len(COUNTRIES) == 15
assert sum(1 for c in COUNTRIES if c.unctad == "south") == 12
assert sum(1 for c in COUNTRIES if c.unctad == "north") == 3


# =========================================================================
# LLMS — 14 models in 5 tiers (v3.3 Full-Spectrum Audit)
# =========================================================================

ModelTier = Literal[
    "A_open_frontier",      # 70B+ open-weight (Llama 4, Qwen 3 72B, DeepSeek V3, Mixtral, Command R+)
    "B_open_mid",           # 14-30B open-weight (Gemma 3 27B, Qwen 3 14B, Phi-4)
    "C_open_small",         # 7-8B open-weight (Llama 4 8B, Lince-Mistral 7B)
    "D_closed_accessible",  # Closed accessible tier (Gemini Flash, GPT-5-mini)
    "E_closed_frontier",    # Closed frontier SOTA (GPT-5)
    "reserve",              # Not executed unless reviewer requests (Opus 4.7)
]

ExecutionVenue = Literal[
    "groq_free",
    "openrouter_free",
    "deepinfra_free",
    "cohere_trial",
    "deepseek_paid",
    "gemini_free",
    "openai_paid",
    "anthropic_paid",
    "ollama_local",
]

OpenWeight = Literal["open", "closed"]


@dataclass(frozen=True)
class LLM:
    id: str
    tier: ModelTier
    venue: ExecutionVenue
    openness: OpenWeight
    vendor: str
    api_model_string: str
    est_params_b: float
    full_scope: bool  # True if run on full 15 x 30 x 3; False for reserve/subset
    notes: str


LLMS: tuple[LLM, ...] = (
    # -----------------------------------------------------------------
    # Tier A — Open-weight frontier (5 models, full scope)
    # -----------------------------------------------------------------
    LLM("llama4_70b",    "A_open_frontier", "groq_free",        "open", "meta",
        "llama-4-70b-instruct", 70.0, True,
        "Open frontier; multilingual pretraining"),
    LLM("qwen3_72b",     "A_open_frontier", "openrouter_free",  "open", "alibaba",
        "qwen/qwen3-72b-instruct", 72.0, True,
        "Open frontier; strong multilingual especially low-resource Asian"),
    LLM("deepseek_v3",   "A_open_frontier", "deepseek_paid",    "open", "deepseek",
        "deepseek-chat", 671.0, True,
        "Open-weight MoE frontier SOTA; mixed EN/CN training"),
    LLM("mixtral_8x22b", "A_open_frontier", "groq_free",        "open", "mistral",
        "mixtral-8x22b-instruct", 141.0, True,
        "Open frontier EU; multilingual European focus"),
    LLM("command_rp",    "A_open_frontier", "cohere_trial",     "open", "cohere",
        "command-r-plus-08-2024", 104.0, True,
        "Open frontier; RAG-tuned + explicitly multilingual"),

    # -----------------------------------------------------------------
    # Tier B — Open-weight mid (3 models, full scope)
    # -----------------------------------------------------------------
    LLM("gemma3_27b",    "B_open_mid",      "groq_free",        "open", "google",
        "gemma-3-27b-it", 27.0, True,
        "Open mid-tier; multilingual"),
    LLM("qwen3_14b",     "B_open_mid",      "ollama_local",     "open", "alibaba",
        "qwen3:14b", 14.0, True,
        "Local Ollama M4; multilingual strong"),
    LLM("phi4_14b",      "B_open_mid",      "ollama_local",     "open", "microsoft",
        "phi4:14b", 14.0, True,
        "Local Ollama M4; heavy English pretraining (control for multilingual effects)"),

    # -----------------------------------------------------------------
    # Tier C — Open-weight small/regional (2 models, full scope)
    # -----------------------------------------------------------------
    LLM("llama4_8b",     "C_open_small",    "ollama_local",     "open", "meta",
        "llama4:8b", 8.0, True,
        "Local Ollama M4; accessibility floor"),
    LLM("lince_mistral", "C_open_small",    "ollama_local",     "open", "pucrs",
        "lince-mistral-7b", 7.0, True,
        "Local Ollama M4; BR-PT tuned open — H3 regional hypothesis"),

    # -----------------------------------------------------------------
    # Tier D — Closed accessible (3 models, full scope)
    # -----------------------------------------------------------------
    LLM("claude_haiku",  "D_closed_accessible", "anthropic_paid", "closed", "anthropic",
        "claude-haiku-4-5", 0.0, True,
        "Anthropic closed accessible tier; paid via US$ 10 budget"),
    LLM("gemini_flash",  "D_closed_accessible", "gemini_free",   "closed", "google",
        "gemini-2.5-flash", 0.0, True,
        "Google closed accessible tier; free API"),
    LLM("gpt5_mini",     "D_closed_accessible", "openai_paid",   "closed", "openai",
        "gpt-5-mini", 0.0, True,
        "OpenAI closed accessible tier; paid via US$ 15 budget"),

    # -----------------------------------------------------------------
    # Tier E — Closed frontier SOTA (1 model, full scope)
    # -----------------------------------------------------------------
    LLM("gpt5",          "E_closed_frontier",   "openai_paid",   "closed", "openai",
        "gpt-5", 0.0, True,
        "OpenAI 2026 SOTA; frontier closed; paid via US$ 15 budget"),

    # -----------------------------------------------------------------
    # RESERVE — not executed unless reviewer requests
    # -----------------------------------------------------------------
    LLM("claude_opus",   "reserve",             "anthropic_paid", "closed", "anthropic",
        "claude-opus-4-7", 0.0, False,
        "Reserve ~US$ 10 Anthropic — activate ONLY if reviewer requests multi-vendor closed frontier"),
)

assert len(LLMS) == 15
assert sum(1 for m in LLMS if m.full_scope) == 14
assert sum(1 for m in LLMS if m.openness == "open") == 10


# =========================================================================
# DOMAINS AND TASKS (unchanged)
# =========================================================================

@dataclass(frozen=True)
class Domain:
    id: str
    label_en: str
    label_pt: str


DOMAINS: tuple[Domain, ...] = (
    Domain("D1", "Public policy and institutions",   "Políticas públicas e instituições"),
    Domain("D2", "Socioeconomic reality",            "Realidade socioeconômica"),
    Domain("D3", "Regional environmental context",   "Contexto ambiental regional"),
)


@dataclass(frozen=True)
class TaskType:
    id: str
    label: str
    format: Literal["closed_factual", "open_generation", "list_extraction", "source_recommendation", "calibration"]
    eval_method: Literal["ground_truth_match", "rubric_score", "rubric_score_citations", "brier"]
    output_length: str


TASKS: tuple[TaskType, ...] = (
    TaskType("T1", "Direct factual recall",         "closed_factual",         "ground_truth_match",       "short (1-3 sentences)"),
    TaskType("T2", "Contextual characterization",   "open_generation",        "rubric_score",             "medium (100-300 words)"),
    TaskType("T3", "Stakeholder identification",    "list_extraction",        "rubric_score",             "list (5-10 items)"),
    TaskType("T4", "Primary-source recommendation", "source_recommendation",  "rubric_score_citations",   "list with URLs"),
    TaskType("T5", "Confidence calibration",        "calibration",            "brier",                    "numeric + short rationale"),
)


# =========================================================================
# EXPERIMENT PARAMETERS (v3.3)
# =========================================================================

@dataclass(frozen=True)
class ExperimentConfig:
    n_prompts_per_country_domain_task: int = 2
    n_replicates_per_call: int = 2              # v3.3: reduced from 5 (v1) to 2 to fit US$15 OpenAI budget while keeping 780-prompt multilingual matrix
    temperature: float = 0.3
    max_tokens_response: int = 800
    api_timeout_seconds: int = 60
    max_retries: int = 3
    retry_backoff_seconds: tuple[int, ...] = (2, 5, 15)
    random_seed: int = 42

    def total_prompts(self) -> int:
        avg_langs = sum(len(c.test_languages) for c in COUNTRIES) / len(COUNTRIES)
        return int(
            len(COUNTRIES) *
            len(DOMAINS) *
            len(TASKS) *
            avg_langs *
            self.n_prompts_per_country_domain_task
        )

    def total_api_calls_full_scope(self) -> int:
        full_scope_models = sum(1 for m in LLMS if m.full_scope)
        return self.total_prompts() * full_scope_models * self.n_replicates_per_call


EXPERIMENT = ExperimentConfig()


# =========================================================================
# BUDGET TRACKING (v3.3)
# =========================================================================

@dataclass(frozen=True)
class BudgetEntry:
    source: str
    allocated_usd: float
    planned_usage_usd: float
    reserve_usd: float
    purpose: str


BUDGET: tuple[BudgetEntry, ...] = (
    BudgetEntry("OpenAI",    15.00, 12.83, 2.17,  "GPT-5 full + GPT-5-mini full (Tier D + E)"),
    BudgetEntry("Anthropic", 10.00,  0.00, 10.00, "RESERVE — Opus subset if reviewer requests"),
    BudgetEntry("DeepSeek",   1.99,  1.19, 0.80,  "DeepSeek-V3 full scope (Tier A)"),
    BudgetEntry("Cash_BRL_to_USD", 38.50, 0.00, 38.50, "R$ 200 cash reserve — untouched by default"),
)


# =========================================================================
# OUTCOME RUBRIC WEIGHTS (pre-registered — unchanged)
# =========================================================================

RUBRIC_WEIGHTS: dict[str, float] = {
    "factual_accuracy":         0.30,
    "contextual_completeness":  0.25,
    "citation_quality":         0.15,
    "calibration":              0.15,
    "absence_of_hallucination": 0.15,
}
assert abs(sum(RUBRIC_WEIGHTS.values()) - 1.0) < 1e-9


# =========================================================================
# CROSS-SCRIPT PATHS
# =========================================================================

from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_GROUND_TRUTH = ROOT / "data" / "ground_truth"
DATA_PILOT = ROOT / "data" / "pilot_202604"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"
TABLES_DIR = ROOT / "tables"


if __name__ == "__main__":
    print(f"Countries: {len(COUNTRIES)} ({sum(1 for c in COUNTRIES if c.unctad == 'south')} South, "
          f"{sum(1 for c in COUNTRIES if c.unctad == 'north')} North)")
    print(f"Models (total):      {len(LLMS)}")
    print(f"  full scope:        {sum(1 for m in LLMS if m.full_scope)}")
    print(f"  reserve:           {sum(1 for m in LLMS if m.tier == 'reserve')}")
    print(f"  open-weight:       {sum(1 for m in LLMS if m.openness == 'open')}")
    print(f"  closed:            {sum(1 for m in LLMS if m.openness == 'closed')}")
    print(f"Domains:            {len(DOMAINS)}")
    print(f"Tasks:              {len(TASKS)}")
    print(f"Estimated total prompts:           {EXPERIMENT.total_prompts():,}")
    print(f"Estimated total API calls (v3.3):  {EXPERIMENT.total_api_calls_full_scope():,}")
    print()
    print("Budget summary:")
    for b in BUDGET:
        print(f"  {b.source:20s} planned ${b.planned_usage_usd:>6.2f} / reserve ${b.reserve_usd:>6.2f}")
