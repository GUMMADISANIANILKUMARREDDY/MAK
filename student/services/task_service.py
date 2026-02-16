from typing import Optional
from datetime import date, datetime
from config.supabase_client import supabase


def create_task(
    moduleid: str,
    title: str,
    description: Optional[str],
    task_type: str,
    created_by: str,
    priority: str,
    story_points: int,
    due_date: Optional[date],
) -> dict:
    """Mentor: Create task in module."""
    result = supabase.table("tasks").insert(
        {
            "moduleid": moduleid,
            "title": title,
            "description": description,
            "task_type": task_type,
            "created_by": created_by,
            "priority": priority,
            "story_points": story_points,
            "status": "backlog",
            "due_date": due_date.isoformat() if due_date else None,
        }
    ).execute()

    if not result.data:
        return {"success": False, "message": "Failed to create task"}
    return {"success": True, "message": "Task created", "task": result.data[0]}


def get_module_tasks(moduleid: str, status: Optional[str] = None, page: int = 1, limit: int = 50) -> dict:
    """Get all tasks in a module."""
    query = supabase.table("tasks").select("*").eq("moduleid", moduleid)
    if status:
        query = query.eq("status", status)

    offset = (page - 1) * limit
    result = query.range(offset, offset + limit - 1).order("created_at", desc=True).execute()
    return {"success": True, "tasks": result.data or [], "page": page, "limit": limit}


def get_task_by_id(taskid: str) -> dict:
    """Get single task."""
    result = supabase.table("tasks").select("*").eq("taskid", taskid).execute()
    if not result.data:
        return {"success": False, "message": "Task not found"}
    return {"success": True, "task": result.data[0]}


def update_task(taskid: str, updates: dict) -> dict:
    """Mentor: Update task."""
    if not updates:
        return {"success": False, "message": "No updates provided"}

    updates = {k: v for k, v in updates.items() if v is not None}
    result = supabase.table("tasks").update(updates).eq("taskid", taskid).execute()

    if not result.data:
        return {"success": False, "message": "Task not found"}
    return {"success": True, "message": "Task updated", "task": result.data[0]}


def delete_task(taskid: str) -> dict:
    """Mentor: Delete task. Cascades: delete all task_assignments for this task, then the task."""
    supabase.table("task_assignments").delete().eq("taskid", taskid).execute()
    supabase.table("tasks").delete().eq("taskid", taskid).execute()
    return {"success": True, "message": "Task deleted"}


def assign_task_to_student(taskid: str, student_userid: str, assigned_by: str) -> dict:
    """Mentor: Assign task to student."""
    user_check = supabase.table("users").select("role").eq("userid", student_userid).execute()
    if not user_check.data or user_check.data[0].get("role") != "student":
        return {"success": False, "message": "Invalid student"}

    # Check if already assigned
    existing = supabase.table("task_assignments").select("*").eq("taskid", taskid).eq("student_userid", student_userid).execute()
    if existing.data:
        return {"success": False, "message": "Task already assigned to this student"}

    result = supabase.table("task_assignments").insert(
        {"taskid": taskid, "student_userid": student_userid, "assigned_by": assigned_by, "status": "assigned"}
    ).execute()

    if not result.data:
        return {"success": False, "message": "Failed to assign task"}
    return {"success": True, "message": "Task assigned to student", "assignment": result.data[0]}


def assign_task_bulk(taskid: str, student_userids: list, assigned_by: str) -> dict:
    """Mentor: Assign task to multiple students."""
    created = []
    errors = []

    for student_userid in student_userids:
        result = assign_task_to_student(taskid, student_userid, assigned_by)
        if result.get("success"):
            created.append(result.get("assignment"))
        else:
            errors.append({"student_userid": student_userid, "error": result.get("message")})

    return {"success": True, "assigned": len(created), "errors": errors}


def get_task_assignments(taskid: str) -> dict:
    """Get all assignments for a task."""
    result = supabase.table("task_assignments").select("*").eq("taskid", taskid).execute()
    return {"success": True, "assignments": result.data or []}


def get_student_tasks(student_userid: str, status: Optional[str] = None) -> dict:
    """Student: Get all tasks assigned to me."""
    query = supabase.table("task_assignments").select("*, tasks(*)").eq("student_userid", student_userid)
    if status:
        query = query.eq("status", status)

    result = query.order("assigned_at", desc=True).execute()
    return {"success": True, "tasks": result.data or []}


def update_task_assignment_status(assignment_id: str, status: str, notes: Optional[str] = None) -> dict:
    """Student: Update task assignment status."""
    updates = {"status": status}
    
    if status == "in_progress" and notes is None:
        updates["started_at"] = datetime.utcnow().isoformat()
    
    if status == "completed":
        updates["completed_at"] = datetime.utcnow().isoformat()
    
    if notes:
        updates["notes"] = notes

    result = supabase.table("task_assignments").update(updates).eq("assignment_id", assignment_id).execute()

    if not result.data:
        return {"success": False, "message": "Assignment not found"}
    return {"success": True, "message": "Status updated", "assignment": result.data[0]}


def submit_task(assignment_id: str, notes: Optional[str]) -> dict:
    """Student: Submit task."""
    updates = {"status": "review", "notes": notes, "completed_at": datetime.utcnow().isoformat()}
    result = supabase.table("task_assignments").update(updates).eq("assignment_id", assignment_id).execute()

    if not result.data:
        return {"success": False, "message": "Assignment not found"}
    return {"success": True, "message": "Task submitted for review", "assignment": result.data[0]}
