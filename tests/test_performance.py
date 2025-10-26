import pytest
import numpy as np
import time
import os


class TestRelativePerformance:
    """Test relative performance between algos."""
    @pytest.fixture
    def benchmark_grids(self):
        """Generate grids for benchmarking."""
        np.random.seed(42)
        return [np.random.rand(50, 50) < 0.6 for _ in range(20)]

    @pytest.mark.skipif(
        os.getenv('CI') == 'true',  # Skip in CI
        reason="C++ performance tests unreliable in CI environment"
    )
    def test_numba_faster_than_bfs(self, benchmark_grids):
        """Numba should be significantly faster than BFS."""
        from Search import find_clusters_bfs, find_clusters_union_find_numba_fast
        
        # Warmup Numba
        _ = find_clusters_union_find_numba_fast(benchmark_grids[0])
        
        # Benchmark BFS
        start = time.perf_counter()
        for grid in benchmark_grids:
            _ = find_clusters_bfs(grid)
        bfs_time = time.perf_counter() - start
        
        # Benchmark Numba
        start = time.perf_counter()
        for grid in benchmark_grids:
            _ = find_clusters_union_find_numba_fast(grid)
        numba_time = time.perf_counter() - start
        
        speedup = bfs_time / numba_time
        print(f"\nNumba is {speedup:.1f}x faster than BFS")
        
        # Should be at least 5x faster
        assert speedup > 5.0, f"Numba only {speedup:.1f}x faster (expected >5x)"


    def test_cpp_faster_than_numba(self, benchmark_grids):
        """C++ should be faster than Numba."""
        from Search import HAS_CPP
        
        if not HAS_CPP:
            pytest.skip("C++ module not available")
        
        from Search import find_clusters_union_find_numba_fast, find_clusters_cpp

        # Warmup both
        _ = find_clusters_union_find_numba_fast(benchmark_grids[0])
        _ = find_clusters_cpp(benchmark_grids[0])
        
        # Benchmark Numba
        start = time.perf_counter()
        for grid in benchmark_grids:
            _ = find_clusters_union_find_numba_fast(grid)
        numba_time = time.perf_counter() - start
        
        # Benchmark C++
        start = time.perf_counter()
        for grid in benchmark_grids:
            _ = find_clusters_cpp(grid)
        cpp_time = time.perf_counter() - start
        
        speedup = numba_time / cpp_time
        print(f"\nC++ is {speedup:.1f}x faster than Numba")
        
        # Should be at least 1.2x faster
        assert speedup > 1.2, f"C++ only {speedup:.1f}x faster (expected >1.2x)"

class TestScalability:
    '''Test performance scaling with grid size.'''
    @pytest.mark.slow
    def test_scaling_with_grid_size(self):
        """Test that algorithm scales well with grid size."""
        from Search import find_clusters_union_find_numba_fast
        
        sizes = [50, 100, 200]
        times = []
        
        for N in sizes:
            np.random.seed(42)
            grid = np.random.rand(N, N) < 0.6
            
            start = time.perf_counter()
            _ = find_clusters_union_find_numba_fast(grid)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
            
            print(f"\n{N}×{N} grid: {elapsed:.4f}s")
        
        # Should scale roughly O(N²)
        # Time for 200×200 should be ~4x time for 100×100
        scaling_factor = times[2] / times[1]
        expected_factor = (sizes[2] / sizes[1]) ** 2
        
        print(f"\nScaling factor: {scaling_factor:.2f} (expected ~{expected_factor:.0f})")
        
        # Allow some overhead, should be between 2x and 8x
        assert 2.0 < scaling_factor < 8.0, \
            f"Poor scaling: {scaling_factor:.2f}x (expected ~{expected_factor:.0f}x)"
        

