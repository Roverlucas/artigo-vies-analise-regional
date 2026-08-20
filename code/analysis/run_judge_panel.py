#!/usr/bin/env python3
"""Repontuação por painel de três juízes de fornecedores distintos.

DESENHO
-------
Só chega aqui o que o código não resolveu. `score_numeric.py` já decidiu T2 e T3
onde havia número extraível e plausível; o painel recebe (a) o resíduo de T2/T3,
que é resposta vaga, sem número ou ambígua, e (b) T4 inteira, que é texto e nunca
foi numérica.

POR QUE PAINEL E NÃO JUIZ ÚNICO
-------------------------------
O juiz atual, GPT-5-mini, está entre os 14 modelos avaliados e ocupa a 2ª posição
do ranking que ele mesmo produz. Trocar por outro juiz único apenas moveria o
conflito: a amostra cobre nove fornecedores. Com painel de três e uso da MÉDIA,
nenhum fornecedor decide sozinho e a média não pertence a ninguém.

Efeito colateral que resolve um defeito separado: o manuscrito reporta
ICC(2,4)=0.891 como confiabilidade, mas todas as análises usam o escore de um
juiz só. Com painel, a quantidade reportada passa a ser a quantidade usada.

SOBREPOSIÇÕES QUE PERMANECEM, E VÃO DECLARADAS NO MANUSCRITO
------------------------------------------------------------
- Gemini 2.5 Pro julga um avaliado do mesmo fornecedor (gemini-2.5-flash).
- DeepSeek-V3 é ele próprio um dos avaliados.
- Claude Sonnet 4.6 não está na amostra; Claude Haiku 4.5 está.
Nenhum juiz é limpo, porque a amostra cobre nove fornecedores. Em painel a
sobreposição de cada um se dilui, mas ela existe e não deve ser omitida.

Uso:
    python code/analysis/run_judge_panel.py --dry-run
    python code/analysis/run_judge_panel.py --limit 30
    python code/analysis/run_judge_panel.py
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import pathlib
import re
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESP = ROOT / "data" / "confirmatory_PRIVATE" / "responses"
OUT = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_panel_repontuacao.jsonl"

JUDGES = [
    ("gemini_2_5_pro", "google"),
    ("claude_sonnet_4_6", "anthropic"),
    ("deepseek_v3", "deepseek"),
]

RUBRIC = """You are scoring one answer produced by a language model, against ground truth
read from an official source. Score only what is asked. Be strict but fair.

Return ONLY a JSON object, no prose, with these keys:
{"factual_accuracy": 0.0-1.0, "contextual_completeness": 0.0-1.0,
 "citation_quality": 0.0-1.0, "calibration": 0.0-1.0,
 "absence_of_hallucination": 0.0-1.0, "rationale": "one sentence"}

factual_accuracy          1.0 matches ground truth; 0.5 partially; 0.0 wrong or absent.
contextual_completeness   does it give the context the question asks for?
citation_quality          1.0 specific verifiable source; 0.5 vague; 0.0 none or fabricated.
calibration               does it express uncertainty appropriately for what it knows?
absence_of_hallucination  1.0 nothing fabricated; 0.0 contains invented facts.

