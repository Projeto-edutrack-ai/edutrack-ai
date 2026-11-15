# classroom-removal Specification

## Purpose
Registrar a retirada completa da integração ativa Google Classroom preservando dados importados, metadados de compatibilidade e rastreabilidade histórica do EduTrack.

## Requirements

### Requirement: No Classroom integration
O aplicativo SHALL operar sem botões, chamadas de rede, configuração OAuth ou endpoints de integração Google Classroom.

#### Scenario: Acesso à rota antiga
- **WHEN** um cliente acessa uma rota de integração Classroom
- **THEN** a aplicação retorna 404 e não inicia sincronização externa

### Requirement: Preserve existing academic records
A remoção SHALL preservar registros já importados e SHALL NOT executar exclusão de tabelas, registros ou colunas no banco existente.

#### Scenario: Banco com dados antigos
- **WHEN** a aplicação atualizada abre um banco com disciplinas e tarefas antigas
- **THEN** os registros e metadados legados permanecem armazenados
