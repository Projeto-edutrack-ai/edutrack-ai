from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserLogin, UserResponse, Token, ForgotPasswordRequest
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticação & Perfil"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Cadastra um novo estudante."""
    existing_user = db.query(User).filter(User.email == user_in.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este email já está cadastrado no EduTrack AI."
        )
    
    new_user = User(
        name=user_in.name.strip(),
        email=user_in.email.lower().strip(),
        password_hash=get_password_hash(user_in.password),
        course=user_in.course,
        college_year=user_in.college_year,
        institution=user_in.institution,
        bio=user_in.bio,
        avatar_url=user_in.avatar_url
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(subject=new_user.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Autentica o estudante e retorna o token JWT."""
    user = db.query(User).filter(User.email == user_in.email.lower().strip()).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos."
        )
    
    access_token = create_access_token(subject=user.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Simula solicitação de recuperação de senha."""
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user:
        return {"message": "Se o email existir, um link de recuperação foi enviado."}
    
    return {
        "message": f"Instruções de recuperação enviadas com sucesso para {user.email}.",
        "status": "success"
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retorna os dados do estudante autenticado."""
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    profile_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Atualiza o perfil do estudante (nome, foto, curso, ano da faculdade, faculdade, bio)."""
    update_data = profile_in.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"]:
        new_email = update_data["email"].lower().strip()
        if new_email != current_user.email:
            existing = db.query(User).filter(User.email == new_email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Este email já está em uso por outro usuário.")
            current_user.email = new_email

    if "password" in update_data and update_data["password"]:
        current_user.password_hash = get_password_hash(update_data["password"])

    for field in ["name", "course", "college_year", "institution", "bio", "avatar_url"]:
        if field in update_data:
            setattr(current_user, field, update_data[field])

    db.commit()
    db.refresh(current_user)
    return current_user
