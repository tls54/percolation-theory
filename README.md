# Percolation Theory Simulator
A high-performance computational toolkit for simulating and analyzing percolation phenomena on 2D lattices. Features multiple optimization levels from pure Python to C++, with a REST API for remote access and future web interface.
Show Image
Show Image

## What is Percolation Theory?
Percolation theory studies how connectivity emerges in random systems. On a grid where each site is randomly occupied with probability p, clusters of connected sites form. At a critical probability p_c ≈ 0.5927 (for 2D square lattices), the system undergoes a dramatic phase transition where a giant spanning cluster suddenly appears.
This simulator lets you explore this fascinating phenomenon with fast, efficient algorithms.

## Features
- 🔬 Multiple Search Algorithms: BFS, Union-Find (Python, Numba JIT, C++)
- ⚡ High Performance: C++ implementation 17x faster than baseline Python
- 🎯 Critical Point Estimation: Automatic p_c detection with error analysis
- 🌐 REST API: FastAPI backend for remote simulations
- 📊 Comprehensive Analysis: Cluster statistics, phase transition detection
- 🧪 Well-Tested: >95% code coverage with pytest
- 🐳 Docker Ready: Containerized deployment (coming soon)

## Performance
Benchmark results for finding clusters in 50×50 grids (200 trials, p=0.6):

| Algorithm            | Time per grid | Speedup vs BFS |
|---------------------|---------------|----------------|
| Union-Find (C++)     | 0.06 ms       | 17.5x faster   |
| Union-Find (Numba)   | 0.09 ms       | 11.7x faster   |
| BFS (baseline)       | 1.05 ms       | 1.0x           |

## Ways to Use This Project

### 1. 🖥️ Command Line (Python Scripts)
Direct simulation in Python - best for research and experimentation
```python
import numpy as np
from Search import find_clusters_union_find_numba_fast
from Percolation import run_percolation_trials
from Estimation import analyze_simulation_results

# Single simulation
results = run_percolation_trials(
    p=0.6,
    N=100,
    num_trials=500,
    search_algo=find_clusters_union_find_numba_fast
)
print(f"Percolation probability: {results['percolation_probability']:.3f}")

# Parameter sweep with p_c estimation
p_values = np.linspace(0.5, 0.7, 31)
percolation_probs = []
for p in p_values:
    results = run_percolation_trials(p, 100, 500, find_clusters_union_find_numba_fast)
    percolation_probs.append(results['percolation_probability'])

# Estimate critical point
pc_results = analyze_simulation_results(
    np.array(p_values),
    np.array(percolation_probs),
    N=100,
    num_trials=500
)
print(f"Estimated p_c: {pc_results['pc_estimate']:.4f} ± {pc_results['pc_stderr']:.4f}")
```
See also: `examples/` folder for more examples (coming soon)

### 2. 🌐 REST API (Remote Access)
HTTP API for integration with other tools and languages

**Start the API Server**
```bash
# Development mode with auto-reload
uvicorn api.main:app --reload --port 8000

# Production mode
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**API Documentation**
- Interactive docs: http://localhost:8000/docs (Swagger UI)  
- Alternative docs: http://localhost:8000/redoc (ReDoc)  
- OpenAPI schema: http://localhost:8000/openapi.json

**Example Usage with curl**
```bash
# Health check
curl http://localhost:8000/health

# Single simulation
curl -X POST http://localhost:8000/api/simulate   -H "Content-Type: application/json"   -d '{
    "p": 0.6,
    "N": 50,
    "num_trials": 100,
    "algorithm": "numba"
  }'

# Parameter sweep with p_c estimation
curl -X POST http://localhost:8000/api/simulate/sweep   -H "Content-Type: application/json"   -d '{
    "p_min": 0.5,
    "p_max": 0.7,
    "p_steps": 21,
    "N": 100,
    "num_trials": 200,
    "algorithm": "cpp",
    "estimate_pc": true
  }'
```

**Example Usage with Python requests**
```python
import requests

# Single simulation
response = requests.post(
    "http://localhost:8000/api/simulate",
    json={
        "p": 0.6,
        "N": 50,
        "num_trials": 100,
        "algorithm": "numba"
    }
)
result = response.json()
print(f"Percolation probability: {result['percolation_probability']:.3f}")

