"""
analyze_pilot_v2.py — Pilot 2.0 analysis using LLM-as-judge scores.

Loads data/pilot_202604/analysis/judge_scores.jsonl and produces:
- Aggregated composite scores per model, country, task, model x country
- Variance components (for SAP recalibration)
- Effect-size estimates (Cohen's d, ICC) for H1 signal
- Heatmap-ready CSV for figure generation
- Updated pilot findings document

This supersedes the heuristic-based analyze_pilot.py for pilot 2.0+.
"""

from __future__ import annotations
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
PILOT_DIR = ROOT / "data" / "pilot_202604"
ANALYSIS_DIR = PILOT_DIR / "analysis"


def load_judge_scores() -> list[dict]:
    rows = []
    with open(ANALYSIS_DIR / "judge_scores.jsonl") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _stats(xs):
    if not xs:
        return {"n": 0, "mean": 0, "sd": 0, "min": 0, "max": 0, "median": 0}
    return {
        "n":      len(xs),
        "mean":   round(statistics.mean(xs), 3),
        "sd":     round(statistics.stdev(xs), 3) if len(xs) > 1 else 0,
        "median": round(statistics.median(xs), 3),
        "min":    round(min(xs), 3),
        "max":    round(max(xs), 3),
    }


def main():
    rows = load_judge_scores()
    rows = [r for r in rows if not r.get("error")]
    print(f"Loaded {len(rows)} judge scores (excluding errors)")

    by_model = defaultdict(list)
    by_country = defaultdict(list)
    by_task = defaultdict(list)
    by_model_country = defaultdict(list)
    by_model_task = defaultdict(list)

    for r in rows:
        c = r["composite"]
        by_model[r["model_id"]].append(c)
        by_country[r["country_iso3"]].append(c)
        by_task[r["task"]].append(c)
        by_model_country[(r["model_id"], r["country_iso3"])].append(c)
        by_model_task[(r["model_id"], r["task"])].append(c)

    GS = ["BRA", "NGA", "IND", "PER", "IDN"]
    GN = ["USA", "DEU"]

    gs_scores = [r["composite"] for r in rows if r["country_iso3"] in GS]
    gn_scores = [r["composite"] for r in rows if r["country_iso3"] in GN]

    # Cohen's d (pooled SD)
    if gs_scores and gn_scores:
        gs_mean = statistics.mean(gs_scores)
        gn_mean = statistics.mean(gn_scores)
        gs_var = statistics.variance(gs_scores) if len(gs_scores) > 1 else 0
        gn_var = statistics.variance(gn_scores) if len(gn_scores) > 1 else 0
        n_gs, n_gn = len(gs_scores), len(gn_scores)
        pooled_sd = ((((n_gs - 1) * gs_var) + ((n_gn - 1) * gn_var)) / max(1, n_gs + n_gn - 2)) ** 0.5
        cohens_d = (gn_mean - gs_mean) / pooled_sd if pooled_sd > 0 else 0
    else:
        gs_mean = gn_mean = cohens_d = 0
        pooled_sd = 0

    # Variance components for SAP recalibration
    grand_mean = statistics.mean([r["composite"] for r in rows])
    country_means = {c: statistics.mean(by_country[c]) for c in by_country}
    model_means = {m: statistics.mean(by_model[m]) for m in by_model}

    # Between-country variance (between-group)
    var_country = statistics.pvariance(list(country_means.values())) if len(country_means) > 1 else 0
    # Between-model variance
    var_model = statistics.pvariance(list(model_means.values())) if len(model_means) > 1 else 0
    # Total variance
    var_total = statistics.pvariance([r["composite"] for r in rows])
    # Residual = total - country - model
    var_residual = max(0, var_total - var_country - var_model)
    icc_country = var_country / var_total if var_total > 0 else 0
    icc_model = var_model / var_total if var_total > 0 else 0

    # H5 — open vs closed frontier
    open_models = ["llama4_scout", "command_rp"]
    closed_accessible = ["claude_haiku", "gpt5_mini", "gemini_flash"]
    open_scores = [r["composite"] for r in rows if r["model_id"] in open_models]
    closed_scores = [r["composite"] for r in rows if r["model_id"] in closed_accessible]
    open_mean = statistics.mean(open_scores) if open_scores else 0
    closed_mean = statistics.mean(closed_scores) if closed_scores else 0

    # Build report
    lines = []
    lines.append("# Pilot 2.0 Findings — LLM-as-Judge Analysis\n")
    lines.append("> **PILOT — exploratory, not confirmatory.** Scoring via Claude Haiku 4.5 as judge (G-Eval framework, Liu et al. 2023). Final confirmatory scoring will use Claude Opus 4.7 or human panel.\n")
    lines.append(f"**Total judge scores analyzed:** {len(rows)}")
    lines.append(f"**Models:** {len(by_model)}")
    lines.append(f"**Countries:** {len(by_country)}\n")

    lines.append("## 1. Composite score by model\n")
    lines.append("| Model | N | Mean | SD | Median | Min | Max |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for m in sorted(by_model, key=lambda k: -statistics.mean(by_model[k])):
        s = _stats(by_model[m])
        lines.append(f"| {m} | {s['n']} | {s['mean']} | {s['sd']} | {s['median']} | {s['min']} | {s['max']} |")

    lines.append("\n## 2. Composite score by country\n")
    lines.append("| Country | Tier | N | Mean | SD | Median |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for c in sorted(by_country, key=lambda k: -statistics.mean(by_country[k])):
        tier = "GS" if c in GS else "GN"
        s = _stats(by_country[c])
        lines.append(f"| {c} | {tier} | {s['n']} | {s['mean']} | {s['sd']} | {s['median']} |")

    lines.append("\n## 3. Model × Country matrix (composite mean)\n")
    countries_ordered = ["BRA", "NGA", "IND", "PER", "IDN", "USA", "DEU"]
    lines.append("| Model | " + " | ".join(countries_ordered) + " | Range |")
    lines.append("|---|" + "|".join([":-:" for _ in countries_ordered]) + "|:-:|")
    for m in sorted(by_model):
        row = [m]
        means = []
        for c in countries_ordered:
            xs = by_model_country.get((m, c), [])
            mean = round(statistics.mean(xs), 2) if xs else None
            means.append(mean)
            row.append(str(mean) if mean is not None else "—")
        valid = [x for x in means if x is not None]
        rng = round(max(valid) - min(valid), 2) if valid else 0
        row.append(str(rng))
        lines.append("| " + " | ".join(row) + " |")

    lines.append("\n## 4. Composite score by task\n")
    lines.append("| Task | N | Mean | SD |")
    lines.append("|---|---:|---:|---:|")
    for t in sorted(by_task):
        s = _stats(by_task[t])
        lines.append(f"| {t} | {s['n']} | {s['mean']} | {s['sd']} |")

    lines.append("\n## 5. H1 signal — Global South vs Global North\n")
    lines.append(f"- **Global South (BRA + NGA + IND + PER + IDN):** mean = **{gs_mean:.3f}**, n = {len(gs_scores)}")
    lines.append(f"- **Global North (USA + DEU):** mean = **{gn_mean:.3f}**, n = {len(gn_scores)}")
    lines.append(f"- **Gap (GN − GS):** **{gn_mean - gs_mean:+.3f}** ({(gn_mean - gs_mean) * 100:+.1f} percentage points)")
    lines.append(f"- **Pooled SD:** {pooled_sd:.3f}")
    lines.append(f"- **Pilot Cohen's d:** **{cohens_d:+.2f}**")
    if abs(cohens_d) >= 0.5:
        verdict = "consistent with H1 hypothesis (d >= 0.5 SESOI)"
    elif abs(cohens_d) >= 0.2:
        verdict = "small-to-moderate; may reach significance at confirmatory N"
    else:
        verdict = "small effect; H1 may be underpowered with current SESOI"
    lines.append(f"- **Direction:** {'GN > GS (consistent with H1)' if cohens_d > 0 else 'GS > GN (unexpected)'}")
    lines.append(f"- **Magnitude:** {verdict}")

    lines.append("\n## 6. Variance components (for SAP recalibration)\n")
    lines.append("| Component | Variance | ICC | Notes |")
    lines.append("|---|---:|---:|---|")
    lines.append(f"| Total | {var_total:.4f} | 1.000 | Reference |")
    lines.append(f"| Between-country | {var_country:.4f} | {icc_country:.3f} | H1-relevant |")
    lines.append(f"| Between-model | {var_model:.4f} | {icc_model:.3f} | Random effect |")
    lines.append(f"| Residual | {var_residual:.4f} | {var_residual/max(var_total, 1e-9):.3f} | Within-cell |")
    lines.append("")
    lines.append(f"**Implication for SAP:** ICC_country = {icc_country:.3f}; ICC_model = {icc_model:.3f}.")
    lines.append("Update Monte Carlo power analysis in `etapa4_sap.md` §3 with these values before OSF deposit.")

    lines.append("\n## 7. H5 signal — Open frontier vs Closed accessible\n")
    lines.append(f"- **Open frontier mean (Llama 4 Scout + Command R+):** {open_mean:.3f} (n={len(open_scores)})")
    lines.append(f"- **Closed accessible mean (Haiku + GPT-5-mini + Gemini Flash):** {closed_mean:.3f} (n={len(closed_scores)})")
    lines.append(f"- **Gap (closed − open):** {closed_mean - open_mean:+.3f}")
    if abs(closed_mean - open_mean) < 0.05:
        h5_verdict = "**consistent with H5** (open ≈ closed within 5pp)"
    else:
        h5_verdict = f"**not consistent with H5** (gap of {abs(closed_mean - open_mean) * 100:.1f}pp exceeds 5pp threshold)"
    lines.append(f"- **Pilot signal:** {h5_verdict}")
    lines.append("- *Caveat:* pilot uses Llama 4 Scout 17B (smaller than Tier A target 70B+). Confirmatory will include Llama 3.3 70B and other Tier A frontier open models.")

    lines.append("\n## 8. Caveats\n")
    lines.append("- **Single judge** (Haiku 4.5). For confirmatory, use Claude Opus 4.7 as judge OR add 2nd judge for inter-rater reliability (Krippendorff α ≥ 0.70).")
    lines.append("- **Single-author prompts** for non-BRA countries. Confirmatory requires expert-panel validation.")
    lines.append("- **Pilot N small** — country-level inference noisy.")
    lines.append("- **Self-evaluation flag:** Haiku 4.5 is in the model sample being evaluated. Pilot 2 documents this as limitation; confirmatory uses non-overlapping judge.")
    lines.append("- **No multilingual prompts in pilot** — all prompts in EN. Confirmatory adds sparse multilingual matrix.")

    output_path = ANALYSIS_DIR / "pilot_findings_v2.md"
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")

    # Print summary
    print()
    print("=" * 60)
    print(f"SIGNAL CHECK — H1")
    print(f"  GS mean: {gs_mean:.3f} (n={len(gs_scores)})")
    print(f"  GN mean: {gn_mean:.3f} (n={len(gn_scores)})")
    print(f"  Gap:     {gn_mean - gs_mean:+.3f} pp")
    print(f"  Cohen's d: {cohens_d:+.2f}")
    print()
    print(f"VARIANCE COMPONENTS")
    print(f"  ICC_country: {icc_country:.3f}")
    print(f"  ICC_model:   {icc_model:.3f}")
    print()
    print(f"H5 signal: open={open_mean:.3f}  closed_accessible={closed_mean:.3f}  gap={abs(closed_mean - open_mean)*100:.1f}pp")


if __name__ == "__main__":
    main()
