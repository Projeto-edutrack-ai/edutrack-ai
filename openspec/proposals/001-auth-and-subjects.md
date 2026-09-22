# Proposal 001: Autenticação de Usuário e Gestão de Disciplinas

**Status:** Aprovado / Implementado  
**Autor:** Aluno (Arquiteto de Soluções) & EduTrack AI Agent  
**Versão:** 1.0  
**Contexto:** MVP - Requisitos 1 e 2 da Especificação EduTrack AI  

## 1. Intenção de Negócio
Permitir que o estudante crie sua conta de forma segura com isolamento estrito de dados (multi-tenant lógico por `user_id`) e cadastre as disciplinas do período letivo com suas respectivas cargas horárias e professores.

## 2. Modelagem Canônica (snake_case)

### Tabela `users`
- `id`: integer (PK)
- `name`: string (not null)
- `email`: string (unique, indexed)
- `password_hash`: string (PBKDF2 / Argon2 / Bcrypt)
- `created_at`: timestamp

### Tabela `subjects`
- `id`: integer (PK)
- `user_id`: integer (FK -> users.id, on delete cascade)
- `name`: string (not null)
- `professor`: string (nullable)
- `workload_hours`: float (default 60.0)
- `description`: text (nullable)
- `start_date`: datetime (nullable)
- `end_date`: datetime (nullable)
- `created_at`: timestamp

## 3. Contratos de API
- `POST /api/auth/register`: Cadastro com email e senha.
- `POST /api/auth/login`: Autenticação e emissão de JWT.
- `GET /api/subjects`: Listagem de disciplinas do usuário autenticado.
- `POST /api/subjects`: Criação de disciplina vinculada ao `user_id`.
- `PUT /api/subjects/{id}`: Atualização de disciplina.
- `DELETE /api/subjects/{id}`: Exclusão em cascata.

## 4. Critérios de Aceitação
1. Um usuário autenticado nunca deve ter acesso às disciplinas de outro usuário.
2. Todas as respostas devem ser em formato JSON padronizado com tempo de resposta inferior a 2s.
