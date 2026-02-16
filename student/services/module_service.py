from typing import Optional
from datetime import date
from config.supabase_client import supabase
from services.task_service import delete_task


def create_module(projectid: str, title: str, description: Optional[str], created_by: str, priority: str, due_date: Optional[date]) -> dict:
    """Manager: Create module in project."""
    result = supabase.table("modules").insert(
        {
            "projectid": projectid,
            "title": title,
            "description": description,
            "created_by": created_by,
            "status": "pending",
            "priority": priority,
            "due_date": due_date.isoformat() if due_date else None,
        }
    ).execute()

    if not result.data:
        return {"success": False, "message": "Failed to create module"}
    return {"success": True, "message": "Module created", "module": result.data[0]}


def get_project_modules(projectid: str, page: int = 1, limit: int = 50) -> dict:
    """Get all modules in a project."""
    offset = (page - 1) * limit
    result = supabase.table("modules").select("*").eq("projectid", projectid).range(offset, offset + limit - 1).order("created_at", desc=True).execute()
    return {"success": True, "modules": result.data or [], "page": page, "limit": limit}


def get_module_by_id(moduleid: str) -> dict:
    """Get single module."""
    result = supabase.table("modules").select("*").eq("moduleid", moduleid).execute()
    if not result.data:
        return {"success": False, "message": "Module not found"}
    return {"success": True, "module": result.data[0]}


def update_module(moduleid: str, updates: dict) -> dict:
    """Manager: Update module."""
    if not updates:
        return {"success": False, "message": "No updates provided"}

    updates = {k: v for k, v in updates.items() if v is not None}
    result = supabase.table("modules").update(updates).eq("moduleid", moduleid).execute()

    if not result.data:
        return {"success": False, "message": "Module not found"}
    return {"success": True, "message": "Module updated", "module": result.data[0]}


def delete_module(moduleid: str) -> dict:
    """Manager: Delete module. Cascades: delete all tasks (and their assignments) in this module, then module_assignments, then the module."""
    modules_result = supabase.table("modules").select("moduleid").eq("moduleid", moduleid).execute()
    if not modules_result.data:
        return {"success": False, "message": "Module not found"}
    tasks_result = supabase.table("tasks").select("taskid").eq("moduleid", moduleid).execute()
    for task in (tasks_result.data or []):
        delete_task(task["taskid"])
    supabase.table("module_assignments").delete().eq("moduleid", moduleid).execute()
    supabase.table("modules").delete().eq("moduleid", moduleid).execute()
    return {"success": True, "message": "Module deleted"}


def assign_module_to_mentor(moduleid: str, mentor_userid: str, assigned_by: str) -> dict:
    """Manager: Assign module to mentor."""
    user_check = supabase.table("users").select("role").eq("userid", mentor_userid).execute()
    if not user_check.data or user_check.data[0].get("role") != "mentor":
        return {"success": False, "message": "Invalid mentor"}

    result = supabase.table("module_assignments").insert(
        {"moduleid": moduleid, "mentor_userid": mentor_userid, "assigned_by": assigned_by}
    ).execute()

    if not result.data:
        return {"success": False, "message": "Failed to assign module"}
    return {"success": True, "message": "Module assigned to mentor", "assignment": result.data[0]}


def get_module_mentors(moduleid: str) -> dict:
    """Get all mentors assigned to a module."""
    result = supabase.table("module_assignments").select("*").eq("moduleid", moduleid).execute()
    return {"success": True, "mentors": result.data or []}


def get_mentor_modules(mentor_userid: str) -> dict:
    """Mentor: Get modules assigned to me."""
    assignments = supabase.table("module_assignments").select("moduleid").eq("mentor_userid", mentor_userid).execute()
    
    if not assignments.data:
        return {"success": True, "modules": []}

    module_ids = [a["moduleid"] for a in assignments.data]
    modules = supabase.table("modules").select("*").in_("moduleid", module_ids).execute()
    
    return {"success": True, "modules": modules.data or []}
