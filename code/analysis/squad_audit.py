#!/usr/bin/env python3
"""Auditoria independente do squad academico, executada em modelo de OUTRO fornecedor.

POR QUE NAO EM CLAUDE
A regra R7 do squad — quem gera nao fecha — existe porque um modelo revisando o
proprio trabalho compartilha os pontos cegos que produziram o trabalho. Todo o
material auditado aqui foi produzido em Claude, entao a validacao precisa correr
em outro fornecedor para que os erros de origem tenham chance de aparecer.

O alvo preferido era GPT-5.2-pro, mas a conta OpenAI estava sem credito e nenhuma
chamada passou. Gemini 2.5 Pro e DeepSeek-V3 satisfazem o mesmo requisito, e as
quatro lentes mais criticas rodam nos DOIS, para que um achado isolado possa ser
distinguido de um achado corroborado. O modelo que produziu cada parecer fica
registrado no resultado, como o R7 exige.

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
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
SAIDA = ROOT / "data" / "processed" / "squad_audit.json"
# Lentes criticas rodam nos dois fornecedores; as demais em um so.
CRITICAS = ("orientador", "narrativa", "didatica", "qa-reviewer")
FORNECEDORES = ("gemini_2_5_pro", "deepseek_v3")


sys.path.insert(0, str(ROOT))


def _chave(nome: str) -> str:
    for linha in (pathlib.Path.home() / ".env").read_text().splitlines():
        m = re.match(rf'\s*(?:export\s+)?{nome}\s*=\s*["\']?([^"\'\s]+)', linha)
        if m:
            return m.group(1)
    raise SystemExit(f"{nome} nao encontrada em ~/.env")


def _post(url: str, payload: dict, headers: dict, timeout: int = 1500) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", **headers})
    for tentativa in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and tentativa < 3:
                time.sleep(30 * (tentativa + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read().decode()[:150]}") from None
        except Exception:
            if tentativa < 3:
                time.sleep(20)
                continue
            raise
    raise RuntimeError("esgotou tentativas")


# ORCAMENTO DE SAIDA PROPRIO, e nao o do painel de juizes.
# A primeira tentativa desta auditoria reusou o call() de run_judge_panel, que
# tem max_tokens 700 (DeepSeek) e 3000 (Gemini) porque julga UMA resposta e
# devolve um JSON curto. Uma auditoria de manuscrito produz milhares de tokens:
# o DeepSeek truncou no meio do primeiro achado e o Gemini gastou todo o
# orcamento em raciocinio e devolveu MAX_TOKENS sem texto. Reusar uma funcao
# calibrada para outra tarefa e o defeito; o orcamento aqui e dimensionado para
# o que esta tarefa produz.
SAIDA_MAX = 16000


def call(fornecedor: str, sistema: str, usuario: str) -> str:
    if fornecedor == "gemini_2_5_pro":
        d = _post(
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-pro:generateContent?key={_chave('GEMINI_API_KEY')}",
            {"systemInstruction": {"parts": [{"text": sistema}]},
             "contents": [{"parts": [{"text": usuario}]}],
             "generationConfig": {"temperature": 0, "maxOutputTokens": SAIDA_MAX}}, {})
        cands = d.get("candidates") or []
        if not cands or "content" not in cands[0] or "parts" not in cands[0]["content"]:
            raise RuntimeError(f"gemini sem texto (finishReason="
                               f"{cands[0].get('finishReason') if cands else '?'})")
        return "".join(p.get("text", "") for p in cands[0]["content"]["parts"])
    if fornecedor == "deepseek_v3":
        d = _post("https://api.deepseek.com/chat/completions",
                  {"model": "deepseek-chat", "max_tokens": 8000, "temperature": 0,
                   "messages": [{"role": "system", "content": sistema},
                                {"role": "user", "content": usuario}]},
                  {"Authorization": f"Bearer {_chave('DEEPSEEK_API_KEY')}"})
        return d["choices"][0]["message"]["content"]
    raise ValueError(f"fornecedor desconhecido: {fornecedor}")


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


BASE = """You are giving a final review of a manuscript before it goes to the
authors' senior colleagues and then to Government Information Quarterly
(Elsevier). The work was produced with heavy assistance from a different AI
model, so your job is to find what that model and its authors missed.

This is a LATE review, so weigh two things equally: whether the work is sound,
and whether it READS. A reader of GIQ is a public-administration scholar or a
practitioner, not a machine-learning researcher. Judge whether the argument can
be followed from first page to last by that reader: whether the through-line
holds, whether each section earns the next, whether the numbers are explained
rather than merely stated, and whether anything is needlessly opaque.

