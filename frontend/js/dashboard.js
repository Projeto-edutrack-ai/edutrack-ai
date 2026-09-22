// ==========================================================================
// Dashboard and Analytics Module for EduTrack AI
// Enhanced with GSAP animations, dynamic charts & study timer
// ==========================================================================

let timeDistributionChart = null;
let subjectProgressChart = null;

// Timer State
let timerInterval = null;
let timerSeconds = 0;
let activeTaskId = null;
let isTimerRunning = false;

const Dashboard = {
  async init() {
    this.initTimer();
    await this.loadAllDashboardData();
  },

  async loadAllDashboardData() {
    if (!API.getToken()) return;

    try {
      const [metrics, timeDist, tasks] = await Promise.all([
        API.getProgressAnalytics(),
        API.getTimeDistribution(),
        API.getTasks()
      ]);

      this.renderKPIs(metrics);
      this.renderCharts(metrics, timeDist);
      this.renderUpcomingTasks(tasks);
      this.populateTimerTasksDropdown(tasks);

      // Sincronizar planetas com as disciplinas do estudante
      if (typeof ScrollWorld !== 'undefined' && ScrollWorld.loadSubjectsAndBuildPlanets) {
        ScrollWorld.loadSubjectsAndBuildPlanets();
      }
    } catch (err) {
      console.error('Erro ao carregar dados do dashboard:', err);
    }
  },

  renderKPIs(metrics) {
    const weightedProgressEl = document.getElementById('kpi-weighted-progress');
    const simpleProgressEl = document.getElementById('kpi-simple-progress');
    const totalTimeEl = document.getElementById('kpi-total-time');
    const tasksCountEl = document.getElementById('kpi-tasks-count');
    const velocityEl = document.getElementById('kpi-velocity');
    const forecastEl = document.getElementById('kpi-forecast-date');
    const progressFillEl = document.getElementById('kpi-progress-bar-fill');

    if (weightedProgressEl && typeof AppAnimations !== 'undefined') {
      AppAnimations.animateNumber(weightedProgressEl, metrics.overall_weighted_progress, '%', 0.8);
    } else if (weightedProgressEl) {
      weightedProgressEl.textContent = `${metrics.overall_weighted_progress}%`;
    }

    if (simpleProgressEl) simpleProgressEl.textContent = `Média simples: ${metrics.overall_simple_progress}%`;
    
    if (totalTimeEl && typeof AppAnimations !== 'undefined') {
      AppAnimations.animateNumber(totalTimeEl, metrics.total_study_time_hours, 'h', 0.8);
    } else if (totalTimeEl) {
      totalTimeEl.textContent = `${metrics.total_study_time_hours}h`;
    }

    if (tasksCountEl) tasksCountEl.textContent = `${metrics.completed_tasks} / ${metrics.total_tasks}`;
    if (velocityEl) velocityEl.textContent = `${metrics.study_velocity_tasks_per_week} tarefas/sem`;
    if (forecastEl) forecastEl.textContent = metrics.estimated_completion_date || 'N/A';
    if (progressFillEl) progressFillEl.style.width = `${Math.min(100, metrics.overall_weighted_progress)}%`;
  },

  renderCharts(metrics, timeDist) {
    const isDark = document.documentElement.classList.contains('dark');
    const textColor = isDark ? '#94a3b8' : '#64748b';
    const gridColor = isDark ? 'rgba(51, 65, 85, 0.3)' : 'rgba(241, 245, 249, 0.8)';

    // 1. Gráfico Doughnut: Tempo por Disciplina
    const pieCanvas = document.getElementById('chart-time-distribution');
    if (pieCanvas && typeof Chart !== 'undefined') {
      const labels = timeDist.distribution.map(d => d.subject_name);
      const dataValues = timeDist.distribution.map(d => d.hours_spent);
      const bgColors = [
        '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'
      ];

      if (timeDistributionChart) {
        timeDistributionChart.destroy();
      }

      timeDistributionChart = new Chart(pieCanvas, {
        type: 'doughnut',
        data: {
          labels: labels.length ? labels : ['Sem dados'],
          datasets: [{
            data: dataValues.length ? dataValues : [1],
            backgroundColor: labels.length ? bgColors.slice(0, labels.length) : ['#cbd5e1'],
            borderWidth: 3,
            borderColor: isDark ? '#0f172a' : '#ffffff',
            hoverOffset: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            animateScale: true,
            animateRotate: true,
            duration: 900
          },
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: textColor, font: { family: 'Plus Jakarta Sans', size: 11, weight: '500' }, boxWidth: 12, padding: 12 }
            },
            tooltip: {
              padding: 10,
              cornerRadius: 10,
              callbacks: {
                label: function(ctx) {
                  return ` ${ctx.label}: ${ctx.raw} horas`;
                }
              }
            }
          },
          cutout: '70%'
        }
      });
    }

    // 2. Gráfico de Barras: Tarefas Concluídas vs Pendentes
    const barCanvas = document.getElementById('chart-subject-progress');
    if (barCanvas && typeof Chart !== 'undefined') {
      const subjs = metrics.subjects_breakdown || [];
      const labels = subjs.map(s => s.subject_name);
      const completedData = subjs.map(s => s.completed_tasks);
      const pendingData = subjs.map(s => s.pending_tasks + s.in_progress_tasks);

      if (subjectProgressChart) {
        subjectProgressChart.destroy();
      }

      subjectProgressChart = new Chart(barCanvas, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Concluídas',
              data: completedData,
              backgroundColor: '#10b981',
              borderRadius: 6
            },
            {
              label: 'Pendentes / Andamento',
              data: pendingData,
              backgroundColor: '#3b82f6',
              borderRadius: 6
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            duration: 800,
            easing: 'easeOutQuart'
          },
          scales: {
            x: {
              stacked: true,
              grid: { display: false },
              ticks: { color: textColor, font: { family: 'Plus Jakarta Sans', size: 10 } }
            },
            y: {
              stacked: true,
              beginAtZero: true,
              grid: { color: gridColor },
              ticks: { color: textColor, precision: 0, font: { family: 'Plus Jakarta Sans', size: 10 } }
            }
          },
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: textColor, font: { family: 'Plus Jakarta Sans', size: 11, weight: '500' }, boxWidth: 12, padding: 12 }
            }
          }
        }
      });
    }
  },

  renderUpcomingTasks(tasks) {
    const listEl = document.getElementById('upcoming-tasks-list');
    if (!listEl) return;

    const pendingTasks = tasks
      .filter(t => t.status !== 'completed')
      .sort((a, b) => new Date(a.due_date || '9999-12-31') - new Date(b.due_date || '9999-12-31'))
      .slice(0, 4);

    if (pendingTasks.length === 0) {
      listEl.innerHTML = `
        <div class="text-center py-6 text-slate-400 text-xs font-medium">
          🎉 Nenhuma tarefa pendente no momento!
        </div>
      `;
      return;
    }

    listEl.innerHTML = pendingTasks.map(t => {
      const isUrgent = t.due_date && new Date(t.due_date) < new Date();
      const dateStr = t.due_date ? new Date(t.due_date).toLocaleDateString('pt-BR') : 'Sem prazo';
      const statusBadge = t.status === 'in_progress' 
        ? '<span class="px-2 py-0.5 text-[10px] font-bold rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">Em Andamento</span>'
        : '<span class="px-2 py-0.5 text-[10px] font-bold rounded-md bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">Pendente</span>';

      return `
        <div class="group flex items-center justify-between p-3.5 rounded-xl bg-white/50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-800/80 hover:border-blue-500/40 hover:bg-white dark:hover:bg-slate-800/80 transition-all duration-200 shadow-sm">
          <div class="flex-1 min-w-0 pr-3">
            <div class="flex items-center gap-2">
              <span class="text-[11px] font-bold text-blue-600 dark:text-blue-400 truncate">${t.subject_name || ''}</span>
              ${statusBadge}
            </div>
            <p class="text-xs md:text-sm font-bold text-slate-900 dark:text-slate-100 truncate mt-0.5">${t.title}</p>
            <p class="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 flex items-center gap-1.5 font-medium">
              <span>📅 ${dateStr}</span> ${isUrgent ? '<span class="text-rose-500 font-bold">(Atrasada!)</span>' : ''}
              <span>•</span>
              <span>⏱️ ${t.actual_time_minutes}m / ${t.estimated_time_minutes}m</span>
            </p>
          </div>
          <button onclick="Dashboard.startTimerForTask(${t.id})" class="px-3 py-1.5 bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white dark:bg-blue-900/30 dark:text-blue-300 dark:hover:bg-blue-600 dark:hover:text-white text-xs font-bold rounded-lg transition-all flex items-center gap-1 btn-press shadow-sm">
            ▶️ Estudar
          </button>
        </div>
      `;
    }).join('');

    if (typeof AppAnimations !== 'undefined') {
      AppAnimations.animateCardsStagger('#upcoming-tasks-list', '.group');
    }
  },

  // Cronômetro Interativo de Estudo
  initTimer() {
    const startBtn = document.getElementById('timer-start-btn');
    const pauseBtn = document.getElementById('timer-pause-btn');
    const resetBtn = document.getElementById('timer-reset-btn');
    const saveBtn = document.getElementById('timer-save-btn');
    const selectEl = document.getElementById('timer-task-select');

    if (startBtn) startBtn.addEventListener('click', () => this.startTimer());
    if (pauseBtn) pauseBtn.addEventListener('click', () => this.pauseTimer());
    if (resetBtn) resetBtn.addEventListener('click', () => this.resetTimer());
    if (saveBtn) saveBtn.addEventListener('click', () => this.saveTimerStudyTime());
    if (selectEl) {
      selectEl.addEventListener('change', (e) => {
        activeTaskId = e.target.value ? parseInt(e.target.value) : null;
      });
    }
  },

  populateTimerTasksDropdown(tasks) {
    const selectEl = document.getElementById('timer-task-select');
    if (!selectEl) return;

    const uncompletedTasks = tasks.filter(t => t.status !== 'completed');
    selectEl.innerHTML = '<option value="">-- Selecione uma tarefa para cronometrar --</option>' + 
      uncompletedTasks.map(t => `<option value="${t.id}">${t.subject_name} — ${t.title}</option>`).join('');

    if (activeTaskId) {
      selectEl.value = activeTaskId;
    }
  },

  startTimerForTask(taskId) {
    activeTaskId = taskId;
    const selectEl = document.getElementById('timer-task-select');
    if (selectEl) selectEl.value = taskId;
    
    const timerWidget = document.getElementById('study-timer-widget');
    if (timerWidget) {
      timerWidget.scrollIntoView({ behavior: 'smooth' });
      gsap.fromTo(timerWidget, { scale: 0.98 }, { scale: 1, duration: 0.3, ease: 'back.out(2)' });
    }
    
    this.startTimer();
  },

  startTimer() {
    const selectEl = document.getElementById('timer-task-select');
    if (!activeTaskId && selectEl && selectEl.value) {
      activeTaskId = parseInt(selectEl.value);
    }

    if (!activeTaskId) {
      Toast.show('Selecione uma tarefa na lista antes de iniciar o cronômetro.', 'warning');
      return;
    }

    if (isTimerRunning) return;

    isTimerRunning = true;
    document.getElementById('timer-start-btn').classList.add('hidden');
    document.getElementById('timer-pause-btn').classList.remove('hidden');
    
    const badge = document.getElementById('timer-status-badge');
    badge.textContent = '⏱️ Sessão Ativa';
    badge.className = 'px-2.5 py-0.5 text-xs font-bold rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 timer-running-pulse';

    const widget = document.getElementById('study-timer-widget');
    if (widget) widget.classList.add('timer-running-pulse');

    Toast.show('Cronômetro de estudo iniciado. Bons estudos!', 'success');

    timerInterval = setInterval(() => {
      timerSeconds++;
      this.updateTimerDisplay();
    }, 1000);
  },

  pauseTimer() {
    if (!isTimerRunning) return;
    isTimerRunning = false;
    clearInterval(timerInterval);
    document.getElementById('timer-pause-btn').classList.add('hidden');
    document.getElementById('timer-start-btn').classList.remove('hidden');
    
    const badge = document.getElementById('timer-status-badge');
    badge.textContent = '⏸️ Pausado';
    badge.className = 'px-2.5 py-0.5 text-xs font-bold rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20';

    const widget = document.getElementById('study-timer-widget');
    if (widget) widget.classList.remove('timer-running-pulse');
  },

  resetTimer() {
    this.pauseTimer();
    timerSeconds = 0;
    this.updateTimerDisplay();
    
    const badge = document.getElementById('timer-status-badge');
    badge.textContent = 'Pronto para iniciar';
    badge.className = 'px-2.5 py-0.5 text-xs font-bold rounded-full bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300';
  },

  updateTimerDisplay() {
    const hours = Math.floor(timerSeconds / 3600);
    const mins = Math.floor((timerSeconds % 3600) / 60);
    const secs = timerSeconds % 60;
    
    const formatted = `${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    const displayEl = document.getElementById('timer-display');
    if (displayEl) displayEl.textContent = formatted;
  },

  async saveTimerStudyTime() {
    if (!activeTaskId) {
      Toast.show('Selecione uma tarefa para registrar seu tempo.', 'warning');
      return;
    }

    const minutesToSave = Math.max(1, Math.round(timerSeconds / 60));
    const markAsCompleted = confirm(`Deseja registrar ${minutesToSave} minuto(s) de estudo?\n\nClique OK para marcar a tarefa como CONCLUÍDA ou CANCELAR para manter EM ANDAMENTO.`);
    const newStatus = markAsCompleted ? 'completed' : 'in_progress';

    try {
      await API.addStudyTime(activeTaskId, minutesToSave, newStatus);
      Toast.show(`Tempo registrado com sucesso: +${minutesToSave} minutos!`, 'success');
      this.resetTimer();
      await this.loadAllDashboardData();
      if (typeof Tasks !== 'undefined' && Tasks.loadTasks) Tasks.loadTasks();
      if (typeof Insights !== 'undefined' && Insights.loadInsights) Insights.loadInsights();
    } catch (err) {
      Toast.show('Erro ao salvar tempo: ' + err.message, 'error');
    }
  }
};
