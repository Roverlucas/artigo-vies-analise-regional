#!/usr/bin/env python3
"""Retoma o painel de juizes ate fechar, atravessando o reset da cota diaria.

O free tier do Gemini corta em 1.000 requisicoes por dia e so libera na
meia-noite do Pacifico. Nenhum backoff recupera isso: a unica saida e esperar o
reset. Este laco roda o painel, mede quanto falta, dorme e tenta de novo, ate a
fila fechar. Como run_judge_panel.py e retomavel e pula o que ja gravou, cada
tentativa custa apenas o que ainda falta.
"""
import json
import pathlib
import subprocess
import sys
import time

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SCORES = RAIZ / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_panel_repontuacao.jsonl"
ALVO_POR_JUIZ = 3191
ESPERA = 1800  # 30 min entre tentativas


def gravados(juiz: str) -> int:
    if not SCORES.exists():
        return 0
    n = 0
    with SCORES.open(encoding="utf-8") as f:
        for linha in f:
            try:
                if json.loads(linha).get("judge") == juiz:
                    n += 1
            except json.JSONDecodeError:
                continue
    return n


def main() -> int:
    tentativa = 0
    while True:
        feitos = gravados("gemini_2_5_pro")
        if feitos >= ALVO_POR_JUIZ:
            print(f"[retomador] painel completo: gemini {feitos}/{ALVO_POR_JUIZ}", flush=True)
            return 0
        tentativa += 1
        print(f"[retomador] tentativa {tentativa}: faltam {ALVO_POR_JUIZ - feitos} do gemini",
              flush=True)
        subprocess.run([sys.executable, str(RAIZ / "code" / "analysis" / "run_judge_panel.py")],
                       cwd=RAIZ)
        depois = gravados("gemini_2_5_pro")
        if depois >= ALVO_POR_JUIZ:
            print(f"[retomador] painel completo: gemini {depois}/{ALVO_POR_JUIZ}", flush=True)
            return 0
        print(f"[retomador] parou em {depois}; dormindo {ESPERA // 60} min "
              f"(cota diaria reseta na meia-noite do Pacifico)", flush=True)
        time.sleep(ESPERA)


if __name__ == "__main__":
    raise SystemExit(main())
