# Percolation Theory Simulator

A high-performance computational toolkit for simulating and analyzing percolation phenomena on 2D lattices. Features multiple optimization levels from pure Python to C++, with a REST API for remote access and visualization.

Show Image
Show Image

## What is Percolation Theory?

Percolation theory studies how connectivity emerges in random systems. On a grid where each site is randomly occupied with probability p, clusters of connected sites form. At a critical probability p_c ≈ 0.5927 (for 2D square lattices), the system undergoes a dramatic phase transition where a giant spanning cluster suddenly appears.

This simulator lets you explore this fascinating phenomenon with fast, efficient algorithms.

## Features

- Multiple search algorithms: BFS, Union-Find (Python, Numba JIT, C++)
- High performance: C++ implementation 17x faster than baseline Python
- Critical point estimation with error analysis
- REST API for remote simulations
- Cluster visualization with color-coded PNG output
- Comprehensive cluster statistics and phase transition detection
- Well-tested: >95% code coverage
- Docker ready with full C++ optimization

## Performance

Benchmark results for 50×50 grids (200 trials, p=0.6):

| Algorithm            | Time per grid | Speedup vs BFS |
|---------------------|---------------|----------------|
| Union-Find (C++)     | 0.06 ms       | 17.5x faster   |
| Union-Find (Numba)   | 0.09 ms       | 11.7x faster   |
| BFS (baseline)       | 1.05 ms       | 1.0x           |

## Quick Start

### Docker (Recommended)

```bash
# Start the API service
docker-compose up -d

# Check health
curl http://localhost:8000/api/health

# Run a simulation
curl -X POST http://localhost:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"p": 0.6, "N": 100, "num_trials": 200, "algorithm": "cpp"}'

# Generate visualization
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{"p": 0.6, "N": 100, "algorithm": "cpp"}' \
  --output percolation.png

# View interactive API docs at http://localhost:8000/docs
```

### Local Installation

```bash
# Clone repository
git clone https://github.com/tls54/percolation-theory.git
cd percolation-theory

# Install dependencies
pip install -r requirements.txt

# (Optional) Build C++ extension for maximum speed
python setup.py build_ext --inplace

# Run tests
pytest

# Start API server
uvicorn api.main:app --reload
```

## Usage Examples

### Python Scripts

```python
from Search import find_clusters_union_find_numba_fast
from Percolation import run_percolation_trials

# Run simulation
results = run_percolation_trials(
    p=0.6,
    N=100,
    num_trials=500,
    search_algo=find_clusters_union_find_numba_fast
)
print(f"Percolation probability: {results['percolation_probability']:.3f}")
```

### REST API

```python
import requests

response = requests.post(
    "http://localhost:8000/api/simulate",
    json={"p": 0.6, "N": 50, "num_trials": 100, "algorithm": "numba"}
)
result = response.json()
print(f"Percolation probability: {result['percolation_probability']:.3f}")
```

## Documentation

- **[Usage Guide](docs/usage.md)** - Full walkthrough from setup to visualization
- **[Development Guide](docs/development.md)** - Local dev setup, testing, and profiling
- **[Algorithm Details](docs/algorithms.md)** - Deep dive into percolation models and implementation
- **[Theory Background](docs/theory.md)** - Percolation theory and critical probability
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[API Reference](api/README.md)** - REST API endpoints and examples
- **[Algorithm Implementation](Search/README.md)** - BFS, Union-Find, and C++ backend
- **[Visualization](visualization/README.md)** - Rendering options and parameters

## Project Structure

```
percolation-theory/
├── Search/              # Cluster-finding algorithms (BFS, Union-Find, C++)
├── api/                 # FastAPI backend
├── visualization/       # Rendering and color assignment
├── tests/              # Algorithm tests
├── tests_api/          # API integration tests
├── cpp/                # C++ source code
├── docs/               # Detailed documentation
├── Percolation.py      # Core simulation logic
├── Estimation.py       # Critical probability estimation
└── requirements.txt    # Dependencies
```

## Contributing

Contributions welcome! Areas of interest:
- Additional lattice types (triangular, hexagonal)
- Visualization improvements
- Performance optimizations
- Documentation enhancements
- Frontend development

See [Development Guide](docs/development.md) for setup instructions.

## License

MIT License - see LICENSE file for details.

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

## References

- Stauffer, D., & Aharony, A. (1994). Introduction to Percolation Theory
- Newman, M. E. J., & Ziff, R. M. (2000). "Efficient Monte Carlo algorithm and high-precision results for percolation"
- Hoshen, J., & Kopelman, R. (1976). "Percolation and cluster distribution"

