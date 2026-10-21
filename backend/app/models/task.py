from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class AcademicTask(Base):
    """Modelo canônico para a tabela 'academic_tasks' (Tarefas Acadêmicas)."""
    __tablename__ = "academic_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending", nullable=False)  # pending, in_progress, completed
    
    # Tempo estimado e tempo real (em minutos) para o motor de insights e métricas
    estimated_time_minutes = Column(Float, default=60.0, nullable=False)
    actual_time_minutes = Column(Float, default=0.0, nullable=False)
    
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Origem Google Classroom (via Xano). Registros locais: source="local" e IDs nulos.
    # actual_time_minutes, estimated_time_minutes e status (manual) continuam locais.
    source = Column(String, nullable=False, default="local", server_default="local")
    classroom_coursework_id = Column(String, nullable=True)
    classroom_link = Column(String, nullable=True)
    max_points = Column(Float, nullable=True)
    classroom_submission_state = Column(String, nullable=True)
    classroom_synced_at = Column(DateTime, nullable=True)

    # O courseWork.id do Classroom é único apenas dentro do curso (= subject)
    __table_args__ = (
        Index("uq_tasks_user_subject_coursework", "user_id", "subject_id", "classroom_coursework_id", unique=True),
    )

    # Relacionamentos
    user = relationship("User", back_populates="academic_tasks")
    subject = relationship("Subject", back_populates="academic_tasks")
