# Design

O plano gratuito documenta 10 requisições em 20 segundos: https://www.xano.com/pricing/. Leituras GET são compartilhadas por 30s, chaveadas por URL/base/cabeçalho e hash da credencial. O cache nunca é exposto diretamente: cada endpoint continua filtrando o aluno autenticado. Mutex por origem elimina consultas simultâneas iguais; chamadas não atendidas pelo cache ficam espaçadas por 2.1s. Escritas invalidam todas as leituras da instância, inclusive em erro de transporte, sem retentar POST/PATCH/DELETE.

429 gera pausa de no mínimo 20s, respeitando Retry-After numérico maior. Não há sleep de 20s: chamadas durante pausa falham rapidamente com HTTP 429 e Retry-After. Leituras após expiração não recebem cache vencido. Instâncias e credenciais não compartilham resultados. MockTransport não usa o limitador de produção para preservar isolamento dos testes; o orçamento é testado com relógio/controlador próprios.

A lista visual mantém cards já carregados diante de falha, com aviso explícito de desatualização. Não apresentar cache antigo como uma atualização bem-sucedida. Vinculação e isolamento existentes permanecem ativos.
