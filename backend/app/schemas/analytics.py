from typing import List, Dict, Optional
from pydantic import BaseModel

class SubjectProgressMetric(BaseModel):
    subject_id: int
    subject_name: str
    workload_hours: float
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    progress_percentage: float
    total_estimated_minutes: float
    total_actual_minutes: float
    time_deviation_percentage: float  # Ex: +20% (gastou mais que o previsto)

class OverallProgressMetrics(BaseModel):
    overall_simple_progress: float        # Média simples das tarefas
    overall_weighted_progress: float      # Ponderada pela carga horária
    total_subjects: int
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    total_study_time_hours: float
    estimated_remaining_hours: float
    study_velocity_tasks_per_week: float
    estimated_completion_date: Optional[str] = None
    subjects_breakdown: List[SubjectProgressMetric]

class TimeDistributionItem(BaseModel):
    subject_id: int
    subject_name: str
    minutes_spent: float
    hours_spent: float
    percentage_of_total: float

class TimeDistributionResponse(BaseModel):
    total_minutes: float
    total_hours: float
    distribution: List[TimeDistributionItem]
