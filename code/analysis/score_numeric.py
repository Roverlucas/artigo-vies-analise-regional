#!/usr/bin/env python3
"""Pontuação determinística de T2 e T3: extrai o número da resposta e compara com
a faixa aceita do registry. O que o código não resolve fica para o juiz LLM.

POR QUE EXISTE
--------------
T2 pergunta uma concentração e T3 pergunta um número de óbitos. Comparar número
com faixa é aritmética, e aritmética se faz com código. Pagar um LLM para isso é
caro e menos confiável: o modelo pode errar a comparação, o código não.

REGRA DE OURO DESTE ARQUIVO
---------------------------
Um extrator que erra em silêncio é pior que gabarito nenhum, que é exatamente o
defeito que esta rodada existe para consertar. Por isso todo valor extraído passa
por guardas de plausibilidade, e tudo que não passa vira `UNRESOLVED` e vai para
o juiz. Preferir mandar caso duvidoso para o LLM a inventar uma nota.

GUARDAS IMPLEMENTADAS, E O QUE CADA UMA PEGOU
---------------------------------------------
- ANO: `2022` e `2013` estavam sendo lidos como número de óbitos.
- POPULAÇÃO: `108.000.000` foi extraído como mortalidade do Egito; é a população.
  Óbitos atribuíveis nunca chegam a 1% da população de um país.
- ORDEM DE GRANDEZA: valor fora de [10, 3_000_000] para óbitos, ou fora de
  [0.1, 2000] µg/m³ para concentração, não é resposta à pergunta feita.
- AMBIGUIDADE: se a resposta traz vários candidatos incompatíveis entre si, o
  código se abstém em vez de escolher.

Uso:
    python code/analysis/score_numeric.py --task T2
    python code/analysis/score_numeric.py --task T3 --out data/processed/
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESP = ROOT / "data" / "confirmatory_PRIVATE" / "responses"

# Populações aproximadas (milhões, ordem de grandeza) só para a guarda de
# plausibilidade. Não entram em nenhum cálculo do artigo.
POP_M = {
    "AGO": 36, "ARG": 46, "AUS": 26, "BGD": 173, "BRA": 215, "CAN": 39, "CHL": 20,
    "COL": 52, "DEU": 84, "EGY": 111, "FRA": 68, "IDN": 278, "IND": 1429, "ITA": 59,
    "JPN": 124, "KEN": 55, "KOR": 52, "MEX": 128, "NGA": 224, "PER": 34, "PHL": 117,
    "PRT": 10, "UK": 68, "USA": 335, "ZAF": 60,
}
MAX_DEATH_FRACTION = 0.01   # óbitos atribuíveis nunca chegam a 1% da população
DEATH_RANGE = (10, 3_000_000)
CONC_RANGE = (0.1, 2000.0)  # µg/m³

ANO = re.compile(r"^(19|20)\d{2}$")
CONC = re.compile(r"(\d{1,4}(?:[.,]\d+)?)\s*(?:µg|ug|μg)\s*/?\s*m\s*[³3]", re.I)
DEATH_CTX = re.compile(
    r"(\d{1,3}(?:[.,]\d{3})+|\d{4,7})[^.]{0,60}?(?:deaths|mortes|óbitos|obitos|fatalities|premature)"
    r"|(?:deaths|mortes|óbitos|obitos|fatalities|premature)[^.]{0,60}?(\d{1,3}(?:[.,]\d{3})+|\d{4,7})",
    re.I)
DEATH_WORD = re.compile(
    r"\b(\d{1,3}(?:[.,]\d+)?)\s*(thousand|mil\b|million|milh[õo]es)\b[^.]{0,50}?"
    r"(?:deaths|mortes|óbitos|obitos|premature)", re.I)


def _int(s: str) -> int | None:
    s = s.replace(" ", "")
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", s):
        return int(re.sub(r"[.,]", "", s))
    if re.fullmatch(r"\d{4,7}", s):
        return int(s)
    return None


def extract_concentration(txt: str) -> tuple[float | None, str]:
    cands = []
    for m in CONC.finditer(txt):
        v = float(m.group(1).replace(",", "."))
        if CONC_RANGE[0] <= v <= CONC_RANGE[1]:
            cands.append(v)
    if not cands:
        return None, "no_candidate"
    # candidatos muito discordantes entre si: o código se abstém
    if max(cands) > 3 * min(cands) and len(set(cands)) > 1:
        return None, "ambiguous_candidates"
    return cands[0], "ok"


def extract_deaths(txt: str, iso: str) -> tuple[int | None, str]:
    teto = int(POP_M.get(iso, 100) * 1e6 * MAX_DEATH_FRACTION)
    cands = []
    for m in DEATH_CTX.finditer(txt):
        raw = next((g for g in m.groups() if g), None)
        if not raw or ANO.match(re.sub(r"[.,]", "", raw)):
            continue
        v = _int(raw)
        if v and DEATH_RANGE[0] <= v <= min(DEATH_RANGE[1], teto):
            cands.append(v)
    for m in DEATH_WORD.finditer(txt):
        base = float(m.group(1).replace(",", "."))
        u = m.group(2).lower()
        mult = 1_000_000 if u.startswith(("million", "milh")) else 1_000
        v = int(base * mult)
        if DEATH_RANGE[0] <= v <= min(DEATH_RANGE[1], teto):
            cands.append(v)
    if not cands:
        return None, "no_candidate_or_implausible"
    if max(cands) > 5 * min(cands) and len(set(cands)) > 1:
        return None, "ambiguous_candidates"
    return cands[0], "ok"


def load_registry(task: str) -> dict:
    f = ROOT / "data" / "ground_truth" / f"{task.lower()}_registry.jsonl"
    return {json.loads(l)["country"]: json.loads(l) for l in f.open(encoding="utf-8")}


def score(task: str) -> list[dict]:
    reg = load_registry(task)
    out = []
    for f in glob.glob(str(RESP / "run_confirmatory_*.jsonl")):
        for line in open(f, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            pid = r.get("prompt_id", "")
            if f"_{task}_" not in pid:
                continue
            txt = r.get("response_text") or ""
            iso = pid.split("_")[0]
            g = reg.get(iso)
            row = {"prompt_id": pid, "model_id": r.get("model_id"), "country": iso,
                   "task": task}
            if not txt:
                out.append({**row, "verdict": "UNRESOLVED", "reason": "empty_response"})
                continue
            if not g or g.get("scoring", "").startswith("EXCLUDE"):
                out.append({**row, "verdict": "EXCLUDED",
                            "reason": g.get("status") if g else "no_registry_entry"})
                continue

            if task == "T2":
                val, why = extract_concentration(txt)
                if val is None:
                    out.append({**row, "verdict": "UNRESOLVED", "reason": why}); continue
                tol = g.get("tolerance_relative", 0.2)
                aceitos = {int(y): v for y, v in (g.get("accepted_years") or {}).items()}
                hit = any(abs(val - v) <= tol * v for v in aceitos.values())
                out.append({**row, "verdict": "CORRECT" if hit else "INCORRECT",
                            "extracted": val, "accepted": aceitos, "reason": "ok"})
            else:
                val, why = extract_deaths(txt, iso)
                if val is None:
                    out.append({**row, "verdict": "UNRESOLVED", "reason": why}); continue
                lo, hi = g["accepted_range"]
                out.append({**row, "verdict": "CORRECT" if lo <= val <= hi else "INCORRECT",
                            "extracted": val, "accepted_range": [lo, hi], "reason": "ok"})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=["T2", "T3"])
    ap.add_argument("--out", type=pathlib.Path,
                    default=ROOT / "data" / "processed")
    a = ap.parse_args()

    rows = score(a.task)
    a.out.mkdir(parents=True, exist_ok=True)
    dest = a.out / f"numeric_scores_{a.task}.jsonl"
    with dest.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    c = collections.Counter(r["verdict"] for r in rows)
    n = len(rows)
    print(f"escrito: {dest}  ({n} respostas de {a.task})")
    for k in ("CORRECT", "INCORRECT", "UNRESOLVED", "EXCLUDED"):
        if c[k]:
            print(f"  {k:<11} {c[k]:>5}  ({100*c[k]/n:.1f}%)")
    resolvido = c["CORRECT"] + c["INCORRECT"]
    print(f"  → resolvido por codigo: {resolvido}/{n} = {100*resolvido/n:.1f}%")
    print(f"  → vai para o juiz LLM : {c['UNRESOLVED']}")
    motivos = collections.Counter(r["reason"] for r in rows if r["verdict"] == "UNRESOLVED")
    if motivos:
        print("  motivos de abstencao:", dict(motivos.most_common(4)))


if __name__ == "__main__":
    main()
