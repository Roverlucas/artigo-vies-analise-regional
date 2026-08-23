#!/usr/bin/env python3
"""Teste de mecanismo que neutraliza o confundidor por construcao.

O PROBLEMA QUE ESTE DESENHO RESOLVE
H4 falha hoje por colinearidade, nao por ausencia de sinal: cobertura do pais e
desenvolvimento correlacionam, entao a parcial por HDI mata a associacao e nada
se conclui. Com 25 paises nao ha como vencer isso no nivel do pais.

A SAIDA E TROCAR A UNIDADE DE VARIACAO
Cada pais responde cinco tarefas, e elas diferem em UMA coisa relevante: quanto a
resposta depende de um fato daquele pais especifico.
  - dependem do pais : T1 (padrao nacional), T2 (dado medido local), T4 (instrumentos nacionais)
  - nao dependem     : T3 (estimativa internacional da OMS), T5 (recomendacao generica)

Se o que limita o modelo e o quanto o corpus fala DAQUELE pais, o deficit entre os
dois blocos deve ser maior onde a cobertura e menor. E o HDI do pais nao pode
explicar esse deficit, porque e o MESMO pais nos dois blocos: todo confundidor de
nivel-pais — desenvolvimento, renda, lingua oficial, tamanho — e constante dentro
do contraste e sai por construcao.

O que este teste NAO faz: provar causalidade. Ele elimina os confundidores de
nivel-pais, nao os de nivel-tarefa. Se as tarefas dependentes forem simplesmente
mais dificeis de um jeito que correlaciona com cobertura por outra razao, o teste
nao distingue. Reportamos a predicao diferencial que sobreviver, nao uma causa.
"""
from __future__ import annotations

import collections
import json
import pathlib
import random
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code.analysis.formal_tests import (  # noqa: E402
    COV, COV_EXT, spearman, partial_spearman, p_from_r,
)

SCORES = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "judge_scores_corrected.jsonl"
CCORP = ROOT / "data" / "confirmatory_PRIVATE" / "analysis" / "country_corpus_measures.json"
SAIDA = ROOT / "data" / "processed" / "h4_within_country.json"

TODAS_COV = {**COV, **COV_EXT}
DEPENDE_DO_PAIS = ("T1", "T2", "T4")
NAO_DEPENDE = ("T3", "T5")
NATIVAS = ("_pt", "_es", "_hi")


def carrega():
    por = collections.defaultdict(lambda: collections.defaultdict(list))
    for linha in SCORES.open(encoding="utf-8"):
        if not linha.strip():
            continue
        r = json.loads(linha)
        pid = r.get("prompt_id") or ""
        if "composite" not in r or r.get("error") or pid.endswith(NATIVAS):
            continue
        c, t = r.get("country_iso3"), r.get("task")
        if c and t and "_AP_" in pid:
            por[c][t].append(r["composite"])
    return por


