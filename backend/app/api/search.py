from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.schemas.subject import SubjectResponse
from app.schemas.task import AcademicTaskResponse
from app.api.deps import get_current_user
from pydantic import BaseModel

class SearchResultResponse(BaseModel):
    query: str
    total_matches: int
    subjects: List[SubjectResponse]
    tasks: List[AcademicTaskResponse]

router = APIRouter(prefix="/search", tags=["Busca Global"])

@router.get("", response_model=SearchResultResponse)
def global_search(
    q: str = Query(..., min_length=1, description="Termo para busca"),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Busca global e avançada em todas as disciplinas e tarefas do usuário."""
    search_term = f"%{q}%"
    
    # Busca em disciplinas
    subjects = db.query(Subject).filter(
        Subject.user_id == current_user.id,
        (Subject.name.ilike(search_term) | Subject.professor.ilike(search_term) | Subject.description.ilike(search_term))
    ).all()
    
    # Busca em tarefas
    task_query = db.query(AcademicTask).filter(
        AcademicTask.user_id == current_user.id,
        (AcademicTask.title.ilike(search_term) | AcademicTask.description.ilike(search_term))
    )
    if status_filter:
        task_query = task_query.filter(AcademicTask.status == status_filter)
    tasks = task_query.all()

    # Mapear subjects para retorno
    subj_map = {s.id: s.name for s in db.query(Subject).filter(Subject.user_id == current_user.id).all()}
    task_responses = []
    for t in tasks:
        tr = AcademicTaskResponse.model_validate(t)
        tr.subject_name = subj_map.get(t.subject_id, "N/A")
        task_responses.append(tr)

    subject_responses = [SubjectResponse.model_validate(s) for s in subjects]

    return SearchResultResponse(
        query=q,
        total_matches=len(subject_responses) + len(task_responses),
        subjects=subject_responses,
        tasks=task_responses
    )
