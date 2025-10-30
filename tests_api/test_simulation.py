import pytest
from fastapi.testclient import TestClient


class TestSimulationEndpoint:
    """Test single simulation endpoint."""
    def test_simulate_returns_200(self, client, sample_simulation_request):
        """Simulate endpoint should return 200 for valid request."""
        response = client.post("/api/simulate", json=sample_simulation_request)
        assert response.status_code == 200

    def test_simulate_response_structure(self, client, sample_simulation_request):
        """Response should contain all required fields."""
        response = client.post("/api/simulate", json=sample_simulation_request)
        data = response.json()
        
        required_fields = [
            "p", "N", "num_trials",
            "percolation_probability",
            "num_percolating",
            "mean_num_clusters",
            "mean_cluster_size",
            "mean_spanning_size",
            "algorithm_used",
            "computation_time_ms"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_simulate_percolation_probability_range(self, client, sample_simulation_request):
        """Percolation probability should be between 0 and 1."""
        response = client.post("/api/simulate", json=sample_simulation_request)
        data = response.json()
        
        assert 0.0 <= data["percolation_probability"] <= 1.0

    def test_simulate_num_percolating_valid(self, client, sample_simulation_request):
        """Number percolating should be <= num_trials."""
        response = client.post("/api/simulate", json=sample_simulation_request)
        data = response.json()
        
        assert 0 <= data["num_percolating"] <= data["num_trials"]

    def test_simulate_computation_time_positive(self, client, sample_simulation_request):
        """Computation time should be positive."""
        response = client.post("/api/simulate", json=sample_simulation_request)
        data = response.json()
        
        assert data["computation_time_ms"] > 0

    def test_simulate_with_different_algorithms(self, client):
        """Should work with all algorithm types."""
        algorithms = ["bfs", "numba", "cpp"]
        
        for algo in algorithms:
            request = {
                "p": 0.6,
                "N": 30,
                "num_trials": 10,
                "algorithm": algo
            }
            
            response = client.post("/api/simulate", json=request)
            assert response.status_code == 200, f"Failed for algorithm: {algo}"
            
            data = response.json()
            # C++ might fallback to numba if not available
            assert data["algorithm_used"] in ["bfs", "numba", "cpp"]

    def test_simulate_at_critical_point(self, client):
        """Simulation near p_c should give ~50% percolation."""
        request = {
            "p": 0.5927,
            "N": 100,
            "num_trials": 200,
            "algorithm": "numba"
        }
        
        response = client.post("/api/simulate", json=request)
        data = response.json()
        
        # At p_c, should be around 0.5 (allow wide range due to randomness)
        assert 0.3 <= data["percolation_probability"] <= 0.7

class TestSimulateValidation:
    """Test input validation for simulate endpoint."""
    def test_simulate_p_too_high(self, client):
        """Should reject p > 1."""
        response = client.post("/api/simulate", json={
            "p": 1.5,
            "N": 50,
            "num_trials": 100,
            "algorithm": "numba"
        })
        assert response.status_code == 422

    def test_simulate_p_negative(self, client):
        """Should reject negative p."""
        response = client.post("/api/simulate", json={
            "p": -0.1,
            "N": 50,
            "num_trials": 100,
            "algorithm": "numba"
        })
        assert response.status_code == 422

    def test_simulate_N_too_large(self, client):
        """Should reject N > 500."""
        response = client.post("/api/simulate", json={
            "p": 0.6,
            "N": 1000,
            "num_trials": 100,
            "algorithm": "numba"
        })
        assert response.status_code == 422

    def test_simulate_N_too_small(self, client):
        """Should reject N < 10."""
        response = client.post("/api/simulate", json={
            "p": 0.6,
            "N": 5,
            "num_trials": 100,
            "algorithm": "numba"
        })
        assert response.status_code == 422

    def test_simulate_num_trials_zero(self, client):
        """Should reject num_trials = 0."""
        response = client.post("/api/simulate", json={
            "p": 0.6,
            "N": 50,
            "num_trials": 0,
            "algorithm": "numba"
        })
        assert response.status_code == 422

    def test_simulate_invalid_algorithm(self, client):
        """Should reject unknown algorithm."""
        response = client.post("/api/simulate", json={
            "p": 0.6,
            "N": 50,
            "num_trials": 100,
            "algorithm": "quantum_annealing"  # Not valid
        })
        assert response.status_code == 422

    def test_simulate_missing_required_field(self, client: TestClient):
        """Missing required field should return 422."""
        response = client.post(  # No await
            "/api/simulate",
            json={
                "N": 50,
                "num_trials": 100
                # Missing 'p' - required field
            }
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestParameterSweepEndpoint:
    """Test parameter sweep endpoint."""
    def test_sweep_returns_200(self, client, sample_sweep_request):
        """Sweep endpoint should return 200 for valid request."""
        response = client.post("/api/simulate/sweep", json=sample_sweep_request)
        assert response.status_code == 200

    def test_sweep_response_structure(self, client, sample_sweep_request):
        """Response should contain all required fields."""
        response = client.post("/api/simulate/sweep", json=sample_sweep_request)
        data = response.json()
        
        required_fields = [
            "p_values",
            "percolation_probabilities",
            "mean_cluster_counts",
            "mean_cluster_sizes",
            "N",
            "num_trials",
            "algorithm_used",
            "total_computation_time_s",
            "pc_estimate",
            "pc_stderr",
            "pc_error_percent"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_sweep_array_lengths_match(self, client, sample_sweep_request):
        """All result arrays should have same length."""
        response = client.post("/api/simulate/sweep", json=sample_sweep_request)
        data = response.json()
        
        p_len = len(data["p_values"])
        assert len(data["percolation_probabilities"]) == p_len
        assert len(data["mean_cluster_counts"]) == p_len
        assert len(data["mean_cluster_sizes"]) == p_len

    def test_sweep_correct_number_of_points(self, client, sample_sweep_request):
        """Should return requested number of p values."""
        response = client.post("/api/simulate/sweep", json=sample_sweep_request)
        data = response.json()
        
        assert len(data["p_values"]) == sample_sweep_request["p_steps"]

    def test_sweep_p_values_in_range(self, client, sample_sweep_request):
        """All p values should be within requested range."""
        response = client.post("/api/simulate/sweep", json=sample_sweep_request)
        data = response.json()
        
        p_min = sample_sweep_request["p_min"]
        p_max = sample_sweep_request["p_max"]
        
        for p in data["p_values"]:
            assert p_min <= p <= p_max

    def test_sweep_pc_estimation(self, client):
        """Should estimate p_c when requested."""
        request = {
            "p_min": 0.5,
            "p_max": 0.7,
            "p_steps": 21,
            "N": 50,
            "num_trials": 100,
            "algorithm": "numba",
            "estimate_pc": True
        }
        
        response = client.post("/api/simulate/sweep", json=request)
        data = response.json()
        
        # Should have p_c estimate
        assert data["pc_estimate"] is not None
        assert data["pc_stderr"] is not None
        assert data["pc_error_percent"] is not None
        
        # p_c should be reasonable
        assert 0.55 < data["pc_estimate"] < 0.65

    def test_sweep_without_pc_estimation(self, client):
        """Should work without p_c estimation."""
        request = {
            "p_min": 0.5,
            "p_max": 0.7,
            "p_steps": 11,
            "N": 50,
            "num_trials": 50,
            "algorithm": "numba",
            "estimate_pc": False
        }
        
        response = client.post("/api/simulate/sweep", json=request)
        data = response.json()
        
        # Should not have p_c estimate
        assert data["pc_estimate"] is None
        assert data["pc_stderr"] is None
        assert data["pc_error_percent"] is None

    @pytest.mark.slow
    def test_sweep_high_resolution(self, client):
        """Test sweep with many p values (slower)."""
        request = {
            "p_min": 0.55,
            "p_max": 0.65,
            "p_steps": 51,
            "N": 100,
            "num_trials": 100,
            "algorithm": "numba",
            "estimate_pc": True
        }
        
        response = client.post("/api/simulate/sweep", json=request)
        assert response.status_code == 200
        
        data = response.json()
        
        # High resolution should give accurate p_c
        if data["pc_estimate"]:
            assert abs(data["pc_estimate"] - 0.5927) < 0.01

class TestParameterSweepValidation:
    """Test input validation for parameter sweep."""
    def test_sweep_p_max_less_than_p_min(self, client):
        """Should reject p_max < p_min."""
        response = client.post("/api/simulate/sweep", json={
            "p_min": 0.7,
            "p_max": 0.5,
            "p_steps": 10,
            "N": 50,
            "num_trials": 100,
            "algorithm": "numba"
        })
        assert response.status_code == 422

    def test_sweep_too_few_steps(self, client):
        """Should reject p_steps < 5."""
        response = client.post("/api/simulate/sweep", json={
            "p_min": 0.5,
            "p_max": 0.7,
            "p_steps": 2,
            "N": 50,
            "num_trials": 100,
            "algorithm": "numba"
        })
        assert response.status_code == 422

    def test_sweep_too_many_steps(self, client):
        """Should reject p_steps > 101."""
        response = client.post("/api/simulate/sweep", json={
            "p_min": 0.5,
            "p_max": 0.7,
            "p_steps": 200,
            "N": 50,
            "num_trials": 100,
            "algorithm": "numba"
        })
        assert response.status_code == 422

class TestAPIDocumentation:
    """Test that API documentation is accessible."""
    def test_docs_accessible(self, client):
        """OpenAPI docs should be accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_accessible(self, client):
        """ReDoc documentation should be accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_json_accessible(self, client):
        """OpenAPI JSON schema should be accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        # Should be valid JSON
        data = response.json()
        assert "info" in data
        assert "paths" in data