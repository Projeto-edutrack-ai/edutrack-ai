# 🪐 Atualização v1.4 — Sistema Solar Planetário 3D & Rotação Livre 360°

> **Status:** Concluído, Integrado & Validado  
> **Escopo:** Three.js Engine, Interatividade 3D, Integração CRUD e Raycasting

---

## 1. Contexto da Atualização
O estudante solicitou uma grande evolução na área interativa 3D:
> *"Nessa parte de interatividade, o usuario pode mover para qualquer lado, além disso cada 'Planetas' será uma materia criada, caso tenha duas materias, terá dois 'Planetas' e assim por diante."*

---

## 2. O Que Mudou Nesta Versão

### 2.1. Correspondência Exata 1:1 de Planetas por Disciplina Criada
- **Geração Procedural de Planetas:**
  - O visualizador 3D deixou de ter nós estáticos fictícios. Agora, cada matéria cadastrada pelo estudante no banco de dados gera exatamente **um planeta orbital 3D**.
  - Se houver 2 matérias cadastradas, a cena renderiza 2 planetas orbitais; se houver 5 matérias, 5 planetas; e assim por diante.
  - **Tamanho Escalar:** O raio da geometria do planeta reflete sua carga horária (disciplinas mais extensas geram planetas maiores).
  - **Identidade Visual Única:** Cada planeta recebe anéis translúcidos em estilo *Sci-Fi* e uma paleta de iluminação específica.
  - **Constelações Conectadas:** Linhas de laser dinâmicas interligam todos os planetas ativos na órbita do sol central.

### 2.2. Movimentação Livre Multidirecional em 360°
- **Arraste Livre em Qualquer Direção:**
  - O usuário pode clicar com o mouse (ou deslizar com os dedos no mobile) e rotacionar a galáxia inteira em **qualquer eixo**: horizontal, vertical ou diagonal.
  - **Inércia Física & Amortecimento:** Ao soltar o mouse, o sistema mantém uma rotação suave com decaimento exponencial de velocidade (`damping`).
- **Zoom com a Roda do Mouse (Wheel):**
  - O usuário pode aproximar ou afastar a câmera espacial para ver detalhes dos planetas ou ter uma visão panorâmica de todo o sistema estelar.
- **Botão "Resetar Vista":**
  - Permite retornar a câmera à posição de observação ideal a qualquer momento com um clique.

### 2.3. Detecção com Raycaster & Tooltip Flutuante
- Ao passar o cursor do mouse sobre qualquer planeta, um algoritmo de projeção vetorial (`Raycaster`) detecta a colisão e abre um cartão flutuante em tempo real exibindo:
  - O nome completo da disciplina.
  - A carga horária da matéria.
  - O total de horas já dedicadas aos estudos.

### 2.4. Sincronização Automática com o CRUD
- Ao criar, editar ou excluir qualquer disciplina na plataforma, o método `ScrollWorld.loadSubjectsAndBuildPlanets()` é disparado automaticamente:
  - Novos planetas entram em órbita instantaneamente.
  - Planetas de matérias excluídas são desmontados da memória da GPU (`dispose`).
  - O badge contador de planetas no topo do canvas atualiza seu número em tempo real.

---

## 3. Arquivos Impactados
- `frontend/js/scroll-world.js`: Reescrita completa da engine com suporte a rotação 360°, zoom, raycast e instanciação dinâmica.
- `frontend/index.html`: Novo overlay com dicas de interação, botão de resetar vista e badge de contagem de planetas.
- `frontend/js/subjects.js`: Gatilhos de atualização do ScrollWorld nas funções de criação, edição e exclusão.
- `frontend/js/dashboard.js`: Atualização da constelação ao carregar os dados iniciais do estudante.
