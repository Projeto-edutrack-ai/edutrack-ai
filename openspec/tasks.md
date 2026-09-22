# OpenSpec Tracking Tasks — EduTrack AI

Matriz viva de rastreabilidade de tarefas e conformidade com as proposals OpenSpec.

## Fase 1: Setup Básico e Autenticação (Semanas 1-3)
- [x] **TASK-001**: Modelagem da tabela `users` com XanoScript e SQLAlchemy ORM.
- [x] **TASK-002**: Implementação do fluxo de Autenticação JWT (`/api/auth/register`, `/api/auth/login`, `/api/auth/me`).
- [x] **TASK-003**: Endpoint de simulação de recuperação de senha (`/api/auth/forgot-password`).
- [x] **TASK-004**: Modelagem e CRUD completo da tabela `subjects` (Disciplinas) com isolamento por usuário.
- [x] **TASK-005**: Conformidade com padrão snake_case para nomes canônicos de tabelas e campos.

## Fase 2: Gestão de Tarefas e Cronômetro (Semanas 4-5)
- [x] **TASK-006**: Modelagem da tabela `academic_tasks` relacionada à disciplina (`subject_id`) e usuário (`user_id`).
- [x] **TASK-007**: CRUD completo de tarefas (`/api/academic_tasks`) com status `pending`, `in_progress`, `completed`.
- [x] **TASK-008**: Implementação do endpoint de registro de tempo de estudo do cronômetro (`/api/academic_tasks/{id}/study-time`).
- [x] **TASK-009**: Filtros avançados por disciplina, status e busca textual.

## Fase 3: Motor Avançado de Progresso em Python (Semanas 6-7)
- [x] **TASK-010**: Implementação do serviço `ProgressEngine` em Python.
- [x] **TASK-011**: Cálculo de progresso ponderado por carga horária das disciplinas (`workload_hours`).
- [x] **TASK-012**: Algoritmo de velocidade de conclusão (`study_velocity_tasks_per_week`) e projeção de data de formatura/fim de semestre.
- [x] **TASK-013**: Cálculo do percentual de desvio entre tempo estimado e tempo real por disciplina.
- [x] **TASK-014**: Endpoint `/api/analytics/progress` e `/api/analytics/time-spent` para renderização de gráficos.

## Fase 4: Inteligência Artificial e Relatórios PDF (Semanas 7-8)
- [x] **TASK-015**: Motor de IA `AIService` com diagnóstico de desvio de cronograma (ex: "Você está levando 30% mais tempo em Python").
- [x] **TASK-016**: Suporte híbrido: integração com Google Gemini API e fallback para algoritmo analítico local.
- [x] **TASK-017**: Gerador de relatório semanal profissional em PDF via Python e ReportLab (`/api/reports/weekly-pdf`).
- [x] **TASK-018**: Interface Frontend Mobile-First responsiva com dashboard de métricas, cronômetro ativo e temas claro/escuro.
- [x] **TASK-019**: Suíte de testes automatizados com `pytest` cobrindo segurança, isolamento e matemática de métricas.
- [x] **TASK-020**: Monografia acadêmica e guia de apresentação para banca da faculdade.
