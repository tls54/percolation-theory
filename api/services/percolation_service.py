"""Business logic for percolation simulations."""

import time
import numpy as np
from typing import Tuple, Optional

from Search import (
    find_clusters_bfs,
    find_clusters_union_find_numba_fast,
    find_clusters_cpp,
    HAS_CPP
)
from Percolation import run_percolation_trials
from Estimation import analyze_simulation_results


def get_algorithm(algorithm: str):
    """Get the appropriate search algorithm function."""
    algorithms = {
        "bfs": find_clusters_bfs,
        "numba": find_clusters_union_find_numba_fast,
        "cpp": find_clusters_cpp if HAS_CPP else find_clusters_union_find_numba_fast
    }
    
    return algorithms.get(algorithm, find_clusters_union_find_numba_fast)


def run_single_simulation(
    p: float,
    N: int,
    num_trials: int,
    algorithm: str
) -> dict:
    """
    Run a single-point percolation simulation.
    
    Returns dict with simulation results and timing.
    """
    search_algo = get_algorithm(algorithm)
    
    start = time.perf_counter()
    results = run_percolation_trials(p, N, num_trials, search_algo, verbose=False)
    elapsed = time.perf_counter() - start
    
    return {
        **results,
        "algorithm_used": algorithm if algorithm != "cpp" or HAS_CPP else "numba",
        "computation_time_ms": elapsed * 1000
    }


def run_parameter_sweep(
    p_min: float,
    p_max: float,
    p_steps: int,
    N: int,
    num_trials: int,
    algorithm: str,
    estimate_pc: bool = True
) -> dict:
    """
    Run parameter sweep across multiple p values.
    
    Returns dict with sweep results, timing, and optional p_c estimate.
    """
    search_algo = get_algorithm(algorithm)
    p_values = np.linspace(p_min, p_max, p_steps)
    
    percolation_probs = []
    cluster_counts = []
    cluster_sizes = []
    
    start = time.perf_counter()
    
    for p in p_values:
        results = run_percolation_trials(p, N, num_trials, search_algo, verbose=False)
        percolation_probs.append(results['percolation_probability'])
        cluster_counts.append(results['mean_num_clusters'])
        cluster_sizes.append(results['mean_cluster_size'])
    
    elapsed = time.perf_counter() - start
    
    result = {
        "p_values": p_values.tolist(),
        "percolation_probabilities": percolation_probs,
        "mean_cluster_counts": cluster_counts,
        "mean_cluster_sizes": cluster_sizes,
        "N": N,
        "num_trials": num_trials,
        "algorithm_used": algorithm if algorithm != "cpp" or HAS_CPP else "numba",
        "total_computation_time_s": elapsed,
        "pc_estimate": None,
        "pc_stderr": None,
        "pc_error_percent": None
    }
    
    # Estimate p_c if requested
    if estimate_pc:
        pc_results = analyze_simulation_results(
            np.array(p_values),
            np.array(percolation_probs),
            N,
            num_trials,
            verbose=False
        )
        
        if pc_results['pc_estimate'] is not None:
            result["pc_estimate"] = float(pc_results['pc_estimate'])
            result["pc_stderr"] = float(pc_results['pc_stderr'])
            result["pc_error_percent"] = float(pc_results['error_percent'])
    
    return result