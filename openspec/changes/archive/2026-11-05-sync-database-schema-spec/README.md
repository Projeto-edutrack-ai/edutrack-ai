# sync-database-schema-spec

Sincronizar a especificação do banco de dados relacional (`openspec/specs/database-schema.md`) com as colunas reais implementadas de integração Google Classroom / Xano, e validar todos os critérios de entrega do projeto para gravação do vídeo demonstrativo.

## Intenção

Garantir que a documentação técnica de arquitetura de dados e os critérios acadêmicos de entrega estejam rigorosamente alinhados com o código-fonte, banco de dados e testes da aplicação.

## Tarefas

- [x] Validar suíte de testes automatizados completa (`python -m pytest`) - 84 testes aprovados.
- [x] Testar os 7 módulos funcionais exigidos na entrega: Login, Esqueci minha senha, Cadastro de usuário, IA, Relatório, Disciplina e Tarefas.
- [x] Atualizar `openspec/specs/database-schema.md` com as colunas e índices de integração Google Classroom (`source`, `classroom_course_id`, `classroom_link`, `classroom_synced_at`, `classroom_coursework_id`, `max_points`, `classroom_submission_state`).
- [x] Detalhar comparativo entre a primeira versão (`edutrack-ai`) e a versão atual (`edutrack`) para embasamento no vídeo e OpenSpec.
- [x] Estruturar roteiro guiado para o vídeo cobrindo funcionalidades, banco de dados/modelo e estrutura do GitHub/OpenSpec.

## Validação

Validação executada em 2026-11-05:
- 84 testes passando em `python -m pytest`.
- Todos os endpoints backend e componentes de frontend testados e operacionais.
- Validação OpenSpec confirmada via `openspec validate --all --json`.
