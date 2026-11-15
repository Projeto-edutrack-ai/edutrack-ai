# Aplicar com segurança no projeto da equipe

1. Extraia o pacote em uma pasta nova e teste pelo README.
2. Preserve a versão atual do repositório, o banco real e o .env. O pacote não contém banco nem credenciais.
3. Abra o repositório atualizado do grupo, confira git status e crie uma branch chore/adequacao-edutrack1.
4. Compare o patch fornecido com essa versão. Execute git apply --check CAMINHO/ALTERACOES_EDUTRACK1.patch antes de aplicar. Se falhar, compare manualmente em vez de forçar.
5. Após conferir o diff, aplique o patch, instale dependências e execute os testes.
6. Faça commit, envie a branch e abra PR para revisão do grupo. Nenhum push foi realizado nesta sessão.
7. Configure o Xano conforme COMO_FINALIZAR_A_CONFIGURACAO.md e faça testes reais antes de publicar.

Não copie por cima de um repositório com mudanças novas da equipe nem descarte o banco existente para resolver erros.
