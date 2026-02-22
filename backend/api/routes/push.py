"""Web Push: subscribe and VAPID public key."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from config.settings import settings
from api.dependencies import get_current_user
from services.push_service import save_subscription, is_push_available

router = APIRouter(prefix="/push", tags=["Push"])


class SubscribeRequest(BaseModel):
    endpoint: str
    keys: dict  # { p256dh: str, auth: str }


@router.get("/vapid-public")
def get_vapid_public():
    """Return the VAPID public key for the frontend to subscribe."""
    if not is_push_available():
        raise HTTPException(status_code=503, detail="Web Push is not configured")
    return {"vapid_public_key": settings.VAPID_PUBLIC_KEY}


@router.post("/subscribe")
def subscribe(
    data: SubscribeRequest,
    current_user: dict = Depends(get_current_user),
):
    """Store the push subscription for the current user."""
    if not is_push_available():
        raise HTTPException(status_code=503, detail="Web Push is not configured")
    ok = save_subscription(
        current_user["sub"],
        {"endpoint": data.endpoint, "keys": data.keys},
        user_agent="",  # Optional: pass from request header
    )
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid subscription data")
    return {"success": True}
