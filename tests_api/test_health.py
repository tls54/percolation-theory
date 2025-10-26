import pytest


class TestHealthEndpoint:
    """Test health check endpoint."""
    def test_health_check_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_structure(self, client):
        """Health check should return correct structure."""
        response = client.get("/health")
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "version" in data
        assert "cpp_available" in data
        assert "numba_available" in data

    def test_health_check_status_healthy(self, client):
        """Health check should report healthy status."""
        response = client.get("/health")
        data = response.json()
        
        assert data["status"] == "healthy"

    def test_health_check_reports_capabilities(self, client):
        """Health check should report available optimizations."""
        response = client.get("/health")
        data = response.json()
        
        # Should be boolean values
        assert isinstance(data["cpp_available"], bool)
        assert isinstance(data["numba_available"], bool)
        
        # Numba should be available (it's in requirements)
        assert data["numba_available"] is True


class TestRootEndpoint:
    """Test root endpoint."""
    def test_root_returns_200(self, client):
        """Root endpoint should return 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_info(self, client):
        """Root endpoint should return API information."""
        response = client.get("/")
        data = response.json()
        
        assert "name" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data