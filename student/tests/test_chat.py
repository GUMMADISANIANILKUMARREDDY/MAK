"""Tests for /chat API endpoints."""

import pytest
from unittest.mock import patch


class TestChatConversations:
    """GET /chat/conversations."""

    @patch("api.routes.chat.get_my_conversations")
    def test_list_conversations_as_mentor(self, mock_get, mentor_client):
        mock_get.return_value = {"success": True, "conversations": []}
        response = mentor_client.get("/chat/conversations")
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data

    @patch("api.routes.chat.get_my_conversations")
    def test_list_conversations_as_student(self, mock_get, student_client):
        mock_get.return_value = {"success": True, "conversations": []}
        response = student_client.get("/chat/conversations")
        assert response.status_code == 200

    def test_list_conversations_unauthorized_without_token(self, client):
        response = client.get("/chat/conversations")
        assert response.status_code == 401


class TestChatGetOrCreateConversation:
    """GET /chat/conversations/with/{other_userid}."""

    @patch("api.routes.chat.get_or_create_conversation")
    def test_get_or_create_conversation_success(self, mock_get, mentor_client):
        mock_get.return_value = {"success": True, "conversation_id": "conv1"}
        response = mentor_client.get("/chat/conversations/with/stu1")
        assert response.status_code == 200
        assert response.json().get("conversation_id") == "conv1"

    @patch("api.routes.chat.get_or_create_conversation")
    def test_get_or_create_conversation_failure_400(self, mock_get, mentor_client):
        mock_get.return_value = {"success": False, "message": "User not found"}
        response = mentor_client.get("/chat/conversations/with/unknown")
        assert response.status_code == 400

    def test_get_or_create_forbidden_for_admin(self, admin_client):
        response = admin_client.get("/chat/conversations/with/stu1")
        assert response.status_code == 403


class TestChatMessages:
    """GET/POST /chat/conversations/{conversation_id}/messages."""

    @patch("api.routes.chat.user_in_conversation")
    @patch("api.routes.chat.get_messages")
    def test_list_messages_success(self, mock_get, mock_in, mentor_client):
        mock_in.return_value = True
        mock_get.return_value = {"messages": []}
        response = mentor_client.get("/chat/conversations/conv1/messages")
        assert response.status_code == 200
        assert "messages" in response.json()

    @patch("api.routes.chat.user_in_conversation")
    def test_list_messages_not_in_conversation_404(self, mock_in, mentor_client):
        mock_in.return_value = False
        response = mentor_client.get("/chat/conversations/conv1/messages")
        assert response.status_code == 404

    @patch("api.routes.chat.user_in_conversation")
    @patch("api.routes.chat.send_message")
    def test_send_message_success(self, mock_send, mock_in, mentor_client):
        mock_in.return_value = True
        mock_send.return_value = {"success": True, "message_id": "msg1"}
        response = mentor_client.post(
            "/chat/conversations/conv1/messages",
            json={"body": "Hello"},
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    @patch("api.routes.chat.user_in_conversation")
    def test_send_message_not_in_conversation_404(self, mock_in, mentor_client):
        mock_in.return_value = False
        response = mentor_client.post(
            "/chat/conversations/conv1/messages",
            json={"body": "Hello"},
        )
        assert response.status_code == 404

    @patch("api.routes.chat.user_in_conversation")
    @patch("api.routes.chat.send_message")
    def test_send_message_failure_400(self, mock_send, mock_in, mentor_client):
        mock_in.return_value = True
        mock_send.return_value = {"success": False, "message": "Empty body"}
        response = mentor_client.post(
            "/chat/conversations/conv1/messages",
            json={"body": ""},
        )
        assert response.status_code == 400
