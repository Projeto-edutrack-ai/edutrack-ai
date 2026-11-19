# Spec Delta

## Purpose

Permitir que professores registrem notas associadas a alunos e atividades específicas, preservando a autorização individual antes de qualquer gravação.

## ADDED Requirements

### Requirement: Grade is associated with a specific student activity
O sistema SHALL armazenar cada nota vinculada à atividade e ao aluno correspondentes, sem usar o nome textual de um professor como identidade ou vínculo de autorização.

#### Scenario: Grade stored for the selected student and activity
- **WHEN** uma nota é lançada para um aluno em uma atividade específica
- **THEN** o registro persistido permanece associado àquele aluno e àquela atividade

### Requirement: Grade submission requires teacher authorization
O sistema SHALL verificar no backend a identidade autenticada do professor e sua autorização para avaliar o aluno na atividade indicada antes de criar ou alterar uma nota.

#### Scenario: Authorized teacher submits a grade
- **WHEN** um professor autenticado tem identidade verificável e autorização para avaliar o aluno na atividade indicada
- **THEN** o sistema armazena a nota para esse aluno e essa atividade

#### Scenario: Teacher identity or authorization cannot be verified
- **WHEN** a identidade do professor ou sua autorização para a atividade e o aluno não pode ser verificada
- **THEN** o sistema recusa a operação e não cria nem altera uma nota
