# Configuração Xano — três tabelas, sem Classroom

## Contrato confirmado
A usuária forneceu o OpenAPI 3.0.0 do grupo `edutrack teste`, versão 0.0.1, em 10/11/2026. URL base:
https://x8ki-letl-twmt.n7.xano.io/api:d_CNfVCs

| Tabela | Campos do contrato |
|---|---|
| alunos | id automático, created_at automático, nome text, email email, curso text, semestre integer |
| materias | id, created_at, alunos_id integer, nome text, professor text, descricao text, carga_horaria integer |
| tarefas | id, created_at, materias_id integer, titulo_ text, descricao text, prazo timestamp nullable, status enum |

Relações: materias.alunos_id -> alunos.id; tarefas.materias_id -> materias.id. Os relacionamentos foram confirmados nos schemas reais exportados em 15/11/2026.

Status exatos: `pendente`, `em_andamento ` (tem espaço no final), `concluida`. Não renomeie campos ou o enum sem atualizar o contrato e o aplicativo. O adaptador normaliza status para o motor Python, mas grava o valor exato aceito no Xano.

GET/POST /alunos, /materias e /tarefas; GET/PATCH/DELETE nas rotas /{tabela}/{id}. Listas são arrays puros. POST/PATCH retornam o objeto; O export real confirma DELETE com resposta null; o cliente aceita esse retorno. Não há autenticação exigida em nenhuma dessas operações no documento recebido.

## 1. Proteger o grupo no Xano antes de publicar
O backend local agora verifica JWT e propriedade de cada registro. Isso NÃO torna as URLs antigas do Xano privadas. É preciso bloqueá-las também no workspace.

Como o login permanece no Python, pode usar uma chave exclusiva de servidor, sem criar tabela de autenticação no Xano:
1. Gere uma chave forte no computador: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
2. Guarde a chave em uma variável de ambiente secreta no workspace Xano.
3. Em TODOS os endpoints existentes (inclusive GET, POST, PATCH e DELETE de alunos/materias/tarefas), adicione uma verificação antes de ler ou alterar o banco: o cabeçalho Authorization recebido deve ser igual ao valor secreto esperado. Use uma precondition; se não corresponder, retorne erro não autorizado.
4. Aplique a proteção também a cópias antigas dos endpoints que continuem publicadas. CORS sozinho não é autenticação.
5. Configure XANO_CRUD_AUTH_VALUE no .env do Python com o valor completo que o Xano compara. Se comparar `Bearer SEGREDO`, guarde exatamente `Bearer SEGREDO` nos dois lados. XANO_CRUD_AUTH_HEADER=Authorization é o padrão; pode usar outro cabeçalho se configurado igualmente no workspace.
6. Teste sem chave (deve negar acesso) e com a chave no backend (deve funcionar). Não exponha a chave no navegador, nos prints ou no Git.

Essa estratégia segue a orientação oficial sobre API keys e verificação de cabeçalho: https://www.xano.com/learn/securing-xano-apis/ . As ações do workspace ainda precisam ser executadas pela equipe; não foram feitas nesta sessão. O bearer JWT do login FastAPI NÃO é presumido válido como JWT nativo do Xano.

## 2. Ativar a fonte remota
Depois da proteção, preencha XANO_CRUD_BASE_URL com a URL acima e XANO_CRUD_AUTH_VALUE no .env. Reinicie o servidor. URL vazia mantém o modo local; URL preenchida seleciona Xano e erros remotos são apresentados, sem substituir o resultado por dados demo.

## 3. Vincular contas antigas sem tomar conta de dados por e-mail
O backend adiciona colunas locais xano_aluno_id e xano_binding_base. Novos registros remotos criados pelo próprio cadastro são vinculados automaticamente. Se o e-mail já existir no Xano, retorna link_required; isso não é defeito nem pedido para apagar o aluno.

Após a equipe verificar que a conta local e o aluno remoto pertencem à mesma pessoa, use em um terminal administrativo do servidor:
`python scripts/link_xano_student.py --local-user-id ID_LOCAL --xano-aluno-id ID_XANO`

O comando acima é uma simulação. Confira os IDs e a identidade; só então acrescente `--apply` para gravar. Não exponha esse comando como endpoint público. IDs de SQLite e Xano não são presumidos iguais. Preserve o banco local; ele contém contas, tokens e tempos de estudo.

## 4. Dados de tempo
O contrato atual do Xano não tem campos de tempo. estimated_time_minutes e actual_time_minutes são metadados guardados no SQLite pelo backend e não são enviados como campos desconhecidos ao Xano. Faça backup desse banco. O cronômetro atualiza o status remoto e incrementa o tempo local sem fabricar horas a partir da quantidade de tarefas.

## 5. Busca/PDF iniciados no Xano (exigidos nas atividades 14 e 15)
O site pode usar as rotas FastAPI autenticadas /api/search e POST /api/reports/generate. O Python calcula sobre os dados espelhados do Xano.
Para atender literalmente à exigência de endpoints de busca/relatório no Xano, crie rotas protegidas no workspace que façam External API Request ao Python:
- GET /api/integration/search?local_user_id=...&q=...&overdue=true
- POST /api/integration/reports/generate?local_user_id=...

Essas rotas Python exigem X-Integration-Key igual a XANO_PYTHON_BRIDGE_KEY. Use chave distinta da chave CRUD. O Xano precisa de uma URL HTTPS pública do Python, não localhost. Resolva o ID local a partir de vínculo confiável no servidor; não aceite um ID arbitrário do visitante. O PDF pode ser repassado como arquivo ou guardado privadamente com URL temporária. Essa orquestração no workspace ainda não foi implantada.

## 6. Conferência final
Com duas contas: criar matéria/tarefa, concluir pelo cronômetro, ver progresso e relatório, buscar atraso, editar/excluir e tentar IDs da outra conta. Confirme que falhas de rede não apagam registros locais. Nenhum teste desta revisão gravou no Xano real.

Não precisa criar tabelas extras de progresso, busca, PDF ou Classroom.

## Export real recebido em 15/11/2026
Consulte xano/LEIA_ANTES.md antes de aplicar os arquivos preparados. Eles usam a função existente auth/validate_api_key: nesse pacote, configure X-API-Key no backend e XANO_API_KEY no ambiente do Xano. Não misture essa configuração com o exemplo genérico de Authorization acima. A proteção de serviço não substitui a autorização por usuário nativa exigida literalmente na atividade 13.
