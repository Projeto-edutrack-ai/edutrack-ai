# Change: Diagnosticar falha do espelho sem escrever dados

## Why
O Xano confirmou tarefas 53 e 54 após o frontend reportar falha de atualização do espelho. A causa ainda não é conhecida e repetir POST cria duplicatas.

## What Changes
Adicionar diagnóstico somente-leitura de vínculos e campos do contrato. Exibir IDs problemáticos e códigos, sem nome, e-mail, senha, chave ou conteúdo dos registros. Não executar mirror_user_data pois ela grava SQLite.

## Impact
Script administrativo local; nenhuma mudança remota ou migração.
