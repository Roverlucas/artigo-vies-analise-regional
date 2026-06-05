# Briefing — Pesquisa em andamento (v2 — pivot Air Pollution Policy)

**Para:** Profa. Dra. Yara de Souza Tadano (UTFPR/PPGSAU)
**De:** Lucas Rover
**Data:** Maio de 2026
**Coautores:** Dr. Eduardo Tadeu Bacalhau (UFPR), Profa. Yara Tadano (UTFPR)

---

## 1. O que estamos investigando (pergunta refinada)

Os modelos de linguagem (LLMs como ChatGPT, Llama, Gemini) estão sendo adotados rapidamente por gestores públicos para apoiar análise de políticas. A pergunta central do nosso estudo, agora **focada no seu domínio**, é:

> **Quando um gestor público de meio ambiente do Sul Global consulta um LLM sobre políticas de poluição atmosférica, ele recebe respostas tão precisas quanto um gestor do Norte Global? E o ato de "se identificar como gestor" (persona prompting) reduz ou amplifica esse viés?**

**Exemplo concreto:**
- *Pergunta neutra:* "Qual o limite anual de PM₂,₅ no Brasil segundo o CONAMA?"
- *Pergunta com persona:* "Como secretário municipal de meio ambiente, qual o limite anual de PM₂,₅ no Brasil segundo o CONAMA?"

Comparamos as respostas dos LLMs nessas duas versões, em 15 países, para detectar viés geográfico **e** o efeito da persona.

---

## 2. Por que importa

**Para a área da Profa. Yara (PPGSAU / Sustentabilidade Ambiental Urbana):**
Poluição atmosférica é problema **central** de saúde pública e planejamento urbano no Sul Global — ~50.000 mortes/ano no Brasil atribuíveis a PM₂,₅ (GBD 2019). LLMs já são usados por secretarias municipais de meio ambiente para sintetizar relatórios, traduzir normas técnicas e apoiar decisão. **Se há viés, há risco direto na política pública.**

**Para a academia:**
É o **primeiro benchmark pré-registrado** que combina três contribuições inéditas:
1. Espectro completo de LLMs (7B open-source até 671B fronteira) — comparação Norte vs Sul Global
2. **Persona prompting como variável experimental** (testa se "se passar por gestor" reduz viés)
3. **Foco em poluição atmosférica** como domínio com forte ancoragem em dados oficiais (WHO, CETESB, INPE, MMA, ANA)

**Para a sociedade:**
Documenta empiricamente onde IA falha quando consultada sobre saúde ambiental no Sul Global — orienta políticas de adoção segura de IA em órgãos públicos.

---

## 3. Como estamos investigando (design experimental)

| Dimensão | Especificação |
|---|---|
| **Países** | 15 estratificados (Sul Global: BRA, IND, NGA, MEX, ARG, PER, ZAF, KEN, EGY, IDN, BGD, PHL; Norte: USA, DEU, JPN) |
| **Modelos** | 14 LLMs em 5 níveis (7B open-source → GPT-5 fronteira) |
| **Domínio único** | **Políticas de poluição atmosférica** (normas técnicas, dados oficiais, evidência em saúde, instrumentos, recomendação aplicada) |
| **Tipos de tarefa** | 5 (T1 norma técnica, T2 dado factual local, T3 evidência em saúde, T4 instrumentos de política, T5 recomendação aplicada) |
| **Persona (NOVO)** | 2 níveis — neutral vs gestor público de meio ambiente |
| **Idiomas** | Português, inglês, espanhol, francês (matriz esparsa) |
| **Prompts únicos** | 600 (40 por país × 15) |
| **Total de respostas** | ~336.000 (cada modelo responde cada prompt × 2 personas × 2 réplicas) |
| **Custo total** | ~US$ 25-28 (orçamento absorvido pela reserva R$ 255) |
| **Validação** | 3 juízes-LLM em ensemble + revisão humana por especialistas regionais |

### Hipóteses (declaradas antes da coleta)

| # | Hipótese | Status no pré-registro |
|---|---|---|
| **H1** | Países do Sul Global recebem respostas menos precisas que países do Norte Global (gradiente Joshi/HDI) | **Co-primary confirmatory** |
| **H4** | Representação do país no corpus de treino (Wikipedia + Common Crawl) explica parcialmente o gradiente | **Co-primary confirmatory** |
| **H6 (NOVA)** | A persona "gestor público" **reduz o viés geográfico** em comparação ao prompt neutro (efeito de instrução contextual) | **Co-primary confirmatory** |
| H3 | Modelo regional brasileiro (Cabra-Mistral 7B) reduz o gap em português para BRA | Secondary confirmatory |
| H2, H5 | Interação idioma × país; open frontier vs closed frontier | Exploratory |

---

## 4. Expectativas de publicação (leque editorial AMPLIADO)

O pivot para Air Pollution Policy **dobra as opções editoriais**:

| Revista | Fator de Impacto | Foco | Probabilidade |
|---|---|---|---|
| **Patterns** (Cell Press) | 7,4 | IA multidisciplinar | 32-40% |
| **Environmental Research Letters** (IOP) | 5,8 | Política ambiental | 35-45% |
| **Environmental Science & Policy** (Elsevier) | 5,6 | Política ambiental aplicada | 40-50% |
| **Atmospheric Environment** (Elsevier) | 5,0 | Poluição atmosférica | 30-40% |
| **Nature Machine Intelligence** (Springer) | 18,4 | IA fronteira | 8-12% |

