"""Tests for /admin/students API endpoints."""

import pytest
from unittest.mock import patch


class TestAdminStudentsList:
    """GET /admin/students/."""

    @patch("api.routes.admin_students.get_all_students")
    def test_list_students_returns_paginated(self, mock_get, admin_client):
        mock_get.return_value = {"data": [], "total": 0, "page": 1, "limit": 20}
        response = admin_client.get("/admin/students/")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    @patch("api.routes.admin_students.get_all_students")
    def test_list_students_with_search(self, mock_get, admin_client):
        mock_get.return_value = {"data": [], "total": 0, "page": 1, "limit": 20}
        response = admin_client.get("/admin/students/", params={"search": "john"})
        assert response.status_code == 200

    def test_list_students_forbidden_without_admin(self, student_client):
        response = student_client.get("/admin/students/")
        assert response.status_code == 403


class TestAdminStudentsGetOne:
    """GET /admin/students/{userid}."""

    @patch("api.routes.admin_students.get_student_by_id")
    def test_get_student_success(self, mock_get, admin_client):
        mock_get.return_value = {
            "success": True,
            "student": {"userid": "s1", "first_name": "John", "last_name": "Doe"},
        }
        response = admin_client.get("/admin/students/s1")
        assert response.status_code == 200
        assert response.json().get("student", {}).get("userid") == "s1"

    @patch("api.routes.admin_students.get_student_by_id")
    def test_get_student_not_found_404(self, mock_get, admin_client):
        mock_get.return_value = {"success": False, "message": "Student not found"}
        response = admin_client.get("/admin/students/nonexistent")
        assert response.status_code == 404


class TestAdminStudentsCreateSingle:
    """POST /admin/students/single."""

    @patch("api.routes.admin_students.create_student")
    def test_create_single_student_success(self, mock_create, admin_client):
        mock_create.return_value = {"success": True, "userid": "s1"}
        response = admin_client.post(
            "/admin/students/single",
            json={
                "userid": "s1",
                "first_name": "Jane",
                "last_name": "Doe",
                "phone": "9999999999",
                "email": "jane@test.com",
            },
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    @patch("api.routes.admin_students.create_student")
    def test_create_single_student_failure_400(self, mock_create, admin_client):
        mock_create.return_value = {"success": False, "message": "User not found"}
        response = admin_client.post(
            "/admin/students/single",
            json={
                "userid": "s1",
                "first_name": "Jane",
                "last_name": "Doe",
                "phone": "9999999999",
                "email": "jane@test.com",
            },
        )
        assert response.status_code == 400


class TestAdminStudentsCreateBulk:
    """POST /admin/students/bulk."""

    @patch("api.routes.admin_students.create_students_bulk")
    def test_create_bulk_students(self, mock_bulk, admin_client):
        mock_bulk.return_value = {"success": True, "created": 1}
        response = admin_client.post(
            "/admin/students/bulk",
            json={
                "students": [
                    {
                        "userid": "s1",
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "phone": "9999999999",
                        "email": "jane@test.com",
                    },
                ],
            },
        )
        assert response.status_code == 200


class TestAdminStudentsUpdate:
    """PUT /admin/students/{userid}."""

    @patch("api.routes.admin_students.update_student")
    def test_update_student_success(self, mock_update, admin_client):
        mock_update.return_value = {"success": True}
        response = admin_client.put(
            "/admin/students/s1",
            json={"first_name": "Janet", "email": "janet@test.com"},
        )
        assert response.status_code == 200

    @patch("api.routes.admin_students.update_student")
    def test_update_student_failure_400(self, mock_update, admin_client):
        mock_update.return_value = {"success": False, "message": "Not found"}
        response = admin_client.put("/admin/students/s1", json={"first_name": "x"})
        assert response.status_code == 400


class TestAdminStudentsDelete:
    """DELETE /admin/students/{userid}."""

    @patch("api.routes.admin_students.delete_student")
    def test_delete_student_success(self, mock_delete, admin_client):
        mock_delete.return_value = {"success": True}
        response = admin_client.delete("/admin/students/s1")
        assert response.status_code == 200


class TestAdminStudentsBulkDelete:
    """POST /admin/students/bulk-delete."""

    @patch("api.routes.admin_students.delete_students_bulk")
    def test_bulk_delete_students(self, mock_bulk, admin_client):
        mock_bulk.return_value = {"success": True, "deleted": 2}
        response = admin_client.post(
            "/admin/students/bulk-delete",
            json={"userids": ["s1", "s2"]},
        )
        assert response.status_code == 200
