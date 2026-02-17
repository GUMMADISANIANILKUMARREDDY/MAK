"""CSV export for admin and mentor."""
import csv
import io
from typing import Iterator
from config.supabase_client import supabase


def stream_students_csv() -> Iterator[str]:
    """Yield CSV lines for all students (admin)."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["userid", "first_name", "last_name", "email", "phone"])
    yield buf.getvalue()
    offset = 0
    limit = 200
    while True:
        r = supabase.table("students").select("*").range(offset, offset + limit - 1).execute()
        if not r.data:
            break
        for row in r.data:
            buf = io.StringIO()
            csv.writer(buf).writerow([
                row.get("userid", ""),
                row.get("first_name", ""),
                row.get("last_name", ""),
                row.get("email", ""),
                row.get("phone", ""),
            ])
            yield buf.getvalue()
        if len(r.data) < limit:
            break
        offset += limit


def stream_projects_csv() -> Iterator[str]:
    """Yield CSV lines for all projects (admin)."""
    buf = io.StringIO()
    csv.writer(buf).writerow(["projectid", "title", "description", "status", "start_date", "end_date", "created_at"])
    yield buf.getvalue()
    offset = 0
    limit = 200
    while True:
        r = supabase.table("projects").select("*").range(offset, offset + limit - 1).execute()
        if not r.data:
            break
        for row in r.data:
            buf = io.StringIO()
            csv.writer(buf).writerow([
                row.get("projectid", ""),
                row.get("title", ""),
                (row.get("description") or "")[:500],
                row.get("status", ""),
                row.get("start_date", ""),
                row.get("end_date", ""),
                row.get("created_at", ""),
            ])
            yield buf.getvalue()
        if len(r.data) < limit:
            break
        offset += limit


def stream_mentor_tasks_csv(mentor_userid: str) -> Iterator[str]:
    """Yield CSV lines for tasks in mentor's modules and their assignments."""
    ma = supabase.table("module_assignments").select("moduleid").eq("mentor_userid", mentor_userid).execute()
    module_ids = [r["moduleid"] for r in (ma.data or [])]
    if not module_ids:
        return
    tasks = supabase.table("tasks").select("taskid, moduleid, title, status, priority, due_date").in_("moduleid", module_ids).execute()
    task_list = tasks.data or []
    buf = io.StringIO()
    csv.writer(buf).writerow(["taskid", "title", "status", "priority", "due_date", "assignment_id", "student_userid", "assignment_status", "submitted"])
    yield buf.getvalue()
    for t in task_list:
        assigns = supabase.table("task_assignments").select("assignment_id, student_userid, status, submission_file_url").eq("taskid", t["taskid"]).execute()
        for a in (assigns.data or []):
            buf = io.StringIO()
            csv.writer(buf).writerow([
                t.get("taskid", ""),
                t.get("title", ""),
                t.get("status", ""),
                t.get("priority", ""),
                t.get("due_date", ""),
                a.get("assignment_id", ""),
                a.get("student_userid", ""),
                a.get("status", ""),
                "yes" if a.get("submission_file_url") else "no",
            ])
            yield buf.getvalue()

