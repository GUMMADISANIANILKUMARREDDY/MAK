"""Tests for /admin/activity-logs API endpoints."""

import pytest
from unittest.mock import patch


class TestAdminActivityLogs:
    """GET /admin/activity-logs."""

    @patch("api.routes.admin_activity.get_activity_logs")
    def test_list_activity_logs_returns_data(self, mock_get, admin_client):
        mock_get.return_value = {"logs": [], "total": 0}
        response = admin_client.get("/admin/activity-logs")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data

    @patch("api.routes.admin_activity.get_activity_logs")
    def test_list_activity_logs_with_filters(self, mock_get, admin_client):
        mock_get.return_value = {"logs": [], "total": 0}
        response = admin_client.get(
            "/admin/activity-logs",
            params={
                "userid": "u1",
                "entity_type": "user",
                "date_from": "2025-01-01",
                "date_to": "2025-12-31",
                "page": 1,
                "limit": 50,
            },
        )
        assert response.status_code == 200

    def test_list_activity_logs_forbidden_without_admin(self, student_client):
        response = student_client.get("/admin/activity-logs")
        assert response.status_code == 403
