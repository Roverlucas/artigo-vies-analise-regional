#!/usr/bin/env python3
"""Auditoria independente do squad academico, executada em modelo de OUTRO fornecedor.

POR QUE EM OPENAI E NAO AQUI
A regra R7 do squad — quem gera nao fecha — existe porque um modelo revisando o
proprio trabalho compartilha os pontos cegos que produziram o trabalho. Todo o
material auditado aqui foi produzido em Claude; a validacao roda em GPT-5.2-pro
justamente para que os erros de origem tenham chance de aparecer.

O parecer que sai daqui e evidencia E3: hipotese a adjudicar, nao instrucao a
executar. Cada achado precisa ser conferido na fonte antes de virar edicao.

LENTES
Cada agente do squad vira uma lente com escopo proprio e material proprio. Nao
pedimos "revise o artigo" a um modelo generico: pedimos a pergunta especifica que
aquele papel faria, com o material que aquele papel leria.
"""
from __future__ import annotations

import concurrent.futures
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
SAIDA = ROOT / "data" / "processed" / "squad_audit_openai.json"
MODELO = "gpt-5.2-pro"
URL = "https://api.openai.com/v1/responses"


def chave() -> str:
    for linha in (pathlib.Path.home() / ".env").read_text().splitlines():
        m = re.match(r'\s*(?:export\s+)?OPENAI_API_KEY\s*=\s*["\']?([^"\'\s]+)', linha)
        if m:
            return m.group(1)
    raise SystemExit("OPENAI_API_KEY nao encontrada em ~/.env")


def ler(*partes: str) -> str:
    out = []
    for p in partes:
        cam = ROOT / p
        if cam.is_dir():
            for f in sorted(cam.glob("*.tex")) or sorted(cam.glob("*.py")):
                out.append(f"\n===== {f.relative_to(ROOT)} =====\n{f.read_text(encoding='utf-8')}")
        elif cam.exists():
            out.append(f"\n===== {p} =====\n{cam.read_text(encoding='utf-8')}")
    return "\n".join(out)


BASE = """You are auditing a manuscript and its analysis code before submission to
Government Information Quarterly (Elsevier). The work was produced with heavy
assistance from a different AI model, so your job is to find what that model and
its authors missed — not to praise what is there.

Report ONLY defects you can point to in the supplied material. For each one give
the exact location, what is wrong, why it matters, and the smallest fix. Do not
speculate about material you were not shown; say "not shown" instead. Do not pad
the list: three real defects beat fifteen plausible ones. If a section is sound,
say so in one line and move on.

Return ONLY this JSON:
{"findings":[{"severity":"critical|major|minor","location":"<file/section>",
"defect":"<what is wrong>","why":"<consequence>","fix":"<smallest change>"}],
"sound":["<what you checked and found solid, one line each>"],
"verdict":"<one sentence: is this submittable as is?>"}"""

