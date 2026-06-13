"""
h4_corpus_mechanism.py — Corpus-representation mechanism, multi-measure (H4).

Two separable mechanisms, each with literature-grounded measures:

H4a (geographic gap, measured IN ENGLISH): does country accuracy track how much
    the corpus is ABOUT the country? Country-corpus measures (language-independent):
      en_wiki_bytes, wd_sitelinks, wd_statements  [Wikimedia/Wikidata]
    Spearman(accuracy, measure) and PARTIAL Spearman controlling HDI.

H4b (native-language penalty): does the per-language penalty track how much
    corpus exists IN that language? Language-corpus measures:
      mc4_tokens_b [Xue 2021], oscar_gb [Abadji 2022], joshi [Joshi 2020]
    Descriptive (n=3 native languages: es, pt, hi) — reported as mechanism, not test.

Because H1's gap is measured in English (language held constant), it cannot be a
language-corpus effect; H4a isolates the country-representation channel, H4b the
language channel for H2. Run now (15 countries) and re-run after the 25-country
collection completes.

Usage:  python -m code.analysis.h4_corpus_mechanism
"""
from __future__ import annotations
import json, math
from pathlib import Path
from code.analysis.formal_tests import spearman, partial_spearman, p_from_r, COV
from code.analysis.corpus_measures import LANG_CORPUS, NATIVE_LANG

A = Path(__file__).parent.parent.parent / "data" / "confirmatory_PRIVATE" / "analysis"
SCORES = A / "judge_scores_confirmatory.jsonl"
CCORP = A / "country_corpus_measures.json"

# HDI extension for the 10 new countries (UNDP HDR 2023-24, 2022 data).
# Same official source as the original COV; values to be cross-checked vs the UNDP xlsx.
HDI_EXT = {"UK": 0.940, "CAN": 0.935, "AUS": 0.946, "KOR": 0.929, "FRA": 0.910,
           "ITA": 0.906, "COL": 0.758, "CHL": 0.860, "PRT": 0.874, "AGO": 0.591}


def hdi(iso):
    if iso in COV:
        return COV[iso][0]
    return HDI_EXT.get(iso)


def load_english_accuracy():
    rows = [json.loads(l) for l in open(SCORES) if l.strip()]
    rows = [r for r in rows if 'composite' in r and not r.get('error')
            and 'JUDGE_API_ERROR' not in str(r.get('rationale', ''))]
    eng = [r for r in rows if '_AP_' in (r.get('prompt_id') or '')
           and not (r.get('prompt_id') or '').endswith(('_pt', '_es', '_hi'))]
    acc = {}
    for r in eng:
        acc.setdefault(r.get('country_iso3'), []).append(r['composite'])
    return {c: sum(v) / len(v) for c, v in acc.items() if v}


def load_native_penalty():
    """Per native-language penalty = mean(accuracy_en - accuracy_native) over paired prompts."""
    rows = [json.loads(l) for l in open(SCORES) if l.strip()]
    rows = [r for r in rows if 'composite' in r and not r.get('error')]
    by_id = {}
    for r in rows:
        by_id.setdefault(r.get('prompt_id'), []).append(r['composite'])
    mean = {k: sum(v) / len(v) for k, v in by_id.items() if v}
    # pair English base id with its native suffix
    penalties = {}  # lang -> list of (en - native)
    for pid, m in mean.items():
        for suf, lang in (('_pt', 'pt'), ('_es', 'es'), ('_hi', 'hi')):
            if pid.endswith(suf):
                base = pid[:-len(suf)]
                if base in mean:
                    penalties.setdefault(lang, []).append(mean[base] - m)
    return {l: sum(v) / len(v) for l, v in penalties.items() if v}


def corr_block(label, acc, measure_of, control_hdi=True):
    pts = [(c, acc[c], measure_of(c)) for c in acc if measure_of(c) is not None]
    pts = [(c, a, m) for c, a, m in pts if m and m > 0]
    if len(pts) < 4:
        print(f"  {label}: n={len(pts)} (insufficient)"); return
    A_ = [a for _, a, _ in pts]; M = [math.log(m) for _, _, m in pts]
    n = len(pts)
    r = spearman(A_, M); p = p_from_r(r, n)
    line = f"  {label}: n={n}  Spearman(acc, log measure)={r:+.3f} (p={p:.3f})"
    if control_hdi:
        H = [hdi(c) for c, _, _ in pts]
        if all(h is not None for h in H):
            pr = partial_spearman(A_, M, H); ppr = p_from_r(pr, n, partial=1)
            line += f"  | PARTIAL|HDI={pr:+.3f} (p={ppr:.3f})"
    print(line)


def main():
    acc = load_english_accuracy()
    print(f"H4a — COUNTRY-corpus mechanism (accuracy in English, n_countries={len(acc)})")
    if CCORP.exists():
        cc = json.loads(CCORP.read_text())
        for key in ("en_wiki_bytes", "wd_sitelinks", "wd_statements"):
            corr_block(f"H4a/{key:14s}", acc,
                       lambda c, k=key: (cc.get(c) or {}).get(k))
    else:
        print("  (country_corpus_measures.json not ready yet)")

    print(f"\nH4b — LANGUAGE-corpus mechanism (native-language penalty)")
    pen = load_native_penalty()
    if pen:
        print(f"  per-language penalty (en - native), positive = native worse:")
        for lang in ("es", "pt", "hi"):
            if lang in pen:
                lc = LANG_CORPUS.get(lang, {})
                print(f"    {lang}: penalty={pen[lang]*100:+.1f}pp | "
                      f"mc4={lc.get('mc4_tokens_b')}B oscar={lc.get('oscar_gb')}GB "
                      f"joshi={lc.get('joshi')}")
        # descriptive rank-direction across the 3 languages
        langs = [l for l in pen if l in LANG_CORPUS]
        if len(langs) >= 3:
            P = [pen[l] for l in langs]
            for key in ("mc4_tokens_b", "oscar_gb"):
                Mv = [LANG_CORPUS[l][key] for l in langs]
                r = spearman(P, [math.log(m) for m in Mv])
                print(f"    Spearman(penalty, log {key}) over {len(langs)} langs = {r:+.3f} "
                      f"(descriptive; n={len(langs)})")
    else:
        print("  (no native-language pairs scored yet)")


if __name__ == "__main__":
    main()
