#!/usr/bin/env python3
"""Testes nao parametricos usados em mais de uma analise, definidos uma vez so.

Antes deste modulo, `wilcoxon_p` estava copiada em tres scripts. Copias divergem:
basta corrigir uma e esquecer as outras para que o mesmo efeito saia com p
diferente dependendo de qual script o calculou. A auditoria independente
encontrou exatamente esse tipo de defeito latente — a formula nao corrigia
empates — e a correcao so e confiavel se existir um lugar unico para faze-la.
"""
from __future__ import annotations

import math


def wilcoxon_p(difs: list[float]) -> float:
    """Wilcoxon signed-rank bilateral, aproximacao normal COM correcao de empates.

    A correcao importa porque 69% dos pares deste estudo compartilham valor
    absoluto com outro par. Sem ela a variancia sob o nulo e superestimada, o que
    torna o teste conservador: o p sai maior do que deveria. Aqui isso nao muda
    nenhuma conclusao do efeito principal, cujo p esta na ordem de 1e-15, mas
    muda a margem em subgrupos pequenos, e um teste correto nao deve depender de
    o resultado ser folgado.
    """
    nz = [d for d in difs if d != 0]
    n = len(nz)
    if n < 10:
        return float("nan")

    ordenado = sorted(nz, key=abs)
    postos = [0.0] * n
    grupos: list[int] = []
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(ordenado[j + 1]) == abs(ordenado[i]):
            j += 1
        medio = (i + j) / 2 + 1
        for k in range(i, j + 1):
            postos[k] = medio
        grupos.append(j - i + 1)
        i = j + 1

    mais = sum(p for p, d in zip(postos, ordenado) if d > 0)
    media = n * (n + 1) / 4
    var = n * (n + 1) * (2 * n + 1) / 24
    # correcao de empates: subtrai a variancia que os grupos empatados nao tem
    var -= sum(t ** 3 - t for t in grupos if t > 1) / 48
    if var <= 0:
        return float("nan")
    z = (mais - media) / math.sqrt(var)
    return math.erfc(abs(z) / math.sqrt(2))
