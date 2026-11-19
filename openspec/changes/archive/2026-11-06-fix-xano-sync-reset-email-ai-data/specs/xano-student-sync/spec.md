## ADDED Requirements

### Requirement: Student record in Xano
O sistema SHALL garantir um registro na tabela `alunos` do Xano, localizado por e-mail, no cadastro e no login, sem duplicar registros, e SHALL informar o resultado da sincronização.

#### Scenario: Novo cadastro
- **WHEN** um aluno cria conta
- **THEN** o backend cria o registro em `alunos` e devolve o `xano_aluno` na resposta

#### Scenario: Xano indisponível
- **WHEN** o Xano não responde durante o cadastro
- **THEN** a conta local é criada e a resposta informa `xano_sync.status = "failed"` com o motivo

### Requirement: Analytics from Xano data
O sistema SHALL espelhar as disciplinas e tarefas do aluno no SQLite antes de calcular analytics, insights de IA e relatório PDF, preservando o tempo de estudo local.

#### Scenario: Aluno com dados no Xano
- **WHEN** o aluno tem disciplinas e tarefas apenas no Xano e abre Insights
- **THEN** as métricas e a IA refletem essas disciplinas e tarefas
