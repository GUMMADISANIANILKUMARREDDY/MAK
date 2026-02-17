"""Task comments: list, create, delete."""
from typing import Optional
from config.supabase_client import supabase


def assignment_accessible_by_mentor(assignment_id: str, mentor_userid: str) -> bool:
    """Check if this assignment's task belongs to a module assigned to this mentor."""
    a = supabase.table("task_assignments").select("taskid").eq("assignment_id", assignment_id).execute()
    if not a.data:
        return False
    t = supabase.table("tasks").select("moduleid").eq("taskid", a.data[0]["taskid"]).execute()
    if not t.data:
        return False
    m = supabase.table("module_assignments").select("mentor_userid").eq("moduleid", t.data[0]["moduleid"]).eq("mentor_userid", mentor_userid).execute()
    return bool(m.data)


def assignment_accessible_by_student(assignment_id: str, student_userid: str) -> bool:
    r = supabase.table("task_assignments").select("student_userid").eq("assignment_id", assignment_id).execute()
    return bool(r.data and r.data[0].get("student_userid") == student_userid)


def list_comments(assignment_id: str) -> dict:
    """List comments for a task assignment, newest first."""
    result = (
        supabase.table("task_comments")
        .select("*")
        .eq("assignment_id", assignment_id)
        .order("created_at", desc=False)
        .execute()
    )
    return {"success": True, "comments": result.data or []}


def create_comment(assignment_id: str, userid: str, comment: str) -> dict:
    """Add a comment. Caller must ensure user has access to this assignment. Returns created comment or error."""
    if not (comment or "").strip():
        return {"success": False, "message": "Comment cannot be empty"}
    result = supabase.table("task_comments").insert({
        "assignment_id": assignment_id,
        "userid": userid,
        "comment": comment.strip(),
    }).execute()
    if not result.data:
        return {"success": False, "message": "Failed to add comment"}
    return {"success": True, "comment": result.data[0]}


def delete_comment(comment_id: str, userid: str) -> dict:
    """Delete own comment only."""
    r = supabase.table("task_comments").select("userid").eq("id", comment_id).execute()
    if not r.data or r.data[0].get("userid") != userid:
        return {"success": False, "message": "Comment not found or not yours"}
    supabase.table("task_comments").delete().eq("id", comment_id).execute()
    return {"success": True, "message": "Comment deleted"}
