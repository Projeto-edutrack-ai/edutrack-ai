# 🎓 EduTrack AI — Assistente Educacional Personalizado

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![OpenSpec](https://img.shields.io/badge/OpenSpec-v1.0-orange.svg)](openspec/tasks.md)
[![Status](https://img.shields.io/badge/Status-100%25%20Aprovado%20em%20Testes-brightgreen.svg)]()

> **Projeto Acadêmico de Graduação / Curso Superior**  
> Desenvolvido com a metodologia **Spec-Driven Development (OpenSpec)** com base na especificação de negócio do EduTrack AI.

---

## 📌 Principais Funcionalidades

- 🔐 **Autenticação Segura JWT**: Registro, login e recuperação de senha com isolamento multi-inquilino.
- 📚 **Gestão Canônica de Disciplinas (`subjects`)**: Cadastro de matérias com carga horária (`workload_hours`), ementa e professor.
- 📝 **Tarefas & Cronômetro de Estudo (`academic_tasks`)**: Gestão de atividades com comparação de **Tempo Estimado vs. Tempo Real** e cronômetro integrado.
- 📊 **Motor Python de Progresso Ponderado**: Algoritmo que calcula o progresso real do estudante ponderado pelas cargas horárias das disciplinas.
- 🎯 **Previsão de Conclusão & Velocity**: Estimativa de data de término do semestre baseada no ritmo de conclusão de tarefas.
- ✨ **Insights Inteligentes de IA**: Diagnósticos automáticos de desvio de cronograma (ex.: *"Você está levando 44% a mais de tempo em Python"*).
- 📄 **Exportação de Relatórios em PDF**: Emissão automática de relatórios semanais com formatação visual profissional via ReportLab.
- 🌓 **Interface Mobile-First Moderna**: Design responsivo com tema claro e escuro, gráficos em pizza e barras (Chart.js).
- 📂 **Documentação Viva OpenSpec**: Proposals formais, `tasks.md` e schemas em **XanoScript** (`.xs`).

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.

### 2. Instalar Dependências
```bash
pip install -r backend/requirements.txt
```

### 3. Iniciar o Sistema (Backend + Frontend)
Execute o comando unificado:
```bash
python run_server.py
```

O terminal exibirá:
- 🌐 **Interface do Aluno:** [http://localhost:8000](http://localhost:8000)
- 📖 **Documentação Interativa da API (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

### 🔑 Credenciais da Conta Demo Pré-configurada
- **Email:** `aluno@edutrack.edu.br`
- **Senha:** `senha123`
*(Você também pode clicar no botão "Entrar com Conta de Demonstração" na tela de login).*

---

## 🧪 Executar Testes Automatizados

O projeto possui uma suíte completa de testes cobrindo autenticação, isolamento de dados, cálculos matemáticos e geração de relatórios:

```bash
python -m pytest
```

---

## 📁 Estrutura do Projeto

```
edutrack-ai/
├── backend/
│   ├── app/
│   │   ├── api/             # Endpoints REST (auth, subjects, tasks, analytics, ai, reports, search)
│   │   ├── core/            # Configurações, segurança JWT e conexão de banco
│   │   ├── models/          # Modelos ORM canônicos (users, subjects, academic_tasks)
│   │   ├── schemas/         # Schemas de validação Pydantic
│   │   ├── services/        # Motor Python de progresso, IA e gerador de PDF
│   │   └── main.py          # Aplicação FastAPI principal
│   ├── seed_data.py         # População de dados demo realistas
│   └── requirements.txt     # Dependências do backend
├── frontend/
│   ├── css/styles.css       # Estilos e temas claro/escuro
│   ├── js/                  # Módulos JS (api, auth, dashboard, subjects, tasks, insights, app)
│   └── index.html           # Interface web/mobile responsiva
├── openspec/
│   ├── proposals/           # Proposals formais de cada funcionalidade
│   ├── specs/               # DER e especificações de banco
│   ├── xanoscript/          # Schemas programáticos XanoScript (.xs)
│   └── tasks.md             # Matriz viva de rastreabilidade
├── tests/                   # Suíte de testes automatizados com pytest
├── DOCUMENTACAO_ACADEMICA.md # Monografia técnica completa para entrega
├── GUIA_DE_APRESENTACAO.md  # Roteiro de fala e pitch para a banca
├── run_server.py            # Script único para iniciar todo o ecossistema
└── pytest.ini               # Configurações de teste
```

---

## 🏆 Avaliação e Defesa Acadêmica

Consulte os arquivos:
- 📄 [`DOCUMENTACAO_ACADEMICA.md`](./DOCUMENTACAO_ACADEMICA.md): Relatório técnico e formal para entrega escrita ao professor.
- 🎤 [`GUIA_DE_APRESENTACAO.md`](./GUIA_DE_APRESENTACAO.md): Roteiro de apresentação de 5 a 8 minutos com perguntas e respostas para a banca.
