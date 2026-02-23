"""Cron or scheduled job endpoints. Use CRON_SECRET in production."""
from fastapi import APIRouter, HTTPException, Header
from config.settings import settings
from services.deadline_service import check_all_deadlines
from services.notification_service import process_pending_chat_emails

router = APIRouter(prefix="/cron", tags=["Cron"])


def _check_cron_secret(x_cron_secret: str | None) -> None:
    if settings.CRON_SECRET and x_cron_secret != settings.CRON_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/deadline-approaching")
def cron_deadline_approaching(x_cron_secret: str = Header(None, alias="X-Cron-Secret")):
    """Call from cron to send 'deadline approaching' notifications to all students. Requires X-Cron-Secret header if CRON_SECRET is set."""
    _check_cron_secret(x_cron_secret)
    return check_all_deadlines()


@router.get("/pending-chat-emails")
def cron_pending_chat_emails(x_cron_secret: str = Header(None, alias="X-Cron-Secret")):
    """Call from cron every 5 min to send emails for chat messages still unread after 5 min. Requires X-Cron-Secret header if CRON_SECRET is set."""
    _check_cron_secret(x_cron_secret)
    return process_pending_chat_emails()
