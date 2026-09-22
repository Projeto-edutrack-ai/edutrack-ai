from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # Novos campos de perfil acadêmico do estudante
    avatar_url = Column(Text, nullable=True)  # URL ou Data URI em Base64
    course = Column(String, nullable=True, default="Ciência da Computação")  # Curso
    college_year = Column(String, nullable=True, default="3º Ano / 6º Semestre")  # Ano/Semestre
    institution = Column(String, nullable=True, default="Faculdade de Tecnologia")  # Faculdade/Universidade
    bio = Column(String, nullable=True)  # Bio / Objetivos de estudo
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    subjects = relationship("Subject", back_populates="user", cascade="all, delete-orphan")
    academic_tasks = relationship("AcademicTask", back_populates="user", cascade="all, delete-orphan")
