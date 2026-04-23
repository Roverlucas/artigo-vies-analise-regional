"""
config.py — Central experiment configuration.

Defines all fixed parameters of the benchmark: countries, languages, models,
domains, tasks. Single source of truth; every script imports from here.

Stratification follows the theoretical triangulation documented in
docs/etapa2b_selecao_paises.md (UNCTAD × Joshi × World Bank).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


# =========================================================================
# COUNTRIES — 15 stratified selection (see docs/etapa2b_selecao_paises.md)
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
    # Joshi et al. (2020) class of the primary administrative language
    joshi_class_primary: int
    # Languages to test with this country
    test_languages: tuple[str, ...]
    # ISO 639-1 codes of official/dominant languages
    official_langs: tuple[str, ...]


COUNTRIES: tuple[Country, ...] = (
    # Latin America
    Country("BRA", "Brazil",         "LatAm",       "south", "upper_middle", 3, ("en", "pt"), ("pt",)),
    Country("MEX", "Mexico",         "LatAm",       "south", "upper_middle", 4, ("en", "es"), ("es",)),
    Country("ARG", "Argentina",      "LatAm",       "south", "upper_middle", 4, ("en", "es"), ("es",)),
    Country("PER", "Peru",           "LatAm",       "south", "upper_middle", 4, ("en", "es"), ("es", "qu")),
    # Africa
    Country("NGA", "Nigeria",        "Africa",      "south", "lower_middle", 1, ("en",),      ("en",)),
    Country("ZAF", "South Africa",   "Africa",      "south", "upper_middle", 1, ("en",),      ("en", "zu", "xh")),
    Country("KEN", "Kenya",          "Africa",      "south", "lower_middle", 1, ("en", "sw"), ("en", "sw")),
    Country("EGY", "Egypt",          "Africa",      "south", "lower_middle", 4, ("en", "ar"), ("ar",)),
    # Asia (Global South)
    Country("IND", "India",          "AsiaSouth",   "south", "lower_middle", 4, ("en", "hi"), ("en", "hi")),
    Country("IDN", "Indonesia",      "AsiaSouth",   "south", "upper_middle", 3, ("en", "id"), ("id",)),
    Country("BGD", "Bangladesh",     "AsiaSouth",   "south", "lower_middle", 3, ("en", "bn"), ("bn",)),
    Country("PHL", "Philippines",    "AsiaSouth",   "south", "lower_middle", 2, ("en",),      ("en", "tl")),
    # Global North (control)
    Country("USA", "United States",  "GlobalNorth", "north", "high",         5, ("en",),      ("en",)),
    Country("DEU", "Germany",        "GlobalNorth", "north", "high",         4, ("en", "de"), ("de",)),
    Country("JPN", "Japan",          "GlobalNorth", "north", "high",         4, ("en", "ja"), ("ja",)),
)

assert len(COUNTRIES) == 15
assert sum(1 for c in COUNTRIES if c.unctad == "south") == 12
assert sum(1 for c in COUNTRIES if c.unctad == "north") == 3


# =========================================================================
# LLMs — 6 models + 1 scale-matched control
# =========================================================================

ModelCategory = Literal["frontier_proprietary", "open_global", "regional", "scale_control"]


@dataclass(frozen=True)
class LLM:
    id: str                  # internal stable id
    category: ModelCategory
    provider: str
    api_model_string: str    # exact version string passed to API
    est_params_b: float      # estimated parameters in billions (public info)
    notes: str


LLMS: tuple[LLM, ...] = (
    LLM("gpt5",        "frontier_proprietary", "openai",    "gpt-5",              500.0, "Frontier; reasoning by default"),
    LLM("claude_opus", "frontier_proprietary", "anthropic", "claude-opus-4-7",    0.0,   "Frontier; parameter count undisclosed"),
    LLM("gemini_25",   "frontier_proprietary", "google",    "gemini-2.5-pro",     0.0,   "Frontier; parameter count undisclosed"),
    LLM("llama4_70b",  "open_global",          "meta",      "llama-4-70b-instruct", 70.0, "Open weights; global training"),
    LLM("sabia3",      "regional",             "maritaca",  "sabia-3",            65.0,  "Brazilian Portuguese emphasis"),
    LLM("qwen3_32b",   "scale_control",        "alibaba",   "qwen3-32b",          32.0,  "Scale-matched control for Sabiá-3"),
)

assert len(LLMS) == 6


# =========================================================================
# DOMAINS AND TASKS
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
    TaskType("T1", "Direct factual recall",        "closed_factual",         "ground_truth_match",       "short (1-3 sentences)"),
    TaskType("T2", "Contextual characterization",  "open_generation",        "rubric_score",             "medium (100-300 words)"),
    TaskType("T3", "Stakeholder identification",   "list_extraction",        "rubric_score",             "list (5-10 items)"),
    TaskType("T4", "Primary-source recommendation", "source_recommendation", "rubric_score_citations",   "list with URLs"),
    TaskType("T5", "Confidence calibration",       "calibration",            "brier",                    "numeric + short rationale"),
)


# =========================================================================
# EXPERIMENT PARAMETERS
# =========================================================================

@dataclass(frozen=True)
class ExperimentConfig:
    n_prompts_per_country_domain_task: int = 2  # Yields ~450 prompts total
    n_replicates_per_call: int = 5               # For stochastic variability
    temperature: float = 0.3                      # Low for determinism, not zero
    max_tokens_response: int = 800
    api_timeout_seconds: int = 60
    max_retries: int = 3
    retry_backoff_seconds: tuple[int, ...] = (2, 5, 15)
    random_seed: int = 42

    def total_prompts(self) -> int:
        # Average country has ~1.5 languages tested (some only EN, some EN+1)
        avg_langs = sum(len(c.test_languages) for c in COUNTRIES) / len(COUNTRIES)
        return int(
            len(COUNTRIES) *
            len(DOMAINS) *
            len(TASKS) *
            avg_langs *
            self.n_prompts_per_country_domain_task
        )

    def total_api_calls(self) -> int:
        return self.total_prompts() * len(LLMS) * self.n_replicates_per_call


EXPERIMENT = ExperimentConfig()


# =========================================================================
# OUTCOME RUBRIC WEIGHTS (pre-registered in OSF)
# =========================================================================

RUBRIC_WEIGHTS: dict[str, float] = {
    "factual_accuracy":     0.30,   # T1 binary, expanded to partial credit in T2-T4
    "contextual_completeness": 0.25, # T2-T4 open-ended rubric 0-5
    "citation_quality":     0.15,   # T4 primarily; DOI/URL verification
    "calibration":          0.15,   # T5; Brier score inverted to 0-1
    "absence_of_hallucination": 0.15, # Binary, flagged by panel
}
assert abs(sum(RUBRIC_WEIGHTS.values()) - 1.0) < 1e-9


# =========================================================================
# CROSS-SCRIPT PATHS
# =========================================================================

from pathlib import Path

ROOT = Path(__file__).parent.parent.parent  # benchmark/ is at code/benchmark/
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_GROUND_TRUTH = ROOT / "data" / "ground_truth"
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"
TABLES_DIR = ROOT / "tables"


if __name__ == "__main__":
    print(f"Countries: {len(COUNTRIES)} ({sum(1 for c in COUNTRIES if c.unctad == 'south')} South, "
          f"{sum(1 for c in COUNTRIES if c.unctad == 'north')} North)")
    print(f"Models:    {len(LLMS)}")
    print(f"Domains:   {len(DOMAINS)}")
    print(f"Tasks:     {len(TASKS)}")
    print(f"Estimated total prompts:     {EXPERIMENT.total_prompts():,}")
    print(f"Estimated total API calls:   {EXPERIMENT.total_api_calls():,}")
