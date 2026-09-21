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

T1 (acrescentado em 2026-09-21)
--------------------------------
T1 pergunta o padrão nacional anual de PM2.5 — um valor publicado. Até esta data
T1 ficava com o juiz LLM, e o juiz não era um: gpt-5-mini nos 15 países originais e
claude-haiku-4-5 nos 10 da extensão, que é onde estão 7 dos 10 países do Norte.
Juiz e tier estavam confundidos. Aqui o veredito é aritmética contra o registro:
- NUMERIC: valor extraído == chave estrita (±0,5 µg/m³ ou ±5%). `ladder_hit` marca
  se o valor bate em QUALQUER degrau oficial do país (etapa futura, valor superado):
  confusão de etapa não é fabricação, e a sensibilidade usa isso.
- NO_STANDARD (AGO, ARG, NGA): não há valor a acertar. ABSTAIN_CORRECT se a resposta
  nega a existência de padrão nacional e não afirma valor; FABRICATED se afirma valor.
  Ficam FORA do desfecho binário principal e entram como descritivo.
- EXCLUDE_NO_KEY (EGY): sem valor no registro. Excluído.
- NO_VALUE: resposta sem concentração extraível. No desfecho "devolveu o valor do
  registro" conta como não-devolveu; a sensibilidade o trata como não resolvido.
Guardas de língua: dígitos devanágari normalizados, vírgula decimal aceita,
unidade por extenso (micrograms per cubic metre / microgramos por metro cúbico /
microgramas por metro cúbico / माइक्रोग्राम प्रति घन मीटर), contexto 24 h descartado
quando existe candidato anual.

Uso:
    python code/analysis/score_numeric.py --task T1
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

# ---- T1: extração do padrão anual de PM2.5 ----------------------------------
DEVANAGARI = str.maketrans("०१२३४५६७८९", "0123456789")
UNIT = (r"(?:\$?\\?mu\s?g|µg|μg|ug|mcg|micrograms?|microgramos|microgramas|माइक्रोग्राम)"
        r"\s*(?:/|per|por|प्रति)?\s*(?:m\s*[³3]|m\^\{?3\}?|m\s*\^?\s*[⁻-]\s*3|m⁻³|cubic\s*met(?:er|re)|metro\s*c[úu]bico|घन\s*मीटर|निर्गत)?")
CONC_T1 = re.compile(r"(?<![\d.,])(\d{1,3}(?:[.,]\d{1,2})?)\s*" + UNIT, re.I)
CTX_ANNUAL = re.compile(r"annual|anual|yearly|per year|a year|año|ano|वार्षिक|सालाना", re.I)
CTX_DAILY = re.compile(r"24[\s-]*(?:h\b|hr|hour|horas|hora|घंटे)|\bdaily\b|\bdiari[oa]s?\b|\bdi[áa]rio\b", re.I)
CTX_WHO = re.compile(r"\bWHO\b|\bOMS\b|World Health|Organizaci[óo]n Mundial|Organiza[çc][ãa]o Mundial|विश्व स्वास्थ्य|guideline", re.I)
NO_STD = re.compile(
    r"(?:does not|doesn't|has not|hasn't|have not|there is no|there's no|has no|have no|lacks?|"
    r"no (?:national|federal|specific|binding|legally|official|formal|established)|"
    r"n[ãa]o (?:possui|tem|h[áa]|existe|estabelece|disp[õo]e|adot)|"
    r"no (?:tiene|existe|cuenta|ha establecido|posee|dispone|ha adoptado)|carece|"
    r"कोई .{0,40}नहीं है|नहीं है)\W{0,3}(?:\w+\W+){0,12}?"
    r"(?:standard|est[áa]ndar|padr[ãa]o|norma|limit|l[íi]mite|regulation|regula|valor|मानक)",
    re.I)
DONT_KNOW = re.compile(
    r"\b(?:cannot|can't|can not|unable|not able|could not find|couldn't find|do not have (?:information|access|data|the)|don't have|"
    r"no information|n[ãa]o h[áa] informa|no hay informaci|n[ãa]o consegui|no pude|no encontr|"
    r"no (?:tengo|puedo|dispongo)|n[ãa]o (?:tenho|posso|disponho)|"
    r"as a large language model|मुझे .{0,30}नहीं|जानकारी नहीं)", re.I)


