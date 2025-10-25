# Testing Guide

Comprehensive test suite for the **Percolation Theory Simulator**, covering algorithm correctness, C++ integration, performance benchmarks, and p_c estimation.

---

## Quick Start

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=Search --cov=Percolation --cov=pc_estimation --cov-report=html
```

---

## Test Organization

### `test_algorithms.py`
Algorithm correctness and consistency tests:

- ✅ Empty/full grid edge cases – Verify boundary conditions  
- ✅ Cluster identification – Correct counting and sizing  
- ✅ Algorithm consistency – All implementations give identical results  
- ✅ Percolation detection – Spanning cluster identification  
- ✅ Large grid handling – Performance on 100×100 and 500×500 grids  
- ✅ Data type handling – Boolean arrays, type conversions  

**Example tests:**

- Single isolated sites form size-1 clusters  
- Diagonal sites not connected (4-connectivity only)  
- Full grid creates exactly one cluster of size N²  

---

### `test_cpp_build.py`
C++ extension build verification and fallback:

- ✅ Import availability – Check if C++ module loads  
- ✅ HAS_CPP flag – Verify correct detection  
- ✅ Fallback behavior – Ensure Numba/BFS work without C++  
- ✅ C++ vs Python correctness – Results match across implementations  
- ✅ Performance verification – C++ faster than Python  
- ✅ Build instructions – Print setup guidance  

**What's tested:**

- C++ module imports without errors  
- Results identical to BFS and Numba implementations  
- C++ achieves expected speedup (>5× vs BFS)  
- Graceful degradation when C++ unavailable  

---

### `test_performance.py`
Performance benchmarks and regression detection:

- ✅ Relative performance – Numba > BFS, C++ > Numba  
- ✅ Scalability – O(N²) scaling verification  
- ✅ Regression detection – Performance doesn’t degrade  
- ✅ Memory efficiency – No memory leaks over many iterations  
- ✅ JIT warmup – Numba compilation overhead measurement  

**Benchmarks include:**

- 20 grids of 50×50 at p=0.6  
- Scaling tests up to 200×200 grids  
- Comprehensive multi-algorithm comparison  

---

### `test_pc_estimation.py`
Critical probability estimation accuracy:

- ✅ Sigmoid function – Correct mathematical behavior  
- ✅ Perfect data recovery – Exact p_c from noise-free sigmoid  
- ✅ Noisy data handling – Robust to realistic noise levels  
- ✅ Edge cases – Insufficient/flat/no transition data  
- ✅ Complete analysis – Full pipeline testing  

**Accuracy targets:**

| Condition | Target Error |
|------------|---------------|
| Perfect sigmoid data | < 0.1% |
| Noisy realistic data | < 1% |
| High-quality simulation (N=200, 200 trials) | < 0.1% |

---

## Running Tests

### Basic Usage

```bash
# All tests
pytest

# Specific test file
pytest tests/test_algorithms.py

# Specific test class
pytest tests/test_algorithms.py::TestAlgorithmCorrectness

# Specific test
pytest tests/test_algorithms.py::TestAlgorithmCorrectness::test_empty_grid

# Stop on first failure
pytest -x

# Show print statements
pytest -s
```

### Verbosity Levels

```bash
# Quiet (minimal output)
pytest -q

# Normal (default)
pytest

# Verbose (show each test)
pytest -v

# Very verbose (show full diff on failure)
pytest -vv
```

### Test Selection

```bash
# Run only fast tests (skip slow)
pytest -m "not slow"

# Run only slow tests
pytest -m slow

# Run only benchmark tests
pytest -m benchmark

# Run C++-related tests only
pytest -m cpp

# Run multiple markers
pytest -m "benchmark or cpp"
```

---

## Coverage Reports

```bash
# Terminal coverage summary
pytest --cov=Search --cov=Percolation --cov=pc_estimation

# HTML coverage report
pytest --cov=Search --cov=Percolation --cov=pc_estimation --cov-report=html
# Open htmlcov/index.html in browser

# Generate coverage badge
pytest --cov=Search --cov-report=term-missing

# Coverage with branch analysis
pytest --cov=Search --cov-branch
```

---

## Parallel Execution

```bash
# Install plugin
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4

# Auto-detect CPU count
pytest -n auto
```

---

## Failed Test Management

```bash
# Re-run only failed tests
pytest --lf

# Run failed first, then others
pytest --ff

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb
```

---

## Output Control

```bash
# Capture output (default)
pytest

