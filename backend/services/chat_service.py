"""In-app chat: conversations and messages."""
from typing import Optional
from config.supabase_client import supabase


def get_or_create_conversation(mentor_userid: str, student_userid: str) -> dict:
    """Get existing or create new conversation between mentor and student."""
    r = supabase.table("conversations").select("*").eq("mentor_userid", mentor_userid).eq("student_userid", student_userid).execute()
    if r.data:
        return {"success": True, "conversation": r.data[0]}
    try:
        ins = supabase.table("conversations").insert({
            "mentor_userid": mentor_userid,
            "student_userid": student_userid,
        }).execute()
        if ins.data:
            return {"success": True, "conversation": ins.data[0]}
    except Exception:
        pass
    return {"success": False, "message": "Failed to create conversation"}


def get_my_conversations(userid: str, as_mentor: bool) -> dict:
    """List conversations for mentor or student."""
    if as_mentor:
        r = supabase.table("conversations").select("*").eq("mentor_userid", userid).order("updated_at", desc=True).execute()
    else:
        r = supabase.table("conversations").select("*").eq("student_userid", userid).order("updated_at", desc=True).execute()
    return {"success": True, "conversations": r.data or []}


def get_messages(conversation_id: str, limit: int = 100) -> dict:
    """List messages in conversation."""
    r = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    messages = list(reversed(r.data or []))
    return {"success": True, "messages": messages}


def send_message(conversation_id: str, sender_userid: str, body: str) -> dict:
    """Send message and update conversation updated_at."""
    if not (body or "").strip():
        return {"success": False, "message": "Message empty"}
    try:
        ins = supabase.table("messages").insert({
            "conversation_id": conversation_id,
            "sender_userid": sender_userid,
            "body": body.strip(),
        }).execute()
        if ins.data:
            from datetime import datetime
            supabase.table("conversations").update({"updated_at": datetime.utcnow().isoformat()}).eq("id", conversation_id).execute()
            return {"success": True, "message": ins.data[0]}
    except Exception as e:
        return {"success": False, "message": str(e)}
    return {"success": False, "message": "Failed to send"}


def user_in_conversation(conversation_id: str, userid: str) -> bool:
    """Check if user is mentor or student in this conversation."""
    r = supabase.table("conversations").select("mentor_userid, student_userid").eq("id", conversation_id).execute()
    if not r.data:
        return False
    c = r.data[0]
    return c.get("mentor_userid") == userid or c.get("student_userid") == userid
