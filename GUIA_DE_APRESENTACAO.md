> Revisão de 10/11/2026: integração Classroom removida por decisão da equipe. Trechos históricos abaixo não descrevem a versão atual; não apresente sincronização Classroom como funcionalidade ativa. Consulte README.md e docs/PENDENCIAS.md.

# Guia de Apresentação & Roteiro do Vídeo: EduTrack AI

Este documento contém o roteiro completo, passo a passo, para a gravação do vídeo de entrega acadêmica do **EduTrack AI**, cobrindo 100% dos critérios avaliativos exigidos.

---

## 📋 Checklist dos Critérios de Entrega

- [x] **Parte 1 — Demonstração das Funcionalidades do Sistema:**
  - [x] **Login** (autenticação JWT e preenchimento rápido da conta demo).
  - [x] **Esqueci minha senha** (fluxo de recuperação e feedback visual).
  - [x] **Cadastro de usuário** (criação de nova conta com hash PBKDF2).
  - [x] **IA (Diagnósticos e Insights)** (análise heurística local + suporte Gemini).
  - [x] **Relatório (PDF)** (geração profissional via ReportLab com download).
  - [x] **Disciplinas** (listagem, carga horária, progresso e gerenciamento).
  - [x] **Tarefas** (status, prazos, estimativas e cronômetro de estudo Pomodoro).
- [x] **Parte 2 — Banco de Dados e Modelagem:**
  - [x] Arquivo SQLite `edutrack.db` e tabelas relacionais (`users`, `subjects`, `academic_tasks`).
  - [x] Modelos SQLAlchemy ORM em Python (`backend/app/models/`).
  - [x] Diagrama Entidade-Relacionamento (DER) e Dicionário de Dados em `openspec/specs/database-schema.md`.
- [x] **Parte 3 — GitHub, Arquitetura e OpenSpec:**
  - [x] **Estrutura do Repositório**: divisão clara entre `backend/`, `frontend/`, `tests/` e `openspec/`.
  - [x] **Programas e Stack**: Python 3.12, FastAPI, SQLAlchemy, SQLite, ReportLab, Vanilla JS/Tailwind.
  - [x] **OpenSpec (Spec-Driven Development)**: rastreabilidade viva em `tasks.md`, contratos em `specs/`, proposals e histórico de evolução da versão 1 (`edutrack-ai`) para a versão atual (`edutrack`).

---

## 🎬 Roteiro Passo a Passo para o Vídeo (Tempo sugerido: 5 a 8 minutos)

### 🚀 Preparação Inicial (Antes de Gravar)
1. Certifique-se de que o backend está rodando:
   ```powershell
   python run_server.py
   ```
2. Abra no navegador: `http://localhost:8000`
3. Deixe aberto em outra aba o VS Code ou explorador de arquivos na pasta do projeto e o GitHub.

---

### PARTE 1: Demonstração das Funcionalidades na Interface (3 a 4 min)

#### 1. Tela Inicial e Esqueci Minha Senha
- **O que falar:** *"Olá! Vamos apresentar o EduTrack AI, um ecossistema inteligente de apoio à gestão acadêmica. Começamos pela autenticação segura."*
- **Ação:** Mostre a tela de login. Clique no link **"Esqueceu a senha?"**.
- **O que falar:** *"O sistema possui o fluxo de recuperação de senha via `/api/auth/forgot-password`, gerando notificação e instruções para o email do estudante."*
- **Ação:** Digite `aluno@edutrack.edu.br` no prompt e confirme. Mostre o Toast de sucesso verde.

#### 2. Cadastro de Usuário
- **Ação:** Clique na aba **"Criar Conta"**.
- **O que falar:** *"O cadastro cria um novo estudante no banco de dados com senha criptografada via PBKDF2 HMAC SHA-256 com salt individual."*
- **Ação:** Preencha:
  - Nome: `Mariana Silva`
  - Email: `mariana@edutrack.edu.br`
  - Senha: `senha123`
- Clique em **"Criar Minha Conta"**. O sistema cria o usuário e já faz o login automático!

#### 3. Login com Conta de Demonstração
- **Ação:** Faça logout (ícone de sair no card do aluno na barra lateral esquerda).
- **O que falar:** *"Para visualizar o histórico acadêmico completo com métricas já acumuladas, vamos utilizar a conta demo."*
- **Ação:** Clique no botão azul **"Entrar com Conta de Demonstração"** e em **"Acessar Meu Painel"**.

#### 4. Disciplinas (Gestão Acadêmica)
- **Ação:** Clique no menu lateral **"Disciplinas"** (ou use o atalho `⌘2`).
- **O que falar:** *"Aqui temos o gerenciamento completo de disciplinas com carga horária, professor e progresso percentual."*
- **Ação:** Mostre os cards existentes (Python & IA, Banco de Dados, etc.).
- **Ação:** Clique em **"+ Nova Disciplina"**, cadastre uma matéria rápida (ex: *Engenharia de Software*, Prof. Carlos, Carga: 60h) e salve.

