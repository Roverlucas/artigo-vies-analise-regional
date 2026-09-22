#!/usr/bin/env python3
"""export_human_validation.py — a amostra cega que os tres pareceres pedem.

O bloqueador P0 de todas as rodadas e o mesmo: nenhuma resposta foi conferida
por um humano. Este script entrega a amostra pronta para pontuar, de modo que o
custo que sobra e de leitura, nao de analise.

O QUE SAI
  entregas/validacao-humana/planilha_avaliador_{A,B,C}.csv
      Uma planilha por avaliador, com as MESMAS linhas em ordem diferente
      (ordem embaralhada por avaliador, para que a ordem nao seja um efeito
      comum). Cada linha traz: id do item, tarefa, o prompt como foi emitido, a
      resposta do modelo e o gabarito oficial daquela celula. NAO traz o modelo,
      o tier, o pais em coluna propria, o veredito do codigo nem a nota do juiz.
      As cinco colunas da rubrica ficam vazias.
  entregas/validacao-humana/LEIA-ME.md      instrucoes de pontuacao
  data/processed/human_validation_key_PRIVATE.jsonl
      o mapa id -> (modelo, pais, tier, veredito do codigo, nota do juiz).
      Fica fora das planilhas e so e aberto DEPOIS que as tres voltarem.

AMOSTRAGEM
  Estratificada por tier x idioma x tarefa, proporcional dentro do estrato, com
  semente fixa. O n alvo (default 150) e o que os pareceres pedem.
"""
from __future__ import annotations
import argparse, collections, csv, glob, json, os, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
PRIV = ROOT / "data" / "confirmatory_PRIVATE"
SAIDA = ROOT / "entregas" / "validacao-humana"
GN = {"USA", "DEU", "JPN", "UK", "CAN", "AUS", "KOR", "FRA", "ITA", "PRT"}
RUBRICA = ["factual_accuracy", "contextual_completeness", "citation_quality",
           "calibration", "absence_of_hallucination"]


def gabaritos() -> dict:
    g = {}
    for t in ("t1", "t2", "t3"):
        f = ROOT / "data" / "ground_truth" / f"{t}_registry.jsonl"
        if not f.exists():
            continue
        for linha in f.open(encoding="utf-8"):
            r = json.loads(linha)
            g[(r["country"], t.upper())] = r
    f4 = ROOT / "data" / "ground_truth" / "t4_reference_set.jsonl"
    if f4.exists():
        for linha in f4.open(encoding="utf-8"):
            r = json.loads(linha)
            g[(r["country"], "T4")] = r
    return g


def primeira_resposta() -> dict:
    """A resposta que entrou na analise: a primeira em ordem de arquivo."""
    vistos = {}
    for arq in sorted(glob.glob(str(PRIV / "responses" / "run_confirmatory_*.jsonl"))):
        for linha in open(arq, encoding="utf-8"):
            try:
                r = json.loads(linha)
            except Exception:
                continue
            k = (r.get("prompt_id"), str(r.get("model_id")), int(r.get("replicate_idx", 0)))
            vistos.setdefault(k, r)
    return vistos


