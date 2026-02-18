"""Tests for /cron API endpoints."""

import pytest
from unittest.mock import patch


class TestCronDeadlineApproaching:
    """GET /cron/deadline-approaching."""

    @patch("api.routes.cron.settings")
    @patch("api.routes.cron.check_all_deadlines")
    def test_cron_without_secret_allowed_when_cron_secret_empty(self, mock_check, mock_settings, client):
        mock_settings.CRON_SECRET = ""
        mock_check.return_value = {"success": True}
        response = client.get("/cron/deadline-approaching")
        assert response.status_code == 200

    @patch("api.routes.cron.settings")
    @patch("api.routes.cron.check_all_deadlines")
    def test_cron_with_correct_secret_allowed(self, mock_check, mock_settings, client):
        mock_settings.CRON_SECRET = "secret123"
        mock_check.return_value = {"success": True}
        response = client.get(
            "/cron/deadline-approaching",
            headers={"X-Cron-Secret": "secret123"},
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    @patch("api.routes.cron.settings")
    def test_cron_with_wrong_secret_forbidden(self, mock_settings, client):
        mock_settings.CRON_SECRET = "secret123"
        response = client.get(
            "/cron/deadline-approaching",
            headers={"X-Cron-Secret": "wrong"},
        )
        assert response.status_code == 403
        assert "Forbidden" in response.json().get("detail", "")
