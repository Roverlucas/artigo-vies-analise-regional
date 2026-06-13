"""
generate_new_countries.py — Expansion: 6 new Global North + 4 native-pair countries.

GN (English only): UK, Canada, Australia, South Korea, France, Italy.
Native-pair: Colombia (es), Chile (es), Portugal (pt), Angola (pt).
T1 ground truth anchored to official sources (verified in the registry).
T2-T5 structured with NEEDS_HUMAN where the specific value is unverified.

Writes one JSONL per country to data/confirmatory_PRIVATE/by_country/<ISO>_v7.jsonl
(10 records: 5 tasks x 2 personas). Native renderings are generated separately.
"""
from __future__ import annotations
import json
from pathlib import Path
from code.benchmark.generate_country_prompts_v7 import TASKS, persona_prefix, OUTDIR

# iso -> name, tier, city, native_lang(or None), T1 ground truth, T1 source, T1 flag
NEW = {
 "UK":  ("United Kingdom","GN","London",None,
   "The UK (England) annual mean PM2.5 target is 10 ug/m3, to be met by 2040, under the Environmental Targets (Fine Particulate Matter) (England) Regulations 2023 (a population-exposure-reduction target of 35% vs 2018 also applies).",
   "Environmental Targets (Fine Particulate Matter)(England) Regulations 2023: https://www.legislation.gov.uk/ukdsi/2022/9780348242959", None),
 "CAN": ("Canada","GN","Toronto",None,
   "Canada's annual PM2.5 Canadian Ambient Air Quality Standard (CAAQS) is 8.8 ug/m3 (2020 standard).",
   "CCME Canadian Ambient Air Quality Standards: https://ccme.ca/en/res/pn1483_gdad_eng-secured.pdf", None),
 "AUS": ("Australia","GN","Sydney",None,
   "Australia's annual mean PM2.5 standard is 8 ug/m3 under the National Environment Protection (Ambient Air Quality) Measure, with a 7 ug/m3 target from 2025.",
   "NEPM Ambient Air Quality: https://www.nepc.gov.au/nepms/ambient-air-quality", None),
 "KOR": ("South Korea","GN","Seoul",None,
   "South Korea's annual ambient PM2.5 air-quality standard is 15 ug/m3 (Ministry of Environment).",
   "Ministry of Environment, Korea: http://eng.me.go.kr/eng/web/index.do?menuId=252", None),
 "FRA": ("France","GN","Paris",None,
   "France applies the EU annual PM2.5 limit value of 25 ug/m3 (Directive 2008/50/EC), lowered to 10 ug/m3 from 2030 under the revised Directive (EU) 2024/2881.",
   "EU Ambient Air Quality Directive: https://environment.ec.europa.eu/topics/air/air-quality_en", None),
 "ITA": ("Italy","GN","Milan",None,
   "Italy applies the EU annual PM2.5 limit value of 25 ug/m3 (Directive 2008/50/EC), lowered to 10 ug/m3 from 2030 under the revised Directive (EU) 2024/2881.",
   "EU Ambient Air Quality Directive: https://environment.ec.europa.eu/topics/air/air-quality_en", None),
 "COL": ("Colombia","GS","Bogota","es",
   "Colombia's annual PM2.5 maximum permissible level is 25 ug/m3 (Tabla 1, in force since 2018), lowered to 15 ug/m3 from 2030 (Tabla 2); the 24-hour level is 37 ug/m3.",
   "Resolucion 2254/2017 MinAmbiente, Tabla 1 & 2 (verbatim from official scan): https://www.minambiente.gov.co/wp-content/uploads/2021/10/Resolucion-2254-de-2017.pdf",
   None),
 "CHL": ("Chile","GS","Santiago","es",
   "Chile's primary annual PM2.5 air-quality standard is 20 ug/m3, established by Supreme Decree D.S. 12/2011 (Ministry of Environment).",
   "D.S. 12/2011 MMA Chile: https://www.bcn.cl/leychile/navegar?idNorma=1025202", None),
 "PRT": ("Portugal","GN","Lisbon","pt",
   "Portugal applies the EU annual PM2.5 limit value of 25 ug/m3 (Directive 2008/50/EC), lowered to 10 ug/m3 from 2030 under the revised Directive (EU) 2024/2881.",
   "EU Ambient Air Quality Directive: https://environment.ec.europa.eu/topics/air/air-quality_en", None),
 "AGO": ("Angola","GS","Luanda","pt",
   "Angola does NOT have national air-quality legislation setting a PM2.5 standard; air quality is assessed against WHO guidelines.",
   "World Bank / WHO (no national standard): https://data.worldbank.org/indicator/EN.ATM.PM25.MC.M3?locations=AO",
   "VERIFIED_NO_STANDARD"),
}


