#!/usr/bin/env python3
"""make_figures.py — as tres figuras do corpo (parecer de painel, rodada 2, P2).

Nenhum numero e digitado aqui: tudo vem de data/processed/*.json, das mesmas
fontes que alimentam latex/numbers.tex. Saida em figures/fig{1,2,3}.pdf.

  Fig 1  Razao de chances Sul/Norte por tarefa: estimativa condicional (GLMM com
         interceptos cruzados) contra a bruta com IC bootstrap por pais. Mostra de
         uma vez por que o nivel de inferencia importa: os intervalos diferem por
         um fator de cinco e so o agregado so-codigo se sustenta.
  Fig 2  H2 pareado por celula: ingles contra idioma nativo, por idioma.
  Fig 3  Acuracia media por pais, ordenada, com o tier como cor — a heterogeneidade
         que impede o gradiente de resolver.
"""
from __future__ import annotations
import collections, json, os, statistics as st, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "processed")
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)
K = json.load(open(os.path.join(P, "cluster_inference.json")))
GN = {"USA", "DEU", "JPN", "UK", "CAN", "AUS", "KOR", "FRA", "ITA", "PRT"}
ANA = os.path.join(ROOT, "data/confirmatory_PRIVATE/analysis")
rows = [json.loads(l) for l in open(os.path.join(ANA, "judge_scores_corrected.jsonl")) if l.strip()]
rows = [r for r in rows if not r.get("error") and "composite" in r]

