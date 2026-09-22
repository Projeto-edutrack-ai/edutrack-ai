import os
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.schemas.ai_insights import AIInsightsResponse, InsightRecommendation
from app.services.progress_engine import ProgressEngine

class AIService:
    """
    Serviço de Inteligência Artificial para análise de desempenho e recomendações.
    Suporta integração com a API Gemini do Google e motor analítico de fallback baseado em regras inteligentes.
    """

    @classmethod
    def generate_insights(cls, db: Session, user_id: int) -> AIInsightsResponse:
        metrics = ProgressEngine.calculate_overall_metrics(db, user_id)
        subjects = db.query(Subject).filter(Subject.user_id == user_id).all()
        tasks = db.query(AcademicTask).filter(AcademicTask.user_id == user_id).all()

        if not subjects:
            return AIInsightsResponse(
                summary="Cadastre suas primeiras disciplinas e tarefas para receber diagnósticos inteligentes de IA.",
                generated_by="EduTrack AI Analytics Engine",
                recommendations=[],
                critical_alerts=[],
                weekly_focus=["Cadastrar disciplinas do semestre", "Adicionar primeiras tarefas"]
            )

        # Se houver chave da API Gemini, tentamos usar o Gemini
        if settings.GEMINI_API_KEY:
            try:
                gemini_result = cls._call_gemini(metrics, tasks, subjects)
                if gemini_result:
                    return gemini_result
            except Exception as e:
                print(f"[AIService] Falha ao chamar Gemini ({e}), usando motor inteligente local.")

        # Fallback para o motor analítico inteligente local
        return cls._generate_heuristic_insights(metrics, tasks, subjects)

    @classmethod
    def _generate_heuristic_insights(cls, metrics, tasks: List[AcademicTask], subjects: List[Subject]) -> AIInsightsResponse:
        recommendations: List[InsightRecommendation] = []
        critical_alerts: List[str] = []
        weekly_focus: List[str] = []

        now = datetime.now(timezone.utc)
        
        # 1. Análise de Desvio de Tempo (Tempo Estimado vs Tempo Real)
        for s_metric in metrics.subjects_breakdown:
            dev = s_metric.time_deviation_percentage
            if dev >= 25.0:
                msg = f"Você está levando {dev:+.0f}% mais tempo em '{s_metric.subject_name}' do que o planejado ({s_metric.total_actual_minutes:.0f}m gastos vs {s_metric.total_estimated_minutes:.0f}m estimados)."
                recommendations.append(InsightRecommendation(
                    category="time_management",
                    type="warning",
                    title=f"Atenção ao Cronograma: {s_metric.subject_name}",
                    message=msg,
                    action_suggested="Replaneje as próximas tarefas aumentando o tempo estimado ou divida tópicos complexos em subtarefas menores.",
                    subject_id=s_metric.subject_id,
                    subject_name=s_metric.subject_name
                ))
                critical_alerts.append(f"Gargalo detectado em {s_metric.subject_name}: desvio de {dev:+.0f}% do tempo previsto.")
            elif dev <= -30.0 and s_metric.completed_tasks > 0:
                msg = f"Excelente eficiência em '{s_metric.subject_name}'! Você concluiu as tarefas em {abs(dev):.0f}% menos tempo do que o estimado."
                recommendations.append(InsightRecommendation(
                    category="time_management",
                    type="success",
                    title=f"Alta Performance: {s_metric.subject_name}",
                    message=msg,
                    action_suggested="Aproveite o tempo livre ganho nesta matéria para reforçar disciplinas mais desafiadoras.",
                    subject_id=s_metric.subject_id,
                    subject_name=s_metric.subject_name
                ))

        # 2. Análise de Prazos Próximos e Atrasos
        overdue_tasks = []
        upcoming_tasks = []
        for t in tasks:
            if t.status != "completed" and t.due_date:
                due_utc = t.due_date.replace(tzinfo=timezone.utc if t.due_date.tzinfo is None else t.due_date.tzinfo)
                if due_utc < now:
                    overdue_tasks.append(t)
                elif due_utc <= now + timedelta(days=3):
                    upcoming_tasks.append(t)

        if overdue_tasks:
            critical_alerts.append(f"Você possui {len(overdue_tasks)} tarefa(s) atrasada(s). Priorize sua conclusão imediata!")
            recommendations.append(InsightRecommendation(
                category="priority_alert",
                type="alert",
                title="Tarefas Atrasadas Detectadas",
                message=f"Existem {len(overdue_tasks)} tarefas com prazo vencido pendentes.",
                action_suggested="Dedique o próximo bloco de estudos exclusivamente para liquidar as pendências atrasadas."
            ))

        if upcoming_tasks:
            weekly_focus.append(f"Focar nas {len(upcoming_tasks)} tarefas que vencem nos próximos 3 dias.")
            recommendations.append(InsightRecommendation(
                category="schedule_optimization",
                type="info",
                title="Prazos Iminentes nos Próximos 3 Dias",
                message=f"Você tem {len(upcoming_tasks)} tarefa(s) com entrega prevista para esta semana.",
                action_suggested="Reserve blocos com cronômetro hoje para evitar acúmulo de última hora."
            ))

        # 3. Análise de Ponderação e Disciplinas com Maior Carga Horária
        if subjects:
            max_workload_subj = max(subjects, key=lambda s: s.workload_hours)
            s_metric = next((m for m in metrics.subjects_breakdown if m.subject_id == max_workload_subj.id), None)
            if s_metric and s_metric.progress_percentage < 50.0:
                weekly_focus.append(f"Acelerar '{max_workload_subj.name}' (peso de {max_workload_subj.workload_hours}h no semestre).")
                recommendations.append(InsightRecommendation(
                    category="priority_alert",
                    type="info",
                    title=f"Disciplina de Alto Peso: {max_workload_subj.name}",
                    message=f"Esta disciplina possui {max_workload_subj.workload_hours}h de carga horária e seu progresso atual é de {s_metric.progress_percentage:.0f}%.",
                    action_suggested="Priorize blocos semanais fixos para não comprometer o progresso geral ponderado."
                ))

        # Resumo executivo
        summary_text = (
            f"Seu progresso ponderado geral é de {metrics.overall_weighted_progress:.1f}%, "
            f"com {metrics.completed_tasks} de {metrics.total_tasks} tarefas concluídas e "
            f"{metrics.total_study_time_hours:.1f} horas de estudo registradas. "
            f"Velocidade média atual: {metrics.study_velocity_tasks_per_week:.1f} tarefas/semana."
        )

        if not weekly_focus:
            weekly_focus = ["Manter a cadência de estudos diária", "Registrar tempos reais com o cronômetro"]

        return AIInsightsResponse(
            summary=summary_text,
            generated_by="EduTrack Heuristic Analytics AI",
            recommendations=recommendations,
            critical_alerts=critical_alerts,
            weekly_focus=weekly_focus
        )

    @classmethod
    def _call_gemini(cls, metrics, tasks: List[AcademicTask], subjects: List[Subject]) -> Optional[AIInsightsResponse]:
        """Chamada opcional via Google Gemini API se configurada."""
        import urllib.request
        
        prompt_data = {
            "metrics": metrics.model_dump(),
            "subjects": [{"id": s.id, "name": s.name, "workload": s.workload_hours} for s in subjects],
            "tasks_summary": {
                "total": len(tasks),
                "completed": sum(1 for t in tasks if t.status == "completed"),
                "pending": sum(1 for t in tasks if t.status == "pending"),
                "in_progress": sum(1 for t in tasks if t.status == "in_progress")
            }
        }
        
        system_instruction = (
            "Você é o assistente pedagógico de IA do EduTrack AI. Analise os dados acadêmicos do aluno "
            "e retorne um JSON estrito correspondente ao schema AIInsightsResponse com summary, recommendations, "
            "critical_alerts e weekly_focus, em português brasileiro."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_instruction}\n\nDados do Aluno:\n{json.dumps(prompt_data, ensure_ascii=False)}"}]
            }],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }

        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            resp_body = json.loads(response.read().decode('utf-8'))
            text_content = resp_body['candidates'][0]['content']['parts'][0]['text']
            data = json.loads(text_content)
            data["generated_by"] = "Gemini 1.5 Flash AI Engine"
            return AIInsightsResponse(**data)
