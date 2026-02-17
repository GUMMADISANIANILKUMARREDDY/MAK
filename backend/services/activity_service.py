"""Activity logs / audit trail: log create/update/delete for key entities."""
from typing import Optional, Any
from config.supabase_client import supabase


def log_activity(
    userid: Optional[str],
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    payload: Optional[dict] = None,
    ip: Optional[str] = None,
) -> None:
    """Insert one activity log. Swallow errors so logging never breaks the request."""
    try:
        supabase.table("activity_logs").insert({
            "userid": userid,
            "action": action,
            "entity_type": entity_type,
            "entity_id": str(entity_id) if entity_id else None,
            "payload": payload,
            "ip": ip,
        }).execute()
    except Exception:
        pass


def get_activity_logs(
    userid: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """Admin: list activity logs with filters."""
    query = supabase.table("activity_logs").select("*", count="exact")
    if userid:
        query = query.eq("userid", userid)
    if entity_type:
        query = query.eq("entity_type", entity_type)
    if entity_id:
        query = query.eq("entity_id", entity_id)
    if date_from:
        query = query.gte("created_at", date_from)
    if date_to:
        query = query.lte("created_at", date_to)
    result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    total = getattr(result, "count", None) or len(result.data or [])
    return {"success": True, "logs": result.data or [], "total": total}