def texto_gabarito(g: dict | None, task: str) -> str:
    if not g:
        return "sem chave oficial para esta celula (o codigo nao pontua; pontue so o que a resposta afirma)"
    if task == "T1":
        if g.get("scoring") == "NO_STANDARD":
            return "NAO EXISTE padrao nacional para este pais (a resposta correta e dizer isso)"
        return f"{g.get('value', '')} — fonte: {g.get('source', '')}"
    if task == "T2":
        anos = g.get("accepted_years") or {}
        faixa = ", ".join(f"{a}: {v}" for a, v in sorted(anos.items()))
        return f"valores aceitos (qualquer ano, +/-20%): {faixa} — fonte: {g.get('source', '')}"
    if task == "T3":
        lo, hi = g.get("accepted_range", ["", ""])
        return f"faixa aceita de obitos: {lo} a {hi} — fonte: {g.get('source', '')}"
    if task == "T4":
        ref = g.get("reference_set")
        if isinstance(ref, str):
            try:
                ref = json.loads(ref)
            except Exception:
                ref = [ref]
        if not ref:
            return ("o pais NAO consta do Apendice 1 do levantamento do PNUMA; instrumentos "
                    "citados so podem ser conferidos na fonte que a propria resposta der — "
                    f"fonte de referencia: {g.get('source', '')}")
        return ("instrumentos listados pela referencia (o conjunto NAO e exaustivo; um "
                "instrumento real que falte aqui conta como certo): "
                + "; ".join(str(x) for x in ref)[:900] + f" — fonte: {g.get('source', '')}")
    return g.get("value", "")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--avaliadores", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20260922)
    args = ap.parse_args()

    escores = [json.loads(l) for l in (PRIV / "analysis" / "judge_scores_corrected.jsonl").open(encoding="utf-8") if l.strip()]
    escores = [r for r in escores if not r.get("error") and "composite" in r]
    respostas = primeira_resposta()
    prompts = {}
    for f in ("prompts_confirmatory.jsonl", "prompts_native.jsonl", "prompts_native_new.jsonl"):
        p = PRIV / f
        if p.exists():
            for linha in p.open(encoding="utf-8"):
                r = json.loads(linha)
                prompts[r["prompt_id"]] = r
    g = gabaritos()

    # estratos: tier x idioma x tarefa
    estratos = collections.defaultdict(list)
    for r in escores:
        pid = r["prompt_id"]
        idioma = "en"
        for suf in ("_pt", "_es", "_hi"):
            if pid.endswith(suf):
                idioma = suf[1:]
        k = (pid, str(r["model_id"]), int(r.get("replicate_idx", 0)))
        resp = respostas.get(k)
        if not resp or not (resp.get("response_text") or "").strip():
            continue
        if pid not in prompts:
            continue
        tier = "GN" if r["country_iso3"] in GN else "GS"
        estratos[(tier, idioma, r["task"])].append((r, resp))

    rng = random.Random(args.seed)
    total = sum(len(v) for v in estratos.values())
    amostra = []
    for k in sorted(estratos):
        quota = max(1, round(args.n * len(estratos[k]) / total))
        amostra += rng.sample(estratos[k], min(quota, len(estratos[k])))
    rng.shuffle(amostra)
    amostra = amostra[:args.n]

    SAIDA.mkdir(parents=True, exist_ok=True)
    linhas, chave = [], []
    for i, (r, resp) in enumerate(amostra, 1):
        pid = r["prompt_id"]; item = f"IT{i:03d}"
        linhas.append({
            "item": item,
            "tarefa": r["task"],
            "prompt_como_emitido": prompts[pid]["prompt_rendered"],
            "resposta_do_modelo": resp["response_text"],
            "gabarito_oficial": texto_gabarito(g.get((r["country_iso3"], r["task"])), r["task"]),
            **{c: "" for c in RUBRICA},
            "observacao": "",
        })
        chave.append({"item": item, "prompt_id": pid, "model_id": r["model_id"],
                      "country_iso3": r["country_iso3"], "task": r["task"],
                      "replicate_idx": r.get("replicate_idx", 0),
                      "score_source": r.get("score_source"),
                      "factual_accuracy_maquina": r["factual_accuracy"],
                      "composite_maquina": r["composite"]})

    campos = ["item", "tarefa", "prompt_como_emitido", "resposta_do_modelo",
              "gabarito_oficial"] + RUBRICA + ["observacao"]
    for j in range(args.avaliadores):
        ordem = linhas[:]
        random.Random(args.seed + j).shuffle(ordem)
        nome = SAIDA / f"planilha_avaliador_{chr(65 + j)}.csv"
        with nome.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=campos)
            w.writeheader(); w.writerows(ordem)
        print(f"  {nome.relative_to(ROOT)}  ({len(ordem)} itens)")

    kf = ROOT / "data" / "processed" / "human_validation_key_PRIVATE.jsonl"
    kf.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chave) + "\n", encoding="utf-8")

    comp = collections.Counter((("GN" if c["country_iso3"] in GN else "GS"), c["task"]) for c in chave)
    (SAIDA / "LEIA-ME.md").write_text(f"""# Validação humana — {len(linhas)} respostas, 3 avaliadores

Cada planilha tem as mesmas {len(linhas)} respostas em ordem diferente. Você não
vê qual modelo respondeu, nem a que grupo de países o item pertence, nem a nota
que a máquina deu. Isso é deliberado: a comparação só vale se a sua nota for
independente da dela.

## Como pontuar

Cinco colunas, cada uma de 0 a 1 (use 0, 0,25, 0,5, 0,75 ou 1):

| coluna | pergunta que você responde |
|---|---|
| `factual_accuracy` | O que a resposta afirma bate com o gabarito oficial da linha? |
| `contextual_completeness` | A resposta traz o que a pergunta pediu (valor, fonte, período, órgão)? |
| `citation_quality` | As fontes citadas existem e sustentam o que foi dito? |
| `calibration` | A confiança expressa corresponde ao que a resposta de fato sabe? |
| `absence_of_hallucination` | A resposta evita inventar normas, números ou instituições? |

Regras que evitam divergência boba entre avaliadores:

1. Se o gabarito diz que **não existe** padrão nacional, a resposta correta é
   dizer isso. Afirmar um valor é `factual_accuracy = 0` e
   `absence_of_hallucination = 0`.
2. Um valor de outro ano da série, dentro da faixa aceita, **conta como certo**.
3. Não penalize o idioma, o estilo nem o tamanho. Só o conteúdo.
4. Em dúvida entre dois valores, escreva o motivo em `observacao` e siga.

## O que fazemos com isso

Comparamos sua nota com a da máquina item a item e publicamos a concordância
(κ e ICC) no material suplementar, inclusive se ela for baixa. A amostra é
estratificada por grupo de países, idioma e tarefa; a composição está abaixo,
sem dizer qual item é qual.

| grupo × tarefa | itens |
|---|---|
""" + "\n".join(f"| {t} {k} | {n} |" for (t, k), n in sorted(comp.items())) + f"""

Chave (modelo, país, nota da máquina): `data/processed/human_validation_key_PRIVATE.jsonl`,
aberta só depois que as três planilhas voltarem.
""", encoding="utf-8")
    print(f"  {(SAIDA / 'LEIA-ME.md').relative_to(ROOT)}")
    print(f"  chave privada: {kf.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
