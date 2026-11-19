## Why

Na validação para a entrega foram encontrados três defeitos: (1) uma conta criada no EduTrack não aparece na tabela `alunos` do Xano, porque a sincronização rodava só no navegador, engolia erros e comparava aluno por nome; (2) "Esqueci minha senha" não envia e-mail, apenas confirma que a conta existe e deixa qualquer pessoa trocar a senha de qualquer e-mail; (3) IA, analytics e relatório PDF leem o SQLite local, enquanto disciplinas e tarefas são gravadas no Xano, então a IA analisa dados vazios.

## What Changes

- Sincronização do aluno com o Xano passa a ser feita pelo FastAPI (cadastro e login), de forma idempotente por e-mail, com o resultado devolvido ao frontend.
- Recuperação de senha com token de uso único e expiração, enviado por e-mail (SMTP configurável; modo `console` para desenvolvimento). **BREAKING**: `POST /api/auth/reset-password` passa a exigir `token` em vez de `email`.
- Espelhamento Xano → SQLite (disciplinas e tarefas do aluno) antes de analytics, IA e relatório, para que usem os dados reais.
- Correção do assistente de IA (`total_time_spent_hours` inexistente) e modelo Gemini configurável.
- Testes passam a usar banco temporário e não apagam `edutrack.db`.

## Capabilities

### New Capabilities
- `password-recovery`: recuperação de senha por e-mail com token.
- `xano-student-sync`: criação/vínculo do aluno no Xano e espelhamento de disciplinas e tarefas.

### Modified Capabilities

## Impact

- `backend/app/api/auth.py`, `core/config.py`, `core/migrations.py`, `models/`, `schemas/user.py`, `services/` (e-mail, Xano, IA), `api/analytics.py`, `api/ai_insights.py`, `api/reports.py`, `api/tasks.py`.
- `frontend/js/api.js`, `auth.js`, `index.html`.
- `.env.example`, README, testes.
- Não foi possível validar contra o Xano real neste ambiente (sem acesso de rede); a validação usa um Xano simulado.
