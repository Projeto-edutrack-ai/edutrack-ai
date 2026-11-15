# Change: Remover integração Google Classroom

## Why
A usuária solicitou em 10/11/2026 que o EduTrack deixe de integrar com Google Classroom e utilize somente alunos, matérias e tarefas no Xano.

## What Changes
- Remover painel, botões, script e chamadas do navegador relativos ao Classroom.
- Remover endpoints, schemas e serviços OAuth/sincronização Classroom.
- Retirar variáveis de ambiente específicas e atualizar a documentação.
- Preservar registros importados, colunas legadas e propostas históricas, sem migração destrutiva.

## Impact
Login, recuperação de senha, mentor Gemini opcional, CRUD Xano, progresso e PDF permanecem. Não serão apagadas tabelas no workspace. Documentos e templates antigos serão identificados como históricos, fora das instruções ativas.
