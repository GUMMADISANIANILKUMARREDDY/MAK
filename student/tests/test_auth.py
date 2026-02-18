"""Tests for /auth API endpoints."""

import pytest
from unittest.mock import patch, MagicMock


class TestAuthRegister:
    """POST /auth/register."""

    def test_register_missing_userid_or_invalid_body_422(self, client):
        response = client.post("/auth/register", json={})
        assert response.status_code == 422

    @patch("api.routes.auth.register_student")
    def test_register_validation_error_400(self, mock_register, client):
        mock_register.return_value = {"success": False, "message": "Email already exists"}
        response = client.post(
            "/auth/register",
            json={
                "userid": "R001",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "9999999999",
                "email": "john@test.com",
                "password": "Pass@1234",
                "confirm_password": "Pass@1234",
            },
        )
        assert response.status_code == 400
        assert "Email already exists" in response.json().get("detail", "")

    @patch("api.routes.auth.register_student")
    def test_register_success_200(self, mock_register, client):
        mock_register.return_value = {"success": True, "message": "OTP sent"}
        response = client.post(
            "/auth/register",
            json={
                "userid": "R001",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "9999999999",
                "email": "john@test.com",
                "password": "Pass@1234",
                "confirm_password": "Pass@1234",
            },
        )
        assert response.status_code == 200
        assert response.json().get("success") is True


class TestAuthVerifyEmail:
    """POST /auth/verify-email."""

    def test_verify_email_invalid_body_422(self, client):
        response = client.post("/auth/verify-email", json={})
        assert response.status_code == 422

    @patch("api.routes.auth.verify_email_otp")
    def test_verify_email_failure_400(self, mock_verify, client):
        mock_verify.return_value = {"success": False, "message": "Invalid OTP"}
        response = client.post("/auth/verify-email", json={"email": "j@test.com", "otp": "000000"})
        assert response.status_code == 400


class TestAuthLogin:
    """POST /auth/login."""

    def test_login_no_userid_no_email_400(self, client):
        response = client.post("/auth/login", json={"password": "Pass@1234"})
        assert response.status_code == 400
        assert "userid or email" in response.json().get("detail", "").lower()

    @patch("api.routes.auth.rate_limit_auth", return_value=None)
    @patch("api.routes.auth.login_user")
    def test_login_invalid_credentials_401(self, mock_login, mock_rate, client):
        mock_login.return_value = None
        response = client.post(
            "/auth/login",
            json={"userid": "u1", "password": "wrong"},
        )
        assert response.status_code == 401

    @patch("api.routes.auth.rate_limit_auth", return_value=None)
    @patch("api.routes.auth.login_user")
    @patch("api.routes.auth.create_access_token")
    @patch("api.routes.auth.create_refresh_token")
    def test_login_success_200(
        self, mock_refresh, mock_access, mock_login, mock_rate, client
    ):
        mock_login.return_value = {
            "userid": "u1",
            "email": "u@test.com",
            "role": "student",
            "username": "u1",
            "active": True,
        }
        mock_access.return_value = "access.token"
        mock_refresh.return_value = "refresh.token"
        response = client.post(
            "/auth/login",
            json={"userid": "u1", "password": "Pass@1234"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("access_token") == "access.token"
        assert data.get("refresh_token") == "refresh.token"
        assert data.get("user", {}).get("userid") == "u1"


class TestAuthResendOtp:
    """POST /auth/resend-otp."""

    @patch("api.routes.auth.rate_limit_auth", return_value=None)
    @patch("api.routes.auth.resend_otp")
    def test_resend_otp_success(self, mock_resend, mock_rate, client):
        mock_resend.return_value = {"success": True}
        response = client.post("/auth/resend-otp", json={"email": "j@test.com"})
        assert response.status_code == 200


class TestAuthChangePassword:
    """POST /auth/change-password (requires auth)."""

    @patch("api.routes.auth.change_password")
    def test_change_password_success(self, mock_change, admin_client):
        mock_change.return_value = {"success": True}
        response = admin_client.post(
            "/auth/change-password",
            json={"current_password": "Old@1234", "new_password": "New@5678"},
        )
        assert response.status_code == 200

    def test_change_password_unauthorized_without_token(self, client):
        response = client.post(
            "/auth/change-password",
            json={"current_password": "Old@1234", "new_password": "New@5678"},
        )
        assert response.status_code == 401  # No Bearer token


class TestAuthForgotPassword:
    """POST /auth/forgot-password."""

    @patch("api.routes.auth.rate_limit_auth", return_value=None)
    @patch("api.routes.auth.forgot_password")
    def test_forgot_password_success(self, mock_forgot, mock_rate, client):
        mock_forgot.return_value = {"success": True}
        response = client.post("/auth/forgot-password", json={"email": "j@test.com"})
        assert response.status_code == 200


class TestAuthResetPassword:
    """POST /auth/reset-password."""

    @patch("api.routes.auth.rate_limit_auth", return_value=None)
    @patch("api.routes.auth.reset_password")
    def test_reset_password_success(self, mock_reset, mock_rate, client):
        mock_reset.return_value = {"success": True}
        response = client.post(
            "/auth/reset-password",
            json={"email": "j@test.com", "otp": "123456", "new_password": "New@5678"},
        )
        assert response.status_code == 200


class TestAuthRefresh:
    """POST /auth/refresh."""

    @patch("api.routes.auth.verify_refresh_token")
    def test_refresh_invalid_token_401(self, mock_verify, client):
        mock_verify.return_value = None
        response = client.post("/auth/refresh", json={"refresh_token": "invalid"})
        assert response.status_code == 401

    @patch("api.routes.auth.verify_refresh_token")
    @patch("api.routes.auth.create_access_token")
    @patch("api.routes.auth.create_refresh_token")
    def test_refresh_success_200(self, mock_refresh, mock_access, mock_verify, client):
        mock_verify.return_value = {
            "userid": "u1",
            "email": "u@test.com",
            "role": "student",
            "username": "u1",
            "active": True,
        }
        mock_access.return_value = "new.access"
        mock_refresh.return_value = "new.refresh"
        response = client.post("/auth/refresh", json={"refresh_token": "valid"})
        assert response.status_code == 200
        assert response.json().get("access_token") == "new.access"


class TestAuthMe:
    """GET /auth/me."""

    def test_me_returns_current_user(self, admin_client):
        response = admin_client.get("/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get("userid") == "admin1"
        assert data.get("role") == "admin"

    def test_me_unauthorized_without_token(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401


class TestAuthAdminOnly:
    """GET /auth/admin-only."""

    def test_admin_only_ok_for_admin(self, admin_client):
        response = admin_client.get("/auth/admin-only")
        assert response.status_code == 200

    def test_admin_only_forbidden_for_student(self, student_client):
        response = student_client.get("/auth/admin-only")
        assert response.status_code == 403


class TestAuthAdminAddUser:
    """POST /auth/admin/add-user."""

    def test_admin_add_user_invalid_role_400(self, admin_client):
        response = admin_client.post(
            "/auth/admin/add-user",
            json={
                "userid": "u2",
                "username": "u2",
                "email": "u2@test.com",
                "password": "Pass@1234",
                "role": "invalid_role",
                "active": True,
            },
        )
        assert response.status_code == 400

    @patch("api.routes.auth.admin_add_user")
    def test_admin_add_user_success(self, mock_add, admin_client):
        mock_add.return_value = {"success": True}
        response = admin_client.post(
            "/auth/admin/add-user",
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