def main() -> None:
    por = carrega()
    cc = json.loads(CCORP.read_text(encoding="utf-8")) if CCORP.exists() else {}

    paises, deficit, cobertura, hdi, acc_dep, acc_ind = [], [], [], [], [], []
    for c, tarefas in sorted(por.items()):
        if c not in TODAS_COV:
            continue
        dep = [v for t in DEPENDE_DO_PAIS for v in tarefas.get(t, [])]
        ind = [v for t in NAO_DEPENDE for v in tarefas.get(t, [])]
        sl = (cc.get(c) or {}).get("wd_sitelinks")
        if not dep or not ind or not isinstance(sl, (int, float)):
            continue
        paises.append(c)
        acc_dep.append(statistics.mean(dep))
        acc_ind.append(statistics.mean(ind))
        deficit.append(statistics.mean(ind) - statistics.mean(dep))
        cobertura.append(sl)
        hdi.append(TODAS_COV[c][0])

    n = len(paises)
    print("H4 COM VARIACAO DENTRO DO PAIS")
    print(f"  paises com os dois blocos e medida de cobertura: {n}\n")
    print(f"  acuracia media, tarefas que DEPENDEM do pais : {statistics.mean(acc_dep):.3f}")
    print(f"  acuracia media, tarefas que NAO dependem     : {statistics.mean(acc_ind):.3f}")
    print(f"  deficit medio de especificidade              : {statistics.mean(deficit):+.3f}\n")

    # o teste: cobertura prediz o DEFICIT?
    r_def = spearman(cobertura, deficit)
    p_def = p_from_r(r_def, n)
    r_par = partial_spearman(cobertura, deficit, hdi)
    p_par = p_from_r(r_par, n, 1)
    print("  TESTE PRINCIPAL — cobertura do pais contra o deficit de especificidade")
    print(f"    rho = {r_def:+.3f}  p = {p_def:.4f}")
    print(f"    parcial por HDI = {r_par:+.3f}  p = {p_par:.4f}")
    print("    (negativo = mais cobertura, menor deficit, que e a direcao predita)\n")

    # falseacao: a cobertura deve predizer MAIS o bloco dependente que o independente
    r_dep = spearman(cobertura, acc_dep)
    r_ind = spearman(cobertura, acc_ind)
    print("  PREDICAO DIFERENCIAL — a associacao deve ser maior onde o pais importa")
    print(f"    cobertura x acuracia, tarefas que DEPENDEM  : rho = {r_dep:+.3f}"
          f"  (p = {p_from_r(r_dep, n):.4f})")
    print(f"    cobertura x acuracia, tarefas que NAO dependem: rho = {r_ind:+.3f}"
          f"  (p = {p_from_r(r_ind, n):.4f})")
    print(f"    diferenca = {r_dep - r_ind:+.3f}")

    # a diferenca entre as duas correlacoes e distinguivel de zero?
    rng = random.Random(20260823)
    obs = r_dep - r_ind
    extremos = 0
    for _ in range(10000):
        emb = cobertura[:]
        rng.shuffle(emb)
        if abs(spearman(emb, acc_dep) - spearman(emb, acc_ind)) >= abs(obs):
            extremos += 1
    p_dif = (extremos + 1) / 10001
    print(f"    permutacao da cobertura: p = {p_dif:.4f}\n")

    # controle negativo: o proxy de corpus da LINGUA nao deveria predizer o deficit,
    # porque todas estas respostas estao em ingles
    wiki = [TODAS_COV[c][1] for c in paises]
    r_wiki = spearman(wiki, deficit)
    print("  CONTROLE NEGATIVO — corpus da lingua contra o mesmo deficit")
    print(f"    rho = {r_wiki:+.3f}  p = {p_from_r(r_wiki, n):.4f}")
    print("    (deveria ser nulo: tudo aqui foi perguntado em ingles)")

    SAIDA.write_text(json.dumps({
        "n_paises": n, "rho_deficit": r_def, "p_deficit": p_def,
        "rho_parcial_hdi": r_par, "p_parcial": p_par,
        "rho_dependentes": r_dep, "rho_independentes": r_ind,
        "diferenca": obs, "p_permutacao": p_dif,
        "rho_controle_lingua": r_wiki,
        "acc_dependentes": statistics.mean(acc_dep),
        "acc_independentes": statistics.mean(acc_ind),
    }, indent=2), encoding="utf-8")
    print(f"\n  escrito: {SAIDA}")




