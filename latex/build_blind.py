#!/usr/bin/env python3
"""Gera a versao anonima para a revisao duplo-cega do GIQ.

Por que um script e nao uma copia editada a mao: a versao cega tem de ser
regenerada a cada revisao do manuscrito, e uma copia manual diverge na primeira
vez que alguem esquece de repetir uma edicao. Pior, o que ela precisa remover nao
e obvio — o vazamento mais serio aqui nao esta no bloco de autores, e sim no
endereco do repositorio publico, que carrega o nome de usuario do autor
correspondente no proprio URL.

O que e removido, e por que cada item identifica:
  - bloco de autores, afiliacoes, ORCIDs e e-mail de contato
  - URL do repositorio (contem o usuario do GitHub do autor)
  - agradecimentos e contribuicoes CRediT (nomes proprios)
  - supervisao institucional citada nos metodos e no suplemento
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
CEGO = RAIZ / "blind"

# (padrao, substituto, rotulo do que estava vazando)
#
# O bloco de autores nao precisa mais ser removido a mao: a classe elsarticle tem
# a opcao doubleblind, que suprime autores e afiliacoes na renderizacao. O que a
# opcao NAO faz — e por isso este script continua existindo — e limpar o resto do
# documento. O vazamento mais serio deste manuscrito nunca esteve no bloco de
# autores: esta no endereco do repositorio publico, que carrega o nome de usuario
# do autor correspondente no proprio URL, e que aparece tambem numa tabela do
# suplemento.
REGRAS = [
    (r"\\documentclass\[review,authoryear,12pt\]\{elsarticle\}",
     "\\\\documentclass[review,authoryear,doubleblind,12pt]{elsarticle}",
     "classe passa a doubleblind (suprime autores na renderizacao)"),
    # A opcao doubleblind limpa o PDF, nao o fonte. Se o portal pedir o .tex, ou
    # se alguem abrir o arquivo, os nomes continuam la. Removemos os dois.
    (r"\\author\[[^\]]*\]\{[^}]*\}(\s*\\corref\{[^}]*\})?", "", "linhas de autor no fonte"),
    (r"\\ead\{[^}]*\}", "", "e-mail de contato no fonte"),
    (r"\\cortext\[[^\]]*\]\{[^}]*\}", "", "nota de autor correspondente"),
    (r"\\affiliation\[[^\]]*\]\{[^}]*(\{[^}]*\}[^}]*)*\}", "", "afiliacoes no fonte"),
    (r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",
     "https://ANONYMISED-FOR-REVIEW", "URL do repositorio com o usuario do autor"),
    (r"\{github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\}",
     "{repository URL withheld for double-blind review}", "URL visivel no texto"),
    (r"\\section\*\{Acknowledgements\}.*?(?=\\section\*)", "", "agradecimentos"),
    (r"\\section\*\{Author contributions\}.*?(?=\\section\*)", "", "contribuicoes CRediT"),
    (r"\(PPGSAU/UTFPR\)", "(institutional details withheld for review)",
     "supervisao institucional"),
    (r"PPGSAU/UTFPR", "[institution withheld]", "instituicao no texto"),
]


def main() -> None:
    if CEGO.exists():
        shutil.rmtree(CEGO)
    CEGO.mkdir()
    for item in ("sections", "supplement", "references.bib", "main.tex",
                 "supplement.tex"):
        origem = RAIZ / item
        if not origem.exists():
            continue
        destino = CEGO / item
        if origem.is_dir():
            shutil.copytree(origem, destino)
        else:
            shutil.copy2(origem, destino)

    achados = []
    for tex in sorted(CEGO.rglob("*.tex")):
        s = tex.read_text(encoding="utf-8")
        antes = s
        for padrao, sub, rotulo in REGRAS:
            novo, n = re.subn(padrao, sub, s, flags=re.S)
            if n:
                achados.append((tex.name, rotulo, n))
                s = novo
        if s != antes:
            tex.write_text(s, encoding="utf-8")

    print("VERSAO ANONIMA GERADA")
    for nome, rotulo, n in achados:
        print(f"  {nome:<22} removido: {rotulo} ({n}x)")

    # verificacao final: nada dos termos identificadores pode sobrar
    proibidos = ("Roverlucas", "lucasrover", "UTFPR", "PPGSAU", "Unicamp", "UFPR",
                 "Descomplica", "Tadano", "Dominski", "Azevedo", "Bacalhau",
                 "Lucas Rover")
    vazou = []
    for tex in sorted(CEGO.rglob("*.tex")):
        s = tex.read_text(encoding="utf-8")
        for t in proibidos:
            if t in s:
                vazou.append((tex.name, t, s.count(t)))
    print()
    if vazou:
        print("  ATENCAO — ainda identificam o autor:")
        for nome, t, n in vazou:
            print(f"    {nome}: '{t}' ({n}x)")
        sys.exit(1)
    print("  verificacao: nenhum termo identificador restante")
    print(f"  saida: {CEGO}")


if __name__ == "__main__":
    main()
