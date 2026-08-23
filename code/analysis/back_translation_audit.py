#!/usr/bin/env python3
"""Auditoria de fidelidade dos prompts nativos por back-translation.

POR QUE ESTE TESTE DECIDE O ARTIGO
H2 — perguntar na lingua do pais reduz a acuracia — passou a ser a afirmacao
central. Os prompts nativos foram gerados por um LLM tradutor (Claude Sonnet 4.6)
sem back-translation, entao existe uma explicacao alternativa que nenhum
reordenamento dos escores elimina: talvez o modelo nao responda pior na lingua;
talvez o prompt nativo simplesmente pergunte outra coisa. Este script separa as
duas.

DESENHO
1. CENSO, nao amostra. Sao 90 prompts nativos unicos em toda a coleta, entao
   auditamos todos e nao ha incerteza amostral a reportar.
2. O back-tradutor e um modelo DIFERENTE do tradutor original. Pedir ao Claude que
   retraduza o que o Claude traduziu deixaria o mesmo modelo consertar o proprio
   erro.
3. A fidelidade e julgada por DOIS modelos independentes contra uma rubrica de
   itens concretos, e o desacordo resolve-se de forma CONSERVADORA: basta um juiz
   apontar divergencia para o prompt ser marcado como divergente. Isso
   superestima a infidelidade de proposito — e o teste mais duro para a nossa
   propria hipotese.

O teste decisivo vem depois, em h2_faithful_subset: se o efeito de lingua persiste
entre os prompts verificadamente fieis, a traducao nao o explica.
"""
from __future__ import annotations

import concurrent.futures
import json
import pathlib
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.run_judge_panel import call  # noqa: E402

PROMPTS = ROOT / "data" / "confirmatory_PRIVATE"
SAIDA = ROOT / "data" / "processed" / "back_translation_audit.jsonl"

BACK_TRADUTOR = "deepseek_v3"          # tradutor original foi claude_sonnet_4_6
JUIZES = ("claude_sonnet_4_6", "gemini_2_5_pro")

SYS_BACK = (
    "You are a professional translator. Translate the text into English. "
    "Translate ONLY what is written: do not correct, complete, clarify or "
    "improve it. If the source is ambiguous or awkward, keep the ambiguity. "
    "Preserve proper nouns, acronyms, units and numbers exactly. "
    "Output the translation and nothing else."
)

SYS_JUIZ = """You compare two English texts: ORIGINAL (the source prompt) and
BACK (an independent back-translation of a native-language rendering of that same
prompt). You are auditing whether the native rendering preserved the question.

Answer each item with true or false:
  same_question   : BACK asks for the same information as ORIGINAL
  same_country    : the country referred to is the same
  same_target     : the requested quantity is the same (same pollutant, same
                    averaging period, same kind of value). false if e.g. ORIGINAL
                    asks the annual standard and BACK asks the 24-hour one
  same_persona    : the role framing (neutral, or acting as a public
                    environmental manager) is preserved
  no_info_shift   : BACK neither adds information that would make the question
                    easier to answer, nor omits information present in ORIGINAL

Wording, style and sentence order may differ freely: that is translation, not
divergence. Judge meaning only.

Return ONLY this JSON object:
{"same_question":bool,"same_country":bool,"same_target":bool,
 "same_persona":bool,"no_info_shift":bool,"note":"<=20 words"}"""

ITENS = ("same_question", "same_country", "same_target", "same_persona",
         "no_info_shift")


def carrega_pares() -> list[dict]:
    vistos = {}
    for nome in ("prompts_native.jsonl", "prompts_native_new.jsonl",
                 "prompts_extra.jsonl"):
        p = PROMPTS / nome
        if not p.exists():
            continue
        for linha in p.open(encoding="utf-8"):
            if not linha.strip():
                continue
            r = json.loads(linha)
            if r.get("language") in ("pt", "es", "hi") and r.get("prompt_rendered_en"):
                vistos.setdefault(r["prompt_id"], r)
    return list(vistos.values())


def parse(txt: str) -> dict | None:
    t = txt.strip()
    if "```" in t:
        t = t.split("```")[1].removeprefix("json").strip()
    i, j = t.find("{"), t.rfind("}")
    if i < 0 or j < 0:
        return None
    try:
        d = json.loads(t[i:j + 1])
    except json.JSONDecodeError:
        return None
    return d if all(k in d for k in ITENS) else None


def main() -> None:
    pares = carrega_pares()
    print(f"prompts nativos com par em ingles: {len(pares)} (censo, sem amostragem)")

    feitos = set()
    if SAIDA.exists():
        for linha in SAIDA.open(encoding="utf-8"):
            try:
                feitos.add(json.loads(linha)["prompt_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    pendentes = [p for p in pares if p["prompt_id"] not in feitos]
    print(f"ja auditados: {len(feitos)} · pendentes: {len(pendentes)}")
    if not pendentes:
        print("nada a fazer")
        return

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    fh = SAIDA.open("a", encoding="utf-8")
    trava = threading.Lock()
    ok = err = 0

    def audita(p: dict) -> dict | None:
        nativo = p["prompt_rendered"]
        original = p["prompt_rendered_en"]
        back = call(BACK_TRADUTOR, SYS_BACK, nativo)
        user = f"ORIGINAL:\n{original}\n\nBACK:\n{back}"
        vereditos = {}
        for j in JUIZES:
            try:
                v = parse(call(j, SYS_JUIZ, user))
                if v:
                    vereditos[j] = v
            except Exception:
                continue
        if not vereditos:
            return None
        # conservador: basta um juiz apontar divergencia
        falhas = sorted({it for v in vereditos.values()
                         for it in ITENS if not v.get(it)})
        return {"prompt_id": p["prompt_id"], "language": p["language"],
                "country": p.get("country_iso3"), "task": p.get("task"),
                "back_translation": back, "original_en": original,
                "juizes": vereditos, "n_juizes": len(vereditos),
                "itens_falhos": falhas,
                "verdict": "FAITHFUL" if not falhas else "DIVERGENT"}

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futuros = {pool.submit(audita, p): p for p in pendentes}
        for n, fut in enumerate(concurrent.futures.as_completed(futuros), 1):
            try:
                r = fut.result()
            except Exception as e:
                r, msg = None, str(e)[:80]
            else:
                msg = ""
            with trava:
                if r:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                    fh.flush()
                    ok += 1
                else:
                    err += 1
                    if msg:
                        print(f"  [erro] {futuros[fut]['prompt_id']}: {msg}", flush=True)
                if n % 15 == 0:
                    print(f"  {n}/{len(pendentes)} | ok={ok} err={err}", flush=True)
    fh.close()
    print(f"CONCLUIDO: {ok} auditados, {err} erros -> {SAIDA}")


if __name__ == "__main__":
    main()