# Parameter sweep
response = requests.post(
    "http://localhost:8000/api/simulate/sweep",
    json={
        "p_min": 0.5,
        "p_max": 0.7,
        "p_steps": 21,
        "N": 100,
        "num_trials": 200,
        "estimate_pc": True
    }
)
result = response.json()
print(f"Estimated p_c: {result['pc_estimate']:.4f}")
```

### 3. 🎨 Web Interface (Coming Soon)
Interactive visualization and exploration through your browser

```bash
# Start the full stack (when ready)
docker-compose up

# Or manually
uvicorn api.main:app --reload &
cd frontend && npm start
```

Planned features:
- Interactive parameter controls (N, p, algorithm selection)
- Real-time cluster visualization with color-coded clusters
- Phase transition animation as p increases
- P(p) vs p plotting with p_c estimation
- Export results as JSON/CSV

## Quick Start

### Installation
1. Clone the repository:
```bash
git clone https://github.com/tls54/percolation-theory.git
cd percolation-theory
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Build C++ extension for maximum speed:

**macOS/Linux:**
```bash
python setup.py build_ext --inplace
```

**Windows:**
- First install Visual Studio Build Tools (select "Desktop development with C++")
- Then run:
```bash
python setup.py build_ext --inplace
```

> Note: If C++ compilation fails, the simulator still works perfectly with the Numba backend (only 1.5x slower than C++)!

### Verify Installation
```bash
# Run tests
pytest

# Check API
uvicorn api.main:app --reload
# Visit http://localhost:8000/docs

# Quick simulation
python -c "
from Search import find_clusters_union_find_numba_fast
from Percolation import run_percolation_trials
result = run_percolation_trials(0.6, 50, 100, find_clusters_union_find_numba_fast)
print(f"Percolation probability: {result['percolation_probability']:.3f}")
"
```

## Project Structure
```
percolation-theory/
├── Search/                   # Cluster-finding algorithms
│   ├── BFS.py               # Breadth-first search
│   ├── UnionFind.py         # Union-Find (Python & Numba)
│   └── percolation_cpp.so   # C++ extension (if built)
├── api/                      # FastAPI backend
│   ├── main.py              # API entry point
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic
│   ├── models.py            # Request/response models
│   └── config.py            # Configuration
├── tests/                    # Algorithm tests
│   ├── test_algorithms.py
│   ├── test_cpp_build.py
│   ├── test_performance.py
│   └── test_pc_estimation.py
├── tests_api/               # API integration tests
│   ├── test_health.py
│   └── test_simulation.py
├── cpp/
│   └── src/
│       ├── union_find.hpp
│       └── bindings.cpp
├── Percolation.py
├── Estimation.py
├── profiling.py
├── setup.py
├── requirements.txt
└── README.md
```
## Algorithm Overview

### BFS (Breadth-First Search)
- **Pros:** Simple, always works, no extra dependencies
- **Cons:** Slowest option
- **Use when:** You want simplicity or are teaching

### Union-Find (Numba JIT)
- **Pros:** 11.7x faster than BFS, no compilation needed
- **Cons:** Requires Numba installation
- **Use when:** You want good performance without hassle
- ⭐ Recommended for most users

### Union-Find (C++)
- **Pros:** Fastest possible (17.5x faster than BFS)
- **Cons:** Requires C++ compiler and build step
- **Use when:** Maximum performance is critical

## API Reference

### Endpoints

**GET /health**  
Check API health and available optimizations  
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "cpp_available": true,
  "numba_available": true
}
```

**POST /api/simulate**  
Run single percolation simulation  
```json
# Request
{
  "p": 0.6,
  "N": 50,
  "num_trials": 100,
  "algorithm": "numba"
}

# Response
{
  "p": 0.6,
  "percolation_probability": 0.743,
  "mean_num_clusters": 12.4,
  "mean_cluster_size": 8.2,
  "computation_time_ms": 45.2,
  "algorithm_used": "numba"
}
```

**POST /api/simulate/sweep**  
Run parameter sweep across multiple p values  
```json
# Request
{
  "p_min": 0.5,
  "p_max": 0.7,
  "p_steps": 21,
  "N": 100,
  "num_trials": 200,
  "algorithm": "cpp",
  "estimate_pc": true
}

# Response
{
  "p_values": [0.5, 0.51, ...],
  "percolation_probabilities": [0.12, 0.18, ...],
  "pc_estimate": 0.5925,
  "pc_stderr": 0.0012,
  "pc_error_percent": 0.03,
  "total_computation_time_s": 2.34
}
```

## Requirements

**Minimum (BFS only)**
- Python 3.8+
- NumPy 1.20+
- Matplotlib 3.3+

**Recommended (Numba version)**
- All above, plus:
  - Numba 0.55+
  - SciPy 1.7+ (for p_c estimation)

**Optional (C++ version)**
- C++ compiler (GCC, Clang, or MSVC)
- pybind11 2.10+

**API**
- FastAPI 0.104+
- Uvicorn 0.24+
- Pydantic 2.0+

See `requirements.txt` for complete list.

## Development

**Running Tests**
```bash
# All tests
pytest

