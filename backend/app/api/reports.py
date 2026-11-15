from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.services.pdf_generator import PDFReportGenerator
from app.api.deps import get_current_user
from app.services.xano_crud import require_mirror, academic_source_scope

router = APIRouter(prefix="/reports", tags=["Relatórios"])

@router.post("/generate")
@router.get("/weekly-pdf")
def download_weekly_pdf(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gera e faz o download do relatório acadêmico semanal em formato PDF."""
    require_mirror(db, current_user)
    with academic_source_scope(db):
        pdf_buffer = PDFReportGenerator.generate_weekly_report(db, current_user)
    filename = "EduTrack_Relatorio.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
