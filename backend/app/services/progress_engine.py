from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.schemas.analytics import OverallProgressMetrics, SubjectProgressMetric, TimeDistributionResponse, TimeDistributionItem

class ProgressEngine:
    """
    Motor Python para cálculos avançados de progresso acadêmico,
    ponderação por carga horária e previsões de velocidade.
    """

    @staticmethod
    def calculate_subject_metrics(subject: Subject, tasks: List[AcademicTask]) -> SubjectProgressMetric:
        subject_tasks = [t for t in tasks if t.subject_id == subject.id]
        total_tasks = len(subject_tasks)
        completed_tasks = sum(1 for t in subject_tasks if t.status == "completed")
        in_progress_tasks = sum(1 for t in subject_tasks if t.status == "in_progress")
        pending_tasks = sum(1 for t in subject_tasks if t.status == "pending")

        progress_percentage = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0

        total_estimated = sum(t.estimated_time_minutes for t in subject_tasks)
        total_actual = sum(t.actual_time_minutes for t in subject_tasks)

        # Cálculo do desvio percentual entre tempo real e estimado
        if total_estimated > 0:
            time_deviation_percentage = ((total_actual - total_estimated) / total_estimated) * 100.0
        else:
            time_deviation_percentage = 0.0

        return SubjectProgressMetric(
            subject_id=subject.id,
            subject_name=subject.name,
            workload_hours=subject.workload_hours,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            pending_tasks=pending_tasks,
            progress_percentage=round(progress_percentage, 1),
            total_estimated_minutes=round(total_estimated, 1),
            total_actual_minutes=round(total_actual, 1),
            time_deviation_percentage=round(time_deviation_percentage, 1)
        )

    @classmethod
    def calculate_overall_metrics(cls, db: Session, user_id: int) -> OverallProgressMetrics:
        subjects = db.query(Subject).filter(Subject.user_id == user_id).all()
        tasks = db.query(AcademicTask).filter(AcademicTask.user_id == user_id).all()

        if not subjects:
            return OverallProgressMetrics(
                overall_simple_progress=0.0,
                overall_weighted_progress=0.0,
                total_subjects=0,
                total_tasks=0,
                completed_tasks=0,
                in_progress_tasks=0,
                pending_tasks=0,
                total_study_time_hours=0.0,
                estimated_remaining_hours=0.0,
                study_velocity_tasks_per_week=0.0,
                estimated_completion_date=None,
                subjects_breakdown=[]
            )

        subjects_breakdown: List[SubjectProgressMetric] = []
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == "completed")
        in_progress_tasks = sum(1 for t in tasks if t.status == "in_progress")
        pending_tasks = sum(1 for t in tasks if t.status == "pending")

        total_actual_minutes = sum(t.actual_time_minutes for t in tasks)
        
        # Tempo estimado restante das tarefas pendentes e em andamento
        remaining_minutes = sum(
            max(0.0, t.estimated_time_minutes - t.actual_time_minutes) if t.status != "completed" else 0.0
            for t in tasks
        )

        total_workload_hours = sum(s.workload_hours for s in subjects)
        weighted_progress_sum = 0.0

        for subject in subjects:
            metric = cls.calculate_subject_metrics(subject, tasks)
            subjects_breakdown.append(metric)
            if total_workload_hours > 0:
                weighted_progress_sum += (metric.progress_percentage * subject.workload_hours)

        overall_simple_progress = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0
        overall_weighted_progress = (weighted_progress_sum / total_workload_hours) if total_workload_hours > 0 else 0.0

        # Cálculo de velocidade de conclusão
        now = datetime.now(timezone.utc)
        four_weeks_ago = now - timedelta(days=28)
        
        recent_completed = [
            t for t in tasks 
            if t.status == "completed" and t.completed_at and t.completed_at.replace(tzinfo=timezone.utc if t.completed_at.tzinfo is None else t.completed_at.tzinfo) >= four_weeks_ago
        ]
        
        # Média de tarefas completadas por semana (últimas 4 semanas ou baseado no total)
        completed_recent_count = len(recent_completed) if recent_completed else (completed_tasks if completed_tasks > 0 else 1)
        velocity_weeks = 4.0 if recent_completed else 2.0
        study_velocity = completed_recent_count / velocity_weeks
        
        remaining_tasks_count = pending_tasks + in_progress_tasks
        if study_velocity > 0 and remaining_tasks_count > 0:
            weeks_needed = remaining_tasks_count / study_velocity
            est_date = (now + timedelta(days=weeks_needed * 7)).strftime("%d/%m/%Y")
        elif remaining_tasks_count == 0:
            est_date = "Concluído!"
        else:
            est_date = "Indeterminado (poucos dados)"

        return OverallProgressMetrics(
            overall_simple_progress=round(overall_simple_progress, 1),
            overall_weighted_progress=round(overall_weighted_progress, 1),
            total_subjects=len(subjects),
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            pending_tasks=pending_tasks,
            total_study_time_hours=round(total_actual_minutes / 60.0, 1),
            estimated_remaining_hours=round(remaining_minutes / 60.0, 1),
            study_velocity_tasks_per_week=round(study_velocity, 2),
            estimated_completion_date=est_date,
            subjects_breakdown=subjects_breakdown
        )

    @classmethod
    def get_time_distribution(cls, db: Session, user_id: int) -> TimeDistributionResponse:
        subjects = db.query(Subject).filter(Subject.user_id == user_id).all()
        tasks = db.query(AcademicTask).filter(AcademicTask.user_id == user_id).all()

        total_minutes = sum(t.actual_time_minutes for t in tasks)
        items: List[TimeDistributionItem] = []

        for subject in subjects:
            subject_tasks = [t for t in tasks if t.subject_id == subject.id]
            mins = sum(t.actual_time_minutes for t in subject_tasks)
            pct = (mins / total_minutes * 100.0) if total_minutes > 0 else 0.0
            
            items.append(TimeDistributionItem(
                subject_id=subject.id,
                subject_name=subject.name,
                minutes_spent=round(mins, 1),
                hours_spent=round(mins / 60.0, 1),
                percentage_of_total=round(pct, 1)
            ))

        return TimeDistributionResponse(
            total_minutes=round(total_minutes, 1),
            total_hours=round(total_minutes / 60.0, 1),
            distribution=items
        )
