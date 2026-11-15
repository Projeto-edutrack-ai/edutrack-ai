from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator, field_validator

class AcademicTaskBase(BaseModel):
    @field_validator("title")
    @classmethod
    def nonblank(cls, value):
        value=value.strip()
        if not value:raise ValueError("Texto obrigatório")
        return value

    subject_id: int
    title: str = Field(..., min_length=1, max_length=500, example="Implementar Árvore Binária")
    description: Optional[str] = Field(None, example="Exercício 3 do capítulo 4")
    due_date: Optional[datetime] = None
    status: Literal["pending", "in_progress", "completed"] = "pending"  # pending, in_progress, completed
    estimated_time_minutes: float = Field(60.0, ge=0.0, example=90.0)
    actual_time_minutes: float = Field(0.0, ge=0.0, example=45.0)

class AcademicTaskCreate(AcademicTaskBase):
    pass

class AcademicTaskUpdate(BaseModel):
    @field_validator("title")
    @classmethod
    def nonblank(cls, value):
        if value is not None and not value.strip():raise ValueError("Texto obrigatório")
        return value.strip() if value else value

    @model_validator(mode="after")
    def validate_required_fields(self):
        return _check_required_updates(self)

    subject_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[Literal["pending", "in_progress", "completed"]] = None
    estimated_time_minutes: Optional[float] = Field(None, ge=0)
    actual_time_minutes: Optional[float] = Field(None, ge=0)

class AddStudyTimeRequest(BaseModel):
    additional_minutes: float = Field(..., gt=0.0, example=25.0)
    new_status: Optional[Literal["pending", "in_progress", "completed"]] = None  # opcionalmente muda para in_progress ou completed

class AcademicTaskResponse(AcademicTaskBase):
    id: int
    user_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    subject_name: Optional[str] = None

    class Config:
        from_attributes = True


# PATCH allows explicit null only for nullable database fields.
def _check_required_updates(self):
    for field in self.model_fields_set:
        if field not in {"description", "due_date"} and getattr(self, field) is None:
            raise ValueError(f"{field} cannot be null")
    return self