plt.rcParams.update({"font.size": 9, "font.family": "serif", "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 200})
AZUL, CINZA = "#1f4e79", "#8c8c8c"

# ---------------------------------------------------------------- Figura 1
# ORs condicionais lidos do log do pipeline (mesma fonte das macros do corpo).
log = open(os.path.join(P, "last_run.log"), encoding="utf-8", errors="ignore").read()
cond = {}
for linha in log.splitlines():
    pecas = linha.split()
    if len(pecas) >= 7 and pecas[0] in ("T1", "T2", "T3", "T4", "T5") and pecas[2].endswith("%"):
        cond[pecas[0]] = (float(pecas[4]), float(pecas[5].strip("[,")), float(pecas[6].strip("]")))
ordem = ["T1", "T4", "T2", "T3"]          # T5 fora: teto de 99,6% vs 99,7%, sem contraste estimavel
rotulo = {"T1": "T1 standard\n(national value)", "T4": "T4 instruments\n(national)",
          "T2": "T2 local datum\n(national value)", "T3": "T3 health synthesis\n(international)"}
fig, ax = plt.subplots(figsize=(6.4, 3.0))
for i, t in enumerate(ordem):
    y = len(ordem) - i
    b = K["B"][t]
    lo, hi = b["ci_country_boot"]
    ax.plot([lo, hi], [y + 0.16, y + 0.16], color=AZUL, lw=1.6, solid_capstyle="butt")
    ax.plot(b["OR_raw"], y + 0.16, "o", color=AZUL, ms=5.5,
            label="raw OR, 95% country bootstrap" if i == 0 else None)
    if t in cond:
        o, clo, chi = cond[t]
        ax.plot([clo, chi], [y - 0.16, y - 0.16], color=CINZA, lw=1.6, solid_capstyle="butt")
        ax.plot(o, y - 0.16, "s", color=CINZA, ms=4.5,
                label="conditional OR (GLMM)" if i == 0 else None)
ax.axvline(1.0, color="black", lw=0.8, ls=(0, (4, 3)))
ax.set_yticks(range(1, len(ordem) + 1)); ax.set_yticklabels([rotulo[t] for t in ordem[::-1]])
ax.set_xscale("log"); ax.set_xlim(0.15, 2.2)
ax.set_xticks([0.2, 0.3, 0.5, 1.0, 2.0]); ax.set_xticklabels(["0.2", "0.3", "0.5", "1.0", "2.0"])
ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
ax.set_ylim(0.4, len(ordem) + 0.8)
ax.set_xlabel("Global South / Global North odds of returning the register value")
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=2, fontsize=8)
ax.set_title("Every per-task interval includes 1 once the country is the unit", fontsize=9, loc="left")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig1_or_by_task.pdf"), bbox_inches="tight"); plt.close(fig)

# ---------------------------------------------------------------- Figura 2
NAT = {"_pt": ("Portuguese", {"BRA", "PRT", "AGO"}), "_es": ("Spanish", {"MEX", "ARG", "PER", "COL", "CHL"}),
       "_hi": ("Hindi", {"IND"})}
cel = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows:
    pid = r["prompt_id"]; base, lang = pid, "en"
    for suf in NAT:
        if pid.endswith(suf):
            base, lang = pid[:-len(suf)], suf
    cel[(base, str(r["model_id"]))][lang].append(r["composite"])
pares = collections.defaultdict(list)
for (base, _m), v in cel.items():
    for suf, (nome, _p) in NAT.items():
        if v.get("en") and v.get(suf):
            pares[nome].append((st.mean(v["en"]), st.mean(v[suf])))
fig, axes = plt.subplots(1, 3, figsize=(6.6, 2.5), sharey=True)
for ax, nome in zip(axes, ["Spanish", "Portuguese", "Hindi"]):
    d = pares[nome]
    x = np.array([a for a, _ in d]); y = np.array([b for _, b in d])
    ax.scatter(x, y, s=7, alpha=0.35, color=AZUL, edgecolors="none")
    ax.plot([0, 1], [0, 1], color="black", lw=0.8, ls=(0, (4, 3)))
    ax.set_title(f"{nome}\n{100*(y-x).mean():+.1f} pp  (n={len(d)})", fontsize=8.5)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_xticks([0, 0.5, 1]); ax.set_yticks([0, 0.5, 1])
    ax.set_xlabel("English prompt")
axes[0].set_ylabel("Native-language prompt")
fig.suptitle("Points below the diagonal: the native-language answer scores worse", fontsize=9, x=0.02, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(os.path.join(FIG, "fig2_h2_pairs.pdf")); plt.close(fig)

# ---------------------------------------------------------------- Figura 3
acc = collections.defaultdict(list)
for r in rows:
    if not r["prompt_id"].endswith(("_pt", "_es", "_hi")):
        acc[r["country_iso3"]].append(r["composite"])
acc = {c: st.mean(v) for c, v in acc.items()}
paises = sorted(acc, key=acc.get)
fig, ax = plt.subplots(figsize=(6.4, 3.4))
for i, c in enumerate(paises):
    norte = c in GN
    ax.plot(acc[c], i, "o", color=AZUL if norte else CINZA, ms=5.5)
m_gn = st.mean([acc[c] for c in acc if c in GN]); m_gs = st.mean([acc[c] for c in acc if c not in GN])
ax.axvline(m_gn, color=AZUL, lw=0.9, ls=(0, (4, 3)))
ax.axvline(m_gs, color=CINZA, lw=0.9, ls=(0, (4, 3)))
ax.text(m_gn, len(paises) - 0.2, " GN mean", color=AZUL, fontsize=7.5, va="top")
ax.text(m_gs, len(paises) - 0.2, "GS mean ", color=CINZA, fontsize=7.5, va="top", ha="right")
ax.set_yticks(range(len(paises))); ax.set_yticklabels(paises, fontsize=7.5)
ax.set_xlabel("Mean composite accuracy, English prompts")
ax.plot([], [], "o", color=AZUL, ms=5.5, label="Global North")
ax.plot([], [], "o", color=CINZA, ms=5.5, label="Global South")
ax.legend(frameon=False, loc="lower right", fontsize=8)
ax.set_title("A tier difference layered over country-specific variation", fontsize=9, loc="left")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig3_country_dotplot.pdf")); plt.close(fig)

print("figuras escritas em figures/: fig1_or_by_task.pdf, fig2_h2_pairs.pdf, fig3_country_dotplot.pdf")
