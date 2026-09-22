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
    # entrada de deposito de dados: o campo author nomeia os tres autores
    (r"author\s*=\s*\{Rover, Lucas and Bacalhau, Eduardo Tadeu and Tadano, Yara\}",
     "author       = {Author(s) withheld for review}",
     "autores na entrada de deposito do .bib"),

    (r"\\documentclass\[review,authoryear,12pt\]\{elsarticle\}",
     "\\\\documentclass[review,authoryear,doubleblind,12pt]{elsarticle}",
     "classe passa a doubleblind (suprime autores na renderizacao)"),
    # A opcao doubleblind limpa o PDF, nao o fonte. Se o portal pedir o .tex, ou
    # se alguem abrir o arquivo, os nomes continuam la. Removemos os dois.
    # O padrao anterior casava \author[..]{Nome} mas deixava o \corref{cor}
    # pendurado com sua chave de fechamento, e o LaTeX morria em "Extra }".
    # A versao cega nunca compilou por isso. Casamos o bloco inteiro.
    (r"\\author\[[^\]]*\]\{(?:[^{}]|\{[^{}]*\})*\}", "", "linhas de autor no fonte"),
    (r"\\ead\{[^}]*\}", "", "e-mail de contato no fonte"),
    (r"\\cortext\[[^\]]*\]\{[^}]*\}", "", "nota de autor correspondente"),
    (r"\\affiliation\[[^\]]*\]\{[^}]*(\{[^}]*\}[^}]*)*\}", "", "afiliacoes no fonte"),
    # o \href inteiro: substituir so a URL deixava o segundo argumento intacto e
    # o texto visivel continuava exibindo o usuario do autor
    (r"\\href\{https://github\.com/[^}]*\}%?\s*\n?\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",
     "{repository URL withheld for double-blind review}", "\\href do repositorio"),
    (r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",
     "https://ANONYMISED-FOR-REVIEW", "URL do repositorio com o usuario do autor"),
    # o endereco visivel aparece em mais de um formato (texto simples, dentro de
    # \texttt, quebrado por \allowbreak); casar o usuario direto cobre todos
    (r"\\texttt\{github\.com/[A-Za-z0-9_.-]+/\}\\allowbreak\\texttt\{[A-Za-z0-9_.-]+\}",
     "{repository URL withheld for double-blind review}", "URL em texttt quebrado"),
    (r"\{github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\}",
     "{repository URL withheld for double-blind review}", "URL visivel no texto"),
    (r"github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",
     "repository URL withheld for review", "qualquer ocorrencia restante do endereco"),
    (r"\\section\*\{Acknowledgements\}.*?(?=\\section\*)", "", "agradecimentos"),
    (r"\\section\*\{Author contributions\}.*?(?=\\section\*)", "", "contribuicoes CRediT"),
    (r"\(PPGSAU/UTFPR\)", "(institutional details withheld for review)",
     "supervisao institucional"),
    (r"PPGSAU/UTFPR", "[institution withheld]", "instituicao no texto"),
]



def remove_comando(texto: str, nome: str) -> tuple[str, int]:
    """Remove \\nome[...]{...} contando chaves, nao por regex.

    Uma expressao regular nao casa argumento com chaves aninhadas em varias
    linhas: `\\affiliation[utfpr]{organization={...}, country={Brazil}}` era
    cortado no primeiro `}` e deixava `, country={Brazil}}` solto no fonte, que
    e o erro "Extra }" que impedia a versao cega de compilar. Contar chaves
    resolve a classe inteira (author, affiliation, ead, cortext).
    """
    saida, i, n = [], 0, 0
    alvo = "\\" + nome
    while True:
        j = texto.find(alvo, i)
        if j < 0:
            saida.append(texto[i:]); break
        k = j + len(alvo)
        if k < len(texto) and texto[k] == "[":            # argumento opcional
            k = texto.find("]", k)
            if k < 0:
                saida.append(texto[i:]); break
            k += 1
        while k < len(texto) and texto[k] in " \n\t":
            k += 1
        if k >= len(texto) or texto[k] != "{":            # nao e o comando que buscamos
            saida.append(texto[i:k or len(texto)]); i = k or len(texto); continue
        nivel, k2 = 0, k
        while k2 < len(texto):
            if texto[k2] == "{":
                nivel += 1
            elif texto[k2] == "}":
                nivel -= 1
                if nivel == 0:
                    k2 += 1; break
            k2 += 1
        saida.append(texto[i:j]); i = k2; n += 1
    return "".join(saida), n


def main() -> None:
    if CEGO.exists():
        shutil.rmtree(CEGO)
    CEGO.mkdir()
    # numbers.tex e as figuras entram porque o corpo cego os usa; sem eles a
    # versao cega nao compila e a checagem vira teatro.
    for item in ("sections", "supplement", "references.bib", "main.tex",
                 "supplement.tex", "numbers.tex"):
        origem = RAIZ / item
        if not origem.exists():
            continue
        destino = CEGO / item
        if origem.is_dir():
            shutil.copytree(origem, destino)
        else:
            shutil.copy2(origem, destino)

    figs = RAIZ.parent / "figures"
    if figs.exists():
        destino = CEGO.parent / "blind_figures"
        if destino.exists():
            shutil.rmtree(destino)
        destino.mkdir()
        for f in sorted(figs.glob("fig*.pdf")):
            shutil.copy2(f, destino / f.name)

    achados = []
    # O .bib ENTRA aqui. A versao anterior so varria *.tex, e a entrada Zenodo do
    # references.bib carregava "Rover, Lucas and Bacalhau ... and Tadano" — se a
    # bibliografia fosse renderizada, a identidade vazava numa submissao cega.
    for tex in sorted(list(CEGO.rglob("*.tex")) + list(CEGO.rglob("*.bib"))):
        s = tex.read_text(encoding="utf-8")
        antes = s
        for nome, rotulo in (("author", "bloco de autor"), ("affiliation", "bloco de afiliacao"),
                             ("ead", "e-mail de contato"), ("cortext", "nota de autor correspondente")):
            s, n = remove_comando(s, nome)
            if n:
                achados.append((tex.name, rotulo, n))
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
    for tex in sorted(f for f in CEGO.rglob("*") if f.is_file()):
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
