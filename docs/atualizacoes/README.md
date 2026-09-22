# 📜 Histórico de Atualizações & Changelog Geral — EduTrack AI

Este documento detalha o histórico evolutivo completo do **EduTrack AI — Assistente Educacional Personalizado**, desde a sua fundação estrutural até as mais recentes inovações visuais, tridimensionais e de experiência do usuário (UX).

---

## 🗺️ Visão Cronológica das Versões

| Versão | Status | Foco Principal | Destaques |
|---|---|---|---|
| **v1.0** | Concluída | **Fundação do Sistema & OpenSpec** | Arquitetura FastAPI, SQLite, JWT, CRUD de Disciplinas e Tarefas, Ponderação e ReportLab PDF. |
| **v1.1** | Concluída | **Design System & Animações** | Paleta Dark/Light, GSAP, Tailwind CSS, transições fluidas e componentes *glassmorphism*. |
| **v1.2** | Concluída | **Identidade & Perfil do Estudante** | Upload de foto (Base64), presets Unsplash, dados acadêmicos (curso, ano, faculdade, bio). |
| **v1.3** | Concluída | **Responsividade & Recuperação de Senha** | Modal interativo de recuperação de senha, safe-area mobile, bottom nav e micro-interações. |
| **v1.4** | Concluída | **Sistema Planetário 3D Interativo** | Three.js dinâmico (1 planeta por matéria), rotação livre 360° em qualquer direção, zoom e raycaster. |

---

## 📑 Documentos Detalhados de Cada Atualização

Para ler o relatório aprofundado com justificativas técnicas, arquivos modificados e testes de cada ciclo:

- 📦 [**`VERSAO_1_0_FUNDACAO_SISTEMA.md`**](file:///C:/Users/luisf/.gemini/antigravity/scratch/edutrack-ai/docs/atualizacoes/VERSAO_1_0_FUNDACAO_SISTEMA.md) — Criação do backend FastAPI, modelagem relacional, auth JWT, motor analítico e geração de PDF semanal.
- 🎨 [**`VERSAO_1_1_DESIGN_SYSTEM_E_ANIMATION.md`**](file:///C:/Users/luisf/.gemini/antigravity/scratch/edutrack-ai/docs/atualizacoes/VERSAO_1_1_DESIGN_SYSTEM_E_ANIMATION.md) — Redesign estilo Linear/Stripe/Apple, GSAP ScrollTrigger, parallax e micro-interações.
- 👤 [**`VERSAO_1_2_PERFIL_ACADEMICO_E_FOTO.md`**](file:///C:/Users/luisf/.gemini/antigravity/scratch/edutrack-ai/docs/atualizacoes/VERSAO_1_2_PERFIL_ACADEMICO_E_FOTO.md) — Central de customização do aluno, upload de avatar, monograma de iniciais e dados curriculares.
- 📱 [**`VERSAO_1_3_RESPONSIVIDADE_E_RECUPERACAO_SENHA.md`**](file:///C:/Users/luisf/.gemini/antigravity/scratch/edutrack-ai/docs/atualizacoes/VERSAO_1_3_RESPONSIVIDADE_E_RECUPERACAO_SENHA.md) — Adaptação para mobile e tablet, touch targets de 44px e modal dedicado para esqueci minha senha.
- 🪐 [**`VERSAO_1_4_SISTEMA_PLANETARIO_3D.md`**](file:///C:/Users/luisf/.gemini/antigravity/scratch/edutrack-ai/docs/atualizacoes/VERSAO_1_4_SISTEMA_PLANETARIO_3D.md) — Galáxia interativa onde cada disciplina gera um planeta orbital com rotação livre 360° e zoom.

---

## 📊 Resumo Comparativo: O Que Mudou

```
+-----------------------------------------------------------------------------------+
| ANTES (Versões Iniciais)            | DEPOIS (Versões Recentes)                   |
+-------------------------------------+---------------------------------------------+
| • Nós 3D estáticos predefinidos     | • 1 Planeta 3D gerado para cada disciplina  |
| • Rotação 3D apenas via scroll      | • Arraste livre 360° em qualquer direção    |
| • Prompt simples de recuperação     | • Modal profissional estilizado com alerta  |
| • Perfil genérico fixo              | • Upload de foto, 4 presets e dados do curso|
| • Layout desktop básico             | • 100% responsivo (Mobile, Tablet, Desktop) |
+-----------------------------------------------------------------------------------+
```
