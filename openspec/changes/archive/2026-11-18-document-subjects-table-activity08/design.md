# Registro da tabela de disciplinas

A proposta histórica 001 descreve a tabela subjects com nome, professor, carga horária e vínculo ao usuário. O modelo Subject em backend/app/models/subject.py declara a tabela local subjects. O schema canônico aparece em openspec/xanoscript/schema_subjects.xs. No contrato exportado em xano/reference/table/materias.xs, a tabela se chama materias e sua coluna alunos_id referencia alunos. A matriz openspec/tasks.md registra a modelagem de disciplinas no item TASK-004.

Conferência realizada sobre a revisão a428c29. O arquivamento documenta a implementação preexistente. Não houve criação de tabela no servidor nem nova execução no Xano durante essa conferência.
