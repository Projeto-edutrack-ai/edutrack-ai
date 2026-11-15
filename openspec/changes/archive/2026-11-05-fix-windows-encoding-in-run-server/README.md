# fix-windows-encoding-in-run-server

Garantir suporte seguro à codificação UTF-8 no console do Windows ao executar `run_server.py`.

## Intenção

Evitar `UnicodeEncodeError` ao imprimir caracteres e emojis no prompt padrão do Windows (cp1252), reconfigurando `sys.stdout` e `sys.stderr` para UTF-8.

## Tarefas

- [x] Configurar reconfiguração de encoding para UTF-8 em `run_server.py`.
- [x] Testar inicialização do servidor e validação com `openspec validate`.

## Validação

Testado em Windows PowerShell com sucesso.