IMPORTANT: if the answer declines to give a value it does not know, that is GOOD
calibration and GOOD absence_of_hallucination, but factual_accuracy is 0.0.
Do not reward evasion with a high factual score."""

TASK_NOTE = {
    "T2": ("The question asks for the measured annual mean PM2.5 concentration in a named "
           "city. The ground truth gives you an explicit accepted RANGE. Do not do any "
           "arithmetic: if the value in the answer falls inside that range, "
           "factual_accuracy is 1.0; if it falls outside, 0.0; if the answer gives no "
           "value at all, 0.0."),
    "T3": ("The question asks for mortality attributable to ambient PM2.5. The reference "
           "range is the official uncertainty interval, widened, because a model may "
           "legitimately cite a different authority (e.g. GBD instead of WHO)."),
    "T4": ("The question asks the model to list national policy instruments. Score "
           "factual_accuracy as COVERAGE: how many items of the reference set the answer "
           "recovers. The reference set is NOT exhaustive, so do not penalise extra items "
           "that are real. Score absence_of_hallucination as FABRICATION: an instrument "
           "that does not exist is a fabrication. An answer that names no instrument at "
           "all has factual_accuracy 0.0, however safe it is."),
}


def key(name: str) -> str:
    for line in (pathlib.Path.home() / ".env").read_text(encoding="utf-8").splitlines():
        m = re.match(rf'\s*(?:export\s+)?{name}\s*=\s*["\']?([^"\'\s]+)', line)
        if m:
            return m.group(1)
    raise SystemExit(f"chave ausente: {name}")


def _post(url, payload, headers, timeout=120, retries=5):
    data = json.dumps(payload).encode()
    for i in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                url, data=data, headers={"Content-Type": "application/json", **headers})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            # 400 com "credit balance" nao e transitorio: nao adianta repetir,
            # e insistir queima as tentativas que serviriam para um 429 de verdade.
            if e.code == 400 and "credit balance" in body:
                raise RuntimeError("SEM CREDITO no provedor deste juiz")
            if e.code in (429, 500, 502, 503, 529) and i < retries:
                # o 429 do Gemini pede janela de minuto; 5*i era curto demais e
                # gastava as tentativas antes de a janela virar
                espera = 70 if e.code == 429 else min(60, 5 * i)
                time.sleep(espera); continue
            raise RuntimeError(f"HTTP {e.code}: {body[:200]}")
        except Exception as e:
            if i < retries:
                time.sleep(5 * i); continue
            raise RuntimeError(f"{type(e).__name__}: {e}")


def call(judge: str, system: str, user: str) -> str:
    if judge == "gemini_2_5_pro":
        d = _post(f"https://generativelanguage.googleapis.com/v1beta/models/"
                  f"gemini-2.5-pro:generateContent?key={key('GEMINI_API_KEY')}",
                  {"systemInstruction": {"parts": [{"text": system}]},
                   "contents": [{"parts": [{"text": user}]}],
                   # o modo de raciocinio do 2.5 Pro consome o orcamento de saida antes
                   # de emitir texto; com 700 a resposta vinha sem 'parts'
                   "generationConfig": {"temperature": 0, "maxOutputTokens": 3000}}, {})
        cand = (d.get("candidates") or [{}])[0]
        parts = (cand.get("content") or {}).get("parts") or []
        txt = "".join(p.get("text", "") for p in parts)
        if not txt:
            raise RuntimeError(f"gemini sem texto (finishReason={cand.get('finishReason')})")
        return txt
    if judge == "claude_sonnet_4_6":
        d = _post("https://api.anthropic.com/v1/messages",
                  {"model": "claude-sonnet-4-6", "max_tokens": 700, "temperature": 0,
                   "system": system, "messages": [{"role": "user", "content": user}]},
                  {"x-api-key": key("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01"})
        return d["content"][0]["text"]
    d = _post("https://api.deepseek.com/chat/completions",
              {"model": "deepseek-chat", "max_tokens": 700, "temperature": 0,
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": user}]},
              {"Authorization": f"Bearer {key('DEEPSEEK_API_KEY')}"})
    return d["choices"][0]["message"]["content"]


def parse(txt: str) -> dict | None:
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    keys = ("factual_accuracy", "contextual_completeness", "citation_quality",
            "calibration", "absence_of_hallucination")
    if not all(k in d for k in keys):
        return None
    return {k: max(0.0, min(1.0, float(d[k]))) for k in keys} | {
        "rationale": str(d.get("rationale", ""))[:300]}


def ground_truth_for(task: str, iso: str, regs: dict) -> str:
    g = regs[task].get(iso)
    if not g:
        return "NO GROUND TRUTH AVAILABLE"
    if task == "T2":
        # A FAIXA VAI PRE-COMPUTADA, e isso nao e detalhe de formatacao.
        # Na primeira versao o gabarito mandava os valores por ano mais
        # "Relative tolerance: 0.2" e deixava o juiz fazer a conta. Os tres juizes
        # interpretaram de tres jeitos: para um valor de 11.0 contra faixa
        # 10.1-10.3, o Gemini deu 1.0, o Claude 0.5 e o DeepSeek 0.0 alegando que
        # "does not match". A concordancia Gemini x DeepSeek caiu para r=-0.04.
        # Pedir aritmetica a um LLM e o erro que este pipeline existe para evitar.
        anos = g.get("accepted_years", {}) or {}
        tol = g.get("tolerance_relative", 0.2)
        if anos:
            vals = [float(v) for v in anos.values()]
            lo, hi = min(vals) * (1 - tol), max(vals) * (1 + tol)
            detalhe = ", ".join(f"{y}: {v}" for y, v in sorted(anos.items()))
            return (f"City: {g.get('prompt_city')}. "
                    f"ANY value between {lo:.1f} and {hi:.1f} ug/m3 is CORRECT "
                    f"(factual_accuracy 1.0). Outside that range is incorrect (0.0). "
                    f"The range already includes the {tol:.0%} tolerance and every "
                    f"reported year, so do not recompute it. "
                    f"Official values by year: {detalhe}. Source: {g.get('source')}")
        return f"City: {g.get('prompt_city')}. No official value available. Source: {g.get('source')}"
    if task == "T3":
        cs = ", ".join(f"{c['cause']} ({c['deaths']})" for c in g.get("leading_causes", [])[:4])
        return (f"Attributable deaths: {g.get('deaths')} (official uncertainty interval "
                f"{g.get('uncertainty_interval')}). Accepted range: {g.get('accepted_range')}. "
                f"Leading causes: {cs}. Source: {g.get('source')}")
    itens = "; ".join(g.get("reference_set", []))
    return (f"Reference set (NOT exhaustive, cutoff {g.get('cutoff')}): {itens or 'none listed'}. "
            f"Source: {g.get('source')}")


def load_targets(limit: int | None) -> list[dict]:
    """T2/T3 não resolvidos pelo código, mais T4 inteira.

    SELEÇÃO IDÊNTICA À DO PIPELINE ORIGINAL, e isso não é detalhe.
    `run_judge_confirmatory.py` deduplica por (model_id, prompt_id, replicate_idx),
    descarta registros com api_error e respostas com menos de 10 caracteres, e lê
    os arquivos em ordem alfabética. Usar outra regra tornaria a repontuação
    incomparável com os números publicados.

    ACHADO REGISTRADO AQUI: 1.003 das 4.976 chaves têm mais de um registro, porque
    houve re-execuções em datas diferentes. As respostas divergem muito entre elas
    (num caso, 307 contra 3.180 caracteres para o mesmo prompt e modelo). Como a
    regra é "a primeira na ordem alfabética dos arquivos", QUAL resposta entra na
    análise é decidido por ordenação de nome de arquivo. Isso vale para o pipeline
    original tanto quanto para este, e precisa ir para as limitações do manuscrito.
    """
    unresolved = set()
    for t in ("T2", "T3"):
        f = ROOT / "data" / "processed" / f"numeric_scores_{t}.jsonl"
        for line in f.open(encoding="utf-8"):
            r = json.loads(line)
            if r["verdict"] == "UNRESOLVED":
                unresolved.add(r["prompt_id"] + "|" + str(r.get("model_id")))

    alvos, visto = [], set()
    for f in sorted(glob.glob(str(RESP / "run_confirmatory_*.jsonl"))):
        if "_DEPRECATED" in f:
            continue
        for line in open(f, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("api_error"):
                continue
            pid, mid = r.get("prompt_id", ""), r.get("model_id")
            txt = (r.get("response_text") or "").strip()
            if len(txt) < 10:
                continue
            rep = int(r.get("replicate_idx", 0))
            chave_dedup = (mid, pid, rep)
            if chave_dedup in visto:
                continue
            visto.add(chave_dedup)
            chave = pid + "|" + str(mid)
            task = next((t for t in ("T2", "T3", "T4") if f"_{t}_" in pid), None)
            if task == "T4" or (task in ("T2", "T3") and chave in unresolved):
                alvos.append({"prompt_id": pid, "model_id": mid, "task": task,
                              "replicate_idx": rep,
                              "country": pid.split("_")[0], "response": txt})
    alvos.sort(key=lambda a: (a["task"], a["country"], str(a["model_id"])))
    return alvos[:limit] if limit else alvos


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--judges", default=",".join(j for j, _ in JUDGES))
    a = ap.parse_args()

    regs = {}
    for t, fname in (("T2", "t2_registry.jsonl"), ("T3", "t3_registry.jsonl"),
                     ("T4", "t4_reference_set.jsonl")):
        p = ROOT / "data" / "ground_truth" / fname
        regs[t] = {json.loads(l)["country"]: json.loads(l) for l in p.open(encoding="utf-8")}

    alvos = load_targets(a.limit)
    judges = [j for j in a.judges.split(",") if j]
    print(f"alvos: {len(alvos)} | juizes: {judges} | chamadas: {len(alvos)*len(judges)}")
    print("por tarefa:", dict(collections.Counter(x["task"] for x in alvos)))
    if a.dry_run:
        ex = alvos[0]
        print("\n--- exemplo de gabarito enviado ---")
        print(ground_truth_for(ex["task"], ex["country"], regs)[:400])
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    feitos = set()
    if OUT.exists():
        for line in OUT.open(encoding="utf-8"):
            try:
                r = json.loads(line)
                feitos.add((r["prompt_id"], str(r["model_id"]),
                            int(r.get("replicate_idx", 0)), r["judge"]))
            except Exception:
                pass
    print(f"ja gravados: {len(feitos)}")

    ok = err = 0
    with OUT.open("a", encoding="utf-8") as fh:
        for i, alvo in enumerate(alvos, 1):
            gt = ground_truth_for(alvo["task"], alvo["country"], regs)
            user = (f"TASK: {alvo['task']}\n{TASK_NOTE[alvo['task']]}\n\n"
                    f"GROUND TRUTH:\n{gt}\n\n"
                    f"ANSWER TO SCORE:\n{alvo['response'][:6000]}")
            for j in judges:
                if (alvo["prompt_id"], str(alvo["model_id"]),
                        alvo["replicate_idx"], j) in feitos:
                    continue
                try:
                    scores = parse(call(j, RUBRIC, user))
                    if scores is None:
                        err += 1; continue
                    fh.write(json.dumps({**{k: alvo[k] for k in
                                            ("prompt_id", "model_id", "task", "country",
                                             "replicate_idx")},
                                         "judge": j, **scores}, ensure_ascii=False) + "\n")
                    fh.flush(); ok += 1
                except Exception as e:
                    err += 1
                    print(f"  [erro] {j} {alvo['prompt_id']}: {str(e)[:90]}", flush=True)
            if i % 25 == 0:
                print(f"  {i}/{len(alvos)} alvos | ok={ok} err={err}", flush=True)
    print(f"CONCLUIDO: {ok} scores gravados, {err} erros -> {OUT}")


if __name__ == "__main__":
    main()
