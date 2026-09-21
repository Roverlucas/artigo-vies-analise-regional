# Review Rounds — version ledger

One line per review/revision round, newest last. Gate **SA-QG-018 (Round Persistence &
Version Control)**. A round is closed when it is WRITTEN (review-log), SYNCED (dependent
artifacts), REMEMBERED (project memory), VERSIONED (this file) and PUSHED.
A commit message is not a round record.

Rounds 1–7 were reconstructed on 2026-09-21 from the git history (commit hashes cited in
each log). The numbers they cite are the ones in force at that date, not the current ones;
`data/processed/freeze_all_effects.json` (section `corrigido`) is the only source for the
manuscript.

| # | Date | Title | Verdict | Review log | Open items |
|---|------|-------|---------|-----------|------------|
| 1 | 2026-08-22 | Congelamento com painel de 3 juízes; H2 principal, H1 exploratório | revisions-applied (39 pp) | `data/review-log/2026-08-22-artigo-vies-analise-regional-round1.yaml` | declaração de IA; validação humana (vai sem) |
| 2 | 2026-08-23 | Auditoria Gemini 2.5 Pro + DeepSeek-V3 (37 achados); adaptação ao GIQ | revisions-applied, 1 refutação (41 pp) | `data/review-log/2026-08-23-artigo-vies-analise-regional-round2.yaml` | elsarticle; graphical abstract |
| 3 | 2026-08-24 | Checkup de 14 pareceres; anti-slop; PT reconstruído; corte 85→72 pp | revisions-applied, 3 refutações | `data/review-log/2026-08-24-artigo-vies-analise-regional-round3.yaml` | corte p/ ~55 pp; 30 slop em pt-resultados |
| 4 | 2026-08-25 | Corte →57 pp; auditoria 11 lentes; consistency_gate.py (mutação 6/6) | revisions-applied; 3 claims recusadas pelo autor | `data/review-log/2026-08-25-artigo-vies-analise-regional-round4.yaml` | 29 slop em pt-discussao |
| 5 | 2026-08-25 | Auditoria Codex CLI (4,5/10); unidade = célula deduplicada (8.300) | revisions-applied; nenhum veredito muda | `data/review-log/2026-08-25-artigo-vies-analise-regional-round5.yaml` | autoria 3 vs 5; ferramentas de IA |
| 6 | 2026-08-27 | Referências: 44/44 fichadas, 36 full-text, 16 correções de atribuição | revisions-applied (59 pp) | `data/review-log/2026-08-27-artigo-vies-analise-regional-round6.yaml` | 7 refs em abstract; 1 livro |
| 7 | 2026-08-27 | Gate check (C) p/ markdown público; autoria de cinco; CFF e preregistration/README.md declaram que o plano nunca foi depositado (sem pré-registro) | revisions-applied — pronto p/ coautores | `data/review-log/2026-08-27-artigo-vies-analise-regional-round7.yaml` | e-mails autores 2–3; dados privados; leitura humana |
| 8 | 2026-09-21 | Fechamento retroativo 1–7; declaração de IA completa; pacote aos coautores | revisions-applied (59/17/31/16 pp) | `data/review-log/2026-09-21-artigo-vies-analise-regional-round8.yaml` | revisão dos coautores; e-mails; leitura humana; dados |
| 9 | 2026-09-21 | Adjudicação do parecer externo (2 partes): 31 UPHELD, 2 REJECTED, 4 DEFERRED; A-0 juiz×tier | adjudicated — não submeter | `data/review-log/2026-09-21-artigo-vies-analise-regional-round9-adjudication.yaml` | tudo aberto até a rodada 10 |
| 10 | 2026-09-21 | T1 por código; UK/EGY/BRA chaves; base única; Métodos como executado; H4 rebaixado; ~60 números; gate ampliado | revisions-applied (66/18/35/16 pp), gates limpos | `data/review-log/2026-09-21-artigo-vies-analise-regional-round10.yaml` | freeze e H4/H3 a ratificar pelo autor; validação humana; re-julgar duplicatas (API); leitura humana |
| 11 | 2026-09-21 | 2º parecer externo: números residuais (classe fechada no gate), H2 aninhado, gap só-código, Bangladesh 15→35 (fonte), hash do registro, H3 descrito como fine-tune 7B, Discussão compactada | revisions-applied, gates limpos | `data/review-log/2026-09-21-artigo-vies-analise-regional-round11.yaml` | "três correções" vs Sabiá-3 (autor); corte adicional (autor); re-julgar T4 (API); validação humana |
