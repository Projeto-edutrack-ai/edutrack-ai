from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator, field_validator

class SubjectBase(BaseModel):
    @field_validator("name")
    @classmethod
    def nonblank(cls, value):
        value=value.strip()
        if not value:raise ValueError("Texto obrigatório")
        return value

    name: str = Field(..., min_length=1, max_length=500, example="Estrutura de Dados")
    professor: Optional[str] = Field(None, example="Prof. Dr. Silva")
    workload_hours: float = Field(60.0, ge=1.0, example=60.0)
    description: Optional[str] = Field(None, example="Algoritmos e estruturas lineares e não-lineares")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    @field_validator("name")
    @classmethod
    def nonblank(cls, value):
        if value is not None and not value.strip():raise ValueError("Texto obrigatório")
        return value.strip() if value else value

    @model_validator(mode="after")
    def validate_required_fields(self):
        for field in ("name", "workload_hours"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self

    name: Optional[str] = Field(None, min_length=1, max_length=500)
    professor: Optional[str] = None
    workload_hours: Optional[float] = Field(None, ge=1)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class SubjectResponse(SubjectBase):
    id: int
    user_id: int
    created_at: datetime
    
    # Campos calculados adicionais
    progress_percentage: Optional[float] = 0.0
    total_tasks: Optional[int] = 0
    completed_tasks: Optional[int] = 0
    total_time_spent_minutes: Optional[float] = 0.0

    class Config:
        from_attributes = True
