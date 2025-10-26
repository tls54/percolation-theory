"""Simulation endpoints."""

from fastapi import APIRouter, HTTPException
from api.models import (
    SimulationRequest,
    SimulationResult,
    ParameterSweepRequest,
    ParameterSweepResult
)
from api.services.percolation_service import run_single_simulation, run_parameter_sweep

router = APIRouter()


@router.post("/simulate", response_model=SimulationResult)
async def simulate(request: SimulationRequest):
    """
    Run a single percolation simulation at given probability p.
    
    - **p**: Occupation probability (0.0 to 1.0)
    - **N**: Grid size (N×N, max 500)
    - **num_trials**: Number of independent trials (max 1000)
    - **algorithm**: Search algorithm ("bfs", "numba", or "cpp")
    """
    try:
        result = run_single_simulation(
            p=request.p,
            N=request.N,
            num_trials=request.num_trials,
            algorithm=request.algorithm
        )
        return SimulationResult(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/simulate/sweep", response_model=ParameterSweepResult)
async def parameter_sweep(request: ParameterSweepRequest):
    """
    Run parameter sweep across multiple p values.
    
    Simulates percolation at evenly-spaced p values between p_min and p_max.
    Optionally estimates the critical probability p_c.
    """
    try:
        result = run_parameter_sweep(
            p_min=request.p_min,
            p_max=request.p_max,
            p_steps=request.p_steps,
            N=request.N,
            num_trials=request.num_trials,
            algorithm=request.algorithm,
            estimate_pc=request.estimate_pc
        )
        return ParameterSweepResult(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parameter sweep failed: {str(e)}")