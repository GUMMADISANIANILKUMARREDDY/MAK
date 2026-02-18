"""Tests for health and unauthenticated endpoints."""

import pytest


class TestHealth:
    """Health check endpoint."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        assert "InternHub" in data.get("service", "")
