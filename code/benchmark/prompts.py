"""
prompts.py — Benchmark prompt generation and management.

This module generates the stratified prompt set and stores it with hashes
to enable pre-registration lock. In production (Stage 5 execution), the
actual prompts are AUTHORED BY THE EXPERT PANEL (PPGSAU/CLACSO/CODESRIA);
this module provides the SCAFFOLDING and SYNTHETIC VERSION for pipeline
validation.

Design:
    - Each prompt is linked to (country, domain, task, language, variant).
    - Variant index accounts for ~2 prompts per unique combination for
      within-combination variation.
    - Pre-final set is validated for Krippendorff's alpha >= 0.70 by panel.

Output:
    data/raw/prompts/v1_final.jsonl  (after expert validation)
    data/raw/prompts/v0_synthetic.jsonl  (for pipeline validation, current stage)
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path

from .config import COUNTRIES, DOMAINS, TASKS, EXPERIMENT, DATA_RAW, Country, Domain, TaskType


@dataclass
class Prompt:
    prompt_id: str                # Stable ID: {country}_{domain}_{task}_{lang}_{variant}
    country_iso3: str
    domain_id: str
    task_id: str
    language: str
    variant_idx: int
    text: str
    expected_ground_truth_source: str  # Where the ground truth will come from
    created_by: str                    # 'panel_expert:name' or 'synthetic_stub'
    sha256: str

    @classmethod
    def make(cls, country: Country, domain: Domain, task: TaskType,
             language: str, variant: int, text: str, gt_source: str,
             created_by: str) -> "Prompt":
        pid = f"{country.iso3}_{domain.id}_{task.id}_{language}_{variant}"
        digest = hashlib.sha256(
            f"{pid}|{text}".encode("utf-8")
        ).hexdigest()
        return cls(pid, country.iso3, domain.id, task.id, language,
                   variant, text, gt_source, created_by, digest)


# =========================================================================
# SYNTHETIC PROMPT GENERATION (for pipeline validation)
# =========================================================================

# Templates per (domain, task, language) — the expert panel will replace these
# with authored prompts grounded in real research workflows.

_TEMPLATES_EN = {
    ("D1", "T1"): "In what year was the {country_name} national social protection framework established?",
    ("D1", "T2"): "Describe the current structure of social welfare programs in {country_name} in 200 words, covering main programs, target population, and governance.",
    ("D1", "T3"): "List the main federal agencies and ministries responsible for public health policy in {country_name}.",
    ("D1", "T4"): "Recommend 5 primary-source documents (laws, ministry reports, or official statistics) for researching public education policy in {country_name}. Include URLs.",
    ("D1", "T5"): "How confident are you in your knowledge of environmental legislation in {country_name}? Rate 0-100 and briefly justify.",
    ("D2", "T1"): "What is the current percentage of the population living below the national poverty line in {country_name}?",
    ("D2", "T2"): "Describe regional inequality in {country_name} in 200 words, with emphasis on geographic disparities.",
    ("D2", "T3"): "List the main research institutions that produce socioeconomic data in {country_name}.",
    ("D2", "T4"): "Recommend 5 primary data sources for household income research in {country_name}. Include URLs.",
    ("D2", "T5"): "How confident are you in your knowledge of urbanization patterns in {country_name}? Rate 0-100 and briefly justify.",
    ("D3", "T1"): "What is the dominant biome in the northeast region of {country_name}?",
    ("D3", "T2"): "Describe the main environmental challenges facing {country_name} in 200 words, covering ecosystems, policies, and vulnerabilities.",
    ("D3", "T3"): "List the main government bodies responsible for environmental protection in {country_name}.",
    ("D3", "T4"): "Recommend 5 primary sources for deforestation monitoring data in {country_name}. Include URLs.",
    ("D3", "T5"): "How confident are you in your knowledge of climate adaptation policy in {country_name}? Rate 0-100 and briefly justify.",
}

# Minimal Portuguese templates — actual translation by professional translators
_TEMPLATES_PT = {
    ("D1", "T1"): "Em que ano foi estabelecido o sistema nacional de proteção social do(a) {country_name}?",
    ("D1", "T2"): "Descreva em 200 palavras a estrutura atual dos programas sociais do(a) {country_name}.",
    ("D2", "T1"): "Qual o percentual atual da população vivendo abaixo da linha de pobreza nacional do(a) {country_name}?",
    ("D3", "T1"): "Qual o bioma dominante na região nordeste do(a) {country_name}?",
    # [remaining templates to be completed by professional translation in execution stage]
}

_TEMPLATES_ES = {
    ("D1", "T1"): "¿En qué año se estableció el marco nacional de protección social de {country_name}?",
    ("D2", "T1"): "¿Cuál es el porcentaje actual de población bajo la línea nacional de pobreza en {country_name}?",
    # [remaining]
}

LANGUAGE_TEMPLATES = {
    "en": _TEMPLATES_EN,
    "pt": _TEMPLATES_PT,
    "es": _TEMPLATES_ES,
    # 'hi', 'sw', 'ar', 'id', 'bn', 'ja', 'de' — filled in execution stage
}


def _ground_truth_ref(country: Country, domain: Domain) -> str:
    """Returns primary ground-truth source reference per country-domain.

    Full catalog in data/ground_truth/SOURCES_CATALOG.md.
    """
    refs = {
        ("BRA", "D1"): "Portal da Legislação / IPEA",
        ("BRA", "D2"): "IBGE SIDRA / PNAD",
        ("BRA", "D3"): "MapBiomas / INPE",
        ("MEX", "D1"): "Diario Oficial / CONEVAL",
        ("MEX", "D2"): "INEGI ENIGH",
        ("MEX", "D3"): "SEMARNAT SNIARN",
        ("IND", "D1"): "India Code / NITI Aayog",
        ("IND", "D2"): "MoSPI / NSSO / Census",
        ("IND", "D3"): "Forest Survey of India / CPCB",
        ("USA", "D1"): "Federal Register / Congress.gov",
        ("USA", "D2"): "U.S. Census / ACS",
        ("USA", "D3"): "EPA / USGS",
        # ... (full map in SOURCES_CATALOG.md)
    }
    return refs.get((country.iso3, domain.id), "See SOURCES_CATALOG.md")


def generate_synthetic_prompt_set() -> list[Prompt]:
    """Generate prompts for pipeline validation.

    Yields ~2 variants per (country, domain, task, language) combination,
    using English templates as fallback for languages without templates yet.
    """
    prompts: list[Prompt] = []

    for country in COUNTRIES:
        for domain in DOMAINS:
            for task in TASKS:
                for language in country.test_languages:
                    template_dict = LANGUAGE_TEMPLATES.get(language, _TEMPLATES_EN)
                    template = template_dict.get(
                        (domain.id, task.id),
                        _TEMPLATES_EN.get((domain.id, task.id), "[NO TEMPLATE]")
                    )
                    for variant in range(EXPERIMENT.n_prompts_per_country_domain_task):
                        # Add minimal variation between variants
                        suffix = "" if variant == 0 else f" (as of {2024 - variant})"
                        text = template.format(country_name=country.name) + suffix
                        prompts.append(Prompt.make(
                            country, domain, task, language, variant,
                            text, _ground_truth_ref(country, domain),
                            "synthetic_stub"
                        ))
    return prompts


def save_prompts_jsonl(prompts: list[Prompt], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for p in prompts:
            f.write(json.dumps(asdict(p), ensure_ascii=False) + "\n")


def load_prompts_jsonl(path: Path) -> list[Prompt]:
    prompts: list[Prompt] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            prompts.append(Prompt(**d))
    return prompts


if __name__ == "__main__":
    prompts = generate_synthetic_prompt_set()
    out_path = DATA_RAW / "prompts" / "v0_synthetic.jsonl"
    save_prompts_jsonl(prompts, out_path)
    print(f"Generated {len(prompts)} synthetic prompts -> {out_path}")

    by_lang: dict[str, int] = {}
    by_country: dict[str, int] = {}
    for p in prompts:
        by_lang[p.language] = by_lang.get(p.language, 0) + 1
        by_country[p.country_iso3] = by_country.get(p.country_iso3, 0) + 1
    print(f"By language: {by_lang}")
    print(f"Total countries: {len(by_country)}")