# Don't capture output (see prints)
pytest -s

# Show full test output
pytest --tb=long

# Show only first and last line of traceback
pytest --tb=short

# No traceback
pytest --tb=no

# Show summary of all test outcomes
pytest -ra
```

---

## Test Markers

Tests are organized with markers for selective execution:

```python
@pytest.mark.slow        # Tests taking >5 seconds (large grids, many iterations)
@pytest.mark.benchmark   # Performance benchmark tests
@pytest.mark.cpp         # Tests requiring C++ module
```

**Using markers:**

```bash
# Skip slow tests
pytest -m "not slow"

# Run only benchmarks
pytest -m benchmark

# Run everything except benchmarks
pytest -m "not benchmark"
```

---

## Continuous Integration

Tests run automatically on:

- Every push to main branch  
- Every pull request  
- Nightly (includes slow tests)

CI configuration: `.github/workflows/tests.yml` (when added)

---

## Common Issues

### "C++ module not available"

**Cause:** C++ extension not built  
**Solution:**

```bash
# Build C++ module
python setup.py build_ext --inplace

# Or skip C++ tests
pytest -m "not cpp"
```

### "ModuleNotFoundError: No module named 'Search'"

**Cause:** Running tests from wrong directory  
**Solution:**

```bash
cd /path/to/percolation-theory
pytest
```

### Tests failing after code changes

**Diagnosis:**

```bash
pytest -vv --tb=long
pytest -l
```

**Solutions:**

- Check if algorithm behavior intentionally changed  
- Update test expectations if correct  
- Fix bugs if unintentional  

---

## Writing New Tests

### Test Structure

```python
class TestFeatureName:
    """Description of what this test class covers."""

    def test_specific_behavior(self):
        """Test that X does Y under condition Z."""
        input_data = create_test_input()
        result = function_under_test(input_data)
        assert result == expected_output
        assert result.property == expected_value
```

### Using Fixtures

```python
def test_with_sample_grids(self, sample_grids):
    grid = sample_grids['random_small']
    # ... test code

def test_with_algorithms(self, algorithms):
    for name, algo in algorithms.items():
        # ... test each algorithm
```

**Available fixtures (from `conftest.py`):**

- `sample_grids` – Pre-generated test grids  
- `algorithms` – Dict of available search algorithms  

---

### Parametrized Tests

```python
@pytest.mark.parametrize("N,p,expected_percolates", [
    (10, 0.3, False),
    (10, 0.6, True),
    (50, 0.59, "sometimes"),
])
def test_percolation_by_params(self, N, p, expected_percolates):
    # Test runs 3 times with different inputs
```

---

### Skipping Tests

```python
@pytest.mark.skipif(not HAS_CPP, reason="C++ not available")
def test_cpp_feature(self):
    # ...
```

---

## Test Coverage Goals

| Component | Target Coverage |
|------------|----------------|
| Search algorithms | >95% |
| Percolation logic | >90% |
| p_c estimation | >85% |
| Overall | >90% |

Check current coverage:

```bash
pytest --cov=. --cov-report=term-missing
```

---

## Performance Baselines

| Algorithm | Target Time | Threshold |
|------------|--------------|------------|
| BFS | ~200ms | <300ms |
| Numba | ~20ms | <40ms |
| C++ | ~12ms | <25ms |

Update baselines in `test_performance.py::TestPerformanceRegression` if:

- Hardware significantly different  
- Algorithm improved  
- Python/NumPy version changed  

---

## Best Practices

- ✅ Test behavior, not implementation  
- ✅ One assertion per concept  
- ✅ Clear names (`test_empty_grid_has_no_clusters`)  
- ✅ Arrange–Act–Assert structure  
- ✅ Independent tests  
- ✅ Mark slow tests with `@pytest.mark.slow`  
- ✅ Use descriptive assertions  

---

## Debugging Tests

```bash
pytest --pdb        # Debug on failure
pytest --trace      # Debug at test start
pytest -l           # Show local variables
pytest -vv          # Verbose with full diff
pytest --cache-show # Keep cache for inspection
```

---

## Resources

- [pytest documentation](https://docs.pytest.org)
- [pytest-cov plugin](https://pytest-cov.readthedocs.io)
- [Testing Best Practices](https://realpython.com/pytest-python-testing/)

---

**Last Updated:** 2025-01-26  
**Test Count:** 43 tests across 4 files  
**Typical Run Time:** ~2 seconds (excluding slow tests)
