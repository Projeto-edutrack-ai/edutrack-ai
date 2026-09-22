// ==========================================================================
// AI Insights & Weekly Report Module for EduTrack AI
// Enhanced with GSAP reveals, Toasts & PDF Export Pipeline
// ==========================================================================

const Insights = {
  async init() {
    this.bindEvents();
    await this.loadInsights();
  },

  async loadInsights() {
    if (!API.getToken()) return;

    try {
      const insights = await API.getAIInsights();
      this.renderInsights(insights);
    } catch (err) {
      console.error('Erro ao carregar insights de IA:', err);
    }
  },

  renderInsights(insights) {
    const summaryEl = document.getElementById('ai-summary-text');
    const badgeEl = document.getElementById('ai-engine-badge');
    const alertsContainer = document.getElementById('ai-critical-alerts-container');
    const recsContainer = document.getElementById('ai-recommendations-list');
    const focusContainer = document.getElementById('ai-weekly-focus-list');

    if (summaryEl) summaryEl.textContent = insights.summary;
    if (badgeEl) badgeEl.textContent = `✨ ${insights.generated_by}`;

    // Alertas Críticos
    if (alertsContainer) {
      if (insights.critical_alerts && insights.critical_alerts.length > 0) {
        alertsContainer.classList.remove('hidden');
        alertsContainer.innerHTML = insights.critical_alerts.map(a => `
          <div class="p-3.5 bg-rose-500/10 dark:bg-rose-950/30 border-l-4 border-rose-500 rounded-r-xl text-xs font-bold text-rose-800 dark:text-rose-300 flex items-center gap-2 shadow-sm">
            <span>⚠️</span> <span>${a}</span>
          </div>
        `).join('');
      } else {
        alertsContainer.classList.add('hidden');
      }
    }

    // Recomendações
    if (recsContainer) {
      if (insights.recommendations && insights.recommendations.length > 0) {
        recsContainer.innerHTML = insights.recommendations.map(r => {
          let typeClass = 'border-blue-500 bg-blue-50/40 dark:bg-blue-900/10 text-blue-900 dark:text-blue-200';
          let icon = '💡';
          if (r.type === 'warning') {
            typeClass = 'border-amber-500 bg-amber-50/40 dark:bg-amber-900/10 text-amber-900 dark:text-amber-200';
            icon = '⏱️';
          } else if (r.type === 'success') {
            typeClass = 'border-emerald-500 bg-emerald-50/40 dark:bg-emerald-900/10 text-emerald-900 dark:text-emerald-200';
            icon = '🚀';
          } else if (r.type === 'alert') {
            typeClass = 'border-rose-500 bg-rose-50/40 dark:bg-rose-900/10 text-rose-900 dark:text-rose-200';
            icon = '🚨';
          }

          return `
            <div class="pro-card p-4.5 rounded-xl border-l-4 ${typeClass} shadow-sm group hover:shadow-md transition-all">
              <div class="flex items-center gap-2 mb-1.5">
                <span class="text-base">${icon}</span>
                <h4 class="text-xs md:text-sm font-bold tracking-tight">${r.title}</h4>
              </div>
              <p class="text-xs text-slate-700 dark:text-slate-300 mb-2.5 leading-relaxed">${r.message}</p>
              ${r.action_suggested ? `
                <div class="text-xs bg-white/80 dark:bg-slate-800/90 p-2.5 rounded-xl font-semibold text-slate-800 dark:text-slate-200 border border-slate-200/60 dark:border-slate-700/60 shadow-xs flex items-center gap-2">
                  <span>👉</span> <span><b>Sugestão de Ação:</b> ${r.action_suggested}</span>
                </div>
              ` : ''}
            </div>
          `;
        }).join('');

        if (typeof AppAnimations !== 'undefined') {
          AppAnimations.animateCardsStagger('#ai-recommendations-list', '.pro-card');
        }
      } else {
        recsContainer.innerHTML = '<p class="text-xs text-slate-400 font-medium">Nenhuma recomendação adicional no momento.</p>';
      }
    }

    // Foco Semanal
    if (focusContainer) {
      if (insights.weekly_focus && insights.weekly_focus.length > 0) {
        focusContainer.innerHTML = insights.weekly_focus.map(f => `
          <li class="flex items-start gap-2.5 text-xs font-semibold text-slate-700 dark:text-slate-300 p-2 rounded-lg hover:bg-slate-100/50 dark:hover:bg-slate-800/40 transition-colors">
            <span class="text-blue-500 font-black mt-0.5">✓</span>
            <span class="leading-relaxed">${f}</span>
          </li>
        `).join('');
      }
    }

    // Update sidebar badge count
    const badgeCount = document.getElementById('sidebar-insights-count');
    if (badgeCount) {
      const totalRecs = (insights.recommendations || []).length + (insights.critical_alerts || []).length;
      if (totalRecs > 0) {
        badgeCount.textContent = totalRecs;
        badgeCount.classList.remove('hidden');
        badgeCount.classList.add('flex');
      } else {
        badgeCount.classList.add('hidden');
        badgeCount.classList.remove('flex');
      }
    }
  },

  bindEvents() {
    const downloadBtn = document.getElementById('btn-download-weekly-pdf');
    if (downloadBtn) {
      downloadBtn.addEventListener('click', async () => {
        try {
          downloadBtn.disabled = true;
          downloadBtn.innerHTML = '<span>⏳</span> <span>Gerando PDF Inteligente...</span>';
          await API.downloadWeeklyReport();
          Toast.show('Relatório Semanal baixado com sucesso!', 'success');
        } catch (err) {
          Toast.show('Erro ao gerar PDF: ' + err.message, 'error');
        } finally {
          downloadBtn.disabled = false;
          downloadBtn.innerHTML = '<span>📄</span> <span>Baixar Relatório Semanal (PDF)</span>';
        }
      });
    }

    const refreshBtn = document.getElementById('btn-refresh-insights');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', async () => {
        refreshBtn.innerHTML = '<span>🔄</span> <span>Recalculando...</span>';
        await this.loadInsights();
        refreshBtn.innerHTML = '<span>✨</span> <span>Recalcular Insights</span>';
        Toast.show('Diagnóstico de IA recalculado com sucesso!', 'success');
      });
    }
  }
};
