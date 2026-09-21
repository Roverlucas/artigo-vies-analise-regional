#!/usr/bin/env python3
"""Sanity check do H3 (parecer externo, 2026-09-21, item Cabra).

A objecao: se o Cabra-Mistral 7B estivesse servido com template quebrado no
Ollama, o "pior dos catorze" seria artefato de serving, nao de modelo. Duas
verificacoes, ambas locais e sem custo de API:

  1. Template. O Modelfile local usa "[INST] {{ .Prompt }} [/INST]", que e
     exatamente o chat_template do tokenizer_config.json publicado em
     botbot-ai/CabraMistral-v3-7b-32k (conferido em 2026-09-21). A base
     declarada no config.json e Mistral-7B-Instruct-v0.3.
  2. Base contra fine-tune, nos MESMOS itens. Reservimos os 30 prompts em
     portugues (BRA, PRT, AGO; 5 tarefas x 2 personas) com 2 replicatas em
     tres modelos locais: cabra-mistral-7b (o do estudo), mistral:7b (a base
     Mistral-7B-Instruct-v0.3, mesma quantizacao Q4_K_M) e llama3.1:8b (o
     par de escala do estudo, re-servido agora para medir deriva de serving).
     T1/T2/T3 sao pontuadas pelo MESMO extrator de codigo do estudo; T4/T5
     nao entram (exigiriam juiz). O desfecho e "devolveu o valor do
     registro" (CORRECT entre os vereditos factuais).

Saida: data/processed/cabra_sanity/responses_*.jsonl e summary.json.
"""
from __future__ import annotations
import collections, json, pathlib, sys, time, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from code.analysis import score_numeric as sn  # noqa: E402
from code.analysis.code_verdicts import FACTUAL  # noqa: E402

OUT = ROOT / "data/processed/cabra_sanity"
OUT.mkdir(parents=True, exist_ok=True)
MODELS = {"cabra_mistral_7b": "cabra-mistral-7b:latest",
          "mistral_7b_instruct_v03_base": "mistral:7b",
          "llama31_8b_reserved": "llama3.1:8b"}
PRIV = ROOT / "data/confirmatory_PRIVATE"


def prompts_pt():
    rows = []
    for f in ("prompts_native.jsonl", "prompts_native_new.jsonl"):
        for l in (PRIV / f).open(encoding="utf-8"):
            r = json.loads(l)
            if r["prompt_id"].endswith("_pt"):
                rows.append(r)
    return rows


def call(tag, prompt):
    body = {"model": tag, "messages": [{"role": "user", "content": prompt}], "stream": False,
            "options": {"temperature": 0.3, "num_predict": 800}}
    req = urllib.request.Request("http://localhost:11434/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as resp:
        d = json.load(resp)
    return d.get("message", {}).get("content") or "", d.get("done"), int((time.time() - t0) * 1000)


def collect():
    ps = prompts_pt()
    print(f"{len(ps)} prompts em portugues · {len(MODELS)} modelos · 2 replicatas")
    for mid, tag in MODELS.items():
        f = OUT / f"responses_{mid}.jsonl"
        done = set()
        if f.exists():
            for l in f.open(encoding="utf-8"):
                r = json.loads(l); done.add((r["prompt_id"], r["replicate_idx"]))
        with f.open("a", encoding="utf-8") as fh:
            for rep in (0, 1):
                for p in ps:
                    if (p["prompt_id"], rep) in done:
                        continue
                    txt, ok, ms = call(tag, p["prompt_rendered"])
                    rec = {"model_id": mid, "ollama_tag": tag, "prompt_id": p["prompt_id"],
                           "country_iso3": p["country_iso3"], "task": p["task"], "persona": p["persona"],
                           "replicate_idx": rep, "response_text": txt, "finish_reason": "stop" if ok else "truncated",
                           "latency_ms": ms, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); fh.flush()
                    print(f"  {mid:30s} {p['prompt_id']:28s} rep{rep} {ms/1000:5.1f}s {len(txt):5d} chars", flush=True)


def summarise():
    files = [str(OUT / f"responses_{mid}.jsonl") for mid in MODELS]
    res = collections.defaultdict(lambda: collections.Counter())
    exemplos = {}
    for task in ("T1", "T2", "T3"):
        for v in sn.score(task, files=files):
            res[(v["model_id"], task)][v["verdict"]] += 1
            res[(v["model_id"], "all")][v["verdict"]] += 1
    # o estudo original: Cabra e Llama em PT, so T1-T3 por codigo
    orig = collections.defaultdict(lambda: collections.Counter())
    for l in (PRIV / "analysis/judge_scores_corrected.jsonl").open(encoding="utf-8"):
        r = json.loads(l)
        if r.get("score_source") != "code" or not r["prompt_id"].endswith("_pt"): continue
        if r["model_id"] not in ("cabra_mistral_7b", "llama31_8b"): continue
        orig[(r["model_id"] + "_ORIGINAL", r["task"])]["CORRECT" if r["factual_accuracy"] >= 0.5 else "NOT"] += 1
        orig[(r["model_id"] + "_ORIGINAL", "all")]["CORRECT" if r["factual_accuracy"] >= 0.5 else "NOT"] += 1
    summary = {}
    print("\nRESUMO — taxa de 'devolveu o valor do registro' entre vereditos factuais (T1-T3, PT)")
    for (mid, task), c in sorted(res.items()):
        fact = sum(n for v, n in c.items() if v in FACTUAL)
        corr = sum(n for v, n in c.items() if v in FACTUAL and FACTUAL[v] >= 0.5)
        summary[f"{mid}|{task}"] = {"n_factual": fact, "correct": corr, "rate": corr / fact if fact else None, "verdicts": dict(c)}
        print(f"  {mid:30s} {task:4s} factual n={fact:3d} correct={corr:3d} rate={corr/fact if fact else float('nan'):.3f}  {dict(c)}")
    for (mid, task), c in sorted(orig.items()):
        n = sum(c.values()); summary[f"{mid}|{task}"] = {"n_factual": n, "correct": c["CORRECT"], "rate": c["CORRECT"] / n if n else None}
        print(f"  {mid:30s} {task:4s} factual n={n:3d} correct={c['CORRECT']:3d} rate={c['CORRECT']/n if n else float('nan'):.3f}  (estudo original)")
    # exemplo de resposta do Cabra a T1 Brasil (sanidade do template: portugues coerente?)
    for l in (OUT / "responses_cabra_mistral_7b.jsonl").open(encoding="utf-8"):
        r = json.loads(l)
        if r["task"] == "T1" and r["country_iso3"] == "BRA":
            exemplos["cabra_T1_BRA"] = r["response_text"][:600]; break
    summary["exemplo"] = exemplos
    summary["template_check"] = {"ollama_modelfile_template": "[INST] {{ .Prompt }} [/INST] ",
                                 "hf_chat_template": "[INST] {content} [/INST]", "base": "Mistral-7B-Instruct-v0.3",
                                 "quantization_both": "Q4_K_M", "verified": "2026-09-21"}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\nexemplo Cabra T1 BRA:", exemplos.get("cabra_T1_BRA", "")[:400])
    print(f"escrito: {OUT/'summary.json'}")


if __name__ == "__main__":
    if "--summary-only" not in sys.argv:
        collect()
    summarise()
