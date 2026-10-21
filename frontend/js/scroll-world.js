// Three.js & Scroll World Engine for EduTrack AI
// Cria um universo 3D interativo com nós acadêmicos, constelações e câmera guiada por scroll

const ScrollWorld = {
  scene: null,
  camera: null,
  renderer: null,
  particles: null,
  nodesGroup: null,
  coreRing: null,
  mouse: { x: 0, y: 0, targetX: 0, targetY: 0 },
  isInitialized: false,

  init(canvasContainerId = 'scroll-world-container') {
    const container = document.getElementById(canvasContainerId);
    if (!container || typeof THREE === 'undefined') return;

    // Dimensões
    const width = container.clientWidth;
    const height = container.clientHeight || 450;

    // 1. Cena
    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.FogExp2(0x090d16, 0.0018);

    // 2. Câmera
    this.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 2000);
    this.camera.position.set(0, 0, 120);

    // 3. Renderer
    this.renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;

    // Limpar container anterior se houver
    container.innerHTML = '';
    container.appendChild(this.renderer.domElement);

    // 4. Iluminação
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    this.scene.add(ambientLight);

    const pointLight1 = new THREE.PointLight(0x3b82f6, 3, 300);
    pointLight1.position.set(50, 50, 50);
    this.scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0x8b5cf6, 2.5, 300);
    pointLight2.position.set(-50, -30, -20);
    this.scene.add(pointLight2);

    const pointLight3 = new THREE.PointLight(0x10b981, 2, 250);
    pointLight3.position.set(0, -60, 40);
    this.scene.add(pointLight3);

    // 5. Criar Objetos 3D
    this.createParticleStarfield();
    this.createAcademicNodes();
    this.createCentralProgressHologram();

    // 6. Listeners de Interatividade
    this.bindEvents(container);

    // 7. Loop de Animação
    this.animate();
    this.isInitialized = true;

    // 8. Integrar com GSAP ScrollTrigger
    this.setupScrollTrigger();
  },

  createParticleStarfield() {
    const particleCount = 1200;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const colorPalette = [
      new THREE.Color(0x3b82f6), // Azul
      new THREE.Color(0x8b5cf6), // Roxo
      new THREE.Color(0x10b981), // Verde
      new THREE.Color(0x60a5fa)  // Azul claro
    ];

    for (let i = 0; i < particleCount; i++) {
      // Posições esparsas no espaço
      positions[i * 3] = (Math.random() - 0.5) * 600;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 500;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 600;

      // Cores gradientes
      const col = colorPalette[Math.floor(Math.random() * colorPalette.length)];
      colors[i * 3] = col.r;
      colors[i * 3 + 1] = col.g;
      colors[i * 3 + 2] = col.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // Material de partículas
    const material = new THREE.PointsMaterial({
      size: 2.2,
      vertexColors: true,
      transparent: true,
      opacity: 0.7,
      blending: THREE.AdditiveBlending
    });

    this.particles = new THREE.Points(geometry, material);
    this.scene.add(this.particles);
  },

  createAcademicNodes() {
    this.nodesGroup = new THREE.Group();

    // Disciplinas como Nós 3D Flutuantes
    const nodesData = [
      { name: "Python & IA", color: 0x3b82f6, pos: [-45, 20, -10], radius: 6.5, speed: 0.01 },
      { name: "Estrutura de Dados", color: 0x10b981, pos: [45, 25, -20], radius: 6.0, speed: 0.012 },
      { name: "Banco de Dados", color: 0xf59e0b, pos: [-40, -25, 10], radius: 5.5, speed: 0.008 },
      { name: "Eng. de Software", color: 0x8b5cf6, pos: [38, -20, -5], radius: 5.0, speed: 0.015 },
      { name: "OpenSpec Core", color: 0xec4899, pos: [0, 42, -30], radius: 7.0, speed: 0.009 }
    ];

    const nodesList = [];

    nodesData.forEach((data) => {
      // Geometria Icosaedro Futurista
      const geometry = new THREE.IcosahedronGeometry(data.radius, 1);
      const material = new THREE.MeshStandardMaterial({
        color: data.color,
        roughness: 0.2,
        metalness: 0.8,
        wireframe: false,
        emissive: data.color,
        emissiveIntensity: 0.25
      });

      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(...data.pos);
      mesh.userData = { ...data, initialPos: [...data.pos] };

      // Wireframe exterior sutil
      const wireGeo = new THREE.IcosahedronGeometry(data.radius * 1.25, 1);
      const wireMat = new THREE.MeshBasicMaterial({
        color: data.color,
        wireframe: true,
        transparent: true,
        opacity: 0.25
      });
      const wireMesh = new THREE.Mesh(wireGeo, wireMat);
      mesh.add(wireMesh);

      this.nodesGroup.add(mesh);
      nodesList.push(mesh);
    });

    // Conectar nós com linhas de laser/constelação
    const lineMaterial = new THREE.LineBasicMaterial({
      color: 0x3b82f6,
      transparent: true,
      opacity: 0.3
    });

    for (let i = 0; i < nodesList.length; i++) {
      for (let j = i + 1; j < nodesList.length; j++) {
        const lineGeo = new THREE.BufferGeometry().setFromPoints([
          nodesList[i].position,
          nodesList[j].position
        ]);
        const line = new THREE.Line(lineGeo, lineMaterial);
        this.nodesGroup.add(line);
      }
    }

    this.scene.add(this.nodesGroup);
  },

  createCentralProgressHologram() {
    const ringGroup = new THREE.Group();

    // Anel Torus Holográfico Central
    const torusGeo = new THREE.TorusGeometry(18, 0.6, 16, 100);
    const torusMat = new THREE.MeshStandardMaterial({
      color: 0x60a5fa,
      emissive: 0x3b82f6,
      emissiveIntensity: 0.6,
      roughness: 0.1,
      metalness: 0.9,
      wireframe: true
    });
    const torus = new THREE.Mesh(torusGeo, torusMat);
    ringGroup.add(torus);

    // Segundo anel inclinado
    const torusGeo2 = new THREE.TorusGeometry(22, 0.4, 16, 100);
    const torusMat2 = new THREE.MeshBasicMaterial({
      color: 0x8b5cf6,
      transparent: true,
      opacity: 0.4,
      wireframe: true
    });
    const torus2 = new THREE.Mesh(torusGeo2, torusMat2);
    torus2.rotation.x = Math.PI / 3;
    ringGroup.add(torus2);

    // Núcleo Esférico Brilhante
    const coreGeo = new THREE.SphereGeometry(6, 32, 32);
    const coreMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      emissive: 0x3b82f6,
      emissiveIntensity: 0.8,
      roughness: 0.3,
      metalness: 0.5
    });
    const coreSphere = new THREE.Mesh(coreGeo, coreMat);
    ringGroup.add(coreSphere);

    this.coreRing = ringGroup;
    this.scene.add(this.coreRing);
  },

  bindEvents(container) {
    // Parallax suave do mouse
    window.addEventListener('mousemove', (e) => {
      this.mouse.targetX = (e.clientX / window.innerWidth - 0.5) * 2;
      this.mouse.targetY = (e.clientY / window.innerHeight - 0.5) * 2;
    });

    // Redimensionamento Responsivo
    window.addEventListener('resize', () => {
      if (!this.renderer || !this.camera || !container) return;
      const w = container.clientWidth;
      const h = container.clientHeight || 450;
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h);
    });
  },

  setupScrollTrigger() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
    gsap.registerPlugin(ScrollTrigger);

    // Animar a câmera e nós 3D conforme o scroll do usuário no documento
    ScrollTrigger.create({
      trigger: 'body',
      start: 'top top',
      end: 'bottom bottom',
      scrub: 1.5,
      onUpdate: (self) => {
        const progress = self.progress; // 0.0 a 1.0

        // Câmera viaja pelo Scroll World
        if (this.camera) {
          this.camera.position.z = 120 - (progress * 70);
          this.camera.position.y = (progress * 30) - 10;
          this.camera.rotation.z = progress * Math.PI * 0.5;
        }

        // Rotação dos grupos 3D
        if (this.nodesGroup) {
          this.nodesGroup.rotation.y = progress * Math.PI * 2;
        }

        if (this.coreRing) {
          this.coreRing.rotation.x = progress * Math.PI;
          this.coreRing.rotation.y = progress * Math.PI * 1.5;
        }

        if (this.particles) {
          this.particles.rotation.y = progress * 0.8;
        }
      }
    });
  },

  animate() {
    requestAnimationFrame(() => this.animate());

    // Suavização do mouse (Interpolação Linear)
    this.mouse.x += (this.mouse.targetX - this.mouse.x) * 0.05;
    this.mouse.y += (this.mouse.targetY - this.mouse.y) * 0.05;

    // Rotação contínua sutil
    if (this.particles) {
      this.particles.rotation.y += 0.0006;
      this.particles.rotation.x += 0.0003;
    }

    if (this.coreRing) {
      this.coreRing.rotation.z += 0.005;
      this.coreRing.rotation.y += 0.008;
    }

    if (this.nodesGroup) {
      this.nodesGroup.children.forEach((child, index) => {
        if (child.isMesh && child.userData) {
          child.rotation.x += child.userData.speed || 0.01;
          child.rotation.y += child.userData.speed || 0.01;
          // Efeito de levitação senoidal
          const t = Date.now() * 0.0015 + index;
          child.position.y = child.userData.initialPos[1] + Math.sin(t) * 3;
        }
      });
    }

    // Parallax de câmera com mouse
    if (this.camera) {
      this.camera.position.x += (this.mouse.x * 15 - this.camera.position.x) * 0.05;
      this.camera.position.y += (-this.mouse.y * 10 - this.camera.position.y) * 0.05;
      this.camera.lookAt(0, 0, 0);
    }

    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  }
};
