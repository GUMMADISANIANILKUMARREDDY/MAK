"""Tests for /notifications API endpoints."""

import pytest
from unittest.mock import patch


class TestNotificationsList:
    """GET /notifications."""

    @patch("api.routes.notifications.get_my_notifications")
    def test_list_my_notifications_returns_data(self, mock_get, admin_client):
        mock_get.return_value = {"notifications": [], "total": 0}
        response = admin_client.get("/notifications")
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data

    @patch("api.routes.notifications.get_my_notifications")
    def test_list_notifications_with_unread_only(self, mock_get, student_client):
        mock_get.return_value = {"notifications": [], "total": 0}
        response = student_client.get("/notifications", params={"unread_only": True, "limit": 20})
        assert response.status_code == 200

    def test_list_notifications_unauthorized_without_token(self, client):
        response = client.get("/notifications")
        assert response.status_code == 401


class TestNotificationsUnreadCount:
    """GET /notifications/unread-count."""

    @patch("api.routes.notifications.get_unread_count")
    def test_unread_count_returns_number(self, mock_count, admin_client):
        mock_count.return_value = 5
        response = admin_client.get("/notifications/unread-count")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("count") == 5


class TestNotificationsMarkAllRead:
    """PUT /notifications/read-all."""

    @patch("api.routes.notifications.mark_all_read")
    def test_mark_all_read_success(self, mock_mark, admin_client):
        mock_mark.return_value = {"success": True}
        response = admin_client.put("/notifications/read-all")
        assert response.status_code == 200


class TestNotificationsMarkOneRead:
    """PUT /notifications/{notification_id}/read."""

    @patch("api.routes.notifications.svc_mark_as_read")
    def test_mark_one_read_success(self, mock_mark, admin_client):
        mock_mark.return_value = {"success": True}
        response = admin_client.put("/notifications/n1/read")
        assert response.status_code == 200

    @patch("api.routes.notifications.svc_mark_as_read")
    def test_mark_one_read_not_found_404(self, mock_mark, admin_client):
        mock_mark.return_value = {"success": False, "message": "Not found"}
        response = admin_client.put("/notifications/nonexistent/read")
        assert response.status_code == 404


class TestNotificationsDelete:
    """DELETE /notifications/{notification_id}."""

    @patch("api.routes.notifications.soft_delete_notification")
    def test_delete_notification_success(self, mock_delete, admin_client):
        mock_delete.return_value = {"success": True}
        response = admin_client.delete("/notifications/n1")
        assert response.status_code == 200

    @patch("api.routes.notifications.soft_delete_notification")
    def test_delete_notification_not_found_404(self, mock_delete, admin_client):
        mock_delete.return_value = {"success": False, "message": "Not found"}
        response = admin_client.delete("/notifications/nonexistent")
        assert response.status_code == 404
