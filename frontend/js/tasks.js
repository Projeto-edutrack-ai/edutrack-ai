// ==========================================================================
// Academic Tasks Management Module for EduTrack AI (Integrado com Xano /tarefas)
// Enhanced with GSAP animations, deviation badges & Toasts
// ==========================================================================

const Tasks = {
  currentEditingId: null,

  async init() {
    this.bindEvents();
    await this.loadTasks();
  },

  async loadTasks() {
    const listContainer = document.getElementById('tasks-container');
    if (!listContainer) return;

    const search = document.getElementById('task-search-input')?.value.trim() || '';
    const subjectId = document.getElementById('task-filter-subject')?.value || '';
    const status = document.querySelector('.task-status-filter-btn.active')?.dataset.status || '';

    try {
      const tasks = await API.getTasks({
        search,
        subject_id: subjectId,
        status: status === 'all' ? '' : status
      });

      this.renderTasks(tasks);
    } catch (err) {
      console.error('Erro ao carregar tarefas do Xano:', err);
      listContainer.innerHTML = `
        <div class="text-center py-12 pro-card border-dashed">
          <p class="text-xs text-rose-500 font-bold mb-2">Erro ao carregar tarefas do Xano.</p>
          <p class="text-xs text-slate-400 mb-4">${err.message}</p>
          <button onclick="Tasks.loadTasks()" class="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold btn-press">
            Tentar Novamente
          </button>
        </div>
      `;
    }
  },

  renderTasks(tasks) {
    const listContainer = document.getElementById('tasks-container');
    if (!listContainer) return;

    if (!tasks || tasks.length === 0) {
      listContainer.innerHTML = `
        <div class="text-center py-16 pro-card border-dashed">
          <div class="w-12 h-12 rounded-2xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-xl mx-auto mb-3">
            📝
          </div>
          <p class="text-slate-600 dark:text-slate-300 font-bold text-sm">Nenhuma tarefa encontrada no Xano.</p>
          <p class="text-xs text-slate-400 mt-1 mb-4">Adicione novas atividades para organizar seu cronograma.</p>
          <button onclick="Tasks.openCreateModal()" class="px-4 py-2.5 btn-gradient rounded-xl text-xs font-bold btn-press shadow-md">
            + Adicionar Nova Tarefa
          </button>
        </div>
      `;
      return;
    }

    listContainer.innerHTML = tasks.map(t => {
      const isCompleted = t.status === 'completed';
      const isOverdue = !isCompleted && t.due_date && new Date(t.due_date) < new Date();
      const dateStr = t.due_date ? new Date(t.due_date).toLocaleDateString('pt-BR') : 'Sem prazo';

      const statusBadge = t.status === 'completed'
        ? '<span class="px-2.5 py-0.5 text-[10px] font-bold rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">Concluída</span>'
        : (t.status === 'in_progress'
          ? '<span class="px-2.5 py-0.5 text-[10px] font-bold rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">Em Andamento</span>'
          : '<span class="px-2.5 py-0.5 text-[10px] font-bold rounded-md bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">Pendente</span>');

      const escapedTitle = (t.title || '').replace(/'/g, "\\'");

      return `
        <div class="task-row-card pro-card p-4 hover:shadow-lg transition-all duration-200 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${isCompleted ? 'opacity-75' : ''}">
          <div class="flex items-start gap-3.5 flex-1 min-w-0">
            <button onclick="Tasks.toggleTaskStatus(${t.id}, '${t.status}')" title="Alternar situação (concluída / pendente)" class="mt-1 w-6 h-6 rounded-lg border flex items-center justify-center transition-all btn-press ${isCompleted ? 'bg-emerald-500 border-emerald-500 text-white shadow-sm' : 'border-slate-300 dark:border-slate-700 bg-white/50 dark:bg-slate-800 hover:border-emerald-500'}">
              ${isCompleted ? '✓' : ''}
            </button>

            <div class="flex-1 min-w-0">
              <div class="flex items-center flex-wrap gap-2 mb-1">
                <span class="px-2 py-0.5 text-[10px] font-bold rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">${t.subject_name || 'Matéria'}</span>
                ${statusBadge}
              </div>

              <h4 class="text-sm md:text-base font-bold text-slate-900 dark:text-white ${isCompleted ? 'line-through text-slate-400 dark:text-slate-500' : ''}">
                ${t.title}
              </h4>
              ${t.description ? `<p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 leading-relaxed">${t.description}</p>` : ''}

              <div class="flex items-center flex-wrap gap-3 mt-2 text-[11px] text-slate-500 dark:text-slate-400 font-medium">
                <span class="${isOverdue ? 'text-rose-500 font-bold' : ''}">
                  📅 ${dateStr} ${isOverdue ? '(Atrasada!)' : ''}
                </span>
                <span>⏱️ Previsto: ${t.estimated_time_minutes || 60}m</span>
                <span class="font-bold text-blue-600 dark:text-blue-400">⏱️ Real: ${t.actual_time_minutes || 0}m</span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-2 self-end md:self-center">
            ${!isCompleted && typeof Dashboard !== 'undefined' && Dashboard.startTimerForTask ? `
              <button onclick="Dashboard.startTimerForTask(${t.id})" class="px-3 py-1.5 btn-gradient text-xs font-bold rounded-xl flex items-center gap-1.5 shadow-md btn-press">
                ▶️ Estudar
              </button>
            ` : ''}
            <button onclick="Tasks.openEditModal(${t.id})" title="Editar" class="p-2 text-slate-400 hover:text-blue-600 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors btn-press">
              ✏️
            </button>
            <button onclick="Tasks.deleteTask(${t.id}, '${escapedTitle}')" title="Excluir" class="p-2 text-slate-400 hover:text-rose-600 rounded-xl hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors btn-press">
              🗑️
            </button>
          </div>
        </div>
      `;
    }).join('');

    if (typeof AppAnimations !== 'undefined') {
      AppAnimations.animateCardsStagger('#tasks-container', '.task-row-card');
    }
  },

  bindEvents() {
    const createBtn = document.getElementById('btn-new-task');
    const form = document.getElementById('form-task-modal');
    const closeBtn = document.getElementById('btn-close-task-modal');
    const searchInput = document.getElementById('task-search-input');
    const filterSubj = document.getElementById('task-filter-subject');
    const filterButtons = document.querySelectorAll('.task-status-filter-btn');

    if (createBtn) createBtn.addEventListener('click', () => this.openCreateModal());
    if (closeBtn) closeBtn.addEventListener('click', () => this.closeModal());

    if (searchInput) {
      searchInput.addEventListener('input', () => this.loadTasks());
    }

    if (filterSubj) {
      filterSubj.addEventListener('change', () => this.loadTasks());
    }

    filterButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        filterButtons.forEach(b => b.classList.remove('active', 'bg-blue-600', 'text-white'));
        btn.classList.add('active', 'bg-blue-600', 'text-white');
        this.loadTasks();
      });
    });

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn ? submitBtn.textContent : 'Salvar';
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.textContent = 'Salvando...';
        }

        const subjVal = document.getElementById('task-modal-subject-id').value;
        const subjectId = parseInt(subjVal);
        if (!subjectId || subjectId <= 0) {
          Toast.show('Por favor, selecione uma matéria válida vinculada.', 'error');
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
          }
          return;
        }

        const dueDateVal = document.getElementById('task-modal-due-date').value;
        const payload = {
          subject_id: subjectId,
          title: document.getElementById('task-modal-title-input').value.trim(),
          description: document.getElementById('task-modal-description').value.trim() || null,
          due_date: dueDateVal ? new Date(dueDateVal).toISOString() : null,
          status: document.getElementById('task-modal-status').value,
          estimated_time_minutes: parseFloat(document.getElementById('task-modal-estimated-time').value) || 60.0,
          actual_time_minutes: parseFloat(document.getElementById('task-modal-actual-time').value) || 0.0
        };

        try {
          if (this.currentEditingId) {
            await API.updateTask(this.currentEditingId, payload);
            Toast.show('Tarefa atualizada com sucesso no Xano!', 'success');
          } else {
            await API.createTask(payload);
            Toast.show('Nova tarefa cadastrada com sucesso no Xano!', 'success');
          }
          this.closeModal();
          await this.loadTasks();
          if (typeof Subjects !== 'undefined') Subjects.loadSubjects();
          if (typeof Dashboard !== 'undefined') Dashboard.loadAllDashboardData();
        } catch (err) {
          Toast.show('Erro ao salvar tarefa no Xano: ' + err.message, 'error');
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
          }
        }
      });
    }
  },

  async openCreateModal() {
    this.currentEditingId = null;
    document.getElementById('task-modal-heading').textContent = 'Nova Tarefa Acadêmica';
    document.getElementById('form-task-modal').reset();
    document.getElementById('task-modal-estimated-time').value = '60';
    document.getElementById('task-modal-actual-time').value = '0';
    
    // Atualiza opções de matérias antes de abrir
    try {
      const subjects = await API.getSubjects();
      Subjects.updateSubjectSelects(subjects);
    } catch (e) {}

    const overlay = document.getElementById('modal-task-overlay');
    overlay.classList.remove('hidden');
    
    if (typeof AppAnimations !== 'undefined') {
      AppAnimations.animateModalOpen(overlay.querySelector('.card-glass, .pro-card'));
    }
  },

  async openCreateModalForSubject(subjectId) {
    if (!subjectId || subjectId <= 0) return;
    await this.openCreateModal();
    const select = document.getElementById('task-modal-subject-id');
    if (select) select.value = String(subjectId);
  },

  async openEditModal(id) {
    if (!id || id <= 0) {
      Toast.show('Identificador de tarefa inválido.', 'error');
      return;
    }

    try {
      // Atualiza opções de matérias
      const subjects = await API.getSubjects();
      Subjects.updateSubjectSelects(subjects);

      const t = await API.getTask(id);
      this.currentEditingId = id;
      document.getElementById('task-modal-heading').textContent = 'Editar Tarefa';
      document.getElementById('task-modal-subject-id').value = String(t.subject_id);
      document.getElementById('task-modal-title-input').value = t.title || '';
      document.getElementById('task-modal-description').value = t.description || '';
      document.getElementById('task-modal-status').value = t.status || 'pending';
      document.getElementById('task-modal-estimated-time').value = t.estimated_time_minutes || 60;
      document.getElementById('task-modal-actual-time').value = t.actual_time_minutes || 0;
      
      if (t.due_date) {
        const d = new Date(t.due_date);
        const pad = n => String(n).padStart(2, '0');
        const localStr = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
        document.getElementById('task-modal-due-date').value = localStr;
      } else {
        document.getElementById('task-modal-due-date').value = '';
      }

      const overlay = document.getElementById('modal-task-overlay');
      overlay.classList.remove('hidden');
      
      if (typeof AppAnimations !== 'undefined') {
        AppAnimations.animateModalOpen(overlay.querySelector('.card-glass, .pro-card'));
      }
    } catch (err) {
      Toast.show('Erro ao carregar tarefa do Xano: ' + err.message, 'error');
    }
  },

  closeModal() {
    document.getElementById('modal-task-overlay').classList.add('hidden');
    this.currentEditingId = null;
  },

  async toggleTaskStatus(id, currentStatus) {
    if (!id || id <= 0) {
      Toast.show('Identificador de tarefa inválido.', 'error');
      return;
    }

    const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    try {
      await API.updateTask(id, { status: newStatus });
      Toast.show(newStatus === 'completed' ? '🎉 Tarefa concluída no Xano!' : 'Tarefa reaberta no Xano.', 'success');
      await this.loadTasks();
      if (typeof Subjects !== 'undefined') Subjects.loadSubjects();
      if (typeof Dashboard !== 'undefined') Dashboard.loadAllDashboardData();
    } catch (err) {
      Toast.show('Erro ao atualizar situação no Xano: ' + err.message, 'error');
    }
  },

  async deleteTask(id, title) {
    if (!id || id <= 0) {
      Toast.show('Identificador de tarefa inválido.', 'error');
      return;
    }

    const confirmDel = confirm(`Tem certeza que deseja excluir a tarefa "${title}"?\nO registro será removido permanentemente no Xano.`);
    if (!confirmDel) return;

    try {
      await API.deleteTask(id);
      Toast.show(`Tarefa "${title}" excluída com sucesso no Xano.`, 'success');
      await this.loadTasks();
      if (typeof Subjects !== 'undefined') Subjects.loadSubjects();
      if (typeof Dashboard !== 'undefined') Dashboard.loadAllDashboardData();
    } catch (err) {
      Toast.show('Erro ao excluir tarefa no Xano: ' + err.message, 'error');
    }
  }
};
