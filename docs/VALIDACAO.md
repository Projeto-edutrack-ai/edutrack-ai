# Validação — base edutrack1

## Resultados locais de 10/11/2026
- Python 3.12: `python -m pytest -q --disable-warnings --tb=short` -> **58 passed**, 15 avisos de depreciação.
- Node.js: `node --test tests/frontend-client.test.cjs` -> **7 passed**, nenhuma falha.
- Sintaxe dos nove arquivos JavaScript ativos validada por node --check.
- `scripts/calculate_progress.py` -> saída JSON percentage=50.0 para uma concluída entre duas; zero e 100% também cobertos.
- OpenSpec 1.17.0 -> validação estrita da mudança de integração, da remoção Classroom e das especificações ativas.

## Cobertura relevante
Recuperação por token com validade/uso único e SMTP local; mentor da equipe; CRUD local e proxy Xano; identidade persistente e recusa de vínculo por simples coincidência de e-mail; bloqueio de IDs alheios e de troca de disciplina entre usuários; rejeição de status e dados inválidos; paginação completa e rollback do espelho; datas UTC; separação de dados demo/remotos; metadados de tempo; URL de produção; contrato exato titulo_/status, enum com espaço e carga horária inteira; cronômetro alterando status remoto; busca por nome OU atraso; PDF autenticado; ponte de serviço; ausência de rotas/interface Classroom; preservação de colunas legadas.

## Sobre a contagem
O ZIP original tinha 100 testes, muitos exclusivos de Classroom. Esses testes e seus serviços foram removidos junto com a funcionalidade solicitada. Foram acrescentadas regressões das correções atuais. A contagem não é uma afirmação de que o workspace real foi testado.

## Limites
Nenhuma chamada de teste gravou no Xano real. Integração remota foi simulada por httpx.MockTransport, seguindo o OpenAPI colado pela usuária. SMTP foi testado apenas com servidor local, sem enviar mensagens a pessoas. Não houve teste visual completo em navegador nem validação do site publicado. Artefatos Figma não foram duplicados/exportados. Não houve push ao GitHub ou deploy.

## Nova execução em 15/11/2026
- Python 3.12: 61 testes passaram (15 avisos), incluindo três verificações estáticas do pacote Xano e DELETE com JSON null do export real.
- Node: 7 testes passaram.
- OpenSpec: 6 itens passaram na validação estrita.
- Os .xs preparados ainda NÃO foram compilados/validados no Xano. Nenhum push remoto ou teste de registros reais foi realizado.

## Correção de inicialização da interface (15/11)
O console real revelou a chamada inexistente Auth.bindProfileEvents. Removida: os eventos de perfil já estão em bindEvents. Novo teste exercita App.init real e auth-success, verifica que o submit da matéria impede navegação nativa e chama a API. Oito testes JavaScript passam. Reprodução no navegador da aluna ainda será conferida após a atualização.

## Limite de chamadas Xano (15/11)
- 68 testes Python e 11 JavaScript passaram. Casos incluem chamadas concorrentes, cópias independentes do cache, expiração, credenciais, invalidação após escrita, pausa 429 sem repetição de POST e inicialização única de handlers.
- OpenSpec da mudança de redução de rajadas validado.
- Evidências reais da aluna confirmaram push de 15 endpoints, recusa pública sem chave e gravação das matérias de teste IDs 22/23. Não há confirmação ainda da aplicação deste último complemento no notebook, nem do isolamento completo entre duas contas.
- O orçamento é por processo Python/origem e reduz chamadas de um servidor local. Outros clientes do mesmo Xano e múltiplos workers podem consumir o limite da instância; não há garantia de ausência de 429 nessas condições.

## Isolamento de registros sem vínculo (15/11)
Diagnóstico real confirmou nove matérias, 28 tarefas, matéria 12 com alunos_id inválido, demais campos e schemas verificados sem problema. O filtro do espelho ignora registros sem vínculo nunca associados ao usuário; continua falhando e preservando dados se um vínculo já conhecido se perder. Nenhum registro remoto alterado.

73 testes Python e 11 JavaScript passaram. Teste de regressão reproduz o cadastro de uma tarefa com matéria antiga sem dono, preserva tempo estimado e confirma métricas. Outro teste preserva registro conhecido com vínculo quebrado. A mensagem de erro pós-gravação informa o ID gravado e pede para não repetir. Aplicação no notebook e teste real ainda pendentes.

## Busca em português e camadas (15/11)
83 testes Python e 11 JavaScript passaram. Testes de busca cobrem caixa, remoção de acentos, NFC/NFD, preservação de valores originais, literais LIKE e isolamento de contas. Função SQLite é registrada por conexão; requer reiniciar o processo. CSS organiza o cabeçalho acima das seções com transformação. Teste visual do dropdown e aplicação no notebook ainda pendentes.

## Evidências reais adicionais fornecidas pela aluna
- Busca por nome/acentos e OR com atraso passou; checkbox sem texto retornou tarefa atrasada e matéria.
- Segunda conta iniciou sem matérias; GET direto a matéria 22 e tarefa 53 retornou 404 no FastAPI. Isso verifica leitura entre contas, não equivale a JWT nativo do Xano nem teste manual de todas as mutações cruzadas.
- Matéria duplicada vazia 23 foi excluída pelo site e exclusão confirmada no Xano.
- Tarefa editada, marcada concluída, cronômetro e tempos persistidos; progresso por matéria e ponderado conferidos.
- PDF real recebido e inspecionado: uma página legível, 2/2 tarefas concluídas, 50% ponderado enquanto havia matéria vazia, horas arredondadas 0,4. Esse arquivo não integra o repositório por conter dados pessoais.
- Repositório público lido em HEAD ba810a7; push/PR desta revisão ainda não realizados.
