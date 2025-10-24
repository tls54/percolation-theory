# Percolation Theory Simulator

A high-performance computational toolkit for simulating and analyzing percolation phenomena on 2D lattices.  
Implements multiple cluster-finding algorithms with performance ranging from simple Python to optimized C++.

---

## What is Percolation Theory?

Percolation theory studies how connectivity emerges in random systems.  
On a grid where each site is randomly occupied with probability `p`, clusters of connected sites form.  
At a critical probability \( p_c \approx 0.5927 \) (for 2D square lattices), the system undergoes a dramatic phase transition where a giant spanning cluster suddenly appears.

This simulator lets you explore this fascinating phenomenon with fast, efficient algorithms.

---

## Features

- **Multiple Search Algorithms:** BFS, Union-Find (Python, Numba JIT, C++)
- **Flexible Performance Tiers:** Choose speed vs. ease of installation
- **Comprehensive Benchmarking:** Built-in profiling and comparison tools
- **Educational:** Well-documented code showing algorithm evolution from simple to optimized

---

## Performance

Benchmark results for finding clusters in 50×50 grids (200 trials, `p = 0.6`):

| Algorithm             | Time per grid | Speedup vs BFS  |
|-----------------------|---------------|-----------------|
| Union-Find (C++)      | 0.06 ms       | 17.5× faster    |
| Union-Find (Numba)    | 0.09 ms       | 11.7× faster    |
| BFS (baseline)        | 1.05 ms       | 1.0×            |
| Union-Find (Python)   | 2.51 ms       | 0.4×            |

**TL;DR:** The C++ version simulates 200 grids in 12 ms. That’s blazing fast! 🚀

---

## Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/percolation-theory.git
   cd percolation-theory
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Build C++ extension for maximum speed**

   **macOS/Linux:**
   ```bash
   python setup.py build_ext --inplace
   ```

   **Windows:**
   - First install Visual Studio Build Tools (select “Desktop development with C++”)
   - Then run:
     ```bash
     python setup.py build_ext --inplace
     ```

> 💡 If C++ compilation fails, the simulator still works perfectly with the Numba backend (only ~1.5× slower than C++).

---

## Basic Usage

```python
import numpy as np
from Search import find_clusters_union_find_numba_fast

# Generate random grid at critical probability
N = 100
p = 0.5927  # Critical probability for 2D square lattice
grid = np.random.rand(N, N) < p

# Find clusters
labels, cluster_info = find_clusters_union_find_numba_fast(grid)

print(f"Found {len(cluster_info)} clusters")
print(f"Largest cluster: {max(c['size'] for c in cluster_info)} sites")
```

---

## Run a Single Simulation

```python
from Percolation import run_percolation_trials
from Search import find_clusters_union_find_numba_fast

# Run 1000 trials at p=0.6
results = run_percolation_trials(
    p=0.6,
    N=50,
    num_trials=1000,
    search_algo=find_clusters_union_find_numba_fast,
    verbose=False
)

print(f"Percolation probability: {results['percolation_probability']:.3f}")
print(f"Mean cluster size: {results['mean_cluster_size']:.1f}")
```

---

## Run a Parameter Sweep

```python
import numpy as np
import matplotlib.pyplot as plt
from Percolation import run_percolation_trials
from Search import find_clusters_union_find_numba_fast

# Sweep across p values near critical point
p_values = np.linspace(0.4, 0.7, 31)
N = 50
num_trials = 100

percolation_probs = []

for p in p_values:
    results = run_percolation_trials(
        p=p,
        N=N,
        num_trials=num_trials,
        search_algo=find_clusters_union_find_numba_fast,
        verbose=False
    )
    percolation_probs.append(results['percolation_probability'])
    print(f"p={p:.3f}: P(p)={results['percolation_probability']:.3f}")

# Plot the phase transition
plt.plot(p_values, percolation_probs, 'o-')
plt.axvline(x=0.5927, color='r', linestyle='--', label='Critical p_c')
plt.xlabel('Occupation probability (p)')
plt.ylabel('Percolation probability')
plt.title('Percolation Phase Transition')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```

---

## Run Benchmarks

```python
from benchmarks import test_search_algorithms, benchmark_search_algorithms

# Verify all algorithms give same results
test_search_algorithms()

# Compare performance
benchmark_search_algorithms()
```

---

## Project Structure

