"""Envio de e-mail (recuperação de senha).

EMAIL_BACKEND=smtp    envia de verdade via SMTP (SMTP_HOST/PORT/USER/PASSWORD, TLS ou SSL).
EMAIL_BACKEND=console modo de desenvolvimento: NÃO entrega; registra no log e grava em outbox/.
"""
import logging
import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from app.core.config import settings

log = logging.getLogger("edutrack.email")
OUTBOX_DIR = Path(os.getenv("EMAIL_OUTBOX_DIR") or Path(__file__).resolve().parents[3] / "outbox")


class EmailDeliveryError(Exception):
    """Falha ao entregar o e-mail ao servidor SMTP."""


def build_message(to: str, subject: str, text: str, html: str = "") -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")
    return msg


def send_email(to: str, subject: str, text: str, html: str = "") -> str:
    """Envia a mensagem. Devolve o backend usado ('smtp' ou 'console'). Lança EmailDeliveryError."""
    msg = build_message(to, subject, text, html)
    if settings.EMAIL_BACKEND.lower() == "smtp":
        if not settings.SMTP_HOST:
            raise EmailDeliveryError("EMAIL_BACKEND=smtp mas SMTP_HOST não está configurado")
        try:
            if settings.SMTP_USE_SSL:
                server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15,
                                          context=ssl.create_default_context())
            else:
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15)
            with server:
                if settings.SMTP_USE_TLS and not settings.SMTP_USE_SSL:
                    server.starttls(context=ssl.create_default_context())
                if settings.SMTP_USER:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        except (smtplib.SMTPException, OSError) as exc:
            raise EmailDeliveryError(f"Falha ao enviar e-mail via SMTP: {exc}") from exc
        return "smtp"

    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTBOX_DIR / f"{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.eml"
    path.write_bytes(bytes(msg))
    log.warning("[EMAIL em modo console - NÃO enviado] para=%s assunto=%s arquivo=%s\n%s", to, subject, path, text)
    return "console"
