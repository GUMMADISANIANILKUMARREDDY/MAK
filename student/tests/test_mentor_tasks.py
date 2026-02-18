"""Tests for /mentor API endpoints (tasks, teams, assignments, comments)."""

import pytest
from unittest.mock import patch
from io import BytesIO


class TestMentorMyModules:
    """GET /mentor/my-modules."""

    @patch("api.routes.mentor_tasks.get_mentor_modules")
    def test_my_modules_returns_list(self, mock_get, mentor_client):
        mock_get.return_value = {"modules": []}
        response = mentor_client.get("/mentor/my-modules")
        assert response.status_code == 200
        data = response.json()
        assert "modules" in data

    def test_my_modules_forbidden_for_student(self, student_client):
        response = student_client.get("/mentor/my-modules")
        assert response.status_code == 403


class TestMentorTeams:
    """Teams CRUD."""

    @patch("api.routes.mentor_tasks.create_team")
    def test_create_team_success(self, mock_create, mentor_client):
        mock_create.return_value = {"success": True, "teamid": "t1"}
        response = mentor_client.post(
            "/mentor/teams/create",
            json={"team_name": "Team A"},
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    @patch("api.routes.mentor_tasks.get_mentor_teams")
    def test_list_teams(self, mock_get, mentor_client):
        mock_get.return_value = {"teams": []}
        response = mentor_client.get("/mentor/teams")
        assert response.status_code == 200

    @patch("api.routes.mentor_tasks.add_student_to_team")
    def test_add_student_to_team_success(self, mock_add, mentor_client):
        mock_add.return_value = {"success": True}
        response = mentor_client.post(
            "/mentor/teams/t1/add-student",
            json={"student_userid": "stu1"},
        )
        assert response.status_code == 200

    @patch("api.routes.mentor_tasks.get_team_members")
    def test_list_team_members(self, mock_get, mentor_client):
        mock_get.return_value = {"members": []}
        response = mentor_client.get("/mentor/teams/t1/members")
        assert response.status_code == 200

    @patch("api.routes.mentor_tasks.remove_student_from_team")
    def test_remove_student_from_team(self, mock_remove, mentor_client):
        mock_remove.return_value = {"success": True}
        response = mentor_client.delete("/mentor/teams/t1/remove-student/stu1")
        assert response.status_code == 200

    @patch("api.routes.mentor_tasks.delete_team")
    def test_delete_team(self, mock_delete, mentor_client):
        mock_delete.return_value = {"success": True}
        response = mentor_client.delete("/mentor/teams/t1")
        assert response.status_code == 200


class TestMentorTasks:
    """Tasks CRUD and assignments."""

    @patch("api.routes.mentor_tasks.get_module_tasks")
    def test_list_tasks(self, mock_get, mentor_client):
        mock_get.return_value = {"data": [], "total": 0, "page": 1, "limit": 50}
        response = mentor_client.get("/mentor/modules/m1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    @patch("api.routes.mentor_tasks.get_task_by_id")
    def test_get_task_success(self, mock_get, mentor_client):
        mock_get.return_value = {"success": True, "task": {"taskid": "tk1"}}
        response = mentor_client.get("/mentor/tasks/tk1")
        assert response.status_code == 200

    @patch("api.routes.mentor_tasks.get_task_by_id")
    def test_get_task_not_found_404(self, mock_get, mentor_client):
        mock_get.return_value = {"success": False, "message": "Not found"}
        response = mentor_client.get("/mentor/tasks/nonexistent")
        assert response.status_code == 404

    @patch("api.routes.mentor_tasks.create_task")
    def test_create_task_success(self, mock_create, mentor_client):
        mock_create.return_value = {"success": True, "taskid": "tk1"}
        response = mentor_client.post(
            "/mentor/modules/m1/tasks/create",
            json={
                "title": "Task 1",
                "description": "Desc",
                "task_type": "task",
                "priority": "high",
                "due_date": "2025-06-01",
            },
        )
        assert response.status_code == 200
        assert response.json().get("success") is True

    @patch("api.routes.mentor_tasks.update_task")
    def test_update_task_success(self, mock_update, mentor_client):
        mock_update.return_value = {"success": True}
        response = mentor_client.put(
            "/mentor/tasks/tk1",
            json={"title": "Updated", "status": "completed"},
        )
        assert response.status_code == 200

    @patch("api.routes.mentor_tasks.delete_task")
    def test_delete_task(self, mock_delete, mentor_client):
        mock_delete.return_value = {"success": True}
        response = mentor_client.delete("/mentor/tasks/tk1")
        assert response.status_code == 200

    @patch("api.routes.mentor_tasks.assign_task_to_student")
    def test_assign_student_success(self, mock_assign, mentor_client):
        mock_assign.return_value = {"success": True}
        response = mentor_client.post(
            "/mentor/tasks/tk1/assign-student",
            json={"student_userid": "stu1"},
        )
        assert response.status_code == 200

    @patch("api.routes.mentor_tasks.assign_task_bulk")
    def test_bulk_assign_students(self, mock_bulk, mentor_client):
        mock_bulk.return_value = {"success": True, "assigned": 2}
        response = mentor_client.post(
            "/mentor/tasks/tk1/bulk-assign",
            json={"student_userids": ["stu1", "stu2"]},
        )
        assert response.status_code == 200

    @patch("api.routes.mentor_tasks.get_task_assignments")
    def test_list_task_assignments(self, mock_get, mentor_client):
        mock_get.return_value = {"assignments": []}
        response = mentor_client.get("/mentor/tasks/tk1/assignments")
        assert response.status_code == 200


class TestMentorSubmissionAndReview:
    """Submission download and review."""

    @patch("api.routes.mentor_tasks.assignment_accessible_by_mentor")
    @patch("api.routes.mentor_tasks.get_submission_download_url")
    def test_get_submission_url_success(self, mock_url, mock_access, mentor_client):
        mock_access.return_value = True
        mock_url.return_value = {"url": "https://example.com/file"}
        response = mentor_client.get("/mentor/tasks/assignments/a1/submission")
        assert response.status_code == 200
        assert "url" in response.json()

    @patch("api.routes.mentor_tasks.assignment_accessible_by_mentor")
    def test_get_submission_url_forbidden_404(self, mock_access, mentor_client):
        mock_access.return_value = False
        response = mentor_client.get("/mentor/tasks/assignments/a1/submission")
        assert response.status_code == 404

    @patch("api.routes.mentor_tasks.assignment_accessible_by_mentor")
    @patch("api.routes.mentor_tasks.upload_review_file")
    def test_upload_review_file_success(self, mock_upload, mock_access, mentor_client):
        mock_access.return_value = True
        mock_upload.return_value = "https://storage/review.pdf"
        response = mentor_client.post(
            "/mentor/tasks/assignments/a1/review-file",
            files={"file": ("review.pdf", BytesIO(b"pdf content"), "application/pdf")},
        )
        assert response.status_code == 200
        assert response.json().get("review_file_url") is not None

    @patch("api.routes.mentor_tasks.assignment_accessible_by_mentor")
    def test_upload_review_file_forbidden_404(self, mock_access, mentor_client):
        mock_access.return_value = False
        response = mentor_client.post(
            "/mentor/tasks/assignments/a1/review-file",
            files={"file": ("r.pdf", BytesIO(b"x"), "application/pdf")},
        )
        assert response.status_code == 404

    @patch("api.routes.mentor_tasks.review_task")
    @patch("api.routes.mentor_tasks.assignment_accessible_by_mentor", return_value=True)
    def test_review_assignment_success(self, mock_access, mock_review, mentor_client):
        mock_review.return_value = {"success": True}
        response = mentor_client.post(
            "/mentor/tasks/assignments/a1/review",
            json={"result": "approved", "feedback": "Good", "score": 90},
        )
        assert response.status_code == 200


class TestMentorComments:
    """Assignment comments."""

    @patch("api.routes.mentor_tasks.assignment_accessible_by_mentor")
    @patch("api.routes.mentor_tasks.list_comments")
    def test_get_assignment_comments(self, mock_list, mock_access, mentor_client):
        mock_access.return_value = True
        mock_list.return_value = {"comments": []}
        response = mentor_client.get("/mentor/tasks/assignments/a1/comments")
        assert response.status_code == 200

    @patch("api.routes.mentor_tasks.assignment_accessible_by_mentor")
    def test_get_assignment_comments_forbidden_404(self, mock_access, mentor_client):
        mock_access.return_value = False
        response = mentor_client.get("/mentor/tasks/assignments/a1/comments")
        assert response.status_code == 404

    @patch("api.routes.mentor_tasks.assignment_accessible_by_mentor")
    @patch("api.routes.mentor_tasks.create_comment")
    def test_add_assignment_comment_success(self, mock_create, mock_access, mentor_client):
        mock_access.return_value = True
        mock_create.return_value = {"success": True, "comment_id": "c1"}
        response = mentor_client.post(
            "/mentor/tasks/assignments/a1/comments",
            json={"comment": "Well done"},
        )
        assert response.status_code == 200

    @patch("api.routes.mentor_tasks.delete_comment")
    def test_delete_comment_success(self, mock_delete, mentor_client):
        mock_delete.return_value = {"success": True}
        response = mentor_client.delete("/mentor/tasks/comments/c1")
        assert response.status_code == 200

    @patch("api.routes.mentor_tasks.delete_comment")
    def test_delete_comment_not_found_404(self, mock_delete, mentor_client):
        mock_delete.return_value = {"success": False, "message": "Not found"}
        response = mentor_client.delete("/mentor/tasks/comments/nonexistent")
        assert response.status_code == 404
