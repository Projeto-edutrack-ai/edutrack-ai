# Xano: pacote limitado à revisão acadêmica

## O que foi confirmado
Foram recebidos 63 documentos XanoScript. Os relacionamentos materias.alunos_id -> alunos e tarefas.materias_id -> materias estão declarados corretamente. Os nomes em português foram autorizados pelo professor. Há uma tabela nativa user com autenticação; ela não está vinculada automaticamente aos alunos nem ao JWT do FastAPI.

Os quinze endpoints do grupo acadêmico estão públicos no export original. Existe uma função auth/validate_api_key, mas eles não a chamam. O DELETE real retorna null, aceito pelo cliente Python. O PATCH original descartava null e texto vazio, impedindo remover prazo/descrição.

## Diretórios
- deploy/: somente 15 endpoints existentes e a função existente auth/validate_api_key, com GUIDs preservados.
- reference/table/: três schemas originais, para documentação; não exigem migração.
- Não há documento de workspace, grupo de API, token Swagger, .env ou registros pessoais neste pacote.

## Antes de qualquer push
1. Configure uma variável secreta XANO_API_KEY no workspace, sem colocar o valor no código.
2. No .env do backend, configure XANO_CRUD_AUTH_HEADER=X-API-Key e XANO_CRUD_AUTH_VALUE com exatamente o mesmo segredo. A variável de ambiente remota e a configuração local têm nomes diferentes por função.
3. Confirme que está na instância correta e no workspace 147367. Não presuma que o perfil CLI continua apontando para ele.
4. Na raiz deste projeto, rode apenas a prévia:

```powershell
xano.cmd workspace push -w 147367 -d ./xano/deploy --dry-run
```

Confira que a prévia contém somente os quinze endpoints existentes e a função de validação existente. Se aparecer erro de sintaxe, criação de tabela, remoção, troca de grupo ou outro objeto, pare e revise. Este código foi inspecionado localmente, mas não foi validado pelo compilador remoto do Xano.

Depois da revisão e com o backend já preparado, o comando sem --dry-run envia os arquivos. Nunca acrescente --delete, --truncate, --env ou --records. Este pacote não foi enviado remotamente pelo assistente.

## Testes após aplicação
- Sem X-API-Key ou com chave errada: negar antes do banco.
- Pelo backend com a chave correta: criar, listar, editar e excluir registros de teste.
- PATCH com prazo:null e descricao:"": deve limpar os campos.
- No site, testar duas contas e IDs cruzados.
- Conferir explicitamente se a exigência de autenticação por usuário no próprio Xano está atendida: esta primeira correção bloqueia o público e mantém autorização por aluno no FastAPI; não implementa auth.id nativo no Xano. Quem possui a chave de serviço tem acesso administrativo ao grupo.

## Não altera o restante do workspace
Há tabelas/funções/endpoints antigos de Classroom e objetos de outros projetos no workspace recebido. Não são necessários ao aplicativo atual, mas não serão apagados automaticamente: o workspace é compartilhado e o export não inclui registros ou todas as dependências de consumidores externos. Se continuarem publicados, devem ser revisados separadamente. Nenhuma integração Google foi reintroduzida no aplicativo.

## Ainda pendente
Busca e relatório iniciados por endpoints Xano, deploy HTTPS do Python, integração real, segurança por usuário nativa exigida literalmente e testes da prévia. Não declarar atividades 13, 14 e 15 como concluídas apenas por aplicar este pacote.
