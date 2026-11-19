# fix-auth-xano-and-enhance-ai

Sincronizar novos usuários cadastrados com a tabela `alunos` no Xano, tornar o fluxo de "Esqueci minha senha" 100% funcional com redefinição real de senha e validação, e enriquecer a experiência de IA com um Assistente Educacional Interativo.

## Intenção

1. Quando um estudante cria conta no EduTrack (`/auth/register`), garantir a persistência imediata também na tabela `alunos` do Xano.
2. Substituir a simulação com `prompt()` de "Esqueci minha senha" por um modal profissional de Recuperação e Redefinição de Senha funcional com persistência no banco SQLite (`/api/auth/reset-password`).
3. Expandir o papel da IA para além dos diagnósticos analíticos automáticos de desvio de tempo, adicionando um endpoint interativo (`POST /api/ai/ask`) e widget de chat/perguntas com contexto pedagógico real do estudante.

## Tarefas

- [x] Sincronizar criação de novos estudantes no Xano durante o fluxo de cadastro e login no frontend (`api.js`).
- [x] Implementar endpoint de redefinição real de senha no backend (`/api/auth/reset-password`).
- [x] Implementar modal e fluxo visual completo de "Esqueci minha senha" no frontend (`index.html` e `auth.js`).
- [x] Implementar endpoint de Assistente Interativo de IA (`/api/ai/ask`) no backend e interface no frontend de Insights.
- [x] Validar com testes automatizados e aprovar no OpenSpec CLI.

## Validação
- 86 testes automatizados executados e aprovados com `python -m pytest`.
- Validação OpenSpec via `openspec validate`.
