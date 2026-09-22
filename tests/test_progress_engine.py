import pytest
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.services.progress_engine import ProgressEngine

def test_calculate_subject_metrics():
    """Testa cálculo de métricas de disciplina individual."""
    subject = Subject(id=1, user_id=1, name="Cálculo 1", workload_hours=80.0)
    tasks = [
        AcademicTask(id=1, user_id=1, subject_id=1, title="T1", status="completed", estimated_time_minutes=60, actual_time_minutes=90),
        AcademicTask(id=2, user_id=1, subject_id=1, title="T2", status="pending", estimated_time_minutes=60, actual_time_minutes=0),
    ]

    metric = ProgressEngine.calculate_subject_metrics(subject, tasks)
    
    assert metric.total_tasks == 2
    assert metric.completed_tasks == 1
    assert metric.progress_percentage == 50.0
    assert metric.total_estimated_minutes == 120.0
    assert metric.total_actual_minutes == 90.0
    # Desvio: (90 - 120) / 120 = -25%
    assert metric.time_deviation_percentage == -25.0

def test_calculate_time_deviation_positive():
    """Testa cálculo de desvio positivo quando aluno demora mais."""
    subject = Subject(id=1, user_id=1, name="Python", workload_hours=60.0)
    tasks = [
        AcademicTask(id=1, user_id=1, subject_id=1, title="T1", status="completed", estimated_time_minutes=100, actual_time_minutes=150),
    ]

    metric = ProgressEngine.calculate_subject_metrics(subject, tasks)
    # Desvio: (150 - 100) / 100 = +50%
    assert metric.time_deviation_percentage == 50.0
