"""Rotas /api/classroom: o frontend fala só com o FastAPI; o FastAPI fala com o Xano.

Fluxo: Google Classroom -> Xano (OAuth, tokens, Classroom API) -> FastAPI (esta camada) -> SQLite.
Os tokens do Google nunca chegam aqui. Nenhuma rota devolve a XANO_API_KEY nem corpo bruto de erro.
"""
import logging
import threading
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.subject import Subject
from app.models.task import AcademicTask
from app.models.user import User
from app.schemas.classroom import (
    ClassroomConnectResponse, ClassroomCourseOut, ClassroomLocalSummary, ClassroomStatus,
    ClassroomSyncRequest, ClassroomSyncResponse, ClassroomTaskOut, RemoteCourseOut,
)
from app.services.classroom_mapper import parse_xano_datetime, InvalidItemError
from app.services.classroom_sync import SOURCE_CLASSROOM, ClassroomSyncError, sync_user_from_xano
from app.services.xano_client import (
    XanoClient, XanoConfigError, XanoConnectionError, XanoError, XanoHTTPError,
    XanoInvalidResponseError, XanoTimeoutError,
)

logger = logging.getLogger("edutrack.classroom")
router = APIRouter(prefix="/classroom", tags=["Google Classroom"])

_sync_locks: Dict[int, threading.Lock] = {}
_sync_locks_guard = threading.Lock()
_REMOTE_SUMMARY_KEYS = ("status", "courses", "coursework", "submissions", "errors")


def get_xano_client() -> XanoClient:
    """Dependência (substituível nos testes)."""
    return XanoClient()


def _lock_for(user_id: int) -> threading.Lock:
    with _sync_locks_guard:
        return _sync_locks.setdefault(user_id, threading.Lock())


def xano_http_error(exc: Exception) -> HTTPException:
    """Traduz falhas do Xano em respostas HTTP seguras (detalhes só no log do servidor)."""
    logger.warning("Falha na integração com o Xano: %s", exc)
    if isinstance(exc, XanoConfigError):
        return HTTPException(503, "Integração com o Xano não configurada no servidor (XANO_BASE_URL/XANO_API_KEY).")
    if isinstance(exc, XanoTimeoutError):
        return HTTPException(504, "O Xano demorou demais para responder. Tente novamente.")
    if isinstance(exc, XanoConnectionError):
        return HTTPException(502, "Não foi possível conectar ao Xano.")
    if isinstance(exc, XanoHTTPError):
        if exc.status_code == 409:
            return HTTPException(409, "Google Classroom não conectado. Conecte sua conta primeiro.")
        return HTTPException(502, f"O Xano recusou ou falhou na requisição (HTTP {exc.status_code}).")
    if isinstance(exc, XanoInvalidResponseError):
        return HTTPException(502, "Resposta inválida do Xano.")
    return HTTPException(502, "Erro na integração com o Xano.")


def _local_summary(db: Session, user_id: int) -> ClassroomLocalSummary:
    courses = db.query(Subject).filter(Subject.user_id == user_id, Subject.source == SOURCE_CLASSROOM).count()
    tasks = db.query(AcademicTask).filter(AcademicTask.user_id == user_id, AcademicTask.source == SOURCE_CLASSROOM).count()
    last = db.query(func.max(AcademicTask.classroom_synced_at)).filter(AcademicTask.user_id == user_id).scalar()
    last_subject = db.query(func.max(Subject.classroom_synced_at)).filter(Subject.user_id == user_id).scalar()
    candidates = [d for d in (last, last_subject) if d is not None]
    return ClassroomLocalSummary(courses=courses, tasks=tasks, last_synced_at=max(candidates) if candidates else None)


@router.get("/status", response_model=ClassroomStatus)
def classroom_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    client: XanoClient = Depends(get_xano_client),
):
    """Estado da integração. Responde 200 mesmo sem Xano configurado/acessível (a UI mostra o motivo)."""
    local = _local_summary(db, current_user.id)
    if not client.is_configured():
        return ClassroomStatus(configured=False, reachable=False, connected=False, status="not_configured",
                               message="Integração com o Xano não configurada no servidor.", local=local)
    try:
        remote = client.get_status(current_user.id)
    except XanoError as exc:
        logger.warning("Status do Xano indisponível: %s", exc)
        return ClassroomStatus(configured=True, reachable=False, connected=False, status="unreachable",
                               message="Não foi possível consultar o Xano agora.", local=local)

    connected = remote.get("connected") is True
    status = remote.get("status") if isinstance(remote.get("status"), str) else ("active" if connected else "not_connected")
    email = remote.get("google_email") if isinstance(remote.get("google_email"), str) else None
    try:
        last_sync = parse_xano_datetime(remote.get("last_sync_at"))
    except InvalidItemError:
        last_sync = None
    return ClassroomStatus(configured=True, reachable=True, connected=connected, status=status,
                           google_email=email, last_sync_at=last_sync, local=local)


@router.post("/connect", response_model=ClassroomConnectResponse)
def classroom_connect(
    current_user: User = Depends(get_current_user),
    client: XanoClient = Depends(get_xano_client),
):
    """Obtém do Xano a URL de consentimento do Google. O return_url vem da configuração, nunca do cliente."""
    return_url = settings.APP_BASE_URL.rstrip("/") + "/"
    try:
        return ClassroomConnectResponse(authorization_url=client.start_oauth(current_user.id, return_url))
    except XanoError as exc:
        raise xano_http_error(exc)


