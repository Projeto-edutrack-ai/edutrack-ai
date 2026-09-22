// ==========================================================================
// GSAP, ScrollTrigger & Micro-Animations Engine
// Comprehensive animation pipeline across all sections
// ==========================================================================

const Toast = {
  show(message, type = 'success', duration = 3500) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-message';

    let icon = '✨';
    let borderColor = 'rgba(59, 130, 246, 0.4)';
    if (type === 'success') {
      icon = '✅';
      borderColor = 'rgba(16, 185, 129, 0.5)';
    } else if (type === 'error') {
      icon = '❌';
      borderColor = 'rgba(239, 68, 68, 0.5)';
    } else if (type === 'warning') {
      icon = '⚠️';
      borderColor = 'rgba(245, 158, 11, 0.5)';
    }

    toast.style.borderColor = borderColor;
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      if (typeof gsap !== 'undefined') {
        gsap.to(toast, {
          opacity: 0,
          y: -15,
          duration: 0.3,
          ease: 'power2.in',
          onComplete: () => toast.remove()
        });
      } else {
        toast.remove();
      }
    }, duration);
  }
};

const AppAnimations = {
  init() {
    if (typeof gsap === 'undefined') return;

    if (typeof ScrollTrigger !== 'undefined') {
      gsap.registerPlugin(ScrollTrigger);
    }

    this.initHeroEntrance();
    this.initParallaxLayers();
    this.initScrollReveals();
  },

  initHeroEntrance() {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    tl.from('#hero-title', {
      y: 24,
      opacity: 0,
      duration: 0.7,
      delay: 0.1
    })
    .from('#hero-subtitle', {
      y: 16,
      opacity: 0,
      duration: 0.5
    }, '-=0.4')
    .from('.kpi-card-animate', {
      scale: 0.94,
      y: 20,
      opacity: 0,
      stagger: 0.08,
      duration: 0.6
    }, '-=0.3')
    .from('#study-timer-widget', {
      y: 20,
      opacity: 0,
      duration: 0.6
    }, '-=0.2');
  },

  animateSectionChange(sectionElement) {
    if (!sectionElement || typeof gsap === 'undefined') return;
    
    gsap.fromTo(sectionElement,
      { opacity: 0, y: 18 },
      { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }
    );

    // Animar cards internos da seção em cascata
    const cards = sectionElement.querySelectorAll('.pro-card, .subject-card, .task-row-card');
    if (cards.length > 0) {
      gsap.fromTo(cards,
        { opacity: 0, y: 15 },
        { opacity: 1, y: 0, stagger: 0.05, duration: 0.35, ease: 'power2.out', delay: 0.05 }
      );
    }
  },

  animateCardsStagger(containerSelector, itemSelector = '.pro-card') {
    const container = document.querySelector(containerSelector);
    if (!container || typeof gsap === 'undefined') return;

    const items = container.querySelectorAll(itemSelector);
    if (items.length === 0) return;

    gsap.fromTo(items,
      { opacity: 0, y: 20, scale: 0.97 },
      { opacity: 1, y: 0, scale: 1, stagger: 0.06, duration: 0.4, ease: 'back.out(1.2)' }
    );
  },

  animateModalOpen(modalBoxElement) {
    if (!modalBoxElement || typeof gsap === 'undefined') return;
    gsap.fromTo(modalBoxElement,
      { opacity: 0, scale: 0.9, y: 25 },
      { opacity: 1, scale: 1, y: 0, duration: 0.35, ease: 'back.out(1.6)' }
    );
  },

  animateNumber(element, targetValue, suffix = '', duration = 1.0) {
    if (!element) return;
    const num = parseFloat(targetValue) || 0;
    const obj = { val: 0 };

    gsap.to(obj, {
      val: num,
      duration: duration,
      ease: 'power2.out',
      onUpdate: () => {
        const isFloat = num % 1 !== 0;
        element.textContent = `${isFloat ? obj.val.toFixed(1) : Math.round(obj.val)}${suffix}`;
      }
    });
  },

  initParallaxLayers() {
    // Parallax suave com o movimento do mouse
    const orbs = document.querySelectorAll('.ambient-orb');
    if (orbs.length > 0) {
      window.addEventListener('mousemove', (e) => {
        const x = (e.clientX / window.innerWidth - 0.5) * 2;
        const y = (e.clientY / window.innerHeight - 0.5) * 2;

        orbs.forEach((orb, i) => {
          const factor = (i + 1) * 15;
          gsap.to(orb, {
            x: x * factor,
            y: y * factor,
            duration: 0.8,
            ease: 'power1.out'
          });
        });
      });
    }
  },

  initScrollReveals() {
    if (typeof ScrollTrigger === 'undefined') return;

    gsap.utils.toArray('[data-animate="fade-up"]').forEach(elem => {
      gsap.fromTo(elem,
        { y: 30, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.7,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: elem,
            start: 'top 88%',
            toggleActions: 'play none none none'
          }
        }
      );
    });
  }
};
