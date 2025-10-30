"""Tests for health check endpoint."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test the health check endpoint."""

    def test_health_check_returns_200(self, client: TestClient):
        """Health check should return 200."""
        response = client.get("/api/health")  # No await
        assert response.status_code == 200

    def test_health_check_structure(self, client: TestClient):
        """Health check should return expected structure."""
        response = client.get("/api/health")  # No await
        data = response.json()

        # Should have these keys
        assert "status" in data
        assert "version" in data
        assert "cpp_available" in data
        assert "numba_available" in data

    def test_health_check_status_healthy(self, client: TestClient):
        """Health check status should be 'healthy'."""
        response = client.get("/api/health")  # No await
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_reports_capabilities(self, client: TestClient):
        """Health check should report algorithm capabilities."""
        response = client.get("/api/health")  # No await
        data = response.json()

        # Should report boolean flags
        assert isinstance(data["cpp_available"], bool)
        assert isinstance(data["numba_available"], bool)


class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root_returns_200(self, client: TestClient):
        """Root endpoint should return 200."""
        response = client.get("/")  # No await
        assert response.status_code == 200

    def test_root_returns_info(self, client: TestClient):
        """Root endpoint should return API information."""
        response = client.get("/")  # No await
        data = response.json()

        # Check for expected keys (based on actual api/main.py)
        assert "message" in data
        assert "version" in data
        assert "docs" in data