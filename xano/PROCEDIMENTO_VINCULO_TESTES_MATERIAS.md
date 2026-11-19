# Vínculo administrativo e testes do CRUD privado de matérias

## Situação local

Os arquivos desta mudança são locais e ainda não foram compilados, publicados ou testados no workspace Xano. O novo grupo `edutrack privado` não integra o login, o frontend ou o FastAPI atuais. As rotas existentes com chave de servidor permanecem separadas e dependem do FastAPI para autorização individual.

O campo `alunos.user_id` é opcional e único. Este pacote não cria contas, preenche vínculos, associa registros automaticamente nem altera registros acadêmicos existentes.

## Procedimento de vínculo administrativo

Execute somente em workspace autorizado, com operador administrativo e após aprovação da equipe:

1. Identifique o registro `alunos` correto por meio do vínculo persistente já verificado entre a conta local e o aluno. Não use igualdade entre IDs como prova.
2. Peça à pessoa que comprove controle da conta local pela sessão autenticada existente e controle da conta Xano por login nativo separado. Confirme a identidade Xano pelo contexto autenticado da conta; não confie em email coincidente ou em um ID informado pela pessoa.
3. Confirme que as duas comprovações apontam para a mesma pessoa e que o aluno ainda não está vinculado a outro usuário. Se houver dúvida, divergência ou falha de comprovação, interrompa e deixe `user_id` sem vínculo.
4. Um administrador autorizado registra manualmente o `user.id` comprovado no `alunos.user_id` correspondente. Não crie endpoint de vínculo nem execute atualização em lote para este procedimento.
5. Registre operador, data, motivo e referência interna da aprovação no mecanismo de auditoria aprovado pela equipe, sem armazenar tokens, senhas ou evidências pessoais neste repositório.
6. Revise que somente o vínculo aprovado foi alterado e que os alunos sem vínculo continuam sem associação.

## Plano de testes reais futuros

Os testes devem ocorrer somente depois de revisão humana e validação Xano, em um workspace de teste isolado e autorizado, nunca contra dados acadêmicos de produção. A equipe prepara duas contas de teste controladas e dois registros de aluno de teste; esta mudança não cria essas contas nem esses registros.

No grupo `edutrack privado`, use estes caminhos:

| Operação | Rota |
|---|---|
| Listar | `GET /privado/materias` |
| Criar | `POST /privado/materias` |
| Ler | `GET /privado/materias/{materias_id}` |
| Alterar | `PATCH /privado/materias/{materias_id}` |
| Excluir | `DELETE /privado/materias/{materias_id}` |

1. Vincule administrativamente a conta A ao aluno A usando o procedimento acima. Obtenha um token por login nativo Xano em tempo de execução; não salve senha ou token em arquivo, fixture, commit, log ou evidência.
2. Mantenha inicialmente a conta B sem `alunos.user_id`. Execute os casos sem vínculo e confirme que nenhuma operação expõe nem altera registros.
3. Vincule manualmente a conta B ao aluno B, distinto do aluno A. Obtenha seu token também por login nativo Xano em tempo de execução.
4. Execute a matriz abaixo para cada token e também sem token. Repita as operações de atualização e exclusão com registros descartáveis de teste.
5. Registre somente o ambiente não sensível, método, resultado esperado/observado e falhas. Limpe apenas registros criados pela própria execução no workspace isolado. Não remova nem altere registros preexistentes.

| Operação | Proprietário vinculado | Outra conta vinculada a outro aluno | Conta sem vínculo | Sem token |
|---|---|---|---|---|
| Listar | Retorna somente matérias próprias | Retorna somente matérias próprias, nunca as do outro aluno | Não retorna matérias de terceiros | Negada pela autenticação |
| Criar | Cria a matéria associada ao aluno resolvido pelo `$auth.id` | Cria somente para o próprio aluno | Negada e não cria registro | Negada pela autenticação |
| Ler por ID | Lê matéria própria | Não revela matéria do outro proprietário | Não revela matéria existente | Negada pela autenticação |
| Alterar | Altera matéria própria sem transferir `alunos_id` | Não altera matéria do outro proprietário | Não altera matéria existente | Negada pela autenticação |
| Excluir | Exclui apenas matéria descartável própria | Não exclui matéria do outro proprietário | Não exclui matéria existente | Negada pela autenticação |

Para a criação, tente também enviar um `alunos_id` de outro aluno como campo extra. O endpoint deve rejeitar o campo ou ignorá-lo; em nenhum caso pode associar a matéria ao aluno indicado pelo cliente. Confirme que o vínculo gravado corresponde ao aluno encontrado a partir de `$auth.id`.

## Limite da integração atual

As APIs privadas novas usam autenticação Xano nativa diretamente e não são chamadas pelo aplicativo atual nesta etapa. As rotas existentes que usam chave de servidor continuam dependendo do FastAPI para autenticação JWT e autorização individual; esta mudança não migra nem declara como migrado o CRUD existente.
