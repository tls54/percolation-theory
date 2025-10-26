from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class SimulationRequest(BaseModel):
    """Request model for single-point simulation."""
    
    p: float = Field(..., ge=0.0, le=1.0, description="Occupation probability")
    N: int = Field(50, ge=10, le=500, description="Grid size (N×N)")
    num_trials: int = Field(100, ge=1, le=1000, description="Number of trials")
    algorithm: Literal["bfs", "numba", "cpp"] = Field(
        "numba", 
        description="Search algorithm to use"
    )
    
    @field_validator("N")
    @classmethod
    def validate_N(cls, v):
        if v > 500:
            raise ValueError("N too large (max 500)")
        return v


class ParameterSweepRequest(BaseModel):
    """Request model for parameter sweep simulation."""
    
    p_min: float = Field(0.4, ge=0.0, le=1.0, description="Minimum p value")
    p_max: float = Field(0.7, ge=0.0, le=1.0, description="Maximum p value")
    p_steps: int = Field(31, ge=5, le=101, description="Number of p values")
    N: int = Field(50, ge=10, le=500, description="Grid size (N×N)")
    num_trials: int = Field(100, ge=1, le=1000, description="Number of trials per p")
    algorithm: Literal["bfs", "numba", "cpp"] = Field("numba", description="Search algorithm")
    estimate_pc: bool = Field(True, description="Estimate critical probability")
    
    @field_validator("p_max")
    @classmethod
    def validate_p_range(cls, v, info):
        if "p_min" in info.data and v <= info.data["p_min"]:
            raise ValueError("p_max must be greater than p_min")
        return v


class SimulationResult(BaseModel):
    """Response model for single-point simulation."""
    
    p: float
    N: int
    num_trials: int
    percolation_probability: float
    num_percolating: int
    mean_num_clusters: float
    mean_cluster_size: float
    mean_spanning_size: float
    algorithm_used: str
    computation_time_ms: float


class ParameterSweepResult(BaseModel):
    """Response model for parameter sweep."""
    
    p_values: list[float]
    percolation_probabilities: list[float]
    mean_cluster_counts: list[float]
    mean_cluster_sizes: list[float]
    N: int
    num_trials: int
    algorithm_used: str
    total_computation_time_s: float
    pc_estimate: Optional[float] = None
    pc_stderr: Optional[float] = None
    pc_error_percent: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    cpp_available: bool
    numba_available: bool