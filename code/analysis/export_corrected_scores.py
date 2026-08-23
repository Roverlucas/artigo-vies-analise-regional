#!/usr/bin/env python3
"""Exporta os escores corrigidos no MESMO esquema do arquivo original.

Por que um exportador em vez de corrigir dentro de cada analise: o modelo misto,
a re-estimacao bayesiana e os E-values leem
`judge_scores_confirmatory.jsonl` diretamente. Reimplementar a regra de
substituicao dentro de cada um seria tres chances de divergir da regra usada no
congelamento. Aqui a regra existe uma vez e todos consomem o mesmo arquivo.

REGRA (identica a de freeze_all_effects.py)
1. T2/T3 com veredito deterministico: troca-se a acuracia factual pelo veredito do
   codigo e recompoe-se o composto com os pesos do instrumento.
2. Residuo de T2/T3 e T4 inteira: media do painel de tres juizes, tanto no
   composto quanto em cada subcomponente.
3. T1 e T5 entram intactas.

O registro de saida preserva todos os campos do original e acrescenta
`score_source` (original | code | panel), para que qualquer analise possa
segmentar por procedencia sem refazer a juncao.
"""
from __future__ import annotations

import collections
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.llm_judge import RUBRIC_WEIGHTS as PESOS  # noqa: E402

ANA = ROOT / "data" / "confirmatory_PRIVATE" / "analysis"
ORIG = ANA / "judge_scores_confirmatory.jsonl"
PANEL = ANA / "judge_panel_repontuacao.jsonl"
NUMERIC = ROOT / "data" / "processed"
SAIDA = ANA / "judge_scores_corrected.jsonl"

SUBS = tuple(PESOS)


def composto(d: dict) -> float:
    return sum(d[k] * w for k, w in PESOS.items())


def main() -> None:
    det = {}
    for t in ("T2", "T3"):
        f = NUMERIC / f"numeric_scores_{t}.jsonl"
        if not f.exists():
            continue
        for linha in f.open(encoding="utf-8"):
            r = json.loads(linha)
            if r["verdict"] in ("CORRECT", "INCORRECT"):
                det[(r["prompt_id"], str(r["model_id"]),
                     int(r.get("replicate_idx", 0)))] = (
                    1.0 if r["verdict"] == "CORRECT" else 0.0)

    por = collections.defaultdict(list)
    for linha in PANEL.open(encoding="utf-8"):
        r = json.loads(linha)
        if all(k in r for k in SUBS):
            por[(r["prompt_id"], str(r["model_id"]),
                 int(r.get("replicate_idx", 0)))].append(r)
    painel = {k: {s: statistics.mean(x[s] for x in v) for s in SUBS}
              for k, v in por.items()}

    # POLITICA DE DESEMPATE: media, nao "primeira em ordem alfabetica de arquivo".
    # 11,5% das celulas pontuadas tem mais de um escore, vindos de re-execucoes em
    # datas diferentes. A regra anterior fazia um numero do artigo depender do nome
    # de um arquivo. A media e deterministica, independe da ordem de leitura e usa
    # toda a informacao coletada. duplicate_policy.py mostra que a escolha entre as
    # quatro politicas plausiveis move os efeitos em no maximo 0,06 pp.
    agrupado = collections.defaultdict(list)
    for linha in ORIG.open(encoding="utf-8"):
        if not linha.strip():
            continue
        r = json.loads(linha)
        if "composite" not in r or r.get("error"):
            continue
        if "JUDGE_API_ERROR" in str(r.get("rationale", "")):
            continue
        agrupado[(r.get("prompt_id"), str(r.get("model_id")),
                  int(r.get("replicate_idx", 0)))].append(r)

    n = {"original": 0, "code": 0, "panel": 0}
    n_media = 0
    with SAIDA.open("w", encoding="utf-8") as out:
        for _chave, grupo in agrupado.items():
            r = dict(grupo[0])
            if len(grupo) > 1:
                for campo in ("composite", *SUBS):
                    vals = [g[campo] for g in grupo if isinstance(g.get(campo), (int, float))]
                    if vals:
                        r[campo] = statistics.mean(vals)
                r["n_respostas_agregadas"] = len(grupo)
                n_media += 1
            k = (r.get("prompt_id"), str(r.get("model_id")),
                 int(r.get("replicate_idx", 0)))
            origem = "original"
            if k in det:
                # o codigo decide APENAS a acuracia factual; os demais
                # subcomponentes seguem vindo do juiz original, senao estariamos
                # trocando o instrumento inteiro sem necessidade
                r["factual_accuracy"] = det[k]
                r["composite"] = composto({s: r.get(s, 0.0) for s in SUBS})
                origem = "code"
            elif k in painel:
                for s in SUBS:
                    r[s] = painel[k][s]
                r["composite"] = composto(painel[k])
                origem = "panel"
            r["score_source"] = origem
            n[origem] += 1
            out.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"escrito: {SAIDA}")
    print(f"  original {n['original']} · codigo {n['code']} · painel {n['panel']}"
          f"  (total {sum(n.values())})")
    print(f"  celulas com mais de uma resposta, resolvidas por media: {n_media}")


if __name__ == "__main__":
    main()
