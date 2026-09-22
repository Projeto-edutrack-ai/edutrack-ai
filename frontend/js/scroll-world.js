// ==========================================================================
// Three.js Orbit & Planetary System Engine for EduTrack AI
// Sistema Planetário Acadêmico 3D:
// - Rotação livre 360° em qualquer direção (Mouse Drag / Touch com OrbitControls)
// - 1 Disciplina Cadastrada = Exatamente 1 Planeta Dinâmico
// - 2 Matérias = 2 Planetas, 4 Matérias = 4 Planetas, etc.
// - Anéis de órbita visíveis para cada disciplina
// - Sol Central Acadêmico representando o Estudante
// - Zoom fluido com Scroll / Pinch e Tooltip Interativo Raycast
// ==========================================================================

const ScrollWorld = {
  scene: null,
  camera: null,
  renderer: null,
  controls: null,
  container: null,
  particles: null,
  sunGroup: null,
  planetsGroup: null,
  orbitRingsGroup: null,
  raycaster: null,
  pointer: null,
  hoveredPlanet: null,
  isInitialized: false,
  resizeObserver: null,
  animationFrameId: null,

  // Paleta de cores vibrantes para os planetas
  palette: [
    { color: 0x3b82f6, glow: 0x60a5fa, name: 'Azul' },
    { color: 0x10b981, glow: 0x34d399, name: 'Esmeralda' },
    { color: 0xf59e0b, glow: 0xfbbf24, name: 'Dourado' },
    { color: 0x8b5cf6, glow: 0xa78bfa, name: 'Púrpura' },
    { color: 0xec4899, glow: 0xf472b6, name: 'Rosa' },
    { color: 0x06b6d4, glow: 0x22d3ee, name: 'Ciano' },
    { color: 0xf97316, glow: 0xfb923c, name: 'Laranja' },
    { color: 0x14b8a6, glow: 0x2dd4bf, name: 'Verde-água' }
  ],

  cachedSubjects: [],

  init(canvasContainerId = 'scroll-world-container') {
    const container = document.getElementById(canvasContainerId);
    if (!container || typeof THREE === 'undefined') return;

    this.container = container;

    // Se já inicializado, apenas redimensiona e sincroniza
    if (this.isInitialized && this.renderer) {
      this.resize();
      this.loadSubjectsAndBuildPlanets();
      return;
    }

    // Dimensões do container (com fallback inteligente caso esteja temporariamente oculto)
    let width = container.clientWidth;
    let height = container.clientHeight || 360;

    if (width <= 0) {
      const parent = container.parentElement;
      width = (parent && parent.clientWidth > 0) ? parent.clientWidth : 1000;
    }

    // 1. Cena
    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.FogExp2(0x090d16, 0.0012);

    // 2. Câmera Perspectiva
    this.camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 2000);
    this.camera.position.set(0, 50, 150);

    // 3. Renderer WebGL
    this.renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.2;

    // Remover qualquer canvas existente
    const oldCanvases = container.querySelectorAll('canvas');
    oldCanvases.forEach(c => c.remove());

    container.appendChild(this.renderer.domElement);

    // 4. OrbitControls para Rotação 360° Livre em Qualquer Direção
    if (typeof THREE.OrbitControls !== 'undefined') {
      this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.06;
      this.controls.enableZoom = true;
      this.controls.minDistance = 35;
      this.controls.maxDistance = 320;
      this.controls.maxPolarAngle = Math.PI - 0.05; // Permite ver de baixo e de cima
      this.controls.minPolarAngle = 0.05;
      this.controls.autoRotate = true;
      this.controls.autoRotateSpeed = 0.5;
      this.controls.target.set(0, 0, 0);

      // Pausar rotação automática durante a interação do usuário
      this.renderer.domElement.addEventListener('pointerdown', () => {
        if (this.controls) this.controls.autoRotate = false;
      });
      this.renderer.domElement.addEventListener('pointerup', () => {
        setTimeout(() => {
          if (this.controls) this.controls.autoRotate = true;
        }, 3000);
      });
    }

    // 5. Iluminação Solar e Cósmica
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    this.scene.add(ambientLight);

    // Luz pontual central emitida pelo Sol (ilumina os planetas de dentro para fora)
    const sunLight = new THREE.PointLight(0xffffff, 3.5, 500);
    sunLight.position.set(0, 0, 0);
    this.scene.add(sunLight);

    // Luzes atmosféricas coloridas suaves
    const blueLight = new THREE.PointLight(0x3b82f6, 1.8, 350);
    blueLight.position.set(80, 50, 60);
    this.scene.add(blueLight);

    const purpleLight = new THREE.PointLight(0x8b5cf6, 1.5, 350);
    purpleLight.position.set(-80, -40, -60);
    this.scene.add(purpleLight);

    // 6. Raycaster & Ponteiro do Mouse para Hover nos Planetas
    this.raycaster = new THREE.Raycaster();
    this.pointer = new THREE.Vector2(-999, -999);

    container.addEventListener('mousemove', (e) => {
      const rect = container.getBoundingClientRect();
      this.pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    });

    container.addEventListener('mouseleave', () => {
      this.pointer.x = -999;
      this.pointer.y = -999;
      const tooltip = document.getElementById('planet-tooltip-3d');
      if (tooltip) tooltip.classList.add('hidden');
    });

    // 7. Criar Elementos da Cena Cósmica
    this.createStarfield();
    this.createCentralSun();

    this.orbitRingsGroup = new THREE.Group();
    this.scene.add(this.orbitRingsGroup);

    this.planetsGroup = new THREE.Group();
    this.scene.add(this.planetsGroup);

    // 8. Sincronizar com as Matérias Reais do Banco
    this.loadSubjectsAndBuildPlanets();

    // 9. Observador de Redimensionamento Automático
    if (window.ResizeObserver) {
      this.resizeObserver = new ResizeObserver(() => {
        this.resize();
      });
      this.resizeObserver.observe(container);
    }
    window.addEventListener('resize', () => this.resize());

    // 10. Ouvinte de Login para Sincronizar Imediatamente com o Aluno
    window.addEventListener('auth-success', () => {
      setTimeout(() => {
        this.resize();
        this.loadSubjectsAndBuildPlanets();
      }, 100);
    });

    // 11. Iniciar Loop de Animação
    this.isInitialized = true;
    this.animate();
  },

  // Campo de estrelas cósmicas no fundo
  createStarfield() {
    const starCount = 1200;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(starCount * 3);
    const colors = new Float32Array(starCount * 3);

    const colorChoices = [
      new THREE.Color(0x3b82f6),
      new THREE.Color(0x60a5fa),
      new THREE.Color(0x8b5cf6),
      new THREE.Color(0xffffff),
      new THREE.Color(0x34d399)
    ];

    for (let i = 0; i < starCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 800;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 600;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 800;

      const col = colorChoices[Math.floor(Math.random() * colorChoices.length)];
      colors[i * 3] = col.r;
      colors[i * 3 + 1] = col.g;
      colors[i * 3 + 2] = col.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 2.0,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending
    });

    this.particles = new THREE.Points(geometry, material);
    this.scene.add(this.particles);
  },

  // Sol Central Acadêmico (Núcleo do Estudante)
  createCentralSun() {
    this.sunGroup = new THREE.Group();

    // 1. Núcleo Solar de Plasma Branco/Dourado
    const coreGeo = new THREE.SphereGeometry(8.5, 32, 32);
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0xffffff
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    this.sunGroup.add(coreMesh);

    // 2. Halo / Atmosfera de Brilho Solar
    const glowGeo = new THREE.SphereGeometry(11.5, 24, 24);
    const glowMat = new THREE.MeshBasicMaterial({
      color: 0x3b82f6,
      transparent: true,
      opacity: 0.35,
      wireframe: true
    });
    const glowMesh = new THREE.Mesh(glowGeo, glowMat);
    this.sunGroup.add(glowMesh);

    // 3. Anel Equatorial Central
    const torusGeo = new THREE.TorusGeometry(17, 0.45, 16, 64);
    const torusMat = new THREE.MeshBasicMaterial({
      color: 0x60a5fa,
      transparent: true,
      opacity: 0.5,
      wireframe: true
    });
    const torus = new THREE.Mesh(torusGeo, torusMat);
    torus.rotation.x = Math.PI / 2.3;
    this.sunGroup.add(torus);

    this.scene.add(this.sunGroup);
  },

  // Busca as disciplinas do usuário e reconstrói o sistema solar
  async loadSubjectsAndBuildPlanets() {
    try {
      if (typeof API !== 'undefined' && API.getToken()) {
        const subjects = await API.getSubjects();
        this.cachedSubjects = subjects || [];
      } else {
        // Se ainda não estiver autenticado, tenta pegar do banco ou aguarda auth
        this.cachedSubjects = [];
      }
    } catch (err) {
      console.warn('ScrollWorld: Erro ao carregar matérias da API.', err);
      this.cachedSubjects = [];
    }

    this.buildPlanets(this.cachedSubjects);
  },

  // Constrói os planetas dinamicamente: 1 Matéria = 1 Planeta
  buildPlanets(subjects = []) {
    if (!this.planetsGroup || !this.orbitRingsGroup) return;

    // 1. Limpar planetas e órbitas anteriores
    while (this.planetsGroup.children.length > 0) {
      const obj = this.planetsGroup.children[0];
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) {
        if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
        else obj.material.dispose();
      }
      this.planetsGroup.remove(obj);
    }

    while (this.orbitRingsGroup.children.length > 0) {
      const ring = this.orbitRingsGroup.children[0];
      if (ring.geometry) ring.geometry.dispose();
      if (ring.material) ring.material.dispose();
      this.orbitRingsGroup.remove(ring);
    }

    // 2. Atualizar o contador de planetas no badge do HTML
    const countBadge = document.getElementById('planets-count-badge');
    const count = subjects.length;
    if (countBadge) {
      countBadge.textContent = `${count} ${count === 1 ? 'Planeta' : 'Planetas'}`;
    }

    if (count === 0) return;

    // 3. Criar exatamente 1 Planeta para cada Disciplina
    subjects.forEach((subject, i) => {
      const paletteItem = this.palette[i % this.palette.length];

      // Distância orbital escalonada e concêntrica
      const orbitRadius = 32 + (i * 18);

      // Tamanho do planeta baseado na carga horária (mínimo 4.2, máximo 7.5)
      const planetRadius = Math.min(7.5, Math.max(4.2, (subject.workload_hours || 60) / 12));

      // --- A. Desenhar Anel de Órbita Visível ---
      const orbitCurve = new THREE.EllipseCurve(0, 0, orbitRadius, orbitRadius, 0, 2 * Math.PI, false, 0);
      const orbitPoints = orbitCurve.getPoints(90);
      const orbitGeo = new THREE.BufferGeometry().setFromPoints(orbitPoints);
      const orbitMat = new THREE.LineBasicMaterial({
        color: paletteItem.color,
        transparent: true,
        opacity: 0.28
      });
      const orbitLine = new THREE.Line(orbitGeo, orbitMat);
      orbitLine.rotation.x = Math.PI / 2; // Coloca no plano horizontal (XZ)
      this.orbitRingsGroup.add(orbitLine);

      // --- B. Planeta 3D ---
      const planetGeo = new THREE.SphereGeometry(planetRadius, 32, 32);
      const planetMat = new THREE.MeshStandardMaterial({
        color: paletteItem.color,
        roughness: 0.3,
        metalness: 0.7,
        emissive: paletteItem.color,
        emissiveIntensity: 0.35
      });

      const planetMesh = new THREE.Mesh(planetGeo, planetMat);

      // Ângulo inicial distribuído harmoniosamente
      const initialAngle = (i * 2 * Math.PI) / count;
      planetMesh.position.x = Math.cos(initialAngle) * orbitRadius;
      planetMesh.position.z = Math.sin(initialAngle) * orbitRadius;
      planetMesh.position.y = (Math.sin(i * 1.5) * 4); // Leve inclinação natural

      // Metadados da Disciplina para Interatividade / Hover
      planetMesh.userData = {
        id: subject.id,
        name: subject.name,
        professor: subject.professor || 'Docente Responsável',
        workload_hours: subject.workload_hours || 60,
        hours_spent: ((subject.total_time_spent_minutes || 0) / 60).toFixed(1),
        orbitRadius: orbitRadius,
        orbitSpeed: 0.008 / Math.sqrt(i + 1), // Planetas mais próximos orbitam mais rápido (Lei Kepleriana)
        currentAngle: initialAngle,
        baseY: planetMesh.position.y,
        planetRadius: planetRadius,
        palette: paletteItem
      };

      // --- C. Atmosfera / Wireframe de Brilho Sutil ---
      const atmoGeo = new THREE.SphereGeometry(planetRadius * 1.18, 16, 16);
      const atmoMat = new THREE.MeshBasicMaterial({
        color: paletteItem.glow,
        wireframe: true,
        transparent: true,
        opacity: 0.25
      });
      const atmoMesh = new THREE.Mesh(atmoGeo, atmoMat);
      planetMesh.add(atmoMesh);

      // --- D. Se a matéria tiver >= 60h, adiciona Anel Planetário Estilo Saturno ---
      if ((subject.workload_hours || 0) >= 60) {
        const ringGeo = new THREE.RingGeometry(planetRadius * 1.4, planetRadius * 1.9, 32);
        const ringMat = new THREE.MeshBasicMaterial({
          color: paletteItem.glow,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: 0.45
        });
        const saturnRing = new THREE.Mesh(ringGeo, ringMat);
        saturnRing.rotation.x = Math.PI / 2.5;
        planetMesh.add(saturnRing);
      }

      this.planetsGroup.add(planetMesh);
    });
  },

  // Ajusta dimensões do Canvas e Câmera
  resize() {
    if (!this.container || !this.renderer || !this.camera) return;

    let width = this.container.clientWidth;
    let height = this.container.clientHeight || 360;

    if (width <= 0) {
      const parent = this.container.parentElement;
      width = (parent && parent.clientWidth > 0) ? parent.clientWidth : 1000;
    }

    if (width > 0 && height > 0) {
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    }
  },

  // Reseta câmera e controles para a visão inicial
  resetCamera() {
    if (this.controls) {
      this.controls.reset();
      this.camera.position.set(0, 50, 150);
      this.controls.target.set(0, 0, 0);
      this.controls.autoRotate = true;
      this.controls.update();
    }
  },

  // Raycasting para Tooltip e Hover nos Planetas
  checkPlanetHover() {
    if (!this.raycaster || !this.camera || !this.planetsGroup || !this.container) return;

    this.raycaster.setFromCamera(this.pointer, this.camera);
    const meshes = this.planetsGroup.children.filter(c => c.isMesh && c.userData && c.userData.name);
    const intersects = this.raycaster.intersectObjects(meshes);

    const tooltip = document.getElementById('planet-tooltip-3d');
    const nameEl = document.getElementById('planet-tooltip-name');
    const infoEl = document.getElementById('planet-tooltip-info');

    if (intersects.length > 0) {
      const hit = intersects[0].object;
      this.hoveredPlanet = hit;

      if (tooltip && nameEl && infoEl) {
        const rect = this.container.getBoundingClientRect();
        const vector = hit.position.clone();
        vector.applyMatrix4(this.planetsGroup.matrixWorld);
        vector.project(this.camera);

        const screenX = ((vector.x + 1) / 2) * rect.width;
        const screenY = ((-vector.y + 1) / 2) * rect.height;

        tooltip.style.left = `${screenX}px`;
        tooltip.style.top = `${screenY - 18}px`;
        nameEl.textContent = `🪐 ${hit.userData.name}`;
        infoEl.textContent = `${hit.userData.workload_hours}h Carga • ${hit.userData.hours_spent}h Estudadas • ${hit.userData.professor}`;
        tooltip.classList.remove('hidden');
      }

      this.container.style.cursor = 'pointer';
    } else {
      this.hoveredPlanet = null;
      if (tooltip) tooltip.classList.add('hidden');
      this.container.style.cursor = 'grab';
    }
  },

  // Loop de renderização e animação orbital fluida
  animate() {
    this.animationFrameId = requestAnimationFrame(() => this.animate());

    // 1. Atualizar OrbitControls (inércia, rotação e amortecimento 360°)
    if (this.controls) {
      this.controls.update();
    }

    // 2. Rotação do Sol Central e seus anéis
    if (this.sunGroup) {
      this.sunGroup.rotation.y += 0.006;
      this.sunGroup.rotation.z += 0.003;
    }

    // 3. Rotação do Campo de Estrelas
    if (this.particles) {
      this.particles.rotation.y += 0.0003;
      this.particles.rotation.x += 0.0001;
    }

    // 4. Translação e Rotação Individual de Cada Planeta (Disciplina)
    if (this.planetsGroup) {
      this.planetsGroup.children.forEach(child => {
        if (child.isMesh && child.userData && child.userData.orbitRadius) {
          // Auto-rotação no próprio eixo do planeta
          child.rotation.y += 0.02;

          // Movimento orbital contínuo ao redor do Sol
          child.userData.currentAngle += child.userData.orbitSpeed;
          const r = child.userData.orbitRadius;
          child.position.x = Math.cos(child.userData.currentAngle) * r;
          child.position.z = Math.sin(child.userData.currentAngle) * r;

          // Oscilação senoidal vertical suave
          child.position.y = child.userData.baseY + Math.sin(Date.now() * 0.002 + r) * 1.5;
        }
      });
    }

    // 5. Verificar Hover
    this.checkPlanetHover();

    // 6. Renderizar
    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  }
};
