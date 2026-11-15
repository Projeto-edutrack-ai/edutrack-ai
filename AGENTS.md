# Instrucoes para agentes de IA

## Contexto do projeto

EduTrack AI e uma aplicacao educacional com backend FastAPI, banco SQLite, frontend em HTML/CSS/JavaScript e integração acadêmica com Xano. O contexto, a arquitetura e as convencoes do projeto estao em `openspec/project.md`.

## Como trabalhar neste repositorio

- Sempre que uma IA for alterar arquivos do projeto, registre o trabalho no OpenSpec antes de implementar: crie uma nova change pela CLI ou atualize uma change ativa que corresponda exatamente ao mesmo escopo. Isso vale tambem para correcoes pequenas e alteracoes de documentacao; nao use uma change sem relacao apenas para evitar criar outra.
- Na change, descreva a intencao, os criterios de conclusao e as tarefas. Ao terminar, atualize as tarefas com o resultado real e sincronize as especificacoes afetadas. Nao declare como concluido algo que nao foi implementado ou validado.
- Para registrar a mudanca, siga `openspec/AGENTS.md` e use os comandos/workflows OpenSpec instalados. Nao crie manualmente diretorios de change nem altere proposals historicas como se fossem um diario de execucao.
- Antes de alterar codigo, leia os arquivos relacionados e preserve o comportamento existente.
- Mantenha a separacao atual entre `backend/app/api`, `backend/app/models`, `backend/app/schemas`, `backend/app/services` e `frontend`.
- Para mudancas de comportamento, mantenha codigo, testes e documentacao diretamente relacionada em sincronia.
- Nao inclua credenciais, tokens, chaves ou dados pessoais reais em codigo, testes ou documentacao.
- Nao substitua ou apague dados de bancos existentes como parte de testes. Use as fixtures e o banco de teste definidos em `tests/` e `pytest.ini`.
- Para mudancas de requisitos ou funcionalidades, siga o fluxo e as convencoes descritos em `openspec/AGENTS.md`.

## Validacao

- Backend e testes: `python -m pytest`
- Ao alterar integracoes ou configuracao externa, diferencie claramente testes locais de verificacoes que exigem contas ou credenciais reais.
- Execute as verificacoes relevantes para a alteracao e informe qualquer limitacao ou falha preexistente.

## Decisões atuais (10/11/2026)
- Antigravity substitui FlutterFlow com autorização do professor.
- Google Classroom foi removido: não reintroduza OAuth, rotas ou tabelas dessa integração.
- Apenas alunos, materias e tarefas são necessários no Xano; autenticação e tokens de recuperação continuam no backend local.
- Todo CRUD de navegador passa pelo FastAPI autenticado. Não coloque chaves Xano no frontend.
- Não associe uma conta remota preexistente só por coincidência de e-mail. Use vínculo persistente/administração verificada.
- Não trate resposta remota inválida como lista vazia nem apague dados para corrigir sincronização.
