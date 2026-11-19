# Aplicar complemento sem perder configuração

1. No terminal do servidor, pressione Ctrl+C uma vez.
2. Extraia correcao_limite_xano.zip.
3. Copie as pastas backend, frontend, tests, openspec e docs e o package.json do complemento para a raiz do projeto atual (ao lado de run_server.py). Mescle pastas e substitua somente os arquivos de mesmo nome.
4. Preserve .env, .venv, edutrack.db e xano_export. Não apagar a pasta do projeto nem substituir o banco.
5. Inicie: .\.venv\Scripts\python.exe run_server.py
6. Deixe cerca de 30 segundos sem novas tentativas antes de reabrir a interface, para liberar eventual janela de bloqueio anterior. Atualize com Ctrl+Shift+R uma vez.
7. Aguarde carregar; leituras não atendidas pelo cache são espaçadas. Não refaça cadastros antigos para testar consulta. Confira primeiro a lista e os IDs já gravados.

Não há alterações Xano para enviar nesta correção. A configuração X-API-Key permanece a mesma. O arquivo frontend/js/auth.js inclui a remoção da chamada bindProfileEvents inexistente.

O complemento compartilha GETs recentes por até 30s, invalida após escritas, não retenta escritas e aplica pausa após 429. Mantém autorização por aluno no FastAPI. Na falha de atualização a interface mantém os cards existentes com aviso; não afirma que dados antigos são uma atualização nova.

A instância gratuita possui limite compartilhado. Este limitador é em memória por processo, adequado ao servidor local; múltiplos workers exigem coordenação externa. Nenhum registro remoto foi apagado pelo assistente. As duas matérias de teste observadas devem ser conferidas antes de excluir uma delas.
