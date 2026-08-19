#!/usr/bin/env python3
"""Monitor de integridade da repontuação por painel.

Roda periodicamente durante a coleta. Não é um contador de progresso: é um
detector de coleta que está andando e produzindo lixo, que é o modo de falha
caro. Sai com código 1 quando encontra algo que exige ação.

CHECAGENS
---------
1  PROGRESSO      quantos scores, ritmo, previsão de término
2  PARIDADE       os três juízes estão acompanhando? um parou?
3  DEGENERAÇÃO    variância por juiz. Juiz que dá sempre a mesma nota está quebrado.
4  CONCORDÂNCIA   correlação entre juízes. Despencar indica um deles desalinhado.
5  DUPLICATAS     mesma (prompt, modelo, juiz) gravada duas vezes.
6  INTEGRIDADE    JSON malformado, campos fora de [0,1], rationale vazio.
7  COBERTURA      alguma tarefa ou país ficando para trás.
"""
from __future__ import annotations

import collections
import json
import pathlib
import statistics
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCORES = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_panel_repontuacao.jsonl"
STATE = ROOT / "data" / "processed" / ".monitor_state.json"
SUBS = ("factual_accuracy", "contextual_completeness", "citation_quality",
        "calibration", "absence_of_hallucination")
ESPERADO_ALVOS = 3192   # apos alinhar a deduplicacao ao pipeline original
JUIZES = ("gemini_2_5_pro", "claude_sonnet_4_6", "deepseek_v3")