LENTES = {
    "senior-scientist": (
        "Lens: John Ioannidis. Threats to validity, inferential overreach, "
        "selective reporting, and whether the conclusions the text draws are the "
        "conclusions the numbers support. You care most about claims that outrun "
        "their evidence and about analytic choices that were made after seeing data.",
        ("latex/sections", "latex/main.tex"),
    ),
    "statistician": (
        "Lens: statistical correctness. Check test choice, independence "
        "assumptions, clustering and pseudo-replication, multiplicity, power "
        "claims, confidence-interval construction, effect-size conversions, and "
        "whether any reported p-value or interval could be wrong given how it was "
        "computed. The code is supplied: verify the statistics AS IMPLEMENTED, not "
        "as described.",
        ("latex/sections/04_results.tex", "code/analysis/freeze_all_effects.py",
         "code/analysis/robustness_extra.py", "code/analysis/robustness_h2.py"),
    ),
    "qa-reviewer": (
        "Lens: internal peer review. Hunt for INTERNAL INCONSISTENCY above all: a "
        "number that differs between abstract, results, discussion, conclusion and "
        "supplement; a claim in one section contradicted by another; a table whose "
        "cells disagree with the prose; a cross-reference to something that is not "
        "there. Be exhaustive and literal.",
        ("latex/sections", "latex/main.tex", "latex/supplement.tex"),
    ),
    "code-reviewer": (
        "Lens: scientific software review. Look for bugs that would change a "
        "reported number: wrong indexing, silent exception handling that hides "
        "failure, off-by-one, incorrect pairing or grouping, seeds that do not "
        "make results reproducible, filters applied inconsistently between "
        "analyses, and any place where the code does something other than what its "
        "docstring claims.",
        ("code/analysis/freeze_all_effects.py", "code/analysis/export_corrected_scores.py",
         "code/analysis/robustness_h2.py", "code/analysis/robustness_extra.py",
         "code/analysis/back_translation_audit.py", "code/analysis/score_numeric.py"),
    ),
    "journal-specialist": (
        "Lens: Phil Bourne, editor's desk at Government Information Quarterly. "
        "Would this survive desk rejection? Judge scope fit, framing for a public "
        "administration and information-policy readership rather than an ML one, "
        "title and abstract effectiveness, and whether the contribution is stated "
        "in terms that journal's readers act on. Flag anything that reads as a "
        "machine-learning benchmark paper submitted to the wrong venue.",
        ("latex/sections/00_abstract.tex", "latex/sections/01_introduction.tex",
         "latex/sections/05_discussion.tex", "latex/sections/06_conclusion.tex",
         "latex/main.tex"),
    ),
    "legal-ethics": (
        "Lens: research ethics and publisher compliance. Check authorship and "
        "CRediT coherence, funding and competing-interest declarations, the "
        "generative-AI disclosure against Elsevier policy, data and code "
        "availability promises against what is actually released, licensing, and "
        "any claim about pre-registration or human subjects that the record does "
        "not support.",
        ("latex/main.tex", "latex/supplement.tex"),
    ),
    "academic-writer": (
        "Lens: scientific writing. Flag hedging that hides a claim, claims stated "
        "more strongly than the evidence, redundancy, and AI-writing tells: "
        "formulaic transitions, inflated abstractions, sentences that assert "
        "importance instead of demonstrating it, and paragraphs that restate the "
        "previous paragraph. Quote the offending sentence.",
        ("latex/sections/00_abstract.tex", "latex/sections/04_results.tex",
         "latex/sections/05_discussion.tex"),
    ),
    "literature-analyst": (
        "Lens: Cassidy Sugimoto. Check whether the related-work framing is fair "
        "and current, whether the gap claimed is really open, whether any citation "
        "is used to support something it cannot support, and whether obvious "
        "relevant work is missing for this venue. Flag any reference that looks "
        "fabricated or mismatched to the claim it backs.",
        ("latex/sections/01_introduction.tex", "latex/sections/02_related_work.tex",
         "latex/references.bib"),
    ),
}


def chamar(lente: str, instrucao: str, material: str, api: str) -> dict:
    payload = {
        "model": MODELO,
        "instructions": BASE + "\n\n" + instrucao,
        "input": material,
        "reasoning": {"effort": "high"},
        "max_output_tokens": 12000,
    }
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api}"})
    for tentativa in range(4):
        try:
            with urllib.request.urlopen(req, timeout=1800) as r:
                d = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            corpo = e.read().decode()[:200]
            if e.code in (429, 500, 502, 503, 504) and tentativa < 3:
                import time
                time.sleep(20 * (tentativa + 1))
                continue
            return {"lente": lente, "erro": f"HTTP {e.code}: {corpo}"}
        except Exception as e:
            if tentativa < 3:
                import time
                time.sleep(15)
                continue
            return {"lente": lente, "erro": str(e)[:200]}
    else:
        return {"lente": lente, "erro": "esgotou tentativas"}

    txt = ""
    for item in d.get("output", []):
        for c in item.get("content", []):
            if c.get("type") in ("output_text", "text"):
                txt += c.get("text", "")
    t = txt.strip()
    if "```" in t:
        t = t.split("```")[1].removeprefix("json").strip()
    i, j = t.find("{"), t.rfind("}")
    try:
        parsed = json.loads(t[i:j + 1])
    except (json.JSONDecodeError, ValueError):
        return {"lente": lente, "erro": "resposta nao parseavel", "bruto": txt[:800]}
    parsed["lente"] = lente
    return parsed


def main() -> None:
    api = chave()
    print(f"auditoria independente em {MODELO} · {len(LENTES)} lentes do squad\n")
    resultados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futuros = {pool.submit(chamar, nome, instr, ler(*mat), api): nome
                   for nome, (instr, mat) in LENTES.items()}
        for fut in concurrent.futures.as_completed(futuros):
            r = fut.result()
            resultados.append(r)
            nome = r.get("lente", futuros[fut])
            if "erro" in r:
                print(f"  [erro] {nome}: {r['erro'][:110]}", flush=True)
            else:
                f = r.get("findings", [])
                sev = {}
                for x in f:
                    sev[x.get("severity", "?")] = sev.get(x.get("severity", "?"), 0) + 1
                print(f"  {nome:<20} {len(f)} achados  {sev}", flush=True)

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nescrito: {SAIDA}")


if __name__ == "__main__":
    main()
