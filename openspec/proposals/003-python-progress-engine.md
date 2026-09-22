# Proposal 003: Motor Python de Cálculo Avançado de Progresso e Métricas

**Status:** Aprovado / Implementado  
**Autor:** Aluno (Arquiteto de Soluções) & EduTrack AI Agent  
**Versão:** 1.0  
**Contexto:** Requisito Funcional 5 (Features Intermediárias)  

## 1. Intenção de Negócio
Superar a limitação de médias aritméticas simples através de um algoritmo estatístico em Python que calcula o progresso ponderado pela carga horária de cada matéria, quantifica a velocidade de entrega semanal e projeta a data de conclusão das demandas do período.

## 2. Fórmulas Matemáticas Implementadas

### 2.1 Progresso Ponderado por Carga Horária ($P_{ponderado}$)
$$P_{ponderado} = \frac{\sum_{i=1}^{n} (P_i \times C_i)}{\sum_{i=1}^{n} C_i}$$
Onde:
- $P_i$: Percentual de conclusão da disciplina $i$ ($\frac{\text{Tarefas Concluídas}}{\text{Total de Tarefas}} \times 100$)
- $C_i$: Carga horária da disciplina $i$ (`workload_hours`)

### 2.2 Desvio de Tempo ($D_t$)
$$D_t = \frac{T_{real} - T_{estimado}}{T_{estimado}} \times 100\%$$
- $D_t > 0$: Aluno levou mais tempo que o previsto (gargalo de aprendizado).
- $D_t < 0$: Aluno executou a atividade mais rápido que o previsto (alta eficiência).

### 2.3 Projeção de Velocidade e Data de Término
$$\text{Velocidade} = \frac{\text{Tarefas Concluídas nos últimos 28 dias}}{4 \text{ semanas}}$$
$$\text{Semanas Restantes} = \frac{\text{Tarefas Pendentes e Em Andamento}}{\text{Velocidade}}$$
$$\text{Data Estimada} = \text{Data Atual} + (\text{Semanas Restantes} \times 7 \text{ dias})$$
