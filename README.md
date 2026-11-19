# EduTrack AI — base edutrack1 corrigida

Versão baseada exclusivamente no edutrack1.zip da equipe, com as correções de 10/11/2026 e remoção do Google Classroom solicitada pela usuária. Antigravity substitui FlutterFlow com autorização do professor, conforme informado pela equipe.

## Tecnologias utilizadas
Git/GitHub, VS Code/Antigravity, HTML/CSS/JavaScript, Python/FastAPI, SQLAlchemy/SQLite, Xano, ReportLab, pytest e OpenSpec 1.17.0. Node/npm são ferramentas do OpenSpec, não um novo frontend.

## O que foi preservado
Recuperação de senha por token, tela de redefinição, mentor/IA da equipe, vínculo de tarefas e disciplinas, cronômetro, relatórios, documentos e propostas anteriores. Não houve deploy, envio ao GitHub, leitura de registros pessoais no Xano nem exclusão de tabelas remotas.

## Como testar no Windows
Extraia em pasta NOVA; abra no VS Code a pasta que contém backend, frontend e run_server.py. No PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backendequirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe run_server.py
```

Se .env já existir, preserve-o e compare os exemplos em vez de sobrescrever. O iniciador carrega o .env. Abra http://127.0.0.1:8000 e /docs para Swagger local.
Se o banco não existir, são criados dados demo: aluno@edutrack.edu.br / senha123. Não publique a conta demo. Sem URL Xano, o CRUD funciona localmente na mesma aplicação. O modo local NÃO importa os registros Xano.

## Conectar o Xano real
Leia [COMO_FINALIZAR_A_CONFIGURACAO.md](COMO_FINALIZAR_A_CONFIGURACAO.md). O OpenAPI recebido confirma as três tabelas e também confirma endpoints sem autenticação. Antes de publicar, configure proteção no workspace e a chave somente no backend. Não use o token da documentação como chave da aplicação.

O navegador agora chama somente o FastAPI com JWT. O adaptador preserva os nomes alunos/materias/tarefas e o espaço no enum em_andamento. Contas remotas antigas exigem vínculo administrativo verificado; simples coincidência de e-mail não concede acesso. Falhas de sincronização não viram métricas falsas de zero.

Progresso, busca, IA e PDF usam o espelho completo validado. No modo Xano, dados demo locais não entram nas métricas remotas. O espelho rejeita paginação incompleta e aplica atualizações/exclusões atomicamente; tempo de estudo continua local, pois não existe no contrato Xano.

## Configuração de publicação
Configure SECRET_KEY estável, DATABASE_URL com backup, APP_BASE_URL pública, CORS ALLOWED_ORIGINS, Xano e SMTP no ambiente. Sem SECRET_KEY configurada, a chave temporária muda ao reiniciar e os usuários precisam entrar novamente. As credenciais não são incluídas no ZIP.
Para frontend separado, defina window.EDUTRACK_CONFIG={apiBase:'https://SEU_BACKEND/api'} antes de carregar api.js. No mesmo domínio, usa /api; não aponta mais para localhost no computador do visitante.

EMAIL_BACKEND=console salva arquivos .eml em outbox e NÃO envia e-mails. Para envio real, configure SMTP. O mentor usa Gemini opcional ou heurísticas locais sem chave.

## Testes e OpenSpec
```powershell
.\.venv\Scripts\python.exe -m pytest -q
node --test tests/frontend-client.test.cjs
npm ci
npm run spec:validate
```
Testes usam banco temporário, SMTP local e Xano simulado. Não comprovam configuração do workspace real. Consulte docs/VALIDACAO.md.

Propostas antigas foram preservadas. A retirada de Classroom está registrada na change remove-google-classroom; a adequação de integração está em harden-edutrack1-integration, com pendências remotas explícitas. Reinicie o editor depois de carregar os workflows OpenSpec.

## Recursos principais
- CRUD com validação de proprietário no backend e PATCH nas rotas locais.
- Busca por nome/texto OU tarefas atrasadas: GET /api/search?q=Python&overdue=true.
- Script scripts/calculate_progress.py retorna JSON percentage, inclusive zero sem tarefas.
- PDF em POST /api/reports/generate e rota anterior /api/reports/weekly-pdf.
- Ponte de busca/PDF para chamadas de servidor Xano, desativada sem chave separada.
- Sem rotas, botões ou serviços Google Classroom. Registros/colunas legados não são apagados. Materiais antigos estão em docs/historico/classroom e não são instruções ativas.

## Entrega acadêmica
Ainda é necessário executar a configuração Xano real, duplicar e analisar templates Figma, exportar assets, conferir as instalações locais, fazer commits/PRs e reunir os entregáveis das 16 atividades. Este ZIP não inventa essas ações. Consulte docs/PENDENCIAS.md.
