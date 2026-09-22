# 🌌 Tela 02 — Dashboard 3D, KPIs & Scroll World

> **Módulo:** Painel de Inteligência Acadêmica & Visualização Espacial  
> **Status:** Concluído & 100% Responsivo  
> **Arquivo Base:** `frontend/index.html` (Linhas 332–503), `frontend/js/dashboard.js`, `frontend/js/scroll-world.js`

---

## 1. Visão Geral
A tela inicial logada do **EduTrack AI** proporciona uma experiência de nível profissional combinando métricas acadêmicas essenciais e um universo gráfico 3D interativo construído com **Three.js** e sincronizado com o **GSAP ScrollTrigger**.

---

## 2. Componentes e Funcionalidades

### 2.1. Welcome Hero
- **Título Dinâmico:** "Painel de Acompanhamento 3D" com gradiente estilizado.
- **Subtítulo Informativo:** Explica a métrica de progresso acadêmico ponderado pela carga horária das disciplinas.
- **Ações Rápidas de Topo:** Botões para criar diretamente uma nova disciplina ou cadastrar uma nova tarefa sem sair da tela.

### 2.2. Sistema Planetário 3D (Scroll World Dinâmico)
- **Correspondência 1:1 de Planetas por Disciplina:**
  - Cada disciplina cadastrada pelo estudante gera um planeta 3D orbital exclusivo.
  - Se houver 2 matérias cadastradas, a cena renderiza exatamente 2 planetas orbitais; se houver 5 matérias, 5 planetas, e assim por diante.
  - O tamanho (raio) do planeta é proporcional à carga horária da disciplina (matérias mais pesadas geram corpos celestes maiores).
  - Cada planeta possui anéis orbitais translúcidos com estética *sci-fi* e iluminação *standard metalness*.
  - Linhas de constelação desenhadas dinamicamente interligam os planetas ativos no espaço.
- **Interatividade Total (Rotação Livre 360° em Qualquer Direção):**
  - **Arraste Livre (Mouse Drag & Touch):** O usuário pode girar o universo em qualquer direção (horizontal, vertical ou diagonal) com inércia física suave e amortecimento amortizado.
  - **Zoom Suave (Wheel):** Aproxime ou afaste a câmera do sistema solar com a roda do mouse.
  - **Raycaster & Tooltip em Tempo Real:** Ao passar o mouse sobre qualquer planeta, exibe um tooltip com o nome da disciplina, carga horária e total de horas estudadas.
  - **Botão "Resetar Vista":** Reposiciona a câmera na perspectiva padrão com um clique.
- **Sincronização em Tempo Real:** Criar, editar ou excluir matérias recalcula e atualiza instantaneamente a constelação planetária sem necessidade de recarregar a página.

### 2.3. Grid de Cards de Indicadores (KPIs)
1. **Progresso Ponderado (%):** 
   - Cálculo real que pondera a carga horária de cada disciplina sobre as tarefas cumpridas.
   - Barra de progresso animada com transição fluida (`smooth-progress`).
   - Exibição de comparativo com a média simples.
2. **Horas Estudadas:**
   - Total de tempo real acumulado via cronômetro e registro das tarefas.
3. **Tarefas Concluídas:**
   - Relação de tarefas finalizadas sobre o total e velocidade média calculada em tarefas por semana.
4. **Previsão de Término:**
   - Estimativa analítica de conclusão das metas do semestre baseada no ritmo de estudo atual.

### 2.4. Resumo de Disciplinas e Tarefas Recentes
- Cards de visualização rápida das disciplinas com menor progresso para direcionamento imediato de esforço.
- Lista resumida com status das próximas atividades a vencer.

---

## 3. Comportamento Responsivo
- **Mobile (< 768px):** 
  - O contêiner Three.js ajusta automaticamente sua altura para `220px` mantendo a taxa de quadros e proporção visual.
  - Grid de KPIs é convertido em layout 2x2 para máxima legibilidade sem rolagem lateral.
  - Botões do Hero empilham-se ou tornam-se de toque integral com 100% de largura.
- **Tablet (768px - 1023px):** Contêiner 3D com altura de `280px` e grid de KPIs distribuído harmoniosamente.
- **Desktop (>= 1024px):** Altura completa de `360px`, grid em 4 colunas com micro-animações sutis de inclinação (`rotateX(2deg)`) no hover.

---

## 4. Endpoints de Integração Backend
| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/analytics/progress` | Retorna o progresso ponderado, tempo total, velocidade e previsão |
| `GET` | `/api/subjects` | Consulta as disciplinas para alimentar os dados do universo 3D |
| `GET` | `/api/tasks` | Lista as atividades para cômputo dos status e horas |
