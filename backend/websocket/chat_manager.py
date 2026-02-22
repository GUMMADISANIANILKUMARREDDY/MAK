"""WebSocket connection manager for real-time chat."""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Set
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


def _json_serial(obj: Any) -> Any:
    """Ensure message dict is JSON-serializable (UUID, datetime -> str)."""
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _json_serial(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_serial(v) for v in obj]
    return obj


class ChatConnectionManager:
    """Tracks WebSocket connections per user and broadcasts messages to conversation participants."""

    def __init__(self):
        # userid -> set of WebSocket connections (user may have multiple tabs)
        self._connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, userid: str) -> None:
        """Register a WebSocket for a user."""
        await websocket.accept()
        if userid not in self._connections:
            self._connections[userid] = set()
        self._connections[userid].add(websocket)
        logger.info("WebSocket connected: userid=%s, total=%d", userid, len(self._connections.get(userid, [])))

    def disconnect(self, websocket: WebSocket, userid: str | None) -> None:
        """Remove a WebSocket connection."""
        if userid and userid in self._connections:
            self._connections[userid].discard(websocket)
            if not self._connections[userid]:
                del self._connections[userid]
        logger.info("WebSocket disconnected: userid=%s", userid)

    async def broadcast_to_conversation(
        self, mentor_userid: str, student_userid: str, message: dict
    ) -> None:
        """Send a new message to both mentor and student in the conversation."""
        msg_serial = _json_serial(message)
        payload = json.dumps({"type": "new_message", "message": msg_serial})
        targets = {mentor_userid, student_userid}
        for userid in targets:
            conns = self._connections.get(userid, set()).copy()
            for ws in conns:
                try:
                    await ws.send_text(payload)
                except Exception as e:
                    logger.warning("Failed to send to %s: %s", userid, e)
                    self._connections.get(userid, set()).discard(ws)

    async def send_messages_read(self, recipient_userid: str, message_ids: list, read_at: str) -> None:
        """Notify sender that their messages were read (for blue tick)."""
        if not message_ids:
            return
        payload = json.dumps({"type": "messages_read", "message_ids": message_ids, "read_at": read_at})
        conns = self._connections.get(recipient_userid, set()).copy()
        for ws in conns:
            try:
                await ws.send_text(payload)
            except Exception as e:
                logger.warning("Failed to send read receipt to %s: %s", recipient_userid, e)
                self._connections.get(recipient_userid, set()).discard(ws)

    async def send_typing(self, recipient_userid: str, conversation_id: str, typer_userid: str, typer_username: str) -> None:
        """Notify recipient that someone is typing."""
        payload = json.dumps({"type": "typing", "conversation_id": str(conversation_id), "userid": typer_userid, "username": typer_username})
        conns = self._connections.get(recipient_userid, set()).copy()
        for ws in conns:
            try:
                await ws.send_text(payload)
            except Exception as e:
                logger.warning("Failed to send typing to %s: %s", recipient_userid, e)
                self._connections.get(recipient_userid, set()).discard(ws)

    async def send_to_user(self, userid: str, payload: str) -> None:
        """Send raw payload to a user's connections."""
        conns = self._connections.get(userid, set()).copy()
        for ws in conns:
            try:
                await ws.send_text(payload)
            except Exception as e:
                logger.warning("Failed to send to %s: %s", userid, e)
                self._connections.get(userid, set()).discard(ws)

    def get_online_userids(self) -> set:
        """Return set of currently connected userids."""
        return set(self._connections.keys())


# Singleton instance
chat_manager = ChatConnectionManager()
