# Guia de Apresentação Acadêmica: EduTrack AI

Use este roteiro para apresentar seu projeto para os professores e banca avaliadora com máxima clareza e impacto!

---

## 🎯 Estrutura da Apresentação (Pitch de 5 a 8 minutos)

### 1. Introdução e O Problema (1 minuto)
> *"Boa noite, professores. O EduTrack AI nasceu para solucionar uma dor real de todo estudante universitário: a sobrecarga e a falsa impressão de progresso. Muitas vezes fazemos várias tarefas pequenas e achamos que estamos adiantados, mas a matéria mais pesada do semestre está atrasada. Além disso, raramente medimos quanto tempo realmente levamos para estudar em comparação com o que planejamos."*

### 2. Metodologia: Spec-Driven Development com OpenSpec (1 minuto)
> *"Neste projeto, atuamos como Arquitetos de Soluções. Usamos a metodologia **OpenSpec (Spec-Driven Development)**: escrevemos as propostas de negócio e arquitetura técnica primeiro (`openspec/proposals/`), e guiamos os agentes de IA para implementar o backend em Python e os schemas em XanoScript. Cada linha de código possui rastreabilidade com o nosso `tasks.md`."*

### 3. Demonstração Prática do Sistema (3 a 4 minutos)
Abra a interface rodando em `http://localhost:8000`:
1. **Login Rápido**: Clique em *"Entrar com Conta de Demonstração"* (`aluno@edutrack.edu.br`).
2. **Dashboard & Progresso Ponderado**: Mostre a diferença entre a *Média Simples* e o *Progresso Ponderado por Carga Horária* (calculado pelo microserviço em Python).
3. **Cronômetro de Estudo**:
   - Selecione a tarefa *"Projeto Prático: Integração com API Gemini"*.
   - Inicie o cronômetro, mostre a contagem em tempo real e clique em *"Salvar Estudo"*.
   - Mostre como o tempo real é persistido via API REST (`POST /api/academic_tasks/{id}/study-time`).
4. **Módulo de IA & Comparativo Estimado vs. Real**:
   - Vá na aba *"✨ Insights de IA & PDF"*.
   - Mostre os diagnósticos: *"Você está levando +44% de tempo em Python do que o planejado. Recomendamos dividir tópicos complexos"*.
   - Mostre os alertas de matérias com prazos próximos e sugestões de reorganização.
5. **Geração do Relatório Semanal PDF**:
   - Clique em *"📄 Baixar Relatório Semanal (PDF)"*.
   - Abra o PDF baixado e mostre a formatação profissional gerada pelo ReportLab com tabelas de desvios e KPIs.

### 4. Conclusão & Tecnologias (1 minuto)
> *"Em resumo, entregamos um ecossistema completo: Frontend Mobile-First, Backend Python com FastAPI, persistência relacional com schemas XanoScript, motor de métricas ponderadas, IA de recomendação e relatórios automatizados em PDF. Obrigado!"*

---

## ❓ Perguntas Frequentes da Banca e Como Responder

### Pergunta 1: *"Por que usar cálculo ponderado em vez de média simples de tarefas?"*
**Resposta:** *"Porque uma tarefa de uma disciplina de 80h tem um impacto formativo e avaliativo muito maior do que uma disciplina de 20h. O progresso ponderado dá a real dimensão do semestre para o estudante."*

### Pergunta 2: *"Como funciona a geração dos insights de IA caso o aluno esteja sem internet?"*
**Resposta:** *"Implementamos uma arquitetura híbrida de IA. Se houver chave do Gemini configurada, usamos IA Generativa. Caso contrário, o sistema ativa automaticamente o nosso motor heurístico em Python, que analisa os dados e gera os diagnósticos de desvio de forma instantânea e 100% offline."*

### Pergunta 3: *"Como foi garantida a segurança e o isolamento dos dados?"*
**Resposta:** *"Utilizamos autenticação JWT com senhas criptografadas via PBKDF2 HMAC SHA-256 com salt. Todas as consultas SQL filtram estritamente pelo `user_id` do token validado, garantindo que nenhum aluno veja as disciplinas ou notas de outro."*
