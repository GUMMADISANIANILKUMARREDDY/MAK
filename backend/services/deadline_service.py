"""Deadline approaching: notify students for tasks due in next N days."""
from datetime import date, timedelta
from config.supabase_client import supabase
from services.notification_service import notify_deadline_approaching

DEADLINE_DAYS_AHEAD = 3  # Notify if due in next 3 days
DEADLINE_NOTIFIED_KEY = "deadline_approaching_sent"  # Could use a table; we use in-memory or skip duplicate by checking notifications


def check_deadlines_for_user(student_userid: str) -> int:
    """For a student, find assignments with due_date in next DEADLINE_DAYS_AHEAD days, send notification+email once per task. Returns count sent."""
    today = date.today()
    end = today + timedelta(days=DEADLINE_DAYS_AHEAD)
    # Get task_assignments for this student with status not yet completed (assigned, in_progress, review) and task has due_date in range
    assignments = (
        supabase.table("task_assignments")
        .select("assignment_id, taskid, status")
        .eq("student_userid", student_userid)
        .in_("status", ["assigned", "in_progress"])
        .execute()
    )
    if not assignments.data:
        return 0
    task_ids = list({a["taskid"] for a in assignments.data})
    tasks = supabase.table("tasks").select("taskid, title, due_date").in_("taskid", task_ids).execute()
    if not tasks.data:
        return 0
    sent = 0
    for t in tasks.data:
        due = t.get("due_date")
        if not due:
            continue
        if isinstance(due, str):
            due = date.fromisoformat(due[:10])
        if today <= due <= end:
            # Avoid spamming: check if we already sent deadline_approaching for this task+user recently (e.g. last 24h)
            # Simple approach: send (user can get once per login). For production, add deadline_notified_at on task_assignments or a small table.
            notify_deadline_approaching(
                student_userid,
                t.get("title", "Task"),
                str(due),
                link="",
            )
            sent += 1
    return sent


def check_all_deadlines() -> dict:
    """Cron: for all students with assigned/in_progress tasks due in next N days, send notification. Returns count of notifications sent."""
    today = date.today()
    end = today + timedelta(days=DEADLINE_DAYS_AHEAD)
    assignments = (
        supabase.table("task_assignments")
        .select("student_userid, taskid")
        .in_("status", ["assigned", "in_progress"])
        .execute()
    )
    if not assignments.data:
        return {"success": True, "sent": 0}
    task_ids = list({a["taskid"] for a in assignments.data})
    tasks = supabase.table("tasks").select("taskid, title, due_date").in_("taskid", task_ids).execute()
    task_map = {t["taskid"]: t for t in (tasks.data or [])}
    sent = 0
    notified = set()  # (student_userid, taskid) to avoid duplicate
    for a in assignments.data:
        t = task_map.get(a["taskid"])
        if not t or not t.get("due_date"):
            continue
        due = t["due_date"]
        if isinstance(due, str):
            due = date.fromisoformat(due[:10])
        if today <= due <= end:
            key = (a["student_userid"], a["taskid"])
            if key not in notified:
                notify_deadline_approaching(
                    a["student_userid"],
                    t.get("title", "Task"),
                    str(due),
                    link="",
                )
                notified.add(key)
                sent += 1
    return {"success": True, "sent": sent}
