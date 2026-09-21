#!/usr/bin/env python3
"""Vereditos de código (T1, T2, T3) num só lugar.

freeze_all_effects.py e export_corrected_scores.py reimplementavam a mesma regra
("T2/T3 com veredito determinístico substituem a acurácia factual"), e por isso
divergiram: o T1 entrou por código em 2026-09-21 e teria de ser acrescentado nos
dois. Agora a regra existe uma vez.

REGRA DE SELEÇÃO DA RESPOSTA — quando a mesma célula (prompt, modelo, réplica) tem
mais de uma resposta armazenada (21,9% das chaves), o veredito de código usa a
PRIMEIRA em ordem de arquivo (`file_order` mínimo), que é a resposta que o juiz
viu (run_judge_confirmatory.py lê os arquivos em ordem e pula chaves já julgadas).
Alinhar os dois instrumentos na mesma resposta é o que permite trocar só o
subcomponente factual e manter os demais do juiz. `todos()` devolve todas as
respostas por chave, para a análise de sensibilidade.

MAPA veredito → acurácia factual (T1):
  CORRECT / ABSTAIN_CORRECT → 1.0
  INCORRECT / FABRICATED / NO_VALUE / DONT_KNOW → 0.0
  UNRESOLVED → sem veredito (fica com o juiz)
  EXCLUDED (EGY: sem chave no registro) → célula EXCLUÍDA da análise
"""
from __future__ import annotations

import collections
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
NUMERIC = ROOT / "data" / "processed"
TASKS = ("T1", "T2", "T3")
FACTUAL = {"CORRECT": 1.0, "ABSTAIN_CORRECT": 1.0,
           "INCORRECT": 0.0, "FABRICATED": 0.0, "NO_VALUE": 0.0, "DONT_KNOW": 0.0}


def _rows(task: str) -> list[dict]:
    f = NUMERIC / f"numeric_scores_{task}.jsonl"
    if not f.exists():
        return []
    return [json.loads(l) for l in f.open(encoding="utf-8") if l.strip()]


def _key(r: dict) -> tuple:
    return (r["prompt_id"], str(r["model_id"]), int(r.get("replicate_idx", 0)))


def todos(tasks=TASKS) -> dict[tuple, list[dict]]:
    por = collections.defaultdict(list)
    for t in tasks:
        for r in _rows(t):
            por[_key(r)].append(r)
    for v in por.values():
        v.sort(key=lambda r: (r.get("file_order", 0), r.get("timestamp_utc") or ""))
    return por


def carregar(tasks=TASKS, selecao: str = "primeira") -> tuple[dict, set, dict]:
    """Devolve (det, excluidas, meta).
    det: chave → acurácia factual decidida por código.
    excluidas: chaves sem gabarito (EXCLUDED) que saem da análise.
    selecao: 'primeira' (a resposta que o juiz viu) | 'media' (todas as respostas).
    """
    det, excl, meta = {}, set(), {"por_task": collections.Counter()}
    for k, grupo in todos(tasks).items():
        # Só o T1 exclui a célula (EGY sem chave). Em T2/T3, EXCLUDED significa
        # "sem gabarito numérico" e a célula segue com o juiz, como antes.
        if grupo[0]["task"] == "T1" and any(r["verdict"] == "EXCLUDED" for r in grupo):
            excl.add(k)
            continue
        vals = [FACTUAL[r["verdict"]] for r in grupo if r["verdict"] in FACTUAL]
        if not vals:
            continue
        if selecao == "media":
            det[k] = sum(vals) / len(vals)
        else:
            primeiro = next((r for r in grupo if r["verdict"] in FACTUAL), None)
            det[k] = FACTUAL[primeiro["verdict"]]
        meta["por_task"][grupo[0]["task"]] += 1
    return det, excl, meta


if __name__ == "__main__":
    det, excl, meta = carregar()
    print(f"vereditos de código: {len(det)}  excluídas (sem chave): {len(excl)}")
    print("  por tarefa:", dict(meta["por_task"]))
