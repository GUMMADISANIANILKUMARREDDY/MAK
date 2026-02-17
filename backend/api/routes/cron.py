"""Cron or scheduled job endpoints. Use CRON_SECRET in production."""
from fastapi import APIRouter, HTTPException, Header
from config.settings import settings
from services.deadline_service import check_all_deadlines

router = APIRouter(prefix="/cron", tags=["Cron"])


@router.get("/deadline-approaching")
def cron_deadline_approaching(x_cron_secret: str = Header(None, alias="X-Cron-Secret")):
    """Call from cron to send 'deadline approaching' notifications to all students. Requires X-Cron-Secret header if CRON_SECRET is set."""
    if settings.CRON_SECRET and x_cron_secret != settings.CRON_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    return check_all_deadlines()
