"""Tests for /admin/colleges API endpoints."""

import pytest
from unittest.mock import patch


class TestAdminCollegesList:
    """GET /admin/colleges."""

    @patch("api.routes.admin_colleges.get_all_colleges")
    def test_list_colleges_returns_data(self, mock_get, admin_client):
        mock_get.return_value = {"colleges": []}
        response = admin_client.get("/admin/colleges")
        assert response.status_code == 200
        data = response.json()
        assert "colleges" in data

    def test_list_colleges_forbidden_without_admin(self, student_client):
        response = student_client.get("/admin/colleges")
        assert response.status_code == 403


class TestAdminCollegesCreate:
    """POST /admin/colleges."""

    @patch("api.routes.admin_colleges.create_college")
    def test_create_college_success(self, mock_create, admin_client):
        mock_create.return_value = {"success": True, "collegeid": "c1"}
        response = admin_client.post(
            "/admin/colleges",
            json={"name": "Test College", "code": "TC"},
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    @patch("api.routes.admin_colleges.create_college")
    def test_create_college_failure_400(self, mock_create, admin_client):
        mock_create.return_value = {"success": False, "message": "Name exists"}
        response = admin_client.post(
            "/admin/colleges",
            json={"name": "Dup", "code": "D"},
        )
        assert response.status_code == 400
