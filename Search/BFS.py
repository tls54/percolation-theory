import numpy as np
from collections import deque


def find_clusters_bfs(grid):
    """Find all clusters in a boolean grid using BFS."""
    N = grid.shape[0]
    labels = np.zeros((N, N), dtype=int)
    cluster_id = 0
    cluster_info = []
    
    for i in range(N):
        for j in range(N):
            if grid[i, j] and labels[i, j] == 0:
                cluster_id += 1
                cluster_sites = []
                
                queue = deque([(i, j)])
                labels[i, j] = cluster_id
                
                while queue:
                    row, col = queue.popleft()
                    cluster_sites.append((row, col))
                    
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        new_row, new_col = row + dr, col + dc
                        
                        if 0 <= new_row < N and 0 <= new_col < N:
                            if grid[new_row, new_col] and labels[new_row, new_col] == 0:
                                labels[new_row, new_col] = cluster_id
                                queue.append((new_row, new_col))
                
                cluster_info.append({
                    'id': cluster_id,
                    'size': len(cluster_sites),
                    'sites': cluster_sites
                })
    
    return labels, cluster_info


def find_clusters_bfs_fast(grid):
    """
    Fast BFS that only tracks cluster sizes, not individual sites.
    """
    N = grid.shape[0]
    labels = np.zeros((N, N), dtype=int)
    cluster_id = 0
    cluster_sizes = []
    
    for i in range(N):
        for j in range(N):
            if grid[i, j] and labels[i, j] == 0:
                cluster_id += 1
                cluster_size = 0
                
                queue = deque([(i, j)])
                labels[i, j] = cluster_id
                
                while queue:
                    row, col = queue.popleft()
                    cluster_size += 1  # Just count, don't store
                    
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        new_row, new_col = row + dr, col + dc
                        
                        if 0 <= new_row < N and 0 <= new_col < N:
                            if grid[new_row, new_col] and labels[new_row, new_col] == 0:
                                labels[new_row, new_col] = cluster_id
                                queue.append((new_row, new_col))
                
                cluster_sizes.append(cluster_size)
    
    # Create minimal cluster_info
    cluster_info = [
        {'id': i+1, 'size': cluster_sizes[i], 'sites': []} 
        for i in range(len(cluster_sizes))
    ]
    
    return labels, cluster_info