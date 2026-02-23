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
    "chat_message",
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
    """Get notifications for user, newest first. Excludes soft-deleted."""
    query = supabase.table("notifications").select("*").eq("userid", userid).is_("deleted_at", "null")
    if unread_only:
        query = query.eq("read", False)
    result = query.order("created_at", desc=True).limit(limit).execute()
    return {"success": True, "notifications": result.data or []}


def mark_as_read(notification_id: str, userid: str) -> dict:
    """Mark one notification as read (only if it belongs to user). Stores read_at for audit."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    result = (
        supabase.table("notifications")
        .update({"read": True, "read_at": now})
        .eq("id", notification_id)
        .eq("userid", userid)
        .is_("deleted_at", "null")
        .execute()
    )
    if not result.data or len(result.data) == 0:
        return {"success": False, "message": "Notification not found"}
    return {"success": True, "message": "Marked as read"}


def mark_all_read(userid: str) -> dict:
    """Mark all notifications as read for user. Stores read_at for audit."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("notifications").update({"read": True, "read_at": now}).eq("userid", userid).eq("read", False).is_("deleted_at", "null").execute()
    return {"success": True, "message": "All marked as read"}


def get_unread_count(userid: str) -> int:
    """Return count of unread notifications for user (excludes soft-deleted)."""
    result = supabase.table("notifications").select("id", count="exact").eq("userid", userid).eq("read", False).is_("deleted_at", "null").execute()
    return getattr(result, "count", 0) or 0


def soft_delete_notification(notification_id: str, userid: str) -> dict:
    """Soft delete: set deleted_at. Notification is stored but hidden from list. Works for every role."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    result = (
        supabase.table("notifications")
        .update({"deleted_at": now})
        .eq("id", notification_id)
        .eq("userid", userid)
        .execute()
    )
    if not result.data or len(result.data) == 0:
        return {"success": False, "message": "Notification not found"}
    return {"success": True, "message": "Notification removed"}


def _get_user_email(userid: str) -> Optional[str]:
    """Get user email from users table."""
    try:
        r = supabase.table("users").select("email").eq("userid", userid).limit(1).execute()
        if r.data and len(r.data) > 0:
            return r.data[0].get("email") or ""
    except Exception:
        pass
    return None


def _send_push(userid: str, title: str, body: str, link: str = "") -> None:
    """Send Web Push to user (phone notification panel). Silently fails if push unavailable."""
    try:
        from config.settings import settings
        from services.push_service import send_push_to_user
        url = link or (settings.FRONTEND_URL + "/dashboard")
        send_push_to_user(userid, title, body, data={"url": url})
    except Exception:
        pass


def notify_task_assigned(userid: str, task_title: str, link: str = "") -> None:
    """Create in-app notification, send email, and Web Push for task assigned."""
    create_notification(userid, "task_assigned", "New task assigned", f"You were assigned: {task_title}", link)
    email = _get_user_email(userid)
    if email:
        from services.email_service import send_task_assigned_email
        send_task_assigned_email(email, task_title, link)
    _send_push(userid, "New task assigned", f"You were assigned: {task_title}", link)


def notify_task_status_changed(userid: str, task_title: str, status: str, link: str = "") -> None:
    """Create notification, send email, and Web Push for task status change."""
    create_notification(userid, "task_status_changed", "Task status updated", f'Task "{task_title}": {status}', link)
    email = _get_user_email(userid)
    if email:
        from services.email_service import send_task_status_changed_email
        send_task_status_changed_email(email, task_title, status, link)
    _send_push(userid, "Task status updated", f'Task "{task_title}": {status}', link)


def notify_deadline_approaching(userid: str, task_title: str, due_date: str, link: str = "") -> None:
    """Create notification, send email, and Web Push for deadline approaching."""
    create_notification(userid, "deadline_approaching", "Deadline approaching", f'Task "{task_title}" due {due_date}', link)
    email = _get_user_email(userid)
    if email:
        from services.email_service import send_deadline_approaching_email
        send_deadline_approaching_email(email, task_title, due_date, link)
    _send_push(userid, "Deadline approaching", f'Task "{task_title}" due {due_date}', link)


def notify_task_reviewed(userid: str, task_title: str, approved: bool, feedback: str = "", link: str = "") -> None:
    """Create notification, send email, and Web Push for task reviewed."""
    title = "Task approved" if approved else "Task needs changes"
    create_notification(userid, "task_reviewed", title, f'Task "{task_title}": {title}', link)
    email = _get_user_email(userid)
    if email:
        from services.email_service import send_task_reviewed_email
        send_task_reviewed_email(email, task_title, approved, feedback, link)
    _send_push(userid, title, f'Task "{task_title}": {title}', link)


def notify_student_added_to_team(userid: str, team_name: str, link: str = "") -> None:
    """Create notification, send email, and Web Push for student added to team."""
    create_notification(userid, "student_added_to_team", "Added to team", f"You were added to team: {team_name}", link)
    email = _get_user_email(userid)
    if email:
        from services.email_service import send_student_added_to_team_email
        send_student_added_to_team_email(email, team_name, link)
    _send_push(userid, "Added to team", f"You were added to team: {team_name}", link)


def notify_mentor_assigned(userid: str, module_title: str, link: str = "") -> None:
    """Create notification, send email, and Web Push for mentor assigned to module."""
    create_notification(userid, "mentor_assigned", "Module assigned", f"You were assigned to module: {module_title}", link)
    email = _get_user_email(userid)
    if email:
        from services.email_service import send_mentor_assigned_email
        send_mentor_assigned_email(email, module_title, link)
    _send_push(userid, "Module assigned", f"You were assigned to module: {module_title}", link)


def notify_chat_message(
    recipient_userid: str,
    sender_username: str,
    message_preview: str,
    link: str = "",
    message_id: str | None = None,
) -> None:
    """Create in-app notification and enqueue delayed email (5 min). Email sent only if message still unread."""
    preview = (message_preview or "")[:100] + ("..." if len(message_preview or "") > 100 else "")
    create_notification(recipient_userid, "chat_message", f"New message from {sender_username}", preview, link)
    # Don't send email immediately - enqueue for 5 min delay; cron will send only if still unread
    if message_id:
        try:
            supabase.table("pending_chat_emails").insert({
                "message_id": message_id,
                "recipient_userid": recipient_userid,
                "sender_username": sender_username,
                "message_preview": (message_preview or "")[:500],
                "link": link or "",
            }).execute()
        except Exception:
            pass


def process_pending_chat_emails() -> dict:
    """Send emails for chat messages that are 5+ min old and still unread. Called by cron every 5 min."""
    from datetime import datetime, timezone, timedelta
    from services.email_service import send_chat_message_email

    five_min_ago = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    try:
        r = supabase.table("pending_chat_emails").select("*").lt("created_at", five_min_ago).execute()
    except Exception:
        return {"sent": 0, "skipped": 0}
    rows = r.data or []
    sent = 0
    for row in rows:
        msg_id = row.get("message_id")
        pid = row.get("id")
        try:
            m = supabase.table("messages").select("read_at").eq("id", msg_id).limit(1).execute()
            if m.data and len(m.data) > 0 and m.data[0].get("read_at") is None:
                email = _get_user_email(row.get("recipient_userid", ""))
                if email:
                    send_chat_message_email(
                        email,
                        row.get("sender_username", "Someone"),
                        row.get("message_preview", ""),
                        row.get("link", ""),
                    )
                    sent += 1
        except Exception:
            pass
        try:
            supabase.table("pending_chat_emails").delete().eq("id", pid).execute()
        except Exception:
            pass
    return {"sent": sent, "processed": len(rows)}
