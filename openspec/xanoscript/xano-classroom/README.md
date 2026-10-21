# Xano — estrutura de dados do Google Classroom (Etapa 2)

Schemas em **XanoScript real** (formato `table`), escritos conforme a documentação oficial
(ver "Fontes"). Esta pasta é independente dos `.xs` antigos em `openspec/xanoscript/`,
que são pseudo-código documental e **não devem ser enviados ao Xano**.

> Nunca use `openspec/xanoscript/` como alvo de `xano workspace push`.
> O alvo é **somente** esta pasta (`openspec/xanoscript/xano-classroom`).

## Escopo
Estrutura de dados (`table/*.xs`). A lógica dos endpoints (OAuth, sincronização, export) está especificada em
`IMPLEMENTACAO_XANO.md` — ainda **não construída** no workspace.

## Tabelas (`table/`)
| Tabela | Papel | Unicidade (idempotência) |
|---|---|---|
| `local_users` | Espelho do usuário do FastAPI (sem senha). Não toca na tabela nativa `user` | `local_user_id` |
| `google_connections` | Conexão OAuth; tokens cifrados em `*_enc` | `owner_id` (1 conexão por usuário) |
| `classroom_courses` | Cursos do Classroom | `(owner_id, google_course_id)` |
| `classroom_coursework` | Atividades | `(owner_id, classroom_courses_id, google_coursework_id)` |
| `classroom_submissions` | Entregas do aluno | `(owner_id, classroom_coursework_id, google_submission_id)` |
| `sync_runs` | Log de sincronizações | — |
| `oauth_states` | `state` anti-CSRF do OAuth (uso único, validade curta) | `nonce` |

Relações (FKs Xano via `table = "..."`): todas as tabelas filhas apontam para `local_users.id` por
`owner_id`; `classroom_coursework` → `classroom_courses`; `classroom_submissions` → `classroom_coursework`.

Convenção de nomes: `local_users.local_user_id` é o `users.id` do FastAPI; `owner_id` é a PK interna
do Xano (`local_users.id`); campos `google_*_id` são IDs do Classroom (texto).

## Propriedade dos dados
- **Classroom (Xano):** título, descrição, curso, criação, prazo (`due_at`), pontuação (`max_points`), link (`alternate_link`) e estado da entrega (`state`, `late`, `assigned_grade`).
- **Local (FastAPI/SQLite), NÃO replicados no Xano:** `actual_time_minutes`, status manual, `workload_hours`, `estimated_time_minutes` e demais campos editáveis.
- `selected` (em `classroom_courses`) é configuração da integração, não campo acadêmico.

## Mapeamento previsto (usado nas etapas seguintes)
- `classroom_courses` → `subjects` (campos novos no FastAPI na etapa de FastAPI): `google_course_id`, `name`, `alternate_link`...
- `classroom_coursework` → `academic_tasks`: `title`, `description`, `due_at → due_date`, `max_points`, link.
- `classroom_submissions.state` → sugestão de conclusão (`TURNED_IN`/`RETURNED`), sem sobrescrever o status manual.

## Decisão: `subjects` e `academic_tasks` do Xano NÃO foram alterados
Os `.xs` existentes são pseudo-código, o estado real do workspace é desconhecido e os campos locais
ficam no FastAPI. Por isso o par `classroom_courses`/`classroom_coursework` faz o papel de
"subjects/tasks vindos do Classroom" com unicidade por usuário + ID do Classroom, sem tocar em
tabelas que possam ter dados. O vínculo com `subjects`/`academic_tasks` ocorre no FastAPI (IDs do Classroom).

## Tokens Google
- Não há senha do Google em lugar nenhum.
- `access_token_enc`/`refresh_token_enc` guardam **ciphertext**. A documentação do Xano indica
  criptografia no nível da aplicação (filtro/função `encrypt`, ex.: `aes-256-cbc`, ou JWE) com a chave
  em **variável de ambiente**; não há criptografia de campo "de um clique".
- O tipo `password` do Xano não serve: é hash (irreversível) e o refresh token precisa ser recuperável.
- A lógica de cifrar/decifrar será implementada com o OAuth (etapa futura). Nenhum segredo vai ao frontend.

## Como aplicar (você, no seu ambiente)
1. `npm install -g @xano/cli` e selecione o workspace (idealmente numa branch de teste).
2. Faça `xano workspace pull -d ./xano-backup` antes (backup do estado real).
3. `xano workspace push -d openspec/xanoscript/xano-classroom --dry-run` e revise o preview.
4. Só depois, `xano workspace push -d openspec/xanoscript/xano-classroom`. **Não** use `--sync --delete` nem `--truncate`.
5. O CLI grava `guid` nos arquivos após o push (não escreva guids à mão).
6. Valide com o Xano Language Server (extensão VS Code) ou a ferramenta de validação do Developer MCP.

## Manual no workspace Xano (após o push)
- Criar a variável de ambiente da chave de criptografia dos tokens (valor gerado por você; nunca no repositório).
- Marcar `access_token_enc` e `refresh_token_enc` como API Access **internal** (recurso da UI), para não aparecerem em respostas.
- Conferir os índices únicos e as FKs na UI.
- Grupo de API `integration` com os endpoints de `IMPLEMENTACAO_XANO.md` e as variáveis de ambiente listadas lá.

## Pontos a confirmar na validação do Xano
- Padrão de campo opcional+nulo `text? campo?` (extrapolado de `timestamp? last_login?` e `email? email`, ambos documentados). Se o validador rejeitar, a documentação também descreve a forma `text ?campo?`.
- Valores padrão `bool x?=true`/`int x?=0` seguem o padrão documentado `?=valor`.

## Fontes consultadas (docs.xano.com)
- XanoScript for the Database: https://docs.xano.com/xanoscript/db
- Field Types Reference: https://docs.xano.com/xanoscript/field-type-reference
- Multidoc (formato real exportado, FKs com `table = "..."`, índices, `guid`): https://docs.xano.com/xanoscript/multidoc
- CLI push/pull e dry-run: https://docs.xano.com/xano-cli/get-started , https://docs.xano.com/xano-cli/managing-data , https://docs.xano.com/xano-cli/cheatsheet
- Segurança (`encrypt`/`decrypt`/JWE, chave em variável de ambiente): https://docs.xano.com/xanoscript/filter-reference/security
- Classroom API (enums de `SubmissionState`): https://developers.google.com/workspace/classroom/reference/rest/v1/courses.courseWork.studentSubmissions
