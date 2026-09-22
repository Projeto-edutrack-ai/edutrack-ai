// ==========================================================================
// Authentication & Student Profile Management Module for EduTrack AI
// Manages User Session, Avatar Upload, Academic Info & Profile Editing
// ==========================================================================

const Auth = {
  currentAvatarData: null,

  init() {
    this.bindEvents();
    this.bindProfileEvents();
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
          Toast.show(`Conta criada com sucesso! Bem-vindo, ${data.user.name}!`, 'success');
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

    // Recuperação de senha via Modal Interativo
    const forgotBtn = document.getElementById('btn-forgot-password');
    const forgotModal = document.getElementById('modal-forgot-password-overlay');
    const closeForgotBtn = document.getElementById('btn-close-forgot-modal');
    const cancelForgotBtn = document.getElementById('btn-cancel-forgot-modal');
    const formForgot = document.getElementById('form-forgot-password');
    const forgotAlert = document.getElementById('forgot-password-alert');
    const forgotAlertText = document.getElementById('forgot-password-alert-text');
    const forgotEmailInput = document.getElementById('forgot-email-input');

    const openForgotModal = () => {
      if (forgotAlert) forgotAlert.classList.add('hidden');
      const currentLoginEmail = document.getElementById('login-email')?.value;
      if (forgotEmailInput && currentLoginEmail) {
        forgotEmailInput.value = currentLoginEmail;
      }
      if (forgotModal) forgotModal.classList.remove('hidden');
    };

    const closeForgotModal = () => {
      if (forgotModal) forgotModal.classList.add('hidden');
    };

    if (forgotBtn) forgotBtn.addEventListener('click', openForgotModal);
    if (closeForgotBtn) closeForgotBtn.addEventListener('click', closeForgotModal);
    if (cancelForgotBtn) cancelForgotBtn.addEventListener('click', closeForgotModal);

    if (forgotModal) {
      forgotModal.addEventListener('click', (e) => {
        if (e.target === forgotModal) closeForgotModal();
      });
    }

    if (formForgot) {
      formForgot.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = forgotEmailInput?.value?.trim();
        const submitBtn = document.getElementById('btn-submit-forgot');
        if (!email) return;

        try {
          if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>⏳</span> <span>Enviando...</span>';
          }
          const resp = await API.forgotPassword(email);
          if (forgotAlert && forgotAlertText) {
            forgotAlertText.textContent = resp.message || 'Instruções enviadas com sucesso para seu email!';
            forgotAlert.classList.remove('hidden');
          }
          Toast.show(resp.message || 'Instruções enviadas com sucesso!', 'success');
          setTimeout(() => {
            closeForgotModal();
          }, 2500);
        } catch (err) {
          Toast.show('Erro: ' + err.message, 'error');
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 2 11 13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              <span>Enviar Instruções</span>
            `;
          }
        }
      });
    }

    window.addEventListener('auth-changed', () => this.checkAuth());
  },

  bindProfileEvents() {
    // Clique no Card do Aluno para abrir edição de perfil
    const userCard = document.getElementById('sidebar-user-card');
    if (userCard) {
      userCard.addEventListener('click', () => this.openProfileModal());
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

  openProfileModal() {
    const user = API.getCurrentUser();
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
  },

  closeProfileModal() {
    const overlay = document.getElementById('modal-profile-overlay');
    if (overlay) overlay.classList.add('hidden');
    this.currentAvatarData = null;
  }
};
