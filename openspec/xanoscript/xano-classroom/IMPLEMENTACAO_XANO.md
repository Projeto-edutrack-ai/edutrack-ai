# O que construir no Xano (especificação — NÃO é XanoScript)

Este documento descreve a lógica dos endpoints do API group `integration`. A **sintaxe XanoScript real
dos endpoints/funções não foi escrita** porque não pôde ser validada neste ambiente; construa pela UI
(Function Stack) ou valide o código com o Language Server do Xano. As **tabelas** (`table/*.xs`) já estão em XanoScript real.

Nada aqui foi criado no workspace real. Contrato consumido pelo FastAPI: `openspec/specs/xano-classroom-contract.md`.

## Variáveis de ambiente do workspace Xano (valores seus; nunca no repositório/frontend)
| Nome | Uso |
|---|---|
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Credenciais OAuth do Google Cloud |
| `GOOGLE_REDIRECT_URI` | URL pública do endpoint `GET /oauth/google/callback` do Xano (igual à cadastrada no Google) |
| `TOKEN_ENCRYPTION_KEY` | Chave para cifrar os tokens (`access_token_enc`/`refresh_token_enc`) |
| `EDUTRACK_API_KEY` | Mesmo valor de `XANO_API_KEY` do FastAPI; checado no cabeçalho `X-API-Key` |
| `APP_ALLOWED_RETURN_URLS` | Origens permitidas para o redirecionamento final (ex.: `http://localhost:8000`) |

## Regras comuns
- Todo endpoint, exceto o callback, começa comparando `X-API-Key` com `EDUTRACK_API_KEY` (diferente → HTTP 401).
- Erros em JSON `{"message": "..."}`. Não conectado / reautorização necessária → HTTP 409.
- Toda consulta filtra por `owner_id` (resolvido de `local_users.local_user_id`). Nunca devolver dados de outro usuário.
- Nunca registrar nem devolver tokens, `code` ou client secret.
- Tokens: cifrar com a chave de `TOKEN_ENCRYPTION_KEY` antes de gravar (documentação do Xano: filtros/funções de criptografia no nível da aplicação; confirmar a função exata no seu workspace).

## Escopos OAuth (somente leitura)
`openid`, `email`, `https://www.googleapis.com/auth/classroom.courses.readonly`,
`https://www.googleapis.com/auth/classroom.coursework.me.readonly`.
- A referência atual do Google para `studentSubmissions.list` aceita `classroom.coursework.me.readonly`; por isso
  **não** pedimos `student-submissions.me.readonly` (ao contrário do plano inicial).
- Confirmar na referência do Google o escopo exigido por `courses.list`. Escopos do Classroom são "sensíveis": o app público exige verificação.

## Endpoints
**1. `POST /oauth/google/start`** body `{local_user_id, return_url}` → `{authorization_url}`
1. Upsert em `local_users` por `local_user_id`. 2. Validar que `return_url` pertence a `APP_ALLOWED_RETURN_URLS` (senão 400; evita open redirect).
3. Gerar `nonce` aleatório (≥ 32 bytes), gravar em `oauth_states` (`expires_at` = agora + 10 min).
4. Montar `https://accounts.google.com/o/oauth2/v2/auth` com: `client_id`, `redirect_uri=GOOGLE_REDIRECT_URI`, `response_type=code`,
   `scope`, `access_type=offline`, `prompt=consent`, `include_granted_scopes=true`, `state=nonce`.

**2. `GET /oauth/google/callback?code&state[&error]`** (público; a segurança é o `state`)
1. Buscar `oauth_states` por `nonce`; ausente/expirado/já usado → redirecionar com `classroom=error&reason=state`. Marcar `used_at`.
2. `error` presente ou sem `code` → redirecionar com `classroom=error&reason=denied`.
3. `POST https://oauth2.googleapis.com/token` (`grant_type=authorization_code`, `code`, `client_id`, `client_secret`, `redirect_uri`).
4. Obter `sub` e `email` (endpoint userinfo do Google ou claims do `id_token`; confirmar na doc do Google).
5. Conferir que os escopos concedidos incluem os dois do Classroom. Upsert `google_connections` (único por `owner_id`):
   tokens cifrados, `token_expires_at`, `scopes`, `status=active`. Se o Google não devolver `refresh_token` e já existir um, manter; se não existir nenhum → erro `no_refresh_token`.
6. Redirecionar o navegador (HTTP 302) para `return_url` + `?classroom=connected` (ou `?classroom=error&reason=…`).
   **Verificar no Xano** como responder 302 com `Location`; se não for possível, devolver uma página HTML mínima com redirecionamento.