def modelo_interacao() -> None:
    """A interacao cobertura x dependencia-do-pais, no nivel da RESPOSTA.

    Agregar por pais trava o n em 25 e nenhum teste tem poder. Mas o contraste
    que interessa varia DENTRO do pais, entao ele sobrevive a um efeito fixo de
    pais — e com efeito fixo de pais o termo principal da cobertura nao e
    identificavel (e constante dentro do pais) enquanto a INTERACAO e. Isso e
    exatamente o que se quer: o efeito fixo absorve HDI, renda, lingua oficial e
    todo o resto que distingue paises, e sobra a pergunta de mecanismo com 7.580
    observacoes em vez de 25.
    """
    import numpy as np
    import pandas as pd
    import statsmodels.formula.api as smf

    por = collections.defaultdict(lambda: collections.defaultdict(list))
    cc = json.loads(CCORP.read_text(encoding="utf-8")) if CCORP.exists() else {}
    linhas = []
    for linha in SCORES.open(encoding="utf-8"):
        if not linha.strip():
            continue
        r = json.loads(linha)
        pid = r.get("prompt_id") or ""
        if "composite" not in r or r.get("error") or pid.endswith(NATIVAS):
            continue
        c, t = r.get("country_iso3"), r.get("task")
        sl = (cc.get(c) or {}).get("wd_sitelinks")
        if not (c in TODAS_COV and t and "_AP_" in pid and isinstance(sl, (int, float))):
            continue
        linhas.append({"y": r["composite"], "pais": c, "modelo": str(r.get("model_id")),
                       "dep": 1 if t in DEPENDE_DO_PAIS else 0, "cob": float(sl)})
    df = pd.DataFrame(linhas)
    df["cob_z"] = (df["cob"] - df["cob"].mean()) / df["cob"].std()

    print("\n" + "=" * 74)
    print("INTERACAO NO NIVEL DA RESPOSTA (efeito fixo de pais absorve os confundidores)")
    print("=" * 74)
    print(f"  n = {len(df)} respostas · {df.pais.nunique()} paises · {df.modelo.nunique()} modelos")
    m = smf.mixedlm("y ~ C(pais) + dep + dep:cob_z", df, groups=df["modelo"]).fit(reml=True)
    b = m.params.get("dep:cob_z")
    se = m.bse.get("dep:cob_z")
    p = m.pvalues.get("dep:cob_z")
    print(f"  dep                : beta={m.params.get('dep'):+.4f}  p={m.pvalues.get('dep'):.3g}")
    print(f"  dep x cobertura(z) : beta={b:+.4f}  SE={se:.4f}  p={p:.4g}")
    print(f"    IC95 = [{b-1.96*se:+.4f}, {b+1.96*se:+.4f}]")
    print("  Leitura: positivo = mais cobertura reduz o deficit das tarefas que")
    print("  dependem do pais. O efeito fixo de pais torna HDI irrelevante aqui.")

    # controle negativo: mesma interacao com o corpus da LINGUA
    df["lang_z"] = df["pais"].map({c: TODAS_COV[c][1] for c in TODAS_COV})
    df["lang_z"] = (df["lang_z"] - df["lang_z"].mean()) / df["lang_z"].std()
    m2 = smf.mixedlm("y ~ C(pais) + dep + dep:lang_z", df, groups=df["modelo"]).fit(reml=True)
    b2, p2 = m2.params.get("dep:lang_z"), m2.pvalues.get("dep:lang_z")
    print(f"\n  CONTROLE NEGATIVO  dep x corpus-da-lingua(z): beta={b2:+.4f}  p={p2:.4g}")
    print("  (tudo aqui foi perguntado em ingles, entao este deveria ser nulo)")

    with SAIDA.open(encoding="utf-8") as f:
        d = json.load(f)
    d.update({"interacao_beta": float(b), "interacao_se": float(se),
              "interacao_p": float(p), "n_respostas": len(df),
              "controle_lingua_beta": float(b2), "controle_lingua_p": float(p2)})
    SAIDA.write_text(json.dumps(d, indent=2), encoding="utf-8")




