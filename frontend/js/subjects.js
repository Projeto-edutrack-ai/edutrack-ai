// ==========================================================================
// Subjects Management Module for EduTrack AI (Integrado com Xano /materias)
// Enhanced with GSAP Stagger animations, Toasts & Loading States
// ==========================================================================

const Subjects = {
  currentEditingId: null,

  async init() {
    this.bindEvents();
    await this.loadSubjects();
  },

  async loadSubjects(search = '') {
    const listContainer = document.getElementById('subjects-grid');
    if (!listContainer) return;

    try {
      const subjects = await API.getSubjects(search);
      this.renderSubjectCards(subjects);
      this.updateSubjectSelects(subjects);
    } catch (err) {
      console.error('Erro ao carregar matérias do Xano:', err);
      listContainer.innerHTML = `
        <div class="col-span-full text-center py-12 pro-card border-dashed">
          <p class="text-xs text-rose-500 font-bold mb-2">Erro ao carregar matérias do Xano.</p>
          <p class="text-xs text-slate-400 mb-4">${err.message}</p>
          <button onclick="Subjects.loadSubjects()" class="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold btn-press">
            Tentar Novamente
          </button>
        </div>
      `;
    }
  },

  renderSubjectCards(subjects) {
    const listContainer = document.getElementById('subjects-grid');
    if (!listContainer) return;

    if (!subjects || subjects.length === 0) {
      listContainer.innerHTML = `
        <div class="col-span-full text-center py-16 pro-card border-dashed">
          <div class="w-12 h-12 rounded-2xl bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center text-xl mx-auto mb-3">
            📚
          </div>
          <p class="text-slate-600 dark:text-slate-300 font-bold text-sm">Nenhuma matéria cadastrada ainda.</p>
          <p class="text-xs text-slate-400 mt-1 mb-4">Adicione suas disciplinas do semestre para começar o acompanhamento.</p>
          <button onclick="Subjects.openCreateModal()" class="px-4 py-2.5 btn-gradient rounded-xl text-xs font-bold btn-press shadow-md">
            + Cadastrar Primeira Matéria
          </button>
        </div>
      `;
      return;
    }

    listContainer.innerHTML = subjects.map(s => {
      const cardTitle = s.name || s.nome || 'Sem título';
      const workloadHours = s.workload_hours !== undefined ? s.workload_hours : (s.carga_horaria || 60);
      const hoursSpent = s.total_time_spent_minutes !== undefined ? (s.total_time_spent_minutes / 60).toFixed(1) : '0.0';
      const progress = s.progress_percentage !== undefined ? s.progress_percentage : 0;
      const completedTasks = s.completed_tasks !== undefined ? s.completed_tasks : 0;
      const totalTasks = s.total_tasks !== undefined ? s.total_tasks : 0;
      const subjectId = s.id || '';
      const escapedTitle = cardTitle.replace(/'/g, "\\'");

      return `
        <div class="subject-card pro-card p-5 flex flex-col justify-between hover:shadow-xl transition-all duration-200 group">
          <div>
            <div class="flex items-start justify-between gap-2 mb-3">
              <span class="px-2.5 py-1 text-[11px] font-bold rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border border-blue-200/50 dark:border-blue-800/50">
                📚 ${workloadHours}h Carga Horária
              </span>
              <div class="flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity">
                <button onclick="Subjects.openEditModal(${subjectId})" title="Editar" class="p-1.5 text-slate-400 hover:text-blue-600 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors btn-press">
                  ✏️
                </button>
                <button onclick="Subjects.deleteSubject(${subjectId}, '${escapedTitle}')" title="Excluir" class="p-1.5 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors btn-press">
                  🗑️
                </button>
              </div>
            </div>

            <h3 class="text-base md:text-lg font-bold text-slate-900 dark:text-white mb-1 tracking-tight">${cardTitle}</h3>
            ${s.professor ? `<p class="text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium">👨‍🏫 ${s.professor}</p>` : ''}
            ${s.description ? `<p class="text-xs text-slate-600 dark:text-slate-300 line-clamp-2 mb-4 leading-relaxed">${s.description}</p>` : ''}
          </div>

          <div class="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800/80">
            <div class="flex items-center justify-between text-xs mb-1.5 font-semibold">
              <span class="text-slate-500 dark:text-slate-400">Progresso</span>
              <span class="text-blue-600 dark:text-blue-400">${progress}%</span>
            </div>
            <div class="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden mb-3">
              <div class="bg-gradient-to-r from-blue-600 to-indigo-600 h-full smooth-progress rounded-full" style="width: ${progress}%"></div>
            </div>

            <div class="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 font-medium">
              <span>📝 ${completedTasks} / ${totalTasks} tarefas</span>
              <span>⏱️ ${hoursSpent}h dedicadas</span>
            </div>

            <button onclick="Tasks.openCreateModalForSubject(${subjectId})" class="mt-3.5 w-full py-2 px-3 bg-slate-100/80 hover:bg-blue-50 text-slate-700 hover:text-blue-600 dark:bg-slate-800/80 dark:hover:bg-blue-900/30 dark:text-slate-300 dark:hover:text-blue-400 text-xs font-bold rounded-xl border border-slate-200/60 dark:border-slate-700/60 transition-all btn-press">
              + Nova Tarefa nesta Matéria
            </button>
          </div>
        </div>
      `;
    }).join('');

    if (typeof AppAnimations !== 'undefined') {
      AppAnimations.animateCardsStagger('#subjects-grid', '.subject-card');
    }
  },

  updateSubjectSelects(subjects) {
    const taskSubjSelect = document.getElementById('task-modal-subject-id');
    const filterSubjSelect = document.getElementById('task-filter-subject');

    if (taskSubjSelect) {
      taskSubjSelect.innerHTML = '<option value="">Selecione uma matéria...</option>' +
        subjects.map(s => `<option value="${s.id}">${s.name || s.nome}</option>`).join('');
    }

    if (filterSubjSelect) {
      filterSubjSelect.innerHTML = '<option value="">Todas as Matérias</option>' +
        subjects.map(s => `<option value="${s.id}">${s.name || s.nome}</option>`).join('');
    }
  },

  bindEvents() {
    const createBtn = document.getElementById('btn-new-subject');
    const form = document.getElementById('form-subject-modal');
    const closeBtn = document.getElementById('btn-close-subject-modal');
    const searchInput = document.getElementById('search-subjects-input');

    if (createBtn) createBtn.addEventListener('click', () => this.openCreateModal());
    if (closeBtn) closeBtn.addEventListener('click', () => this.closeModal());
    
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.loadSubjects(e.target.value.trim());
      });
    }

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn ? submitBtn.textContent : 'Salvar';
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.textContent = 'Salvando...';
        }

        const payload = {
          name: document.getElementById('subject-modal-name').value.trim(),
          professor: document.getElementById('subject-modal-professor').value.trim() || null,
          workload_hours: parseFloat(document.getElementById('subject-modal-workload').value) || 60.0,
          description: document.getElementById('subject-modal-description').value.trim() || null
        };

        try {
          if (this.currentEditingId) {
            await API.updateSubject(this.currentEditingId, payload);
            Toast.show('Matéria atualizada com sucesso no Xano!', 'success');
          } else {
            await API.createSubject(payload);
            Toast.show('Nova matéria cadastrada com sucesso no Xano!', 'success');
          }
          this.closeModal();
          await this.loadSubjects();
          if (typeof Dashboard !== 'undefined') Dashboard.loadAllDashboardData();
          if (typeof Tasks !== 'undefined') Tasks.loadTasks();
        } catch (err) {
          Toast.show('Erro ao salvar matéria no Xano: ' + err.message, 'error');
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
          }
        }
      });
    }
  },

  openCreateModal() {
    this.currentEditingId = null;
    document.getElementById('subject-modal-title').textContent = 'Nova Matéria';
    document.getElementById('form-subject-modal').reset();
    document.getElementById('subject-modal-workload').value = '60';
    
    const overlay = document.getElementById('modal-subject-overlay');
    overlay.classList.remove('hidden');
    
    if (typeof AppAnimations !== 'undefined') {
      AppAnimations.animateModalOpen(overlay.querySelector('.card-glass, .pro-card'));
    }
  },

  async openEditModal(id) {
    if (!id || id <= 0) {
      Toast.show('Identificador de matéria inválido.', 'error');
      return;
    }

    try {
      const s = await API.getSubject(id);
      this.currentEditingId = id;
      document.getElementById('subject-modal-title').textContent = 'Editar Matéria';
      document.getElementById('subject-modal-name').value = s.name || '';
      document.getElementById('subject-modal-professor').value = s.professor || '';
      document.getElementById('subject-modal-workload').value = s.workload_hours || 60;
      document.getElementById('subject-modal-description').value = s.description || '';
      
      const overlay = document.getElementById('modal-subject-overlay');
      overlay.classList.remove('hidden');
      
      if (typeof AppAnimations !== 'undefined') {
        AppAnimations.animateModalOpen(overlay.querySelector('.card-glass, .pro-card'));
      }
    } catch (err) {
      Toast.show('Erro ao buscar matéria no Xano: ' + err.message, 'error');
    }
  },

  closeModal() {
    document.getElementById('modal-subject-overlay').classList.add('hidden');
    this.currentEditingId = null;
  },

  async deleteSubject(id, name) {
    if (!id || id <= 0) {
      Toast.show('Identificador de matéria inválido.', 'error');
      return;
    }

    const confirmDel = confirm(`Tem certeza que deseja excluir a matéria "${name}"?\nOs dados correspondentes serão removidos no Xano.`);
    if (!confirmDel) return;

    try {
      await API.deleteSubject(id);
      Toast.show(`Matéria "${name}" removida com sucesso no Xano.`, 'success');
      await this.loadSubjects();
      if (typeof Tasks !== 'undefined') Tasks.loadTasks();
      if (typeof Dashboard !== 'undefined') Dashboard.loadAllDashboardData();
    } catch (err) {
      Toast.show('Erro ao excluir matéria no Xano: ' + err.message, 'error');
    }
  }
};
