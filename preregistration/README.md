# O que este diretório é — e o que ele não é

**Nenhum registro foi criado no OSF.** Apesar do prefixo `osf_prereg_` nos nomes
dos arquivos, o depósito planejado nunca aconteceu: `docs/progress.md` o registra
como "aguardando deposit" e assim ficou. Por isso o manuscrito **não reivindica
pré-registro** e se reporta como exploratório do início ao fim. Se você chegou aqui
esperando encontrar um registro público, ele não existe.

O que existe é o **plano de análise**, em suas versões sucessivas, versionado no
git. Isso é menos do que um registro público e mais do que nada: as datas de
inclusão de cada arquivo são verificáveis e anteriores à coleta.

| arquivo | entrou no git | o que é |
|---|---|---|
| `osf_prereg_v0_1_RETROACTIVE.md` | 2026-04-26 | a v0.1, redigida em 23/04, adicionada depois para preservar o rastro |
| `osf_prereg_draft.md` | 2026-04-23 | plano de trabalho, revisado ao longo de abril |
| `osf_prereg_v7_skeleton.md` | 2026-06-05 | esqueleto da v7 |
| `osf_prereg_v7_full.md` | 2026-06-05 | v7 completa |

Confira com `git log --diff-filter=A --format='%ad' --date=short -- <arquivo>`.

## Sobre a palavra "retroactive"

No nome da v0.1 ela significa que um rascunho **anterior** foi adicionado ao
repositório **depois**, para que o histórico de hipóteses ficasse rastreável.
Não significa que qualquer registro tenha sido datado para trás — não há registro
a datar. O próprio arquivo é explícito quanto a isso, e vai além: ele documenta
que a v2.0 foi retirada por HARKing identificado em auditoria interna. Esse
material fica aqui porque expõe o processo, não porque o favorece.

## Por que o plano não vale como pré-registro

Um plano que só o autor pode ver não restringe o autor. O valor do pré-registro
vem de ser público e imutável antes dos dados, e nada disso se aplica aqui. O
manuscrito trata os desvios em relação a este plano numa seção própria, e reporta
os testes como exploratórios em vez de confirmatórios — que é a leitura correta
do que estes arquivos sustentam.
