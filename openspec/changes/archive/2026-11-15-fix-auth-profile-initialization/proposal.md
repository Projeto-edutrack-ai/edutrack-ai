# Change: Corrigir inicialização dos formulários após login

## Why
O console real mostrou TypeError em Auth.init: bindProfileEvents não existe. A exceção impede registrar o evento auth-success e inicializar os formulários de matérias/tarefas. O submit nativo pode então navegar e reabrir a tela de login.

## What Changes
- Remover a chamada inexistente; os eventos de perfil já estão em bindEvents.
- Exercitar App.init real e o fluxo auth-success -> envio da matéria, verificando preventDefault e chamada da API.

## Impact
Somente inicialização frontend, teste de regressão e documentação. Não altera banco, credenciais ou configuração Xano.
