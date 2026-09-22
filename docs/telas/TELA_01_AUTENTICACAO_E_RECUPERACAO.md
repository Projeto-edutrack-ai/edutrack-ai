# 🔐 Tela 01 — Autenticação, Cadastro & Recuperação de Senha

> **Módulo:** Controle de Acesso e Segurança  
> **Status:** Concluído & 100% Responsivo  
> **Arquivo Base:** `frontend/index.html` (Linhas 58–190), `frontend/js/auth.js`

---

## 1. Visão Geral
A tela de autenticação do **EduTrack AI** é apresentada como uma sobreposição (*modal overlay*) com efeito *glassmorphism* (`backdrop-blur-md`) e ambient orbs dinâmicos em segundo plano. Ela concentra o fluxo completo de entrada na plataforma com transição fluida entre login, cadastro e recuperação de credenciais.

---

## 2. Componentes e Funcionalidades

### 2.1. Cabeçalho da Marca
- **Logotipo Vetorial SVG:** Ícone estilizado de capelo acadêmico em degradê azul-índigo (`bg-gradient-to-tr from-blue-600 to-indigo-600`) com sombra luminosa.
- **Identificador de Marca:** Título "EduTrack" com badge `AI` estilizado em fonte monoespaçada.
- **Slogan:** "Assistente Educacional & Gestão Acadêmica Inteligente".

### 2.2. Alternância de Abas (Tabs)
- **Aba "Entrar":** Foco no acesso diário com e-mail e senha.
- **Aba "Criar Conta":** Expande o formulário para cadastro imediato com nome, e-mail e senha.
- **Transição Suave:** Indicador ativo com borda inferior destacada e troca de visibilidade sem recarregar a página.

### 2.3. Formulário de Login
- **Campo E-mail Acadêmico:** Validação de formato de e-mail com placeholder contextual (`aluno@edutrack.edu.br`).
- **Campo Senha:** Entrada segura com tipo `password`.
- **Link "Esqueceu a senha?":** Abre o modal dedicado de recuperação de senha.
- **Botão de Acesso:** Estilizado em degradê com efeito de micro-interação ao clique (`btn-press`).

### 2.4. Formulário de Cadastro
- **Campos:** Nome Completo, E-mail Acadêmico e Criação de Senha (mínimo de 6 caracteres).
- **Feedback Visual:** Exibe mensagens de erro customizadas caso o e-mail já esteja registrado.

### 2.5. Acesso Rápido — Conta de Demonstração
- **Botão Inteligente:** Permite ao avaliador preencher instantaneamente as credenciais do usuário demo (`aluno@edutrack.edu.br` / `senha123`) com apenas 1 clique.

### 2.6. Modal de Recuperação de Senha (Esqueci Minha Senha)
- **Modal Dedicado:** `#modal-forgot-password-overlay` com animação de entrada (`modal-animate-in`).
- **Preenchimento Inteligente:** Caso o usuário já tenha digitado o e-mail na tela de login, o modal o carrega automaticamente.
- **Integração com a API:** Conexão direta com a rota `POST /api/auth/forgot-password`.
- **Feedback em Tempo Real:** Alerta visual na tela e notificação via `Toast` confirmando o envio das instruções.

---

## 3. Comportamento Responsivo
- **Mobile (< 768px):** O card ocupa largura total com margens de segurança, inputs com tamanho de fonte de 16px para evitar zoom indesejado no Safari/iOS e botões de toque com altura mínima de 44px.
- **Desktop (>= 1024px):** Card centralizado com largura máxima otimizada (`max-w-md`), sombra profunda e profundidade tridimensional.

---

## 4. Endpoints de Integração Backend
| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/auth/login` | Autenticação com credenciais e geração de Token JWT |
| `POST` | `/api/auth/register` | Criação de nova conta de estudante |
| `POST` | `/api/auth/forgot-password` | Disparo do fluxo de recuperação de senha |
