"""Tests for /admin/reports API endpoints (PDF/Excel)."""

import pytest
from unittest.mock import patch
from io import BytesIO


class TestReportProjectSummaryExcel:
    """GET /admin/reports/project-summary.xlsx."""

    @patch("api.routes.reports.project_summary_excel")
    def test_project_summary_excel_returns_file(self, mock_excel, admin_client):
        mock_excel.return_value = BytesIO(b"xlsx content")
        response = admin_client.get("/admin/reports/project-summary.xlsx")
        assert response.status_code == 200
        assert "spreadsheet" in response.headers.get("content-type", "").lower() or "xlsx" in response.headers.get("content-type", "")
        assert "project-summary.xlsx" in response.headers.get("content-disposition", "")

    @patch("api.routes.reports.project_summary_excel")
    def test_project_summary_excel_failure_500(self, mock_excel, admin_client):
        mock_excel.return_value = None
        response = admin_client.get("/admin/reports/project-summary.xlsx")
        assert response.status_code == 500

    def test_project_summary_excel_forbidden_without_admin(self, student_client):
        response = student_client.get("/admin/reports/project-summary.xlsx")
        assert response.status_code == 403


class TestReportProjectSummaryPdf:
    """GET /admin/reports/project-summary.pdf."""

    @patch("api.routes.reports.project_summary_pdf")
    def test_project_summary_pdf_returns_file(self, mock_pdf, admin_client):
        mock_pdf.return_value = BytesIO(b"pdf content")
        response = admin_client.get("/admin/reports/project-summary.pdf")
        assert response.status_code == 200
        assert "pdf" in response.headers.get("content-type", "").lower()
        assert "project-summary.pdf" in response.headers.get("content-disposition", "")

    @patch("api.routes.reports.project_summary_pdf")
    def test_project_summary_pdf_failure_500(self, mock_pdf, admin_client):
        mock_pdf.return_value = None
        response = admin_client.get("/admin/reports/project-summary.pdf")
        assert response.status_code == 500


class TestReportStudentProgressExcel:
    """GET /admin/reports/student-progress.xlsx."""

    @patch("api.routes.reports.student_progress_excel")
    def test_student_progress_excel_returns_file(self, mock_excel, admin_client):
        mock_excel.return_value = BytesIO(b"xlsx content")
        response = admin_client.get("/admin/reports/student-progress.xlsx")
        assert response.status_code == 200
        assert "student-progress.xlsx" in response.headers.get("content-disposition", "")

    @patch("api.routes.reports.student_progress_excel")
    def test_student_progress_excel_failure_500(self, mock_excel, admin_client):
        mock_excel.return_value = None
        response = admin_client.get("/admin/reports/student-progress.xlsx")
        assert response.status_code == 500
