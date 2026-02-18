from typing import Optional
from datetime import date
from config.supabase_client import supabase
from services.module_service import delete_module


def create_project(title: str, description: Optional[str], created_by: str, start_date: Optional[date], end_date: Optional[date]) -> dict:
    """Admin: Create project."""
    result = supabase.table("projects").insert(
        {
            "title": title,
            "description": description,
            "created_by": created_by,
            "status": "active",
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        }
    ).execute()

    if not result.data:
        return {"success": False, "message": "Failed to create project"}
    return {"success": True, "message": "Project created", "project": result.data[0]}


def get_all_projects(
    status: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort: str = "created_at",
    order: str = "desc",
    page: int = 1,
    limit: int = 20,
) -> dict:
    """Admin: Get all projects with filters and sort."""
    query = supabase.table("projects").select("*", count="exact")
    if status:
        query = query.eq("status", status)
    if search and search.strip():
        q = search.strip()
        query = query.or_(f"title.ilike.%{q}%,description.ilike.%{q}%")
    if date_from:
        query = query.gte("start_date", date_from.isoformat())
    if date_to:
        query = query.lte("start_date", date_to.isoformat())
    sort_col = sort if sort in ("created_at", "updated_at", "start_date", "end_date", "title") else "created_at"
    desc = order.lower() == "desc"
    offset = (page - 1) * limit
    result = query.range(offset, offset + limit - 1).order(sort_col, desc=desc).execute()
    total = getattr(result, "count", None)
    if total is None and result.data is not None:
        total = len(result.data)
    return {"success": True, "projects": result.data or [], "page": page, "limit": limit, "total": total}


def get_project_by_id(projectid: str) -> dict:
    """Get single project."""
    result = supabase.table("projects").select("*").eq("projectid", projectid).execute()
    if not result.data:
        return {"success": False, "message": "Project not found"}
    return {"success": True, "project": result.data[0]}


def update_project(projectid: str, updates: dict) -> dict:
    """Admin: Update project."""
    if not updates:
        return {"success": False, "message": "No updates provided"}

    updates = {k: v for k, v in updates.items() if v is not None}
    result = supabase.table("projects").update(updates).eq("projectid", projectid).execute()

    if not result.data:
        return {"success": False, "message": "Project not found"}
    return {"success": True, "message": "Project updated", "project": result.data[0]}


def delete_project(projectid: str) -> dict:
    """Admin: Delete project. Cascades: delete all modules (and their tasks/assignments) in this project, then project_assignments, then the project."""
    projects_result = supabase.table("projects").select("projectid").eq("projectid", projectid).execute()
    if not projects_result.data:
        return {"success": False, "message": "Project not found"}
    modules_result = supabase.table("modules").select("moduleid").eq("projectid", projectid).execute()
    for module in (modules_result.data or []):
        delete_module(module["moduleid"])
    supabase.table("project_assignments").delete().eq("projectid", projectid).execute()
    supabase.table("projects").delete().eq("projectid", projectid).execute()
    return {"success": True, "message": "Project deleted"}


def assign_project_to_manager(projectid: str, manager_userid: str, assigned_by: str) -> dict:
    """Admin: Assign project to manager."""
    # Check if manager exists and has manager role
    user_check = supabase.table("users").select("role").eq("userid", manager_userid).execute()
    if not user_check.data or user_check.data[0].get("role") != "manager":
        return {"success": False, "message": "Invalid manager"}

    result = supabase.table("project_assignments").insert(
        {"projectid": projectid, "manager_userid": manager_userid, "assigned_by": assigned_by}
    ).execute()

    if not result.data:
        return {"success": False, "message": "Failed to assign project"}
    return {"success": True, "message": "Project assigned to manager", "assignment": result.data[0]}


def get_project_managers(projectid: str) -> dict:
    """Get all managers assigned to a project with username."""
    result = supabase.table("project_assignments").select("*").eq("projectid", projectid).execute()
    assignments = result.data or []
    managers = []
    for a in assignments:
        mid = a.get("manager_userid")
        if mid:
            ur = supabase.table("users").select("userid, username").eq("userid", mid).limit(1).execute()
            u = ur.data[0] if ur.data else {}
            managers.append({"manager_userid": mid, "username": u.get("username", "")})
    return {"success": True, "managers": managers}


def get_manager_projects(manager_userid: str) -> dict:
    """Manager: Get projects assigned to me."""
    assignments = supabase.table("project_assignments").select("projectid").eq("manager_userid", manager_userid).execute()
    
    if not assignments.data:
        return {"success": True, "projects": []}

    project_ids = [a["projectid"] for a in assignments.data]
    projects = supabase.table("projects").select("*").in_("projectid", project_ids).execute()
    
    return {"success": True, "projects": projects.data or []}
