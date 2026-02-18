"""Tests for /admin/projects API endpoints."""

import pytest
from unittest.mock import patch


class TestAdminProjectsList:
    """GET /admin/projects/."""

    @patch("api.routes.admin_projects.get_all_projects")
    def test_list_projects_returns_paginated(self, mock_get, admin_client):
        mock_get.return_value = {"data": [], "total": 0, "page": 1, "limit": 20}
        response = admin_client.get("/admin/projects/")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    @patch("api.routes.admin_projects.get_all_projects")
    def test_list_projects_with_filters(self, mock_get, admin_client):
        mock_get.return_value = {"data": [], "total": 0, "page": 1, "limit": 20}
        response = admin_client.get(
            "/admin/projects/",
            params={"status": "active", "search": "test", "page": 1, "limit": 10},
        )
        assert response.status_code == 200

    def test_list_projects_forbidden_without_admin(self, student_client):
        response = student_client.get("/admin/projects/")
        assert response.status_code == 403


class TestAdminProjectsGetOne:
    """GET /admin/projects/{projectid}."""

    @patch("api.routes.admin_projects.get_project_by_id")
    def test_get_project_success(self, mock_get, admin_client):
        mock_get.return_value = {
            "success": True,
            "project": {"projectid": "p1", "title": "Proj 1"},
        }
        response = admin_client.get("/admin/projects/p1")
        assert response.status_code == 200
        assert response.json().get("project", {}).get("projectid") == "p1"

    @patch("api.routes.admin_projects.get_project_by_id")
    def test_get_project_not_found_404(self, mock_get, admin_client):
        mock_get.return_value = {"success": False, "message": "Project not found"}
        response = admin_client.get("/admin/projects/nonexistent")
        assert response.status_code == 404

    @patch("api.routes.admin_projects.get_project_by_id")
    def test_get_project_allowed_for_manager(self, mock_get, manager_client):
        mock_get.return_value = {"success": True, "project": {"projectid": "p1"}}
        response = manager_client.get("/admin/projects/p1")
        assert response.status_code == 200


class TestAdminProjectsCreate:
    """POST /admin/projects/create."""

    @patch("api.routes.admin_projects.create_project")
    def test_create_project_success(self, mock_create, admin_client):
        mock_create.return_value = {"success": True, "projectid": "p1"}
        response = admin_client.post(
            "/admin/projects/create",
            json={
                "title": "New Project",
                "description": "Desc",
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
            },
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    @patch("api.routes.admin_projects.create_project")
    def test_create_project_failure_400(self, mock_create, admin_client):
        mock_create.return_value = {"success": False, "message": "Invalid dates"}
        response = admin_client.post(
            "/admin/projects/create",
            json={"title": "P", "description": "D"},
        )
        assert response.status_code == 400


class TestAdminProjectsUpdate:
    """PUT /admin/projects/{projectid}."""

    @patch("api.routes.admin_projects.update_project")
    def test_update_project_success(self, mock_update, admin_client):
        mock_update.return_value = {"success": True}
        response = admin_client.put(
            "/admin/projects/p1",
            json={"title": "Updated Title", "status": "active"},
        )
        assert response.status_code == 200

    @patch("api.routes.admin_projects.update_project")
    def test_update_project_failure_400(self, mock_update, admin_client):
        mock_update.return_value = {"success": False, "message": "Not found"}
        response = admin_client.put("/admin/projects/p1", json={"title": "x"})
        assert response.status_code == 400


class TestAdminProjectsDelete:
    """DELETE /admin/projects/{projectid}."""

    @patch("api.routes.admin_projects.delete_project")
    def test_delete_project_success(self, mock_delete, admin_client):
        mock_delete.return_value = {"success": True}
        response = admin_client.delete("/admin/projects/p1")
        assert response.status_code == 200

    @patch("api.routes.admin_projects.delete_project")
    def test_delete_project_not_found_404(self, mock_delete, admin_client):
        mock_delete.return_value = {"success": False, "message": "Not found"}
        response = admin_client.delete("/admin/projects/nonexistent")
        assert response.status_code == 404


class TestAdminProjectsAssignManager:
    """POST /admin/projects/{projectid}/assign-manager."""

    @patch("api.routes.admin_projects.assign_project_to_manager")
    def test_assign_manager_success(self, mock_assign, admin_client):
        mock_assign.return_value = {"success": True}
        response = admin_client.post(
            "/admin/projects/p1/assign-manager",
            json={"manager_userid": "mgr1"},
        )
        assert response.status_code == 200

    @patch("api.routes.admin_projects.assign_project_to_manager")
    def test_assign_manager_failure_400(self, mock_assign, admin_client):
        mock_assign.return_value = {"success": False, "message": "Manager not found"}
        response = admin_client.post(
            "/admin/projects/p1/assign-manager",
            json={"manager_userid": "unknown"},
        )
        assert response.status_code == 400


class TestAdminProjectsManagers:
    """GET /admin/projects/{projectid}/managers."""

    @patch("api.routes.admin_projects.get_project_managers")
    def test_list_project_managers(self, mock_get, admin_client):
        mock_get.return_value = {"managers": []}
        response = admin_client.get("/admin/projects/p1/managers")
        assert response.status_code == 200
        assert "managers" in response.json()
