# 📚 Tela 03 — Gerenciamento de Disciplinas

> **Módulo:** Gestão Acadêmica  
> **Status:** Concluído & 100% Responsivo  
> **Arquivo Base:** `frontend/index.html` (Linhas 505–528 e 870–910), `frontend/js/subjects.js`

---

## 1. Visão Geral
A tela de **Disciplinas** do EduTrack AI oferece controle total sobre a grade curricular do estudante. Cada disciplina possui peso na ponderação acadêmica baseado em sua respectiva carga horária, permitindo um planejamento realista das metas semestrais.

---

## 2. Componentes e Funcionalidades

### 2.1. Cabeçalho & Ações
- **Título & Descrição:** Identificação clara do módulo de matérias cursadas.
- **Botão "Nova Disciplina":** Abre o modal dedicado para cadastramento de matéria.
- **Filtro em Tempo Real:** Campo de pesquisa instantânea por nome da matéria ou nome do docente.

### 2.2. Grid de Cards de Disciplinas
- **Cards com Estilo Moderno:** Renderizados com a classe `.pro-card` e animações escalonadas de entrada via GSAP (`stagger`).
- **Informações Exibidas por Card:**
  - Nome da Disciplina e Professor responsável.
  - Carga Horária em horas (peso no cálculo do progresso geral).
  - Barra de progresso individual da disciplina.
  - Quantidade de tarefas vinculadas pendentes vs. concluídas.
  - Ações de **Editar** e **Excluir** com confirmação e mensagens de feedback via `Toast`.

### 2.3. Modal de Cadastro e Edição de Disciplina
- **Identificador do Modal:** `#modal-subject-overlay`.
- **Campos do Formulário:**
  - Nome da Disciplina (obrigatório).
  - Professor(a) responsável.
  - Carga Horária em Horas (obrigatório, numérico com valor padrão sugerido).
  - Ementa / Descrição detalhada dos tópicos da matéria.
- **Ações:** Botões "Cancelar" e "Salvar Disciplina" com animações suaves de clique.

---

## 3. Comportamento Responsivo
- **Mobile (< 768px):** Grid em 1 coluna única facilitando a leitura de todos os detalhes sem aperto visual; botões de ação ocupam largura confortável para o toque dos dedos.
- **Tablet (768px - 1023px):** Grid organizado em 2 colunas com distribuição balanceada.
- **Desktop (>= 1024px):** Grid expansivo em 3 colunas, proporcionando ampla visão de toda a grade curricular.

---

## 4. Endpoints de Integração Backend
| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/subjects` | Listagem de todas as disciplinas com suporte a busca |
| `POST` | `/api/subjects` | Criação de uma nova disciplina |
| `PUT` | `/api/subjects/{id}` | Edição dos dados de uma disciplina existente |
| `DELETE` | `/api/subjects/{id}` | Exclusão de uma disciplina e reajuste automático das métricas |