def main() -> int:
    alertas: list[str] = []
    if not SCORES.exists():
        print("ALERTA: arquivo de scores nao existe ainda")
        return 1

    rows, malformadas = [], 0
    for line in SCORES.open(encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            malformadas += 1

    n = len(rows)
    total = ESPERADO_ALVOS * len(JUIZES)
    print(f"┌─ MONITOR · {time.strftime('%H:%M:%S')}")
    print(f"│ 1 PROGRESSO   {n:>6} / {total} scores  ({100*n/total:.1f}%)")

    # ritmo, comparando com o estado anterior
    agora = time.time()
    if STATE.exists():
        try:
            st = json.loads(STATE.read_text())
            dt = agora - st["t"]
            dn = n - st["n"]
            if dt > 60:
                por_min = dn / (dt / 60)
                print(f"│               ritmo {por_min:.1f} scores/min", end="")
                if por_min > 0:
                    falta = (total - n) / por_min
                    print(f" · faltam ~{falta/60:.1f} h")
                else:
                    print()
                if dn == 0:
                    alertas.append("coleta PAROU: nenhum score novo desde a ultima checagem")
        except Exception:
            pass
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"t": agora, "n": n}))

    if malformadas:
        alertas.append(f"{malformadas} linhas JSON malformadas no arquivo")

    if not rows:
        print("└─ sem dados ainda")
        return 1

    # 2 paridade entre juízes
    porj = collections.Counter(r.get("judge") for r in rows)
    print("│ 2 PARIDADE    " + " · ".join(f"{j.split('_')[0]}={porj.get(j,0)}" for j in JUIZES))
    if porj:
        mx = max(porj.values())
        for j in JUIZES:
            if porj.get(j, 0) < mx * 0.7:
                alertas.append(f"juiz {j} ficou para tras ({porj.get(j,0)} vs {mx}); "
                               f"provavel falha de API")

    # 3 degeneração: variância por juiz.
    #
    # Olhar só factual_accuracy dá falso positivo: o resíduo de T2 que chega ao
    # painel é, por construção, resposta SEM valor numérico, e a nota correta ali
    # é 0.0 para todos os juízes. Um juiz de verdade quebrado não varia em NENHUM
    # dos cinco subcomponentes, então o teste é sobre o conjunto.
    print("│ 3 DEGENERACAO ", end="")
    linha = []
    for j in JUIZES:
        sub = [r for r in rows if r.get("judge") == j]
        if len(sub) < 15:
            linha.append(f"{j.split('_')[0]}=n/a"); continue
        sds = []
        for k in SUBS:
            vals = [r[k] for r in sub if isinstance(r.get(k), (int, float))]
            if vals:
                sds.append(statistics.pstdev(vals))
        fa = [r["factual_accuracy"] for r in sub if isinstance(r.get("factual_accuracy"), (int, float))]
        linha.append(f"{j.split('_')[0]}: fa={statistics.mean(fa):.2f} sd_max={max(sds):.2f}")
        if max(sds) < 0.05:
            alertas.append(f"juiz {j}: desvio maximo {max(sds):.3f} em TODOS os cinco "
                           f"subcomponentes, provavelmente quebrado")
    print(" · ".join(linha))

    # 4 concordância par a par no que já foi julgado pelos três
    porchave = collections.defaultdict(dict)
    for r in rows:
        if isinstance(r.get("factual_accuracy"), (int, float)):
            porchave[(r["prompt_id"], str(r.get("model_id")),
                  int(r.get("replicate_idx", 0)))][r["judge"]] = r["factual_accuracy"]
    completos = [v for v in porchave.values() if len(v) == len(JUIZES)]
    print(f"│ 4 CONCORDANCIA {len(completos)} itens com os 3 juizes", end="")
    if len(completos) >= 30:
        pares = []
        for a in range(len(JUIZES)):
            for b in range(a + 1, len(JUIZES)):
                xs = [c[JUIZES[a]] for c in completos]
                ys = [c[JUIZES[b]] for c in completos]
                if statistics.pstdev(xs) > 0 and statistics.pstdev(ys) > 0:
                    mx, my = statistics.mean(xs), statistics.mean(ys)
                    cov = sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / len(xs)
                    r_ = cov / (statistics.pstdev(xs) * statistics.pstdev(ys))
                    pares.append((f"{JUIZES[a].split('_')[0]}×{JUIZES[b].split('_')[0]}", r_))
        print("  " + " · ".join(f"{k}={v:+.2f}" for k, v in pares))
        for k, v in pares:
            if v < 0.30:
                alertas.append(f"concordancia baixa em {k} (r={v:+.2f}): um juiz "
                               f"pode estar interpretando a rubrica de outro jeito")
    else:
        print()

    # 5 duplicatas
    # a chave inclui replicate_idx: o desenho tem replicas legitimas do mesmo
    # (prompt, modelo), e conta-las como duplicata era falso positivo
    chaves = collections.Counter((r["prompt_id"], str(r.get("model_id")),
                                  int(r.get("replicate_idx", 0)), r.get("judge"))
                                 for r in rows)
    dups = sum(1 for v in chaves.values() if v > 1)
    print(f"│ 5 DUPLICATAS  {dups}")
    if dups:
        alertas.append(f"{dups} combinacoes (prompt, modelo, juiz) gravadas mais de uma vez")

    # 6 integridade dos valores
    fora, sem_rat = 0, 0
    for r in rows:
        for k in SUBS:
            v = r.get(k)
            if not isinstance(v, (int, float)) or not (0.0 <= v <= 1.0):
                fora += 1
        if not str(r.get("rationale", "")).strip():
            sem_rat += 1
    print(f"│ 6 INTEGRIDADE valores fora de [0,1]: {fora} · sem rationale: {sem_rat}")
    if fora:
        alertas.append(f"{fora} valores fora do intervalo [0,1]")
    if sem_rat > n * 0.2:
        alertas.append(f"{sem_rat} scores sem rationale ({100*sem_rat/n:.0f}%)")

    # 7 cobertura por tarefa
    portask = collections.Counter(r.get("task") for r in rows)
    print("│ 7 COBERTURA   " + " · ".join(f"{k}={v}" for k, v in sorted(portask.items())))

    if alertas:
        print("├─ PENDENCIAS")
        for a in alertas:
            print(f"│  ⚠ {a}")
        print("└─")
        return 1
    print("└─ tudo integro")
    return 0


if __name__ == "__main__":
    sys.exit(main())
