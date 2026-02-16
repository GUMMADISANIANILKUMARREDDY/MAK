import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings
from utils.email_templates import (
    get_registration_otp_subject,
    get_registration_otp_plain,
    get_registration_otp_html,
)


def send_otp_email(to_email: str, otp: str) -> bool:
    """Send OTP email via SMTP at registration. Uses company-style template from utils (welcome as student + OTP). Returns True on success."""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email
        msg["Subject"] = get_registration_otp_subject()

        plain_body = get_registration_otp_plain(
            to_email, otp, settings.OTP_EXPIRE_MINUTES
        )
        html_body = get_registration_otp_html(
            to_email, otp, settings.OTP_EXPIRE_MINUTES
        )

        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception:
        return False