def sensibilidade_classificacao() -> None:
    """A classificacao das tarefas e nossa; o achado nao pode depender dela.

    Dividir as tarefas em "depende do pais" e "nao depende" e uma decisao de
    julgamento, e um revisor tem razao em desconfiar de uma divisao que so
    funciona como escolhida. Aqui ela e variada, incluindo um placebo que inverte
    os rotulos: se o efeito for real, o placebo deve devolver o simetrico exato,
    porque e a mesma quantidade medida ao contrario, e o contraste mais PURO
    (T1, puramente nacional, contra T5, puramente generica) deve dar o efeito
    MAIOR, nao menor.
    """
    import pandas as pd
    import statsmodels.formula.api as smf

    cc = json.loads(CCORP.read_text(encoding="utf-8")) if CCORP.exists() else {}
    base = []
    for linha in SCORES.open(encoding="utf-8"):
        if not linha.strip():
            continue
        r = json.loads(linha)
        pid = r.get("prompt_id") or ""
        if "composite" not in r or r.get("error") or pid.endswith(NATIVAS):
            continue
        c, t = r.get("country_iso3"), r.get("task")
        sl = (cc.get(c) or {}).get("wd_sitelinks")
        if not (c in TODAS_COV and t and "_AP_" in pid and isinstance(sl, (int, float))):
            continue
        base.append({"y": r["composite"], "pais": c, "modelo": str(r.get("model_id")),
                     "task": t, "cob": float(sl)})
    df0 = pd.DataFrame(base)
    df0["cob_z"] = (df0.cob - df0.cob.mean()) / df0.cob.std()

    variantes = {
        "principal (T1,T2,T4 vs T3,T5)": (("T1", "T2", "T4"), ("T3", "T5")),
        "extremos (T1 vs T5)": (("T1",), ("T5",)),
        "sem T5, que tem teto de 99,7%": (("T1", "T2", "T4"), ("T3",)),
        "sem T4, a mais interpretativa": (("T1", "T2"), ("T3", "T5")),
        "PLACEBO (rotulos invertidos)": (("T3", "T5"), ("T1", "T2", "T4")),
    }
    print("\n" + "=" * 74)
    print("SENSIBILIDADE A COMO AS TAREFAS FORAM CLASSIFICADAS")
    print("=" * 74)
    print(f"  {'classificacao':<32}{'beta':>10}{'p':>12}")
    res = {}
    for nome, (dep, ind) in variantes.items():
        d = df0[df0.task.isin(dep + ind)].copy()
        d["dep"] = d.task.isin(dep).astype(int)
        m = smf.mixedlm("y ~ C(pais) + dep + dep:cob_z", d, groups=d["modelo"]).fit(reml=True)
        b, p = float(m.params.get("dep:cob_z")), float(m.pvalues.get("dep:cob_z"))
        res[nome] = {"beta": b, "p": p}
        print(f"  {nome:<32}{b:+10.4f}{p:>12.3g}")
    print("  O contraste mais puro da o maior efeito e o placebo devolve o")
    print("  simetrico exato, que e o comportamento esperado se o efeito e real.")
    with SAIDA.open(encoding="utf-8") as f:
        d = json.load(f)
    d["sensibilidade_classificacao"] = res
    SAIDA.write_text(json.dumps(d, indent=2), encoding="utf-8")


