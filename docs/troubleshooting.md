# Troubleshooting

Common issues and solutions for the Percolation Theory Simulator.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [C++ Compilation Problems](#c-compilation-problems)
3. [API Issues](#api-issues)
4. [Docker Issues](#docker-issues)
5. [Performance Issues](#performance-issues)
6. [Import Errors](#import-errors)
7. [Test Failures](#test-failures)
8. [Visualization Problems](#visualization-problems)

## Installation Issues

### pip install fails

**Problem:** Error installing dependencies from requirements.txt

**Solutions:**

```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output to see error details
pip install -r requirements.txt -v

# Try installing problematic packages individually
pip install numpy
pip install numba
pip install fastapi
```

**Common causes:**
- Outdated pip version
- Missing system dependencies
- Python version too old (need 3.9+)

### Python version too old

**Problem:** "Python 3.9 or higher is required"

**Solution:**
```bash
# Check your Python version
python --version

# Install Python 3.9+ from python.org or use pyenv
pyenv install 3.10.0
pyenv local 3.10.0
```

### NumPy installation fails

**Problem:** Error building NumPy from source

**Solutions:**

**Windows:**
```bash
# Install precompiled wheel
pip install numpy --only-binary numpy
```

**Linux:**
```bash
# Install build dependencies
sudo apt-get update
sudo apt-get install python3-dev build-essential
pip install numpy
```

**macOS:**
```bash
# Install Xcode Command Line Tools
xcode-select --install
pip install numpy
```

## C++ Compilation Problems

### "Unable to find vcvarsall.bat" (Windows)

**Problem:** C++ compiler not found on Windows

**Solution:**

1. Download Visual Studio Build Tools:
   https://visualstudio.microsoft.com/downloads/

2. Install with "Desktop development with C++" workload

3. Restart terminal and try again:
   ```bash
   python setup.py build_ext --inplace
   ```

### "Python.h not found" (Linux)

**Problem:** Python development headers missing

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev

# Fedora/RHEL
sudo dnf install python3-devel

# Arch
sudo pacman -S python
```

### "clang: command not found" (macOS)

**Problem:** Xcode Command Line Tools not installed

**Solution:**
```bash
xcode-select --install

# Wait for installation to complete, then:
python setup.py build_ext --inplace
```

### C++ build succeeds but module not importable

**Problem:** Built module but can't import

**Diagnosis:**
```bash
# Check if .so file exists
ls -la Search/*.so

# Try importing with error details
python -c "from Search import find_clusters_cpp"
```

**Solutions:**

1. Check Python version matches build:
   ```bash
   python --version
   which python
   ```

2. Rebuild from clean state:
   ```bash
   rm -rf build/ Search/*.so
   python setup.py build_ext --inplace
   ```

3. Verify with test:
   ```bash
   pytest tests/test_cpp_build.py -v
   ```

### Build succeeds but HAS_CPP is False

**Problem:** C++ module built but not detected

**Solution:**
```python
# Check import manually
python -c "
try:
    from Search.percolation_cpp import find_clusters_cpp
    print('C++ module imports successfully')
except ImportError as e:
    print(f'Import failed: {e}')
"
```

## API Issues

### "Port 8000 already in use"

**Problem:** API won't start because port is occupied

**Solutions:**

1. Find what's using the port:
   ```bash
   # macOS/Linux
   lsof -i :8000

   # Windows
   netstat -ano | findstr :8000
   ```

2. Kill the process or use different port:
   ```bash
   # Use different port
   uvicorn api.main:app --port 8001

   # Or kill the process
   kill -9 <PID>
   ```

### API starts but returns 500 errors

**Problem:** Internal server error on all endpoints

**Diagnosis:**
```bash
# Check API logs
uvicorn api.main:app --reload --log-level debug

# Test health endpoint
curl http://localhost:8000/health
```

**Common causes:**
- Missing dependencies
- Import errors
- Configuration issues

**Solution:**
```bash
# Verify dependencies
pip install -r requirements.txt

# Check imports
python -c "from api.main import app"

# Run with detailed logging
uvicorn api.main:app --reload --log-level debug
```

### "Module not found" errors in API

**Problem:** API can't import Search, Percolation, etc.

**Solution:**
```bash
# Ensure running from project root
cd /path/to/percolation-theory
uvicorn api.main:app --reload

# Check PYTHONPATH if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### API endpoints return 422 validation errors

**Problem:** Request parameters rejected

**Example error:**
```json
{
  "detail": [
    {
      "loc": ["body", "N"],
      "msg": "ensure this value is greater than or equal to 10",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

**Solution:** Check request parameters match API spec:
- Visit http://localhost:8000/docs for interactive documentation
- Verify all required fields are present
- Check value ranges (N: 10-500, p: 0.0-1.0, etc.)

## Docker Issues

### Docker container won't start

**Problem:** Container exits immediately after starting

**Diagnosis:**
```bash
# Check logs
docker-compose logs api

# Check container status
docker-compose ps

# Try running without detached mode
docker-compose up
```

**Common causes:**
- Port conflicts
- Build failures
- Missing environment variables

**Solution:**
```bash
# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### C++ extension not working in Docker

**Problem:** HAS_CPP is False inside container

**Diagnosis:**
```bash
# Check inside container
docker-compose exec api python -c "from Search import HAS_CPP; print(f'C++ available: {HAS_CPP}')"

# Check build logs
docker-compose logs api | grep -i "build"
```

**Solution:**
```bash
# Rebuild container
docker-compose down
docker-compose build --no-cache

# Verify Dockerfile builds C++ extension
cat Dockerfile | grep setup.py
```

### Container keeps restarting

**Problem:** Container in restart loop

**Diagnosis:**
```bash
# Check logs for errors
docker-compose logs api

# Check health endpoint
curl http://localhost:8000/health
```

**Solutions:**

1. Check application startup:
   ```bash
   docker-compose exec api python -c "from api.main import app"
   ```

2. Verify environment variables:
   ```bash
   docker-compose exec api env | grep API_
   ```

3. Check Docker resources (CPU/memory):
   - Docker Desktop → Preferences → Resources

### Cannot connect to Docker daemon

**Problem:** "Cannot connect to the Docker daemon"

**Solutions:**

1. Start Docker Desktop (macOS/Windows)

2. Or start Docker service (Linux):
   ```bash
   sudo systemctl start docker
   ```

3. Check Docker is running:
   ```bash
   docker ps
   ```

## Performance Issues

### Simulations are very slow

**Problem:** Simulations taking much longer than expected

**Diagnosis:**
```python
from Search import HAS_CPP, HAS_NUMBA
print(f"C++: {HAS_CPP}, Numba: {HAS_NUMBA}")
```

**Solutions:**

1. **Use faster algorithm:**
   ```python
   # Instead of BFS:
   from Search import find_clusters_bfs  # Slow

   # Use Numba:
   from Search import find_clusters_union_find_numba_fast  # Fast

   # Or C++:
   from Search import find_clusters_cpp  # Fastest
   ```

2. **Build C++ extension:**
   ```bash
   python setup.py build_ext --inplace
   ```

3. **Reduce problem size:**
   - Use smaller N for testing
   - Reduce num_trials
   - Use coarser p_steps in sweeps

### First Numba call is slow

**Problem:** First simulation with Numba takes ~100ms, then fast

**Explanation:** This is expected! Numba compiles on first call.

**Solution:**
```python
# Warm-up call
import numpy as np
from Search import find_clusters_union_find_numba_fast

dummy_grid = np.random.rand(10, 10) < 0.5
find_clusters_union_find_numba_fast(dummy_grid)  # Compile
# Now subsequent calls are fast
```

### Memory issues with large grids

**Problem:** Out of memory errors with N > 1000

**Solutions:**

1. **Reduce grid size:**
   - Use N ≤ 500 for most purposes
   - Theoretical p_c is independent of N

2. **Reduce num_trials:**
   - Statistical accuracy scales as 1/√num_trials
   - 200-500 trials usually sufficient

3. **Process in batches:**
   ```python
   # Instead of one large simulation
   results_all = []
   for batch in range(10):
       results = run_percolation_trials(p, N, num_trials=100)
       results_all.append(results)
   # Combine results
   ```

## Import Errors

### "No module named 'Search'"

**Problem:** Can't import Search module

**Solutions:**

1. Check working directory:
   ```bash
   pwd  # Should be in percolation-theory/
   ls Search/  # Should see __init__.py
   ```

2. Add to PYTHONPATH if needed:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

3. Check __init__.py exists:
   ```bash
   ls Search/__init__.py
   ```

### "cannot import name 'find_clusters_cpp'"

**Problem:** C++ module not available

**Solution:** This is expected if C++ extension not built:
```python
# Use Numba instead:
from Search import find_clusters_union_find_numba_fast

# Or check if C++ is available first:
from Search import HAS_CPP
if HAS_CPP:
    from Search import find_clusters_cpp
else:
    print("C++ not available, using Numba")
```

### "cannot import name 'find_clusters_union_find_numba_fast'"

**Problem:** Numba not installed

**Solution:**
```bash
pip install numba

# Verify
python -c "import numba; print(numba.__version__)"
```

## Test Failures

### Tests fail with "No module named"

**Problem:** pytest can't find modules

**Solution:**
```bash
# Run from project root
cd /path/to/percolation-theory
pytest

# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Performance tests fail (too slow)

**Problem:** Tests fail because algorithm too slow

**Solution:**
```bash
# Skip slow tests
pytest -m "not slow"

# Or ensure C++/Numba is available
python setup.py build_ext --inplace
pytest tests/test_performance.py
```

### API tests fail

**Problem:** API integration tests failing

**Solutions:**

1. Install test dependencies:
   ```bash
   pip install pytest httpx
   ```

2. Check API can start:
   ```bash
   python -c "from api.main import app"
   ```

3. Run API tests only:
   ```bash
   pytest tests_api/ -v
   ```

## Visualization Problems

### "No module named 'matplotlib'"

**Problem:** Matplotlib not installed

**Solution:**
```bash
pip install matplotlib

# Verify
python -c "import matplotlib; print(matplotlib.__version__)"
```

### Visualization endpoint returns 500 error

**Problem:** API visualization fails

**Diagnosis:**
```bash
# Check error details
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{"p": 0.6, "N": 100, "algorithm": "numba"}'
```

**Solutions:**

1. Check matplotlib installed:
   ```bash
   docker-compose exec api python -c "import matplotlib"
   ```

2. Check algorithm available:
   ```bash
   # Use "numba" or "bfs" if "cpp" fails
   curl ... -d '{"p": 0.6, "N": 100, "algorithm": "numba"}'
   ```

### Generated images are blank

**Problem:** PNG returned but image is blank

**Cause:** p value too low or too high

**Solution:**
```bash
# Use p near critical point (0.59)
curl ... -d '{"p": 0.6, "N": 100, ...}'

# Not:
curl ... -d '{"p": 0.01, "N": 100, ...}'  # Too low, no clusters
```

### Colors look wrong

**Problem:** Cluster colors aren't distinct

**Solutions:**

1. Try different colormap:
   ```json
   {"colormap": "viridis"}  // or "tab20", "Set3", etc.
   ```

2. Adjust min_cluster_size:
   ```json
   {"min_cluster_size": 20}  // Show fewer, larger clusters
   ```

## Getting More Help

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check System Information

```bash
# Python version and packages
python --version
pip list

# Check available algorithms
python -c "
from Search import HAS_CPP, HAS_NUMBA
print(f'C++ available: {HAS_CPP}')
print(f'Numba available: {HAS_NUMBA}')
"

# Run diagnostics
pytest tests/test_cpp_build.py -v
```

### Report Issues

If you can't resolve the issue:

1. Check existing issues: https://github.com/tls54/percolation-theory/issues

2. Create new issue with:
   - Operating system and version
   - Python version
   - Full error message
   - Steps to reproduce

## See Also

- [Development Guide](development.md) - Testing and debugging
- [Usage Guide](usage.md) - How to use the simulator
- [API Reference](../api/README.md) - API documentation
