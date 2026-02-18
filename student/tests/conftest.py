"""Pytest configuration and shared fixtures for API tests."""
import warnings

import pytest
from fastapi.testclient import TestClient

# Suppress Supabase client deprecation warnings (timeout/verify params - internal to library)
warnings.filterwarnings(
    "ignore",
    message=r".*'timeout' parameter is deprecated.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*'verify' parameter is deprecated.*",
    category=DeprecationWarning,
)


def pytest_configure(config):
    """Register pytest filterwarnings for Supabase deprecations (pytest applies these first)."""
    config.addinivalue_line(
        "filterwarnings",
        "ignore:The 'timeout' parameter is deprecated. Please configure it in the http client instead.:DeprecationWarning",
    )
    config.addinivalue_line(
        "filterwarnings",
        "ignore:The 'verify' parameter is deprecated. Please configure it in the http client instead.:DeprecationWarning",
    )

from app import app
from api.dependencies import get_current_user

# Test user payloads (sub, email, role, username) for dependency override
ADMIN_USER = {"sub": "admin1", "email": "admin@test.com", "role": "admin", "username": "admin"}
MANAGER_USER = {"sub": "mgr1", "email": "manager@test.com", "role": "manager", "username": "manager"}
MENTOR_USER = {"sub": "mentor1", "email": "mentor@test.com", "role": "mentor", "username": "mentor"}
STUDENT_USER = {"sub": "stu1", "email": "student@test.com", "role": "student", "username": "student"}


@pytest.fixture
def client():
    """Plain TestClient; no auth override. Use for health and unauthenticated endpoints."""
    with TestClient(app) as c:
        yield c


def _override_user(user: dict):
    app.dependency_overrides[get_current_user] = lambda: user


def _clear_user_override():
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def admin_client(client):
    """Client with get_current_user overridden to admin. Use for admin-only routes."""
    _override_user(ADMIN_USER)
    try:
        yield client
    finally:
        _clear_user_override()


@pytest.fixture
def manager_client(client):
    """Client with get_current_user overridden to manager."""
    _override_user(MANAGER_USER)
    try:
        yield client
    finally:
        _clear_user_override()


@pytest.fixture
def mentor_client(client):
    """Client with get_current_user overridden to mentor."""
    _override_user(MENTOR_USER)
    try:
        yield client
    finally:
        _clear_user_override()


@pytest.fixture
def student_client(client):
    """Client with get_current_user overridden to student."""
    _override_user(STUDENT_USER)
    try:
        yield client
    finally:
        _clear_user_override()
