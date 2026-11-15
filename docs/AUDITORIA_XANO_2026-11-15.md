# Auditoria do export real — 15/11/2026

| Item | Resultado |
|---|---|
| Documentos recebidos | 63 |
| Três tabelas acadêmicas | Presentes, nomes em português autorizados |
| Relacionamentos | Corretamente declarados |
| Métodos CRUD | 15 endpoints existentes |
| Autenticação no grupo acadêmico | Ausente no original |
| Função de chave de serviço | Já existe, mas não é chamada no CRUD original |
| Tabela de autenticação nativa user | Existe, sem vínculo declarado em alunos |
| DELETE | Resposta null, diferente do schema simplificado Swagger |
| PATCH | Original remove null/texto vazio; correção preserva atualizações explícitas e limita campos |
| Classroom no workspace | Ainda há objetos legados; aplicativo local segue sem integração |
| Objetos de outros projetos | Presentes, preservados |
| Busca/PDF Xano | Não há endpoints correspondentes no export recebido |

Preparação local em xano/deploy e instruções em xano/LEIA_ANTES.md. Não houve push, migração, leitura de registros ou alteração do workspace real. Validação estática não equivale a compilação/dry-run e teste remoto.