**3. `GET /classroom/status?local_user_id`** → `{connected, status, google_email, scopes, last_sync_at, courses_count}`
`status`: `not_connected | active | needs_reauth | revoked | error`. `last_sync_at` = último `sync_runs` com `success`/`partial`.

**4. `POST /classroom/sync`** body `{local_user_id}` → `{status, courses, coursework, submissions, errors}`
1. Sem conexão ativa → 409. Criar `sync_runs` (`running`).
2. Token de acesso válido: se `token_expires_at` < agora+60s, renovar com `grant_type=refresh_token`. `invalid_grant` → `status=needs_reauth`, 409.
3. `GET https://classroom.googleapis.com/v1/courses` (`studentId=me`, `courseStates=ACTIVE`, `pageToken` em laço). Upsert `classroom_courses`
   (curso novo entra com `selected=true`; existente mantém `selected`; curso que sumiu → `is_active=false`).
4. Para cada curso `selected` e ativo: `GET /v1/courses/{id}/courseWork` (paginado; alunos só veem `PUBLISHED`). Upsert `classroom_coursework`
   (chave: owner + curso + `google_coursework_id`).
5. Entregas: `GET /v1/courses/{id}/courseWork/-/studentSubmissions?userId=me` (confirmado na referência do Google: `-` = todas as atividades). Upsert `classroom_submissions`.
6. Falha em um curso → registrar em `errors`, seguir com os demais, `status=partial`. Retentar 429/5xx com espera curta e limite.
7. Fechar `sync_runs` (`finished_at`, contadores, `status`). Não existe tempo real: só sob demanda (e, depois, tarefa agendada do Xano).

**5. `GET /classroom/courses?local_user_id`** → `{courses:[{google_course_id,name,section,course_state,selected,is_active}]}`

**6. `GET /classroom/export?local_user_id[&since]`** → payload canônico (ver contrato). Cursos `selected` e `is_active`; atividades `is_active`;
`submission` da atividade (ou `null`). Datas em epoch ms. `since` é opcional (o FastAPI atual não o usa; pode ser ignorado na v1).

**7. `DELETE /classroom/connection?local_user_id`** → `{disconnected:true}`. Revogar o token (`POST https://oauth2.googleapis.com/revoke`), apagar tokens e marcar `status=revoked`.

## Mapeamento Google → Xano
| Google | Tabela.campo |
|---|---|
| Course `id`, `name`, `section`, `descriptionHeading`, `description`, `room`, `courseState`, `alternateLink`, `creationTime`, `updateTime` | `classroom_courses`: `google_course_id`, `name`, `section`, `description_heading`, `description`, `room`, `course_state`, `alternate_link`, `google_created_at`, `google_updated_at` |
| CourseWork `id`, `title`, `description`, `alternateLink`, `maxPoints`, `state`, `workType`, `creationTime`, `updateTime` | `classroom_coursework`: `google_coursework_id`, `title`, `description`, `alternate_link`, `max_points`, `state`, `work_type`, `google_created_at`, `google_updated_at` |
| CourseWork `dueDate{year,month,day}` + `dueTime{hours,minutes,seconds,nanos}` (UTC) | `due_at` (campos de hora ausentes = 0; sem `dueDate` → nulo). Se vier `dueDate` sem `dueTime` (a doc exige os dois), usar 23:59:59Z — decisão a confirmar |
| StudentSubmission `id`, `state`, `late`, `assignedGrade`, `alternateLink`, `creationTime`, `updateTime` | `classroom_submissions`: `google_submission_id`, `state`, `late`, `assigned_grade`, `alternate_link`, `google_created_at`, `google_updated_at` |

IDs do Google são texto e estáveis; o `courseWork.id` só é único dentro do curso (por isso o índice composto).

## Exemplos
`POST /oauth/google/start` → `{"authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?...&state=<nonce>"}`

`GET /classroom/status` → `{"connected": true, "status": "active", "google_email": "aluno@gmail.com", "last_sync_at": 1760572800000, "courses_count": 3}`

`POST /classroom/sync` → `{"status": "success", "courses": 3, "coursework": 21, "submissions": 21, "errors": []}`

Parcial → `{"status": "partial", "courses": 3, "coursework": 14, "submissions": 14, "errors": ["course 123: PERMISSION_DENIED"]}`

Erro de reautorização → HTTP 409 `{"message": "reauthorization_required"}`
