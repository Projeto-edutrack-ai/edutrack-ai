# 📖 Catálogo de Telas & Interfaces — EduTrack AI

Bem-vindo à documentação oficial das interfaces e telas desenvolvidas para a plataforma **EduTrack AI — Assistente Educacional Personalizado**.

Cada documento abaixo detalha a arquitetura visual, componentes, integração com APIs e o comportamento responsivo de cada tela da aplicação:

---

## 📑 Lista de Documentações por Tela

| Tela | Nome do Módulo | Arquivo de Documentação | Principais Tecnologias |
|---|---|---|---|
| **01** | **Autenticação, Cadastro & Recuperação de Senha** | [TELA_01_AUTENTICACAO_E_RECUPERACAO.md](file:///C:/Users/luisf/.gemini/antigravity/scratch/edutrack-ai/docs/telas/TELA_01_AUTENTICACAO_E_RECUPERACAO.md) | JWT, Tailwind CSS, Glassmorphism, Modal Interativo |
| **02** | **Dashboard 3D, KPIs & Scroll World** | [TELA_02_DASHBOARD_3D_E_KPIS.md](file:///C:/Users/luisf/.gemini/antigravity/scratch/edutrack-ai/docs/telas/TELA_02_DASHBOARD_3D_E_KPIS.md) | Three.js, GSAP ScrollTrigger, Parallax, Python Analytics |
| **03** | **Gerenciamento de Disciplinas** | [TELA_03_DISCIPLINAS.md](file:///C:/Users/luisf/.gemini/antigravity/scratch/edutrack-ai/docs/telas/TELA_03_DISCIPLINAS.md) | CRUD Ponderado, Carga Horária, GSAP Stagger |
| **04** | **Tarefas, Estudos & Cronômetro** | [TELA_04_TAREFAS_E_CRONOMETRO.md](file:///C:/Users/luisf/.gemini/antigravity/scratch/edutrack-ai/docs/telas/TELA_04_TAREFAS_E_CRONOMETRO.md) | Cronômetro ao vivo, Desvio Tempo Real vs. Estimado |
| **05** | **Insights de IA & Relatórios em PDF** | [TELA_05_INSIGHTS_DE_IA_E_PDF.md](file:///C:/Users/luisf/.gemini/antigravity/scratch/edutrack-ai/docs/telas/TELA_05_INSIGHTS_DE_IA_E_PDF.md) | Motor Heurístico de IA, ReportLab PDF com gráficos |
| **06** | **Perfil Acadêmico do Estudante** | [TELA_06_PERFIL_ACADEMICO.md](file:///C:/Users/luisf/.gemini/antigravity/scratch/edutrack-ai/docs/telas/TELA_06_PERFIL_ACADEMICO.md) | Upload Base64, Presets Unsplash, Edição Acadêmica |

---

## 📱 Diretrizes de Responsividade Adotadas
Todas as telas acima foram construídas e validadas seguindo:
1. **Design Mobile-First:** Suporte nativo para smartphones (< 768px), tablets (768px - 1023px) e desktops widescreen (>= 1024px).
2. **Safe-Area Insets:** Compatibilidade total com barras de navegação de celulares modernos (iOS Safari e Android).
3. **Prevenção de Zoom Indesejado:** Entradas de formulário com tamanho de 16px no mobile.
4. **Touch Targets de 44x44px:** Todos os botões respeitam a diretriz de ergonomia e acessibilidade (WCAG).