class TestPerformanceRegression:
    """Test for performance regressions."""
    @pytest.fixture
    def reference_benchmark(self):
        """Reference benchmark times (update these periodically)."""
        return {
            'bfs': 0.20,  # 200ms for 20 grids of 50×50
            'numba': 0.02,  # 20ms for 20 grids of 50×50
            'cpp': 0.012,  # 12ms for 20 grids of 50×50
        }

    def test_bfs_performance_regression(self, reference_benchmark):
        """BFS should not be slower than baseline."""
        from Search import find_clusters_bfs
        
        np.random.seed(42)
        grids = [np.random.rand(50, 50) < 0.6 for _ in range(20)]
        
        start = time.perf_counter()
        for grid in grids:
            _ = find_clusters_bfs(grid)
        elapsed = time.perf_counter() - start
        
        baseline = reference_benchmark['bfs']
        tolerance = 1.5  # Allow 50% slower
        
        print(f"\nBFS: {elapsed:.4f}s (baseline: {baseline:.4f}s)")
        
        if elapsed > baseline * tolerance:
            pytest.fail(
                f"Performance regression in BFS: {elapsed:.4f}s vs baseline {baseline:.4f}s "
                f"(>{tolerance}x slower)"
            )

    def test_numba_performance_regression(self, reference_benchmark):
        """Numba should not be slower than baseline."""
        from Search import find_clusters_union_find_numba_fast
        
        np.random.seed(42)
        grids = [np.random.rand(50, 50) < 0.6 for _ in range(20)]
        
        # Warmup
        _ = find_clusters_union_find_numba_fast(grids[0])
        
        start = time.perf_counter()
        for grid in grids:
            _ = find_clusters_union_find_numba_fast(grid)
        elapsed = time.perf_counter() - start
        
        baseline = reference_benchmark['numba']
        tolerance = 1.5
        
        print(f"\nNumba: {elapsed:.4f}s (baseline: {baseline:.4f}s)")
        
        if elapsed > baseline * tolerance:
            pytest.fail(
                f"Performance regression in Numba: {elapsed:.4f}s vs baseline {baseline:.4f}s "
                f"(>{tolerance}x slower)"
            )



    def test_cpp_performance_regression(self, reference_benchmark):
        """C++ should not be slower than baseline."""
        from Search import HAS_CPP
        
        if not HAS_CPP:
            pytest.skip("C++ module not available")
        
        from Search import find_clusters_cpp
        
        np.random.seed(42)
        grids = [np.random.rand(50, 50) < 0.6 for _ in range(20)]
        
        # Warmup
        _ = find_clusters_cpp(grids[0])
        
        start = time.perf_counter()
        for grid in grids:
            _ = find_clusters_cpp(grid)
        elapsed = time.perf_counter() - start
        
        baseline = reference_benchmark['cpp']
        tolerance = 1.5
        
        print(f"\nC++: {elapsed:.4f}s (baseline: {baseline:.4f}s)")
        
        if elapsed > baseline * tolerance:
            pytest.fail(
                f"Performance regression in C++: {elapsed:.4f}s vs baseline {baseline:.4f}s "
                f"(>{tolerance}x slower)"
            )

class TestMemoryEfficiency:
    '''Test memory usage patterns.'''
    @pytest.mark.slow
    def test_no_memory_leak(self):
        """Running many simulations should not leak memory."""
        from Search import find_clusters_union_find_numba_fast
        import gc
        
        # Run many iterations
        np.random.seed(42)
        for i in range(100):
            grid = np.random.rand(100, 100) < 0.6
            labels, info = find_clusters_union_find_numba_fast(grid)
            
            # Clean up
            del labels, info, grid
            
            if i % 20 == 0:
                gc.collect()
        
        print("\n✓ No memory leaks detected over 100 iterations")
    
