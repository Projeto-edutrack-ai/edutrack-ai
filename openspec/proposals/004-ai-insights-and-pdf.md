# Proposal 004: Inteligência Artificial, Recomendações e Relatórios Semanais PDF

**Status:** Aprovado / Implementado  
**Autor:** Aluno (Arquiteto de Soluções) & EduTrack AI Agent  
**Versão:** 1.0  
**Contexto:** Requisitos Funcionais 7 e 8 (Features Avançadas)  

## 1. Intenção de Negócio
Gerar valor cognitivo para o estudante através de diagnósticos inteligentes sobre desvios de tempo (Tempo Estimado vs. Real), alertas de prazos iminentes e emissão de relatórios consolidados em formato PDF para acompanhamento semanal.

## 2. Especificação do Módulo de IA
1. **Comparativo Estimado vs Real**:
   - Se desvio $\ge +25\%$, emite alerta preventivo de gargalo.
   - Se desvio $\le -30\%$, reconhece alto rendimento e sugere realocação de tempo.
2. **Alertas de Prazo**:
   - Tarefas com prazo $< 0$ dias geram alertas críticos.
   - Tarefas com prazo $\le 3$ dias entram na lista de foco da semana.
3. **Suporte Híbrido**:
   - Integração com Google Gemini 1.5 Flash quando `GEMINI_API_KEY` estiver presente.
   - Fallback para motor heurístico inteligente em Python quando operando offline/sem chave.

## 3. Especificação do Relatório PDF (ReportLab)
- **Estrutura**:
  - Cabeçalho institucional EduTrack AI com dados do estudante e carimbo de data/hora.
  - Tabela com KPIs executivos (progresso ponderado, horas totais, velocity, data estimada).
  - Tabela detalhada de matérias com desvios coloridos.
  - Seção de Insights de IA e Foco Semanal.
