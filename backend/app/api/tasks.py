from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.schemas.task import AcademicTaskCreate, AcademicTaskUpdate, AcademicTaskResponse, AddStudyTimeRequest
from app.api.deps import get_current_user

router = APIRouter(prefix="/academic_tasks", tags=["Tarefas Acadêmicas"])

@router.get("", response_model=List[AcademicTaskResponse])
def list_tasks(
    subject_id: Optional[int] = Query(None, description="Filtrar por disciplina"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filtrar por status: pending, in_progress, completed"),
    search: Optional[str] = Query(None, description="Filtrar por título ou descrição"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista tarefas acadêmicas com múltiplos filtros."""
    query = db.query(AcademicTask).filter(AcademicTask.user_id == current_user.id)
    
    if subject_id:
        query = query.filter(AcademicTask.subject_id == subject_id)
    if status_filter:
        query = query.filter(AcademicTask.status == status_filter)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (AcademicTask.title.ilike(search_fmt)) | (AcademicTask.description.ilike(search_fmt))
        )

    tasks = query.order_by(AcademicTask.due_date.asc().nulls_last(), AcademicTask.id.desc()).all()
    
    # Mapear nome da disciplina para enriquecimento da resposta
    subjects_map = {s.id: s.name for s in db.query(Subject).filter(Subject.user_id == current_user.id).all()}
    
    result = []
    for t in tasks:
        resp = AcademicTaskResponse.model_validate(t)
        resp.subject_name = subjects_map.get(t.subject_id, "Disciplina Desconhecida")
        result.append(resp)

    return result

@router.post("", response_model=AcademicTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: AcademicTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria uma nova tarefa acadêmica vinculada a uma disciplina do usuário."""
    subject = db.query(Subject).filter(
        Subject.id == task_in.subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Disciplina vinculada não encontrada ou não pertence ao usuário.")

    completed_at = datetime.now(timezone.utc) if task_in.status == "completed" else None

    new_task = AcademicTask(
        user_id=current_user.id,
        subject_id=task_in.subject_id,
        title=task_in.title.strip(),
        description=task_in.description,
        due_date=task_in.due_date,
        status=task_in.status,
        estimated_time_minutes=task_in.estimated_time_minutes,
        actual_time_minutes=task_in.actual_time_minutes,
        completed_at=completed_at
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    resp = AcademicTaskResponse.model_validate(new_task)
    resp.subject_name = subject.name
    return resp

@router.get("/{task_id}", response_model=AcademicTaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém os detalhes de uma tarefa acadêmica."""
    task = db.query(AcademicTask).filter(
        AcademicTask.id == task_id,
        AcademicTask.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    
    subject = db.query(Subject).filter(Subject.id == task.subject_id).first()
    resp = AcademicTaskResponse.model_validate(task)
    resp.subject_name = subject.name if subject else None
    return resp

@router.put("/{task_id}", response_model=AcademicTaskResponse)
def update_task(
    task_id: int,
    task_in: AcademicTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza uma tarefa acadêmica."""
    task = db.query(AcademicTask).filter(
        AcademicTask.id == task_id,
        AcademicTask.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    update_data = task_in.model_dump(exclude_unset=True)

    # Tratar mudança de status para completed ou reabertura
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == "completed" and task.status != "completed":
            task.completed_at = datetime.now(timezone.utc)
        elif new_status != "completed":
            task.completed_at = None

    for field, val in update_data.items():
        setattr(task, field, val)

    db.commit()
    db.refresh(task)

    subject = db.query(Subject).filter(Subject.id == task.subject_id).first()
    resp = AcademicTaskResponse.model_validate(task)
    resp.subject_name = subject.name if subject else None
    return resp

@router.post("/{task_id}/study-time", response_model=AcademicTaskResponse)
def record_study_time(
    task_id: int,
    payload: AddStudyTimeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Registra minutos adicionais de estudo (ex: vindos do cronômetro da interface)."""
    task = db.query(AcademicTask).filter(
        AcademicTask.id == task_id,
        AcademicTask.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    task.actual_time_minutes += payload.additional_minutes
    if payload.new_status:
        task.status = payload.new_status
        if payload.new_status == "completed":
            task.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)

    subject = db.query(Subject).filter(Subject.id == task.subject_id).first()
    resp = AcademicTaskResponse.model_validate(task)
    resp.subject_name = subject.name if subject else None
    return resp

@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exclui uma tarefa acadêmica."""
    task = db.query(AcademicTask).filter(
        AcademicTask.id == task_id,
        AcademicTask.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

    db.delete(task)
    db.commit()
    return {"message": f"Tarefa '{task.title}' excluída com sucesso.", "id": task_id}
