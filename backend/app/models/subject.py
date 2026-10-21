from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
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

    # Origem Google Classroom (via Xano). Registros locais: source="local" e IDs nulos.
    # workload_hours, professor, start_date e end_date continuam locais.
    source = Column(String, nullable=False, default="local", server_default="local")
    classroom_course_id = Column(String, nullable=True)
    classroom_link = Column(String, nullable=True)
    classroom_synced_at = Column(DateTime, nullable=True)

    # Garante um único registro por usuário + curso do Classroom (NULLs não colidem)
    __table_args__ = (
        Index("uq_subjects_user_classroom_course", "user_id", "classroom_course_id", unique=True),
    )

    # Relacionamentos
    user = relationship("User", back_populates="subjects")
    academic_tasks = relationship("AcademicTask", back_populates="subject", cascade="all, delete-orphan")
