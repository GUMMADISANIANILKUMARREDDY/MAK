"""Tests for /dashboard API endpoints."""

import pytest
from unittest.mock import patch


class TestDashboardAdminStats:
    """GET /dashboard/admin-stats."""

    @patch("api.routes.dashboard.get_admin_stats")
    def test_admin_stats_returns_data(self, mock_get, admin_client):
        mock_get.return_value = {"total_users": 10, "total_students": 5, "total_projects": 2}
        response = admin_client.get("/dashboard/admin-stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data

    def test_admin_stats_forbidden_for_student(self, student_client):
        response = student_client.get("/dashboard/admin-stats")
        assert response.status_code == 403


class TestDashboardManagerStats:
    """GET /dashboard/manager-stats."""

    @patch("api.routes.dashboard.get_manager_stats")
    def test_manager_stats_returns_data(self, mock_get, manager_client):
        mock_get.return_value = {"modules_by_status": {}, "tasks_pending_review": 0}
        response = manager_client.get("/dashboard/manager-stats")
        assert response.status_code == 200

    def test_manager_stats_forbidden_for_student(self, student_client):
        response = student_client.get("/dashboard/manager-stats")
        assert response.status_code == 403


class TestDashboardMentorStats:
    """GET /dashboard/mentor-stats."""

    @patch("api.routes.dashboard.get_mentor_stats")
    def test_mentor_stats_returns_data(self, mock_get, mentor_client):
        mock_get.return_value = {"tasks_pending_review": 3, "teams_count": 2}
        response = mentor_client.get("/dashboard/mentor-stats")
        assert response.status_code == 200

    def test_mentor_stats_forbidden_for_student(self, student_client):
        response = student_client.get("/dashboard/mentor-stats")
        assert response.status_code == 403


class TestDashboardStudentStats:
    """GET /dashboard/student-stats."""

    @patch("api.routes.dashboard.get_student_stats")
    def test_student_stats_returns_data(self, mock_get, student_client):
        mock_get.return_value = {"assigned": 5, "in_progress": 2, "review": 1, "completed": 10}
        response = student_client.get("/dashboard/student-stats")
        assert response.status_code == 200

    def test_student_stats_forbidden_for_admin(self, admin_client):
        # Admin can access admin-stats but student-stats is role-restricted to student
        response = admin_client.get("/dashboard/student-stats")
        assert response.status_code == 403
