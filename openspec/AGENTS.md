# Instrucoes OpenSpec — EduTrack AI

## Organizacao dos artefatos

- `config.yaml` define o schema e o idioma usados pela CLI do OpenSpec.
- `specs/` contem especificacoes de referencia do produto e dos contratos.
- `changes/` e o local para novas mudancas propostas pelo fluxo atual do OpenSpec.
- `changes/archive/` guarda mudancas arquivadas pela CLI.
- `proposals/` contem proposals anteriores do projeto. Preserve esses documentos; nao os mova nem os converta sem uma solicitacao especifica.
- `tasks.md` e a matriz de rastreabilidade existente. Atualize-a quando uma mudanca alterar o estado ou o escopo das tarefas listadas.
- `xanoscript/` contem artefatos e documentacao de Xano; mantenha-os alinhados com os contratos relevantes.

## Fluxo de trabalho

- **Registro obrigatorio para trabalho de IA:** antes de qualquer IA modificar arquivos do projeto, crie uma change OpenSpec para o escopo solicitado ou atualize uma change ativa que trate exatamente desse escopo. Inclua a intencao, criterios de conclusao e tarefas antes da implementacao. Isso tambem se aplica a correcoes pequenas e mudancas de documentacao.
- Ao concluir, marque somente as tarefas efetivamente implementadas e validadas, registre os testes executados e atualize as especificacoes afetadas. Se o trabalho ficar incompleto, deixe as tarefas pendentes e explique o que falta; nao apresente a change como concluida.
- Use a CLI ou os comandos OpenSpec instalados para criar e arquivar changes. Nao crie manualmente diretorios de change nem use `proposals/` como diario. Preserve as proposals historicas existentes.
- Para uma nova mudanca, use o fluxo OpenSpec configurado para Gemini (por exemplo, `/opsx:propose`) ou a CLI (`openspec new change`). Nao crie manualmente uma pasta de change: a CLI gera os metadados necessarios.
- Consulte as especificacoes existentes antes de propor um comportamento novo; atualize-as quando a mudanca alterar o comportamento esperado do produto.
- Escreva o conteudo dos artefatos em portugues, mantendo os titulos estruturais e palavras-chave exigidos pelo schema OpenSpec.
- Mantenha o escopo da proposta, os requisitos, os criterios de aceitacao e as tarefas de implementacao coerentes entre si.
- Nao marque uma tarefa como concluida sem implementacao e validacao correspondentes.
- Preserve os artefatos existentes que nao estejam diretamente envolvidos na mudanca.

## Ferramentas desta revisão
OpenSpec 1.17.0 foi fixado em package.json. Workflows Antigravity estão em .agents/workflows e skills em .agents/skills; Gemini usa .gemini. Este arquivo contém instruções próprias da equipe e foi preservado após a configuração da CLI. Não execute init/update cegamente: a limpeza de arquivos legados pode removê-lo.
