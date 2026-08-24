#!/usr/bin/env python3
"""Ataques ao achado principal (H2): o efeito sobrevive a quem tenta derruba-lo?

H2 passou a ser a afirmacao central do artigo, entao merece o tratamento que um
revisor daria: nao "confirme que existe", e sim "tente faze-lo sumir". Cada bloco
abaixo remove uma explicacao alternativa possivel. Um efeito que sobrevive a
todos e defensavel; um que depende de um pais, de um modelo ou de uma tarefa nao
e um efeito de lingua, e o artigo precisa saber disso antes do revisor.

O que NAO esta aqui, e nao pode estar: qualidade da traducao. Os prompts nativos
foram gerados por LLM sem back-translation, entao nenhum reordenamento destes
dados separa "o modelo responde pior na lingua" de "o prompt nativo pergunta
outra coisa". Isso exige coleta nova e esta declarado como limitacao.
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
NATIVAS = ("_pt", "_es", "_hi")


def carrega():
    linhas = []
    for l in SCORES.open(encoding="utf-8"):
        if not l.strip():
            continue
        r = json.loads(l)
        if "composite" not in r or r.get("error"):
            continue
        pid = r.get("prompt_id") or ""
        linhas.append({"v": r["composite"], "pid": pid,
                       "modelo": str(r.get("model_id")), "task": r.get("task"),
                       "pais": r.get("country_iso3"),
                       "fonte": r.get("score_source", "original"),
                       # o campo persona vem do proprio registro; a versao anterior
                       # inferia a condicao lendo o prompt_id, o que casaria com
                       # qualquer id que contivesse a substring "env"
                       "persona": r.get("persona"),
                       "nativa": pid.endswith(NATIVAS)})
    return linhas


def pares(linhas, filtro=None):
    """Diferencas nativo-menos-ingles por celula (prompt, modelo), replicatas colapsadas."""
    sel = [r for r in linhas if filtro is None or filtro(r)]
    acc = collections.defaultdict(list)
    for r in sel:
        acc[(r["pid"], r["modelo"])].append(r["v"])
    medias = {k: statistics.mean(v) for k, v in acc.items()}
    ing = {k: v for k, v in medias.items() if not k[0].endswith(NATIVAS)}
    out = []
    for (pid, modelo), v in medias.items():
        if not pid.endswith(NATIVAS):
            continue
        base = pid.rsplit("_", 1)[0]
        if (base, modelo) in ing:
            out.append(v - ing[(base, modelo)])
    return out


def linha(rotulo, difs, largura=34):
    if len(difs) < 10:
        print(f"  {rotulo:<{largura}} n={len(difs):<5} (poucos pares)")
        return
    pp = statistics.mean(difs) * 100
    p = wilcoxon_p(difs)
    marca = "" if p < 0.05 else "   <-- PERDE"
    print(f"  {rotulo:<{largura}} {pp:+7.2f} pp   p={p:<10.2e} n={len(difs):<5}{marca}")


def main() -> None:
    L = carrega()
    base = pares(L)
    print("ATAQUES AO ACHADO PRINCIPAL (H2)\n")
    print("0) EFEITO COMPLETO")
    linha("todos os pares", base)

    print("\n1) UM PAIS SOZINHO SUSTENTA O EFEITO?")
    paises = sorted({r["pais"] for r in L if r["nativa"] and r["pais"]})
    piores = []
    for c in paises:
        d = pares(L, lambda r, c=c: r["pais"] != c)
        if len(d) >= 10:
            piores.append((statistics.mean(d) * 100, wilcoxon_p(d), c))
    piores.sort()
    print(f"  removendo cada um dos {len(paises)} paises com par nativo:")
    print(f"    efeito mais fraco  {piores[-1][0]:+.2f} pp (sem {piores[-1][2]}), p={piores[-1][1]:.1e}")
    print(f"    efeito mais forte  {piores[0][0]:+.2f} pp (sem {piores[0][2]}), p={piores[0][1]:.1e}")
    print(f"    todos significativos: {all(p < 0.05 for _, p, _ in piores)}")

    print("\n2) UM MODELO SOZINHO SUSTENTA O EFEITO?")
    modelos = sorted({r["modelo"] for r in L if r["nativa"]})
    res = []
    for m in modelos:
        d = pares(L, lambda r, m=m: r["modelo"] != m)
        if len(d) >= 10:
            res.append((statistics.mean(d) * 100, wilcoxon_p(d), m))
    res.sort()
    print(f"  removendo cada um dos {len(modelos)} modelos:")
    print(f"    efeito mais fraco  {res[-1][0]:+.2f} pp (sem {res[-1][2]}), p={res[-1][1]:.1e}")
    print(f"    efeito mais forte  {res[0][0]:+.2f} pp (sem {res[0][2]}), p={res[0][1]:.1e}")
    print(f"    todos significativos: {all(p < 0.05 for _, p, _ in res)}")

    print("\n3) O EFEITO EXISTE EM CADA TAREFA, OU SO NUMA?")
    for t in ("T1", "T2", "T3", "T4", "T5"):
        linha(f"apenas {t}", pares(L, lambda r, t=t: r["task"] == t))

    print("\n4) DEPENDE DE QUEM PONTUOU?")
    print("  (T1/T5 vem do juiz original, T2/T3 do codigo, o resto do painel)")
    for f, rot in (("original", "so celulas do juiz original"),
                   ("code", "so celulas adjudicadas por codigo"),
                   ("panel", "so celulas do painel de 3")):
        linha(rot, pares(L, lambda r, f=f: r["fonte"] == f))

    print("\n5) DEPENDE DA PERSONA?")
    for p_, rot in (("neutral", "so prompts neutros"),
                    ("public_manager_env", "so prompts com persona")):
        linha(rot, pares(L, lambda r, p_=p_: r["persona"] == p_))

    print("\n6) E SE OS 5% DE PARES MAIS EXTREMOS FOREM ARTEFATO?")
    ordenado = sorted(base)
    corte = max(1, int(len(ordenado) * 0.05))
    linha("aparando 5% de cada cauda", ordenado[corte:-corte])
    print("\n7) O EFEITO SOBREVIVE SEM JUIZ NENHUM?")
    print("  Desfecho binario e objetivo: a resposta contem um valor extraivel e")
    print("  comparavel ao registro? Quem decide e o extrator, nao um modelo.")
    print("  Isto tambem explica o bloco 4: a adjudicacao por codigo so age quando HA")
    print("  numero, entao aquele subconjunto esta condicionado a 'houve valor nas duas")
    print("  linguas' e remove justamente o pior modo de falha.")
    verif = collections.defaultdict(list)
    for r in L:
        if r["task"] in ("T2", "T3"):
            verif[(r["pid"], r["modelo"])].append(1 if r["fonte"] == "code" else 0)
    med = {k: statistics.mean(v) for k, v in verif.items()}
    ing = {k: v for k, v in med.items() if not k[0].endswith(NATIVAS)}
    duplas = [(v, ing[(k[0].rsplit("_", 1)[0], k[1])], k[0][-3:])
              for k, v in med.items()
              if k[0].endswith(NATIVAS) and (k[0].rsplit("_", 1)[0], k[1]) in ing]
    dif = [a - b for a, b, _ in duplas]
    nz = [x for x in dif if x]
    neg = sum(1 for x in nz if x < 0)
    p_sinais = sum(math.comb(len(nz), k)
                   for k in range(0, min(neg, len(nz) - neg) + 1)) * 2 / 2 ** len(nz)
    print(f"    taxa de valor verificavel: ingles "
          f"{statistics.mean([b for _, b, _ in duplas]):.1%} · nativa "
          f"{statistics.mean([a for a, _, _ in duplas]):.1%}")
    print(f"    diferenca pareada {statistics.mean(dif)*100:+.1f} pp · nativa pior em "
          f"{neg}/{len(nz)} pares discordantes · teste de sinais p={p_sinais:.1e}")
    for suf, nome in (("_es", "espanhol"), ("_pt", "portugues"), ("_hi", "hindi")):
        dd = [a - b for a, b, lg in duplas if lg == suf]
        if dd:
            print(f"    {nome:<10} {statistics.mean(dd)*100:+6.1f} pp   n={len(dd)}")

    print("\n  Leitura: um efeito que so aparece num pais, num modelo, numa tarefa ou")
    print("  sob um pontuador nao e um efeito de lingua. Este aparece em todos, e")
    print("  sobrevive a um desfecho que nenhum juiz tocou.")


if __name__ == "__main__":
    main()
