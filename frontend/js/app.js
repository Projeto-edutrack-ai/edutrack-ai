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
    Classroom.bindEvents();
    Classroom.handleReturn();
    
    window.addEventListener('auth-success', () => {
      this.loadAllViews();
    });

    if (API.getToken()) {
      this.loadAllViews();
    }

    // Inicializar Three.js Scroll World e Animações GSAP
    setTimeout(() => {
      if (typeof ScrollWorld !== 'undefined' && ScrollWorld.init) {
        ScrollWorld.init('scroll-world-container');
      }
      if (typeof AppAnimations !== 'undefined' && AppAnimations.init) {
        AppAnimations.init();
      }
    }, 150);
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
      const target = btn.dataset.tabTarget;
      const isCurrent = btn.classList.contains('active');

      btn.type = 'button';
      btn.setAttribute('aria-controls', `view-${target}`);
      if (isCurrent) {
        btn.setAttribute('aria-current', 'page');
      } else {
        btn.removeAttribute('aria-current');
      }

      btn.addEventListener('click', () => {
        this.switchTab(target);
      });
    });

    document.querySelectorAll('.tab-view-section').forEach(view => {
      view.setAttribute('aria-hidden', String(view.classList.contains('hidden')));
    });
  },

  switchTab(tabName) {
    const targetView = document.getElementById(`view-${tabName}`);
    if (!targetView) return;

    const isAlreadyVisible = this.activeTab === tabName && !targetView.classList.contains('hidden');
    this.activeTab = tabName;

    // Sincronizar estado visual e semântico no desktop e no mobile.
    document.querySelectorAll('[data-tab-target]').forEach(btn => {
      const isCurrent = btn.dataset.tabTarget === tabName;
      btn.classList.toggle('active', isCurrent);

      if (isCurrent) {
        btn.setAttribute('aria-current', 'page');
      } else {
        btn.removeAttribute('aria-current');
      }
    });

    // Atualizar seções de conteúdo com animação GSAP
    document.querySelectorAll('.tab-view-section').forEach(view => {
      const isTarget = view === targetView;
      view.classList.toggle('hidden', !isTarget);
      view.setAttribute('aria-hidden', String(!isTarget));

      if (isTarget && !isAlreadyVisible) {
        if (typeof AppAnimations !== 'undefined') {
          AppAnimations.animateSectionChange(view);
        }
      }
    });

    // A aba já aberta não precisa reanimar nem refazer chamadas de dados.
    if (isAlreadyVisible) return;

    // Gatilhos de carregamento sob demanda
    if (tabName === 'dashboard') {
      Dashboard.loadAllDashboardData();
      setTimeout(() => {
        if (typeof ScrollWorld !== 'undefined' && !ScrollWorld.isInitialized) {
          ScrollWorld.init('scroll-world-container');
        }
      }, 100);
    }
    if (tabName === 'subjects') { Subjects.loadSubjects(); Classroom.load(); }
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
