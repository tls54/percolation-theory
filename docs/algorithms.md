# Algorithm Details

Deep dive into percolation algorithms, data structures, and implementation.

## Overview

This project implements three cluster-finding algorithms with progressively increasing performance:

1. **BFS**: Pure Python breadth-first search
2. **Union-Find (Numba)**: JIT-compiled Union-Find with path compression
3. **Union-Find (C++)**: Native C++ implementation with Python bindings

All algorithms solve the same problem: identify connected clusters in a boolean grid.

## Problem Definition

Given an N×N grid where each cell is either **occupied** (True) or **empty** (False), find all connected clusters of occupied cells. Two cells are connected if they are adjacent horizontally or vertically (not diagonally).

**Input:**
```
Grid (5×5):
T T F F T
T F F T T
F F F T F
T T F F F
F T F T T
```

**Output:**
```
Clusters (labeled):
1 1 0 0 2
1 0 0 2 2
0 0 0 2 0
3 3 0 0 0
0 3 0 4 4

Number of clusters: 4
```

## Breadth-First Search (BFS)

### Algorithm

1. Scan grid left-to-right, top-to-bottom
2. When an unlabeled occupied cell is found:
   - Assign new cluster label
   - Use BFS to label all connected cells
3. Continue scanning until entire grid is processed

### Pseudocode

```
function find_clusters_bfs(grid):
    clusters = zeros_like(grid)
    current_label = 0

    for i in 0 to N-1:
        for j in 0 to N-1:
            if grid[i,j] and not clusters[i,j]:
                current_label += 1
                queue = [(i, j)]
                while queue not empty:
                    x, y = queue.pop(0)
                    if already labeled:
                        continue
                    clusters[x,y] = current_label
                    for each neighbor (nx, ny):
                        if grid[nx,ny] and not clusters[nx,ny]:
                            queue.append((nx, ny))

    return clusters, current_label
```

### Complexity

- **Time**: O(N²) - each cell visited once
- **Space**: O(N²) - queue can contain entire cluster

### Pros and Cons

**Pros:**
- Simple and intuitive
- Easy to understand and debug
- No special dependencies

**Cons:**
- Slowest performance (baseline)
- Queue operations have overhead
- Not cache-friendly

### Implementation Details

Located in `Search/BFS.py`:

```python
def find_clusters_bfs(grid):
    N = grid.shape[0]
    clusters = np.zeros((N, N), dtype=np.int32)
    current_label = 0

    for i in range(N):
        for j in range(N):
            if grid[i, j] and clusters[i, j] == 0:
                current_label += 1
                queue = [(i, j)]

                while queue:
                    x, y = queue.pop(0)
                    if clusters[x, y] != 0:
                        continue

                    clusters[x, y] = current_label

                    # Check all 4 neighbors
                    for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < N and 0 <= ny < N:
                            if grid[nx, ny] and clusters[nx, ny] == 0:
                                queue.append((nx, ny))

    return clusters, current_label
```

## Union-Find Algorithm

### Hoshen-Kopelman Variant

The Union-Find algorithm (also called Disjoint Set Union) efficiently merges clusters as they're discovered. The Hoshen-Kopelman variant is specifically optimized for lattice percolation.

### Key Operations

**Find**: Determine which cluster a cell belongs to
```python
def find(parent, x):
    # Path compression: flatten tree
    if parent[x] != x:
        parent[x] = find(parent, parent[x])
    return parent[x]
```

**Union**: Merge two clusters
```python
def union(parent, rank, x, y):
    root_x = find(parent, x)
    root_y = find(parent, y)

    if root_x == root_y:
        return

    # Union by rank: attach smaller tree to larger
    if rank[root_x] < rank[root_y]:
        parent[root_x] = root_y
    elif rank[root_x] > rank[root_y]:
        parent[root_y] = root_x
    else:
        parent[root_y] = root_x
        rank[root_x] += 1
```

### Algorithm Steps

1. **Initialization**: Each occupied cell starts as its own cluster
2. **Single scan**: Process grid left-to-right, top-to-bottom
3. **Check neighbors**: For each occupied cell, check left and up neighbors
4. **Union**: If neighbor is occupied, merge clusters
5. **Relabeling**: Compress labels to sequential integers

### Pseudocode

```
function find_clusters_union_find(grid):
    # Initialize parent array (each cell is its own parent)
    parent = [i for i in range(N*N)]
    rank = zeros(N*N)

    # Single scan
    for i in 0 to N-1:
        for j in 0 to N-1:
            if not grid[i,j]:
                continue

            current = i*N + j

            # Check left neighbor
            if j > 0 and grid[i,j-1]:
                left = i*N + (j-1)
                union(parent, rank, current, left)

            # Check up neighbor
            if i > 0 and grid[i-1,j]:
                up = (i-1)*N + j
                union(parent, rank, current, up)

    # Relabel to sequential integers
    clusters = relabel(parent, grid)

    return clusters, num_clusters
```

### Complexity

- **Time**: O(N² α(N²)) where α is inverse Ackermann (effectively constant)
- **Space**: O(N²) for parent and rank arrays

### Optimizations

**Path Compression**: Flattens tree structure during find operations
```
Before:          After:
   5               5
   |              /|\
   4             1 2 4
   |
   3
   |
   2
   |
   1
```

**Union by Rank**: Attaches smaller tree to larger tree
- Keeps trees balanced
- Reduces find operation time

## Numba Implementation

### Just-In-Time Compilation