#### 5. Tarefas & Cronômetro Pomodoro de Estudo
- **Ação:** Clique no menu lateral **"Tarefas & Estudos"** (ou atalho `⌘3`).
- **O que falar:** *"As tarefas acadêmicas possuem status, data de entrega, estimativa de tempo e tempo real."*
- **Ação:** Mostre os filtros (Todas, Pendentes, Em Andamento, Concluídas).
- **Ação:** Volte ao **Dashboard 3D** (menu 1) e mostre o widget do **Cronômetro Interativo**:
  - Selecione uma tarefa pendente.
  - Clique em **Iniciar Estudo**. Mostre os segundos rodando e o efeito visual de foco.
  - Clique em **Pausar** e depois em **Salvar Estudo** para persistir o tempo gasto diretamente no banco (`/study-time`).

#### 6. Inteligência Artificial (Diagnósticos & Insights)
- **Ação:** Clique no menu **"✨ Insights de IA & PDF"**.
- **O que falar:** *"O módulo de IA analisa a discrepância entre tempo planejado e tempo real. O sistema utiliza uma arquitetura híbrida: se houver chave da API Gemini do Google configurada, gera síntese generativa; caso contrário, executa nosso motor analítico heurístico local em Python."*
- **Ação:** Destaque na tela o diagnóstico: *"Você está levando +44% de tempo em Python... Recomendamos dividir tópicos complexos"*, além dos alertas de gargalo e foco semanal.

#### 7. Geração de Relatório Profissional em PDF
- **Ação:** No topo da página de Insights, clique no botão **"📄 Baixar Relatório Semanal (PDF)"**.
- **O que falar:** *"O backend em FastAPI utiliza a biblioteca ReportLab para compilar os dados em um PDF elegante com gráficos vetoriais, status ponderado e tabela analítica de desvios."*
- **Ação:** Abra o PDF baixado e mostre o cabeçalho, os KPIs e a formatação profissional.

---

### PARTE 2: Apresentação do Banco de Dados e Modelo (1 a 2 min)

- **O que falar:** *"Agora vamos ao banco de dados e à modelagem relacional da aplicação."*
- **Ação:** Abra o arquivo `openspec/specs/database-schema.md` no VS Code ou visualize a visualização Mermaid:
  1. **Diagrama Entidade-Relacionamento (DER):**
     - Explique o relacionamento 1:N entre `users` e `subjects` (um aluno possui várias disciplinas).
     - Explique o relacionamento 1:N entre `subjects` e `academic_tasks` (uma disciplina contém várias tarefas).
     - Explique o vínculo de isolamento `user_id` em todas as tabelas (garantia de multi-tenancy e privacidade).
  2. **Modelos SQLAlchemy:**
     - Abra `backend/app/models/user.py`, `subject.py` e `task.py`.
     - Mostre as colunas canônicas tipadas e os relacionamentos bidirecionais (`relationship`).
  3. **Persistência SQLite:**
     - Mostre o arquivo `edutrack.db` na raiz e explique que o banco é inicializado automaticamente na inicialização via `init_db()` com migrações aditivas seguras.

---

### PARTE 3: Apresentação do GitHub, Estrutura, Programas e OpenSpec (1 a 2 min)

- **O que falar:** *"Por fim, vamos analisar a estrutura do repositório no GitHub, a stack tecnológica e a governança com OpenSpec."*
- **Ação:** Mostre a árvore do projeto no VS Code / GitHub:
  1. **Estrutura de Pastas:**
     - `backend/app/`: Arquitetura em camadas (API routes, core security/database, models, schemas Pydantic, services).
     - `frontend/`: Interface moderna Mobile-First com Tailwind CSS, GSAP e Three.js para o ambiente 3D.
     - `tests/`: Bateria com 84 testes automatizados cobrindo autenticação, cálculo ponderado de métricas e integrações.
     - `openspec/`: Metodologia Spec-Driven Development.
  2. **Stack Tecnológica / Programas:**
     - Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, SQLite, ReportLab, Pytest, Uvicorn.
  3. **OpenSpec (Metodologia e Evolução do Projeto):**
     - Abra a pasta `openspec/`:
       - `project.md`: Visão arquitetural e convenções.
       - `tasks.md`: Matriz viva de rastreabilidade de todas as 26 tarefas do projeto.
       - `specs/`: Contratos formais (`database-schema.md` e `xano-classroom-contract.md`).
       - `proposals/`: Propostas históricas da solução.
     - **O que mudou da Versão 1 (`edutrack-ai`) para a Versão 2 (`edutrack`):**
       - *"Comparando com a versão inicial anexada: na v2 estruturamos a integração completa com Google Classroom e Xano, criamos migrações de schema aditivas sem quebra (`migrations.py`), expandimos a suíte de testes de testes básicos para 84 testes unitários e de integração, limpamos credenciais sensíveis e adotamos o OpenSpec CLI oficial para validação automatizada (`openspec validate --all`)."*

---

## 🏆 Dicas para a Gravação
- Grave a tela inteira em 1080p usando OBS Studio, Xbox Game Bar (`Win + G`) ou Loom.
- Mantenha a voz firme e pausada.
- O roteiro acima cobre com folga e precisão todos os critérios da banca!
