# Correção da sincronização

A matéria 12 sem aluno válido impedia atualizar o espelho de outra conta. O complemento ajusta o filtro sem apagar/reatribuir dados e mantém a proteção de registros locais conhecidos. Não há alterações Xano ou novas dependências.

Com o servidor parado e o ZIP em D:\Downloads, execute no PowerShell:

```powershell
Expand-Archive -LiteralPath "D:\Downloads\correcao_sincronizacao.zip" -DestinationPath "D:\Downloads\edutrack1_corrigido\edutrack1_corrigido" -Force
```

Depois inicie normalmente com .\.venv\Scripts\python.exe run_server.py. Atualize o navegador e confira as tarefas 53/54 existentes sem novo cadastro. O pacote não contém .env, credenciais ou banco.
