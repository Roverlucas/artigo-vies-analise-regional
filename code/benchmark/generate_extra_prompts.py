"""
generate_extra_prompts.py — Multiply native/English pairs for H2 power.

For the 5 countries with a native-language pair (BRA->pt, MEX/ARG/PER->es,
IND->hi), generate 2 additional question variants per (country, task) via Claude
Sonnet, each rendered neutral + persona in English and then translated to the
native language. This multiplies the within-country English/native pairs that
test H2 without adding new languages.

Anti-fabrication: variants must probe a DIFFERENT verifiable aspect of the same
task; ground truth must cite an official/known source or be marked rubric-scored,
never an invented value. For the paired H2 contrast, ground-truth imperfection
cancels (both members share it).

Output: data/confirmatory_PRIVATE/prompts_extra.jsonl
"""
from __future__ import annotations
import json
from pathlib import Path
from code.benchmark.llm_clients import call_llm

ROOT = Path(__file__).parent.parent.parent
OUT = ROOT / "data" / "confirmatory_PRIVATE" / "prompts_extra.jsonl"
GEN = "claude_sonnet"

COUNTRIES = {
    "BRA": ("pt","Brazilian Portuguese","Sao Paulo","Brazil"),
    "MEX": ("es","Spanish (Mexican)","Mexico City","Mexico"),
    "ARG": ("es","Spanish (Argentine)","Buenos Aires","Argentina"),
    "PER": ("es","Spanish (Peruvian)","Lima","Peru"),
    "IND": ("hi","Hindi","Delhi","India"),
}
TASKS = {
 "T1":"national air-quality standards (e.g. the binding annual vs 24-hour PM2.5 limit, the regulation that sets it, how it compares to the WHO guideline)",
 "T2":"officially measured local air-quality data (a specific city/region/year PM2.5 mean from the national environmental agency)",
 "T3":"peer-reviewed epidemiological evidence on the PM2.5 health burden in the country (deaths, causes, trends)",
 "T4":"national policy instruments and executing agencies for air-pollution control",
 "T5":"applied short-term recommendations for an acute PM2.5 episode (rubric-scored)",
}

VARIANT_PROMPT = """You are designing benchmark questions for an air-pollution-policy LLM evaluation about {country}.
Task type {task} concerns: {topic}.
Produce exactly 2 DISTINCT question variants that probe DIFFERENT verifiable sub-aspects of this task for {country} (e.g. a different metric, city, year, agency, or angle). Each must be answerable in 1-4 sentences.

RULES (No Invention): the ground_truth must reference an OFFICIAL or peer-reviewed source (national environmental agency, official regulation, WHO, GBD) OR be marked rubric-scored for open tasks. NEVER invent a numeric value or citation; if a precise value is not known, phrase the ground_truth as the verification criterion plus the official source to check, and set "needs_value": true.

Return ONLY a JSON array of 2 objects, each: {{"prompt": str, "ground_truth": str, "source": str, "needs_value": bool}}. No prose."""


def gen_variants(country, task, topic):
    p = VARIANT_PROMPT.format(country=country, task=task, topic=topic)
    r = call_llm(GEN, p, "en")
    txt = (r.response_text or "").strip()
    # extract JSON array
    s = txt.find("["); e = txt.rfind("]")
    if s < 0 or e < 0:
        return []
    try:
        arr = json.loads(txt[s:e+1])
        return arr if isinstance(arr, list) else []
    except Exception:
        return []


def translate(text, lang_name):
    p = (f"Translate into {lang_name}, preserving meaning, register, any role frame, "
         f"technical terms (PM2.5, ug/m3, agency names), and the brevity instruction. "
         f"Keep proper nouns/acronyms. Output ONLY the translation.\n\n{text}")
    return (call_llm(GEN, p, "en").response_text or "").strip()


def main():
    n = 0
    with open(OUT, "w", encoding="utf-8") as out:
        for iso,(lang,lang_name,city,cname) in COUNTRIES.items():
            for task,topic in TASKS.items():
                variants = gen_variants(cname, task, topic)
                for vi,v in enumerate(variants[:2], start=2):  # variant index 2,3 (1 = original)
                    base_en = v.get("prompt","").strip()
                    if not base_en: continue
                    gt = v.get("ground_truth",""); src = v.get("source","")
                    flag = "NEEDS_VALUE" if v.get("needs_value") else "OK_SOURCED"
                    native = translate(base_en, lang_name)
                    if not native: continue
                    persona_pref = f"I am the municipal environmental management official of {city}, {cname}, and I need to brief decision-makers. "
                    for persona in ("neutral","public_manager_env"):
                        en_render = base_en if persona=="neutral" else persona_pref+base_en
                        nat_render = native if persona=="neutral" else translate(persona_pref,lang_name)+" "+native
                        for langc, render in (("en",en_render),(lang,nat_render)):
                            pid = f"{iso}_AP_{task}_N0{vi}_{persona}" + ("" if langc=="en" else f"_{langc}")
                            rec = {"prompt_id":pid,"country_iso3":iso,"country_name":cname,
                                   "domain":"AP_policy","task":task,"task_name":task,
                                   "persona":persona,"language":langc,"prompt_rendered":render,
                                   "ground_truth":gt,"ground_truth_source":src,
                                   "rubric_primary":"factual_accuracy","validation_flag":flag,
                                   "variant":vi}
                            out.write(json.dumps(rec,ensure_ascii=False)+"\n"); n+=1
                print(f"  {iso} {task}: +{len(variants[:2])} variants")
    print(f"DONE. extra prompt renderings written: {n} -> {OUT.name}")


if __name__=="__main__":
    main()
