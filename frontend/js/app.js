// ==========================================================================
// Main Application Orchestrator for EduTrack AI
// Manages Tabs, Global Navigation, GSAP Sequences & Three.js Init
// ==========================================================================

const App = {
  activeTab: 'dashboard',

  init() {
    this.initTheme();
    this.bindNavigation();
    this.bindGlobalSearch();

    Auth.init();
    
    // Ao fazer login, carregar todos os dados e (re)iniciar o ScrollWorld com as matérias do aluno
    window.addEventListener('auth-success', () => {
      this.loadAllViews().then(() => {
        // ScrollWorld já ouve 'auth-success' internamente e chamará loadSubjectsAndBuildPlanets
        // Mas garantimos também um init caso ainda não tenha sido feito
        if (typeof ScrollWorld !== 'undefined') {
          if (!ScrollWorld.isInitialized) {
            ScrollWorld.init('scroll-world-container');
          } else {
            ScrollWorld.loadSubjectsAndBuildPlanets();
          }
        }
      });
    });

    // Se já existe token ao carregar a página (sessão mantida), carregar diretamente
    if (API.getToken()) {
      this.loadAllViews();
    }

    // Inicializar Three.js Scroll World e Animações GSAP (com pequeno delay para o DOM estar pronto)
    setTimeout(() => {
      if (typeof ScrollWorld !== 'undefined' && ScrollWorld.init) {
        ScrollWorld.init('scroll-world-container');
      }
      if (typeof AppAnimations !== 'undefined' && AppAnimations.init) {
        AppAnimations.init();
      }
    }, 200);
  },

  initTheme() {
    const isDarkStored = localStorage.getItem('edutrack_dark') === 'true';
    if (isDarkStored) {
      document.documentElement.classList.add('dark');
    }

    const themeToggleBtn = document.getElementById('btn-toggle-theme');
    if (themeToggleBtn) {
      themeToggleBtn.addEventListener('click', () => {
        const isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('edutrack_dark', isDark);
        
        Toast.show(isDark ? 'Tema Escuro ativado.' : 'Tema Claro ativado.', 'info', 2000);

        if (this.activeTab === 'dashboard' && typeof Dashboard !== 'undefined') {
          Dashboard.loadAllDashboardData();
        }
      });
    }
  },

  bindNavigation() {
    const navButtons = document.querySelectorAll('[data-tab-target]');
    navButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.dataset.tabTarget;
        this.switchTab(target);
      });
    });
  },

  switchTab(tabName) {
    this.activeTab = tabName;

    // Atualizar estilo visual dos botões de navegação usando a classe .active
    document.querySelectorAll('[data-tab-target]').forEach(btn => {
      if (btn.dataset.tabTarget === tabName) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Atualizar seções de conteúdo com animação GSAP
    document.querySelectorAll('.tab-view-section').forEach(view => {
      if (view.id === `view-${tabName}`) {
        view.classList.remove('hidden');
        if (typeof AppAnimations !== 'undefined') {
          AppAnimations.animateSectionChange(view);
        }
      } else {
        view.classList.add('hidden');
      }
    });

    // Gatilhos de carregamento sob demanda
    if (tabName === 'dashboard') {
      Dashboard.loadAllDashboardData();
      // Aguarda o container ser visível para que clientWidth != 0 antes de inicializar/redimensionar
      setTimeout(() => {
        if (typeof ScrollWorld !== 'undefined') {
          if (!ScrollWorld.isInitialized) {
            ScrollWorld.init('scroll-world-container');
          } else {
            ScrollWorld.resize();
            ScrollWorld.loadSubjectsAndBuildPlanets();
          }
        }
      }, 120);
    }
    if (tabName === 'subjects') Subjects.loadSubjects();
    if (tabName === 'tasks') Tasks.loadTasks();
    if (tabName === 'insights') Insights.loadInsights();
  },

  bindGlobalSearch() {
    const searchInput = document.getElementById('global-search-input');
    if (searchInput) {
      searchInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
          const query = searchInput.value.trim();
          if (query) {
            this.switchTab('tasks');
            const taskSearchInput = document.getElementById('task-search-input');
            if (taskSearchInput) {
              taskSearchInput.value = query;
              Tasks.loadTasks();
            }
          }
        }
      });
    }
  },

  async loadAllViews() {
    await Promise.all([
      Dashboard.init(),
      Subjects.init(),
      Tasks.init(),
      Insights.init()
    ]);
  }
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
