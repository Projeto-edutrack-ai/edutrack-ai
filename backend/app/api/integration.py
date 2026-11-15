"""Server-to-server Python entry points for Xano search/report orchestration.

A separate shared key is required; never expose it in frontend configuration.
"""
import secrets
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services.xano_crud import require_mirror, academic_source_scope
from app.api.search import SearchResultResponse, search_academic
from app.services.pdf_generator import PDFReportGenerator
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/integration", tags=["Integração servidor Xano"])


def service_user(local_user_id: int = Query(..., gt=0),
                 x_integration_key: str = Header(""), db: Session = Depends(get_db)):
    expected = settings.XANO_PYTHON_BRIDGE_KEY
    if not expected:
        raise HTTPException(503, "Integração de servidor não configurada.")
    if not secrets.compare_digest(x_integration_key, expected):
        raise HTTPException(401, "Credencial de integração inválida.")
    user = db.get(User, local_user_id)
    if not user:
        raise HTTPException(404, "Usuário não encontrado.")
    return user


@router.get("/search", response_model=SearchResultResponse)
def integration_search(q: str = Query("", max_length=200), overdue: bool = False,
                       user: User = Depends(service_user), db: Session = Depends(get_db)):
    require_mirror(db,user,force=True)
    with academic_source_scope(db):
        return search_academic(db, user.id, q.strip(), overdue=overdue)


@router.post("/reports/generate")
def integration_report(user: User = Depends(service_user), db: Session = Depends(get_db)):
    require_mirror(db,user,force=True)
    with academic_source_scope(db):
        data = PDFReportGenerator.generate_weekly_report(db, user)
    return StreamingResponse(data, media_type="application/pdf",
                             headers={"Content-Disposition": 'attachment; filename="EduTrack_Relatorio.pdf"'})
