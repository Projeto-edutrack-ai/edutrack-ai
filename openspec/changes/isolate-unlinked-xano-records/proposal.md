# Change: Isolar registros sem vínculo no espelho Xano

## Why
Diagnóstico real confirmou matéria 12 sem alunos_id válido, bloqueando a sincronização de contas não relacionadas. Tarefas 53 e 54 já haviam sido gravadas remotamente, mas a atualização do espelho falhou.

## What Changes
- Ignorar registros sem vínculo que não estejam associados previamente ao usuário no SQLite.
- Continuar recusando snapshot com vínculo quebrado em registro já espelhado do usuário, preservando seus dados.
- Manter validação integral de IDs/listagem e dos campos dos registros próprios.
- Explicar explicitamente quando o Xano gravou a tarefa mas a atualização local falhou, para evitar novo cadastro.

## Impact
Filtro do espelho e mensagem pós-gravação no backend. Nenhum registro remoto é alterado, apagado ou reatribuído.
