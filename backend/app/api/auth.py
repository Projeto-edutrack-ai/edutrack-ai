import hashlib
import html as html_lib
import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserLogin, UserResponse, Token, ForgotPasswordRequest, ResetPasswordRequest
from app.api.deps import get_current_user
from app.core.config import settings
from app.models.password_reset import PasswordResetToken
from app.services.email_service import send_email, EmailDeliveryError
from app.services.xano_crud import sync_aluno

log = logging.getLogger("edutrack.auth")
MIN_PASSWORD_LENGTH = 6

router = APIRouter(prefix="/auth", tags=["Autenticação & Perfil"])


def _authenticate_user(email: str, password: str, db: Session) -> User:
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos."
        )
    return user


def _token_for_user(user: User, xano_sync: dict = None) -> Token:
    access_token = create_access_token(subject=user.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        xano_sync=xano_sync,
    )


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

    # Cria o aluno também no Xano. Falha do Xano não impede o cadastro: o resultado vai na resposta.
    return _token_for_user(new_user, xano_sync=sync_aluno(new_user))

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """Autentica o estudante e retorna o token JWT (e garante o aluno no Xano)."""
    user = _authenticate_user(user_in.email, user_in.password, db)
    return _token_for_user(user, xano_sync=sync_aluno(user))

@router.post("/xano-sync")
def xano_sync_endpoint(current_user: User = Depends(get_current_user)):
    """Força a sincronização do aluno logado com a tabela `alunos` do Xano."""
    return sync_aluno(current_user)


@router.post("/token", response_model=Token)
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Autentica pelo fluxo OAuth2 Password usado pelo botão Authorize do Swagger."""
    return _token_for_user(_authenticate_user(form_data.username, form_data.password, db))

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Envia por e-mail um link de redefinição (token de uso único). A resposta é sempre a mesma,
    exista o e-mail ou não, para não revelar quais contas existem."""
    generic = {
        "message": "Se este e-mail estiver cadastrado, enviamos um link para redefinir a senha. Verifique sua caixa de entrada e o spam.",
        "status": "success",
        "email_backend": settings.EMAIL_BACKEND.lower(),
    }
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user:
        return generic

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for old in db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id, PasswordResetToken.used_at.is_(None)
    ).all():
        old.used_at = now  # só o link mais recente vale
    raw_token = secrets.token_urlsafe(32)
    db.add(PasswordResetToken(
        user_id=user.id,
        token_hash=_hash_token(raw_token),
        expires_at=now + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_MINUTES),
    ))
    db.commit()

    link = f"{settings.APP_BASE_URL.rstrip('/')}/?reset_token={raw_token}"
    minutes = settings.PASSWORD_RESET_TOKEN_MINUTES
    text = (
        f"Olá, {user.name}!\n\n"
        "Recebemos um pedido para redefinir a senha da sua conta no EduTrack AI.\n"
        f"Abra o link abaixo (válido por {minutes} minutos, uso único):\n\n{link}\n\n"
        "Se você não pediu isso, ignore este e-mail; sua senha continua a mesma."
    )
    html_body = (
        f"<p>Olá, <b>{html_lib.escape(user.name)}</b>!</p>"
        "<p>Recebemos um pedido para redefinir a senha da sua conta no EduTrack AI.</p>"
        f'<p><a href="{link}">Redefinir minha senha</a> (válido por {minutes} minutos, uso único).</p>'
        "<p>Se você não pediu isso, ignore este e-mail; sua senha continua a mesma.</p>"
    )
    try:
        send_email(user.email, "EduTrack AI - Redefinição de senha", text, html_body)
    except EmailDeliveryError as exc:
        log.error("Falha ao enviar e-mail de recuperação para %s: %s", user.email, exc)
    return generic


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Redefine a senha usando o token recebido por e-mail (uso único, com validade)."""
    new_password = req.new_password.strip()
    if len(new_password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A nova senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres."
        )
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == _hash_token(req.token.strip())
    ).first()
    if not record or record.used_at is not None or record.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Link de redefinição inválido ou expirado. Solicite um novo."
        )
    user = db.query(User).filter(User.id == record.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Link de redefinição inválido ou expirado. Solicite um novo.")

    user.password_hash = get_password_hash(new_password)
    record.used_at = now
    db.commit()
    return {"message": "Senha atualizada com sucesso. Entre com a nova senha.", "status": "success"}

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
            if current_user.xano_aluno_id is not None:
                raise HTTPException(status_code=409, detail="Conta vinculada ao Xano: alteração de e-mail exige revisão do vínculo.")
            current_user.email = new_email

    if "password" in update_data and update_data["password"]:
        current_user.password_hash = get_password_hash(update_data["password"])

    for field in ["name", "course", "college_year", "institution", "bio", "avatar_url"]:
        if field in update_data:
            setattr(current_user, field, update_data[field])

    db.commit()
    db.refresh(current_user)
    return current_user
