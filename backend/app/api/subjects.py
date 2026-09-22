from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/subjects", tags=["Disciplinas"])

@router.get("", response_model=List[SubjectResponse])
def list_subjects(
    search: Optional[str] = Query(None, description="Filtrar por nome ou professor"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todas as disciplinas do usuário autenticado com métricas calculadas."""
    query = db.query(Subject).filter(Subject.user_id == current_user.id)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Subject.name.ilike(search_fmt)) | (Subject.professor.ilike(search_fmt))
        )
    
    subjects = query.order_by(Subject.name.asc()).all()
    user_tasks = db.query(AcademicTask).filter(AcademicTask.user_id == current_user.id).all()

    result = []
    for s in subjects:
        s_tasks = [t for t in user_tasks if t.subject_id == s.id]
        total = len(s_tasks)
        completed = sum(1 for t in s_tasks if t.status == "completed")
        time_spent = sum(t.actual_time_minutes for t in s_tasks)
        pct = (completed / total * 100.0) if total > 0 else 0.0

        subj_dict = SubjectResponse.model_validate(s)
        subj_dict.total_tasks = total
        subj_dict.completed_tasks = completed
        subj_dict.progress_percentage = round(pct, 1)
        subj_dict.total_time_spent_minutes = round(time_spent, 1)
        result.append(subj_dict)

    return result

@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_in: SubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cria uma nova disciplina vinculada ao usuário logado."""
    new_subject = Subject(
        user_id=current_user.id,
        name=subject_in.name.strip(),
        professor=subject_in.professor.strip() if subject_in.professor else None,
        workload_hours=subject_in.workload_hours,
        description=subject_in.description,
        start_date=subject_in.start_date,
        end_date=subject_in.end_date
    )
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    
    resp = SubjectResponse.model_validate(new_subject)
    resp.total_tasks = 0
    resp.completed_tasks = 0
    resp.progress_percentage = 0.0
    resp.total_time_spent_minutes = 0.0
    return resp

@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtém uma disciplina específica do usuário."""
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada.")
    
    tasks = db.query(AcademicTask).filter(AcademicTask.subject_id == subject_id).all()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == "completed")
    time_spent = sum(t.actual_time_minutes for t in tasks)
    pct = (completed / total * 100.0) if total > 0 else 0.0

    resp = SubjectResponse.model_validate(subject)
    resp.total_tasks = total
    resp.completed_tasks = completed
    resp.progress_percentage = round(pct, 1)
    resp.total_time_spent_minutes = round(time_spent, 1)
    return resp

@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    subject_in: SubjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza os dados de uma disciplina existente."""
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada.")

    update_data = subject_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(subject, field, val)

    db.commit()
    db.refresh(subject)
    return SubjectResponse.model_validate(subject)

@router.delete("/{subject_id}", status_code=status.HTTP_200_OK)
def delete_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exclui uma disciplina e suas tarefas associadas."""
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.user_id == current_user.id
    ).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada.")

    db.delete(subject)
    db.commit()
    return {"message": f"Disciplina '{subject.name}' excluída com sucesso.", "id": subject_id}
