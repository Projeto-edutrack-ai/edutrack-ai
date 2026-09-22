from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class SubjectBase(BaseModel):
    name: str = Field(..., example="Estrutura de Dados")
    professor: Optional[str] = Field(None, example="Prof. Dr. Silva")
    workload_hours: float = Field(60.0, ge=1.0, example=60.0)
    description: Optional[str] = Field(None, example="Algoritmos e estruturas lineares e não-lineares")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    professor: Optional[str] = None
    workload_hours: Optional[float] = None
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