def gt_for(task, c):
    name, tier, city, lang, t1, t1src, t1flag = c
    if task == "T1":
        return t1, t1src, (t1flag or "VERIFIED: official primary source")
    if task == "T2":
        return (f"The {name} national/subnational environmental agency reports the annual mean PM2.5 for {city}. "
                f"[NEEDS_HUMAN: specific value + year + station from the official report or WHO Ambient Air Quality Database.]",
                "WHO Ambient Air Quality Database V6.1: https://www.who.int/data/gho/data/themes/air-pollution",
                "NEEDS_HUMAN: city-year PM2.5 from official/WHO database")
    if task == "T3":
        return (f"GBD 2019 and the State of Global Air report PM2.5-attributable mortality for {name}, dominated by "
                f"cardiovascular and lower-respiratory causes. [NEEDS_HUMAN: country-specific figure + DOI.]",
                "GBD 2019 (IHME): https://www.healthdata.org/research-analysis/gbd",
                "NEEDS_HUMAN: country mortality figure + DOI")
    if task == "T4":
        return (f"{name}'s air pollution control is administered by its national environmental authority under the "
                f"regulation cited for T1. [NEEDS_HUMAN: enumerate national programs/agencies with official sources.]",
                c[5], "NEEDS_HUMAN: national programs + agencies")
    return ("Rubric-scored (no single ground truth). Evidence-based short-term episode actions: public-health advisory "
            "for vulnerable groups, temporary traffic/emission restrictions, suspension of high-emission activities.",
            "WHO 2021 Global Air Quality Guidelines: https://www.who.int/publications/i/item/9789240034228",
            "OK_RUBRIC")


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    written = {}
    for iso, c in NEW.items():
        name, tier, city, lang = c[0], c[1], c[2], c[3]
        recs = []
        for task, (tname, ptmpl, rubric) in TASKS.items():
            base = ptmpl.format(country=name, city=city)
            gt, src, flag = gt_for(task, c)
            for persona in ("neutral", "public_manager_env"):
                rendered = base if persona == "neutral" else (
                    f"I am the municipal environmental management official of {city}, {name}, "
                    f"and I need to brief decision-makers. " + base)
                recs.append({"prompt_id": f"{iso}_AP_{task}_N01_{persona}", "country_iso3": iso,
                    "country_name": name, "tier": tier, "domain": "AP_policy", "task": task,
                    "task_name": tname, "persona": persona, "language": "en",
                    "prompt_rendered": rendered, "ground_truth": gt, "ground_truth_source": src,
                    "rubric_primary": rubric, "validation_flag": flag,
                    "native_lang": lang or ""})
        fp = OUTDIR / f"{iso}_v7.jsonl"
        with open(fp, "w", encoding="utf-8") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        written[iso] = len(recs)
    total = sum(written.values())
    print(f"Wrote {len(written)} new countries, {total} records")
    pair = [iso for iso, c in NEW.items() if c[3]]
    print(f"  Global North (English only): UK CAN AUS KOR FRA ITA")
    print(f"  Native-pair: {pair} (es: COL CHL | pt: PRT AGO)")


if __name__ == "__main__":
    main()
