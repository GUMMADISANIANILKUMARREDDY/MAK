"""Role permissions: check and list."""
from typing import List
from config.supabase_client import supabase


def get_role_permissions(role: str) -> dict:
    """List permissions for a role."""
    r = supabase.table("role_permissions").select("*").eq("role", role).execute()
    return {"success": True, "permissions": r.data or []}


def get_all_permissions() -> dict:
    """List all role-permission rows (admin)."""
    r = supabase.table("role_permissions").select("*").execute()
    return {"success": True, "permissions": r.data or []}


def set_permission(role: str, resource: str, action: str, grant: bool) -> dict:
    """Grant or revoke permission. If grant, insert; else delete."""
    if grant:
        try:
            supabase.table("role_permissions").insert({"role": role, "resource": resource, "action": action}).execute()
            return {"success": True, "message": "Granted"}
        except Exception:
            return {"success": False, "message": "Already exists or error"}
    else:
        supabase.table("role_permissions").delete().eq("role", role).eq("resource", resource).eq("action", action).execute()
        return {"success": True, "message": "Revoked"}


def has_permission(role: str, resource: str, action: str) -> bool:
    """Check if role has permission. If no row exists, fallback to default (admin has all)."""
    r = supabase.table("role_permissions").select("id").eq("role", role).eq("resource", resource).eq("action", action).execute()
    if r.data:
        return True
    # Default: admin and super_admin have all
    if role in ("admin", "super_admin"):
        return True
    return False