Numba compiles Python code to optimized machine code at runtime:

```python
from numba import njit

@njit
def find_clusters_union_find_numba(grid):
    # Algorithm implementation
    # Compiles to native code on first call
    ...
```

### Benefits

- No manual compilation step
- Python-like syntax
- Near-C++ performance
- Type inference and optimization

### Implementation Details

Located in `Search/UnionFind.py`:

```python
@njit
def find_clusters_union_find_numba_fast(grid):
    N = grid.shape[0]
    parent = np.arange(N * N, dtype=np.int32)
    rank = np.zeros(N * N, dtype=np.int32)

    # Union-Find with path compression
    for i in range(N):
        for j in range(N):
            if not grid[i, j]:
                continue

            current = i * N + j

            if j > 0 and grid[i, j-1]:
                left = i * N + (j-1)
                union_with_path_compression(parent, rank, current, left)

            if i > 0 and grid[i-1, j]:
                up = (i-1) * N + j
                union_with_path_compression(parent, rank, current, up)

    # Relabel
    return relabel_clusters(grid, parent)
```

### Performance Characteristics

- First call: ~100ms compilation overhead
- Subsequent calls: 11.7× faster than BFS
- Cache-friendly memory access
- SIMD vectorization where possible

## C++ Implementation

### Why C++?

- Direct memory access
- Compiler optimizations (O3, loop unrolling)
- No Python interpreter overhead
- Inline function calls

### Implementation

Located in `cpp/src/union_find.hpp`:

```cpp
class UnionFind {
private:
    std::vector<int> parent;
    std::vector<int> rank;

public:
    UnionFind(int size) : parent(size), rank(size, 0) {
        std::iota(parent.begin(), parent.end(), 0);
    }

    int find(int x) {
        if (parent[x] != x) {
            parent[x] = find(parent[x]);  // Path compression
        }
        return parent[x];
    }

    void unite(int x, int y) {
        int root_x = find(x);
        int root_y = find(y);

        if (root_x == root_y) return;

        // Union by rank
        if (rank[root_x] < rank[root_y]) {
            parent[root_x] = root_y;
        } else if (rank[root_x] > rank[root_y]) {
            parent[root_y] = root_x;
        } else {
            parent[root_y] = root_x;
            rank[root_x]++;
        }
    }
};
```

### Python Bindings

Using pybind11 (`cpp/src/bindings.cpp`):

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

py::tuple find_clusters_cpp(py::array_t<bool> grid) {
    // Extract grid data
    auto buf = grid.request();
    bool *ptr = static_cast<bool*>(buf.ptr);
    int N = buf.shape[0];

    // Run Union-Find
    UnionFind uf(N * N);

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            if (!ptr[i * N + j]) continue;

            int current = i * N + j;

            if (j > 0 && ptr[i * N + (j-1)]) {
                uf.unite(current, current - 1);
            }
            if (i > 0 && ptr[(i-1) * N + j]) {
                uf.unite(current, current - N);
            }
        }
    }

    // Relabel and return
    return relabel_clusters(grid, uf);
}

PYBIND11_MODULE(percolation_cpp, m) {
    m.def("find_clusters_cpp", &find_clusters_cpp);
}
```

### Compiler Optimizations

Build with optimization flags:
```bash
-O3              # Maximum optimization
-march=native    # Use CPU-specific instructions
-flto            # Link-time optimization
```

### Performance Characteristics

- 17.5× faster than BFS
- 1.5× faster than Numba
- Best for N ≥ 100
- Essential for N ≥ 500

## Performance Comparison

### Benchmark Setup

- Grid size: 50×50
- Occupation probability: p=0.6
- Number of trials: 200
- Platform: Modern CPU (Intel/AMD)

### Results

| Algorithm | Time per grid | Memory | First Call |
|-----------|--------------|--------|------------|
| BFS       | 1.05 ms      | O(N²)  | ~1 ms      |
| Numba     | 0.09 ms      | O(N²)  | ~100 ms    |
| C++       | 0.06 ms      | O(N²)  | ~1 ms      |

### Scaling with Grid Size

| N   | BFS      | Numba    | C++      |
|-----|----------|----------|----------|
| 50  | 1.05 ms  | 0.09 ms  | 0.06 ms  |
| 100 | 4.2 ms   | 0.36 ms  | 0.24 ms  |
| 200 | 17 ms    | 1.4 ms   | 0.96 ms  |
| 500 | 106 ms   | 8.8 ms   | 6.0 ms   |

Complexity is O(N²), so doubling N quadruples time.

## Algorithm Selection Guide

### Decision Tree

```
Do you need maximum performance?
├─ Yes: Use C++ (if available)
│   └─ C++ not available?
│       └─ Use Numba
└─ No: Are you teaching/learning?
    ├─ Yes: Use BFS
    └─ No: Use Numba (best balance)
```

### Recommendations

**BFS**:
- Teaching percolation concepts
- Small grids (N ≤ 30)
- Debugging cluster logic
- When simplicity matters most

**Numba**:
- ⭐ Default choice for most users
- Production simulations (N ≤ 200)
- When C++ build is not possible
- Development and testing

**C++**:
- Large-scale simulations (N ≥ 200)
- Maximum performance required
- Production deployment
- Batch processing

## See Also

- [Theory Background](theory.md) - Percolation theory fundamentals
- [Development Guide](development.md) - Building and profiling
- [Search README](../Search/README.md) - Algorithm implementations
- [Usage Guide](usage.md) - How to use each algorithm
