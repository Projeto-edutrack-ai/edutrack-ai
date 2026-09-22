from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import OverallProgressMetrics, TimeDistributionResponse
from app.services.progress_engine import ProgressEngine
from app.api.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics e Métricas"])

@router.get("/progress", response_model=OverallProgressMetrics)
def get_progress_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna métricas avançadas calculadas pelo motor Python:
    - Progresso simples
    - Progresso ponderado pela carga horária
    - Horas estudadas e restantes
    - Velocidade de conclusão e data estimada
    - Detalhamento por disciplina com desvio de tempo
    """
    return ProgressEngine.calculate_overall_metrics(db, current_user.id)

@router.get("/time-spent", response_model=TimeDistributionResponse)
def get_time_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna a distribuição de tempo estudado por disciplina para gráficos em pizza/barras."""
    return ProgressEngine.get_time_distribution(db, current_user.id)
