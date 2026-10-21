"""Sincronização Xano -> SQLite dos cursos/atividades vindos do Google Classroom.

Regras:
- Idempotente: identifica registros por (user_id, ID do Classroom); rodar de novo não duplica.
- Atualiza só os campos controlados pelo Classroom (nome/título, descrição, prazo, pontuação, link).
- Preserva campos locais: workload_hours, professor, datas do semestre, estimated/actual_time_minutes
  e o status manual da tarefa.
- Isolamento: toda consulta filtra por user_id; o export de outro usuário é rejeitado.
- Nunca apaga registros (nem os locais, nem os que sumiram do Classroom).
- Tudo ou nada: falha de banco faz rollback; erro/resposta inválida do Xano não toca no banco.
"""
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.subject import Subject
from app.models.task import AcademicTask
from app.services.classroom_mapper import (
    CanonicalCourse,
    CanonicalCoursework,
    InvalidExportError,
    initial_status,
    parse_export,
    resolve_status_on_update,
    subject_values,
    task_values,
)
from app.services.xano_client import XanoInvalidResponseError

SOURCE_CLASSROOM = "classroom"


class ClassroomSyncError(Exception):
    """Falha ao gravar no banco local (a transação foi revertida)."""


@dataclass
class SyncResult:
    user_id: int
    courses_created: int = 0
    courses_updated: int = 0
    courses_unchanged: int = 0
    tasks_created: int = 0
    tasks_updated: int = 0
    tasks_unchanged: int = 0
    tasks_completed_by_classroom: int = 0
    skipped_courses: int = 0
    skipped_coursework: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _apply(obj: Any, values: Dict[str, Any]) -> bool:
    """Atribui apenas o que mudou; devolve True se algo foi alterado."""
    changed = False
    for key, value in values.items():
        if getattr(obj, key) != value:
            setattr(obj, key, value)
            changed = True
    return changed


def sync_user_from_xano(
    db: Session,
    user_id: int,
    client: Any,
    since: Optional[Any] = None,
) -> SyncResult:
    """Importa o export do Xano do usuário ``user_id`` para o SQLite local.

    ``client`` precisa expor ``get_export(local_user_id, since=None)`` (ex.: XanoClient).
    Exceções XanoError do cliente propagam sem alterar o banco.
    """
    payload = client.get_export(user_id, since=since)
    try:
        parsed = parse_export(payload, expected_user_id=user_id)
    except InvalidExportError as exc:
        raise XanoInvalidResponseError(str(exc)) from exc

    result = SyncResult(
        user_id=user_id,
        skipped_courses=parsed.skipped_courses,
        skipped_coursework=parsed.skipped_coursework,
        errors=list(parsed.errors),
        warnings=list(parsed.warnings),
    )
    now = _utcnow()
    try:
        for course in parsed.courses:
            subject = _upsert_subject(db, user_id, course, now, result)
            for work in course.coursework:
                _upsert_task(db, user_id, subject, work, now, result)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise ClassroomSyncError("Falha ao gravar a sincronização no banco local") from exc
    except Exception:
        db.rollback()
        raise
    return result


def _upsert_subject(
    db: Session, user_id: int, course: CanonicalCourse, now: datetime, result: SyncResult
) -> Subject:
    values = subject_values(course)
    subject = (
        db.query(Subject)
        .filter(Subject.user_id == user_id, Subject.classroom_course_id == course.google_course_id)
        .first()
    )
    if subject is None:
        subject = Subject(
            user_id=user_id,
            source=SOURCE_CLASSROOM,
            classroom_course_id=course.google_course_id,
            classroom_synced_at=now,
            **values,
        )
        db.add(subject)
        db.flush()  # precisa do id para vincular as atividades
        result.courses_created += 1
        return subject

    changed = _apply(subject, values)
    subject.classroom_synced_at = now
    if changed:
        result.courses_updated += 1
    else:
        result.courses_unchanged += 1
    return subject


def _upsert_task(
    db: Session,
    user_id: int,
    subject: Subject,
    work: CanonicalCoursework,
    now: datetime,
    result: SyncResult,
) -> AcademicTask:
    values = task_values(work)
    task = (
        db.query(AcademicTask)
        .filter(
            AcademicTask.user_id == user_id,
            AcademicTask.subject_id == subject.id,
            AcademicTask.classroom_coursework_id == work.google_coursework_id,
        )
        .first()
    )

    if task is None:
        status = initial_status(work.submission_state)
        task = AcademicTask(
            user_id=user_id,
            subject_id=subject.id,
            source=SOURCE_CLASSROOM,
            classroom_coursework_id=work.google_coursework_id,
            classroom_submission_state=work.submission_state,
            classroom_synced_at=now,
            status=status,
            completed_at=(work.submission_updated_at or now) if status == "completed" else None,
            **values,
        )
        db.add(task)
        result.tasks_created += 1
        if status == "completed":
            result.tasks_completed_by_classroom += 1
        return task

    changed = _apply(task, values)
    if work.has_submission:
        previous_state = task.classroom_submission_state
        new_status, completed_now = resolve_status_on_update(task.status, previous_state, work.submission_state)
        changed |= _apply(task, {"classroom_submission_state": work.submission_state})
        if completed_now:
            task.status = new_status
            task.completed_at = work.submission_updated_at or now
            result.tasks_completed_by_classroom += 1
            changed = True
    # Sem dados de entrega no export: mantém o estado anterior (dado incompleto não apaga nada)
    task.classroom_synced_at = now
    if changed:
        result.tasks_updated += 1
    else:
        result.tasks_unchanged += 1
    return task
