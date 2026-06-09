"""
validate_collection.py — Quality/coverage audit of the confirmatory collection.

Judge-free, API-free: reads only the local response files and assesses whether
the collected data is sound, BEFORE spending anything on judging.

Per run it:
  - Computes coverage (responses per model x country x task x persona vs target),
  - Flags quality issues (empty responses, truncation, suspiciously short or
    duplicated outputs, missing cells),
  - Writes a human-readable report (collection_validation.md), and
  - APPENDS a timestamped snapshot to collection_evolution.jsonl so the run can
    be invoked repeatedly to track how the collection fills in over time.

Target per model = (# unique prompts) x N_REPS. Only the v7 15-country prompt set
(prompt_id contains '_AP_') is audited; legacy BRA_C* prompts are ignored.

Usage:
    python -m code.analysis.validate_collection
    python -m code.analysis.validate_collection --reps 2
"""
from __future__ import annotations
import argparse
import glob
import json
import statistics
from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
PROMPTS = ROOT / "data" / "confirmatory_PRIVATE" / "prompts_confirmatory.jsonl"
RESPONSES_DIR = ROOT / "data" / "confirmatory_PRIVATE" / "responses"
ANALYSIS = ROOT / "data" / "confirmatory_PRIVATE" / "analysis"

GS = {"BRA","MEX","ARG","PER","NGA","ZAF","KEN","EGY","IND","IDN","BGD","PHL"}
GN = {"USA","DEU","JPN"}


