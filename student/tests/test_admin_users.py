"""Tests for /admin/users API endpoints."""

import pytest
from unittest.mock import patch


class TestAdminUsersList:
    """GET /admin/users/."""

    @patch("api.routes.admin_users.get_all_users")
    def test_list_users_returns_paginated(self, mock_get, admin_client):
        mock_get.return_value = {"data": [], "total": 0, "page": 1, "limit": 20}
        response = admin_client.get("/admin/users/")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["total"] == 0

    @patch("api.routes.admin_users.get_all_users")
    def test_list_users_with_filters(self, mock_get, admin_client):
        mock_get.return_value = {"data": [], "total": 0, "page": 1, "limit": 20}
        response = admin_client.get(
            "/admin/users/",
            params={"role": "student", "page": 1, "limit": 10},
        )
        assert response.status_code == 200

    def test_list_users_forbidden_without_admin(self, student_client):
        response = student_client.get("/admin/users/")
        assert response.status_code == 403


class TestAdminUsersByRole:
    """GET /admin/users/role/{role}."""

    @patch("api.routes.admin_users.get_all_users")
    def test_list_users_by_role(self, mock_get, admin_client):
        mock_get.return_value = {"data": [], "total": 0, "page": 1, "limit": 20}
        response = admin_client.get("/admin/users/role/student")
        assert response.status_code == 200


class TestAdminUsersGetOne:
    """GET /admin/users/{userid}."""

    @patch("api.routes.admin_users.get_user_by_id")
    def test_get_user_success(self, mock_get, admin_client):
        mock_get.return_value = {
            "success": True,
            "user": {"userid": "u1", "username": "u1", "email": "u1@test.com", "role": "student"},
        }
        response = admin_client.get("/admin/users/u1")
        assert response.status_code == 200
        assert response.json().get("user", {}).get("userid") == "u1"

    @patch("api.routes.admin_users.get_user_by_id")
    def test_get_user_not_found_404(self, mock_get, admin_client):
        mock_get.return_value = {"success": False, "message": "User not found"}
        response = admin_client.get("/admin/users/nonexistent")
        assert response.status_code == 404


class TestAdminUsersCreateSingle:
    """POST /admin/users/single."""

    @patch("api.routes.admin_users.log_activity")
    @patch("api.routes.admin_users.create_user")
    def test_create_single_user_success(self, mock_create, mock_log, admin_client):
        mock_create.return_value = {"success": True, "userid": "u2"}
        response = admin_client.post(
            "/admin/users/single",
            json={
                "userid": "u2",
                "username": "u2",
                "email": "u2@test.com",
                "password": "Pass@1234",
                "role": "student",
                "active": True,
            },
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    @patch("api.routes.admin_users.create_user")
    def test_create_single_user_failure_400(self, mock_create, admin_client):
        mock_create.return_value = {"success": False, "message": "Userid exists"}
        response = admin_client.post(
            "/admin/users/single",
            json={
                "userid": "u2",
                "username": "u2",
                "email": "u2@test.com",
                "password": "Pass@1234",
                "role": "student",
                "active": True,
            },
        )
        assert response.status_code == 400


class TestAdminUsersCreateBulk:
    """POST /admin/users/bulk."""

    @patch("api.routes.admin_users.create_users_bulk")
    def test_create_bulk_users(self, mock_bulk, admin_client):
        mock_bulk.return_value = {"success": True, "created": 2}
        response = admin_client.post(
            "/admin/users/bulk",
            json={
                "users": [
                    {
                        "userid": "u1",
                        "username": "u1",
                        "email": "u1@test.com",
                        "password": "Pass@1234",
                        "role": "student",
                        "active": True,
                    },
                ],
            },
        )
        assert response.status_code == 200


class TestAdminUsersUpdate:
    """PUT /admin/users/{userid}."""

    @patch("api.routes.admin_users.log_activity")
    @patch("api.routes.admin_users.update_user")
    def test_update_user_success(self, mock_update, mock_log, admin_client):
        mock_update.return_value = {"success": True}
        response = admin_client.put(
            "/admin/users/u1",
            json={"username": "newname", "active": False},
        )
        assert response.status_code == 200

    @patch("api.routes.admin_users.update_user")
    def test_update_user_failure_400(self, mock_update, admin_client):
        mock_update.return_value = {"success": False, "message": "Not found"}
        response = admin_client.put("/admin/users/u1", json={"username": "x"})
        assert response.status_code == 400


class TestAdminUsersDelete:
    """DELETE /admin/users/{userid}."""

    @patch("api.routes.admin_users.log_activity")
    @patch("api.routes.admin_users.delete_user")
    def test_delete_user_success(self, mock_delete, mock_log_activity, admin_client):
        mock_delete.return_value = {"success": True}
        response = admin_client.delete("/admin/users/u1")
        assert response.status_code == 200

    @patch("api.routes.admin_users.log_activity")
    @patch("api.routes.admin_users.delete_user")
    def test_delete_user_with_soft_param(self, mock_delete, mock_log_activity, admin_client):
        mock_delete.return_value = {"success": True}
        response = admin_client.delete("/admin/users/u1", params={"soft": False})
        assert response.status_code == 200


class TestAdminUsersBulkDelete:
    """POST /admin/users/bulk-delete."""

    @patch("api.routes.admin_users.delete_users_bulk")
    def test_bulk_delete_users(self, mock_bulk, admin_client):
        mock_bulk.return_value = {"success": True, "deleted": 2}
        response = admin_client.post(
            "/admin/users/bulk-delete",
            json={"userids": ["u1", "u2"]},
            params={"soft": True},
        )
        assert response.status_code == 200
