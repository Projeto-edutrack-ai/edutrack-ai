from typing import List, Optional, Literal
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, false, func
from app.core.search_text import search_key
from app.core.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.schemas.subject import SubjectResponse
from app.schemas.task import AcademicTaskResponse
from app.api.deps import get_current_user
from app.services.xano_crud import require_mirror, academic_source_scope
from pydantic import BaseModel


class SearchResultResponse(BaseModel):
    query: str
    total_matches: int
    subjects: List[SubjectResponse]
    tasks: List[AcademicTaskResponse]


router = APIRouter(prefix="/search", tags=["Busca Global"])


@router.get("", response_model=SearchResultResponse)
def global_search(
    q: str = Query("", max_length=200, description="Texto; vazio permite consultar somente atrasadas"),
    status_filter: Optional[Literal["pending", "in_progress", "completed"]] = Query(None, alias="status"),
    overdue: bool = Query(False, description="Nome/texto OU tarefas com prazo vencido e não concluídas"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_mirror(db, current_user, force=True)
    with academic_source_scope(db):
        return search_academic(db, current_user.id, q.strip(), status_filter, overdue)


def search_academic(db, user_id, q, status_filter=None, overdue=False):
    # Literal substring: escape SQL wildcard characters from user input.
    sqlite = db.get_bind().dialect.name == 'sqlite'
    term = search_key(q) if sqlite else q
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    pattern = f"%{escaped}%"
    now = datetime.now(timezone.utc)
    late = (AcademicTask.due_date < now) & (AcademicTask.status != "completed")
    late_subjects = db.query(AcademicTask.subject_id).filter(AcademicTask.user_id == user_id, late)
    def matches(column):
        if sqlite:
            return func.edutrack_search_key(column).like(pattern, escape="\\")
        return column.ilike(pattern, escape="\\")
    subject_match = or_(matches(Subject.name), matches(Subject.professor), matches(Subject.description)) if term else false()
    task_match = or_(matches(AcademicTask.title), matches(AcademicTask.description)) if term else false()
    if overdue:
        subject_match = or_(subject_match, Subject.id.in_(late_subjects))
        task_match = or_(task_match, late)
    subjects = db.query(Subject).filter(Subject.user_id == user_id, subject_match).order_by(Subject.name).all()
    tasks_query = db.query(AcademicTask).filter(AcademicTask.user_id == user_id, task_match)
    if status_filter:
        tasks_query = tasks_query.filter(AcademicTask.status == status_filter)
    tasks = tasks_query.order_by(AcademicTask.id).all()
    names = {s.id: s.name for s in db.query(Subject).filter(Subject.user_id == user_id).all()}
    result_tasks = []
    for task in tasks:
        result = AcademicTaskResponse.model_validate(task)
        result.subject_name = names.get(task.subject_id)
        result_tasks.append(result)
    return SearchResultResponse(query=q, total_matches=len(subjects)+len(tasks),
                                subjects=[SubjectResponse.model_validate(s) for s in subjects], tasks=result_tasks)
