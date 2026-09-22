// API Client for EduTrack AI
const API_BASE = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
  ? `${window.location.origin}/api`
  : 'http://localhost:8000/api';

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

  // Auth Endpoints
  login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
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

  updateProfile(profileData) {
    return this.request('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
  },

  getProfile() {
    return this.request('/auth/me');
  },

  // Subjects Endpoints
  getSubjects(search = '') {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.request(`/subjects${query}`);
  },

  getSubject(id) {
    return this.request(`/subjects/${id}`);
  },

  createSubject(subjectData) {
    return this.request('/subjects', {
      method: 'POST',
      body: JSON.stringify(subjectData)
    });
  },

  updateSubject(id, subjectData) {
    return this.request(`/subjects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(subjectData)
    });
  },

  deleteSubject(id) {
    return this.request(`/subjects/${id}`, {
      method: 'DELETE'
    });
  },

  // Tasks Endpoints
  getTasks(params = {}) {
    const query = new URLSearchParams();
    if (params.subject_id) query.append('subject_id', params.subject_id);
    if (params.status) query.append('status', params.status);
    if (params.search) query.append('search', params.search);
    const queryString = query.toString() ? `?${query.toString()}` : '';
    return this.request(`/academic_tasks${queryString}`);
  },

  getTask(id) {
    return this.request(`/academic_tasks/${id}`);
  },

  createTask(taskData) {
    return this.request('/academic_tasks', {
      method: 'POST',
      body: JSON.stringify(taskData)
    });
  },

  updateTask(id, taskData) {
    return this.request(`/academic_tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(taskData)
    });
  },

  addStudyTime(taskId, minutes, newStatus = null) {
    return this.request(`/academic_tasks/${taskId}/study-time`, {
      method: 'POST',
      body: JSON.stringify({
        additional_minutes: minutes,
        new_status: newStatus
      })
    });
  },

  deleteTask(id) {
    return this.request(`/academic_tasks/${id}`, {
      method: 'DELETE'
    });
  },

  // Analytics Endpoints
  getProgressAnalytics() {
    return this.request('/analytics/progress');
  },

  getTimeDistribution() {
    return this.request('/analytics/time-spent');
  },

  // AI Insights
  getAIInsights() {
    return this.request('/ai/insights');
  },

  // Reports
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

  // Global Search
  search(query, status = null) {
    const params = new URLSearchParams({ q: query });
    if (status) params.append('status', status);
    return this.request(`/search?${params.toString()}`);
  }
};
