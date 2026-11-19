# Design

## Context

Veja [proposal.md](./proposal.md) para a motivação e [specs/activity-grades/spec.md](./specs/activity-grades/spec.md) para o contrato comportamental. Hoje, o backend autentica usuários locais por JWT e filtra atividades e disciplinas pelo `user_id` do usuário autenticado. Esse modelo trata o usuário como aluno; `subjects.professor` é texto livre e não existe papel docente nem relação de autorização entre professor, aluno e atividade.

## Goals / Non-Goals

**Goals:**
- Manter a gravação atrás do backend autenticado, com autorização verificada para o professor, aluno e atividade exatos.
- Persistir cada nota ligada à atividade e ao aluno corretos, sem presumir equivalência entre IDs locais e IDs Xano.
- Falhar de forma fechada quando a identidade docente ou o vínculo de autorização não puder ser verificado.

**Non-Goals:**
- Definir boletins, médias, relatórios, gestão de turmas ou sincronização geral de atividades.
- Usar o texto `subjects.professor`, coincidência de e-mail ou um ID fornecido pelo cliente como prova de identidade ou autorização.
- Escolher silenciosamente o SQLite ou o Xano como fonte de verdade das notas antes de mapear identidades e relações.

## Decisions

- **A autorização é aplicada no backend antes da persistência.** O cliente não determina seu papel nem os vínculos autorizados. A identidade autenticada deve ser resolvida por uma associação confiável e persistente, e a autorização deve cobrir a atividade e o aluno solicitados. Isso preserva a fronteira de segurança existente. Usar apenas os filtros atuais de propriedade do aluno foi considerado, mas não permite autorizar professores.
- **Identidade e vínculo docente são pré-requisitos ainda sem contrato.** O modelo atual não fornece um papel professor ou uma relação professor-aluno-atividade. Até que esses dados e sua validação sejam definidos, uma tentativa de gravação sem identidade e autorização verificáveis deve ser recusada sem persistência. O campo textual da disciplina não é alternativa segura.
- **A nota é conceitualmente associada ao par aluno-atividade.** A persistência não deve alterar o significado nem a propriedade da atividade para acomodar a nota. A forma física de armazenamento e a regra de atualização/histórico dependem das decisões em aberto; não se presume uma nova tabela nem um campo específico neste planejamento.
- **A fonte de verdade permanece em aberto.** SQLite e Xano existem na arquitetura, mas o contrato de notas e os vínculos entre identidades/IDs ainda não foram definidos. Gravar diretamente do navegador ou assumir que IDs locais e remotos coincidem foram descartados.

## Risks / Trade-offs

- **[Sem identidade docente verificável, a funcionalidade não poderá aceitar lançamentos]** → manter a autorização fail-closed e resolver a identidade e os vínculos antes de implementar gravações.
- **[Persistência divergente entre SQLite e Xano pode associar nota ao aluno errado ou perder atualizações]** → escolher uma fonte de verdade e um mapeamento persistente antes de implementar; não converter falhas remotas em sucesso.
- **[Escala e regra de revisão ainda não definidas podem causar notas inválidas ou sobrescritas]** → definir formato, limites, precisão e política de correção/histórico antes de fechar os contratos de entrada e persistência.

## Migration Plan

Esta change contém somente planejamento; nenhuma migração ou alteração de dados será executada nela. Antes da implementação, definir a fonte de verdade, a identidade e os vínculos de autorização, bem como o formato da nota. A implementação deverá usar migração aditiva e reversível conforme os padrões existentes, sem substituir bancos nem apagar registros acadêmicos existentes.

## Open Questions

- Qual identidade autenticada representa um professor, e qual vínculo persistente e verificável comprova que ele pode avaliar determinado aluno e atividade? O contrato atual só define usuários-alunos e não responde a isso.
- As notas serão persistidas no SQLite ou no Xano? Como as identidades e referências de aluno/atividade serão vinculadas sem presumir igualdade entre IDs?
- Qual escala, precisão e limite de nota serão aceitos; a atividade pode ter pontuação máxima? Uma nova submissão substitui a nota anterior ou mantém histórico de correções?

Estas decisões são pré-requisitos para a implementação e devem ser resolvidas antes de criar contratos de gravação ou persistência.
