# 💡 Tela 05 — Insights de IA & Relatórios em PDF

> **Módulo:** Motor de Inteligência Artificial & Auditoria Pedagógica  
> **Status:** Concluído & 100% Responsivo  
> **Arquivo Base:** `frontend/index.html` (Linhas 651–726), `frontend/js/insights.js`, `backend/app/api/ai.py`, `backend/app/api/reports.py`

---

## 1. Visão Geral
A tela de **Insights de IA & Relatórios** representa o diferencial tecnológico do EduTrack AI. Nela, algoritmos analíticos em Python processam a série temporal do estudante, identificam gargalos de tempo (desvio entre estimado e real) e geram diagnósticos preventivos, planos de ação personalizados e exportação formal em documento PDF com gráficos para entrega ao orientador ou universidade.

---

## 2. Componentes e Funcionalidades

### 2.1. Cabeçalho Analítico & Ações
- **Badge do Motor:** `✨ EduTrack Analytics Engine` indicando processamento ativo.
- **Botão "Recalcular Insights":** Dispara reanálise instantânea em tempo real.
- **Botão "Baixar Relatório Semanal (PDF)":** Gera e faz o download direto do documento PDF formatado com gráficos e métricas de desempenho.

### 2.2. Resumo Executivo da IA
- **Banner Proeminente:** Caixa com estilo *glassmorphism* destacada (`bg-gradient-to-r from-blue-50/70 via-indigo-50/40 to-white`) apresentando um resumo contextual e pedagógico da rotina do estudante.

### 2.3. Alertas Críticos de Sobrecarga
- **Painel de Alertas (`ai-critical-alerts-container`):** Exibido dinamicamente quando tarefas ultrapassam limites críticos ou quando disciplinas essenciais estão com progresso em atraso acentuado.

### 2.4. Recomendações e Otimização de Cronograma
- **Cards Categorizados por Tipo:**
  - 💡 **Dica de Produtividade (Azul):** Otimização de sessões de estudo.
  - ⏱️ **Aviso de Desvio de Tempo (Âmbar):** Aponta disciplinas que estão demandando mais tempo que o previsto.
  - 🚀 **Conquista de Ritmo (Verde):** Reconhecimento de consistência acadêmica.
  - 🚨 **Alerta de Sobrecarga (Vermelho):** Necessidade urgente de redistribuição de tarefas antes de provas.
- **Sugestão de Ação Imediata:** Cada recomendação traz um bloco prático com o próximo passo recomendado para o estudante.

### 2.5. Foco Prioritário da Semana
- **Lista de Metas de Alto Impacto:** Checklist curado pela inteligência para orientar as prioridades imediatas dos próximos 7 dias.

---

## 3. Comportamento Responsivo
- **Mobile (< 768px):** 
  - Layout reorganizado em coluna única sem perda de legibilidade.
  - Botões de recalcular e exportar PDF ajustam-se para ocupar a largura da tela com toque seguro.
  - Textos das recomendações e badges ganham espaçamento otimizado para telas estreitas.
- **Desktop (>= 1024px):** Layout dividido em 3 colunas (2 colunas para recomendações e 1 coluna para o plano de foco prioritário semanal).

---

## 4. Endpoints de Integração Backend
| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/ai/insights` | Análise com geração de recomendações e alertas |
| `GET` | `/api/reports/weekly-pdf` | Geração dinâmica de PDF via ReportLab com gráficos vetoriais |
