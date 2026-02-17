"""Chat: conversations and messages (mentor ↔ student)."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from services.chat_service import (
    get_or_create_conversation,
    get_my_conversations,
    get_messages,
    send_message,
    user_in_conversation,
)
from api.dependencies import require_role, get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


class SendMessageRequest(BaseModel):
    body: str


@router.get("/conversations")
def list_conversations(current_user: dict = Depends(get_current_user)):
    """List my conversations (as mentor or student)."""
    role = current_user.get("role")
    if role == "mentor":
        return get_my_conversations(current_user["sub"], as_mentor=True)
    if role == "student":
        return get_my_conversations(current_user["sub"], as_mentor=False)
    return {"success": True, "conversations": []}


@router.get("/conversations/with/{other_userid}")
def get_or_create_conversation_route(other_userid: str, current_user: dict = Depends(require_role(["mentor", "student"]))):
    """Get or create conversation. Mentor can open with student; student with mentor."""
    role = current_user.get("role")
    if role == "mentor":
        result = get_or_create_conversation(current_user["sub"], other_userid)
    else:
        result = get_or_create_conversation(other_userid, current_user["sub"])
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@router.get("/conversations/{conversation_id}/messages")
def list_messages(
    conversation_id: str,
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
):
    """List messages in conversation."""
    if not user_in_conversation(conversation_id, current_user["sub"]):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return get_messages(conversation_id, limit)


@router.post("/conversations/{conversation_id}/messages")
def send_message_route(
    conversation_id: str,
    data: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
):
    """Send message in conversation."""
    if not user_in_conversation(conversation_id, current_user["sub"]):
        raise HTTPException(status_code=404, detail="Conversation not found")
    result = send_message(conversation_id, current_user["sub"], data.body)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result
