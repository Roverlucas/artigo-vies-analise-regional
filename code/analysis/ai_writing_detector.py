#!/usr/bin/env python3
"""Gate anti-slop: encontra passagens que soam a texto gerado.

POR QUE ESTE GATE EXISTE SEPARADO DA REVISAO GERAL
Uma revisao de qualidade avalia se o argumento se sustenta. Esta procura outra
coisa: frases que anunciam importancia em vez de demonstra-la, transicoes
formulaicas, abstracoes infladas e paralelismos que sinalizam geracao automatica.
Sao defeitos de VOZ, nao de conteudo, e uma revisao focada em rigor passa por cima
deles — foi exatamente o que aconteceu aqui: o parecer geral apontou os traccos
nominalmente e o achado nao foi aplicado.

Roda sobre o ingles e o portugues. O portugues importa mais, nao menos: aquele
texto foi produzido de uma vez, sem revisao humana intermediaria, e e onde a voz
gerada tem mais chance de ter passado.
"""
from __future__ import annotations

import concurrent.futures
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.squad_audit import call, ler  # noqa: E402

SAIDA = ROOT / "data" / "processed" / "ai_writing_detector.json"

SISTEMA = """You are looking for one thing only: sentences that read as machine-generated
rather than as written by a scientist with something to say.

Flag these patterns, and only these:
  - a sentence that ASSERTS importance instead of demonstrating it
    ("This is the study's strongest result", "This matters because")
  - formulaic transitions, especially short declarative openers that announce
    what the paragraph will do ("The effect survives being attacked.",
    "And it survives with no judge at all.")
  - inflated abstraction where a concrete noun would do ("the centre of gravity",
    "a disciplined picture")
  - three-part parallel constructions used for rhythm rather than meaning
  - hedging stacked on hedging, or emphasis stacked on emphasis
  - any sentence that could be deleted without losing information

Do NOT flag: technical density, long sentences, passive voice where it is
correct, or hedging that reflects genuine uncertainty about evidence. Those are
scientific writing, not slop.

For each finding quote the offending sentence VERBATIM so it can be located, and
give a rewrite that says the same thing in a plainer voice. If a rewrite would
lose information, say so and leave it.

Return ONLY this JSON:
{"findings":[{"file":"<file name>","quote":"<verbatim sentence>",
"why":"<which pattern>","rewrite":"<plainer version, or KEEP with reason>"}],
"clean_sections":["<sections that read as human-written>"],
"verdict":"<one sentence on the overall voice>"}"""

ALVOS = {
    "en-resultados": ("latex/sections/04_results.tex",),
    "en-discussao": ("latex/sections/05_discussion.tex",),
    "en-abertura": ("latex/sections/00_abstract.tex",
                    "latex/sections/01_introduction.tex",
                    "latex/sections/06_conclusion.tex"),
    "pt-resultados": ("latex/sections-PT/04_resultados.tex",),
    "pt-discussao": ("latex/sections-PT/05_discussao.tex",),
    "pt-abertura": ("latex/sections-PT/00_resumo.tex",
                    "latex/sections-PT/01_introducao.tex",
                    "latex/sections-PT/06_conclusao.tex"),
}


def analisa(rotulo: str, arquivos: tuple[str, ...]) -> dict:
    idioma = "Portuguese" if rotulo.startswith("pt") else "English"
    sistema = SISTEMA + f"\n\nThe text is in {idioma}; write the rewrites in {idioma}."
    try:
        txt = call("deepseek_v3", sistema, ler(*arquivos))
    except Exception as e:
        return {"bloco": rotulo, "erro": str(e)[:150]}
    t = txt.strip()
    if "```" in t:
        t = t.split("```")[1].removeprefix("json").strip()
    i, j = t.find("{"), t.rfind("}")
    try:
        d = json.loads(t[i:j + 1])
    except (json.JSONDecodeError, ValueError):
        return {"bloco": rotulo, "erro": "nao parseavel", "bruto": txt[:400]}
    d["bloco"] = rotulo
    return d


def main() -> None:
    print(f"gate anti-slop · {len(ALVOS)} blocos · auditor de outro fornecedor\n")
    res = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        fut = {pool.submit(analisa, r, a): r for r, a in ALVOS.items()}
        for f in concurrent.futures.as_completed(fut):
            r = f.result()
            res.append(r)
            if "erro" in r:
                print(f"  [erro] {r['bloco']}: {r['erro'][:70]}", flush=True)
            else:
                print(f"  {r['bloco']:<16} {len(r.get('findings', []))} passagens", flush=True)
    SAIDA.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  escrito: {SAIDA}")


if __name__ == "__main__":
    main()