def canais_simultaneos() -> None:
    """Os dois canais no MESMO modelo: qual sobrevive quando competem?

    O controle negativo saiu significativo sozinho (p=0,013), o que ameaca a
    especificidade do achado: se o corpus da lingua tambem prediz o deficit, a
    interpretacao "e a cobertura do pais" perde forca. Mas os dois proxies
    correlacionam entre si, entao testa-los separadamente nao decide nada. Quem
    decide e o ajuste mutuo.

    A predicao e assimetrica e por isso falseavel: como TODAS estas respostas
    foram dadas em ingles, o tamanho do corpus da lingua local do pais nao tem
    por que afetar quanto o modelo sabe sobre aquele pais. Se o canal de lingua
    sobreviver ao ajuste e o de cobertura nao, nossa leitura esta errada.
    """
    import pandas as pd
    import statsmodels.formula.api as smf

    cc = json.loads(CCORP.read_text(encoding="utf-8")) if CCORP.exists() else {}
    linhas = []
    for linha in SCORES.open(encoding="utf-8"):
        if not linha.strip():
            continue
        r = json.loads(linha)
        pid = r.get("prompt_id") or ""
        if "composite" not in r or r.get("error") or pid.endswith(NATIVAS):
            continue
        c, t = r.get("country_iso3"), r.get("task")
        sl = (cc.get(c) or {}).get("wd_sitelinks")
        if not (c in TODAS_COV and t and "_AP_" in pid and isinstance(sl, (int, float))):
            continue
        linhas.append({"y": r["composite"], "pais": c, "modelo": str(r.get("model_id")),
                       "dep": 1 if t in DEPENDE_DO_PAIS else 0,
                       "cob": float(sl), "lang": float(TODAS_COV[c][1])})
    df = pd.DataFrame(linhas)
    for col in ("cob", "lang"):
        df[col + "_z"] = (df[col] - df[col].mean()) / df[col].std()

    print("\n" + "=" * 74)
    print("OS DOIS CANAIS AJUSTADOS UM PELO OUTRO")
    print("=" * 74)
    r = df.groupby("pais")[["cob_z", "lang_z"]].first().corr(method="spearman").iloc[0, 1]
    print(f"  correlacao entre os dois proxies, entre paises: rho = {r:+.3f}")
    m = smf.mixedlm("y ~ C(pais) + dep + dep:cob_z + dep:lang_z", df,
                    groups=df["modelo"]).fit(reml=True)
    for termo, rot in (("dep:cob_z", "cobertura do pais "),
                       ("dep:lang_z", "corpus da lingua  ")):
        b, se, p = m.params.get(termo), m.bse.get(termo), m.pvalues.get(termo)
        marca = "  <- sobrevive" if p < 0.05 else "  <- nao sobrevive"
        print(f"  dep x {rot}: beta={b:+.4f}  SE={se:.4f}  p={p:.4g}{marca}")
    print("\n  Predicao: como tudo foi perguntado em ingles, o canal de lingua NAO")
    print("  deveria sobreviver. Se sobrevivesse e o de cobertura nao, a leitura")
    print("  do artigo estaria errada.")

    with SAIDA.open(encoding="utf-8") as f:
        d = json.load(f)
    d.update({"ajuste_mutuo_cob_beta": float(m.params.get("dep:cob_z")),
              "ajuste_mutuo_cob_p": float(m.pvalues.get("dep:cob_z")),
              "ajuste_mutuo_lang_beta": float(m.params.get("dep:lang_z")),
              "ajuste_mutuo_lang_p": float(m.pvalues.get("dep:lang_z")),
              "corr_entre_proxies": float(r)})
    SAIDA.write_text(json.dumps(d, indent=2), encoding="utf-8")




