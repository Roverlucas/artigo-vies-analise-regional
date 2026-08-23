#!/usr/bin/env python3
"""O teste decisivo de H2: o efeito sobrevive entre traducoes verificadamente fieis?

A objecao que este script existe para responder e a unica que os escores sozinhos
nao respondem: se os prompts nativos foram gerados por um LLM, talvez o modelo nao
responda pior na lingua — talvez o prompt nativo pergunte outra coisa.

back_translation_audit.py classificou os 90 prompts nativos em FAITHFUL e
DIVERGENT por back-translation independente com julgamento conservador. Aqui o
efeito de H2 e reestimado APENAS sobre os pares cujo prompt nativo foi verificado
como fiel. Se ele persiste com magnitude semelhante, a traducao nao o explica, e a
objecao esta respondida com dado em vez de argumento.

Reportamos tambem o efeito no subconjunto DIVERGENT. Se a infidelidade fosse a
causa, o efeito deveria estar concentrado la.
"""
from __future__ import annotations

import collections
import json
import math
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.nonparametric import wilcoxon_p  # noqa: E402

SCORES = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_scores_corrected.jsonl"
AUDIT = ROOT / "data" / "processed" / "back_translation_audit.jsonl"
NATIVAS = ("_pt", "_es", "_hi")


def pares_por_prompt():
    """Diferenca nativo-menos-ingles por celula, indexada pelo prompt_id nativo."""
    acc = collections.defaultdict(list)
    for linha in SCORES.open(encoding="utf-8"):
        if not linha.strip():
            continue
        r = json.loads(linha)
        if "composite" not in r or r.get("error"):
            continue
        acc[(r.get("prompt_id") or "", str(r.get("model_id")))].append(r["composite"])
    med = {k: statistics.mean(v) for k, v in acc.items()}
    ing = {k: v for k, v in med.items() if not k[0].endswith(NATIVAS)}
    out = collections.defaultdict(list)
    for (pid, modelo), v in med.items():
        if not pid.endswith(NATIVAS):
            continue
        base = pid.rsplit("_", 1)[0]
        if (base, modelo) in ing:
            out[pid].append(v - ing[(base, modelo)])
    return out


def bloco(rotulo, difs, largura=30):
    if len(difs) < 10:
        print(f"  {rotulo:<{largura}} n={len(difs)} (poucos pares para testar)")
        return
    print(f"  {rotulo:<{largura}} {statistics.mean(difs)*100:+7.2f} pp   "
          f"p={wilcoxon_p(difs):<10.2e} n={len(difs)}")


def main() -> None:
    if not AUDIT.exists():
        print("auditoria ausente; rode back_translation_audit.py antes")
        return
    aud = {}
    for linha in AUDIT.open(encoding="utf-8"):
        r = json.loads(linha)
        aud[r["prompt_id"]] = r

    n_fiel = sum(1 for r in aud.values() if r["verdict"] == "FAITHFUL")
    print(f"AUDITORIA DE TRADUCAO — censo de {len(aud)} prompts nativos")
    print(f"  fieis: {n_fiel} ({n_fiel/len(aud):.0%}) · divergentes: {len(aud)-n_fiel}")

    falhas = collections.Counter(it for r in aud.values() for it in r["itens_falhos"])
    if falhas:
        print("  itens que mais falharam:")
        for it, n in falhas.most_common():
            print(f"    {it:<16} {n}")

    por_lingua = collections.defaultdict(lambda: [0, 0])
    for r in aud.values():
        por_lingua[r["language"]][r["verdict"] == "FAITHFUL"] += 1
    print("  fidelidade por lingua:")
    for lg in sorted(por_lingua):
        div, fiel = por_lingua[lg]
        print(f"    {lg}: {fiel}/{fiel+div} fieis")

    pares = pares_por_prompt()
    fiel = [d for pid, ds in pares.items()
            if aud.get(pid, {}).get("verdict") == "FAITHFUL" for d in ds]
    div = [d for pid, ds in pares.items()
           if aud.get(pid, {}).get("verdict") == "DIVERGENT" for d in ds]
    todos = [d for ds in pares.values() for d in ds]

    print("\nEFEITO DE H2 POR FIDELIDADE DA TRADUCAO")
    bloco("todos os pares", todos)
    bloco("so traducoes FIEIS", fiel)
    bloco("so traducoes DIVERGENTES", div)

    print("\n  Leitura: se a traducao explicasse o efeito, ele estaria concentrado")
    print("  no bloco divergente e ausente no fiel.")


if __name__ == "__main__":
    main()
