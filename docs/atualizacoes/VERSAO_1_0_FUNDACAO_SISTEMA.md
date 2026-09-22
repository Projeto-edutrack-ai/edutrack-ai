# 📦 Atualização v1.0 — Fundação do Sistema, Arquitetura & OpenSpec

> **Data de Lançamento:** Janeiro de 2026  
> **Status:** Concluído & Testado  
> **Escopo:** Backend FastAPI, Banco Relacional, Autenticação JWT, Motor Analítico e Relatório PDF

---

## 1. Contexto & Necessidade do Projeto
O **EduTrack AI** nasceu da especificação OpenSpec v1.0 com o propósito de suprir a necessidade dos estudantes universitários de possuírem um assistente educacional com **inteligência temporal**. Em vez de tratar todas as matérias de forma homogênea, a plataforma calcula o progresso acadêmico **ponderado pela carga horária** de cada disciplina e analisa a discrepância entre o tempo estimado e o tempo real de estudo.

---

## 2. O Que Foi Desenvolvido Nesta Versão

### 2.1. Arquitetura de Backend
- **Framework:** FastAPI com tipagem estrita e documentação automática Swagger UI (`/docs`).
- **Banco de Dados Relacional:** SQLAlchemy ORM estruturado em SQLite (`edutrack.db`).
- **Segurança & Criptografia:** Senhas com salt e hash seguro (`bcrypt`), geração e validação de tokens JWT (`Bearer token`).

### 2.2. Modelagem de Dados
- **Tabela `users`:** Armazenamento de credenciais e identificação básica do aluno.
- **Tabela `subjects`:** Registro de disciplinas, nomes de docentes, carga horária e ementa.
- **Tabela `tasks`:** Atividades vinculadas a disciplinas, prazos, status (`pending`, `in_progress`, `completed`), minutos estimados e minutos reais de estudo.

### 2.3. Motor Analítico & Heurística de IA
- **Progresso Ponderado:** Algoritmo que calcula:
  $$\text{Progresso Ponderado} = \frac{\sum (\text{Progresso da Disciplina} \times \text{Carga Horária})}{\sum \text{Carga Horária Total}}$$
- **Velocidade de Estudo:** Cálculo de tarefas concluídas por semana.
- **Previsão de Conclusão:** Estimativa de data de término do semestre baseada na cadência do aluno.
- **Geração de Diagnósticos de IA:** Algoritmo heurístico que detecta sobrecarga de estudo, estresse de prazos e desvios de estimativa.

### 2.4. Exportação em PDF com ReportLab
- Criação do endpoint `GET /api/reports/weekly-pdf` gerando relatórios com layout vetorial profissional e gráficos integrados para entrega acadêmica.

---

## 3. Arquivos Criados Nesta Versão
- `backend/app/main.py`: Ponto de entrada do FastAPI.
- `backend/app/models/`: Modelos SQLAlchemy (`user.py`, `subject.py`, `task.py`).
- `backend/app/api/`: Roteadores de autenticação, matérias, tarefas, analítica e IA.
- `backend/seed_data.py`: Carga inicial de dados para demonstração com usuário demo.
- `tests/test_api.py`, `tests/test_auth.py`: Bateria inicial de testes automatizados com pytest.
