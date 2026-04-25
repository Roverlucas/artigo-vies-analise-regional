# Email Template — Aprovação de Pivot Estratégico para Profa. Yara

**Status:** Rascunho para Lucas enviar
**Idioma:** português acadêmico formal
**Comprimento alvo:** ~350 palavras
**Anexos sugeridos:** `pilot_findings_v2.md`, `proposta_consolidada_v3.md` (v3.4)

---

**Assunto:** Pedido de aprovação — pivot estratégico no artigo de viés em LLMs (pré-registro OSF)

---

Profa. Yara,

Espero que esteja bem. Escrevo para pedir sua aprovação de um **pivot estratégico** no projeto do artigo sobre viés em LLMs antes do depósito do pré-registro no OSF.

## Contexto

Como combinamos, executei um estudo piloto exploratório (n=700, 5 modelos × 7 países × 10 prompts × 2 réplicas, scored via LLM-as-judge com Claude Haiku 4.5). Os resultados estão no anexo `pilot_findings_v2.md`. Dois achados motivam o pivot:

1. **H1 confirmada na direção esperada**, mas com tamanho de efeito menor (Cohen's *d* = +0,34 vs +0,50 hipotetizado). Gap GN-GS = 6 pontos percentuais.

2. **Achado inesperado em H5:** modelos open-weight (Llama 4 Scout 17B, Command R+ 104B) **subperformam** modelos closed accessible (Haiku 4.5, GPT-5-mini, Gemini Flash) em **12,5 pontos percentuais** — efeito 2× maior que H1, na direção oposta ao que originalmente hipotetizei.

## Proposta de pivot

Elevar **H5 de secundária para co-primária com H1**, reposicionando o paper para focar no "open-weight penalty" como contribuição principal. Esse achado, se sustentado em escala 70B+ no confirmatório, é completamente inédito na literatura Q1 e tem implicação direta para política de soberania de IA no Sul Global.

**Novo título proposto:** *"The Open-Weight Penalty: Frontier Open Models Underperform Closed-Accessible Models by 12pp in Global South Applied Research — A 15-Country Audit With Mechanism Analysis"*

A probabilidade de aceite em *Patterns* sobe estimadamente de 32-40% (v3.3 com H1 puro) para 38-50% (v3.4 com H5 elevada).

## Pedido específico

Preciso de sua **aprovação por email** desta versão revisada antes de depositar o pré-registro no OSF (proteção contra HARKing). A versão completa está no documento anexo `proposta_consolidada_v3.md` (v3.4) e o SAP recalibrado em `sap_v2_pilot_recalibrated.md`.

Posso agendar **15 minutos** essa semana para discutir, ou se preferir um simples "*aprovado conforme proposto*" por email já basta para eu prosseguir.

Cronograma se aprovado:
- D+1: depósito OSF
- D+2 a D+14: execução confirmatória (10.500 calls)
- D+15 a D+22: redação + auditoria
- D+23 a D+25: submissão *Patterns*

Agradeço o feedback.

Abraços,
Lucas

---

**Notas para Lucas:**
- Anexar `pilot_findings_v2.md` e `proposta_consolidada_v3.md`
- Se Yara responder com edits, atualizar OSF draft antes de depositar
- Se aprovação demorar > 3 dias úteis, considerar reunião curta para destravar
