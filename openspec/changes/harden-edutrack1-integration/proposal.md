# Change: Fortalecer a integração do EduTrack1 preservando a base da equipe

## Why
A versão da equipe mantém o CRUD Xano no navegador, associa alunos por e-mail sem verificação, aceita páginas incompletas no espelho e apresenta divergências de status, URL, IDs e busca. É necessário preservar recuperação de senha por token, mentor de IA e OpenSpec atual ao corrigir essas lacunas.

## What Changes
- Mediar CRUD pelo FastAPI com JWT, vínculo persistente e autorização por registro.
- Validar paginação e transações do espelho; não tratar indisponibilidade como conjunto vazio nem sucesso atualizado.
- Corrigir URL de produção, normalização de status, PATCH e troca de disciplina.
- Completar busca texto OU atraso, contrato percentage e PDF.
- Acrescentar regressões, instruções de configuração, pesquisa de referências e pendências reais.

## Impact
A configuração de autenticação e os endpoints efetivos do Xano dependem das URLs/documentação que a equipe enviará. Nenhuma implantação remota é autorizada por inferência nem declarada concluída. Dados e propostas anteriores serão preservados; nenhuma migração destrutiva será executada.
