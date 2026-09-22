from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
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

    # Relacionamentos
    user = relationship("User", back_populates="academic_tasks")
    subject = relationship("Subject", back_populates="academic_tasks")
