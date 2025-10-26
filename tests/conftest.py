import pytest
import numpy as np

@pytest.fixture
def sample_grids():
    """Provide various test grids."""
    return {
        'empty': np.zeros((10, 10), dtype=bool),
        'full': np.ones((10, 10), dtype=bool),
        'random_small': np.random.rand(20, 20) < 0.5,
        'random_large': np.random.rand(100, 100) < 0.6,
    }

@pytest.fixture
def algorithms():
    """Import all available algorithms."""
    from Search import (
        find_clusters_bfs,
        find_clusters_union_find_numba_fast,
        HAS_CPP  # Add this
    )
    
    algos = {
        'BFS': find_clusters_bfs,
        'Numba': find_clusters_union_find_numba_fast,
    }
    
    # Only add C++ if actually available
    if HAS_CPP:
        from Search import find_clusters_cpp
        algos['C++'] = find_clusters_cpp
    
    return algos