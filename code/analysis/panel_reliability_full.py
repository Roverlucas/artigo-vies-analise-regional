#!/usr/bin/env python3
"""Confiabilidade do painel de repontuacao, sobre a base inteira.

Por que nao basta o numero que o manuscrito ja reporta: aquele ICC vem do painel
de calibracao, 131 itens julgados por quatro modelos numa amostra fixa. O escore
que agora entra nas analises e a media de TRES juizes sobre 3.190 itens — base 24
vezes maior e, o que importa mais, e a mesma base que produz os efeitos. Reportar
a confiabilidade de uma amostra de calibracao enquanto os efeitos vem de outra
deixa o leitor sem como julgar o instrumento que de fato foi usado.

A quantidade operativa e ICC(2,3): o escore usado e a MEDIA dos tres juizes, nao o
julgamento de um. ICC(2,1) vai junto porque e ele que diz o quanto um juiz sozinho
— o desenho do artigo publicado — era confiavel.
"""
from __future__ import annotations

import collections
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.krippendorff_3judges import (  # noqa: E402
    icc21, icc2k, krippendorff_interval, pearson,
)
from code.analysis.llm_judge import RUBRIC_WEIGHTS as PESOS  # noqa: E402

PANEL = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_panel_repontuacao.jsonl"
SAIDA = ROOT / "data" / "processed" / "panel_reliability_full.json"
JUIZES = ("gemini_2_5_pro", "claude_sonnet_4_6", "deepseek_v3")


def composto(d: dict) -> float:
    return sum(d[k] * w for k, w in PESOS.items())


def main() -> None:
    por = collections.defaultdict(dict)
    for linha in PANEL.open(encoding="utf-8"):
        r = json.loads(linha)
        if not all(k in r for k in PESOS):
            continue
        chave = (r["prompt_id"], str(r["model_id"]), int(r.get("replicate_idx", 0)))
        por[chave][r["judge"]] = composto(r)

    completos = [[v[j] for j in JUIZES] for v in por.values()
                 if all(j in v for j in JUIZES)]
    print(f"itens no painel: {len(por)} · com os 3 juizes: {len(completos)}")

    res = {
        "n_itens": len(completos),
        "krippendorff_alpha": krippendorff_interval(completos),
        "icc21": icc21(completos),
        "icc2k": icc2k(completos),
        "k_juizes": len(JUIZES),
    }
    print(f"  Krippendorff alpha (intervalar)      = {res['krippendorff_alpha']:.3f}")
    print(f"  ICC(2,1) juiz unico                  = {res['icc21']:.3f}")
    print(f"  ICC(2,3) media do painel  <- operativa = {res['icc2k']:.3f}")

    print("  Pearson par a par:")
    for i, a in enumerate(JUIZES):
        for b in JUIZES[i + 1:]:
            x = [v[a] for v in por.values() if a in v and b in v]
            y = [v[b] for v in por.values() if a in v and b in v]
            r = pearson(x, y)
            res[f"pearson_{a}_{b}"] = r
            print(f"    {a:18s} x {b:18s} = {r:+.3f}")

    media_juiz = {j: statistics.mean([v[j] for v in por.values() if j in v])
                  for j in JUIZES}
    res["media_por_juiz"] = media_juiz
    print("  media do composto por juiz: "
          + " · ".join(f"{j}={m:.3f}" for j, m in media_juiz.items()))

    SAIDA.write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"\n  escrito: {SAIDA}")


if __name__ == "__main__":
    main()
