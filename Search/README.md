# Search Algorithms

Cluster-finding algorithms for percolation simulations with multiple optimization levels.

## Available Algorithms

### BFS (Breadth-First Search)

Pure Python implementation using breadth-first search.

**Pros:**
- Simple and easy to understand
- No compilation or special dependencies
- Always works

**Cons:**
- Slowest option (baseline performance)

**Use when:**
- Teaching or learning percolation concepts
- Simplicity is more important than speed
- No Numba or C++ compiler available

**Example:**
```python
from Search import find_clusters_bfs
import numpy as np

grid = np.random.rand(50, 50) < 0.6
clusters, num_clusters = find_clusters_bfs(grid)
print(f"Found {num_clusters} clusters")
```

### Union-Find (Numba JIT)

Optimized Union-Find with Numba just-in-time compilation.

**Pros:**
- 11.7x faster than BFS
- No manual compilation step
- Easy installation (just `pip install numba`)

**Cons:**
- Requires Numba package
- First run has compilation overhead

**Use when:**
- You want good performance without hassle
- C++ compilation is not available or desired
- ⭐ **Recommended for most users**

**Example:**
```python
from Search import find_clusters_union_find_numba_fast
import numpy as np

grid = np.random.rand(50, 50) < 0.6
clusters, num_clusters = find_clusters_union_find_numba_fast(grid)
print(f"Found {num_clusters} clusters")
```

### Union-Find (C++)

High-performance C++ implementation with Python bindings.

**Pros:**
- 17.5x faster than BFS
- Maximum possible performance
- Ideal for large-scale simulations

**Cons:**
- Requires C++ compiler
- Manual build step required
- Platform-specific compilation

**Use when:**
- Maximum performance is critical
- Running many large simulations
- Processing grids larger than 200×200

**Example:**
```python
from Search import find_clusters_cpp
import numpy as np

grid = np.random.rand(50, 50) < 0.6
clusters, num_clusters = find_clusters_cpp(grid)
print(f"Found {num_clusters} clusters")
```

## Performance Comparison

Benchmark results for 50×50 grids (200 trials, p=0.6):

| Algorithm            | Time per grid | Speedup vs BFS | Status Check |
|---------------------|---------------|----------------|--------------|
| Union-Find (C++)     | 0.06 ms       | 17.5x faster   | `HAS_CPP`    |
| Union-Find (Numba)   | 0.09 ms       | 11.7x faster   | `HAS_NUMBA`  |
| BFS (baseline)       | 1.05 ms       | 1.0x           | Always available |

**Check what's available:**
```python
from Search import HAS_CPP, HAS_NUMBA

print(f"C++ available: {HAS_CPP}")
print(f"Numba available: {HAS_NUMBA}")
```

## Building the C++ Extension

### Requirements

- C++ compiler (GCC, Clang, or MSVC)
- Python development headers
- pybind11 (installed via requirements.txt)

### macOS

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Build extension
python setup.py build_ext --inplace

# Verify
python -c "from Search import HAS_CPP; print(f'C++ available: {HAS_CPP}')"
```

### Linux

```bash
# Install build tools
sudo apt-get update
sudo apt-get install build-essential python3-dev

# Build extension
python setup.py build_ext --inplace

# Verify
python -c "from Search import HAS_CPP; print(f'C++ available: {HAS_CPP}')"
```

### Windows

```bash
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/
# Select "Desktop development with C++"

# Build extension
python setup.py build_ext --inplace

# Verify
python -c "from Search import HAS_CPP; print(f'C++ available: {HAS_CPP}')"
```

### Rebuilding

```bash
# Clean old builds
rm -rf build/ Search/*.so Search/*.pyd

# Rebuild from scratch
python setup.py build_ext --inplace
```

### Docker

Docker automatically builds the C++ extension:

```bash
# C++ is built during image creation
docker-compose up --build

# Verify in container
docker-compose exec api python -c "from Search import HAS_CPP; print(f'C++ available: {HAS_CPP}')"
```

## Algorithm Details

### Union-Find with Path Compression

All optimized implementations use the Hoshen-Kopelman variant:

1. **Single scan**: Process grid left-to-right, top-to-bottom
2. **Union operation**: Merge clusters when neighbors are found
3. **Path compression**: Flatten tree structure for O(1) lookups
4. **Union by rank**: Keep trees balanced

**Time Complexity:** O(N² α(N²)) where α is the inverse Ackermann function (effectively constant)

**Space Complexity:** O(N²) for the label array

### Implementation Differences

**Python/Numba:**
- Separate parent and rank arrays
- Explicit path compression in find operation
- NumPy-based grid processing

**C++:**
- Combined parent/rank in single array
- Aggressive compiler optimizations
- Direct memory access without Python overhead

See [Algorithm Details](../docs/algorithms.md) for deeper dive into the theory and implementation.

## Troubleshooting

### C++ Build Fails

**"Unable to find vcvarsall.bat" (Windows):**
- Install Visual Studio Build Tools with C++ support
- Restart terminal after installation

**"Python.h not found" (Linux):**
```bash
sudo apt-get install python3-dev
```

**"clang: command not found" (macOS):**
```bash
xcode-select --install
```

### Import Errors

**"cannot import name 'find_clusters_cpp'":**
- C++ extension not built or build failed
- Use Numba version instead: `find_clusters_union_find_numba_fast`

**"cannot import name 'find_clusters_union_find_numba_fast'":**
- Numba not installed: `pip install numba`

### Performance Issues

**First run is slow with Numba:**
- Numba compiles on first call (one-time overhead)
- Subsequent calls are fast
- Solution: Run a warm-up simulation

**C++ not faster than expected:**
- Verify C++ is actually being used: check `HAS_CPP`
- Small grids (N < 50) have minimal benefit
- Try larger grids (N > 100) for best speedup

## Benchmarking

Run your own benchmarks:

```python
from profiling import ProfilerConfig, profile_context
from Search import find_clusters_cpp, find_clusters_union_find_numba_fast, find_clusters_bfs
import numpy as np
import time

N = 100
p = 0.6
num_trials = 200

# Generate grids
grids = [np.random.rand(N, N) < p for _ in range(num_trials)]

# Benchmark each algorithm
for name, algo in [("C++", find_clusters_cpp),
                   ("Numba", find_clusters_union_find_numba_fast),
                   ("BFS", find_clusters_bfs)]:
    start = time.time()
    for grid in grids:
        clusters, num_clusters = algo(grid)
    elapsed = time.time() - start
    print(f"{name}: {elapsed*1000/num_trials:.2f} ms per grid")
```

## See Also

- [Algorithm Deep Dive](../docs/algorithms.md) - Implementation details and theory
- [Development Guide](../docs/development.md) - Profiling and optimization
- [Theory Background](../docs/theory.md) - Percolation theory fundamentals