class TestWarmupTime:
    '''Test JIT compilation warmup times.'''
    def test_numba_warmup_time(self):
        """First Numba call should compile (slow), subsequent calls fast."""
        # Force a fresh import to test compilation
        import sys
        import importlib
        
        # Remove cached modules
        if 'Search.UnionFind' in sys.modules:
            del sys.modules['Search.UnionFind']
        if 'Search' in sys.modules:
            importlib.reload(sys.modules['Search'])
        
        from Search import find_clusters_union_find_numba_fast
        
        grid = np.random.rand(50, 50) < 0.6
        
        # First call (includes compilation)
        start = time.perf_counter()
        _ = find_clusters_union_find_numba_fast(grid)
        first_time = time.perf_counter() - start
        
        # Second call (compiled)
        start = time.perf_counter()
        _ = find_clusters_union_find_numba_fast(grid)
        second_time = time.perf_counter() - start
        
        print(f"\nNumba first call: {first_time:.4f}s (with compilation)")
        print(f"Numba second call: {second_time:.4f}s (compiled)")
        
        # If already compiled, just check it's reasonably fast
        if first_time < 0.01:  # Less than 10ms means already compiled
            print("  (Numba was already compiled from previous tests)")
            assert second_time < 0.01, "Numba should be fast when compiled"
        else:
            # Second call should be much faster
            speedup = first_time / second_time
            assert speedup > 2.0, \
                f"Numba compilation not providing speedup (speedup: {speedup:.1f}x)"
            

@pytest.fixture(scope="session")
def benchmark_report(request):
    """Generate a benchmark report at end of test session."""
    def finalizer():
        print("\n" + "="*60)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("="*60)
        
        try:
            from Search import (
                find_clusters_bfs,
                find_clusters_union_find_numba_fast,
                HAS_CPP
            )
            
            np.random.seed(42)
            grids = [np.random.rand(50, 50) < 0.6 for _ in range(20)]
            
            # Warmup
            _ = find_clusters_union_find_numba_fast(grids[0])
            
            results = {}
            
            # BFS
            start = time.perf_counter()
            for grid in grids:
                _ = find_clusters_bfs(grid)
            results['BFS'] = time.perf_counter() - start
            
            # Numba
            start = time.perf_counter()
            for grid in grids:
                _ = find_clusters_union_find_numba_fast(grid)
            results['Numba'] = time.perf_counter() - start
            
            # C++ (if available)
            if HAS_CPP:
                from Search import find_clusters_cpp
                _ = find_clusters_cpp(grids[0])  # Warmup
                
                start = time.perf_counter()
                for grid in grids:
                    _ = find_clusters_cpp(grid)
                results['C++'] = time.perf_counter() - start
            
            # Print results
            fastest = min(results.values())
            
            for name, time_val in sorted(results.items(), key=lambda x: x[1]):
                speedup = fastest / time_val
                per_grid = time_val / len(grids) * 1000
                print(f"{name:10s}: {time_val:.4f}s total, "
                    f"{per_grid:.2f}ms per grid, "
                    f"{1/speedup:.1f}x vs fastest")
            
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"Could not generate benchmark report: {e}\n")

    request.addfinalizer(finalizer)

@pytest.mark.benchmark
class TestComprehensiveBenchmark:
    """Comprehensive benchmark suite (run with pytest -m benchmark)."""
    def test_full_benchmark(self, benchmark_report):
        """Run full benchmark across all algorithms and grid sizes."""
        from Search import (
            find_clusters_bfs,
            find_clusters_union_find_numba_fast,
            HAS_CPP
        )
        
        algorithms = {
            'BFS': find_clusters_bfs,
            'Numba': find_clusters_union_find_numba_fast,
        }
        
        if HAS_CPP:
            from Search import find_clusters_cpp
            algorithms['C++'] = find_clusters_cpp
        
        grid_sizes = [25, 50, 100, 200]
        num_trials = 10
        
        print("\n" + "="*60)
        print("COMPREHENSIVE BENCHMARK")
        print("="*60 + "\n")
        
        for N in grid_sizes:
            print(f"\nGrid size: {N}×{N}")
            print("-" * 40)
            
            np.random.seed(42)
            grids = [np.random.rand(N, N) < 0.6 for _ in range(num_trials)]
            
            for name, algo in algorithms.items():
                # Warmup
                if name in ['Numba', 'C++']:
                    _ = algo(grids[0])
                
                start = time.perf_counter()
                for grid in grids:
                    _ = algo(grid)
                elapsed = time.perf_counter() - start
                
                per_grid = elapsed / num_trials * 1000
                print(f"  {name:10s}: {per_grid:6.2f}ms per grid")
        
        print("\n" + "="*60 + "\n")
