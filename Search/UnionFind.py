import numpy as np
import numba

def find_clusters_union_find(grid):
    """Find all clusters using Union-Find (Hoshen-Kopelman) algorithm."""
    # Step 1: Initialize parent and size arrays
    N = grid.shape[0]
    parent = np.arange(N*N)
    size = np.ones(N*N, dtype=int)
    labels = np.zeros((N, N), dtype=int)
    
    # ======== Helpers ========
    def find(x):
        # Find root first
        root = x
        while parent[root] != root:
            root = parent[root]
        
        # Path compression: make all nodes point to root
        while parent[x] != root:
            next_node = parent[x]
            parent[x] = root
            x = next_node
        
        return root
        
    def union(x, y):
        # Merge clusters containing x and y

        root_x = find(x)
        root_y = find(y)

        if root_x == root_y:
            return
    
        if size[root_x] < size[root_y]:
            parent[root_x] = root_y
            size[root_y] += size[root_x]
        else:
            parent[root_y] = root_x
            size[root_x] += size[root_y]
        pass
    
    # =========================
    # Step 2: First pass - merge clusters
    for i in range(N):
        for j in range(N):
            if not grid[i, j]:
                continue
            current = i * N + j

            # Check left neighbor
            if j > 0 and grid[i, j-1]:
                left = current - 1 
                union(current, left)

            # Check up neighbor
            if i > 0 and grid[i-1, j]:
                up = current - N
                union(current, up)
    
    # Step 3: Second pass - assign labels and collect info
    cluster_map = np.full(N*N, -1, dtype=int)  # -1 means unassigned
    next_label = 1
    cluster_sizes = {}  # Track sizes
    cluster_sites = {}  # Track sites

    for i in range(N):
        for j in range(N):
            if not grid[i,j]:
                continue
            
            current = i * N + j
            root = find(current)
            
            if cluster_map[root] == -1:  # New cluster
                cluster_map[root] = next_label
                cluster_sizes[next_label] = 0
                cluster_sites[next_label] = []
                next_label += 1
            
            cluster_id = cluster_map[root]
            labels[i, j] = cluster_id
            cluster_sizes[cluster_id] += 1
            cluster_sites[cluster_id].append((i, j))

    # Convert to cluster_info format
    cluster_info = []
    for cid in sorted(cluster_sizes.keys()):
        cluster_info.append({
            'id': cid,
            'size': cluster_sizes[cid],
            'sites': cluster_sites[cid]
        })
        
    return labels, cluster_info


# ========== NUMBA-OPTIMIZED UNION-FIND ==========

@numba.njit
def _find_numba(parent, x):
    """Find root with path compression (Numba-compiled)."""
    # Find root
    root = x
    while parent[root] != root:
        root = parent[root]
    
    # Path compression
    while parent[x] != root:
        next_node = parent[x]
        parent[x] = root
        x = next_node
    
    return root


@numba.njit
def _union_numba(parent, size, x, y):
    """Union two sets by size (Numba-compiled)."""
    root_x = _find_numba(parent, x)
    root_y = _find_numba(parent, y)
    
    if root_x == root_y:
        return
    
    # Union by size
    if size[root_x] < size[root_y]:
        parent[root_x] = root_y
        size[root_y] += size[root_x]
    else:
        parent[root_y] = root_x
        size[root_x] += size[root_y]


@numba.njit
def _union_find_core_numba(grid):
    """
    Core Union-Find algorithm (Numba-compiled).
    Returns only the labels array.
    """
    N = grid.shape[0]
    parent = np.arange(N * N, dtype=np.int32)
    size = np.ones(N * N, dtype=np.int32)
    labels = np.zeros((N, N), dtype=np.int32)
    
    # First pass: merge clusters
    for i in range(N):
        for j in range(N):
            if not grid[i, j]:
                continue
            
            current = i * N + j
            
            # Check left neighbor
            if j > 0 and grid[i, j-1]:
                left = current - 1
                _union_numba(parent, size, current, left)
            
            # Check up neighbor
            if i > 0 and grid[i-1, j]:
                up = current - N
                _union_numba(parent, size, current, up)
    
    # Second pass: assign cluster labels
    cluster_map = np.full(N * N, -1, dtype=np.int32)
    next_label = 1
    
    for i in range(N):
        for j in range(N):
            if not grid[i, j]:
                continue
            
            current = i * N + j
            root = _find_numba(parent, current)
            
            if cluster_map[root] == -1:
                cluster_map[root] = next_label
                next_label += 1
            
            labels[i, j] = cluster_map[root]
    
    return labels


def find_clusters_union_find_numba(grid):
    """
    Find clusters using Numba-optimized Union-Find.
    
    This is a wrapper that calls the Numba core and extracts cluster info.
    """
    # Call Numba-compiled core
    labels = _union_find_core_numba(grid)
    
    # Extract cluster info in Python (this part is fast enough)
    N = grid.shape[0]
    cluster_data = {}  # cluster_id -> {'size': int, 'sites': list}
    
    for i in range(N):
        for j in range(N):
            if labels[i, j] > 0:
                cluster_id = labels[i, j]
                if cluster_id not in cluster_data:
                    cluster_data[cluster_id] = {'size': 0, 'sites': []}
                cluster_data[cluster_id]['size'] += 1
                cluster_data[cluster_id]['sites'].append((i, j))
    
    # Convert to cluster_info format
    cluster_info = []
    for cid in sorted(cluster_data.keys()):
        cluster_info.append({
            'id': cid,
            'size': cluster_data[cid]['size'],
            'sites': cluster_data[cid]['sites']
        })
    
    return labels, cluster_info

@numba.njit
def _extract_cluster_sizes_numba(labels):
    """Just get sizes, no sites."""
    N = labels.shape[0]
    max_label = np.max(labels)
    sizes = np.zeros(max_label + 1, dtype=np.int32)
    
    for i in range(N):
        for j in range(N):
            if labels[i, j] > 0:
                sizes[labels[i, j]] += 1
    
    return sizes[1:]  # Skip 0 (empty)


def find_clusters_union_find_numba_fast(grid):
    """Ultra-fast version without site extraction."""
    labels = _union_find_core_numba(grid)
    sizes = _extract_cluster_sizes_numba(labels)
    
    # Minimal cluster_info (just what's needed for statistics)
    cluster_info = [{'id': i+1, 'size': int(s), 'sites': []} 
                    for i, s in enumerate(sizes) if s > 0]
    
    return labels, cluster_info