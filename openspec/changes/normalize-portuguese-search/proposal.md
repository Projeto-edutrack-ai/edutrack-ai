# Change: Normalizar busca em português e corrigir sobreposição dos resultados

## Why
No teste real, Teste encontra registros e Integração retorna zero. SQLite LIKE/lower não normaliza Unicode nem faz case folding completo. O dropdown também fica atrás do conteúdo animado.

## What Changes
- Normalizar termos e campos pesquisáveis no SQLite sem mudar valores armazenados.
- Ignorar diferenças de acento, caixa e composição NFC/NFD.
- Preservar filtro de usuário, status, origem e lógica nome OU atraso.
- Dar ao cabeçalho contexto de empilhamento acima das seções animadas.

## Impact
Busca Python/SQLite e CSS; sem migração, credenciais ou mudanças Xano. Reinício necessário para registrar função SQLite nas conexões.
