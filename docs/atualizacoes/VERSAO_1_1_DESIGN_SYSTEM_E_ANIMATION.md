# 🎨 Atualização v1.1 — Design System, Micro-Interações & Animações GSAP

> **Status:** Concluído & Aplicado  
> **Escopo:** Frontend, Tailwind CSS, GSAP 3.12, Three.js Inicial, Parallax e Tema Dark/Light

---

## 1. Contexto da Atualização
Com a base de dados e a API funcionando, o usuário solicitou uma transformação visual completa: transformar uma interface simples em uma experiência **leve, moderna, intuitiva e profissional**, inspirada nos padrões visuais da **Linear, Stripe e Apple**.

---

## 2. O Que Mudou Nesta Versão

### 2.1. Design System & Glassmorphism
- **Variáveis CSS Temáticas:** Definição de paletas para modo claro e modo escuro (`.dark`) com transições suaves de cor.
- **Cartões com Efeito de Vidro (`.pro-card`):** Filtro `backdrop-filter: blur(16px)` com bordas sutis e sombras profundas.
- **Botões com Efeito de Pressão (`.btn-press`, `.btn-gradient`):** Micro-interações táteis de clique que diminuem ligeiramente a escala do botão (`scale(0.96)`) ao toque.

### 2.2. Tipografia Profissional
- Integração via Google Fonts das famílias:
  - **Plus Jakarta Sans:** Usada em títulos e textos corridos para máxima elegibilidade e ar moderno.
  - **JetBrains Mono:** Utilizada para métricas, badges, porcentagens e contadores de tempo.

### 2.3. Animações com GSAP & ScrollTrigger
- **Stagger nas Listas:** Cards de disciplinas e recomendações surgem com um efeito cascata suave (`stagger: 0.08s`).
- **Animação de Números:** Os números dos KPIs no dashboard sobem dinamicamente de 0 até o valor real com interpolação matemática.
- **Transição de Abas:** A troca entre abas deixou de ser instantânea e seca, passando a ter um *fade-in* com subida sutil em Y (`translateY(8px)` para `0`).

### 2.4. Ambient Orbs & Parallax
- Criação de esferas luminosas no fundo da tela (`.ambient-orb`) com desfoque profundo (`blur(90px)`) que criam um efeito de profundidade cósmica enquanto o usuário navega.

### 2.5. Toast Notification System
- Notificações flutuantes animadas (`toastEntrance`) com ícones de sucesso, erro e informação, substituindo alertas intrusivos do navegador.

---

## 3. Arquivos Impactados
- `frontend/css/styles.css`: Criação de todo o design system.
- `frontend/js/animations.js`: Módulo orquestrador do GSAP.
- `frontend/index.html`: Substituição de elementos legados por componentes estilizados.