@router.delete("/connection")
def classroom_disconnect(
    current_user: User = Depends(get_current_user),
    client: XanoClient = Depends(get_xano_client),
):
    """Desconecta o Google no Xano. Disciplinas e tarefas já importadas permanecem no EduTrack."""
    try:
        client.disconnect(current_user.id)
    except XanoError as exc:
        raise xano_http_error(exc)
    return {"disconnected": True, "message": "Conexão removida. Os dados já importados foram mantidos."}


@router.post("/sync", response_model=ClassroomSyncResponse)
def classroom_sync(
    payload: Optional[ClassroomSyncRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    client: XanoClient = Depends(get_xano_client),
):
    """Sincronização sob demanda: (opcional) Xano busca no Google; depois o FastAPI importa para o SQLite."""
    refresh = True if payload is None else payload.refresh
    lock = _lock_for(current_user.id)
    if not lock.acquire(blocking=False):
        raise HTTPException(409, "Já existe uma sincronização em andamento para este usuário.")
    try:
        remote: Optional[Dict[str, Any]] = None
        try:
            if refresh:
                raw = client.start_sync(current_user.id)
                remote = {k: raw.get(k) for k in _REMOTE_SUMMARY_KEYS if k in raw}
            result = sync_user_from_xano(db, current_user.id, client)
        except XanoError as exc:
            raise xano_http_error(exc)
        except ClassroomSyncError as exc:
            logger.error("Falha ao gravar sincronização do usuário %s: %s", current_user.id, exc)
            raise HTTPException(500, "Falha ao gravar os dados importados. Nada foi alterado.")
        return ClassroomSyncResponse(remote=remote, result=result.as_dict())
    finally:
        lock.release()


@router.get("/courses", response_model=List[ClassroomCourseOut])
def classroom_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cursos importados do Classroom (lidos do SQLite, sem chamar o Xano)."""
    subjects = (
        db.query(Subject)
        .filter(Subject.user_id == current_user.id, Subject.source == SOURCE_CLASSROOM)
        .order_by(Subject.name.asc())
        .all()
    )
    totals: Dict[int, int] = {}
    pending: Dict[int, int] = {}
    for subject_id, status in (
        db.query(AcademicTask.subject_id, AcademicTask.status)
        .filter(AcademicTask.user_id == current_user.id, AcademicTask.source == SOURCE_CLASSROOM)
        .all()
    ):
        totals[subject_id] = totals.get(subject_id, 0) + 1
        if status != "completed":
            pending[subject_id] = pending.get(subject_id, 0) + 1
    return [
        ClassroomCourseOut(
            id=s.id, classroom_course_id=s.classroom_course_id, name=s.name, description=s.description,
            link=s.classroom_link, tasks_total=totals.get(s.id, 0), tasks_pending=pending.get(s.id, 0),
            synced_at=s.classroom_synced_at,
        )
        for s in subjects
    ]


@router.get("/courses/remote", response_model=List[RemoteCourseOut])
def classroom_remote_courses(
    current_user: User = Depends(get_current_user),
    client: XanoClient = Depends(get_xano_client),
):
    """Cursos como o Xano os conhece (inclui os ainda não importados)."""
    try:
        items = client.get_courses(current_user.id)
    except XanoError as exc:
        raise xano_http_error(exc)
    out: List[RemoteCourseOut] = []
    for item in items:
        gid = item.get("google_course_id")
        if gid is None or str(gid).strip() == "":
            continue
        out.append(RemoteCourseOut(
            google_course_id=str(gid),
            name=item.get("name") if isinstance(item.get("name"), str) else None,
            section=item.get("section") if isinstance(item.get("section"), str) else None,
            course_state=item.get("course_state") if isinstance(item.get("course_state"), str) else None,
            selected=item.get("selected") if isinstance(item.get("selected"), bool) else None,
            is_active=item.get("is_active") if isinstance(item.get("is_active"), bool) else None,
        ))
    return out


@router.get("/tasks", response_model=List[ClassroomTaskOut])
def classroom_tasks(
    course_id: Optional[int] = Query(None, description="subjects.id para filtrar por curso"),
    status: Optional[str] = Query(None, description="pending | in_progress | completed"),
    limit: int = Query(200, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atividades importadas do Classroom (lidas do SQLite), prazo mais próximo primeiro."""
    query = (
        db.query(AcademicTask, Subject.name)
        .join(Subject, Subject.id == AcademicTask.subject_id)
        .filter(AcademicTask.user_id == current_user.id, AcademicTask.source == SOURCE_CLASSROOM)
    )
    if course_id is not None:
        query = query.filter(AcademicTask.subject_id == course_id)
    if status:
        query = query.filter(AcademicTask.status == status)
    rows = query.all()
    rows.sort(key=lambda r: (r[0].due_date is None, r[0].due_date or 0, r[0].title))
    return [
        ClassroomTaskOut(
            id=t.id, subject_id=t.subject_id, course_name=course_name,
            classroom_coursework_id=t.classroom_coursework_id, title=t.title, description=t.description,
            due_date=t.due_date, max_points=t.max_points, link=t.classroom_link, status=t.status,
            submission_state=t.classroom_submission_state, synced_at=t.classroom_synced_at,
        )
        for t, course_name in rows[:limit]
    ]
