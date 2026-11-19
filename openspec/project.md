# EduTrack AI — contexto do projeto

## Objetivo

O EduTrack AI ajuda estudantes a organizar disciplinas e atividades, acompanhar o tempo de estudo e entender seu progresso academico. A aplicacao oferece autenticacao, painel de acompanhamento, insights e relatorios em PDF. A integração acadêmica Xano depende de configuração externa. Google Classroom foi removido por solicitação da equipe em 10/11/2026.

## Tecnologias e arquitetura

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy, Pydantic e SQLite.
- **Frontend:** HTML, CSS e JavaScript sem framework, servido pelo backend.
- **Relatorios:** PDF gerado com ReportLab.
- **Integracoes:** cliente CRUD Xano mediado pelo backend, cuja configuracao real exige credenciais e recursos externos.
- **Especificacoes:** documentos de produto em `openspec/specs/`, proposals historicas em `openspec/proposals/` e modelos XanoScript em `openspec/xanoscript/`.

## Estrutura principal

- `backend/app/api/`: rotas HTTP da aplicacao.
- `backend/app/core/`: configuracao, banco, migracoes e seguranca.
- `backend/app/models/` e `backend/app/schemas/`: persistencia e contratos de dados.
- `backend/app/services/`: logica de negocio, integracoes, progresso e relatorios.
- `frontend/`: interface web.
- `tests/`: testes automatizados.
- `openspec/`: contexto, especificacoes, proposals e artefatos OpenSpec.

## Dominio e convencoes

- Os dados academicos centrais sao usuarios (`users`), disciplinas (`subjects`) e tarefas (`academic_tasks`).
- Use `snake_case` nos nomes canonicos de tabelas e campos.
- Dados de disciplinas e tarefas devem permanecer isolados por usuario autenticado.
- Mantenha a compatibilidade entre os modelos, schemas, rotas, servicos e frontend.
- Prefira mudancas pequenas, tipadas e cobertas por testes; nao introduza dependencias sem necessidade.
- Nao registre segredos ou credenciais. A configuracao de integracoes deve vir do ambiente.

## Comandos uteis

- Instalar dependencias do backend: `pip install -r backend/requirements.txt`
- Iniciar a aplicacao: `python run_server.py`
- Executar testes: `python -m pytest`

Os testes locais nao comprovam a conexao com contas reais Google ou Xano. Consulte `COMO_FINALIZAR_A_CONFIGURACAO.md` antes de fazer verificacoes ponta a ponta dessas integracoes.

