"""Tests for export API endpoints (CSV)."""

import pytest
from unittest.mock import patch


class TestExportStudents:
    """GET /admin/export/students."""

    @patch("api.routes.export_routes.stream_students_csv")
    def test_export_students_returns_csv(self, mock_stream, admin_client):
        def gen():
            yield b"userid,email\n"
            yield b"s1,s1@test.com\n"
        mock_stream.return_value = gen()
        response = admin_client.get("/admin/export/students")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "students.csv" in response.headers.get("content-disposition", "")

    def test_export_students_forbidden_without_admin(self, student_client):
        response = student_client.get("/admin/export/students")
        assert response.status_code == 403


class TestExportProjects:
    """GET /admin/export/projects."""

    @patch("api.routes.export_routes.stream_projects_csv")
    def test_export_projects_returns_csv(self, mock_stream, admin_client):
        def gen():
            yield b"projectid,title\n"
        mock_stream.return_value = gen()
        response = admin_client.get("/admin/export/projects")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "projects.csv" in response.headers.get("content-disposition", "")


class TestExportMentorTasks:
    """GET /mentor/export/tasks."""

    @patch("api.routes.export_routes.stream_mentor_tasks_csv")
    def test_export_mentor_tasks_returns_csv(self, mock_stream, mentor_client):
        def gen():
            yield b"taskid,title\n"
        mock_stream.return_value = gen()
        response = mentor_client.get("/mentor/export/tasks")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "mentor-tasks.csv" in response.headers.get("content-disposition", "")

    def test_export_mentor_tasks_forbidden_for_student(self, student_client):
        response = student_client.get("/mentor/export/tasks")
        assert response.status_code == 403
