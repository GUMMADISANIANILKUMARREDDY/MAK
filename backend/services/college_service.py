"""Multi-tenant colleges: list, create. Scoping for super_admin vs clgadmin."""
from typing import Optional
from config.supabase_client import supabase


def get_all_colleges() -> dict:
    """List all colleges (admin/super_admin)."""
    r = supabase.table("colleges").select("*").order("name").execute()
    return {"success": True, "colleges": r.data or []}


def create_college(name: str, code: Optional[str] = None) -> dict:
    """Create college (super_admin only in full impl)."""
    try:
        ins = supabase.table("colleges").insert({"name": name, "code": code}).execute()
        if ins.data:
            return {"success": True, "college": ins.data[0]}
    except Exception as e:
        return {"success": False, "message": str(e)}
    return {"success": False, "message": "Failed to create"}


def get_user_collegeid(userid: str) -> Optional[str]:
    """Return collegeid for user if set."""
    r = supabase.table("users").select("collegeid").eq("userid", userid).execute()
    if r.data and r.data[0].get("collegeid"):
        return str(r.data[0]["collegeid"])
    return None


def scope_query_by_college(query, table: str, collegeid: Optional[str], role: str):
    """If role is not super_admin and collegeid is set, filter by collegeid. Modifies query in place if applicable."""
    if role == "super_admin":
        return
    if collegeid and hasattr(query, "eq"):
        # Tables that have collegeid: users, projects
        if table in ("users", "projects"):
            query = query.eq("collegeid", collegeid)
    return query
