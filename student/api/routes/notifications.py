from fastapi import APIRouter, Depends, HTTPException, Query
from services.notification_service import (
    get_my_notifications,
    mark_as_read as svc_mark_as_read,
    mark_all_read,
    get_unread_count,
)
from api.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
def list_my_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """Get current user's notifications."""
    return get_my_notifications(current_user["sub"], unread_only=unread_only, limit=limit)


@router.get("/unread-count")
def unread_count(current_user: dict = Depends(get_current_user)):
    """Get unread notification count."""
    count = get_unread_count(current_user["sub"])
    return {"success": True, "count": count}


@router.put("/read-all")
def mark_all_read_endpoint(current_user: dict = Depends(get_current_user)):
    """Mark all my notifications as read. Must be before /{id}/read to avoid path conflict."""
    return mark_all_read(current_user["sub"])


@router.put("/{notification_id}/read")
def mark_one_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    """Mark one notification as read."""
    result = svc_mark_as_read(notification_id, current_user["sub"])
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message"))
    return result
