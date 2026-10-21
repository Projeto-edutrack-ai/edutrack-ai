"""Schemas de resposta das rotas /api/classroom (formato consumido pelo frontend)."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ClassroomLocalSummary(BaseModel):
    courses: int = 0
    tasks: int = 0
    last_synced_at: Optional[datetime] = None


class ClassroomStatus(BaseModel):
    configured: bool                       # XANO_BASE_URL/XANO_API_KEY definidos neste servidor
    reachable: bool                        # o Xano respondeu
    connected: bool                        # o usuário autorizou o Google no Xano
    status: str = "unknown"                # not_configured | unreachable | not_connected | active | needs_reauth | revoked | error
    google_email: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    message: Optional[str] = None
    local: ClassroomLocalSummary = ClassroomLocalSummary()


class ClassroomConnectResponse(BaseModel):
    authorization_url: str


class ClassroomSyncRequest(BaseModel):
    # True: manda o Xano buscar no Google e depois importa. False: só reimporta o que o Xano já tem.
    refresh: bool = True


class ClassroomSyncResponse(BaseModel):
    remote: Optional[Dict[str, Any]] = None   # resumo devolvido pelo Xano (status, contagens, erros)
    result: Dict[str, Any]                    # contagens da projeção para o SQLite


class ClassroomCourseOut(BaseModel):
    id: int                                   # subjects.id
    classroom_course_id: str
    name: str
    description: Optional[str] = None
    link: Optional[str] = None
    tasks_total: int = 0
    tasks_pending: int = 0
    synced_at: Optional[datetime] = None


class ClassroomTaskOut(BaseModel):
    id: int                                   # academic_tasks.id
    subject_id: int
    course_name: Optional[str] = None
    classroom_coursework_id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    max_points: Optional[float] = None
    link: Optional[str] = None
    status: str
    submission_state: Optional[str] = None
    synced_at: Optional[datetime] = None


class RemoteCourseOut(BaseModel):
    google_course_id: str
    name: Optional[str] = None
    section: Optional[str] = None
    course_state: Optional[str] = None
    selected: Optional[bool] = None
    is_active: Optional[bool] = None
