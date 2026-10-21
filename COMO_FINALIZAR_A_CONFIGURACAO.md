# COMO FINALIZAR A CONFIGURAÇÃO (Google Classroom → Xano → EduTrack)

O código do FastAPI, do SQLite e do frontend já está pronto. Falta só o que depende de contas e credenciais suas.
Nada abaixo foi feito ou testado com Google/Xano reais.

## 1. Instalar e rodar os testes (no seu ambiente)
1. `cd backend && pip install -r requirements.txt`
2. Faça backup do `edutrack.db`. A suíte antiga (`seed_data`) apaga e recria o banco do diretório atual; rode numa cópia.
3. Na raiz: `pytest`. Se algo falhar, cole a saída.
4. Ao subir o app, a migração aditiva adiciona as colunas do Classroom sem apagar dados.

## 2. Google Cloud
1. Crie um projeto e ative a **Google Classroom API**.
2. Tela de consentimento OAuth: tipo Externo (ou Interno, se for conta Workspace da escola) e adicione seu e-mail como usuário de teste.
3. Escopos (somente leitura): `openid`, `email`, `classroom.courses.readonly`, `classroom.coursework.me.readonly`.
4. Crie um **OAuth Client ID (Aplicativo da Web)**. Em "URIs de redirecionamento autorizados" coloque a URL do endpoint `GET /oauth/google/callback` do Xano (passo 3.5).
5. Guarde Client ID e Client Secret. Contas escolares podem ter apps de terceiros bloqueados pelo administrador. Uso público exige verificação do Google.

## 3. Xano
1. `xano workspace pull` (backup) e `xano workspace push -d openspec/xanoscript/xano-classroom --dry-run`; revise e então faça o push (sem `--sync --delete`). Detalhes em `openspec/xanoscript/xano-classroom/README.md`.
2. Defina as variáveis de ambiente do workspace: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `TOKEN_ENCRYPTION_KEY` (gere um valor aleatório longo), `EDUTRACK_API_KEY` (gere outro), `APP_ALLOWED_RETURN_URLS` (ex.: `http://localhost:8000`).
3. Marque `access_token_enc` e `refresh_token_enc` como API Access *internal*.
4. Crie o API group `integration` e construa os 7 endpoints descritos em `openspec/xanoscript/xano-classroom/IMPLEMENTACAO_XANO.md`. Eles ainda não existem no Xano.
5. Copie a URL pública do callback para `GOOGLE_REDIRECT_URI` e para o Google Cloud (passo 2.4). Verifique no Xano como devolver o redirecionamento 302 (marcado no documento).

## 4. `.env` do FastAPI
Copie `.env.example` para `.env` (já está no `.gitignore`) e preencha: `XANO_BASE_URL` (URL do API group `integration`, sem barra final), `XANO_API_KEY` (o mesmo valor de `EDUTRACK_API_KEY`) e, se não usar localhost, `APP_BASE_URL`. O app não lê `.env` sozinho: exporte as variáveis no shell ou use `uvicorn --env-file .env`.

## 5. Teste final de ponta a ponta
1. Suba o app, faça login, abra **Disciplinas** e clique em **Conectar Google Classroom**.
2. Autorize no Google; você volta ao app com a mensagem de sucesso.
3. Clique em **Sincronizar agora**; confira cursos e atividades (prazo, pontuação, link, entrega).
4. Sincronize de novo: não deve duplicar nada. Edite `actual_time_minutes` de uma tarefa importada, mude o título no Classroom e sincronize: o título atualiza e o tempo permanece.
5. Teste **Desconectar** e reconectar.

## Antes de usar de verdade
Troque a `SECRET_KEY` padrão do FastAPI e restrinja o CORS (hoje `*`). Não há sincronização periódica: é sob demanda (uma tarefa agendada no Xano pode ser acrescentada depois).
