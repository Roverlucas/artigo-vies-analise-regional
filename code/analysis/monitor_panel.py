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
import re
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCORES = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_panel_repontuacao.jsonl"
STATE = ROOT / "data" / "processed" / ".monitor_state.json"
SUBS = ("factual_accuracy", "contextual_completeness", "citation_quality",
        "calibration", "absence_of_hallucination")
ESPERADO_ALVOS = 3192   # apos alinhar a deduplicacao ao pipeline original
JUIZES = ("gemini_2_5_pro", "claude_sonnet_4_6", "deepseek_v3")


def _key(nome: str) -> str | None:
    try:
        for line in (pathlib.Path.home() / ".env").read_text(encoding="utf-8").splitlines():
            m = re.match(rf'\s*(?:export\s+)?{nome}\s*=\s*["\']?([^"\'\s]+)', line)
            if m:
                return m.group(1)
    except Exception:
        pass
    return None


def _painel_vivo() -> bool:
    """Ha coleta em andamento? Muda a leitura de um 429 na sonda."""
    import subprocess
    try:
        return subprocess.run(["pgrep", "-f", "run_judge_panel"],
                              capture_output=True).returncode == 0
    except Exception:
        return False


def probe_providers() -> dict[str, str]:
    """OK, SEM_CREDITO, RATE_LIMIT ou HTTP <codigo>, por juiz."""
    alvos = {
        "gemini_2_5_pro": (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-pro:generateContent?key={_key('GEMINI_API_KEY')}",
            {"contents": [{"parts": [{"text": "ok"}]}],
             "generationConfig": {"maxOutputTokens": 1200}}, {}),
        "claude_sonnet_4_6": (
            "https://api.anthropic.com/v1/messages",
            {"model": "claude-sonnet-4-6", "max_tokens": 5,
             "messages": [{"role": "user", "content": "ok"}]},
            {"x-api-key": _key("ANTHROPIC_API_KEY") or "", "anthropic-version": "2023-06-01"}),
        "deepseek_v3": (
            "https://api.deepseek.com/chat/completions",
            {"model": "deepseek-chat", "max_tokens": 5,
             "messages": [{"role": "user", "content": "ok"}]},
            {"Authorization": f"Bearer {_key('DEEPSEEK_API_KEY')}"}),
    }
    out = {}
    for j, (url, payload, hdr) in alvos.items():
        try:
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", **hdr})
            urllib.request.urlopen(req, timeout=45)
            out[j] = "OK"
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            out[j] = ("SEM_CREDITO" if "credit balance" in body
                      else "RATE_LIMIT" if e.code == 429 else f"HTTP {e.code}")
        except Exception as e:
            out[j] = type(e).__name__
    return out


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

    saude = probe_providers()
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
                    # Parada com causa conhecida e sem acao possivel nao e pendencia.
                    # Se o unico juiz que ainda tem trabalho esta sem cota ou sem
                    # credito, parar e o comportamento correto: alertar todo ciclo
                    # so treina quem le a ignorar o alerta.
                    bloqueados = [j for j, e in saude.items()
                                  if e in ("SEM_CREDITO", "RATE_LIMIT")]
                    if bloqueados and not _painel_vivo():
                        print(f"│               coleta parada aguardando "
                              f"{', '.join(bloqueados)}. Nada a fazer ate o reset.")
                    else:
                        alertas.append("coleta PAROU: nenhum score novo desde a "
                                       "ultima checagem, e os provedores respondem")
        except Exception:
            pass
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"t": agora, "n": n}))

    if malformadas:
        alertas.append(f"{malformadas} linhas JSON malformadas no arquivo")

    if not rows:
        print("└─ sem dados ainda")
        return 1

    # 2 paridade entre juízes.
    #
    # Um juiz para atrás por três razões diferentes, e tratá-las como a mesma
    # coisa produz alarme falso: (a) provedor sem saldo, que é decisão de quem
    # paga e não defeito; (b) o juiz é simplesmente mais lento, e o Gemini 2.5 Pro
    # leva ~14 s por chamada contra ~2 s do DeepSeek; (c) falha de verdade. Só (c)
    # é pendência, então o monitor consulta o provedor antes de acusar.
    porj = collections.Counter(r.get("judge") for r in rows)
    print("│ 2 PARIDADE    " + " · ".join(f"{j.split('_')[0]}={porj.get(j,0)}" for j in JUIZES))
    if porj:
        mx = max(porj.values())
        for j in JUIZES:
            if porj.get(j, 0) < mx * 0.7:
                estado = saude.get(j, "?")
                if estado == "SEM_CREDITO":
                    print(f"│               {j}: parado por FALTA DE CREDITO "
                          f"({porj.get(j,0)} vs {mx}). Nao e defeito; exige recarga.")
                elif estado == "OK":
                    print(f"│               {j}: atras ({porj.get(j,0)} vs {mx}) mas "
                          f"respondendo; e o juiz mais lento do painel.")
                elif estado == "RATE_LIMIT" and not _painel_vivo():
                    # Sem painel rodando, ninguem esta disputando cota: um 429 aqui
                    # e a cota real do provedor, nao contencao com o proprio trabalho.
                    print(f"│               {j}: SEM COTA no provedor e coleta parada "
                          f"({porj.get(j,0)} vs {mx}). Aguardando reset; o runner "
                          f"retoma sozinho e preenche so o que falta.")
                elif estado == "RATE_LIMIT":
                    # A sonda do monitor COMPETE com o painel pela mesma cota. Se o
                    # painel esta vivo e produzindo, um 429 na sonda significa que a
                    # janela esta saturada pelo proprio trabalho, nao que o juiz
                    # quebrou. Acusar aqui e alarme falso: foi o que aconteceu com o
                    # Gemini, que tinha 2 erros em 500 pares enquanto a sonda dava 429.
                    print(f"│               {j}: atras ({porj.get(j,0)} vs {mx}) e no "
                          f"limite de taxa. A sonda disputa cota com o proprio painel; "
                          f"so e pendencia se a coleta tambem estiver falhando.")
                else:
                    alertas.append(f"juiz {j} ficou para tras ({porj.get(j,0)} vs {mx}) "
                                   f"e o provedor responde {estado}")

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
