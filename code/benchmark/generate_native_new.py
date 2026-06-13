"""
generate_native_new.py — Native renderings for the 4 NEW native-pair countries.

COL, CHL -> Spanish; PRT, AGO -> Portuguese. Same protocol as
generate_native_prompts.py: translate the English v7 prompt_rendered via Claude
Sonnet, keep ground truth in English, new id = <orig>_<lang>.

Output: data/confirmatory_PRIVATE/prompts_native_new.jsonl
"""
from __future__ import annotations
import json
from pathlib import Path
from code.benchmark.llm_clients import call_llm
from code.benchmark.generate_native_prompts import translate, BYC

OUT = Path(__file__).parent.parent.parent / "data" / "confirmatory_PRIVATE" / "prompts_native_new.jsonl"

NATIVE = {
    "COL": ("es", "Spanish (Colombian)"),
    "CHL": ("es", "Spanish (Chilean)"),
    "PRT": ("pt", "European Portuguese"),
    "AGO": ("pt", "Angolan Portuguese"),
}


def main():
    n, skipped = 0, 0
    with open(OUT, "w", encoding="utf-8") as out:
        for iso, (lang, lang_name) in NATIVE.items():
            fp = BYC / f"{iso}_v7.jsonl"
            if not fp.exists():
                print(f"missing {fp}"); continue
            for line in open(fp, encoding="utf-8"):
                r = json.loads(line)
                en = r.get("prompt_rendered", "")
                if not en:
                    skipped += 1; continue
                native = translate(en, lang_name)
                if not native or "JUDGE_API_ERROR" in native:
                    print(f"  translation failed {r['prompt_id']} -> {lang}")
                    skipped += 1; continue
                rec = dict(r)
                rec["prompt_id"] = f"{r['prompt_id']}_{lang}"
                rec["language"] = lang
                rec["prompt_rendered"] = native
                rec["prompt_rendered_en"] = en
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
                if n % 10 == 0:
                    print(f"  translated {n}...")
    print(f"DONE. new native prompts: {n} (skipped {skipped}) -> {OUT.name}")


if __name__ == "__main__":
    main()