Score the manuscript 0-10 on your dimension, where 5 = publishable somewhere with
work, 7 = solid for this venue, 9 = among the better papers the venue runs. Be
calibrated: a 9 must be defended, and so must a 4.

Report weaknesses you can point at, and — separately — opportunities that are
WITHIN the study's declared scope (a protocol for auditing regulatory
information; testing the mitigations an agency can actually deploy; locating
where reliability differs). Do not propose new data collection unless it is the
only way to fix something you consider blocking.

Return ONLY this JSON:
{"score": <0-10 number>,
 "score_rationale": "<two sentences defending the number>",
 "weaknesses":[{"severity":"critical|major|minor","location":"<section>",
   "problem":"<what is wrong>","fix":"<smallest change>"}],
 "opportunities":[{"what":"<within-scope improvement>","payoff":"<why it is worth it>"}],
 "readability":"<one paragraph: can a public-administration reader follow this start to finish? where does it lose them?>",
 "verdict":"<one sentence>"}"""

LENTES = {
    "orientador": (
        "Lens: the supervising academic. Judge the manuscript AS A WHOLE: does the "
        "argument hold from title to conclusion, does each section earn the next, "
        "is the contribution stated clearly enough that a busy reader gets it from "
        "the abstract alone, and is any claim stronger than its evidence? You are "
        "the last person to see this before the co-authors do.",
        ("latex/sections", "latex/main.tex"),
    ),
    "narrativa": (
        "Lens: storytelling and line of reasoning. Trace the through-line from the "
        "opening problem to the closing implication. Does the paper set up a "
        "question and answer THAT question? Are there sections that break the "
        "thread, repeat an earlier one, or arrive without being set up? Does the "
        "reader always know why they are being shown a number? Name the exact "
        "places where the thread snaps, and say what would restore it.",
        ("latex/sections",),
    ),
    "didatica": (
        "Lens: accessibility for a public-administration readership. This audience "
        "reads statistics but does not build models. Flag: jargon used without "
        "being introduced, a statistic reported without saying what it means in "
        "practical terms, a table the reader cannot interpret unaided, and any "
        "passage where the writing is harder than the idea requires. Quote the "
        "offending sentence and rewrite it in one line.",
        ("latex/sections/00_abstract.tex", "latex/sections/03_methods.tex",
         "latex/sections/04_results.tex"),
    ),
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


def chamar(lente: str, instrucao: str, material: str, fornecedor: str) -> dict:
    try:
        txt = call(fornecedor, BASE + "\n\n" + instrucao, material)
    except Exception as e:
        return {"lente": lente, "auditor": fornecedor, "erro": str(e)[:200]}
    t = txt.strip()
    if "```" in t:
        t = t.split("```")[1].removeprefix("json").strip()
    i2, j2 = t.find("{"), t.rfind("}")
    try:
        parsed = json.loads(t[i2:j2 + 1])
    except (json.JSONDecodeError, ValueError):
        return {"lente": lente, "auditor": fornecedor,
                "erro": "resposta nao parseavel", "bruto": txt[:600]}
    parsed["lente"] = lente
    parsed["auditor"] = fornecedor
    return parsed


def main() -> None:
    tarefas = []
    for nome, (instr, mat) in LENTES.items():
        alvos = FORNECEDORES if nome in CRITICAS else (FORNECEDORES[1],)
        for f in alvos:
            tarefas.append((nome, instr, mat, f))
    print(f"auditoria independente · {len(LENTES)} lentes · {len(tarefas)} pareceres")
    print(f"  criticas em duplicata: {', '.join(CRITICAS)}\n")
    resultados = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futuros = {pool.submit(chamar, nome, instr, ler(*mat), f): f"{nome}@{f}"
                   for nome, instr, mat, f in tarefas}
        for fut in concurrent.futures.as_completed(futuros):
            r = fut.result()
            resultados.append(r)
            rot = futuros[fut]
            if "erro" in r:
                print(f"  [erro] {rot}: {r['erro'][:100]}", flush=True)
            else:
                w = r.get("weaknesses", [])
                o = r.get("opportunities", [])
                sev = {}
                for x in w:
                    sev[x.get("severity", "?")] = sev.get(x.get("severity", "?"), 0) + 1
                print(f"  {rot:<38} nota {r.get('score','?'):<5} "
                      f"{len(w)} fraquezas {sev} · {len(o)} oportunidades", flush=True)

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nescrito: {SAIDA}")


if __name__ == "__main__":
    main()
