import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings
from utils.email_templates import (
    get_registration_otp_subject,
    get_registration_otp_plain,
    get_registration_otp_html,
    get_password_reset_otp_plain,
    get_password_reset_otp_subject,
    get_task_assigned_subject,
    get_task_assigned_plain,
    get_task_status_changed_subject,
    get_task_status_changed_plain,
    get_deadline_approaching_subject,
    get_deadline_approaching_plain,
    get_task_reviewed_subject,
    get_task_reviewed_plain,
    get_student_added_to_team_subject,
    get_student_added_to_team_plain,
    get_mentor_assigned_subject,
    get_mentor_assigned_plain,
    get_chat_message_subject,
    get_chat_message_plain,
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


def send_password_reset_email(to_email: str, otp: str) -> bool:
    """Send password reset OTP email. Returns True on success."""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email
        msg["Subject"] = get_password_reset_otp_subject()
        plain_body = get_password_reset_otp_plain(otp, settings.OTP_EXPIRE_MINUTES)
        msg.attach(MIMEText(plain_body, "plain"))
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception:
        return False


def _send_plain_email(to_email: str, subject: str, plain_body: str) -> bool:
    """Send a plain-text email. Returns True on success."""
    if not to_email or not subject:
        return False
    try:
        msg = MIMEText(plain_body, "plain")
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email
        msg["Subject"] = subject
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception:
        return False


def send_task_assigned_email(to_email: str, task_title: str, link: str = "") -> bool:
    return _send_plain_email(to_email, get_task_assigned_subject(), get_task_assigned_plain(task_title, link))


def send_task_status_changed_email(to_email: str, task_title: str, status: str, link: str = "") -> bool:
    return _send_plain_email(
        to_email, get_task_status_changed_subject(), get_task_status_changed_plain(task_title, status, link)
    )


def send_deadline_approaching_email(to_email: str, task_title: str, due_date: str, link: str = "") -> bool:
    return _send_plain_email(
        to_email, get_deadline_approaching_subject(), get_deadline_approaching_plain(task_title, due_date, link)
    )


def send_task_reviewed_email(to_email: str, task_title: str, approved: bool, feedback: str = "", link: str = "") -> bool:
    return _send_plain_email(
        to_email,
        get_task_reviewed_subject(approved),
        get_task_reviewed_plain(task_title, approved, feedback, link),
    )


def send_student_added_to_team_email(to_email: str, team_name: str, link: str = "") -> bool:
    return _send_plain_email(
        to_email, get_student_added_to_team_subject(), get_student_added_to_team_plain(team_name, link)
    )


def send_mentor_assigned_email(to_email: str, module_title: str, link: str = "") -> bool:
    return _send_plain_email(
        to_email, get_mentor_assigned_subject(), get_mentor_assigned_plain(module_title, link)
    )


def send_chat_message_email(to_email: str, sender_username: str, message_preview: str, link: str = "") -> bool:
    return _send_plain_email(
        to_email,
        get_chat_message_subject(sender_username),
        get_chat_message_plain(sender_username, message_preview, link),
    )
