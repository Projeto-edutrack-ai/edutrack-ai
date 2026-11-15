# Change: Reduzir rajadas de chamadas Xano

## Why
O teste real confirmou HTTP 429 e dois registros salvos após repetição manual. Dashboard, disciplinas, tarefas e insights consultam as mesmas listas simultaneamente.

## What Changes
- Compartilhar leituras recentes e serializar chamadas por instância Xano no processo Python.
- Respeitar pausa após 429 sem repetir automaticamente escritas.
- Invalidar leituras após escrita e manter propriedade validada antes de responder ao navegador.
- Inicializar handlers uma vez; evitar requisições duplicadas de carregamento de disciplinas.
- Preservar cards já exibidos e informar falha de atualização.

## Impact
Backend e frontend locais. Nenhuma alteração de schema, registro ou chave Xano. O limitador é por processo, adequado ao servidor local de uma instância; múltiplos processos exigem coordenação compartilhada.
