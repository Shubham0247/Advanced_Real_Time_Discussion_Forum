import logging
import smtplib
from email.message import EmailMessage

from backend.services.auth_service.app.core.config import settings


logger = logging.getLogger(__name__)


def send_password_reset_otp_email(to_email: str, otp: str) -> None:
    """Send a password reset OTP email, or log it when SMTP is not configured."""
    
    subject = "Password reset OTP"
    body = (
        "Use this one-time code to reset your password.\n\n"
        f"OTP: {otp}\n"
        f"This code expires in {settings.password_reset_otp_expire_minutes} minutes."
    )

    if not settings.smtp_host:
        logger.warning(
            "SMTP host is not configured. Password reset OTP for %s is %s",
            to_email,
            otp,
        )
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from_email
    message["To"] = to_email
    message.set_content(body)

    if settings.smtp_use_ssl:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_username:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
        return

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)
