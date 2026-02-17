"""Admin: activity logs / audit trail."""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from services.activity_service import get_activity_logs
from api.dependencies import require_role

router = APIRouter(prefix="/admin", tags=["Admin - Activity Logs"])


@router.get("/activity-logs")
def list_activity_logs(
    userid: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    _=Depends(require_role(["admin"])),
):
    """Admin: List activity logs with filters."""
    offset = (page - 1) * limit
    return get_activity_logs(
        userid=userid,
        entity_type=entity_type,
        entity_id=entity_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
