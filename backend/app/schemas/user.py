from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    name: str
    email: EmailStr
    course: Optional[str] = "Ciência da Computação"
    college_year: Optional[str] = "3º Ano / 6º Semestre"
    institution: Optional[str] = "Faculdade de Tecnologia"
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    course: Optional[str] = "Ciência da Computação"
    college_year: Optional[str] = "3º Ano / 6º Semestre"
    institution: Optional[str] = "Faculdade de Tecnologia"
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    course: Optional[str] = None
    college_year: Optional[str] = None
    institution: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None
