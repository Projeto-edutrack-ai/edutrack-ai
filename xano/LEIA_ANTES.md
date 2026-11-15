# Xano: pacote limitado à revisão acadêmica

## O que foi confirmado
Foram recebidos 63 documentos XanoScript. Os relacionamentos materias.alunos_id -> alunos e tarefas.materias_id -> materias estão declarados corretamente. Os nomes em português foram autorizados pelo professor. Há uma tabela nativa user com autenticação; ela não está vinculada automaticamente aos alunos nem ao JWT do FastAPI.

Os quinze endpoints do grupo acadêmico estão públicos no export original. Existe uma função auth/validate_api_key, mas eles não a chamam. O DELETE real retorna null, aceito pelo cliente Python. O PATCH original descartava null e texto vazio, impedindo remover prazo/descrição.

## Mudança local de autorização por usuário
O diretório deploy agora também contém a definição local de alunos com `int? user_id?` (campo opcional e anulável, sem valor padrão nem atribuição automática), seu índice único, a definição `api_group.xs` de `edutrack privado` e cinco novos endpoints em `GET`/`POST /privado/materias` e `GET`/`PATCH`/`DELETE /privado/materias/{materias_id}`. O GUID existente da tabela alunos foi preservado; os endpoints novos receberam GUIDs locais exclusivos. A documentação oficial do Xano não especifica se o índice único aceita vários valores `NULL`; isso precisa ser validado em workspace isolado antes de afirmar essa garantia. A preservação efetiva dos registros existentes também depende de validação da migração. Os arquivos não foram compilados, publicados nem testados no workspace Xano.

O novo grupo não substitui nem migra os quinze endpoints existentes. O aplicativo atual continua usando a integração FastAPI; as rotas atuais com chave de servidor continuam dependendo do FastAPI para autorização individual. O procedimento administrativo de vínculo e a matriz para futuros testes reais estão em PROCEDIMENTO_VINCULO_TESTES_MATERIAS.md.

## Diretórios
- deploy/: 15 endpoints existentes, a função existente auth/validate_api_key, a definição local atualizada de alunos e cinco novos endpoints no grupo privado.
- reference/table/: três schemas originais, para documentação; não exigem migração.
- O pacote não contém export completo nem metadados do grupo remoto, token Swagger, .env ou registros pessoais. O grupo `edutrack privado` descrito acima é somente a definição local nova.

## Antes de qualquer push
1. Configure uma variável secreta XANO_API_KEY no workspace, sem colocar o valor no código.
2. No .env do backend, configure XANO_CRUD_AUTH_HEADER=X-API-Key e XANO_CRUD_AUTH_VALUE com exatamente o mesmo segredo. A variável de ambiente remota e a configuração local têm nomes diferentes por função.
3. Confirme que está na instância correta e no workspace 147367. Não presuma que o perfil CLI continua apontando para ele.
4. Na raiz deste projeto, rode apenas a prévia:

```powershell
xano.cmd workspace push -w 147367 -d ./xano/deploy --dry-run
```

Confira que a prévia contém os quinze endpoints existentes, a função de validação existente, a atualização de alunos e os cinco endpoints do novo grupo privado, sem objetos não relacionados. Se aparecer erro de sintaxe, criação inesperada, remoção, alteração dos endpoints existentes ou outro objeto, pare e revise. Esta mudança local não foi validada pelo compilador remoto do Xano. O assistente não executou push, dry-run, deploy ou alterações no workspace.

Depois da revisão e com o backend já preparado, o comando sem --dry-run envia os arquivos. Nunca acrescente --delete, --truncate, --env ou --records. Este pacote não foi enviado remotamente pelo assistente.

## Testes após aplicação
- Para as rotas atuais em `edutrack teste`, testar a chave de servidor ausente/incorreta e a operação pelo FastAPI com autorização individual; PATCH com prazo:null e descricao:"" deve limpar os campos.
- Para o novo grupo `edutrack privado`, seguir a matriz em PROCEDIMENTO_VINCULO_TESTES_MATERIAS.md. Essas verificações de `auth = "user"` e `$auth.id` ainda não foram executadas no workspace.
- Não confundir o grupo novo com migração: as rotas atuais permanecem protegidas por chave de serviço no Xano e dependem do FastAPI para autorização individual.

## Não altera o restante do workspace
Há tabelas/funções/endpoints antigos de Classroom e objetos de outros projetos no workspace recebido. Não são necessários ao aplicativo atual, mas não serão apagados automaticamente: o workspace é compartilhado e o export não inclui registros ou todas as dependências de consumidores externos. Se continuarem publicados, devem ser revisados separadamente. Nenhuma integração Google foi reintroduzida no aplicativo.

## Ainda pendente
Busca e relatório iniciados por endpoints Xano, deploy HTTPS do Python, integração real, validação do novo schema e das APIs no workspace, testes de autorização nativa e qualquer publicação. Não declarar atividades 13, 14 e 15 como concluídas apenas por criar estes arquivos locais.
