"""
Pytest configuration for API tests.

Provides fixtures for testing FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """
    FastAPI test client.
    
    Uses TestClient which doesn't require running the server.
    Synchronous, perfect for testing.
    """
    # Create instance with context manager
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_simulation_request():
    """Sample valid simulation request."""
    return {
        "p": 0.6,
        "N": 50,
        "num_trials": 100,
        "algorithm": "numba"
    }


@pytest.fixture
def sample_sweep_request():
    """Sample valid parameter sweep request."""
    return {
        "p_min": 0.5,
        "p_max": 0.7,
        "p_steps": 11,
        "N": 50,
        "num_trials": 50,
        "algorithm": "numba",
        "estimate_pc": True
    }