```
percolation-theory/
├── Search/                   # Cluster-finding algorithms
│   ├── BFS.py               # Breadth-first search implementations
│   ├── UnionFind.py         # Union-Find (Python & Numba)
│   └── __init__.py          # Module interface
├── cpp/                      # C++ extension (optional)
│   └── src/
│       ├── union_find.hpp   # C++ Union-Find implementation
│       └── bindings.cpp     # Python bindings (pybind11)
├── Percolation.py           # Main simulation runner
├── profiling.py             # Performance profiling utilities
├── benchmarks.py            # Algorithm validation & benchmarking
├── setup.py                 # C++ build configuration
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## Algorithm Overview

### BFS (Breadth-First Search)
- **Pros:** Simple, always works, no dependencies beyond NumPy  
- **Cons:** Slowest option  
- **Use when:** You want simplicity or have no other dependencies

### Union-Find (Numba)
- **Pros:** 11.7× faster than BFS, no compilation needed  
- **Cons:** Requires Numba installation  
- **Use when:** You want good performance without C++ compilation  
  ✅ *Recommended for most users*

### Union-Find (C++)
- **Pros:** Fastest possible (17.5× faster than BFS)  
- **Cons:** Requires C++ compiler and build step  
- **Use when:** Maximum performance is critical

---

## Requirements

### Minimum (BFS only)
- Python 3.8+
- NumPy 1.20+
- Matplotlib 3.3+

### Recommended (Numba version)
```bash
pip install numba>=0.55.0
```

### Optional (C++ version)
- C++ compiler (GCC, Clang, or MSVC)
- pybind11 2.10+

> See `requirements.txt` for the complete list.

---

## How It Works

### Percolation Process

1. **Grid Generation:** Create an N×N grid where each site is occupied with probability `p`  
2. **Cluster Finding:** Identify connected components of occupied sites  
3. **Percolation Check:** Does any cluster span from top to bottom?  
4. **Statistics:** Aggregate results over many trials  

### Critical Behavior

At \( p_c \approx 0.5927 \):

- **Below p_c:** Small isolated clusters  
- **At p_c:** Fractal clusters at all scales  
- **Above p_c:** Giant spanning cluster emerges  

The transition is sharp and universal across different lattice types!

---

## Development

### Running Tests
```python
from benchmarks import test_search_algorithms

# Validate all algorithms produce identical results
test_search_algorithms()
```

### Profiling
```python
from profiling import ProfilerConfig, profile_context

config = ProfilerConfig(
    enabled=True,
    line_profile=True,
    output_dir='profiling_results'
)

# Profile your code
with profile_context(config, "my_simulation"):
    # Your simulation code here
    pass
```

### Building C++ Extension
The C++ module uses `pybind11` to create Python bindings. To rebuild:

```bash
# Clean old builds
rm -rf build/ Search/*.so

# Rebuild
python setup.py build_ext --inplace
```

---

## Troubleshooting

### “C++ module not available”
- **Solution 1:** Use Numba version instead (nearly as fast!)  
- **Solution 2:** Check compiler installation  
  - macOS: `xcode-select --install`  
  - Linux: `sudo apt-get install build-essential`  
  - Windows: Install Visual Studio Build Tools

### Numba compilation warnings
- First run is slow (JIT compilation), subsequent runs are fast  
- Warnings are normal — can be ignored  

### Import errors
- Ensure you're running from the project root directory  
- Check that `Search/__init__.py` exists and is not empty  

---

## Theory Background

### Union-Find Algorithm

The **Hoshen–Kopelman** variant of Union-Find is particularly efficient for percolation:

1. **Single scan:** Process grid left-to-right, top-to-bottom  
2. **Union operation:** Merge clusters when neighbors are found  
3. **Path compression:** Flatten tree structure for fast lookups  
4. **Union by rank:** Keep trees balanced  

Time complexity:  
\( O(N^2 \alpha(N^2)) \) where \( \alpha \) is the inverse Ackermann function (effectively constant).

### Why It's Fast
- **BFS:** Must maintain a queue and make multiple passes per cluster  
- **Union-Find:** Single pass, efficient merging, optimal for grid connectivity  
- **C++:** Compiled to machine code — no Python interpreter overhead

---

## Future Plans

- REST API (FastAPI backend)  
- Interactive web visualization  
- 3D percolation  
- Different lattice types (triangular, hexagonal)  
- Cluster size distribution analysis  
- Finite-size scaling analysis  

---

## Contributing

Contributions welcome!  
Areas of interest:

- Additional lattice types  
- Visualization improvements  
- Performance optimizations  
- Documentation enhancements  

---

## License

**MIT License** — see `LICENSE` file for details.

---

## References

- Stauffer, D., & Aharony, A. (1994). *Introduction to Percolation Theory*  
- Newman, M. E. J., & Ziff, R. M. (2000). *Efficient Monte Carlo algorithm and high-precision results for percolation*  
- Hoshen, J., & Kopelman, R. (1976). *Percolation and cluster distribution. I. Cluster multiple labeling technique and critical concentration algorithm*

---

## Citation

If you use this in research:

```bibtex
@software{percolation_simulator_2025,
  author = {Your Name},
  title = {Percolation Theory Simulator},
  year = {2025},
  url = {https://github.com/yourusername/percolation-theory}
}
```

---

## Acknowledgments

Built as a learning project exploring the intersection of **algorithm optimization**, **scientific computing**, and **software engineering**.
