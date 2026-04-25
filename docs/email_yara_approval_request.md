# Email Template — Aprovação de Pivot Estratégico + Inclusão do Coorientador

**Status:** Rascunho para Lucas enviar
**Para:** Profa. Dra. Yara Tadano (orientadora)
**Cc:** Prof. Dr. Eduardo Tadeu Bacalhau (coorientador)
**Idioma:** português acadêmico formal
**Comprimento alvo:** ~400 palavras
**Anexos sugeridos:** `pilot_findings_v2.md`, `proposta_consolidada_v3.md` (v3.4), `sap_v2_pilot_recalibrated.md`

---

**Assunto:** Pedido de aprovação — pivot estratégico no artigo de viés em LLMs (pré-registro OSF) + inclusão do Prof. Dr. Eduardo Tadeu Bacalhau como coorientador

**Para:** Profa. Dra. Yara Tadano
**Cc:** Prof. Dr. Eduardo Tadeu Bacalhau

---

Profa. Yara, Prof. Eduardo,

Espero que estejam bem. Escrevo para pedir aprovação de um **pivot estratégico** no projeto do artigo sobre viés em LLMs antes do depósito do pré-registro no OSF, e para formalizar a **inclusão do Prof. Eduardo como coorientador** do projeto.

## Contexto

Como combinamos, executei um estudo piloto exploratório (n=700, 5 modelos × 7 países × 10 prompts × 2 réplicas, scored via LLM-as-judge com Claude Haiku 4.5). Os resultados estão no anexo `pilot_findings_v2.md`. Dois achados motivam o pivot:

1. **H1 confirmada na direção esperada**, mas com tamanho de efeito menor (Cohen's *d* = +0,34 vs +0,50 hipotetizado). Gap GN-GS = 6 pontos percentuais.

2. **Achado inesperado em H5:** modelos open-weight (Llama 4 Scout 17B, Command R+ 104B) **subperformam** modelos closed accessible (Haiku 4.5, GPT-5-mini, Gemini Flash) em **12,5 pontos percentuais** — efeito 2× maior que H1, na direção oposta ao que originalmente hipotetizei.

## Proposta de pivot

Elevar **H5 de secundária para co-primária com H1**, reposicionando o paper para focar no "open-weight penalty" como contribuição principal. Esse achado, se sustentado em escala 70B+ no confirmatório, é completamente inédito na literatura Q1 e tem implicação direta para política de soberania de IA no Sul Global.

**Novo título proposto:** *"The Open-Weight Penalty: Frontier Open Models Underperform Closed-Accessible Models by 12pp in Global South Applied Research — A 15-Country Audit With Mechanism Analysis"*

A probabilidade de aceite em *Patterns* sobe estimadamente de 32-40% (v3.3 com H1 puro) para 38-50% (v3.4 com H5 elevada).

## Coautoria — Prof. Eduardo

Como combinamos, formalizo nesta mensagem a inclusão do **Prof. Dr. Eduardo Tadeu Bacalhau como coautor** do artigo, junto com a Profa. Yara. Ambos compartilharão os papéis CRediT de **validação metodológica, supervisão, revisão de resultados e revisão da escrita**. A ordem de assinatura no manuscrito será:

1. Lucas Rover (primeiro autor, autor correspondente)
2. Prof. Dr. Eduardo Tadeu Bacalhau (autor intermediário)
3. Profa. Dra. Yara Tadano (autora sênior)

Caso ambos concordem com o pivot estratégico abaixo, peço a confirmação por esta resposta de email — isso autoriza o depósito do pré-registro no OSF com os três como co-registrants.

## Pedido específico

Preciso de **aprovação por email da Profa. Yara e do Prof. Eduardo** desta versão revisada antes de depositar o pré-registro no OSF (proteção contra HARKing). A versão completa está no documento anexo `proposta_consolidada_v3.md` (v3.4) e o SAP recalibrado em `sap_v2_pilot_recalibrated.md`.

Posso agendar **15 minutos** essa semana para discutir, ou se preferirem um simples "*aprovado conforme proposto*" por email já basta para eu prosseguir.

Cronograma se aprovado:
- D+1: depósito OSF (com os três como co-registrants)
- D+2 a D+14: execução confirmatória (10.500 calls)
- D+15 a D+22: redação + auditoria
- D+23 a D+25: submissão *Patterns*

Agradeço o feedback de ambos.

Abraços,
Lucas Rover

---

**Notas para Lucas (não enviar):**
- Anexar `pilot_findings_v2.md` e `proposta_consolidada_v3.md`
- Cc: Prof. Eduardo Tadeu Bacalhau (confirmar email institucional dele)
- Se Yara/Eduardo responderem com edits, atualizar OSF draft antes de depositar
- Se aprovação demorar > 3 dias úteis, considerar reunião curta para destravar
- No depósito OSF, adicionar Yara e Eduardo como co-contributors com permissão "Read+Write"
