"""In-app chat: conversations and messages."""
from typing import Optional
from config.supabase_client import supabase


def get_or_create_conversation(mentor_userid: str, student_userid: str) -> dict:
    """Get existing or create new conversation. Uses mentor/student columns for any two users (ordered for consistency)."""
    # Ensure consistent ordering: smaller userid -> mentor_userid
    u1, u2 = (mentor_userid, student_userid) if mentor_userid <= student_userid else (student_userid, mentor_userid)
    r = supabase.table("conversations").select("*").eq("mentor_userid", u1).eq("student_userid", u2).execute()
    if r.data:
        return {"success": True, "conversation": r.data[0]}
    try:
        ins = supabase.table("conversations").insert({
            "mentor_userid": u1,
            "student_userid": u2,
        }).execute()
        if ins.data:
            return {"success": True, "conversation": ins.data[0]}
    except Exception:
        pass
    return {"success": False, "message": "Failed to create conversation"}


def _get_usernames(userids: list) -> dict:
    """Fetch userid -> username mapping for display."""
    if not userids:
        return {}
    r = supabase.table("users").select("userid, username").in_("userid", list(set(userids))).execute()
    return {u["userid"]: (u.get("username") or u.get("userid") or "") for u in (r.data or [])}


def get_conversation_partners(userid: str) -> list[str]:
    """Return userids of everyone this user has a conversation with."""
    r1 = supabase.table("conversations").select("mentor_userid, student_userid").eq("mentor_userid", userid).execute()
    r2 = supabase.table("conversations").select("mentor_userid, student_userid").eq("student_userid", userid).execute()
    partners = set()
    for c in (r1.data or []) + (r2.data or []):
        m, s = c.get("mentor_userid"), c.get("student_userid")
        if m and m != userid:
            partners.add(m)
        if s and s != userid:
            partners.add(s)
    return list(partners)


def get_my_conversations(userid: str, as_mentor: bool = None) -> dict:
    """List conversations where user is a participant, with other participant's display name and last message."""
    r1 = supabase.table("conversations").select("*").eq("mentor_userid", userid).order("updated_at", desc=True).execute()
    r2 = supabase.table("conversations").select("*").eq("student_userid", userid).order("updated_at", desc=True).execute()
    convos = (r1.data or []) + (r2.data or [])
    convos = sorted(convos, key=lambda c: c.get("updated_at") or "", reverse=True)
    conv_ids = [c["id"] for c in convos]
    userids = []
    for c in convos:
        m, s = c.get("mentor_userid"), c.get("student_userid")
        if m and m != userid:
            userids.append(m)
        if s and s != userid:
            userids.append(s)
    names = _get_usernames(userids)
    last_msgs = {}
    if conv_ids:
        r = supabase.table("messages").select("conversation_id, body, created_at, sender_userid").in_("conversation_id", conv_ids).order("created_at", desc=True).limit(500).execute()
        for m in r.data or []:
            cid = m.get("conversation_id")
            if cid and cid not in last_msgs:
                last_msgs[cid] = {"body": m.get("body", ""), "created_at": m.get("created_at"), "sender_userid": m.get("sender_userid")}
    for c in convos:
        other = c.get("student_userid") if c.get("mentor_userid") == userid else c.get("mentor_userid")
        c["other_userid"] = other
        c["other_username"] = names.get(other, other or "")
        c["last_message"] = last_msgs.get(c["id"])
    return {"success": True, "conversations": convos}


def mark_messages_read(conversation_id: str, reader_userid: str) -> tuple[list, str | None, str | None]:
    """Mark messages from the other party as read. Returns (message_ids, read_at, sender_userid)."""
    from datetime import datetime
    r = supabase.table("messages").select("id, sender_userid").eq("conversation_id", conversation_id).neq("sender_userid", reader_userid).is_("read_at", "null").execute()
    rows = r.data or []
    ids = [str(m["id"]) for m in rows if m.get("id")]
    sender_userid = rows[0].get("sender_userid") if rows else None
    if ids:
        now = datetime.utcnow().isoformat()
        for m in rows:
            if m.get("id"):
                supabase.table("messages").update({"read_at": now}).eq("id", m["id"]).execute()
        return ids, now, sender_userid
    return [], None, None


def get_messages(conversation_id: str, limit: int = 100, reader_userid: str | None = None) -> tuple[dict, tuple | None]:
    """List messages in conversation. If reader_userid given, mark received messages as read.
    Returns (result_dict, read_info) where read_info is (message_ids, read_at, sender_userid) for WebSocket."""
    read_info = None
    if reader_userid:
        ids, read_at, sender = mark_messages_read(conversation_id, reader_userid)
        if ids and sender:
            read_info = (ids, read_at, sender)
    r = (
        supabase.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    messages = list(reversed(r.data or []))
    return {"success": True, "messages": messages}, read_info


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


def get_conversation_participants(conversation_id: str) -> tuple[str | None, str | None]:
    """Return (mentor_userid, student_userid) for a conversation, or (None, None) if not found."""
    r = supabase.table("conversations").select("mentor_userid, student_userid").eq("id", conversation_id).execute()
    if not r.data:
        return None, None
    c = r.data[0]
    return c.get("mentor_userid"), c.get("student_userid")


def search_chattable_users(userid: str, search: Optional[str] = None, limit: int = 20) -> dict:
    """Search any user to start a chat with (mentors, students, admins, etc.). Excludes self."""
    query = (
        supabase.table("users")
        .select("userid, username, email, role")
        .eq("active", True)
        .neq("userid", userid)
        .in_("role", ["mentor", "student", "admin", "manager", "clgadmin"])
    )
    if search and search.strip():
        q = search.strip()
        query = query.or_(f"username.ilike.%{q}%,email.ilike.%{q}%,userid.ilike.%{q}%")
    r = query.limit(limit).order("username").execute()
    return {"success": True, "users": r.data or []}