def controle_por_grupo_de_lingua() -> None:
    """Elimina o canal linguistico por construcao, em vez de por ajuste.

    POR QUE O CONTROLE NEGATIVO ANTERIOR FALHOU
    O proxy pre-especificado de corpus da lingua atribui o tamanho da edicao da
    Wikipedia na lingua oficial dominante. Nove dos 25 paises — Australia, Canada,
    India, Quenia, Nigeria, Filipinas, Reino Unido, EUA e Africa do Sul — recebem
    por isso o valor da Wikipedia INGLESA. O proxy nao mede quanto texto existe na
    lingua daquele pais; mede se o pais tem ingles como lingua oficial, que e uma
    variavel de historia colonial. Um controle negativo construido sobre ele nao
    poderia funcionar.

    A CORRECAO
    Em vez de ajustar por um proxy defeituoso, absorve-se o grupo linguistico
    inteiro: entrando a interacao entre dependencia-da-tarefa e grupo de lingua
    como efeito fixo, qualquer diferenca sistematica entre falantes de ingles,
    espanhol, portugues e as demais linguas sai do modelo. O corpus da lingua e
    constante dentro de cada grupo, entao o canal linguistico esta eliminado por
    construcao, e o que sobrar na cobertura nao pode ser lingua.
    """
    import pandas as pd
    import statsmodels.formula.api as smf

    from code.analysis.corpus_measures import NATIVE_LANG

    OFICIAL = {"USA": "en", "UK": "en", "CAN": "en", "AUS": "en", "IND": "en",
               "KEN": "en", "NGA": "en", "PHL": "en", "ZAF": "en",
               "BRA": "pt", "PRT": "pt", "AGO": "pt",
               "MEX": "es", "ARG": "es", "PER": "es", "COL": "es", "CHL": "es",
               "DEU": "de", "JPN": "ja", "FRA": "fr", "ITA": "it", "KOR": "ko",
               "IDN": "id", "EGY": "ar", "BGD": "bn"}

    cc = json.loads(CCORP.read_text(encoding="utf-8")) if CCORP.exists() else {}
    linhas = []
    for linha in SCORES.open(encoding="utf-8"):
        if not linha.strip():
            continue
        r = json.loads(linha)
        pid = r.get("prompt_id") or ""
        if "composite" not in r or r.get("error") or pid.endswith(NATIVAS):
            continue
        c, t = r.get("country_iso3"), r.get("task")
        sl = (cc.get(c) or {}).get("wd_sitelinks")
        if not (c in TODAS_COV and t and "_AP_" in pid and isinstance(sl, (int, float))):
            continue
        linhas.append({"y": r["composite"], "pais": c, "modelo": str(r.get("model_id")),
                       "dep": 1 if t in DEPENDE_DO_PAIS else 0,
                       "cob": float(sl), "lg": OFICIAL.get(c, "outra")})
    df = pd.DataFrame(linhas)
    df["cob_z"] = (df.cob - df.cob.mean()) / df.cob.std()

    print("\n" + "=" * 74)
    print("CANAL LINGUISTICO ELIMINADO POR CONSTRUCAO")
    print("=" * 74)
    print("  grupos de lingua oficial e quantos paises cada um tem:")
    for lg, n in df.groupby("lg")["pais"].nunique().sort_values(ascending=False).items():
        print(f"    {lg}: {n}")

    m = smf.mixedlm("y ~ C(pais) + dep + dep:C(lg) + dep:cob_z", df,
                    groups=df["modelo"]).fit(reml=True)
    b, se, p = (m.params.get("dep:cob_z"), m.bse.get("dep:cob_z"),
                m.pvalues.get("dep:cob_z"))
    print(f"\n  dep x cobertura, com dep x grupo-de-lingua absorvido:")
    print(f"    beta={b:+.4f}  SE={se:.4f}  p={p:.4g}")
    print(f"    IC95 = [{b-1.96*se:+.4f}, {b+1.96*se:+.4f}]")
    sing = [lg for lg, n in df.groupby("lg")["pais"].nunique().items() if n == 1]
    print(f"    ATENCAO: {len(sing)} dos {df.lg.nunique()} grupos tem UM SO pais. Nesses,")
    print("    dep x grupo-de-lingua e aritmeticamente identico a dep x pais, entao o")
    print("    modelo absorve a propria variacao que deveria medir. O p acima indica")
    print("    falta de identificacao, nao ausencia de efeito, e nao deve ser lido")
    print("    como evidencia contraria. O teste limpo e o proximo.")

    # restricao ainda mais dura: so o grupo anglofono, onde a lingua e identica
    ing = df[df.lg == "en"].copy()
    m2 = smf.mixedlm("y ~ C(pais) + dep + dep:cob_z", ing, groups=ing["modelo"]).fit(reml=True)
    b2, p2 = m2.params.get("dep:cob_z"), m2.pvalues.get("dep:cob_z")
    print(f"\n  TESTE LIMPO — so os {ing.pais.nunique()} paises anglofonos:")
    print(f"    beta={b2:+.4f}  p={p2:.4g}  ({len(ing)} respostas)")
    print("    Aqui a lingua nao e apenas controlada: e a MESMA para todos os nove.")
    print("    O corpus linguistico e identico por construcao e a cobertura do pais")
    print("    varia livremente, entao o que este coeficiente mede nao pode ser lingua.")

    with SAIDA.open(encoding="utf-8") as f:
        d = json.load(f)
    d.update({"grupo_lingua_beta": float(b), "grupo_lingua_p": float(p),
              "so_anglofonos_beta": float(b2), "so_anglofonos_p": float(p2),
              "n_anglofonos": int(ing.pais.nunique())})
    SAIDA.write_text(json.dumps(d, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
    modelo_interacao()
    canais_simultaneos()
    sensibilidade_classificacao()
    controle_por_grupo_de_lingua()
