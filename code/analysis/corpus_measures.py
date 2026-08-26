"""
corpus_measures.py — Literature-grounded corpus-representation measures.

Two conceptually distinct families of measure, mapped to the two hypotheses
they can address:

(A) LANGUAGE-corpus measures — size of the web/pretraining corpus IN a given
    language. Relevant to H2 (native-language penalty): a model may answer
    worse in a language because that language is under-represented in training.
    Sources (all official/peer-reviewed, quoted verbatim):
      - mC4 tokens (B) & mT5 sampling % : Xue et al. 2021, NAACL, Table 6
        "mT5: A Massively Multilingual Pre-trained Text-to-Text Transformer"
        https://aclanthology.org/2021.naacl-main.41/
      - OSCAR-2301 size (GB) & words (B) : dataset card do OSCAR-2301.
        ATENCAO: sao os totais da versao ORIGINAL do card, nao da deduplicada, e nao
        coincidem com o paper LREC de Abadji et al. 2022, que descreve o OSCAR 22.01
        (espanhol 381,9 GB ali contra 429,9 GB aqui). Conferido em 2026-08-26.
        "Towards a Cleaner Document-Oriented Multilingual Crawled Corpus";
        figures from the official oscar-corpus/OSCAR-2301 dataset card.
      - Joshi linguistic-resource class (0-5) : Joshi et al. 2020, ACL
        "The State and Fate of Linguistic Diversity and Inclusion in the NLP World"

(B) COUNTRY-corpus measures — how much the web/encyclopedic corpus is ABOUT a
    given country (geo-entity coverage), independent of language. Relevant to
    H1/H4 (geographic gap measured IN ENGLISH): because every country is queried
    in the same language (English), a residual North/South gap cannot be a
    language-corpus effect; the candidate mechanism is country representation.
    Sources:
      - Wikipedia articles about the country (Wikidata sitelinks / pageviews)
      - (socioeconomic covariates HDI, GDP handled in formal_tests COV)

This module only stores the VERIFIED measures and exposes helpers; the
statistics are run in formal_tests.py.
"""
from __future__ import annotations

# (A) LANGUAGE-corpus measures, keyed by ISO 639-1.
# mc4_tokens_b, mc4_pages_m, mt5_pct : Xue et al. 2021 Table 6 (verbatim).
# oscar_gb, oscar_words_b : OSCAR-2301 dataset card, versao ORIGINAL (verbatim).
# joshi : Joshi et al. 2020 resource class.
LANG_CORPUS = {
    "en": {"mc4_tokens_b": 2733.0, "mc4_pages_m": 3067.0, "mt5_pct": 5.67,
           "oscar_gb": 3400.0, "oscar_words_b": 523.9, "joshi": 5},
    "es": {"mc4_tokens_b": 433.0,  "mc4_pages_m": 416.0,  "mt5_pct": 3.09,
           "oscar_gb": 429.9, "oscar_words_b": 63.4,  "joshi": 5},
    "fr": {"mc4_tokens_b": 318.0,  "mc4_pages_m": 333.0,  "mt5_pct": 2.89,
           "oscar_gb": 430.5, "oscar_words_b": 62.1,  "joshi": 5},
    "it": {"mc4_tokens_b": 162.0,  "mc4_pages_m": 186.0,  "mt5_pct": 2.43,
           "oscar_gb": 259.4, "oscar_words_b": 36.3,  "joshi": 4},
    "pt": {"mc4_tokens_b": 146.0,  "mc4_pages_m": 169.0,  "mt5_pct": 2.36,
           "oscar_gb": 105.0, "oscar_words_b": 15.2,  "joshi": 4},
    "ko": {"mc4_tokens_b": 26.0,   "mc4_pages_m": 16.0,   "mt5_pct": 1.14,
           "oscar_gb": 38.1,  "oscar_words_b": 3.4,   "joshi": 4},
    "hi": {"mc4_tokens_b": 24.0,   "mc4_pages_m": 19.0,   "mt5_pct": 1.21,
           "oscar_gb": 32.6,  "oscar_words_b": 2.5,   "joshi": 4},
}

# Citations for the language-corpus measures (for the paper's methods/refs).
LANG_CORPUS_SOURCES = {
    "mc4_tokens_b": "Xue et al. 2021 (NAACL), mC4 Table 6 — tokens in billions",
    "mc4_pages_m":  "Xue et al. 2021 (NAACL), mC4 Table 6 — pages in millions",
    "mt5_pct":      "Xue et al. 2021 (NAACL), mC4 Table 6 — mT5 sampling % (alpha=0.3)",
    "oscar_gb":     "Abadji et al. 2022 (LREC); OSCAR-2301 card — dedup size GB",
    "oscar_words_b":"Abadji et al. 2022 (LREC); OSCAR-2301 card — dedup words (B)",
    "joshi":        "Joshi et al. 2020 (ACL) — linguistic-resource class 0-5",
}

# Native language per native-pair country (ISO3 -> ISO639-1).
NATIVE_LANG = {
    "BRA": "pt", "PRT": "pt", "AGO": "pt",
    "MEX": "es", "ARG": "es", "PER": "es", "COL": "es", "CHL": "es",
    "IND": "hi",
}


def lang_measure(iso2: str, key: str):
    """Return one language-corpus measure, or None if unknown."""
    return LANG_CORPUS.get(iso2, {}).get(key)


def native_lang_measures(iso3: str):
    """All language-corpus measures for a country's native language."""
    l = NATIVE_LANG.get(iso3)
    return LANG_CORPUS.get(l) if l else None


if __name__ == "__main__":
    print("Language-corpus measures (verbatim from literature):")
    hdr = ["lang", "mc4_tok_B", "mt5_%", "oscar_GB", "joshi"]
    print("  " + "  ".join(f"{h:>9}" for h in hdr))
    for l, m in LANG_CORPUS.items():
        print("  " + "  ".join(f"{str(x):>9}" for x in
              [l, m["mc4_tokens_b"], m["mt5_pct"], m["oscar_gb"], m["joshi"]]))
    print("\nSources:")
    for k, v in LANG_CORPUS_SOURCES.items():
        print(f"  {k}: {v}")
