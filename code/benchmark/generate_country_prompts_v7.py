"""
generate_country_prompts_v7.py — Generate T1-T5 x persona prompts for the 15
countries of the v7 study, with web-verified national PM2.5 standards (T1) and
honest NEEDS_HUMAN flags where a specific value was not verified (T2-T5).

T1 ground truth verified via official/authoritative web sources (2026-06).
Writes one JSONL per country to data/confirmatory_PRIVATE/by_country/<ISO>_v7.jsonl
(10 records each: 5 tasks x 2 personas).

NO INVENTION: every numeric T1 value carries a real source; unverified values
are flagged NEEDS_HUMAN rather than fabricated.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
OUTDIR = ROOT / "data" / "confirmatory_PRIVATE" / "by_country"
OUTDIR.mkdir(parents=True, exist_ok=True)

# Per-country: city (T2 anchor), T1 standard ground truth + source, optional flag.
COUNTRIES = {
    "BRA": dict(name="Brazil", tier="GS", city="São Paulo",
        t1="Brazil's national PM2.5 standards are set by CONAMA Resolution 506/2024 (which superseded the relevant articles of Resolution 491/2018). The stage in force in 2026 is Intermediate Target PI-2; the Final Target adopts the WHO 2021 annual guideline of 5 ug/m3.",
        t1_src="CONAMA Resolution 506/2024: https://conama.mma.gov.br/index.php?option=com_sisconama&view=atonormativo&id=756",
        t1_flag="NEEDS_HUMAN: exact PI-2 annual PM2.5 numeric value (Annex I CONAMA 506/2024)"),
    "MEX": dict(name="Mexico", tier="GS", city="Mexico City",
        t1="Mexico's annual mean PM2.5 ambient air quality standard is 10 ug/m3 (24h: 33 ug/m3), per NOM-025-SSA1-2021.",
        t1_src="NOM-025-SSA1-2021, DOF 27/10/2021: https://dof.gob.mx/nota_detalle.php?codigo=5633855", t1_flag=None),
    "ARG": dict(name="Argentina", tier="GS", city="Buenos Aires",
        t1="Argentina lacks a single binding federal annual PM2.5 standard; Law 20.284/1973 is the federal framework, and PM2.5 limits are set at the subnational level (e.g., CABA references WHO guidelines).",
        t1_src="Ley 20.284/1973: https://www.argentina.gob.ar/normativa/nacional/ley-20284-40167",
        t1_flag="NEEDS_HUMAN: confirm whether a binding federal annual PM2.5 value exists or cite the relevant subnational standard"),
    "PER": dict(name="Peru", tier="GS", city="Lima",
        t1="Peru's annual mean PM2.5 environmental quality standard (ECA) is 25 ug/m3 (24h: 50 ug/m3), per D.S. 003-2017-MINAM.",
        t1_src="D.S. 003-2017-MINAM: https://www.gob.pe/institucion/minam/normas-legales/3670-003-2017-minam", t1_flag=None),
    "NGA": dict(name="Nigeria", tier="GS", city="Lagos",
        t1="Nigeria's national annual PM2.5 ambient air quality standard is 20 ug/m3, set and enforced by NESREA under the National Environmental (Air Quality Control) Regulations.",
        t1_src="NESREA Air Quality Regulations: https://www.nesrea.gov.ng/wp-content/uploads/2023/07/Airquality_Regulation.pdf",
        t1_flag="NEEDS_HUMAN: confirm exact value against primary NESREA gazette text"),
    "ZAF": dict(name="South Africa", tier="GS", city="Johannesburg",
        t1="South Africa's national annual PM2.5 ambient air quality standard is 20 ug/m3 (24h: 40 ug/m3), set under NEMAQA (Act 39 of 2004), effective 2012.",
        t1_src="SA NAAQS under NEMAQA: https://www.environment.gov.za/", t1_flag=None),
    "KEN": dict(name="Kenya", tier="GS", city="Nairobi",
        t1="Kenya regulates ambient air quality under the EMCA (Air Quality) Regulations 2014, administered by NEMA.",
        t1_src="NEMA Air Quality Regulations: https://www.nema.go.ke/",
        t1_flag="NEEDS_HUMAN: exact annual PM2.5 value from EMCA Air Quality Regulations 2014 not verified"),
    "EGY": dict(name="Egypt", tier="GS", city="Cairo",
        t1="Egypt's ambient PM2.5 standard derives from Environmental Law No. 4/1994 (as amended by Laws 9/2009 and 105/2015); the annual PM2.5 limit reported under this framework is on the order of 50-70 ug/m3.",
        t1_src="Environmental Law 4/1994 (amended): https://wedocs.unep.org/bitstream/handle/20.500.11822/17186/Egypt.pdf",
        t1_flag="NEEDS_HUMAN: confirm current annual PM2.5 value after 2009/2015 amendments (50 vs 70 ug/m3)"),
    "IND": dict(name="India", tier="GS", city="Delhi",
        t1="India's national annual PM2.5 ambient air quality standard is 40 ug/m3 (24h: 60 ug/m3), per the CPCB National Ambient Air Quality Standards (2009).",
        t1_src="CPCB NAAQS: https://cpcb.nic.in/upload/NAAQS_2019.pdf", t1_flag=None),
    "IDN": dict(name="Indonesia", tier="GS", city="Jakarta",
        t1="Indonesia's national annual PM2.5 ambient air quality standard is 15 ug/m3, per Government Regulation PP No. 22/2021 (Lampiran VII).",
        t1_src="PP No. 22/2021: https://peraturan.bpk.go.id/Details/161852/pp-no-22-tahun-2021", t1_flag=None),
    "BGD": dict(name="Bangladesh", tier="GS", city="Dhaka",
        t1="Bangladesh's national annual PM2.5 standard was 15 ug/m3 under ECR 1997 (rev. 2005); the Air Pollution (Control) Rules 2022 revised the standards, with sources reporting an annual value of 35 ug/m3.",
        t1_src="Bangladesh DoE / Air Pollution Control Rules 2022: https://doe.portal.gov.bd/",
        t1_flag="NEEDS_HUMAN: confirm current annual PM2.5 value (15 ug/m3 ECR vs 35 ug/m3 2022 revision)"),
    "PHL": dict(name="Philippines", tier="GS", city="Manila",
        t1="The Philippines sets ambient PM2.5 guideline values under RA 8749 (Clean Air Act) via DENR Administrative Orders; a provisional annual guideline value of 25 ug/m3 has been used (DAO 2013-13).",
        t1_src="DENR EMB Air Quality: https://air.emb.gov.ph/",
        t1_flag="NEEDS_HUMAN: confirm current provisional annual PM2.5 guideline value and DAO reference"),
    "USA": dict(name="United States", tier="GN", city="Los Angeles",
        t1="The U.S. primary annual PM2.5 NAAQS is 9.0 ug/m3, strengthened from 12.0 ug/m3 by EPA on 7 February 2024 (effective 6 May 2024); the 24h primary standard (35 ug/m3) was retained.",
        t1_src="EPA Final Reconsideration, Federal Register 2024-02637: https://www.federalregister.gov/documents/2024/03/06/2024-02637/", t1_flag=None),
    "DEU": dict(name="Germany", tier="GN", city="Berlin",
        t1="Germany applies the EU annual PM2.5 limit value of 25 ug/m3 (Directive 2008/50/EC), in force in 2026; the revised Ambient Air Quality Directive (EU) 2024/2881 lowers it to 10 ug/m3 from 1 January 2030.",
        t1_src="Directive (EU) 2024/2881: https://environment.ec.europa.eu/news/new-pollution-rules-come-effect-cleaner-air-2030-2024-12-10_en", t1_flag=None),
    "JPN": dict(name="Japan", tier="GN", city="Tokyo",
        t1="Japan's environmental quality standard for PM2.5 is an annual mean of 15 ug/m3 (24h: 35 ug/m3), established by the Ministry of the Environment in 2009.",
        t1_src="Ministry of the Environment, Japan: https://www.env.go.jp/en/air/aq/aq.html", t1_flag=None),
}

TASKS = {
    "T1": ("norma_tecnica",
        "What is the current national annual mean ambient air quality standard for PM2.5 in {country}? State the regulation that establishes it and whether it is an intermediate or final target. Limit to 1-3 sentences.",
        "factual_accuracy"),
    "T2": ("dado_factual_local",
        "According to the national or subnational environmental agency, what was the annual mean PM2.5 concentration in {city}, {country}, in the most recent reported year? Provide value in ug/m3, the reference station or network, and the source.",
        "factual_accuracy"),
    "T3": ("sintese_evidencia_saude",
        "Summarize the epidemiological evidence on mortality attributable to ambient PM2.5 exposure in {country} over the last decade. Include estimated annual deaths, primary causes, and at least one authoritative source.",
        "factual_accuracy_and_completeness"),
    "T4": ("instrumentos_politica",
        "List the principal national programs or legal instruments for monitoring and controlling ambient air pollution in {country}, with the executing agency for each.",
        "factual_accuracy_and_completeness"),
    "T5": ("recomendacao_aplicada",
        "A metropolitan region of {country} faces a forecast episode with PM2.5 expected to exceed 75 ug/m3 within 24 hours. Recommend three short-term policy actions (deployable within 48 hours) to reduce population exposure, each justified by public-health evidence or operational feasibility.",
        "rubric_quality_score"),
}

def persona_prefix(c):
    return f"I am the municipal environmental management official of {c['city']}, {c['name']}, and I need to brief decision-makers. "

def ground_truth_for(task, c):
    if task == "T1":
        return c["t1"], c["t1_src"], (c.get("t1_flag") or "OK_VERIFIED: T1 standard from official/authoritative source")
    if task == "T2":
        return (f"The {c['name']} national environmental agency reports annual mean PM2.5 for {c['city']}. [NEEDS_HUMAN: specific value + year + reference station from the official agency report.]",
                c["t1_src"], "NEEDS_HUMAN: city-year PM2.5 value from official agency report")
    if task == "T3":
        return (f"GBD 2019 and the State of Global Air report PM2.5-attributable mortality for {c['name']}, dominated by cardiovascular and lower-respiratory causes. [NEEDS_HUMAN: country-specific annual death estimate + a peer-reviewed source with resolvable DOI.]",
                "GBD 2019 (IHME): https://www.healthdata.org/research-analysis/gbd; State of Global Air: https://www.stateofglobalair.org/",
                "NEEDS_HUMAN: country-specific mortality figure + verified DOI")
    if task == "T4":
        return (f"{c['name']}'s air pollution control is administered by its national environmental authority under the regulation cited for T1. [NEEDS_HUMAN: enumerate the specific national programs/instruments and executing agencies with official sources.]",
                c["t1_src"], "NEEDS_HUMAN: enumerate national programs + agencies with sources")
    if task == "T5":
        return ("Rubric-scored (no single ground truth). Evidence-based short-term actions include a public-health advisory for vulnerable groups, temporary traffic/emission restrictions, and suspension of high-emission activities under episode protocols. Rubric scores action specificity, public-health linkage, operational feasibility, and use of authoritative sources.",
                "WHO 2021 Global Air Quality Guidelines (episode communication): https://www.who.int/publications/i/item/9789240034228",
                "OK_RUBRIC: open task, no single ground truth")
    return "", "", ""

def main():
    written = {}
    for iso, c in COUNTRIES.items():
        records = []
        for task, (tname, ptmpl, rubric) in TASKS.items():
            base = ptmpl.format(country=c["name"], city=c["city"])
            gt, src, flag = ground_truth_for(task, c)
            for persona in ("neutral", "public_manager_env"):
                rendered = base if persona == "neutral" else persona_prefix(c) + base
                records.append({
                    "prompt_id": f"{iso}_AP_{task}_N01_{persona}",
                    "country_iso3": iso, "country_name": c["name"], "tier": c["tier"],
                    "domain": "AP_policy", "task": task, "task_name": tname,
                    "persona": persona, "language": "en",
                    "prompt_rendered": rendered,
                    "ground_truth": gt, "ground_truth_source": src,
                    "rubric_primary": rubric, "validation_flag": flag,
                })
        fp = OUTDIR / f"{iso}_v7.jsonl"
        with open(fp, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        written[iso] = len(records)
    total = sum(written.values())
    print(f"Wrote {len(written)} countries, {total} records ({total//2} prompts x 2 personas)")
    for iso, n in written.items():
        print(f"  {iso}: {n}")

if __name__ == "__main__":
    main()
