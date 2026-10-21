// ==========================================================================
// Google Classroom (via FastAPI -> Xano). O frontend NUNCA fala com o Xano nem com o Google
// diretamente (exceto o redirecionamento do navegador para a tela de consentimento).
// ==========================================================================

const Classroom = {
  bound: false,
  busy: false,

  // ---------- funções puras (testáveis sem DOM) ----------

  // Converte o status da API em o que mostrar. Texto sempre estático/sem HTML.
  statusView(s) {
    const v = { text: '', showConnect: false, connectLabel: 'Conectar Google Classroom', showSync: false, showDisconnect: false };
    if (!s) { v.text = 'Não foi possível verificar a conexão.'; return v; }
    if (!s.configured) { v.text = 'Integração com o Google Classroom ainda não configurada neste servidor.'; return v; }
    if (!s.reachable) { v.text = 'Serviço de integração indisponível no momento. Tente novamente em instantes.'; return v; }
    if (s.connected && s.status === 'active') {
      v.text = s.google_email ? `Conectado como ${s.google_email}.` : 'Conectado ao Google Classroom.';
      v.showSync = true; v.showDisconnect = true; return v;
    }
    if (s.status === 'needs_reauth' || s.status === 'revoked' || s.status === 'error') {
      v.text = 'A autorização do Google expirou ou foi revogada. Reconecte para continuar sincronizando.';
      v.showConnect = true; v.connectLabel = 'Reconectar Google Classroom'; v.showDisconnect = true; return v;
    }
    v.text = 'Conecte sua conta Google para importar cursos e atividades do Classroom.';
    v.showConnect = true; return v;
  },

  // Só aceita links https; qualquer outra coisa (javascript:, data:, relativo) vira null.
  safeLink(url) {
    if (typeof url !== 'string') return null;
    try {
      const u = new URL(url);
      return u.protocol === 'https:' ? u.href : null;
    } catch { return null; }
  },

  // A URL de consentimento deve ser do Google, em https.
  isGoogleAuthUrl(url) {
    try {
      const u = new URL(url);
      return u.protocol === 'https:' && u.hostname === 'accounts.google.com';
    } catch { return false; }
  },

  formatDue(iso) {
    if (!iso) return 'Sem prazo';
    // A API devolve UTC sem fuso; marca como UTC para o navegador converter para o horário local.
    const d = new Date(/[zZ]|[+-]\d\d:\d\d$/.test(iso) ? iso : iso + 'Z');
    if (isNaN(d.getTime())) return 'Sem prazo';
    return d.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  },

  formatPoints(p) {
    return (typeof p === 'number' && isFinite(p)) ? `${Number.isInteger(p) ? p : p.toFixed(2)} pts` : 'Sem pontuação';
  },

  summarize(response) {
    const r = (response && response.result) || {};
    const novas = r.tasks_created || 0, atual = r.tasks_updated || 0, cursos = (r.courses_created || 0) + (r.courses_updated || 0);
    const avisos = (r.errors || []).length;
    let msg = `Sincronizado: ${cursos} curso(s) novo(s)/atualizado(s), ${novas} atividade(s) nova(s), ${atual} atualizada(s).`;
    if (avisos) msg += ` ${avisos} item(ns) ignorado(s) por dados inválidos.`;
    return { message: msg, type: avisos ? 'warning' : 'success' };
  },

  // Mensagem segura para o Toast (que usa innerHTML): escapa HTML.
  esc(text) {
    return String(text == null ? '' : text).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  },

  // ---------- UI ----------

  bindEvents() {
    if (this.bound) return;
    const byId = id => document.getElementById(id);
    const connect = byId('btn-classroom-connect'), sync = byId('btn-classroom-sync'), disc = byId('btn-classroom-disconnect');
    if (!connect || !sync || !disc) return;
    this.bound = true;
    connect.addEventListener('click', () => this.connect());
    sync.addEventListener('click', () => this.sync());
    disc.addEventListener('click', () => this.disconnect());
  },

  // Trata o retorno do OAuth (?classroom=connected|error) e limpa a URL.
  handleReturn() {
    const params = new URLSearchParams(window.location.search);
    const result = params.get('classroom');
    if (!result) return;
    params.delete('classroom'); params.delete('reason');
    const qs = params.toString();
    window.history.replaceState({}, '', window.location.pathname + (qs ? `?${qs}` : '') + window.location.hash);
    setTimeout(() => {
      if (result === 'connected') Toast.show('Google Classroom conectado! Clique em "Sincronizar agora".', 'success');
      else Toast.show('Não foi possível conectar o Google Classroom. Tente novamente.', 'error');
      if (typeof App !== 'undefined' && App.switchTab) App.switchTab('subjects');
    }, 400);
  },

  async load() {
    if (!API.getToken() || !document.getElementById('classroom-card')) return;
    this.bindEvents();
    let status = null;
    try { status = await API.classroomStatus(); } catch (err) { console.error('Classroom status:', err); }
    this.renderStatus(status);
    if (status && status.local && (status.local.courses > 0 || status.local.tasks > 0)) await this.loadImported();
    else this.renderImported([], []);
  },

  renderStatus(status) {
    const v = this.statusView(status);
    const set = (id, fn) => { const el = document.getElementById(id); if (el) fn(el); };
    set('classroom-status-text', el => { el.textContent = v.text; });
    set('btn-classroom-connect', el => { el.classList.toggle('hidden', !v.showConnect); el.textContent = v.connectLabel; });
    set('btn-classroom-sync', el => el.classList.toggle('hidden', !v.showSync));
    set('btn-classroom-disconnect', el => el.classList.toggle('hidden', !v.showDisconnect));
    set('classroom-last-sync', el => {
      const last = status && status.local && status.local.last_synced_at;
      el.textContent = last ? `Última sincronização: ${this.formatDue(last)} · ${status.local.courses} curso(s), ${status.local.tasks} atividade(s) importada(s).` : '';
    });
  },

  async loadImported() {
    try {
      const [courses, tasks] = await Promise.all([API.classroomCourses(), API.classroomTasks({ limit: 50 })]);
      this.renderImported(courses, tasks);
    } catch (err) { console.error('Classroom importados:', err); }
  },

  renderImported(courses, tasks) {
    const wrap = document.getElementById('classroom-imported');
    const cl = document.getElementById('classroom-courses-list'), tl = document.getElementById('classroom-tasks-list');
    if (!wrap || !cl || !tl) return;
    wrap.classList.toggle('hidden', !courses.length && !tasks.length);
    cl.replaceChildren(...courses.map(c => this.row(c.name, `${c.tasks_pending} pendente(s) de ${c.tasks_total}`, c.link)));
    tl.replaceChildren(...tasks.map(t => this.row(
      t.title,
      `${t.course_name || ''} · ${this.formatDue(t.due_date)} · ${this.formatPoints(t.max_points)}${t.status === 'completed' ? ' · ✔ entregue' : ''}`,
      t.link)));
  },

  row(title, subtitle, link) {
    const li = document.createElement('li');
    li.className = 'text-xs text-slate-700 dark:text-slate-300 py-1.5 border-b border-slate-100 dark:border-slate-800';
    const safe = this.safeLink(link);
    const head = document.createElement(safe ? 'a' : 'span');
    head.className = 'font-bold block ' + (safe ? 'text-blue-600 dark:text-blue-400 hover:underline' : '');
    head.textContent = title;
    if (safe) { head.href = safe; head.target = '_blank'; head.rel = 'noopener noreferrer'; }
    const sub = document.createElement('span');
    sub.className = 'text-[11px] text-slate-500 dark:text-slate-400';
    sub.textContent = subtitle;
    li.append(head, sub);
    return li;
  },

  setBusy(on, label) {
    this.busy = on;
    ['btn-classroom-connect', 'btn-classroom-sync', 'btn-classroom-disconnect'].forEach(id => {
      const el = document.getElementById(id); if (el) el.disabled = on;
    });
    const sync = document.getElementById('btn-classroom-sync');
    if (sync && label) sync.textContent = label;
  },

  async connect() {
    if (this.busy) return;
    this.setBusy(true);
    try {
      const { authorization_url } = await API.classroomConnect();
      if (!this.isGoogleAuthUrl(authorization_url)) throw new Error('URL de autorização inválida.');
      window.location.href = authorization_url;
    } catch (err) {
      Toast.show(this.esc(err.message || 'Falha ao iniciar a conexão.'), 'error');
      this.setBusy(false);
    }
  },

  async sync() {
    if (this.busy) return;
    this.setBusy(true, 'Sincronizando...');
    try {
      const response = await API.classroomSync(true);
      const s = this.summarize(response);
      Toast.show(this.esc(s.message), s.type);
      if (typeof Subjects !== 'undefined') await Subjects.loadSubjects();
      if (typeof Tasks !== 'undefined') await Tasks.loadTasks();
    } catch (err) {
      Toast.show(this.esc(err.message || 'Falha na sincronização.'), 'error');
    } finally {
      this.setBusy(false, 'Sincronizar agora');
      await this.load();
    }
  },

  async disconnect() {
    if (this.busy) return;
    if (!window.confirm('Desconectar o Google Classroom? Os cursos e atividades já importados serão mantidos.')) return;
    this.setBusy(true);
    try {
      await API.classroomDisconnect();
      Toast.show('Google Classroom desconectado.', 'success');
    } catch (err) {
      Toast.show(this.esc(err.message || 'Falha ao desconectar.'), 'error');
    } finally {
      this.setBusy(false);
      await this.load();
    }
  }
};

if (typeof module !== 'undefined') module.exports = Classroom;  // permite testar as funções puras no Node
