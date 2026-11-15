# Especificação de Banco de Dados — EduTrack AI

## Diagrama Entidade-Relacionamento (DER)

```mermaid
erDiagram
    users ||--o{ subjects : "possui"
    users ||--o{ academic_tasks : "possui"
    subjects ||--o{ academic_tasks : "contém"

    users {
        int id PK
        string name
        string email UK
        string password_hash
        string avatar_url "Foto de perfil / Base64"
        string course "Curso (ex: Ciência da Computação)"
        string college_year "Ano / Semestre (ex: 3º Ano)"
        string institution "Faculdade / Universidade"
        string bio "Metas / Bio do Aluno"
        datetime created_at
    }

    subjects {
        int id PK
        int user_id FK
        string name
        string professor
        float workload_hours
        string description
        datetime start_date
        datetime end_date
        datetime created_at
        string source "Origem: local ou google_classroom"
        string classroom_course_id "ID do curso no Google Classroom"
        string classroom_link "Link direto no Classroom"
        datetime classroom_synced_at "Data/hora da sincronização"
    }

    academic_tasks {
        int id PK
        int user_id FK
        int subject_id FK
        string title
        string description
        datetime due_date
        string status "pending, in_progress, completed"
        float estimated_time_minutes
        float actual_time_minutes
        datetime completed_at
        datetime created_at
        string source "Origem: local ou google_classroom"
        string classroom_coursework_id "ID da atividade no Classroom"
        string classroom_link "Link direto da atividade"
        float max_points "Pontuação máxima da atividade"
        string classroom_submission_state "Estado da submissão no Classroom"
        datetime classroom_synced_at "Data/hora da sincronização"
    }
```

## Dicionário de Dados

### Tabela: `users`
| Campo | Tipo | Nulo? | Chave | Descrição |
|---|---|---|---|---|
| `id` | Integer | Não | PK | Identificador único do estudante |
| `name` | String | Não | | Nome completo do estudante |
| `email` | String | Não | UK | Email institucional ou pessoal para login |
| `password_hash` | String | Não | | Hash PBKDF2 HMAC-SHA256 da senha |
| `avatar_url` | Text | Sim | | URL da foto de perfil ou Data URI em Base64 |
| `course` | String | Sim | | Curso de graduação do estudante |
| `college_year` | String | Sim | | Ano letivo ou semestre acadêmico |
| `institution` | String | Sim | | Faculdade ou universidade de vínculo |
| `bio` | Text | Sim | | Biografia e foco acadêmico do aluno |
| `created_at` | DateTime | Não | | Data de cadastro |

### Tabela: `subjects`
| Campo | Tipo | Nulo? | Chave | Descrição |
|---|---|---|---|---|
| `id` | Integer | Não | PK | Identificador único da disciplina |
| `user_id` | Integer | Não | FK | Vínculo com a tabela `users` |
| `name` | String | Não | | Nome da disciplina |
| `professor` | String | Sim | | Nome do professor(a) |
| `workload_hours` | Float | Não | | Carga horária total (usada no cálculo ponderado) |
| `description` | String | Sim | | Ementa ou objetivos da disciplina |
| `start_date` | DateTime | Sim | | Data de início do período letivo |
| `end_date` | DateTime | Sim | | Data de término do período letivo |
| `created_at` | DateTime | Não | | Data de criação |
| `source` | String | Não | | Origem dos dados (`local` ou `google_classroom`) |
| `classroom_course_id` | String | Sim | | ID do curso no Google Classroom (se integrado via Xano) |
| `classroom_link` | String | Sim | | URL direta para o curso no Google Classroom |
| `classroom_synced_at` | DateTime | Sim | | Carimbo de data/hora da última sincronização |

### Tabela: `academic_tasks`
| Campo | Tipo | Nulo? | Chave | Descrição |
|---|---|---|---|---|
| `id` | Integer | Não | PK | Identificador único da tarefa |
| `user_id` | Integer | Não | FK | Vínculo com a tabela `users` |
| `subject_id` | Integer | Não | FK | Vínculo com a tabela `subjects` |
| `title` | String | Não | | Título da tarefa/atividade |
| `description` | String | Sim | | Detalhes e instruções |
| `due_date` | DateTime | Sim | | Prazo final para entrega |
| `status` | String | Não | | Status: `pending`, `in_progress`, `completed` |
| `estimated_time_minutes` | Float | Não | | Tempo estimado de estudo planejado |
| `actual_time_minutes` | Float | Não | | Tempo real acumulado no cronômetro |
| `completed_at` | DateTime | Sim | | Data e hora de conclusão |
| `created_at` | DateTime | Não | | Data de criação |
| `source` | String | Não | | Origem dos dados (`local` ou `google_classroom`) |
| `classroom_coursework_id` | String | Sim | | ID da atividade no Google Classroom |
| `classroom_link` | String | Sim | | URL direta para a atividade no Google Classroom |
| `max_points` | Float | Sim | | Pontuação máxima da atividade |
| `classroom_submission_state` | String | Sim | | Estado da submissão (`NEW`, `CREATED`, `TURNED_IN`, `RETURNED`) |
| `classroom_synced_at` | DateTime | Sim | | Carimbo de data/hora da última sincronização |
