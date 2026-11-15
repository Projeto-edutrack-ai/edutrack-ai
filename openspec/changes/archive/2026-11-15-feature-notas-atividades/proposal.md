# Change: feature-notas-atividades

## Why

Esta proposta é exclusivamente um exercício da atividade 10 e será arquivada sem implementação. As tarefas documentam trabalho futuro e permanecerão desmarcadas; esta proposta não autoriza implementar a funcionalidade.

Professores precisam registrar notas associadas a alunos e atividades específicas, mas o sistema atual não define uma funcionalidade de lançamento de notas nem uma identidade de professor autorizada. A change estabelece esse comportamento sem presumir como professores são identificados no contrato atual.

## What Changes

- Definir o armazenamento de uma nota vinculada a um aluno e a uma atividade específica.
- Definir o lançamento da nota por um professor autenticado, com verificação de autorização no backend antes de persistir qualquer alteração.
- Registrar como decisão em aberto a identidade confiável do professor e a relação que determina quais alunos e atividades ele pode avaliar.
- Restringir o escopo a armazenamento e lançamento de notas; não incluir boletins, cálculos de médias, relatórios ou gestão geral de atividades.

## Capabilities

### New Capabilities

- `activity-grades`: armazenar e lançar notas de alunos em atividades específicas com autorização.

### Modified Capabilities

Nenhuma.

## Impact

A implementação futura deverá considerar persistência, validação de domínio, autenticação/autorização no backend, contratos e testes. O modelo atual autentica usuários, mas não define papéis de professor nem vínculo de autorização docente; o campo textual `subjects.professor` não constitui uma identidade verificável. Este artefato planeja o comportamento e não cria tabelas, endpoints ou código.
