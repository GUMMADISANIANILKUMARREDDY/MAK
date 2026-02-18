"""Tests for /student API endpoints (my-tasks, submit, comments)."""

import pytest
from unittest.mock import patch
from io import BytesIO


class TestStudentMyTasks:
    """GET /student/my-tasks."""

    @patch("api.routes.student_tasks.get_student_tasks")
    def test_my_tasks_returns_paginated(self, mock_get, student_client):
        mock_get.return_value = {"data": [], "total": 0, "page": 1, "limit": 50}
        response = student_client.get("/student/my-tasks")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    @patch("api.routes.student_tasks.get_student_tasks")
    def test_my_tasks_with_filters(self, mock_get, student_client):
        mock_get.return_value = {"data": [], "total": 0, "page": 1, "limit": 50}
        response = student_client.get(
            "/student/my-tasks",
            params={"status": "assigned", "search": "task", "page": 1, "limit": 20},
        )
        assert response.status_code == 200

    def test_my_tasks_forbidden_for_mentor(self, mentor_client):
        response = mentor_client.get("/student/my-tasks")
        assert response.status_code == 403


class TestStudentGetTask:
    """GET /student/tasks/{taskid}."""

    @patch("api.routes.student_tasks.get_task_by_id")
    def test_get_task_details_success(self, mock_get, student_client):
        mock_get.return_value = {"success": True, "task": {"taskid": "tk1"}}
        response = student_client.get("/student/tasks/tk1")
        assert response.status_code == 200
        assert response.json().get("task", {}).get("taskid") == "tk1"

    @patch("api.routes.student_tasks.get_task_by_id")
    def test_get_task_not_found_404(self, mock_get, student_client):
        mock_get.return_value = {"success": False, "message": "Not found"}
        response = student_client.get("/student/tasks/nonexistent")
        assert response.status_code == 404


class TestStudentUpdateStatus:
    """PUT /student/tasks/{assignment_id}/update-status."""

    @patch("api.routes.student_tasks.update_task_assignment_status")
    def test_update_status_success(self, mock_update, student_client):
        mock_update.return_value = {"success": True}
        response = student_client.put(
            "/student/tasks/a1/update-status",
            json={"status": "in_progress"},
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    @patch("api.routes.student_tasks.update_task_assignment_status")
    def test_update_status_failure_400(self, mock_update, student_client):
        mock_update.return_value = {"success": False, "message": "Invalid status"}
        response = student_client.put(
            "/student/tasks/a1/update-status",
            json={"status": "invalid"},
        )
        assert response.status_code == 400


class TestStudentSubmitTask:
    """POST /student/tasks/{assignment_id}/submit."""

    @patch("api.routes.student_tasks.submit_task")
    def test_submit_task_with_notes_only_success(self, mock_submit, student_client):
        mock_submit.return_value = {"success": True}
        response = student_client.post(
            "/student/tasks/a1/submit",
            data={"notes": "Done"},
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    @patch("api.routes.student_tasks.upload_submission_file")
    @patch("api.routes.student_tasks.submit_task")
    def test_submit_task_with_file_success(self, mock_submit, mock_upload, student_client):
        mock_upload.return_value = ("https://storage/file", "path/file")
        mock_submit.return_value = {"success": True}
        response = student_client.post(
            "/student/tasks/a1/submit",
            data={"notes": "See attachment"},
            files={"file": ("doc.pdf", BytesIO(b"content"), "application/pdf")},
        )
        assert response.status_code == 200


class TestStudentComments:
    """Comments on assignments."""

    @patch("api.routes.student_tasks.assignment_accessible_by_student")
    @patch("api.routes.student_tasks.list_comments")
    def test_get_assignment_comments(self, mock_list, mock_access, student_client):
        mock_access.return_value = True
        mock_list.return_value = {"comments": []}
        response = student_client.get("/student/tasks/assignments/a1/comments")
        assert response.status_code == 200

    @patch("api.routes.student_tasks.assignment_accessible_by_student")
    def test_get_assignment_comments_forbidden_404(self, mock_access, student_client):
        mock_access.return_value = False
        response = student_client.get("/student/tasks/assignments/a1/comments")
        assert response.status_code == 404

    @patch("api.routes.student_tasks.assignment_accessible_by_student")
    @patch("api.routes.student_tasks.create_comment")
    def test_add_assignment_comment_success(self, mock_create, mock_access, student_client):
        mock_access.return_value = True
        mock_create.return_value = {"success": True, "comment_id": "c1"}
        response = student_client.post(
            "/student/tasks/assignments/a1/comments",
            json={"comment": "Question about deadline"},
        )
        assert response.status_code == 200

    @patch("api.routes.student_tasks.delete_comment")
    def test_delete_comment_success(self, mock_delete, student_client):
        mock_delete.return_value = {"success": True}
        response = student_client.delete("/student/tasks/comments/c1")
        assert response.status_code == 200

    @patch("api.routes.student_tasks.delete_comment")
    def test_delete_comment_not_found_404(self, mock_delete, student_client):
        mock_delete.return_value = {"success": False, "message": "Not found"}
        response = student_client.delete("/student/tasks/comments/nonexistent")
        assert response.status_code == 404
