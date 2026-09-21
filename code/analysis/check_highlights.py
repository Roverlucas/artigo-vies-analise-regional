#!/usr/bin/env python3
"""Gate de formato: os Highlights cabem no limite que o GIQ impõe?

O limite é de 3 a 5 marcadores com no máximo 85 caracteres cada, espaços
incluídos. É o tipo de regra que se descobre violada no portal de submissão,
depois de tudo pronto, e que custa uma rodada inteira por um detalhe de contagem.
Barato conferir aqui.
"""
from __future__ import annotations

import pathlib
import re
import sys

ARQ = pathlib.Path(__file__).resolve().parents[2] / "latex" / "highlights.tex"
LIMITE = 85
MIN_ITENS, MAX_ITENS = 3, 5


def main() -> int:
    if not ARQ.exists():
        print(f"FALHA: {ARQ} não existe")
        return 1
    itens = re.findall(r"\\item\s+(.+?)\s*(?=\n\\item|\n\\end\{itemize\})",
                       ARQ.read_text(encoding="utf-8"), re.S)
    itens = [re.sub(r"\s+", " ", i).strip() for i in itens]

    # os highlights carregam macros (\\nXXX de latex/numbers.tex); o portal ve o
    # numero, nao a macro — expandir antes de contar caracteres
    import re as _re
    import pathlib as _pl; _nums = _pl.Path(__file__).resolve().parents[2] / "latex" / "numbers.tex"
    if _nums.exists():
        _M = dict(_re.findall(r"\\newcommand\{\\(n[a-z]+)\}\{((?:[^{}]|\{[^{}]*\})*)\}", _nums.read_text(encoding="utf-8")))
        def _exp(t):
            for k in sorted(_M, key=len, reverse=True):
                t = _re.sub(r"\\" + k + r"(?![a-zA-Z])(\{\})?", _M[k].replace("{,}", ","), t)
            return t
        itens = [_exp(t) for t in itens]
    print(f"HIGHLIGHTS — {len(itens)} marcadores (o GIQ aceita {MIN_ITENS} a {MAX_ITENS})\n")
    falhou = False
    for i, t in enumerate(itens, 1):
        n = len(t)
        marca = "" if n <= LIMITE else f"  <- EXCEDE em {n - LIMITE}"
        if n > LIMITE:
            falhou = True
        print(f"  {i}. [{n:>3}/{LIMITE}] {t}{marca}")

    if not MIN_ITENS <= len(itens) <= MAX_ITENS:
        print(f"\nFALHA: {len(itens)} marcadores, fora da faixa permitida")
        falhou = True
    print("\nFALHA: algum marcador excede o limite" if falhou else "\nOK: dentro das regras do GIQ")
    return 1 if falhou else 0


if __name__ == "__main__":
    raise SystemExit(main())
