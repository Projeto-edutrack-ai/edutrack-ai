# require-ai-change-tracking

Adicionar regras comuns e instrucoes para Gemini exigindo que trabalho de IA seja registrado em uma change OpenSpec antes da edicao, com tarefas e validacao atualizadas ao concluir.

## Tarefas

- [x] Atualizar `AGENTS.md` e `openspec/AGENTS.md` para exigir registro OpenSpec antes de alteracoes feitas por IA.
- [x] Adicionar instrucoes de contexto para Gemini em `GEMINI.md`.
- [x] Registrar a mesma regra no contexto de `openspec/config.yaml`.
- [x] Validar a configuracao e a change com `openspec validate --all --json`.

## Validacao

Validacao executada em 2026-10-26. `openspec validate --all --json` reconheceu a change; `skip_specs: true` e intencional porque esta mudanca trata de orientacoes e configuracao, sem alterar requisitos funcionais do produto.
