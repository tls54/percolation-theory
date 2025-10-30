# Development Guide

Local development setup, testing, profiling, and optimization.

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- (Optional) C++ compiler for maximum performance
- (Optional) Docker for containerized development

### Clone and Install

```bash
# Clone repository
git clone https://github.com/tls54/percolation-theory.git
cd percolation-theory

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov line_profiler

# Build C++ extension (optional)
python setup.py build_ext --inplace
```

### Verify Installation

```bash
# Run tests
pytest

# Check what's available
python -c "from Search import HAS_CPP, HAS_NUMBA; print(f'C++: {HAS_CPP}, Numba: {HAS_NUMBA}')"

# Start API server
uvicorn api.main:app --reload
```

## Project Structure

```
percolation-theory/
├── Search/              # Algorithm implementations
│   ├── BFS.py          # Breadth-first search
│   ├── UnionFind.py    # Union-Find (Python & Numba)
│   └── __init__.py     # Package exports
├── api/                 # REST API
│   ├── main.py         # FastAPI app
│   ├── routes/         # API endpoints
│   ├── services/       # Business logic
│   ├── models.py       # Pydantic models
│   └── config.py       # Configuration
├── visualization/       # Visualization module
│   ├── core.py         # Color assignment
│   ├── config.py       # Settings
│   └── renderers/
│       └── matplotlib.py
├── cpp/                # C++ source
│   └── src/
│       ├── union_find.hpp
│       └── bindings.cpp
├── tests/              # Algorithm tests
├── tests_api/          # API tests
├── docs/               # Documentation
├── Percolation.py      # Core simulation
├── Estimation.py       # p_c estimation
├── profiling.py        # Profiling utilities
├── setup.py            # C++ build config
└── requirements.txt    # Dependencies
```

## Testing

### Run All Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Test Organization

**Algorithm tests** (`tests/`):
- `test_algorithms.py`: Correctness of cluster finding
- `test_cpp_build.py`: C++ extension build verification
- `test_performance.py`: Performance benchmarks
- `test_pc_estimation.py`: Critical probability estimation

**API tests** (`tests_api/`):
- `test_health.py`: Health endpoint
- `test_simulation.py`: Simulation endpoints
- `test_visualization.py`: Visualization endpoint

### Run Specific Tests

```bash
# Just algorithm tests
pytest tests/

# Just API tests
pytest tests_api/

# Specific test file
pytest tests/test_algorithms.py

# Specific test function
pytest tests/test_algorithms.py::test_bfs_correctness

# Skip slow tests
pytest -m "not slow"

# Run only failed tests from last run
pytest --lf
```

### Test with Docker

```bash
# Run tests in container
docker-compose exec api pytest

# With coverage
docker-compose exec api pytest --cov=. --cov-report=html

# Specific tests
docker-compose exec api pytest tests/test_algorithms.py
```

### Writing Tests

Example test structure:

```python
import pytest
import numpy as np
from Search import find_clusters_bfs

def test_single_site():
    """Test grid with single occupied site."""
    grid = np.array([[True]], dtype=bool)
    clusters, num_clusters = find_clusters_bfs(grid)
    assert num_clusters == 1
    assert clusters[0, 0] == 1

def test_empty_grid():
    """Test empty grid."""
    grid = np.zeros((10, 10), dtype=bool)
    clusters, num_clusters = find_clusters_bfs(grid)
    assert num_clusters == 0
    assert np.all(clusters == 0)

@pytest.mark.slow
def test_large_grid():
    """Test large grid (marked as slow)."""
    grid = np.random.rand(500, 500) < 0.6
    clusters, num_clusters = find_clusters_bfs(grid)
    assert num_clusters > 0
```

## Profiling

### Built-in Profiling Tools

The project includes profiling utilities:

```python
from profiling import ProfilerConfig, profile_context, profile_function

# Context manager
config = ProfilerConfig(
    enabled=True,
    line_profile=True,
    output_dir='profiling_results'
)

with profile_context(config, "my_simulation"):
    # Your code here
    results = run_percolation_trials(p=0.6, N=100, num_trials=500)

# Decorator
@profile_function(config)
def my_expensive_function():
    # Function code
    pass
```

### cProfile

For function-level profiling:

```bash
# Profile a script
python -m cProfile -o profile.stats Percolation.py

# View results
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"
```

### line_profiler

For line-by-line profiling:

```bash
# Install
pip install line_profiler

# Add @profile decorator to function
# Then run:
kernprof -l -v Percolation.py
```

### Performance Testing

Run benchmark tests:

```bash
# Run performance tests
pytest tests/test_performance.py -v

# Skip slow tests during development
pytest tests/test_performance.py -m "not slow"
```

