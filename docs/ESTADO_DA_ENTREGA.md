# Estado da entrega — 15/11/2026

## Funcionalidades conferidas
Cadastro/login, conexão com Xano protegido por chave de servidor, CRUD de matéria, edição/conclusão de tarefa, cronômetro, progresso, PDF, busca por nome/atraso/OR e bloqueio de leitura de registros da primeira conta pela segunda no FastAPI. Correções locais passaram em 83 testes Python e 11 JavaScript antes da preparação do clone.

## Pendências para as atividades
- Instalação/configuração Git no notebook, commits/branches/PRs reais e entrega dos links/prints.
- Pesquisa prática de dois templates Figma, referências/reflexão e assets.
- Demonstração do agente lendo AGENTS e proposta de teste de notas.
- Endpoints de busca e relatório iniciados no próprio Xano, serviço Python acessível por HTTPS e ligação de retorno/arquivo. Estão funcionando pela interface FastAPI local, o que não substitui essa etapa literal das atividades 14 e 15.
- Conferência do requisito literal de autorização por usuário no Xano: CRUD atual é interno por chave de serviço; autenticação e propriedade por aluno ficam no FastAPI. JWT FastAPI não é presumido válido como JWT nativo Xano.
- Auditoria final de propostas, relatório pessoal do grupo e PR final aberto para o professor.

Professor autorizou Antigravity em lugar de FlutterFlow e nomes em português no Xano. Não são necessárias tabelas duplicadas em inglês nem integração Classroom.

## Privacidade e dados
Não versionar .env, SQLite, pastas .venv/node_modules, tokens, credenciais ou export bruto Xano com token de documentação. O diretório xano/ contém somente fontes sanitizadas para revisão; workspace original preservado fora do repositório. PDF real, screenshots e dados pessoais devem ser entregues separadamente conforme a atividade.

Não marcar todas as 16 atividades como concluídas com base apenas no funcionamento do site.
