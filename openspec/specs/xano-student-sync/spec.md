# xano-student-sync Specification

## Purpose

Definir a ligação entre contas locais e alunos remotos e a sincronização dos dados acadêmicos utilizados pelo dashboard, mentor e relatórios do EduTrack.

## Requirements

### Requirement: Student record in Xano
O sistema SHALL usar vínculo persistente entre conta local e aluno Xano, SHALL informar o resultado da sincronização e SHALL NOT conceder acesso a registro preexistente apenas por coincidência de e-mail. Novos registros criados pelo backend são vinculados à conta; registros antigos exigem verificação administrativa.

#### Scenario: Novo cadastro
- **WHEN** um aluno cria conta
- **THEN** o backend cria o registro em `alunos` e devolve o `xano_aluno` na resposta

#### Scenario: Xano indisponível
- **WHEN** o Xano não responde durante o cadastro
- **THEN** a conta local é criada e a resposta informa `xano_sync.status = "failed"` com o motivo

### Requirement: Analytics from Xano data
O sistema SHALL espelhar um conjunto completo e validado de disciplinas e tarefas do aluno no SQLite antes de calcular analytics, insights de IA e relatório PDF, preservando o tempo local. Uma falha de leitura SHALL ser informada, sem ser tratada como lista vazia ou sucesso atualizado. No modo Xano, registros locais/de demonstração não integram as métricas remotas.

#### Scenario: Aluno com dados no Xano
- **WHEN** o aluno tem disciplinas e tarefas apenas no Xano e abre Insights
- **THEN** as métricas e a IA refletem essas disciplinas e tarefas
