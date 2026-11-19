## ADDED Requirements

### Requirement: Authenticated CRUD mediation
O sistema SHALL exigir JWT no backend para CRUD de matérias e tarefas e SHALL verificar a propriedade atual e da nova disciplina antes de alterar dados.

#### Scenario: Transferência entre usuários
- **WHEN** um usuário tenta mover tarefa para disciplina de outro aluno
- **THEN** a operação é recusada sem alteração do registro

### Requirement: Complete transactional mirror
O espelho SHALL rejeitar respostas inválidas e paginação incompleta antes de alterar dados e SHALL aplicar alterações atomicamente.

#### Scenario: Página remota inválida
- **WHEN** a listagem remota é truncada ou incompatível
- **THEN** os registros locais são preservados e a falha é informada

### Requirement: Explicit identity binding
O sistema SHALL guardar um vínculo persistente para o aluno Xano e SHALL NOT assumir propriedade de registro preexistente apenas por e-mail ou nome.

#### Scenario: E-mail de aluno preexistente
- **WHEN** uma conta local sem vínculo encontra aluno remoto com o mesmo e-mail
- **THEN** o sistema solicita vinculação administrativa verificada sem retornar os dados acadêmicos

### Requirement: Overdue subject search
A busca SHALL combinar texto OU disciplinas com tarefas de prazo vencido e não concluídas, limitada ao usuário autenticado.

#### Scenario: Tarefa concluída vencida
- **WHEN** uma tarefa concluída tem prazo no passado
- **THEN** ela não é considerada atrasada

### Requirement: Shared progress and report contracts
O sistema SHALL oferecer script de cálculo com JSON percentage e relatório PDF autenticado usando os dados sincronizados do usuário.

#### Scenario: Nenhuma tarefa
- **WHEN** o script recebe lista vazia
- **THEN** retorna percentage igual a zero
