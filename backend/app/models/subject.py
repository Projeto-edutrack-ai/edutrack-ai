from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Subject(Base):
    """Modelo canônico para a tabela 'subjects' (Disciplinas)."""
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    professor = Column(String, nullable=True)
    workload_hours = Column(Float, default=60.0, nullable=False)  # Carga horária em horas
    description = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    user = relationship("User", back_populates="subjects")
    academic_tasks = relationship("AcademicTask", back_populates="subject", cascade="all, delete-orphan")
