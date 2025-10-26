"""Search algorithms for percolation theory."""

# Import BFS algorithms
from .BFS import find_clusters_bfs, find_clusters_bfs_fast

# Import Python/Numba Union-Find algorithms
from .UnionFind import (
    find_clusters_union_find,
    find_clusters_union_find_numba,
    find_clusters_union_find_numba_fast,
)

# Try to import C++ version
try:
    from . import percolation_cpp  # type: ignore
    
    def find_clusters_cpp(grid):
        """C++ Union-Find with fast NumPy wrapper."""
        import numpy as np
        
        # Fast C++ core
        labels = percolation_cpp.find_clusters(grid)
        
        # Fast cluster size extraction using NumPy
        if labels.max() == 0:
            # Empty grid
            return labels, []
        
        # Use np.bincount for fast counting (much faster than loops!)
        flat_labels = labels.ravel()
        counts = np.bincount(flat_labels)
        
        # Skip label 0 (empty), create cluster_info
        cluster_info = [
            {'id': i, 'size': int(counts[i]), 'sites': []}
            for i in range(1, len(counts)) if counts[i] > 0
        ]
        
        return labels, cluster_info
    
    HAS_CPP = True
    
except ImportError as e:
    HAS_CPP = False
    print(f"Warning: C++ module not available. Error: {e}")
    
    def find_clusters_cpp(grid):
        raise RuntimeError("C++ module not built")

# Export all
__all__ = [
    'find_clusters_bfs',
    'find_clusters_bfs_fast',
    'find_clusters_union_find',
    'find_clusters_union_find_numba',
    'find_clusters_union_find_numba_fast',
    'find_clusters_cpp',
    'HAS_CPP',
]