def load_jsonl(p: Path):
    if not p.exists():
        return
    for l in open(p, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        try:
            yield json.loads(l)
        except Exception:
            continue


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=2)
    args = ap.parse_args()
    ANALYSIS.mkdir(parents=True, exist_ok=True)

    # v7 prompt universe
    prompts = [p for p in load_jsonl(PROMPTS) if "_AP_" in (p.get("prompt_id") or "")]
    prompt_ids = {p["prompt_id"] for p in prompts}
    n_prompts = len(prompt_ids)
    countries = sorted({p["country_iso3"] for p in prompts})
    tasks = sorted({p["task"] for p in prompts})
    personas = sorted({p.get("persona", "neutral") for p in prompts})
    target_per_model = n_prompts * args.reps

    # Aggregate responses (v7 only), dedup by (model, prompt, rep) keeping any valid
    cells = {}  # (model, pid, rep) -> rec
    for fp in glob.glob(str(RESPONSES_DIR / "run_*.jsonl")):
        if "_DEPRECATED" in fp:
            continue
        for r in load_jsonl(Path(fp)):
            pid = r.get("prompt_id") or r.get("pilot_id")
            if pid not in prompt_ids:
                continue
            key = (r.get("model_id"), pid, int(r.get("replicate_idx", 0)))
            cur = cells.get(key)
            txt = (r.get("response_text") or "").strip()
            # prefer a non-empty record if duplicates exist
            if cur is None or (not (cur.get("response_text") or "").strip() and txt):
                cells[key] = r

    models = sorted({k[0] for k in cells})
    by_model = {}
    dup_texts = defaultdict(Counter)
    for m in models:
        recs = [v for k, v in cells.items() if k[0] == m]
        texts = [(v.get("response_text") or "").strip() for v in recs]
        valid = [t for t in texts if t]
        empty = sum(1 for t in texts if not t)
        short = sum(1 for t in valid if len(t) < 20)
        trunc = sum(1 for v in recs if v.get("finish_reason") in ("truncated", "length", "MAX_TOKENS"))
        lens = [len(t) for t in valid]
        # exact-duplicate detection within model (sign of a stuck/echoing model)
        tc = Counter(valid)
        dups = sum(c for t, c in tc.items() if c > 1 and len(t) > 0) - len([t for t, c in tc.items() if c > 1])
        by_model[m] = {
            "collected": len(recs),
            "valid": len(valid),
            "empty": empty,
            "short_lt20": short,
            "truncated": trunc,
            "exact_dup_extra": dups,
            "coverage_pct": round(100 * len(recs) / target_per_model, 1),
            "valid_pct": round(100 * len(valid) / target_per_model, 1),
            "mean_len": round(statistics.mean(lens), 0) if lens else 0,
            "median_len": round(statistics.median(lens), 0) if lens else 0,
        }

    # Coverage matrices
    cov_country = Counter(k[1].split("_")[0] for k in cells)
    cov_task = Counter()
    for k in cells:
        # task is the 3rd underscore token in <ISO>_AP_T#_...
        parts = k[1].split("_")
        if len(parts) >= 3:
            cov_task[parts[2]] += 1

    total_collected = len(cells)
    total_valid = sum(1 for v in cells.values() if (v.get("response_text") or "").strip())
    total_target = len(models) * target_per_model if models else 0

    # ---- Report ----
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    L = [f"# Collection Validation\n",
         f"Generated: {ts}\n",
         f"v7 prompts: {n_prompts} · countries: {len(countries)} · tasks: {len(tasks)} · "
         f"personas: {len(personas)} · target/model: {target_per_model}\n",
         f"Models with data: {len(models)} · total collected: {total_collected} · "
         f"valid: {total_valid} ({round(100*total_valid/max(1,total_collected),1)}%)\n",
         "\n## Per-model quality\n",
         "| Model | Collected | Valid | Cov% | Empty | Short<20 | Trunc | DupX | MeanLen |",
         "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    flags = []
    for m in sorted(by_model, key=lambda m: -by_model[m]["valid_pct"]):
        d = by_model[m]
        L.append(f"| {m} | {d['collected']} | {d['valid']} | {d['valid_pct']} | {d['empty']} | "
                 f"{d['short_lt20']} | {d['truncated']} | {d['exact_dup_extra']} | {int(d['mean_len'])} |")
        if d["valid_pct"] < 90:
            flags.append(f"{m}: only {d['valid_pct']}% valid coverage ({d['valid']}/{target_per_model})")
        if d["empty"] > 0.10 * target_per_model:
            flags.append(f"{m}: high empty rate ({d['empty']})")
        if d["exact_dup_extra"] > 0.15 * max(1, d["valid"]):
            flags.append(f"{m}: many exact-duplicate outputs ({d['exact_dup_extra']}) — possible stuck model")

    L.append("\n## Coverage by country (responses across all models)\n")
    L.append("| Country | Tier | N |")
    L.append("|---|---|---:|")
    for c in countries:
        tier = "GN" if c in GN else "GS"
        L.append(f"| {c} | {tier} | {cov_country.get(c,0)} |")

    L.append("\n## Coverage by task\n")
    L.append("| Task | N |\n|---|---:|")
    for t in tasks:
        L.append(f"| {t} | {cov_task.get(t,0)} |")

    L.append("\n## Quality flags\n")
    if flags:
        for f in flags:
            L.append(f"- ⚠️ {f}")
    else:
        L.append("- ✅ No quality flags (all models ≥90% valid, low empties/dups).")

    (ANALYSIS / "collection_validation.md").write_text("\n".join(L))

    # ---- Evolution snapshot (append) ----
    snap = {
        "ts": ts,
        "total_collected": total_collected,
        "total_valid": total_valid,
        "target_full": total_target,
        "pct_of_full": round(100 * total_collected / total_target, 1) if total_target else None,
        "models_with_data": len(models),
        "models_complete": sum(1 for m in by_model if by_model[m]["coverage_pct"] >= 100),
        "countries_covered": len(cov_country),
        "by_model_valid": {m: by_model[m]["valid"] for m in by_model},
    }
    with open(ANALYSIS / "collection_evolution.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(snap, ensure_ascii=False) + "\n")

    # ---- Console summary ----
    print(f"[{ts}] collected={total_collected} valid={total_valid} "
          f"models={len(models)} complete={snap['models_complete']} "
          f"countries={len(cov_country)}")
    if flags:
        print("FLAGS:")
        for f in flags[:12]:
            print("  -", f)
    else:
        print("No quality flags.")
    print(f"Report: {ANALYSIS/'collection_validation.md'}")
    print(f"Evolution appended: {ANALYSIS/'collection_evolution.jsonl'} (now {sum(1 for _ in load_jsonl(ANALYSIS/'collection_evolution.jsonl'))} snapshots)")


if __name__ == "__main__":
    main()
