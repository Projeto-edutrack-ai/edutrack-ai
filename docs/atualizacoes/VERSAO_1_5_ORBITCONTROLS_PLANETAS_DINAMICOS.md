# VERSAO 1.5 - Sistema Planetario 3D com OrbitControls e Dinamica 1:1 Materia/Planeta

Data: Setembro 2026
Arquivos: scroll-world.js, app.js, styles.css, index.html

## Problema Corrigido
- Cena 3D exibia nos estaticos fixos em vez de planetas dinamicos baseados nas materias do aluno
- Rotacao limitada (so horizontal) sem suporte ao eixo vertical
- Canvas bloqueado por overlays com pointer-events incorretos

## Mudancas Principais

### scroll-world.js - Reescrita Completa

1. Rotacao 360 graus com THREE.OrbitControls oficial (CDN r128)
   - Qualquer direcao: cima, baixo, esquerda, direita, diagonal
   - Amortecimento inercial (dampingFactor = 0.06)
   - Auto-rotate quando o usuario nao interage, pausa ao arrastar
   - Retoma auto-rotate apos 3 segundos

2. Dinamica estrita 1 Materia = 1 Planeta
   - buildPlanets(subjects) cria exatamente 1 planeta por materia
   - 4 materias = 4 planetas, 2 materias = 2 planetas etc.
   - Planetas reconstruidos ao criar/editar/excluir materias

3. Orbitas Visiveis por Planeta
   - Anel de orbita no plano XZ para cada disciplina
   - Distancias escaladas: orbitas internas mais rapidas (Lei Kepleriana)

4. Anel Estilo Saturno
   - Materias com carga >= 60h ganham anel planar RingGeometry

5. Resize Automatico com ResizeObserver
   - Canvas se adapta ao container dinamicamente

6. Listener de Login
   - ScrollWorld ouve auth-success e reconstroi planetas imediatamente

### app.js - Orquestracao Melhorada

- auth-success: chama loadSubjectsAndBuildPlanets() ou init() conforme estado
- Tab dashboard: chama resize() + loadSubjectsAndBuildPlanets() se ja inicializado
- Timeout de 200ms (era 150ms) para garantir dimensoes do container

### styles.css - Correcoes de Interatividade

- canvas: pointer-events: auto (necessario para OrbitControls)
- overlays (> div): pointer-events: none (nao bloqueiam drag)
- botoes dentro de overlays: pointer-events: auto
- Alturas: Mobile 240px, Tablet 300px, Desktop 420px (base 400px)

### index.html

- OrbitControls CDN adicionado apos Three.js no head
- Classes cursor-grab e overflow-hidden movidas para CSS

## Verificacao

- API retorna exatamente 4 materias para o usuario demo
- 8/8 testes pytest passando
- Sintaxe JS valida (node -c)
- Servidor rodando em http://127.0.0.1:8000

## Como Usar

1. Login com aluno@edutrack.edu.br / senha123
2. Dashboard exibe 4 planetas (1 por materia)
3. Arrastar mouse/toque em qualquer direcao para rotacionar
4. Scroll para zoom
5. Hover no planeta exibe tooltip com nome e horas
6. Botao Resetar Vista volta para angulo inicial
7. Criar nova materia = novo planeta aparece em tempo real
