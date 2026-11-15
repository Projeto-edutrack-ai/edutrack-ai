// API Client for EduTrack AI - Integrado com Xano CRUD APIs
const API_BASE = (window.EDUTRACK_CONFIG?.apiBase || `${window.location.origin}/api`).replace(/\/$/, '');

const API = {
  getToken() {
    return localStorage.getItem('edutrack_token');
  },

  setToken(token) {
    localStorage.setItem('edutrack_token', token);
  },

  clearAuth() {
    localStorage.removeItem('edutrack_token');
    localStorage.removeItem('edutrack_user');
    localStorage.removeItem('edutrack_xano_aluno');
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('edutrack_user');
    try {
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  },

  setCurrentUser(user) {
    localStorage.setItem('edutrack_user', JSON.stringify(user));
  },

  // ===== Xano Aluno Session Management (Não substitui autenticação) =====
  getXanoAluno() {
    const raw = localStorage.getItem('edutrack_xano_aluno');
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  setXanoAluno(aluno) {
    if (aluno && aluno.id && aluno.id > 0) {
      localStorage.setItem('edutrack_xano_aluno', JSON.stringify(aluno));
    }
  },

  // O backend (FastAPI) cria/localiza o aluno na tabela `alunos` do Xano, por e-mail (sem duplicar).
  async syncXanoAluno(user) {
    if (!user) return null;
    try {
      const result = await this.request('/auth/xano-sync', { method: 'POST' });
      if (result && result.aluno) {
        this.setXanoAluno(result.aluno);
        return result.aluno;
      }
      console.warn('[Xano] Sincronização do aluno não concluída:', result && result.detail);
    } catch (err) {
      console.warn('[Xano] Falha ao sincronizar aluno:', err);
    }
    localStorage.removeItem('edutrack_xano_aluno');
    return null;
  },

  // ===== Requisições genéricas para a API local (Auth e Analytics) =====
  async request(endpoint, options = {}) {
    const token = this.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });

      if (response.status === 401) {
        this.clearAuth();
        window.dispatchEvent(new CustomEvent('auth-changed'));
        throw new Error('Sessão expirada. Faça login novamente.');
      }

      if (response.headers.get('content-type')?.includes('application/pdf')) {
        return response.blob();
      }

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Erro na requisição.');
      }
      return data;
    } catch (error) {
      console.error(`[API Error] ${endpoint}:`, error);
      throw error;
    }
  },

  // ===== Requisições para o grupo CRUD do Xano (/alunos, /materias, /tarefas) =====
  async xanoRequest(endpoint, options = {}) {
    return this.request(`/xano${endpoint}`, options);
  },

  // ==========================================
  // Auth Endpoints (Preservada autenticação)
  // ==========================================
  // O backend já sincroniza o aluno com o Xano e devolve o resultado em `xano_sync`.
  _storeXanoSync(res) {
    localStorage.removeItem('edutrack_xano_aluno');
    if (res && res.xano_sync && res.xano_sync.aluno) {
      this.setXanoAluno(res.xano_sync.aluno);
    }
    return res;
  },

  async login(email, password) {
    const res = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    return this._storeXanoSync(res);
  },

  async register(name, email, password) {
    const res = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password })
    });
    return this._storeXanoSync(res);
  },

  forgotPassword(email) {
    return this.request('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email })
    });
  },

  resetPassword(token, newPassword) {
    return this.request('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword })
    });
  },

  // ==========================================
  // Perfil do Aluno (Consultar e Editar em /alunos)
  // ==========================================
  async getProfile() {
    const user = this.getCurrentUser();
    let xanoAluno = this.getXanoAluno();

    if (!xanoAluno && user) {
      xanoAluno = await this.syncXanoAluno(user);
    }

    if (xanoAluno && xanoAluno.id && xanoAluno.id > 0) {
      try {
        const fresh = await this.xanoRequest(`/alunos/${xanoAluno.id}`, { method: 'GET' });
        if (fresh && fresh.id) {
          this.setXanoAluno(fresh);
          return {
            ...user,
            name: fresh.nome || user.name,
            course: fresh.curso || user.course,
            college_year: fresh.semestre ? `${fresh.semestre}º Semestre` : user.college_year
          };
        }
      } catch (err) {
        console.warn('[Xano] Falha ao consultar aluno no Xano:', err);
      }
    }
    return user;
  },

  async updateProfile(profileData) {
    const user = this.getCurrentUser() || {};
    let xanoAluno = this.getXanoAluno();

    if (!xanoAluno && user) {
      xanoAluno = await this.syncXanoAluno(user);
    }

    if (xanoAluno && xanoAluno.id && xanoAluno.id > 0) {
      let sem = parseInt(profileData.college_year);
      if (isNaN(sem) || sem <= 0) {
        sem = xanoAluno.semestre || 1;
      }

      // Preserva campos não alterados
      const patchPayload = {
        nome: profileData.name !== undefined ? profileData.name.trim() : xanoAluno.nome,
        curso: profileData.course !== undefined ? (profileData.course || '').trim() : xanoAluno.curso,
        semestre: sem
      };

      const updatedAluno = await this.xanoRequest(`/alunos/${xanoAluno.id}`, {
        method: 'PATCH',
        body: JSON.stringify(patchPayload)
      });
      this.setXanoAluno(updatedAluno);
    }

    const updatedUser = await this.request('/auth/profile', {
      method:'PUT', body:JSON.stringify(profileData)
    });
    this.setCurrentUser(updatedUser);
    return updatedUser;
  },

  // ==========================================
  // MATÉRIAS (CRUD Xano /materias)
  // ==========================================
  async getSubjects(search = '') {
    const currentAluno = this.getXanoAluno();

    const [materiasData, tarefasData] = await Promise.all([
      this.xanoRequest('/materias', { method: 'GET' }),
      this.xanoRequest('/tarefas', { method: 'GET' })
    ]);

    let materias = Array.isArray(materiasData) ? materiasData : (materiasData?.items || []);
    const tarefas = Array.isArray(tarefasData) ? tarefasData : (tarefasData?.items || []);

    // Cada aluno vê somente as próprias matérias (sem cair para as de outros alunos)
    if (currentAluno && currentAluno.id && currentAluno.id > 0) {
      materias = materias.filter(m => m.alunos_id === currentAluno.id);
    } else {
      materias = [];
    }

    let mapped = materias.map(m => {
      const mTasks = tarefas.filter(t => t.materias_id === m.id);
      const total = mTasks.length;
      const completed = mTasks.filter(t => (t.status ?? t.status_ ?? '').trim() === 'concluida').length;
      const pct = total > 0 ? Math.round((completed / total) * 100) : 0;

      return {
        id: m.id,
        alunos_id: m.alunos_id,
        name: m.nome,
        professor: m.professor || null,
        description: m.descricao || null,
        workload_hours: m.carga_horaria || 60,
        total_tasks: total,
        completed_tasks: completed,
        progress_percentage: pct,
        total_time_spent_minutes: mTasks.reduce((sum,t) => sum + Number(t.actual_time_minutes || 0), 0)
      };
    });

    if (search) {
      const q = search.toLowerCase();
      mapped = mapped.filter(m =>
        (m.name && m.name.toLowerCase().includes(q)) ||
        (m.professor && m.professor.toLowerCase().includes(q)) ||
        (m.description && m.description.toLowerCase().includes(q))
      );
    }

    return mapped;
  },

  async getSubject(id) {
    const matId = parseInt(id);
    if (!matId || matId <= 0) throw new Error('ID de matéria inválido.');

    const m = await this.xanoRequest(`/materias/${matId}`, { method: 'GET' });
    return {
      id: m.id,
      alunos_id: m.alunos_id,
      name: m.nome,
      professor: m.professor || '',
      description: m.descricao || '',
      workload_hours: m.carga_horaria || 60
    };
  },

  async createSubject(subjectData) {
    let currentAluno = this.getXanoAluno();
    if (!currentAluno || !currentAluno.id || currentAluno.id <= 0) {
      const user = this.getCurrentUser();
      currentAluno = await this.syncXanoAluno(user);
    }
    const alunoId = currentAluno ? currentAluno.id : 0;
    if (!alunoId || alunoId <= 0) {
      throw new Error('Não foi possível vincular sua conta ao Xano. Verifique a conexão e tente novamente.');
    }

    const payload = {
      alunos_id: alunoId,
      nome: subjectData.name.trim(),
      professor: (subjectData.professor || '').trim(),
      descricao: (subjectData.description || '').trim(),
      carga_horaria: parseFloat(subjectData.workload_hours) || 60
    };

    const res = await this.xanoRequest('/materias', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    return {
      id: res.id,
      alunos_id: res.alunos_id,
      name: res.nome,
      professor: res.professor,
      description: res.descricao,
      workload_hours: res.carga_horaria,
      total_tasks: 0,
      completed_tasks: 0,
      progress_percentage: 0,
      total_time_spent_minutes: 0
    };
  },

  async updateSubject(id, subjectData) {
    const matId = parseInt(id);
    if (!matId || matId <= 0) {
      throw new Error('Identificador de matéria inválido (não pode ser zero).');
    }

    // Preserva campos não alterados
    const existing = await this.getSubject(matId).catch(() => ({}));

    const payload = {
      nome: subjectData.name !== undefined ? subjectData.name.trim() : existing.name,
      professor: subjectData.professor !== undefined ? (subjectData.professor || '').trim() : existing.professor,
      descricao: subjectData.description !== undefined ? (subjectData.description || '').trim() : existing.description,
      carga_horaria: subjectData.workload_hours !== undefined ? (parseFloat(subjectData.workload_hours) || 60) : existing.workload_hours
    };

    const res = await this.xanoRequest(`/materias/${matId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    });

    return {
      id: res.id,
      alunos_id: res.alunos_id,
      name: res.nome,
      professor: res.professor,
      description: res.descricao,
      workload_hours: res.carga_horaria
    };
  },

  async deleteSubject(id) {
    const matId = parseInt(id);
    if (!matId || matId <= 0) {
      throw new Error('Identificador de matéria inválido (não pode ser zero).');
    }
    await this.xanoRequest(`/materias/${matId}`, { method: 'DELETE' });
    return true;
  },

  // ==========================================
  // TAREFAS (CRUD Xano /tarefas)
  // ==========================================
  async getTasks(params = {}) {
    const [tarefasData, materiasData] = await Promise.all([
      this.xanoRequest('/tarefas', { method: 'GET' }),
      this.xanoRequest('/materias', { method: 'GET' })
    ]);

    const allMaterias = Array.isArray(materiasData) ? materiasData : (materiasData?.items || []);
    const currentAlunoT = this.getXanoAluno();
    const materias = currentAlunoT && currentAlunoT.id > 0
      ? allMaterias.filter(m => m.alunos_id === currentAlunoT.id)
      : [];
    const materiaIds = new Set(materias.map(m => m.id));
    const allTarefas = Array.isArray(tarefasData) ? tarefasData : (tarefasData?.items || []);
    const tarefas = allTarefas.filter(t => materiaIds.has(t.materias_id));
    const matMap = Object.fromEntries(materias.map(m => [m.id, m.nome]));

    let mapped = tarefas.map(t => {
      // Campo 'status' (Xano renomeou status_ → status)
      // Valores: 'pendente', 'em_andamento ' (com espaço!), 'concluida'
      const rawStatus = (t.status ?? t.status_ ?? '').trim();
      let statusUi = 'pending';
      if (rawStatus === 'concluida') statusUi = 'completed';
      else if (rawStatus === 'em_andamento') statusUi = 'in_progress';

      return {
        id: t.id,
        subject_id: t.materias_id,
        subject_name: matMap[t.materias_id] || `Matéria ${t.materias_id}`,
        title: t.titulo_ || 'Sem título',
        description: t.descricao || '',
        due_date: t.prazo ? (typeof t.prazo === 'number' ? new Date(t.prazo).toISOString() : t.prazo) : null,
        status: statusUi,
        xano_status: t.status,  // valor raw do Xano
        estimated_time_minutes: Number(t.estimated_time_minutes ?? 60),
        actual_time_minutes: Number(t.actual_time_minutes ?? 0)
      };
    });

    if (params.subject_id) {
      const sId = parseInt(params.subject_id);
      mapped = mapped.filter(t => t.subject_id === sId);
    }

    if (params.status && params.status !== 'all') {
      mapped = mapped.filter(t => t.status === params.status);
    }

    if (params.search) {
      const q = params.search.toLowerCase();
      mapped = mapped.filter(t =>
        (t.title && t.title.toLowerCase().includes(q)) ||
        (t.description && t.description.toLowerCase().includes(q))
      );
    }

    return mapped;
  },

  async getTask(id) {
    const tarId = parseInt(id);
    if (!tarId || tarId <= 0) throw new Error('ID de tarefa inválido.');

    const t = await this.xanoRequest(`/tarefas/${tarId}`, { method: 'GET' });
    const rawStatus = (t.status ?? t.status_ ?? '').trim();
    let statusUi = 'pending';
    if (rawStatus === 'concluida') statusUi = 'completed';
    else if (rawStatus === 'em_andamento') statusUi = 'in_progress';

    return {
      id: t.id,
      subject_id: t.materias_id,
      title: t.titulo_,
      description: t.descricao || '',
      due_date: t.prazo ? (typeof t.prazo === 'number' ? new Date(t.prazo).toISOString() : t.prazo) : null,
      status: statusUi,
      xano_status: t.status,
      estimated_time_minutes: Number(t.estimated_time_minutes ?? 60),
      actual_time_minutes: Number(t.actual_time_minutes ?? 0)
    };
  },

  async createTask(taskData) {
    const matId = parseInt(taskData.subject_id);
    if (!matId || matId <= 0) {
      throw new Error('Selecione uma matéria válida vinculada (não pode ser zero).');
    }

    // Campo 'status' (Xano renomeou status_ → status)
    // Valores aceitos: 'pendente', 'em_andamento ' (com espaço!), 'concluida'
    let xanoStatus = 'pendente';
    if (taskData.status === 'completed') xanoStatus = 'concluida';
    else if (taskData.status === 'in_progress') xanoStatus = 'em_andamento ';

    let prazoMs = null;
    if (taskData.due_date) {
      const ms = new Date(taskData.due_date).getTime();
      if (!isNaN(ms)) prazoMs = ms;
    }

    const payload = {
      materias_id: matId,
      titulo_: (taskData.title || '').trim(),
      estimated_time_minutes: taskData.estimated_time_minutes ?? 60,
      actual_time_minutes: taskData.actual_time_minutes ?? 0,
      descricao: (taskData.description || '').trim(),
      prazo: prazoMs,
      status: xanoStatus
    };

    const res = await this.xanoRequest('/tarefas', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    const rawStatus = (res.status || '').trim();
    const statusUi = rawStatus === 'concluida' ? 'completed'
                   : rawStatus === 'em_andamento' ? 'in_progress'
                   : 'pending';

    return {
      id: res.id,
      subject_id: res.materias_id,
      title: res.titulo_,
      description: res.descricao,
      due_date: res.prazo ? new Date(res.prazo).toISOString() : null,
      status: statusUi,
      xano_status: res.status,
      estimated_time_minutes: Number(res.estimated_time_minutes ?? taskData.estimated_time_minutes ?? 60),
      actual_time_minutes: Number(res.actual_time_minutes ?? taskData.actual_time_minutes ?? 0)
    };
  },

  async updateTask(id, taskData) {
    const tarId = parseInt(id);
    if (!tarId || tarId <= 0) {
      throw new Error('Identificador de tarefa inválido (não pode ser zero).');
    }

    // Preserva campos não alterados
    const existing = await this.getTask(tarId).catch(() => ({}));

    const matId = taskData.subject_id !== undefined ? parseInt(taskData.subject_id) : existing.subject_id;
    if (!matId || matId <= 0) {
      throw new Error('Matéria vinculada inválida (não pode ser zero).');
    }

    // Resolve status usando campo 'status' (Xano renomeou status_ → status)
    let xanoStatus = existing.xano_status || 'pendente';
    if (taskData.status !== undefined) {
      if (taskData.status === 'completed') xanoStatus = 'concluida';
      else if (taskData.status === 'in_progress') xanoStatus = 'em_andamento ';
      else xanoStatus = 'pendente';
    } else if (taskData.xano_status !== undefined) {
      xanoStatus = taskData.xano_status;
    }

    let prazoMs = existing.due_date ? new Date(existing.due_date).getTime() : null;
    if (taskData.due_date !== undefined) {
      if (taskData.due_date) {
        const ms = new Date(taskData.due_date).getTime();
        prazoMs = !isNaN(ms) ? ms : null;
      } else {
        prazoMs = null;
      }
    }

    const payload = {
      materias_id: matId,
      titulo_: taskData.title !== undefined ? taskData.title.trim() : existing.title,
      estimated_time_minutes: taskData.estimated_time_minutes ?? existing.estimated_time_minutes ?? 60,
      actual_time_minutes: taskData.actual_time_minutes ?? existing.actual_time_minutes ?? 0,
      descricao: taskData.description !== undefined ? (taskData.description || '').trim() : existing.description,
      prazo: prazoMs,
      status: xanoStatus
    };

    const res = await this.xanoRequest(`/tarefas/${tarId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    });

    const rawResStatus = (res.status || '').trim();
    const statusUi = rawResStatus === 'concluida' ? 'completed'
                   : rawResStatus === 'em_andamento' ? 'in_progress'
                   : 'pending';

    return {
      id: res.id,
      subject_id: res.materias_id,
      title: res.titulo_,
      description: res.descricao,
      due_date: res.prazo ? new Date(res.prazo).toISOString() : null,
      status: statusUi,
      xano_status: res.status,
      estimated_time_minutes: Number(res.estimated_time_minutes ?? payload.estimated_time_minutes ?? 60),
      actual_time_minutes: Number(res.actual_time_minutes ?? payload.actual_time_minutes ?? 0)
    };
  },

  async deleteTask(id) {
    const tarId = parseInt(id);
    if (!tarId || tarId <= 0) {
      throw new Error('Identificador de tarefa inválido (não pode ser zero).');
    }
    await this.xanoRequest(`/tarefas/${tarId}`, { method: 'DELETE' });
    return true;
  },

  addStudyTime(taskId, minutes, newStatus = null) {
    return this.request(`/academic_tasks/by-xano/${taskId}/study-time`, {
      method: 'POST',
      body: JSON.stringify({
        additional_minutes: minutes,
        new_status: newStatus
      })
    });
  },

  // ==========================================
  // Analytics & Reports
  // ==========================================
  getProgressAnalytics() { return this.request('/analytics/progress'); },
  getTimeDistribution() { return this.request('/analytics/time-spent'); },
  getAIInsights() { return this.request('/ai/insights'); },

  askAI(question) { return this.request('/ai/ask', {method:'POST',body:JSON.stringify({question})}); },

  async downloadWeeklyReport() {
    const blob = await this.request('/reports/generate', {method:'POST'});
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `EduTrack_Relatorio_${new Date().toISOString().slice(0, 10)}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },

  search(query = '', status = null, overdue = false) {
    const params = new URLSearchParams({ q: query, overdue: String(overdue) });
    if (status) params.append('status', status);
    return this.request(`/search?${params.toString()}`);
  }
};
