// ==========================================================================
// Authentication & Student Profile Management Module for EduTrack AI
// Manages User Session, Avatar Upload, Academic Info & Profile Editing
// ==========================================================================

const Auth = {
  currentAvatarData: null,

  init() {
    this.bindEvents();
    this.checkAuth();
  },

  checkAuth() {
    const token = API.getToken();
    const user = API.getCurrentUser();
    
    const authOverlay = document.getElementById('auth-modal-overlay');
    const mainApp = document.getElementById('main-app-container');
    const userNameDisplay = document.getElementById('user-name-display');
    const userCourseDisplay = document.getElementById('user-course-display');
    const avatarImg = document.getElementById('user-avatar-image');
    const avatarInitials = document.getElementById('user-avatar-initials');

    if (token && user) {
      if (authOverlay) authOverlay.classList.add('hidden');
      if (mainApp) mainApp.classList.remove('hidden');
      if (userNameDisplay) userNameDisplay.textContent = user.name;
      
      const academicInfo = [user.course, user.college_year].filter(Boolean).join(' • ') || (user.email || 'Estudante');
      if (userCourseDisplay) userCourseDisplay.textContent = academicInfo;
      
      // Atualizar Avatar (Foto ou Iniciais)
      if (user.avatar_url && avatarImg) {
        avatarImg.src = user.avatar_url;
        avatarImg.classList.remove('hidden');
        if (avatarInitials) avatarInitials.classList.add('hidden');
      } else {
        if (avatarImg) avatarImg.classList.add('hidden');
        if (avatarInitials) {
          avatarInitials.classList.remove('hidden');
          const initials = user.name
            .split(' ')
            .filter(n => n.length > 0)
            .slice(0, 2)
            .map(n => n[0].toUpperCase())
            .join('');
          avatarInitials.textContent = initials || 'AL';
        }
      }
    } else {
      if (authOverlay) authOverlay.classList.remove('hidden');
      if (mainApp) mainApp.classList.add('hidden');
    }
  },

  bindEvents() {
    // Alternância entre abas de Login e Cadastro
    const tabLoginBtn = document.getElementById('tab-login-btn');
    const tabRegisterBtn = document.getElementById('tab-register-btn');
    const formLogin = document.getElementById('form-login');
    const formRegister = document.getElementById('form-register');

    if (tabLoginBtn && tabRegisterBtn) {
      tabLoginBtn.addEventListener('click', () => {
        tabLoginBtn.classList.add('border-blue-600', 'text-blue-600', 'dark:text-blue-400');
        tabLoginBtn.classList.remove('border-transparent', 'text-slate-500');
        tabRegisterBtn.classList.remove('border-blue-600', 'text-blue-600', 'dark:text-blue-400');
        tabRegisterBtn.classList.add('border-transparent', 'text-slate-500');
        formLogin.classList.remove('hidden');
        formRegister.classList.add('hidden');
      });

      tabRegisterBtn.addEventListener('click', () => {
        tabRegisterBtn.classList.add('border-blue-600', 'text-blue-600', 'dark:text-blue-400');
        tabRegisterBtn.classList.remove('border-transparent', 'text-slate-500');
        tabLoginBtn.classList.remove('border-blue-600', 'text-blue-600', 'dark:text-blue-400');
        tabLoginBtn.classList.add('border-transparent', 'text-slate-500');
        formRegister.classList.remove('hidden');
        formLogin.classList.add('hidden');
      });
    }

    // Submit de Login
    if (formLogin) {
      formLogin.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        const errorEl = document.getElementById('auth-error-msg');

        try {
          errorEl.classList.add('hidden');
          const data = await API.login(email, password);
          API.setToken(data.access_token);
          API.setCurrentUser(data.user);
          this.checkAuth();
          Toast.show(`Bem-vindo, ${data.user.name}!`, 'success');
          if (data.xano_sync && data.xano_sync.status === 'failed') {
            Toast.show(`Aviso: sincronização com o Xano falhou: ${data.xano_sync.detail}`, 'error');
          }
          window.dispatchEvent(new CustomEvent('auth-success'));
        } catch (err) {
          errorEl.textContent = err.message;
          errorEl.classList.remove('hidden');
        }
      });
    }

    // Submit de Registro
    if (formRegister) {
      formRegister.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('register-name').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const errorEl = document.getElementById('auth-error-msg');

        try {
          errorEl.classList.add('hidden');
          const data = await API.register(name, email, password);
          API.setToken(data.access_token);
          API.setCurrentUser(data.user);
          this.checkAuth();
          const sync = data.xano_sync || {};
          if (sync.status === 'synced') {
            Toast.show(`Conta criada e sincronizada com o Xano! Bem-vindo, ${data.user.name}!`, 'success');
          } else {
            Toast.show(`Conta criada, mas NÃO foi sincronizada com o Xano: ${sync.detail || 'sem detalhe'}`, 'error');
          }
          window.dispatchEvent(new CustomEvent('auth-success'));
        } catch (err) {
          errorEl.textContent = err.message;
          errorEl.classList.remove('hidden');
        }
      });
    }

    // Botão de preenchimento da Conta Demo
    const demoBtn = document.getElementById('btn-fill-demo');
    if (demoBtn) {
      demoBtn.addEventListener('click', () => {
        const emailInput = document.getElementById('login-email');
        const passInput = document.getElementById('login-password');
        if (emailInput && passInput) {
          emailInput.value = 'aluno@edutrack.edu.br';
          passInput.value = 'senha123';
          if (tabLoginBtn) tabLoginBtn.click();
          Toast.show('Credenciais demo preenchidas! Clique em "Acessar Meu Painel".', 'info');
        }
      });
    }

    // Botão de Logout
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        API.clearAuth();
        this.checkAuth();
        Toast.show('Você saiu da sua conta.', 'info');
      });
    }

    // Recuperação de senha: (1) pede o link por e-mail; (2) abre o link e define a nova senha.
    const forgotBtn = document.getElementById('btn-forgot-password');
    const forgotModal = document.getElementById('forgot-password-modal');
    const closeForgotModalBtn = document.getElementById('btn-close-forgot-modal');
    const formForgotRequest = document.getElementById('form-forgot-request');
    const formResetPassword = document.getElementById('form-reset-password');
    const resetEmailInput = document.getElementById('reset-email');
    const resetPasswordInput = document.getElementById('reset-new-password');
    const forgotErrorEl = document.getElementById('forgot-modal-error');
    const forgotSuccessEl = document.getElementById('forgot-modal-success');
    const forgotTitleEl = document.getElementById('forgot-modal-title');

    const showForgotStep = (step) => {
      forgotErrorEl.classList.add('hidden');
      forgotSuccessEl.classList.add('hidden');
      formForgotRequest.classList.toggle('hidden', step !== 'request');
      formResetPassword.classList.toggle('hidden', step !== 'reset');
      forgotTitleEl.textContent = step === 'reset' ? 'Criar Nova Senha' : 'Recuperar Senha';
      forgotModal.classList.remove('hidden');
    };

    if (forgotBtn && forgotModal) {
      forgotBtn.addEventListener('click', () => {
        const loginEmail = document.getElementById('login-email')?.value || '';
        if (loginEmail) resetEmailInput.value = loginEmail;
        showForgotStep('request');
      });
    }

    if (closeForgotModalBtn && forgotModal) {
      closeForgotModalBtn.addEventListener('click', () => forgotModal.classList.add('hidden'));
    }

    if (formForgotRequest) {
      formForgotRequest.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById('btn-submit-forgot');
        try {
          forgotErrorEl.classList.add('hidden');
          forgotSuccessEl.classList.add('hidden');
          submitBtn.disabled = true;
          submitBtn.textContent = 'Enviando...';
          const res = await API.forgotPassword(resetEmailInput.value.trim());
          let msg = res.message;
          if (res.email_backend === 'console') {
            msg += ' (Modo desenvolvimento: o e-mail não é entregue; o link foi gravado na pasta outbox/ e no log do servidor.)';
          }
          forgotSuccessEl.textContent = msg;
          forgotSuccessEl.classList.remove('hidden');
        } catch (err) {
          forgotErrorEl.textContent = err.message;
          forgotErrorEl.classList.remove('hidden');
        } finally {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Enviar link de recuperação';
        }
      });
    }

    if (formResetPassword) {
      formResetPassword.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById('btn-submit-reset');
        const token = new URLSearchParams(window.location.search).get('reset_token');
        try {
          forgotErrorEl.classList.add('hidden');
          forgotSuccessEl.classList.add('hidden');
          submitBtn.disabled = true;
          submitBtn.textContent = 'Atualizando...';
          const res = await API.resetPassword(token || '', resetPasswordInput.value);
          forgotSuccessEl.textContent = res.message || 'Senha atualizada com sucesso!';
          forgotSuccessEl.classList.remove('hidden');
          Toast.show('Senha atualizada! Entre com a nova senha.', 'success');
          resetPasswordInput.value = '';
          window.history.replaceState({}, document.title, window.location.pathname);
          setTimeout(() => forgotModal.classList.add('hidden'), 2000);
        } catch (err) {
          forgotErrorEl.textContent = err.message;
          forgotErrorEl.classList.remove('hidden');
        } finally {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Atualizar Minha Senha';
        }
      });
    }

    // Link recebido por e-mail (/?reset_token=...): abre direto a tela de nova senha
    if (forgotModal && new URLSearchParams(window.location.search).get('reset_token')) {
      API.clearAuth();
      showForgotStep('reset');
    }

    // Botão de fechar modal de perfil
    const closeBtn = document.getElementById('btn-close-profile-modal');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.closeProfileModal());
    }

    // Upload de Arquivo de Foto de Perfil
    const avatarFileInput = document.getElementById('profile-avatar-file');
    if (avatarFileInput) {
      avatarFileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
          if (file.size > 2 * 1024 * 1024) {
            Toast.show('A imagem deve ter no máximo 2MB.', 'warning');
            return;
          }
          const reader = new FileReader();
          reader.onload = (event) => {
            this.currentAvatarData = event.target.result;
            const previewImg = document.getElementById('profile-modal-avatar-preview');
            if (previewImg) {
              previewImg.src = this.currentAvatarData;
              previewImg.classList.remove('hidden');
            }
            Toast.show('Foto selecionada! Salve o perfil para confirmar.', 'info');
          };
          reader.readAsDataURL(file);
        }
      });
    }

    // Remover Foto de Perfil
    const removeAvatarBtn = document.getElementById('btn-remove-avatar');
    if (removeAvatarBtn) {
      removeAvatarBtn.addEventListener('click', () => {
        this.currentAvatarData = "";
        const previewImg = document.getElementById('profile-modal-avatar-preview');
        if (previewImg) {
          previewImg.src = "";
          previewImg.classList.add('hidden');
        }
        Toast.show('Foto removida. Salve para aplicar.', 'info');
      });
    }

    // Presets de Avatares Rápidos
    document.querySelectorAll('.avatar-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const url = btn.dataset.avatarUrl;
        if (url) {
          this.currentAvatarData = url;
          const previewImg = document.getElementById('profile-modal-avatar-preview');
          if (previewImg) {
            previewImg.src = url;
            previewImg.classList.remove('hidden');
          }
          Toast.show('Avatar selecionado!', 'info');
        }
      });
    });

    // Submissão do Formulário de Perfil
    const formProfile = document.getElementById('form-profile-modal');
    if (formProfile) {
      formProfile.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
          name: document.getElementById('profile-modal-name').value.trim(),
          course: document.getElementById('profile-modal-course').value.trim() || null,
          college_year: document.getElementById('profile-modal-year').value.trim() || null,
          institution: document.getElementById('profile-modal-institution').value.trim() || null,
          bio: document.getElementById('profile-modal-bio').value.trim() || null
        };

        if (this.currentAvatarData !== null) {
          payload.avatar_url = this.currentAvatarData || null;
        }

        try {
          const updatedUser = await API.updateProfile(payload);
          API.setCurrentUser(updatedUser);
          this.checkAuth();
          this.closeProfileModal();
          Toast.show('Perfil acadêmico atualizado com sucesso!', 'success');
        } catch (err) {
          Toast.show('Erro ao atualizar perfil: ' + err.message, 'error');
        }
      });
    }
  },

  async openProfileModal() {
    let user = API.getCurrentUser();
    if (!user) return;

    this.currentAvatarData = user.avatar_url || null;

    document.getElementById('profile-modal-name').value = user.name || '';
    document.getElementById('profile-modal-course').value = user.course || '';
    document.getElementById('profile-modal-year').value = user.college_year || '';
    document.getElementById('profile-modal-institution').value = user.institution || '';
    document.getElementById('profile-modal-bio').value = user.bio || '';

    const previewImg = document.getElementById('profile-modal-avatar-preview');
    if (previewImg) {
      if (user.avatar_url) {
        previewImg.src = user.avatar_url;
        previewImg.classList.remove('hidden');
      } else {
        previewImg.src = '';
        previewImg.classList.add('hidden');
      }
    }

    const overlay = document.getElementById('modal-profile-overlay');
    if (overlay) {
      overlay.classList.remove('hidden');
      if (typeof AppAnimations !== 'undefined') {
        AppAnimations.animateModalOpen(overlay.querySelector('.pro-card'));
      }
    }

    // Atualiza com dados acadêmicos recentes do Xano (/alunos)
    try {
      const fresh = await API.getProfile();
      if (fresh) {
        if (fresh.name) document.getElementById('profile-modal-name').value = fresh.name;
        if (fresh.course) document.getElementById('profile-modal-course').value = fresh.course;
        if (fresh.college_year) document.getElementById('profile-modal-year').value = fresh.college_year;
      }
    } catch (err) {
      console.warn('Erro ao carregar dados acadêmicos do Xano:', err);
    }
  },

  closeProfileModal() {
    const overlay = document.getElementById('modal-profile-overlay');
    if (overlay) overlay.classList.add('hidden');
    this.currentAvatarData = null;
  }
};
