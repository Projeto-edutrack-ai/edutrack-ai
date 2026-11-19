# task-completion-percentage Specification

## Purpose

Documentar o contrato observável do cálculo do percentual de conclusão a partir de uma lista de tarefas, incluindo entrada, saída JSON e lista vazia.

## Requirements

### Requirement: CLI accepts and validates task status input
O script SHALL aceitar uma lista JSON de tarefas por `--tasks` ou por stdin quando `--tasks` não for informado. Cada item SHALL ser um objeto cujo `status` seja `pending`, `in_progress` ou `completed`; entrada inválida SHALL produzir erro JSON em stderr e código de saída 2.

#### Scenario: Valid task list is provided
- **WHEN** o script recebe uma lista JSON de objetos com status permitidos por `--tasks` ou stdin
- **THEN** a lista é aceita para calcular o percentual de conclusão

#### Scenario: Invalid task list is provided
- **WHEN** o script recebe JSON que não seja uma lista de objetos com status permitidos
- **THEN** escreve um objeto JSON de erro em stderr e termina com código 2

### Requirement: CLI returns completion percentage as JSON
O script SHALL escrever em stdout um objeto JSON com a chave `percentage`, calculado como a proporção de tarefas `completed` sobre o total e arredondado a uma casa decimal; uma lista vazia SHALL resultar em `0.0`.

#### Scenario: One completed task and one pending task
- **WHEN** a entrada contém uma tarefa `completed` e uma tarefa `pending`
- **THEN** stdout contém `{"percentage": 50.0}`

#### Scenario: Empty task list
- **WHEN** a entrada é uma lista vazia
- **THEN** stdout contém `{"percentage": 0.0}`
