# Proposal 002: Gestão de Tarefas Acadêmicas e Cronômetro de Estudo

**Status:** Aprovado / Implementado  
**Autor:** Aluno (Arquiteto de Soluções) & EduTrack AI Agent  
**Versão:** 1.0  
**Contexto:** Requisitos Funcionais 3 e 4 da Especificação EduTrack AI  

## 1. Intenção de Negócio
Possibilitar o gerenciamento de entregas acadêmicas (trabalhos, provas, laboratórios) vinculadas a uma disciplina, registrando o tempo previsto de estudo (`estimated_time_minutes`) e o tempo efetivamente dedicado (`actual_time_minutes`) via cronômetro de estudo interativo.

## 2. Modelagem Canônica

### Tabela `academic_tasks`
- `id`: integer (PK)
- `user_id`: integer (FK -> users.id, on delete cascade)
- `subject_id`: integer (FK -> subjects.id, on delete cascade)
- `title`: string (not null)
- `description`: text (nullable)
- `due_date`: datetime (nullable)
- `status`: string (`pending`, `in_progress`, `completed`)
- `estimated_time_minutes`: float (default 60.0)
- `actual_time_minutes`: float (default 0.0)
- `completed_at`: datetime (nullable)
- `created_at`: timestamp

## 3. Fluxo de Cronômetro & Registro de Tempo
1. O aluno seleciona uma tarefa e inicia a contagem no painel web/mobile.
2. O status transiciona automaticamente para `in_progress`.
3. Ao pausar ou concluir a sessão, a requisição `POST /api/academic_tasks/{id}/study-time` incrementa `actual_time_minutes`.
4. Ao concluir, `completed_at` é registrado para auditoria temporal.
