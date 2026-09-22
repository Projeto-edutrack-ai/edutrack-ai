from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class AcademicTaskBase(BaseModel):
    subject_id: int
    title: str = Field(..., example="Implementar Árvore Binária")
    description: Optional[str] = Field(None, example="Exercício 3 do capítulo 4")
    due_date: Optional[datetime] = None
    status: str = Field("pending", example="pending")  # pending, in_progress, completed
    estimated_time_minutes: float = Field(60.0, ge=0.0, example=90.0)
    actual_time_minutes: float = Field(0.0, ge=0.0, example=45.0)

class AcademicTaskCreate(AcademicTaskBase):
    pass

class AcademicTaskUpdate(BaseModel):
    subject_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    estimated_time_minutes: Optional[float] = None
    actual_time_minutes: Optional[float] = None

class AddStudyTimeRequest(BaseModel):
    additional_minutes: float = Field(..., gt=0.0, example=25.0)
    new_status: Optional[str] = None  # opcionalmente muda para in_progress ou completed

class AcademicTaskResponse(AcademicTaskBase):
    id: int
    user_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    subject_name: Optional[str] = None

    class Config:
        from_attributes = True
