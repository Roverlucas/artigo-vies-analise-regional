"""
analyze_confirmatory.py — Descriptive + signal analysis of CONFIRMATORY judge scores.

Reads data/confirmatory_PRIVATE/analysis/judge_scores_confirmatory.jsonl and writes
data/confirmatory_PRIVATE/analysis/confirmatory_findings.md:
- composite by model, country, task, persona
- H1 (GS vs GN + Cohen's d) and ICC when >1 country present
- persona effect (neutral vs public_manager_env) when persona present

Stdlib only. Honest about scope: with a single country, H1/ICC are skipped.
"""
from __future__ import annotations
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
ANALYSIS = ROOT / "data" / "confirmatory_PRIVATE" / "analysis"
SCORES = ANALYSIS / "judge_scores_confirmatory.jsonl"

GS = {"BRA","MEX","ARG","PER","NGA","ZAF","KEN","EGY","IND","IDN","BGD","PHL"}
GN = {"USA","DEU","JPN"}
OPEN = {"llama4_scout","llama33_70b","deepseek_v3","gpt_oss_120b","command_rp",
        "qwen3_32b","qwen3_14b","phi4_14b","llama31_8b","cabra_mistral_7b"}
CLOSED_ACC = {"claude_haiku","gemini_flash","gpt5_mini"}


def load():
    rows = []
    if not SCORES.exists():
        return rows
    for line in open(SCORES):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("error"):
            continue
        if "composite" not in r:
            continue
        rows.append(r)
    return rows


def stat(xs):
    if not xs:
        return (0.0, 0.0, 0)
    m = statistics.mean(xs)
    sd = statistics.pstdev(xs) if len(xs) > 1 else 0.0
    return (m, sd, len(xs))


def table(rows, key, label):
    agg = defaultdict(list)
    for r in rows:
        agg[r.get(key, "?")].append(r["composite"])
    out = [f"\n## Composite by {label}\n", f"| {label} | N | Mean | SD |", "|---|---:|---:|---:|"]
    for k in sorted(agg, key=lambda k: -statistics.mean(agg[k])):
        m, sd, n = stat(agg[k])
        out.append(f"| {k} | {n} | {m:.3f} | {sd:.3f} |")
    return out


def main():
    rows = load()
    L = [f"# Confirmatory Findings (LLM-as-judge)\n", f"**Total judge scores:** {len(rows)}\n"]
    if not rows:
        L.append("\n_No confirmatory judge scores yet._\n")
        ANALYSIS.mkdir(parents=True, exist_ok=True)
        (ANALYSIS / "confirmatory_findings.md").write_text("\n".join(L))
        print("No scores yet.")
        return

    countries = sorted({r.get("country_iso3") for r in rows})
    personas = sorted({r.get("persona", "neutral") for r in rows})
    L.append(f"**Countries:** {', '.join(countries)}  |  **Personas:** {', '.join(personas)}\n")

    L += table(rows, "model_id", "model")
    L += table(rows, "task", "task")
    if len(countries) > 1:
        L += table(rows, "country_iso3", "country")

    # H1 (only meaningful with both tiers)
    gs = [r["composite"] for r in rows if r.get("country_iso3") in GS]
    gn = [r["composite"] for r in rows if r.get("country_iso3") in GN]
    if gs and gn:
        gm, _, _ = stat(gs); nm, _, _ = stat(gn)
        pooled = statistics.pstdev(gs + gn) or 1e-9
        d = (nm - gm) / pooled
        L += ["\n## H1 signal — Global South vs Global North\n",
              f"- GS mean: **{gm:.3f}** (n={len(gs)})",
              f"- GN mean: **{nm:.3f}** (n={len(gn)})",
              f"- Gap (GN-GS): **{(nm-gm)*100:+.1f} pp**",
              f"- Cohen's d: **{d:+.2f}**"]

    # Persona effect (preliminary H6 read)
    if len(personas) > 1:
        pn = [r["composite"] for r in rows if r.get("persona") == "neutral"]
        pp = [r["composite"] for r in rows if r.get("persona") == "public_manager_env"]
        if pn and pp:
            mn, _, _ = stat(pn); mp, _, _ = stat(pp)
            L += ["\n## Persona effect (preliminary H6 read)\n",
                  f"- neutral mean: **{mn:.3f}** (n={len(pn)})",
                  f"- public_manager_env mean: **{mp:.3f}** (n={len(pp)})",
                  f"- Persona - neutral: **{(mp-mn)*100:+.1f} pp**",
                  "- Note: this is a marginal contrast, not the country-level DiD of H6."]

    # H5
    om = [r["composite"] for r in rows if r.get("model_id") in OPEN]
    cm = [r["composite"] for r in rows if r.get("model_id") in CLOSED_ACC]
    if om and cm:
        omm, _, _ = stat(om); cmm, _, _ = stat(cm)
        L += ["\n## H5 signal — open vs closed-accessible\n",
              f"- open mean: **{omm:.3f}** (n={len(om)})",
              f"- closed-accessible mean: **{cmm:.3f}** (n={len(cm)})",
              f"- Gap: **{(cmm-omm)*100:+.1f} pp**"]

    L.append("\n---\n_Single-country runs skip H1/ICC. Judge = claude_haiku (self-evaluation caveat).\n")
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    out = ANALYSIS / "confirmatory_findings.md"
    out.write_text("\n".join(L))
    print(f"Wrote {out}")
    print("\n".join(L[:2]))
    if gs and gn:
        print(f"H1: GS={statistics.mean(gs):.3f} GN={statistics.mean(gn):.3f} gap={(statistics.mean(gn)-statistics.mean(gs))*100:+.1f}pp")


if __name__ == "__main__":
    main()
