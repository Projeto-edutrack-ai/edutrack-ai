## Context
O frontend conhece IDs Xano; os serviços Python usam IDs locais com xano_id. A recuperação de senha da equipe usa token e deve ser preservada.

## Decisions
Manter os contratos legados materias/tarefas no adaptador servidor, usar JWT para o navegador, validar a propriedade no FastAPI e documentar proteção adicional obrigatória das URLs Xano. Vínculos legados não serão assumidos por simples coincidência de e-mail. O espelho só aplica exclusões após leitura e validação completas.

## Risks / Trade-offs
O workspace real ainda não foi inspecionado. Métodos, envelopes, autenticação e campos precisam ser confirmados antes da publicação. Não misturar dados de demonstração com dados remotos silenciosamente. A configuração remota não está concluída apenas porque testes com mocks passam.

## Migration Plan
Testar em cópia, preservar bancos/segredos, aplicar migrações aditivas e mapear contas antigas explicitamente. Criar PR e validar com duas contas antes de publicar.
