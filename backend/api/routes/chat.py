"""Chat: conversations and messages (mentor ↔ student)."""
import json
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel

from config.settings import settings
from services.chat_service import (
    get_or_create_conversation,
    get_my_conversations,
    get_messages,
    send_message,
    user_in_conversation,
    get_conversation_participants,
    get_conversation_partners,
    search_chattable_users,
)
from api.dependencies import require_role, get_current_user
from websocket.chat_manager import chat_manager

router = APIRouter(prefix="/chat", tags=["Chat"])


def _decode_ws_token(token: str | None) -> dict | None:
    """Decode JWT from token string. Returns payload or None."""
    if not token or not token.strip():
        return None
    try:
        payload = jwt.decode(
            token.strip(),
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("sub"):
            return payload
    except JWTError:
        pass
    return None


class SendMessageRequest(BaseModel):
    body: str


@router.get("/available-users")
def list_available_users(
    q: Optional[str] = Query(None, description="Search by username, email, or userid"),
    limit: int = Query(20, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    """Search any user to start a chat with (mentors, students, admins, etc.)."""
    return search_chattable_users(
        current_user["sub"],
        search=q,
        limit=limit,
    )


@router.get("/online-status")
def online_status(current_user: dict = Depends(get_current_user)):
    """Get which of your conversation partners are currently online."""
    partners = get_conversation_partners(current_user["sub"])
    online = chat_manager.get_online_userids()
    return {"online_userids": [p for p in partners if p in online]}


@router.get("/conversations")
def list_conversations(current_user: dict = Depends(get_current_user)):
    """List my conversations. Works for any role."""
    return get_my_conversations(current_user["sub"])


@router.get("/conversations/with/{other_userid}")
def get_or_create_conversation_route(other_userid: str, current_user: dict = Depends(get_current_user)):
    """Get or create conversation with any user."""
    result = get_or_create_conversation(current_user["sub"], other_userid)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.get("/conversations/{conversation_id}/messages")
async def list_messages(
    conversation_id: str,
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
):
    """List messages in conversation. Marks messages from other party as read."""
    if not user_in_conversation(conversation_id, current_user["sub"]):
        raise HTTPException(status_code=404, detail="Conversation not found")
    result, read_info = get_messages(conversation_id, limit, reader_userid=current_user["sub"])
    if read_info:
        ids, read_at, sender_userid = read_info
        await chat_manager.send_messages_read(sender_userid, ids, read_at)
    return result


@router.post("/conversations/{conversation_id}/messages")
async def send_message_route(
    conversation_id: str,
    data: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
):
    """Send message in conversation and broadcast via WebSocket for real-time delivery."""
    if not user_in_conversation(conversation_id, current_user["sub"]):
        raise HTTPException(status_code=404, detail="Conversation not found")
    result = send_message(conversation_id, current_user["sub"], data.body)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    # Broadcast new message to conversation participants via WebSocket
    msg = result.get("message")
    if msg:
        mentor_userid, student_userid = get_conversation_participants(conversation_id)
        recipient_userid = student_userid if mentor_userid == current_user["sub"] else mentor_userid
        if mentor_userid and student_userid:
            await chat_manager.broadcast_to_conversation(
                mentor_userid, student_userid, msg
            )
        # If recipient is offline, send email and Web Push notification
        online = chat_manager.get_online_userids()
        if recipient_userid and recipient_userid not in online:
            link = f"{settings.FRONTEND_URL}/dashboard?tab=chat&conversation={conversation_id}"
            sender_username = current_user.get("username") or current_user["sub"]
            try:
                from services.notification_service import notify_chat_message
                notify_chat_message(recipient_userid, sender_username, data.body or "", link)
            except Exception:
                pass
            try:
                from services.push_service import send_push_to_user
                preview = (data.body or "")[:80] + ("..." if len(data.body or "") > 80 else "")
                send_push_to_user(
                    recipient_userid,
                    title=f"Message from {sender_username}",
                    body=preview,
                    data={"url": link, "conversation_id": conversation_id},
                )
            except Exception:
                pass
    return result


@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time chat. Connect with ?token=<jwt>."""
    token = websocket.query_params.get("token")
    payload = _decode_ws_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid or missing token")
        return
    userid = payload.get("sub")
    if not userid:
        await websocket.close(code=4001, reason="Invalid token")
        return
    await chat_manager.connect(websocket, userid)
    partners = get_conversation_partners(userid)
    online_set = chat_manager.get_online_userids()
    partners_online = [p for p in partners if p in online_set]
    await websocket.send_text(json.dumps({"type": "online_status", "online_userids": partners_online}))
    for pid in partners:
        await chat_manager.send_to_user(pid, json.dumps({"type": "user_online", "userid": userid}))
    try:
        while True:
            data = await websocket.receive_text()
            try:
                obj = json.loads(data)
                if obj.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif obj.get("type") == "typing":
                    conv_id = obj.get("conversation_id")
                    if conv_id and user_in_conversation(conv_id, userid):
                        mentor_userid, student_userid = get_conversation_participants(conv_id)
                        other = student_userid if mentor_userid == userid else mentor_userid
                        if other:
                            username = obj.get("username") or userid
                            await chat_manager.send_typing(other, conv_id, userid, username)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        for pid in partners:
            await chat_manager.send_to_user(pid, json.dumps({"type": "user_offline", "userid": userid}))
        chat_manager.disconnect(websocket, userid)
