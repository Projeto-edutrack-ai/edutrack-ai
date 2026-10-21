# Contrato Xano ⇄ FastAPI (Google Classroom) — PARTE 1

Status: **contrato proposto, ainda não implementado no Xano** (lógica em `openspec/xanoscript/xano-classroom/IMPLEMENTACAO_XANO.md`). O cliente
(`backend/app/services/xano_client.py`) e o mapeador (`classroom_mapper.py`) seguem este documento.
Os endpoints serão criados no API group `integration` do Xano numa etapa futura.

## Transporte e autenticação
- Base: `XANO_BASE_URL` (o API group, sem barra final). Chave: `XANO_API_KEY` no cabeçalho `X-API-Key`.
- A chave existe somente no backend. O frontend nunca fala com o Xano.
- Todos os endpoints recebem `local_user_id` (= `users.id` do FastAPI) e só devolvem dados desse usuário.
- Respostas JSON. Status >= 300 é erro.

## Endpoints
| Método | Caminho | Uso |
|---|---|---|
| GET | `/classroom/status?local_user_id=` | Estado da conexão (objeto JSON livre) |
| GET | `/classroom/courses?local_user_id=` | Lista de cursos (lista ou `{"courses":[...]}`) |
| GET | `/classroom/export?local_user_id=&since=` | Export canônico (abaixo). `since` opcional (ISO 8601) |
| POST | `/classroom/sync` body `{"local_user_id": n}` | Pede ao Xano que sincronize com o Google. 409 se não conectado |
| POST | `/oauth/google/start` body `{"local_user_id": n, "return_url": "…"}` | Devolve `{"authorization_url": "https://accounts.google.com/…"}` (https obrigatório) |
| DELETE | `/classroom/connection?local_user_id=` | Revoga/apaga a conexão Google. Dados já importados no EduTrack permanecem |
| GET | `/oauth/google/callback` | Público, chamado pelo Google; redireciona o navegador para `return_url?classroom=connected` ou `?classroom=error&reason=…` |

## Status (`GET /classroom/status`)
```json
{"connected": true, "status": "active", "google_email": "aluno@gmail.com", "last_sync_at": 1760572800000}
```
`status`: `not_connected | active | needs_reauth | revoked | error`. Campos ausentes/inválidos são tolerados pelo FastAPI.

## Export canônico (`GET /classroom/export`)
```json
{
  "local_user_id": 1,
  "courses": [
    {
      "google_course_id": "123",
      "name": "Cálculo I",
      "description": "…", "description_heading": "…",
      "alternate_link": "https://classroom.google.com/c/…",
      "selected": true, "is_active": true,
      "coursework": [
        {
          "google_coursework_id": "456",
          "title": "Lista 1", "description": "…",
          "alternate_link": "https://…",
          "max_points": 10, "due_at": "2026-10-15T23:59:00Z",
          "state": "PUBLISHED", "is_active": true,
          "submission": { "state": "TURNED_IN", "google_updated_at": 1760572800000 }
        }
      ]
    }
  ]
}
```
- `local_user_id` no export é opcional; se presente e diferente do solicitado, o lote é rejeitado.
- Datas: epoch em **milissegundos** (formato do Xano; valores < 1e11 são lidos como segundos) ou ISO 8601.
  Sem fuso = UTC. O SQLite guarda UTC sem tzinfo.
- `submission` pode ser `null`/ausente. Estados esperados: `NEW`, `CREATED`, `TURNED_IN`, `RETURNED`,
  `RECLAIMED_BY_STUDENT`. Desconhecidos são aceitos como "não concluído" (com aviso).

## Regras de importação
| Xano | EduTrack |
|---|---|
| course | `subjects` (`source="classroom"`, `classroom_course_id`) |
| coursework | `academic_tasks` (`classroom_coursework_id`, único por usuário+curso) |
| `due_at` | `due_date` |
| `max_points` | `max_points` |
| `alternate_link` | `classroom_link` |
| `submission.state` | `classroom_submission_state`; `TURNED_IN`/`RETURNED` → `status="completed"` |

- Controlados pelo Classroom: nome/título, descrição, prazo, pontuação, link, estado da entrega.
- Locais (nunca sobrescritos): `workload_hours`, `professor`, `start_date`/`end_date`,
  `estimated_time_minutes`, `actual_time_minutes` e o `status` manual.
- O Classroom só **promove** a tarefa para `completed`, e só quando a entrega passa de não-concluída
  para concluída; nunca rebaixa, e uma reabertura manual não é desfeita a cada sincronização.
- Cursos com `selected=false`/`is_active=false` e atividades `DRAFT`/`DELETED`/`is_active=false` são ignorados.
- Nada é apagado localmente (inclusive o que sumiu do Classroom). Registros `source="local"` não são tocados.
- Não há adoção automática de disciplinas locais com o mesmo nome: a identidade é o ID do Classroom.
