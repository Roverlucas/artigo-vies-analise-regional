"""
generate_native_prompts.py — Native-language renderings for the 4-language benchmark.

For the 5 countries with a target native language (BRA->pt, MEX/ARG/PER->es,
IND->hi), translate the English v7 prompt_rendered into the native language via a
high-quality translator (Claude Sonnet 4.6), preserving meaning and the
persona frame. Ground truth stays in English (the factual target is
language-invariant); the judge is multilingual.

Output: data/confirmatory_PRIVATE/prompts_native.jsonl
New prompt_id = <orig_id>_<lang> (e.g. BRA_AP_T1_N01_neutral_pt).

Usage:
    python -m code.benchmark.generate_native_prompts
"""
from __future__ import annotations
import json
from pathlib import Path

from code.benchmark.llm_clients import call_llm

ROOT = Path(__file__).parent.parent.parent
BYC = ROOT / "data" / "confirmatory_PRIVATE" / "by_country"
OUT = ROOT / "data" / "confirmatory_PRIVATE" / "prompts_native.jsonl"

# country -> native language code + name for the translator
NATIVE = {
    "BRA": ("pt", "Brazilian Portuguese"),
    "MEX": ("es", "Spanish (Mexican)"),
    "ARG": ("es", "Spanish (Argentine)"),
    "PER": ("es", "Spanish (Peruvian)"),
    "IND": ("hi", "Hindi"),
}

TRANSLATOR = "claude_sonnet"


def translate(text: str, lang_name: str) -> str:
    prompt = (
        f"Translate the following text into {lang_name}. It is a survey question put to a "
        f"language model about national air-pollution policy. Preserve the meaning, the "
        f"register, any role-framing (e.g. 'I am the municipal environmental manager...'), "
        f"technical terms (PM2.5, µg/m³, agency names), and the instruction to answer briefly. "
        f"Keep proper nouns and acronyms as-is. Output ONLY the translation, no preamble.\n\n"
        f"TEXT:\n{text}"
    )
    r = call_llm(TRANSLATOR, prompt, "en")
    return (r.response_text or "").strip()


def main():
    n = 0
    skipped = 0
    with open(OUT, "w", encoding="utf-8") as out:
        for iso, (lang, lang_name) in NATIVE.items():
            fp = BYC / f"{iso}_v7.jsonl"
            if not fp.exists():
                print(f"missing {fp}")
                continue
            for line in open(fp, encoding="utf-8"):
                r = json.loads(line)
                en = r.get("prompt_rendered", "")
                if not en:
                    skipped += 1
                    continue
                native = translate(en, lang_name)
                if not native or "JUDGE_API_ERROR" in native:
                    print(f"  translation failed for {r['prompt_id']} -> {lang}")
                    skipped += 1
                    continue
                rec = dict(r)
                rec["prompt_id"] = f"{r['prompt_id']}_{lang}"
                rec["language"] = lang
                rec["prompt_rendered"] = native
                rec["prompt_rendered_en"] = en  # keep the English source for the H2 pair
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
                if n % 10 == 0:
                    print(f"  translated {n}...")
    print(f"DONE. native prompts written: {n} (skipped {skipped}) -> {OUT.name}")


if __name__ == "__main__":
    main()