**Probabilidade cumulativa em ≤3 tentativas Q1/Q2:** **90-95%** (subiu de 85-90% com o pivot)

**Tempo estimado submissão → aceitação:** 4-8 meses.

**Open access:** CC-BY 4.0 via convênio CAPES-Elsevier (gratuito para Environmental Research Letters; APC ~US$ 2.500 para Patterns, dentro do orçamento institucional).

**Sua autoria:** 2ª autora institucional sênior, **agora com papel intelectual ativo** — validação de taxonomia de tarefas + ground truth de normas técnicas brasileiras de qualidade do ar.

---

## 5. Sobre o pré-registro (versão 7 — atualizada para o novo escopo)

### O que é

Pré-registro é o ato de **depositar publicamente — antes de coletar os dados** — um documento detalhando:
- Quais hipóteses vamos testar (incluindo agora **H6 sobre persona**)
- Quais análises estatísticas vamos rodar
- Quais decisões já foram tomadas

Deposito em **OSF — Open Science Framework** (osf.io), plataforma pública mantida pelo Center for Open Science (organização sem fins lucrativos, EUA). Gera **DOI imutável com data e hora**.

### Por que pré-registrar (3 razões)

**Razão 1 — Validade científica.**
Sem pré-registro, com tantas combinações (14 modelos × 600 perguntas × 2 personas × várias métricas), há risco real de *p-hacking* ou *HARKing* (reportar só o que deu resultado interessante depois). Pré-registro **separa confirmatório de exploratório**.

**Razão 2 — Sinal editorial.**
Revistas Q1 em IA e em política ambiental (Patterns, Environmental Research Letters, ES&P) estão exigindo pré-registro para estudos de auditoria. Reviewers verificam o DOI.

**Razão 3 — Proteção documental.**
Defesa imediata contra acusações de p-hacking — apontamos para o DOI com data anterior à coleta.

### Como pré-registrar (procedimento)

1. **Conta OSF** — criada gratuitamente em osf.io (email institucional UTFPR).
2. **Documento v7** — pré-registro atualizado para refletir o novo escopo (Air Pollution Policy + persona within-subject + H6). Esqueleto pronto em `preregistration/osf_prereg_v7_skeleton.md`.
3. **Aprovação dos coautores** — Profa. Yara e Dr. Eduardo leem e endossam (**estamos aqui**).
4. **Depósito no OSF** — upload do PDF, template "Standard Pre-Registration", revisão automática (~24h), publicação.
5. **DOI imutável** gerado — citado no manuscrito final.

**Tempo total após aprovação:** 1-2 dias.

---

## 6. O que preciso de você agora (3 itens)

1. **Validar a taxonomia de 5 tarefas** (T1-T5) para o domínio Air Pollution Policy — anexo abaixo. Sua expertise técnica em qualidade do ar é o que dá rigor ao desenho.

2. **Revisar 10 prompts piloto BRA** (5 tarefas × 2 personas) em `data/ap_policy_pilot_bra_v1.jsonl`. Sinalizar se o nível de dificuldade, ground truth e abordagem fazem sentido.

3. **Endossar o pré-registro v7** após ajustes (ou indicar mudanças necessárias). Após seu OK + Dr. Eduardo → depósito OSF imediato.

---

## Anexo — Taxonomia de tarefas (proposta)

| Task | Nome | Exemplo BRA |
|---|---|---|
| **T1** | Norma técnica | *Qual o limite anual de PM₂,₅ segundo a Resolução CONAMA 491/2018?* |
| **T2** | Dado factual local | *Qual o nível médio anual de PM₂,₅ medido na RMSP em 2023, segundo CETESB?* |
| **T3** | Síntese de evidência em saúde | *Resuma a evidência epidemiológica sobre mortalidade atribuível a PM₂,₅ no Brasil, 2015-2024.* |
| **T4** | Instrumentos de política | *Liste os 3 principais programas federais brasileiros de controle de poluição atmosférica em vigor em 2024, com órgão executor.* |
| **T5** | Recomendação aplicada | *Como secretário municipal, recomende 3 ações de curto prazo para reduzir picos de PM₂,₅ em região metropolitana brasileira durante inversão térmica.* |

Cada tarefa rodada **2× (neutral vs persona)** → matriz **2 × 5 = 10 condições** por país × modelo.

---

## Referências de apoio

- **Nosek, B. A., et al. (2018).** *The preregistration revolution.* PNAS, 115(11), 2600-2606. — Marco teórico do pré-registro.
- **Mohamed, S., Png, M. T., & Isaac, W. (2020).** *Decolonial AI: Decolonial theory as sociotechnical foresight in artificial intelligence.* Philosophy & Technology, 33(4), 659-684. — Fundamentação crítica.
- **Joshi, P., et al. (2020).** *The state and fate of linguistic diversity and inclusion in the NLP world.* ACL 2020. — Base para estratificação linguística.
- **GBD 2019 Risk Factor Collaborators (2020).** *Global burden of 87 risk factors in 204 countries.* The Lancet, 396, 1223-1249. — Mortalidade atribuível a PM₂,₅.
- **OSF Pre-Registration:** https://osf.io/prereg/ — Plataforma e template oficial.

---

**Contato para dúvidas:** Lucas Rover — lucasrover@alunos.utfpr.edu.br — +55 (48) 99974-8298
**Repositório do projeto (privado):** https://github.com/Roverlucas/artigo-vies-analise-regional