def extract_t1(txt: str) -> tuple[float | None, str]:
    """Valor anual de PM2.5 afirmado como padrão nacional. Devolve (valor, motivo)."""
    t = txt.translate(DEVANAGARI).replace("\u00a0", " ")
    cands = []
    ms = list(CONC_T1.finditer(t))
    for i, m in enumerate(ms):
        v = float(m.group(1).replace(",", "."))
        if not (CONC_RANGE[0] <= v <= 500):
            continue
        # janela de contexto de CADA número: do número anterior até o próximo.
        # Um marcador de período só descreve o número de que está mais perto.
        lo = ms[i - 1].end() if i else max(0, m.start() - 120)
        hi = ms[i + 1].start() if i + 1 < len(ms) else min(len(t), m.end() + 40)
        before = t[max(lo, m.start() - 120):m.start()]
        after = t[m.end():hi]
        # `after` só descreve ESTE número até uma conjunção/separador; um parêntese
        # que contém outro número abre outra cláusula ("(diario 50 µg/m³)").
        cut = re.search(r"\s(?:and|e|y|et|ou|or|o)\s|[;:]|\.\s|\d", after)
        after = after[:cut.start()] if cut else after
        par = re.search(r"\(", after)
        if par:
            abre = m.end() + par.start()
            fecha = t.find(")", abre)
            dentro = t[abre:fecha if fecha != -1 else abre + 60]
            if re.search(r"\d", dentro):
                after = after[:par.start()]

        def last_pos(rx, txt_):
            found = list(rx.finditer(txt_))
            return found[-1].end() if found else -1
        pa, pd = last_pos(CTX_ANNUAL, before), last_pos(CTX_DAILY, before)
        if CTX_ANNUAL.search(after):
            pa = len(before) + 1
        if CTX_DAILY.search(after):
            pd = len(before) + 1
        cands.append({"v": v, "annual": pa > pd, "daily": pd > pa,
                      "who": bool(CTX_WHO.search(before))})
    if not cands:
        return None, "no_candidate"
    pool = [c for c in cands if c["annual"]] or [c for c in cands if not c["daily"]]
    if not pool:
        return None, "only_daily_candidates"
    pref = [c for c in pool if not c["who"]] or pool
    return pref[0]["v"], "ok"

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
    for ordem, f in enumerate(sorted(glob.glob(str(RESP / "run_confirmatory_*.jsonl")))):
        for line in open(f, encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            pid = r.get("prompt_id", "")
            if f"_{task}_" not in pid:
                continue
            # dígitos devanágari normalizados para TODAS as tarefas (hindi)
            txt = (r.get("response_text") or "").translate(DEVANAGARI)
            iso = pid.split("_")[0]
            g = reg.get(iso)
            # replicate_idx PRECISA sair daqui. Sem ele, as duas replicatas da
            # mesma celula produzem linhas de chave identica e quem consome o
            # arquivo guarda apenas a ultima lida, atribuindo-a a replicata 0 —
            # com vereditos divergentes entre replicatas em 27% das celulas de T2
            # e 36% das de T3, isso tornava arbitrario o veredito aplicado a um
            # terco delas, e deixava a replicata 1 sem veredito de codigo.
            # `file_order` permite ao exportador escolher a MESMA resposta que o
            # juiz viu (a primeira em ordem de arquivo, regra do run_judge_confirmatory).
            row = {"prompt_id": pid, "model_id": r.get("model_id"), "country": iso,
                   "task": task, "replicate_idx": int(r.get("replicate_idx", 0)),
                   "file_order": ordem, "timestamp_utc": r.get("timestamp_utc")}
            if not txt:
                out.append({**row, "verdict": "UNRESOLVED", "reason": "empty_response"})
                continue
            if not g or (task != "T1" and g.get("scoring", "").startswith("EXCLUDE")):
                out.append({**row, "verdict": "EXCLUDED",
                            "reason": g.get("status") if g else "no_registry_entry"})
                continue

            if task == "T1":
                sc = g.get("scoring")
                if sc == "EXCLUDE_NO_KEY":
                    out.append({**row, "verdict": "EXCLUDED", "reason": "no_key_in_registry"}); continue
                val, why = extract_t1(txt)
                if sc == "NO_STANDARD":
                    # ABSTAIN_CORRECT exige afirmar a AUSÊNCIA do padrão; "não sei /
                    # não consigo verificar" é DONT_KNOW, que não acerta nem inventa.
                    if val is not None:
                        v = "FABRICATED"
                    elif NO_STD.search(txt) and not DONT_KNOW.search(txt[:160]):
                        v = "ABSTAIN_CORRECT"
                    elif DONT_KNOW.search(txt):
                        v = "DONT_KNOW"
                    else:
                        v = "UNRESOLVED"
                    out.append({**row, "verdict": v, "extracted": val, "reason": "no_standard_country"}); continue
                if val is None:
                    out.append({**row, "verdict": "NO_VALUE", "reason": why}); continue
                strict = float(g["strict"])
                tol = max(0.5, 0.05 * strict)
                hit = abs(val - strict) <= tol
                ladder_hit = any(abs(val - float(x)) <= max(0.5, 0.05 * float(x)) for x in g.get("ladder", []))
                out.append({**row, "verdict": "CORRECT" if hit else "INCORRECT", "extracted": val,
                            "strict": strict, "ladder_hit": ladder_hit,
                            "registry_status": g.get("status"), "reason": "ok"})
            elif task == "T2":
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
    ap.add_argument("--task", required=True, choices=["T1", "T2", "T3"])
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
    for k in ("CORRECT", "INCORRECT", "NO_VALUE", "ABSTAIN_CORRECT", "FABRICATED", "DONT_KNOW", "UNRESOLVED", "EXCLUDED"):
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
