## Context

Usuários vivem no SQLite local (JWT próprio). Disciplinas e tarefas são lidas e gravadas pelo navegador diretamente no Xano (`alunos`, `materias`, `tarefas`). Analytics, IA e PDF leem apenas o SQLite.

## Decisions

- **Sincronização no backend**: `XanoCrudClient` (httpx) usa `XANO_CRUD_BASE_URL` (grupo CRUD, sem chave). `ensure_aluno` busca por e-mail e só cria se não existir; nunca casa por nome.
- **Espelho Xano → SQLite**: colunas `xano_id` em `subjects` e `academic_tasks` (migração aditiva). Upsert por `xano_id`; `actual_time_minutes` e `estimated_time_minutes` locais são preservados. Falha do Xano não derruba analytics (usa o que já está no SQLite).
- **Recuperação de senha**: tabela `password_reset_tokens` guarda apenas o hash SHA-256 do token, validade de 30 min, uso único. Resposta sempre genérica. Envio por `smtplib` (`EMAIL_BACKEND=smtp`) ou, por padrão sem SMTP, `console` (log + arquivo em `outbox/`), declarado como modo de desenvolvimento.
- **Tempo de estudo**: rota `POST /academic_tasks/by-xano/{xano_id}/study-time` para o cronômetro, que só conhece IDs do Xano.

## Risks

- Campos reais de `alunos` no Xano não puderam ser inspecionados; o payload segue o que o frontend já usava (`nome`, `email`, `curso`, `semestre`).
- Disciplinas do Xano sem `alunos_id` do usuário não são espelhadas.
