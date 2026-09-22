# ⏱️ Tela 04 — Tarefas, Estudos & Cronômetro

> **Módulo:** Gestão de Atividades & Acompanhamento Temporal  
> **Status:** Concluído & 100% Responsivo  
> **Arquivo Base:** `frontend/index.html` (Linhas 530–571 e 912–974), `frontend/js/tasks.js`

---

## 1. Visão Geral
A tela de **Tarefas & Estudos** é o coração operacional do estudante no EduTrack AI. Ela permite não apenas criar e marcar entregas como concluídas, mas principalmente comparar o **tempo estimado versus o tempo real** gasto, além de fornecer um **cronômetro em tempo real** para foco de estudos.

---

## 2. Componentes e Funcionalidades

### 2.1. Barra de Filtros & Busca
- **Busca por Texto:** Pesquisa instantânea por palavras-chave no título ou descrição da tarefa.
- **Filtro por Disciplina:** Menu de seleção com todas as matérias cadastradas.
- **Pills de Status:** Botões de alternância rápida entre "Todas", "Pendentes", "Em Andamento" e "Concluídas".

### 2.2. Cards de Tarefas & Cálculo de Desvio
- **Badge de Desvio:** Calcula a discrepância entre a estimativa e o tempo real:
  - 🟢 **Tempo Adequado / Positivo:** Quando concluída dentro do tempo estimado.
  - 🟡 **Em Progresso:** Indicando o ritmo de execução.
  - 🔴 **Estourou Estimativa:** Alerta visual quando o aluno gastou mais tempo do que o planejado originalmente, alimentando o motor de IA para diagnósticos futuros.
- **Cronômetro de Estudo Integrado:**
  - Botão Play/Pause para cronometrar a sessão de foco.
  - Ao pausar ou finalizar, o tempo real decorrido é somado e sincronizado imediatamente com o backend.
- **Ações Rápidas:** Alternar status para concluído com um clique, editar informações ou excluir tarefa.

### 2.3. Modal de Criação / Edição de Tarefas
- **Identificador do Modal:** `#modal-task-overlay`.
- **Campos Disponíveis:**
  - Disciplina Vinculada (menu suspenso obrigatório).
  - Título da Atividade (obrigatório).
  - Data e Prazo de Entrega (`datetime-local`).
  - Status inicial (`pending`, `in_progress`, `completed`).
  - Tempo Estimado em minutos (obrigatório).
  - Tempo Real Já Gasto em minutos.
  - Descrição Detalhada com links ou instruções de apoio.

---

## 3. Comportamento Responsivo
- **Mobile (< 768px):** 
  - Barra de filtros converte-se em layout verticalizado e a seleção de status permite rolagem horizontal fluida com toque.
  - Os botões do cronômetro possuem dimensões ampliadas com feedback tátil.
  - Cada card de tarefa ajusta seus metadados em blocos empilhados para não truncar títulos ou prazos.
- **Desktop (>= 1024px):** Layout horizontal espaçoso com alinhamento perfeito de status, badges e botões de ação lateral.

---

## 4. Endpoints de Integração Backend
| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/tasks` | Listagem e filtros das tarefas acadêmicas |
| `POST` | `/api/tasks` | Cadastro de nova atividade com tempo estimado |
| `PUT` | `/api/tasks/{id}` | Edição dos dados da tarefa ou incremento de minutos estudados |
| `DELETE` | `/api/tasks/{id}` | Remoção da atividade |
