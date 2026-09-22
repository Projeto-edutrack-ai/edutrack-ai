from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.ai_insights import AIInsightsResponse
from app.services.ai_service import AIService
from app.api.deps import get_current_user

router = APIRouter(prefix="/ai", tags=["Inteligência Artificial e Insights"])

@router.get("/insights", response_model=AIInsightsResponse)
def get_ai_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Gera diagnósticos e recomendações inteligentes de estudo:
    - Comparação entre tempo estimado vs. tempo real
    - Alertas de tarefas atrasadas e gargalos
    - Recomendações de reorganização de cronograma
    - Foco semanal prioritário
    """
    return AIService.generate_insights(db, current_user.id)
