"""Tests for /manager API endpoints (modules, projects)."""

import pytest
from unittest.mock import patch


class TestManagerMyProjects:
    """GET /manager/my-projects."""

    @patch("api.routes.manager_modules.get_manager_projects")
    def test_my_projects_returns_list(self, mock_get, manager_client):
        mock_get.return_value = {"projects": []}
        response = manager_client.get("/manager/my-projects")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data

    def test_my_projects_forbidden_for_student(self, student_client):
        response = student_client.get("/manager/my-projects")
        assert response.status_code == 403


class TestManagerListModules:
    """GET /manager/projects/{projectid}/modules."""

    @patch("api.routes.manager_modules.get_project_modules")
    def test_list_modules_returns_paginated(self, mock_get, admin_client):
        mock_get.return_value = {"data": [], "total": 0, "page": 1, "limit": 50}
        response = admin_client.get("/manager/projects/p1/modules")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    @patch("api.routes.manager_modules.get_project_modules")
    def test_list_modules_with_filters(self, mock_get, manager_client):
        mock_get.return_value = {"data": [], "total": 0, "page": 1, "limit": 50}
        response = manager_client.get(
            "/manager/projects/p1/modules",
            params={"search": "m1", "status": "active", "page": 1, "limit": 20},
        )
        assert response.status_code == 200


class TestManagerGetModule:
    """GET /manager/modules/{moduleid}."""

    @patch("api.routes.manager_modules.get_module_by_id")
    def test_get_module_success(self, mock_get, manager_client):
        mock_get.return_value = {"success": True, "module": {"moduleid": "m1", "title": "M1"}}
        response = manager_client.get("/manager/modules/m1")
        assert response.status_code == 200
        assert response.json().get("module", {}).get("moduleid") == "m1"

    @patch("api.routes.manager_modules.get_module_by_id")
    def test_get_module_not_found_404(self, mock_get, manager_client):
        mock_get.return_value = {"success": False, "message": "Module not found"}
        response = manager_client.get("/manager/modules/nonexistent")
        assert response.status_code == 404


class TestManagerCreateModule:
    """POST /manager/projects/{projectid}/modules/create."""

    @patch("api.routes.manager_modules.create_module")
    def test_create_module_success(self, mock_create, manager_client):
        mock_create.return_value = {"success": True, "moduleid": "m1"}
        response = manager_client.post(
            "/manager/projects/p1/modules/create",
            json={
                "title": "Module 1",
                "description": "Desc",
                "priority": "high",
                "due_date": "2025-06-01",
            },
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    @patch("api.routes.manager_modules.create_module")
    def test_create_module_failure_400(self, mock_create, manager_client):
        mock_create.return_value = {"success": False, "message": "Project not found"}
        response = manager_client.post(
            "/manager/projects/p1/modules/create",
            json={"title": "M1"},
        )
        assert response.status_code == 400

    def test_create_module_forbidden_for_mentor(self, mentor_client):
        response = mentor_client.post(
            "/manager/projects/p1/modules/create",
            json={"title": "M1"},
        )
        assert response.status_code == 403


class TestManagerUpdateModule:
    """PUT /manager/modules/{moduleid}."""

    @patch("api.routes.manager_modules.update_module")
    def test_update_module_success(self, mock_update, manager_client):
        mock_update.return_value = {"success": True}
        response = manager_client.put(
            "/manager/modules/m1",
            json={"title": "Updated", "status": "completed"},
        )
        assert response.status_code == 200

    @patch("api.routes.manager_modules.update_module")
    def test_update_module_failure_400(self, mock_update, manager_client):
        mock_update.return_value = {"success": False, "message": "Not found"}
        response = manager_client.put("/manager/modules/m1", json={"title": "x"})
        assert response.status_code == 400


class TestManagerDeleteModule:
    """DELETE /manager/modules/{moduleid}."""

    @patch("api.routes.manager_modules.delete_module")
    def test_delete_module_success(self, mock_delete, manager_client):
        mock_delete.return_value = {"success": True}
        response = manager_client.delete("/manager/modules/m1")
        assert response.status_code == 200

    @patch("api.routes.manager_modules.delete_module")
    def test_delete_module_not_found_404(self, mock_delete, manager_client):
        mock_delete.return_value = {"success": False, "message": "Not found"}
        response = manager_client.delete("/manager/modules/nonexistent")
        assert response.status_code == 404


class TestManagerAssignMentor:
    """POST /manager/modules/{moduleid}/assign-mentor."""

    @patch("api.routes.manager_modules.assign_module_to_mentor")
    def test_assign_mentor_success(self, mock_assign, manager_client):
        mock_assign.return_value = {"success": True}
        response = manager_client.post(
            "/manager/modules/m1/assign-mentor",
            json={"mentor_userid": "mentor1"},
        )
        assert response.status_code == 200

    @patch("api.routes.manager_modules.assign_module_to_mentor")
    def test_assign_mentor_failure_400(self, mock_assign, manager_client):
        mock_assign.return_value = {"success": False, "message": "Mentor not found"}
        response = manager_client.post(
            "/manager/modules/m1/assign-mentor",
            json={"mentor_userid": "unknown"},
        )
        assert response.status_code == 400


class TestManagerModuleMentors:
    """GET /manager/modules/{moduleid}/mentors."""

    @patch("api.routes.manager_modules.get_module_mentors")
    def test_list_module_mentors(self, mock_get, manager_client):
        mock_get.return_value = {"mentors": []}
        response = manager_client.get("/manager/modules/m1/mentors")
        assert response.status_code == 200
        assert "mentors" in response.json()
