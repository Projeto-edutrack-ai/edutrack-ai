# Design

Apenas registros com referência inteira positiva são candidatos à filtragem de propriedade. Referências inválidas de registros que nunca foram espelhados para o usuário são ignoradas. Se o mesmo xano_id já pertence ao espelho local do usuário, falhar antes de qualquer mutação: referência ausente não significa exclusão. IDs de registros continuam obrigatórios/únicos e paginação continua completa. Outros alunos válidos são filtrados por owner/subject_ids como antes.

Na falha de atualização após escrita remota confirmada, manter o código HTTP da falha e informar ID gravado sem retentar escrita automaticamente. Este ajuste não implementa idempotência de POST.
