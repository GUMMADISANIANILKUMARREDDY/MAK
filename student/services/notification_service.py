"""In-app notifications: create, list, mark read."""
from typing import Optional
from config.supabase_client import supabase

NOTIFICATION_TYPES = (
    "task_assigned",
    "task_status_changed",
    "deadline_approaching",
    "task_reviewed",
    "student_added_to_team",
    "mentor_assigned",
)


def create_notification(
    userid: str,
    type: str,
    title: str,
    message: Optional[str] = None,
    link: Optional[str] = None,
) -> Optional[dict]:
    """Create a notification for a user. Returns notification dict or None on failure."""
    if type not in NOTIFICATION_TYPES:
        type = "task_assigned"  # fallback
    try:
        result = supabase.table("notifications").insert(
            {
                "userid": userid,
                "type": type,
                "title": title,
                "message": message or "",
                "link": link,
                "read": False,
            }
        ).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
    except Exception:
        pass
    return None


def get_my_notifications(
    userid: str,
    unread_only: bool = False,
    limit: int = 50,
) -> dict:
    """Get notifications for user, newest first."""
    query = supabase.table("notifications").select("*").eq("userid", userid)
    if unread_only:
        query = query.eq("read", False)
    result = query.order("created_at", desc=True).limit(limit).execute()
    return {"success": True, "notifications": result.data or []}


def mark_as_read(notification_id: str, userid: str) -> dict:
    """Mark one notification as read (only if it belongs to user)."""
    result = (
        supabase.table("notifications")
        .update({"read": True})
        .eq("id", notification_id)
        .eq("userid", userid)
        .execute()
    )
    if not result.data or len(result.data) == 0:
        return {"success": False, "message": "Notification not found"}
    return {"success": True, "message": "Marked as read"}


def mark_all_read(userid: str) -> dict:
    """Mark all notifications as read for user."""
    supabase.table("notifications").update({"read": True}).eq("userid", userid).eq("read", False).execute()
    return {"success": True, "message": "All marked as read"}


def get_unread_count(userid: str) -> int:
    """Return count of unread notifications for user."""
    result = supabase.table("notifications").select("id", count="exact").eq("userid", userid).eq("read", False).execute()
    return getattr(result, "count", 0) or 0


def _get_user_email(userid: str) -> Optional[str]:
    """Get user email from users table."""
    try:
        r = supabase.table("users").select("email").eq("userid", userid).limit(1).execute()
        if r.data and len(r.data) > 0:
            return r.data[0].get("email") or ""
    except Exception:
        pass
    return None


def notify_task_assigned(userid: str, task_title: str, link: str = "") -> None:
    """Create in-app notification and send email for task assigned."""
    create_notification(userid, "task_assigned", "New task assigned", f"You were assigned: {task_title}", link)
    email = _get_user_email(userid)
    if email:
        from services.email_service import send_task_assigned_email
        send_task_assigned_email(email, task_title, link)


def notify_task_status_changed(userid: str, task_title: str, status: str, link: str = "") -> None:
    """Create notification and send email for task status change."""
    create_notification(userid, "task_status_changed", "Task status updated", f'Task "{task_title}": {status}', link)
    email = _get_user_email(userid)
    if email:
        from services.email_service import send_task_status_changed_email
        send_task_status_changed_email(email, task_title, status, link)


def notify_deadline_approaching(userid: str, task_title: str, due_date: str, link: str = "") -> None:
    """Create notification and send email for deadline approaching."""
    create_notification(userid, "deadline_approaching", "Deadline approaching", f'Task "{task_title}" due {due_date}', link)
    email = _get_user_email(userid)
    if email:
        from services.email_service import send_deadline_approaching_email
        send_deadline_approaching_email(email, task_title, due_date, link)


def notify_task_reviewed(userid: str, task_title: str, approved: bool, feedback: str = "", link: str = "") -> None:
    """Create notification and send email for task reviewed."""
    title = "Task approved" if approved else "Task needs changes"
    create_notification(userid, "task_reviewed", title, f'Task "{task_title}": {title}', link)
    email = _get_user_email(userid)
    if email:
        from services.email_service import send_task_reviewed_email
        send_task_reviewed_email(email, task_title, approved, feedback, link)


def notify_student_added_to_team(userid: str, team_name: str, link: str = "") -> None:
    """Create notification and send email for student added to team."""
    create_notification(userid, "student_added_to_team", "Added to team", f"You were added to team: {team_name}", link)
    email = _get_user_email(userid)
    if email:
        from services.email_service import send_student_added_to_team_email
        send_student_added_to_team_email(email, team_name, link)


def notify_mentor_assigned(userid: str, module_title: str, link: str = "") -> None:
    """Create notification and send email for mentor assigned to module."""
    create_notification(userid, "mentor_assigned", "Module assigned", f"You were assigned to module: {module_title}", link)
    email = _get_user_email(userid)
    if email:
        from services.email_service import send_mentor_assigned_email
        send_mentor_assigned_email(email, module_title, link)
