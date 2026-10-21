// API Client for EduTrack AI - Integrado com Xano CRUD APIs
const API_BASE = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
  ? `${window.location.origin}/api`
  : 'http://localhost:8000/api';

// URL Base do grupo de CRUD do Xano
const XANO_BASE_URL = 'https://x8ki-letl-twmt.n7.xano.io/api:d_CNfVCs';

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

  async syncXanoAluno(user) {
    if (!user) return null;
    try {
      const alunos = await this.xanoRequest('/alunos', { method: 'GET' });
      const list = Array.isArray(alunos) ? alunos : (alunos?.items || []);
      
      // Busca aluno pelo e-mail do usuário autenticado
      let matched = list.find(a => a.email && a.email.toLowerCase() === (user.email || '').toLowerCase());

      if (!matched && list.length > 0) {
        // Fallback por nome
        matched = list.find(a => a.nome && a.nome.toLowerCase() === (user.name || '').toLowerCase());
      }

      if (!matched) {
        // Cadastra novo aluno no Xano para este usuário (dinâmico, sem fixar ID 1)
        matched = await this.xanoRequest('/alunos', {
          method: 'POST',
          body: JSON.stringify({
            nome: user.name || 'Estudante',
            email: user.email || `aluno_${Date.now()}@edutrack.edu.br`,
            curso: user.course || 'Ciência da Computação',
            semestre: parseInt(user.college_year) || 1
          })
        });
      }

      if (matched && matched.id > 0) {
        this.setXanoAluno(matched);
      }
      return matched;
    } catch (err) {
      console.warn('[Xano] Falha ao sincronizar aluno:', err);
      return this.getXanoAluno();
    }
  },

  // ===== Requisições genéricas para a API local (Auth, Analytics, Classroom) =====
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
    const url = `${XANO_BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      if (!response.ok) {
        let errorMsg = `Erro na API Xano (${response.status})`;
        try {
          const errData = await response.json();
          errorMsg = errData.message || errData.payload?.message || errorMsg;
        } catch {
          errorMsg = response.statusText || errorMsg;
        }
        throw new Error(errorMsg);
      }

      if (response.status === 204) {
        return null;
      }

      return await response.json();
    } catch (error) {
      console.error(`[Xano Error] ${options.method || 'GET'} ${endpoint}:`, error);
      throw error;
    }
  },

  // ==========================================
  // Auth Endpoints (Preservada autenticação)
  // ==========================================
  async login(email, password) {
    const res = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (res && res.user) {
      // Sincroniza em segundo plano com a tabela alunos do Xano
      this.syncXanoAluno(res.user).catch(() => {});
    }
    return res;
  },

  register(name, email, password) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password })
    });
  },

  forgotPassword(email) {
    return this.request('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email })
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

    // Atualiza dados locais do estudante
    const updatedUser = {
      ...user,
      name: profileData.name !== undefined ? profileData.name : user.name,
      course: profileData.course !== undefined ? profileData.course : user.course,
      college_year: profileData.college_year !== undefined ? profileData.college_year : user.college_year,
      institution: profileData.institution !== undefined ? profileData.institution : user.institution,
      bio: profileData.bio !== undefined ? profileData.bio : user.bio,
      avatar_url: profileData.avatar_url !== undefined ? profileData.avatar_url : user.avatar_url
    };
    this.setCurrentUser(updatedUser);

    // Tenta atualizar no backend local também se houver token
    if (this.getToken()) {
      try {
        await this.request('/auth/profile', {
          method: 'PUT',
          body: JSON.stringify(profileData)
        });
      } catch (e) {
        console.warn('Atualização local de perfil ignorada:', e);
      }
    }

    return updatedUser;
  },

  // ==========================================
  // MATÉRIAS (CRUD Xano /materias)
  // ==========================================
  async getSubjects(search = '') {
    const currentAluno = this.getXanoAluno();

    const [materiasData, tarefasData] = await Promise.all([
      this.xanoRequest('/materias', { method: 'GET' }),
      this.xanoRequest('/tarefas', { method: 'GET' }).catch(() => [])
    ]);

    let materias = Array.isArray(materiasData) ? materiasData : (materiasData?.items || []);
    const tarefas = Array.isArray(tarefasData) ? tarefasData : (tarefasData?.items || []);

    // Se temos um aluno identificado, filtramos as matérias dele (se existirem)
    if (currentAluno && currentAluno.id && currentAluno.id > 0) {
      const alunoMaterias = materias.filter(m => m.alunos_id === currentAluno.id);
      if (alunoMaterias.length > 0) {
        materias = alunoMaterias;
      }
    }

    let mapped = materias.map(m => {
      const mTasks = tarefas.filter(t => t.materias_id === m.id);
      const total = mTasks.length;
      const completed = mTasks.filter(t => (t.status_ || '').trim() === 'concluida').length;
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
        total_time_spent_minutes: completed * 60
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
    const alunoId = currentAluno ? currentAluno.id : 1;
    if (!alunoId || alunoId <= 0) {
      throw new Error('Identificador de aluno inválido (não pode ser zero).');
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
      this.xanoRequest('/materias', { method: 'GET' }).catch(() => [])
    ]);

    const tarefas = Array.isArray(tarefasData) ? tarefasData : (tarefasData?.items || []);
    const materias = Array.isArray(materiasData) ? materiasData : (materiasData?.items || []);
    const matMap = Object.fromEntries(materias.map(m => [m.id, m.nome]));

    let mapped = tarefas.map(t => {
      // Campo 'status' (Xano renomeou status_ → status)
      // Valores: 'pendente', 'em_andamento ' (com espaço!), 'concluida'
      const rawStatus = (t.status || '').trim();
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
        estimated_time_minutes: 60,
        actual_time_minutes: statusUi === 'completed' ? 60 : 0
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
    const rawStatus = (t.status || '').trim();
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
      estimated_time_minutes: 60,
      actual_time_minutes: statusUi === 'completed' ? 60 : 0
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
      estimated_time_minutes: parseFloat(taskData.estimated_time_minutes) || 60,
      actual_time_minutes: parseFloat(taskData.actual_time_minutes) || 0
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
      estimated_time_minutes: 60,
      actual_time_minutes: statusUi === 'completed' ? 60 : 0
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
    return this.request(`/academic_tasks/${taskId}/study-time`, {
      method: 'POST',
      body: JSON.stringify({
        additional_minutes: minutes,
        new_status: newStatus
      })
    }).catch(err => {
      console.warn('Registro de tempo local:', err);
    });
  },

  // ==========================================
  // Analytics & Reports
  // ==========================================
  getProgressAnalytics() {
    return this.request('/analytics/progress').catch(() => ({
      overall_weighted_progress: 0,
      overall_simple_progress: 0,
      total_time_spent_hours: 0,
      total_tasks_completed: 0,
      total_tasks: 0,
      study_velocity_tasks_per_week: 0,
      projected_completion_date: 'N/A'
    }));
  },

  getTimeDistribution() {
    return this.request('/analytics/time-spent').catch(() => []);
  },

  getAIInsights() {
    return this.request('/ai/insights').catch(() => ({
      summary: 'Análise indisponível no momento.',
      recommendations: []
    }));
  },

  async downloadWeeklyReport() {
    const blob = await this.request('/reports/weekly-pdf');
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `EduTrack_Relatorio_${new Date().toISOString().slice(0, 10)}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },

  search(query, status = null) {
    const params = new URLSearchParams({ q: query });
    if (status) params.append('status', status);
    return this.request(`/search?${params.toString()}`);
  },

  // Google Classroom endpoints (preservados caso existam)
  classroomStatus() {
    return this.request('/classroom/status').catch(() => ({ connected: false }));
  },

  classroomConnect() {
    return this.request('/classroom/connect', { method: 'POST' });
  },

  classroomSync(refresh = true) {
    return this.request('/classroom/sync', {
      method: 'POST',
      body: JSON.stringify({ refresh })
    });
  },

  classroomCourses() {
    return this.request('/classroom/courses');
  },

  classroomTasks(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') query.set(k, v); });
    const qs = query.toString();
    return this.request(`/classroom/tasks${qs ? `?${qs}` : ''}`);
  },

  classroomDisconnect() {
    return this.request('/classroom/connection', { method: 'DELETE' });
  }
};
