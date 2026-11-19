# Change: document-python-progress-activity12

## Why

O contrato de uso de `scripts/calculate_progress.py` precisa estar documentado de forma verificável para a atividade 12, sem recriar nem alterar o script. A documentação também distinguirá os resultados manuais informados pela aluna de testes executados nesta change.

## What Changes

- Documentar a entrada do script: argumento `--tasks` com uma lista JSON ou lista JSON lida de stdin, com status `pending`, `in_progress` ou `completed`.
- Documentar a saída JSON `percentage`, o cálculo baseado na proporção de tarefas concluídas e o resultado para uma lista vazia.
- Registrar como verificação manual informada pela aluna os casos `completed` + `pending` → `{"percentage": 50.0}` e lista vazia → `{"percentage": 0.0}`.
- Não recriar, editar ou executar o script; não alterar testes, proposals históricas nem pendências de outras atividades.

## Capabilities

### New Capabilities

- `task-completion-percentage`: contrato da entrada e do percentual JSON calculado para uma lista de tarefas.

### Modified Capabilities

Nenhuma.

## Impact

Somente os artefatos OpenSpec desta change serão adicionados. O contrato detalhado não substituirá nem modificará a capability `academic-security` ainda delta de outra change ativa; suas tarefas e pendências serão preservadas.
