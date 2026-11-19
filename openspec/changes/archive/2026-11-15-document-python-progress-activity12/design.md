# Design

## Context

Consulte [proposal.md](./proposal.md) para a motivação e [specs/task-completion-percentage/spec.md](./specs/task-completion-percentage/spec.md) para o contrato documentado. A leitura do script mostra entrada por `--tasks` ou stdin, validação de objetos com status permitido e saída JSON. O cálculo compartilhado conta status `completed`, arredonda para uma casa decimal e retorna zero para lista vazia. A change ativa `harden-edutrack1-integration` já possui uma delta ampla de contrato de progresso; ela e suas tarefas não serão alteradas.

## Goals / Non-Goals

**Goals:**
- Documentar o contrato observável sem alterar a implementação.
- Separar a verificação relatada pela aluna da validação OpenSpec executada nesta change.

**Non-Goals:**
- Recriar ou editar o script, executar o script, rodar testes de runtime ou modificar proposals e changes existentes.

## Decisions

- Documentar a interface CLI e os resultados diretamente observáveis no código, mantendo a capability nova restrita ao percentual de conclusão.
- Registrar os dois resultados como “verificação manual informada pela aluna”; não atribuí-los à execução desta change. A inspeção dos testes automatizados existentes não os executa nem substitui esse relato.
- Manter a delta da change `harden-edutrack1-integration` intacta para não interferir em suas pendências.

## Risks / Trade-offs

- **[O contrato documentado pode divergir se o script mudar depois]** → manter a especificação alinhada ao código em futuras alterações e executar os testes pertinentes nessas alterações.
- **[A validação OpenSpec não verifica a execução matemática]** → declarar separadamente que os exemplos foram informados como verificação manual pela aluna e que o script não foi executado nesta change.

## Migration Plan

Não há migração: esta change altera somente documentação OpenSpec. Não há mudança de runtime nem rollback de código.
