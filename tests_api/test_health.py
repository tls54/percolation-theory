"""Tests for health check endpoint."""

import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    """Test the health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_returns_200(self, client: AsyncClient):
        """Health check should return 200."""
        response = await client.get("/api/health")  # Changed from /health
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_check_structure(self, client: AsyncClient):
        """Health check should return expected structure."""
        response = await client.get("/api/health")  # Changed
        data = response.json()

        # Should have these keys
        assert "status" in data
        assert "version" in data
        assert "cpp_available" in data
        assert "numba_available" in data

    @pytest.mark.asyncio
    async def test_health_check_status_healthy(self, client: AsyncClient):
        """Health check status should be 'healthy'."""
        response = await client.get("/api/health")  # Changed
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_reports_capabilities(self, client: AsyncClient):
        """Health check should report algorithm capabilities."""
        response = await client.get("/api/health")  # Changed
        data = response.json()

        # Should report boolean flags
        assert isinstance(data["cpp_available"], bool)
        assert isinstance(data["numba_available"], bool)


class TestRootEndpoint:
    """Test the root endpoint."""

    @pytest.mark.asyncio
    async def test_root_returns_200(self, client: AsyncClient):
        """Root endpoint should return 200."""
        response = await client.get("/")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_root_returns_info(self, client: AsyncClient):
        """Root endpoint should return API information."""
        response = await client.get("/")
        data = response.json()

        # Check for expected keys (based on actual api/main.py)
        assert "message" in data  # Changed from "name"
        assert "version" in data
        assert "docs" in data