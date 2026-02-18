"""Tests for /admin/permissions API endpoints."""

import pytest
from unittest.mock import patch


class TestAdminPermissionsList:
    """GET /admin/permissions."""

    @patch("api.routes.admin_permissions.get_all_permissions")
    def test_list_all_permissions(self, mock_get, admin_client):
        mock_get.return_value = {"permissions": []}
        response = admin_client.get("/admin/permissions")
        assert response.status_code == 200
        data = response.json()
        assert "permissions" in data

    def test_list_permissions_forbidden_without_admin(self, student_client):
        response = student_client.get("/admin/permissions")
        assert response.status_code == 403


class TestAdminPermissionsByRole:
    """GET /admin/permissions/role/{role}."""

    @patch("api.routes.admin_permissions.get_role_permissions")
    def test_list_role_permissions(self, mock_get, admin_client):
        mock_get.return_value = {"permissions": []}
        response = admin_client.get("/admin/permissions/role/admin")
        assert response.status_code == 200


class TestAdminPermissionsSet:
    """POST /admin/permissions."""

    @patch("api.routes.admin_permissions.set_permission")
    def test_set_permission_success(self, mock_set, admin_client):
        mock_set.return_value = {"success": True}
        response = admin_client.post(
            "/admin/permissions",
            json={
                "role": "mentor",
                "resource": "tasks",
                "action": "read",
                "grant": True,
            },
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    @patch("api.routes.admin_permissions.set_permission")
    def test_set_permission_failure_400(self, mock_set, admin_client):
        mock_set.return_value = {"success": False, "message": "Invalid role"}
        response = admin_client.post(
            "/admin/permissions",
            json={"role": "x", "resource": "y", "action": "z", "grant": True},
        )
        assert response.status_code == 400
