import uuid
from typing import Optional
from datetime import date, datetime
from config.supabase_client import supabase
from config.settings import settings


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


def get_module_tasks(
    moduleid: str,
    status: Optional[str] = None,
    search: Optional[str] = None,
    priority: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort: str = "created_at",
    order: str = "desc",
    page: int = 1,
    limit: int = 50,
) -> dict:
    """Get all tasks in a module with filters and sort."""
    query = supabase.table("tasks").select("*").eq("moduleid", moduleid)
    if status:
        query = query.eq("status", status)
    if search and search.strip():
        q = search.strip()
        query = query.or_(f"title.ilike.%{q}%,description.ilike.%{q}%")
    if priority:
        query = query.eq("priority", priority)
    if date_from:
        query = query.gte("due_date", date_from.isoformat())
    if date_to:
        query = query.lte("due_date", date_to.isoformat())
    sort_col = sort if sort in ("created_at", "updated_at", "due_date", "title", "priority") else "created_at"
    desc = order.lower() == "desc"
    offset = (page - 1) * limit
    result = query.range(offset, offset + limit - 1).order(sort_col, desc=desc).execute()
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
    assignment = result.data[0]
    try:
        task_row = supabase.table("tasks").select("title").eq("taskid", taskid).limit(1).execute()
        task_title = task_row.data[0]["title"] if task_row.data else "Task"
        from services.notification_service import notify_task_assigned
        notify_task_assigned(student_userid, task_title, link="")
    except Exception:
        pass
    return {"success": True, "message": "Task assigned to student", "assignment": assignment}


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


def review_task(
    assignment_id: str,
    reviewed_by: str,
    result: str,
    feedback: Optional[str] = None,
    score: Optional[int] = None,
) -> dict:
    """Mentor: Review task assignment (approve/reject), set feedback and optional score."""
    if result not in ("approved", "rejected"):
        return {"success": False, "message": "result must be 'approved' or 'rejected'"}
    assignment_row = supabase.table("task_assignments").select("*").eq("assignment_id", assignment_id).limit(1).execute()
    if not assignment_row.data or len(assignment_row.data) == 0:
        return {"success": False, "message": "Assignment not found"}
    assignment = assignment_row.data[0]
    if assignment.get("status") != "review":
        return {"success": False, "message": "Task is not in review status"}
    updates = {
        "status": result,
        "review_result": result,
        "review_feedback": feedback or "",
        "review_score": score,
        "reviewed_at": datetime.utcnow().isoformat(),
        "reviewed_by": reviewed_by,
    }
    result_up = supabase.table("task_assignments").update(updates).eq("assignment_id", assignment_id).execute()
    if not result_up.data:
        return {"success": False, "message": "Update failed"}
    student_userid = assignment.get("student_userid")
    task_row = supabase.table("tasks").select("title").eq("taskid", assignment["taskid"]).limit(1).execute()
    task_title = task_row.data[0]["title"] if task_row.data else "Task"
    try:
        from services.notification_service import notify_task_reviewed
        notify_task_reviewed(student_userid, task_title, result == "approved", feedback or "", link="")
    except Exception:
        pass
    return {"success": True, "message": f"Task {result}", "assignment": result_up.data[0]}


def get_student_tasks(
    student_userid: str,
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "assigned_at",
    order: str = "desc",
    page: int = 1,
    limit: int = 50,
) -> dict:
    """Student: Get all tasks assigned to me with filters and sort."""
    query = supabase.table("task_assignments").select("*, tasks(*)").eq("student_userid", student_userid)
    if status:
        query = query.eq("status", status)
    if search and search.strip():
        q = search.strip()
        task_ids_r = supabase.table("tasks").select("taskid").or_(f"title.ilike.%{q}%,description.ilike.%{q}%").execute()
        task_ids = [r["taskid"] for r in (task_ids_r.data or [])]
        if task_ids:
            query = query.in_("taskid", task_ids)
        else:
            query = query.eq("taskid", "00000000-0000-0000-0000-000000000000")
    sort_col = sort if sort in ("assigned_at", "completed_at", "status") else "assigned_at"
    desc = order.lower() == "desc"
    offset = (page - 1) * limit
    result = query.order(sort_col, desc=desc).range(offset, offset + limit - 1).execute()
    return {"success": True, "tasks": result.data or [], "page": page, "limit": limit}


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


def submit_task(assignment_id: str, notes: Optional[str], submission_file_url: Optional[str] = None) -> dict:
    """Student: Submit task with optional notes and attachment URL (from file upload)."""
    updates = {"status": "review", "notes": notes, "completed_at": datetime.utcnow().isoformat()}
    if submission_file_url is not None:
        updates["submission_file_url"] = submission_file_url
    result = supabase.table("task_assignments").update(updates).eq("assignment_id", assignment_id).execute()

    if not result.data:
        return {"success": False, "message": "Assignment not found"}
    assignment = result.data[0]
    try:
        task_row = supabase.table("tasks").select("title, created_by").eq("taskid", assignment["taskid"]).limit(1).execute()
        if task_row.data:
            mentor_userid = task_row.data[0].get("created_by")
            task_title = task_row.data[0].get("title", "Task")
            if mentor_userid:
                from services.notification_service import notify_task_status_changed
                notify_task_status_changed(mentor_userid, task_title, "submitted for review", link="")
    except Exception:
        pass
    return {"success": True, "message": "Task submitted for review", "assignment": assignment}


def upload_submission_file(assignment_id: str, filename: str, file_bytes: bytes, content_type: Optional[str] = None) -> Optional[str]:
    """Upload file to Supabase Storage and return public URL. Returns None on failure."""
    bucket = settings.STORAGE_BUCKET_SUBMISSIONS
    safe_name = (filename or "file").split("/")[-1][:100]
    path = f"{assignment_id}/{uuid.uuid4().hex}_{safe_name}"
    opts = {}
    if content_type:
        opts["content_type"] = content_type
    try:
        supabase.storage.from_(bucket).upload(path, file_bytes, opts)
        # Get public URL (if bucket is public) or signed URL
        public = supabase.storage.from_(bucket).get_public_url(path)
        return public
    except Exception:
        return None
