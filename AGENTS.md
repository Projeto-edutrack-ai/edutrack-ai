# Instruções para Agentes de IA — EduTrack AI

## Perfil do projeto
EduTrack AI é um app de gestão acadêmica orientado por especificações (OpenSpec).
- Frontend: HTML/CSS/JavaScript com Antigravity, substituição do FlutterFlow autorizada pelo professor.
- Backend: FastAPI, autenticação JWT e SQLite; Xano armazena alunos, matérias e tarefas.
- IA assistente: ferramentas do projeto para Antigravity e Gemini Code Assist.
- Arquitetura e contexto adicionais: `openspec/project.md`.
Estas regras orientam o trabalho no repositório, respeitando instruções superiores e os pedidos explícitos do usuário. Em conflitos entre documentos do projeto, preserve as decisões específicas abaixo e explique a divergência relevante.

## Escopo e planejamento
- Faça somente o escopo solicitado. Planejar não autoriza implementar; uma proposta de notas não autoriza criar CRUD completo ou endpoints de consulta extras.
- Antes de qualquer edição por IA, leia integralmente `openspec/AGENTS.md` e registre uma change pela CLI para esse escopo, ou atualize uma change ativa exatamente correspondente. Inclua intenção, critérios de conclusão e tarefas antes da implementação, inclusive para documentação e pequenas correções.
- Consulte os arquivos relacionados e as especificações existentes antes de propor alterações.
- Preserve propostas históricas. Não crie diretórios de change manualmente nem utilize uma proposta sem relação como diário.
- Marque como concluído somente o que foi realizado e validado. Uma proposta de teste arquivada não equivale a funcionalidade implementada.

## Publicação e revisão
- Não faça push, sync ou deploy por iniciativa própria. A entrega padrão é produzir os arquivos e a validação local para revisão humana.
- Execute ações externas somente quando explicitamente autorizadas pelo usuário; uma autorização já concedida para a ação continua válida.
- Não confunda geração de XanoScript com aceitação ou publicação no servidor. Distinga testes locais de verificações reais.

## Nomenclatura e Git
- Novos identificadores de código, funções e comentários técnicos: inglês; tabelas e campos em snake_case; IDs de changes em kebab-case.
- Exceção autorizada: preserve os nomes portugueses do contrato Xano (`alunos`, `materias`, `tarefas`, `alunos_id`, `materias_id`, `titulo_`). Não renomeie contratos existentes apenas para traduzir.
- Branches: `feat/<escopo>`, `fix/<escopo>` ou `docs/<escopo>`.
- Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:` e `test:`. Exemplo: `docs: detalha regras dos agentes`.
- Novos `tasks.md` devem ser escritos em inglês. Não reescreva artefatos históricos apenas para mudar o idioma.

## OpenSpec
- Use a versão fixada em package.json. Crie changes com `openspec new change <id>` ou o workflow instalado correspondente (por exemplo `/opsx:propose`).
- `proposal.md`: `# Change: <id>`, `## Why`, `## What Changes`, `## Impact`.
- Specs permanentes em `openspec/specs/<capability>/spec.md`: título, `## Purpose`, `## Requirements`.
- Deltas em `openspec/changes/<id>/specs/<capability>/spec.md`: `## ADDED Requirements`, `## MODIFIED Requirements` ou `## REMOVED Requirements`, conforme a mudança.
- Cada `### Requirement:` deve usar SHALL ou MUST e conter pelo menos um `#### Scenario:` com bullets **WHEN** e **THEN**.
- Mantenha proposta, requisitos, tarefas e escopo coerentes. Valide com `npm.cmd run spec:validate` no PowerShell (ou `npm run spec:validate` em outros ambientes).
- Arquive pela CLI; sincronize specs somente para comportamento efetivamente entregue. Propostas de teste sem implementação não devem virar requisitos permanentes ativos.

## XanoScript e contrato real
- Antes de editar qualquer `.xs`, consulte as diretrizes correspondentes fornecidas pela extensão/projeto: tabelas, funções, APIs ou tarefas, além dos exemplos relevantes.
- Procure primeiro `docs/table_guideline.md`, `docs/function_guideline.md`, `docs/api_query_guideline.md` ou `docs/task_guideline.md`. Esses caminhos são referências possíveis, não arquivos garantidos neste repositório.
- Se ausentes, consulte a documentação oficial disponível e informe a ausência. Não invente documentação ou sintaxe com base apenas em memória.
- Relações: `materias.alunos_id` referencia alunos; `tarefas.materias_id` referencia matérias. Não presuma igualdade entre IDs locais, IDs remotos e identidade nativa do Xano.
- Preserve `titulo_`, carga horária inteira e o enum real de status, inclusive o espaço final de `em_andamento ` na fronteira com Xano. Use os adaptadores existentes.
- Siga REST nos endpoints solicitados, sem ampliar o escopo. Preserve a separação entre api, models, schemas, services e frontend.

## Segurança e dados
- Toda operação acadêmica do navegador passa pelo FastAPI autenticado e pela verificação de propriedade: usuário local → vínculo persistente do aluno → matéria → tarefa. Isso vale para leitura e escrita.
- Não presuma que a credencial de servidor Xano identifique o aluno ou forneça `auth.id` individual. Autorização individual permanece no FastAPI nesta arquitetura.
- Não associe contas remotas existentes apenas por coincidência de e-mail: use vínculo persistente e verificado.
- Nunca exponha chaves Xano no frontend nem inclua .env, tokens, banco local ou dados pessoais reais nos commits, exemplos ou evidências públicas.
- Não substitua ou apague bancos existentes durante testes. Utilize fixtures e bancos isolados definidos em tests/ e pytest.ini.
- Não converta respostas remotas inválidas em listas vazias nem apague registros para resolver sincronização. Trate erros sem mascarar falhas.
- Google Classroom foi removido por decisão do grupo; não reintroduza OAuth, rotas ou tabelas dessa integração.

## Comunicação e validação
- Antes de agir, explique a intenção e os arquivos envolvidos. Peça esclarecimentos somente quando uma informação necessária não puder ser obtida no contexto.
- Para mudanças de comportamento, mantenha implementação, testes e documentação relacionada em sincronia.
- Execute verificações pertinentes: backend `python -m pytest`, frontend `npm.cmd run test:frontend`, especificações `npm.cmd run spec:validate`.
- Informe resultados reais, limitações e falhas existentes. Não declare deploy, segurança remota, demonstração da IA ou conclusão das 16 atividades sem evidência correspondente.