Custom benchmark:

```python
import time
import numpy as np
from Search import find_clusters_cpp

N = 100
p = 0.6
num_trials = 200

grids = [np.random.rand(N, N) < p for _ in range(num_trials)]

start = time.time()
for grid in grids:
    clusters, num_clusters = find_clusters_cpp(grid)
elapsed = time.time() - start

print(f"Time per grid: {elapsed*1000/num_trials:.2f} ms")
print(f"Grids per second: {num_trials/elapsed:.1f}")
```

## Building C++ Extension

### Development Build

```bash
# Clean old builds
rm -rf build/ Search/*.so Search/*.pyd

# Build in place
python setup.py build_ext --inplace

# Verify
python -c "from Search import HAS_CPP; print(f'C++ available: {HAS_CPP}')"
```

### Debug Build

For debugging with gdb/lldb:

```bash
# Build with debug symbols
python setup.py build_ext --inplace --debug

# Run with debugger
gdb python
> run -c "from Search import find_clusters_cpp"
```

### Modify C++ Code

After changing C++ source files:

```bash
# Rebuild
rm -rf build/ Search/*.so
python setup.py build_ext --inplace

# Run tests to verify
pytest tests/test_cpp_build.py
```

## Docker Development

### Build and Run

```bash
# Build image
docker-compose build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

### Execute Commands in Container

```bash
# Run tests
docker-compose exec api pytest

# Python shell
docker-compose exec api python

# Bash shell
docker-compose exec api bash

# Check C++ availability
docker-compose exec api python -c "from Search import HAS_CPP; print(f'C++: {HAS_CPP}')"
```

### Development Workflow

```bash
# Make code changes locally
# (Files are mounted into container)

# Rebuild if needed
docker-compose up --build

# Run tests
docker-compose exec api pytest

# Check API
curl http://localhost:8000/api/health
```

## API Development

### Start Development Server

```bash
# Auto-reload on code changes
uvicorn api.main:app --reload --port 8000

# Access at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Add New Endpoint

1. Create route function in `api/routes/`:

```python
# api/routes/my_feature.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/my-endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```

2. Register in `api/main.py`:

```python
from api.routes import my_feature

app.include_router(my_feature.router, prefix="/api")
```

3. Add tests in `tests_api/`:

```python
# tests_api/test_my_feature.py
def test_my_endpoint(client):
    response = client.get("/api/my-endpoint")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}
```

### Environment Variables

Set in `.env` file or `docker-compose.yml`:

```bash
API_TITLE=Percolation Theory API
API_VERSION=0.1.0
DEFAULT_N=50
DEFAULT_NUM_TRIALS=100
MAX_N=500
MAX_TRIALS=10000
USE_CPP=true
```

## Code Quality

### Linting

```bash
# Install tools
pip install flake8 black isort

# Check style
flake8 .

# Format code
black .

# Sort imports
isort .
```

### Type Checking

```bash
# Install mypy
pip install mypy

# Check types
mypy Search/ api/ Percolation.py Estimation.py
```

## Continuous Integration

Tests run automatically on:
- Push to main branch
- Pull requests

Local CI simulation:

```bash
# Run all checks
pytest --cov=. --cov-report=term
flake8 .
mypy .
```

## Performance Tips

### Algorithm Selection

- Development: Use BFS (simple, no dependencies)
- Testing: Use Numba (fast, no build step)
- Production: Use C++ (fastest, requires build)

### Grid Size Considerations

- N ≤ 50: All algorithms perform well
- N = 100: Numba/C++ recommended
- N ≥ 200: C++ strongly recommended
- N ≥ 500: C++ required for reasonable performance

### Optimization Checklist

- [ ] Use C++ algorithm for large grids
- [ ] Enable multiple workers in production: `--workers 4`
- [ ] Use appropriate num_trials (more isn't always better)
- [ ] Cache results when possible
- [ ] Profile before optimizing

## Contributing

### Process

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run test suite: `pytest`
5. Commit changes: `git commit -m "Add feature"`
6. Push to branch: `git push origin feature-name`
7. Create pull request

### Guidelines

- Add tests for new features
- Maintain >90% code coverage
- Follow existing code style
- Update documentation
- Keep commits focused and atomic

### Areas for Contribution

- Additional lattice types (triangular, hexagonal)
- Visualization improvements
- Performance optimizations
- Documentation enhancements
- Frontend development (web UI)

## See Also

- [Usage Guide](usage.md) - How to use the simulator
- [Algorithm Details](algorithms.md) - Implementation details
- [Troubleshooting](troubleshooting.md) - Common issues
- [API Reference](../api/README.md) - REST API documentation
