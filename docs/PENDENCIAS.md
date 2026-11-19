# Pendências reais

## Fora do código local
1. Proteger todos os endpoints reais Xano com credencial exclusiva de servidor; o contrato recebido tem security: [] em todas as operações.
2. Configurar o .env no servidor e verificar vínculos antigos; não enviar chaves ao chat.
3. Testar fluxo real com duas contas após configurar o workspace.
4. Criar as rotas Xano de orquestração de busca/PDF para atender aos endpoints exigidos nas atividades 14 e 15. O lado Python está disponível, mas não há deploy remoto.
5. Duplicar/analisar duas referências Figma e exportar os assets permitidos. Pesquisa documental não equivale a essa execução.
6. Realizar a proposta de teste de notas da atividade 10 com o agente. Não foi fabricado histórico da conversa.
7. Configurar e verificar ferramentas no computador da aluna, fazer PRs reais e entregar relatório final/links. O PR final deve permanecer aberto para o professor.
8. Antes de substituir a versão da equipe, comparar com o repositório atual e preservar bancos/segredos/alterações posteriores. O ZIP original pode estar mais antigo que o GitHub.

## Decisões confirmadas
Antigravity substitui FlutterFlow. Google Classroom foi removido por solicitação explícita. Nenhuma nova tabela Xano é necessária além de alunos, materias e tarefas; a autenticação permanece no backend Python.

## Bancos existentes
As migrações adicionam vínculos locais sem descartar tabelas/colunas. Os bancos .db não são incluídos no pacote e não devem ser substituídos por bancos demo. Dados antigos importados permanecem armazenados; não há sincronização Classroom ativa.

## Revisão do export real (15/11)
O pull já foi realizado e os arquivos recebidos. Relações e nomes em português confirmados. Pacote limitado preparado em xano/deploy com guarda de serviço, sem alterações remotas. A autenticação individual no próprio Xano ainda exige alinhamento arquitetural; somente a chave de servidor não demonstra auth.id nativo.
