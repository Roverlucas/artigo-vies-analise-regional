"""
krippendorff_3judges.py — Three-judge inter-rater reliability.

Judges:
  J1 = gpt5_mini       (primary, full)    judge_scores_confirmatory.jsonl
  J2 = claude_sonnet   (out-of-sample)    judge_scores_claude_sonnet_sample.jsonl
  J3 = gemini_2_5_pro  (out-of-sample)    judge_scores_gemini_2_5_pro_sample.jsonl

On the items judged by all three (matched on model_id+prompt_id+replicate_idx),
report Krippendorff's alpha (interval), three-way ICC(2,1), and pairwise Pearson
on the `composite` score. This strengthens the single-judge limitation: if the
three independent judges agree, the composite is judge-robust.

Krippendorff interval alpha (Krippendorff 2011), exact small-sample form:
  alpha = 1 - Do/De
  Do = (1/n) * sum_u (1/(m_u-1)) * sum_{i!=j in u} (x_ui-x_uj)^2
  De = (1/(n*(n-1))) * sum_{g!=h global} (x_g-x_h)^2
with n the total number of pairable values.

Usage:  python -m code.analysis.krippendorff_3judges
"""
from __future__ import annotations
import json, math
from pathlib import Path

A = Path(__file__).parent.parent.parent / "data" / "confirmatory_PRIVATE" / "analysis"
PRIMARY = ("gpt5_mini", A / "judge_scores_confirmatory.jsonl")
KEY = ("model_id", "prompt_id", "replicate_idx")


def discover_files():
    """Primary judge + every out-of-sample panel judge (judge_scores_<m>_sample.jsonl)."""
    files = {PRIMARY[0]: PRIMARY[1]}
    for fp in sorted(A.glob("judge_scores_*_sample.jsonl")):
        name = fp.name[len("judge_scores_"):-len("_sample.jsonl")]
        files[name] = fp
    return files


def load(fp):
    out = {}
    if not fp.exists():
        return out
    for line in open(fp, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("error"):
            continue
        c = d.get("composite")
        if c is None:
            continue
        out[tuple(d.get(k) for k in KEY)] = float(c)
    return out


def krippendorff_interval(units):
    """units: list of lists of values (one list per item, m>=2 values)."""
    units = [u for u in units if len(u) >= 2]
    n = sum(len(u) for u in units)
    if n < 2:
        return float("nan")
    # observed
    do_num = 0.0
    for u in units:
        m = len(u)
        s = sum(u); s2 = sum(v * v for v in u)
        sq_ordered = 2 * (m * s2 - s * s)  # sum_{i!=j}(x_i-x_j)^2
        do_num += sq_ordered / (m - 1)
    Do = do_num / n
    # expected (global)
    allv = [v for u in units for v in u]
    S = sum(allv); S2 = sum(v * v for v in allv)
    de_ordered = 2 * (n * S2 - S * S)
    De = de_ordered / (n * (n - 1))
    return 1 - Do / De if De > 0 else float("nan")


def pearson(x, y):
    n = len(x)
    if n < 2:
        return float("nan")
    mx = sum(x) / n; my = sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x); syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else float("nan")


def _icc_ms(rows):
    """Return (MSR, MSC, MSE, n, k) for a two-way random-effects design."""
    n = len(rows); k = len(rows[0])
    grand = sum(v for r in rows for v in r) / (n * k)
    row_m = [sum(r) / k for r in rows]
    col_m = [sum(rows[i][j] for i in range(n)) / n for j in range(k)]
    SSR = k * sum((rm - grand) ** 2 for rm in row_m)
    SSC = n * sum((cm - grand) ** 2 for cm in col_m)
    SST = sum((v - grand) ** 2 for r in rows for v in r)
    SSE = SST - SSR - SSC
    MSR = SSR / (n - 1); MSC = SSC / (k - 1); MSE = SSE / ((n - 1) * (k - 1))
    return MSR, MSC, MSE, n, k


def icc21(rows):
    """ICC(2,1): reliability of a SINGLE judge (absolute agreement)."""
    MSR, MSC, MSE, n, k = _icc_ms(rows)
    denom = MSR + (k - 1) * MSE + k * (MSC - MSE) / n
    return (MSR - MSE) / denom if denom > 0 else float("nan")


def icc2k(rows):
    """ICC(2,k): reliability of the MEAN of k judges (the panel composite).
    This is the Spearman-Brown-stepped-up reliability — the key argument that a
    panel mean is highly reliable even when individual judges agree only moderately."""
    MSR, MSC, MSE, n, k = _icc_ms(rows)
    denom = MSR + (MSC - MSE) / n
    return (MSR - MSE) / denom if denom > 0 else float("nan")


def main():
    FILES = discover_files()
    J = {name: load(fp) for name, fp in FILES.items()}
    for name, d in J.items():
        print(f"  {name:16s}: {len(d):5d} scores{'  (empty)' if not d else ''}")
    # Fixed reliability sample = items both anchor judges (claude, gemini) scored.
    anchors = [a for a in ("claude_sonnet", "gemini_2_5_pro") if J.get(a)]
    fixed = set.intersection(*[set(J[a]) for a in anchors]) if len(anchors) == 2 else set()
    if not fixed:
        fixed = set.intersection(*[set(J[n]) for n in J if J[n]])
    # Include a judge only if it covers >=90% of the fixed sample (drops exhausted judges).
    names, dropped = [], []
    for n in J:
        if not J[n]:
            continue
        cov = len(set(J[n]) & fixed) / max(1, len(fixed))
        (names if cov >= 0.90 else dropped).append((n, cov))
    if dropped:
        print(f"\n  excluded (sample coverage <90%): " +
              ", ".join(f"{n} ({c*100:.0f}%)" for n, c in dropped))
    names = [n for n, _ in names]
    common = fixed & set.intersection(*[set(J[n]) for n in names]) if names else set()
    k = len(names)
    print(f"\n  panel: {k} judges {names}")
    print(f"  fixed sample (claude∩gemini): {len(fixed)} | items judged by ALL {k}: {len(common)}")
    if len(common) < 10:
        print("  (panel still incomplete — re-run when more judges finish)")
        if not common:
            return
    keys = sorted(common)
    cols = {n: [J[n][key] for key in keys] for n in names}
    units = [[cols[n][i] for n in names] for i in range(len(keys))]
    alpha = krippendorff_interval(units)
    icc1 = icc21(units)
    icck = icc2k(units)
    print(f"\n  Krippendorff alpha (interval)        = {alpha:.3f}")
    print(f"  ICC(2,1)  single-judge reliability   = {icc1:.3f}")
    print(f"  ICC(2,{k}) PANEL-MEAN reliability      = {icck:.3f}   <-- composite")
    print(f"  Pairwise Pearson:")
    for i in range(k):
        for j in range(i + 1, k):
            print(f"    {names[i]:14s} x {names[j]:14s} = {pearson(cols[names[i]], cols[names[j]]):+.3f}")
    out = A / "judge_panel_reliability.json"
    payload = {"judges": names, "k": k, "n_common": len(common),
        "krippendorff_alpha": alpha, "icc_2_1": icc1, "icc_2_k": icck,
        "pairwise_pearson": {f"{names[i]}|{names[j]}": pearson(cols[names[i]], cols[names[j]])
                             for i in range(k) for j in range(i + 1, k)}}
    out.write_text(json.dumps(payload, indent=2))
    print(f"\n  saved -> {out.name}")


if __name__ == "__main__":
    main()
