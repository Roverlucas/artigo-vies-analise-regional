# Parecer de Validação — Taxonomia T1-T5 + Ground Truth (pilot BRA)

**Quality Gate:** SA-QG-003 (Methodology Rigor) — componente de validação de domínio
**Data:** 2026-06-05
**Validadores (Squad Acadêmico):** sa-public-health (Victora), sa-meteorologist (Nobre), sa-senior-scientist (Ioannidis)
**Orquestração:** sa-advisor (Shneiderman)
**Input auditado:** `data/ap_policy_pilot_bra_v1.jsonl` (10 prompts, 5 tarefas × 2 personas)
**Output:** `data/ap_policy_pilot_bra_v2.jsonl` (corrigido) + este parecer

---

## Veredito

| Dimensão | Resultado |
|---|---|
| **Estrutura da taxonomia (T1-T5)** | ✅ PASS — sólida, mapeada a atividades reais de gestor |
| **Conteúdo do ground truth** | ❌ FAIL → corrigido para CONDITIONAL PASS após v2 |
| **Decisão** | ⚠️ **NEEDS REVISION** — endosso da Yara condicionado a 4 itens pendentes |

2 falhas críticas + 3 concerns em 10 prompts. Estrutura aprovada; conteúdo exigiu correção factual antes de qualquer endosso ou escrita.

---

## Achados por tarefa

### T1 — Norma técnica · 🔴 CRÍTICO (corrigido)
- **Problema:** prompt amarrava a **CONAMA 491/2018**, parcialmente **revogada** pela **CONAMA 506/2024** (5 jul 2024 — revoga arts. 1º-8º e Anexo I). Ground truth afirmava "PI-1 vigente em 2026": **errado**. Em 2026 vigora o **PI-2** (desde 1 jan 2025) sob a 506/2024. Cronograma 506/2024: PI-1 até 31/12/2024 · PI-2 desde 01/01/2025 · PI-3 desde 01/01/2033 · PI-4 desde 01/01/2044 · PF = WHO 2021 (5 µg/m³ anual).
- **Risco metodológico (Ioannidis):** com cutoffs de treino heterogêneos entre os 14 modelos, um LLM atualizado que responda "506/2024 / PI-2" seria penalizado por gabarito obsoleto → **desatualização do ground truth vira confusor de H1 e H6** (co-primárias). Ataque direto à validade interna.
- **Correção v2:** prompt desamarrado da 491; ground truth aponta 506/2024 / PI-2; valor numérico exato do PI-2 anual marcado `NEEDS_HUMAN` (Anexo I).

### T2 — Dado factual local · 🟡 CONCERNS (corrigido)
- Range largo "16-22, ~17 µg/m³" não travado contra a Ficha RQAR 2023 (fonte retornou 403). Referência "approaching CONAMA PI-1 (20)" desatualizada (ver T1).
- **Correção v2:** removida referência ao PI-1; valor único + estação de referência marcados `NEEDS_HUMAN` (tabela oficial CETESB RQAR 2023).

### T3 — Síntese de evidência em saúde · 🔴 CRÍTICO (corrigido)
- **Citações fabricadas no gabarito:** "Sobrinho et al. 2023" e "Andrade et al. 2024" **não existem** (busca não localiza; existe estudo real correlato — *Short-term air pollution exposure and mortality in Brazil*, Environ. Pollut. 2023, PMID 37879554 — mas não desses autores). **Viola o Citation Verification Protocol do próprio projeto** e o princípio No Invention.
- Número ~50.000 mortes/ano (GBD 2019) verificado na ordem de magnitude (~49.660 implícito em cross-check).
- **Correção v2:** citações fabricadas removidas; GBD 2019 mantido com DOI verificável; substituição por refs reais marcada `NEEDS_HUMAN`.

### T4 — Instrumentos de política · 🟢 PASS
- PRONAR (CONAMA 5/1989), PROCONVE (CONAMA 18/1986), PROMOT (CONAMA 297/2002): corretos e verificáveis.
- Nuance: enunciado mistura "monitoramento" (PRONAR) e "controle de fontes móveis" (PROCONVE/PROMOT). Considerar separar no stem ou aceitar conjunto de respostas válidas na rubrica.

### T5 — Recomendação aplicada · 🟡 CONCERNS (corrigido)
- Rubric-based correta para tarefa aberta. Porém "8-15% PM reduction Operação Inverno" é número específico **sem fonte**.
- **Correção v2:** número sem fonte removido; critério mantido qualitativo.

---

## Pendências de validação humana (handoff → Profa. Yara + Dr. Eduardo)

1. **T1** — valor numérico exato do **PI-2 anual MP2,5** conforme Anexo I da CONAMA 506/2024.
2. **T2** — valor único + estação de referência da **Ficha RQAR CETESB 2023**.
3. **T3** — 1-2 estudos brasileiros **verificados** para substituir as citações removidas.
4. **T5** — fonte para magnitude de redução de PM em restrição veicular (ou manter qualitativo).

## Ponto de generalização (antes de escalar BRA → 15 países)
T1 ancora em norma nacional. É necessário um **ground-truth registry por país** com fonte oficial equivalente e igualmente verificável; caso contrário H1 (gap geográfico) fica confundido com disponibilidade de gabarito. **Bloqueia a coleta confirmatória multi-país, não apenas o piloto.**

---

## RETRO (Framework 7 — disparado por citação fabricada)

- **Trigger:** ground truth com citação fabricada (T3) sobreviveu até a fase de validação.
- **Root cause:** prompts piloto gerados sem passar por verificação de citação na origem; o CVP do projeto não estava sendo aplicado na *geração* do ground truth, só seria aplicado no manuscrito.
- **Improvement:** mover o **Citation Verification Protocol para a etapa de geração do ground truth** — toda referência num gabarito deve ter DOI/URL resolvível ANTES de entrar no dataset. Adicionar checagem automatizável (resolver DOI/URL) ao pipeline de prompts.
- **Status:** pendente de implementação no gerador de prompts (`code/`).
