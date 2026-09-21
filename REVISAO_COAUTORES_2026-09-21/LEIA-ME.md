# Pacote para revisão dos coautores — 21/09/2026

**Artigo:** *Whose Regulation Does the Model Know? Reliability of LLM-Retrieved Regulatory Information for Public Environmental Management in 25 Countries*
**Autores (ordem de assinatura):** Lucas Rover (UTFPR) · Vitor de Melo Dominski (Descomplica) · Anibal Tavares de Azevedo (Unicamp) · Eduardo Tadeu Bacalhau (UFPR) · Yara de Souza Tadano (UTFPR)
**Alvo:** *Government Information Quarterly* (Elsevier)
**Repositório (público):** https://github.com/Roverlucas/artigo-vies-analise-regional (commit `f08ff3d`)

## Arquivos

| arquivo | conteúdo | pp |
|---|---|---|
| `...MANUSCRITO-EN` | manuscrito completo, inglês (idioma de submissão) — formato `elsarticle [review]`, espaçamento duplo | 59 |
| `...SUPLEMENTAR-EN` | material suplementar, inglês | 17 |
| `...MANUSCRITO-PT` | versão de leitura em português | 31 |
| `...SUPLEMENTAR-PT` | suplemento em português | 16 |

A versão em inglês é a autoritativa. As 59 páginas são efeito do espaçamento duplo exigido na submissão; em formato `preprint` o mesmo texto ocupa 42.

## O que o artigo afirma (todos os números saem de `data/processed/freeze_all_effects.json`, reproduzível com `python code/run_all.py --confirmatory`)

- **Achado principal (H2):** perguntar na língua do país **piora** a acurácia em **−4,75 pp** (Wilcoxon p = 3×10⁻¹⁵, n = 839 pares). Hindi −11,1 pp, espanhol −4,4, português −3,9. Resiste a leave-one-out de país e de modelo, trimming e reponderação do composto.
- **Lacuna Norte/Sul (H1):** +5,4 pp (permutação p = 0,020) sob a partição developing/developed da UNCTAD. O gradiente com IDH (ρ = 0,41, p = 0,043) fica **abaixo do critério pré-fixado (ρ ≥ 0,55)** e é reportado como exploratório.
- **Modelo regional (H3):** o modelo brasileiro é o pior dos 14 (δ = −0,47).
- **Persona de gestor local (H6):** não ajuda (+0,83 pp, p = 0,27).
- **Aberto vs. fechado (H5):** +12,6 pp a favor dos fechados.
- **Piso de recuperação factual:** onde a resposta é um valor publicado (padrão de PM2,5, dado local) a acurácia cai a 0,37 contra 0,61 em síntese.

## A virada metodológica que define o artigo

Os gabaritos de T2/T3 eram placeholders e a comparação "o valor está na faixa?" era feita por LLM. Reconstruir as chaves a partir dos registros oficiais (WHO AAQD, WHO GHO, UNEP GAAPL) e mover a comparação para código **mudou as conclusões** (gradiente ρ 0,51 → 0,41; penalidade nativa −2,1 → −4,75 pp). Por isso H2 é o achado principal e H1 é exploratório. O manuscrito relata isso explicitamente.

## Transparência

- **Não há pré-registro depositado.** O plano foi fixado antes da coleta (rastro versionado em `preregistration/`), mas nunca depositado. O texto se reporta como exploratório e não reivindica pré-registro.
- **Validação humana do gabarito:** não há camada human-gold; o gabarito é fonte oficial primária + painel de 3 fornecedores de juízes-LLM. Declarado como limitação.
- **Uso de IA:** juízes-LLM produzem os escores; tradução dos prompts por LLM; Claude Code e Codex CLI usados no código e na revisão. Tudo declarado.
- **Referências:** 44 citadas, 36 lidas na íntegra, 7 conferidas em abstract, 1 livro sem localizador.

## O que pedimos a cada coautor

1. Ler o manuscrito em inglês (ou a versão PT) e anotar diretamente no PDF ou por e-mail.
2. Confirmar afiliação, ORCID e **e-mail institucional** (Dominski e Azevedo: ainda não temos).
3. Dizer se concorda com a força da claim principal (H2) e com o enquadramento exploratório de H1.
4. Sinalizar qualquer outra ferramenta de IA usada, para a declaração exigida pela Elsevier.

Sem a aprovação explícita dos cinco, não submetemos.