# Just algorithm tests
pytest tests/

# Just API tests
pytest tests_api/

# With coverage
pytest --cov=. --cov-report=html

# Skip slow tests
pytest -m "not slow"
```

### Profiling

**Profile your own code:**
```python
from profiling import ProfilerConfig, profile_context

config = ProfilerConfig(
    enabled=True,
    line_profile=True,
    output_dir='profiling_results'
)

with profile_context(config, "my_simulation"):
    # Your code here
    results = run_percolation_trials(...)
```

**Profile existing scripts:**
```bash
# Using cProfile
python -m cProfile -o profile.stats Percolation.py

# View results
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"

# Using line_profiler (install: pip install line_profiler)
kernprof -l -v Percolation.py
```

**Profile specific functions:**
Add `@profile` decorator in your script:
```python
from profiling import ProfilerConfig, profile_function

profiler_config = ProfilerConfig(enabled=True)

@profile_function(profiler_config)
def my_expensive_function():
    # Function code here
    pass
```
Results are saved to `profiling_results/` direct

**Building C++ Extension**
```bash
# Clean old builds
rm -rf build/ Search/*.so

# Rebuild
python setup.py build_ext --inplace

# Verify
python -c "from Search import HAS_CPP; print(f'C++ available: {HAS_CPP}')"
```

## Troubleshooting

- **"C++ module not available"**
  - Solution 1: Use Numba version instead (nearly as fast!)
  - Solution 2: Install compiler and rebuild  
    macOS: `xcode-select --install`  
    Linux: `sudo apt-get install build-essential`  
    Windows: Install Visual Studio Build Tools

- **API won't start**  
  Check port 8000 is not in use: `lsof -i :8000`  
  Verify dependencies: `pip install -r requirements.txt`  
  Check imports: `python -c "from api.main import app"`

- **Tests failing**  
  Ensure running from project root  
  Check all dependencies installed  
  Try: `pytest --lf` to re-run only failed tests

- **Import errors**  
  Verify you're in project root directory  
  Check `PYTHONPATH` if needed  
  Ensure `__init__.py` files exist in all packages

## Contributing

Contributions welcome! Areas of interest:
- Additional lattice types (triangular, hexagonal)
- Visualization improvements
- Performance optimizations
- Documentation enhancements
- Frontend development

**Process:**
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Performance Tips

**For Maximum Speed**
```python
# Use C++ with large grids and many trials
from Search import find_clusters_cpp
results = run_percolation_trials(
    p=0.6,
    N=500,
    num_trials=1000,
    search_algo=find_clusters_cpp
)
```

**For Best p_c Accuracy**
```python
# Use focused p-values near p_c
p_values = np.linspace(0.55, 0.65, 51)  # Dense near p_c
N = 200  # Large grid
num_trials = 500  # Many trials
```

**For API Performance**
```bash
# Use multiple workers in production
uvicorn api.main:app --workers 4 --port 8000

# Enable C++ algorithm
# In .env file: USE_CPP=true
```

## Theory Background

**Union-Find Algorithm**  
The Hoshen-Kopelman variant of Union-Find is particularly efficient for percolation:
- Single scan: Process grid left-to-right, top-to-bottom
- Union operation: Merge clusters when neighbors found
- Path compression: Flatten tree structure for fast lookups
- Union by rank: Keep trees balanced

Time complexity: O(N² α(N²)) where α is the inverse Ackermann function (effectively constant).

**Critical Probability**  
For 2D square lattice site percolation:
- Theoretical p_c: 0.59274621...
- Our estimates: Typically within 0.1% with N=100, 200 trials

## Citation
If you use this in research:
```bibtex
@software{percolation_simulator_2025,
  author = {Theo Smith},
  title = {Percolation Theory Simulator},
  year = {2025},
  url = {https://github.com/tls54/percolation-theory}
}
```

## License
MIT License - see LICENSE file for details.

## References
- Stauffer, D., & Aharony, A. (1994). Introduction to Percolation Theory
- Newman, M. E. J., & Ziff, R. M. (2000). "Efficient Monte Carlo algorithm and high-precision results for percolation"
- Hoshen, J., & Kopelman, R. (1976). "Percolation and cluster distribution"

