from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.ai_insights import AIInsightsResponse, AIAskRequest, AIAskResponse
from app.services.ai_service import AIService
from app.api.deps import get_current_user
from app.services.xano_crud import require_mirror, academic_source_scope

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
    require_mirror(db, current_user)  # a IA analisa os dados reais do aluno no Xano
    with academic_source_scope(db):
        return AIService.generate_insights(db, current_user.id)

@router.post("/ask", response_model=AIAskResponse)
def ask_ai_assistant(
    payload: AIAskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permite ao estudante interagir com o Mentor Educacional de IA,
    fazendo perguntas pedagógicas, pedidos de orientação de cronograma ou dicas de estudo.
    """
    require_mirror(db, current_user)
    with academic_source_scope(db):
        return AIService.ask_assistant(db, current_user.id, payload.question)
