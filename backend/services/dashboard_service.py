"""Role-based dashboard stats for Overview."""
from config.supabase_client import supabase


def get_admin_stats() -> dict:
    """Total users, students, projects; active vs inactive users."""
    users_r = supabase.table("users").select("userid, active", count="exact").execute()
    total_users = getattr(users_r, "count", None) or (len(users_r.data or []))
    active_users = sum(1 for u in (users_r.data or []) if u.get("active") is True)
    inactive_users = total_users - active_users

    students_r = supabase.table("students").select("userid", count="exact").execute()
    total_students = getattr(students_r, "count", None) or (len(students_r.data or []))

    projects_r = supabase.table("projects").select("projectid", count="exact").execute()
    total_projects = getattr(projects_r, "count", None) or (len(projects_r.data or []))

    return {
        "success": True,
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "total_students": total_students,
        "total_projects": total_projects,
    }


def get_manager_stats(manager_userid: str) -> dict:
    """Modules by status, tasks pending review for manager's projects."""
    # Projects assigned to this manager
    pa = supabase.table("project_assignments").select("projectid").eq("manager_userid", manager_userid).execute()
    project_ids = [r["projectid"] for r in (pa.data or [])]
    if not project_ids:
        return {
            "success": True,
            "modules_by_status": {},
            "tasks_pending_review": 0,
            "total_modules": 0,
        }

    # Modules in these projects
    mods = supabase.table("modules").select("moduleid, status").in_("projectid", project_ids).execute()
    modules_by_status = {}
    total_modules = len(mods.data or [])
    for m in mods.data or []:
        s = m.get("status") or "pending"
        modules_by_status[s] = modules_by_status.get(s, 0) + 1

    module_ids = [m["moduleid"] for m in (mods.data or [])]
    if not module_ids:
        return {
            "success": True,
            "modules_by_status": modules_by_status,
            "tasks_pending_review": 0,
            "total_modules": total_modules,
        }

    # Task assignments with status 'review' for tasks in these modules
    tasks_in_modules = supabase.table("tasks").select("taskid").in_("moduleid", module_ids).execute()
    task_ids = [t["taskid"] for t in (tasks_in_modules.data or [])]
    if not task_ids:
        return {
            "success": True,
            "modules_by_status": modules_by_status,
            "tasks_pending_review": 0,
            "total_modules": total_modules,
        }

    review_r = (
        supabase.table("task_assignments")
        .select("assignment_id", count="exact")
        .in_("taskid", task_ids)
        .eq("status", "review")
        .execute()
    )
    tasks_pending_review = getattr(review_r, "count", None) or (len(review_r.data or []))

    return {
        "success": True,
        "modules_by_status": modules_by_status,
        "tasks_pending_review": tasks_pending_review,
        "total_modules": total_modules,
    }


def get_mentor_stats(mentor_userid: str) -> dict:
    """Tasks pending review (my modules), teams count."""
    # Modules assigned to this mentor
    ma = supabase.table("module_assignments").select("moduleid").eq("mentor_userid", mentor_userid).execute()
    module_ids = [r["moduleid"] for r in (ma.data or [])]
    tasks_pending_review = 0
    if module_ids:
        tasks_in_modules = supabase.table("tasks").select("taskid").in_("moduleid", module_ids).execute()
        task_ids = [t["taskid"] for t in (tasks_in_modules.data or [])]
        if task_ids:
            review_r = (
                supabase.table("task_assignments")
                .select("assignment_id", count="exact")
                .in_("taskid", task_ids)
                .eq("status", "review")
                .execute()
            )
            tasks_pending_review = getattr(review_r, "count", None) or (len(review_r.data or []))

    teams_r = supabase.table("teams").select("teamid", count="exact").eq("mentor_userid", mentor_userid).execute()
    teams_count = getattr(teams_r, "count", None) or (len(teams_r.data or []))

    return {
        "success": True,
        "tasks_pending_review": tasks_pending_review,
        "teams_count": teams_count,
        "modules_count": len(module_ids),
    }


def get_student_stats(student_userid: str) -> dict:
    """Task counts by status: assigned, in_progress, review, approved, rejected."""
    r = supabase.table("task_assignments").select("status").eq("student_userid", student_userid).execute()
    data = r.data or []
    by_status = {}
    for row in data:
        s = row.get("status") or "assigned"
        by_status[s] = by_status.get(s, 0) + 1
    return {
        "success": True,
        "by_status": by_status,
        "total": len(data),
        "assigned": by_status.get("assigned", 0),
        "in_progress": by_status.get("in_progress", 0),
        "review": by_status.get("review", 0),
        "approved": by_status.get("approved", 0),
        "rejected": by_status.get("rejected", 0),
    }
