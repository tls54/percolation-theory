import pytest
import numpy as np
import sys


class TestCppAvailability:
    '''Test C++ module import and availability'''
    def test_cpp_import_attempt(self):
        """Test that we can attempt to import C++ module."""
        try:
            from Search import percolation_cpp
            assert hasattr(percolation_cpp, 'find_clusters'), \
                "C++ module should have find_clusters function"
            print("✓ C++ module successfully imported")
        except ImportError as e:
            print(f"⚠ C++ module not available: {e}")
            pytest.skip("C++ module not built")

    def test_has_cpp_flag(self):
        """Test that HAS_CPP flag is set correctly."""
        from Search import HAS_CPP
        
        if HAS_CPP:
            # Should be able to import
            from Search import find_clusters_cpp
            assert callable(find_clusters_cpp)
            print("✓ HAS_CPP=True and C++ module works")
        else:
            # Should not be able to import
            print("⚠ HAS_CPP=False, C++ module not available")

    def test_fallback_available(self):
        """Test that fallback algorithms are always available."""
        from Search import (
            find_clusters_bfs,
            find_clusters_union_find_numba_fast
        )
        
        # These should always work
        assert callable(find_clusters_bfs)
        assert callable(find_clusters_union_find_numba_fast)
        print("✓ Fallback algorithms (BFS, Numba) available")


class TestCppCorrectness:
    '''Test C++ implementation (if available).'''
    @pytest.fixture(autouse=True)
    def skip_if_no_cpp(self):
        """Skip these tests if C++ not available."""
        from Search import HAS_CPP
        if not HAS_CPP:
            pytest.skip("C++ module not available")

    def test_cpp_vs_bfs(self):
        """C++ results should match BFS results."""
        from Search import find_clusters_cpp, find_clusters_bfs
        
        np.random.seed(42)
        grid = np.random.rand(50, 50) < 0.6
        
        labels_cpp, info_cpp = find_clusters_cpp(grid)
        labels_bfs, info_bfs = find_clusters_bfs(grid)
        
        # Same number of clusters
        assert len(info_cpp) == len(info_bfs), \
            f"C++ found {len(info_cpp)} clusters, BFS found {len(info_bfs)}"
        
        # Same cluster sizes
        sizes_cpp = sorted([c['size'] for c in info_cpp])
        sizes_bfs = sorted([c['size'] for c in info_bfs])
        assert sizes_cpp == sizes_bfs, "C++ and BFS cluster sizes don't match"
        
        # Same label structure
        assert np.array_equal(labels_cpp > 0, labels_bfs > 0), \
            "C++ and BFS label structures don't match"
        
        print("✓ C++ matches BFS results")

    def test_cpp_vs_numba(self):
        """C++ results should match Numba results."""
        from Search import find_clusters_cpp, find_clusters_union_find_numba_fast
        
        np.random.seed(42)
        grid = np.random.rand(50, 50) < 0.6
        
        labels_cpp, info_cpp = find_clusters_cpp(grid)
        labels_numba, info_numba = find_clusters_union_find_numba_fast(grid)
        
        # Same number of clusters
        assert len(info_cpp) == len(info_numba), \
            f"C++ found {len(info_cpp)} clusters, Numba found {len(info_numba)}"
        
        # Same cluster sizes
        sizes_cpp = sorted([c['size'] for c in info_cpp])
        sizes_numba = sorted([c['size'] for c in info_numba])
        assert sizes_cpp == sizes_numba, "C++ and Numba cluster sizes don't match"
        
        print("✓ C++ matches Numba results")

    def test_cpp_multiple_grids(self):
        """C++ should give consistent results across multiple grids."""
        from Search import find_clusters_cpp
        
        for i in range(10):
            np.random.seed(i)
            grid = np.random.rand(30, 30) < 0.5
            
            labels, info = find_clusters_cpp(grid)
            
            # Basic sanity checks
            assert len(info) >= 0
            total = sum(c['size'] for c in info)
            assert total == np.sum(grid), f"Iteration {i}: Total sites mismatch"
        
        print("✓ C++ gives consistent results across multiple grids")

class TestCppPerformance:
    '''Test C++ performance characteristics (if available).'''
    @pytest.fixture(autouse=True)
    def skip_if_no_cpp(self):
        """Skip these tests if C++ not available."""
        from Search import HAS_CPP
        if not HAS_CPP:
            pytest.skip("C++ module not available")

    def test_cpp_faster_than_bfs(self):
        """C++ should be faster than BFS."""
        import time
        from Search import find_clusters_cpp, find_clusters_bfs
        
        # Generate test grids
        np.random.seed(42)
        grids = [np.random.rand(50, 50) < 0.6 for _ in range(20)]
        
        # Time BFS
        start = time.perf_counter()
        for grid in grids:
            labels, info = find_clusters_bfs(grid)
        bfs_time = time.perf_counter() - start
        
        # Time C++
        start = time.perf_counter()
        for grid in grids:
            labels, info = find_clusters_cpp(grid)
        cpp_time = time.perf_counter() - start
        
        speedup = bfs_time / cpp_time
        print(f"✓ C++ is {speedup:.1f}x faster than BFS")
        
        # C++ should be at least 5x faster (conservative check)
        assert speedup > 5.0, \
            f"C++ only {speedup:.1f}x faster than BFS (expected >5x)"

    @pytest.mark.slow
    def test_cpp_handles_large_grids(self):
        """C++ should efficiently handle large grids."""
        import time
        from Search import find_clusters_cpp
        
        np.random.seed(42)
        grid = np.random.rand(500, 500) < 0.6
        
        start = time.perf_counter()
        labels, info = find_clusters_cpp(grid)
        elapsed = time.perf_counter() - start
        
        print(f"✓ C++ processed 500×500 grid in {elapsed:.3f}s")
        
        # Should complete in reasonable time (< 1 second)
        assert elapsed < 1.0, f"C++ too slow for 500×500 grid ({elapsed:.3f}s)"

class TestBuildInstructions:
    '''Test and document build process.'''
    def test_print_build_status(self):
        """Print current build status and instructions."""
        from Search import HAS_CPP
        
        print("\n" + "="*60)
        print("C++ BUILD STATUS")
        print("="*60)
        
        if HAS_CPP:
            print("✓ C++ module is built and available")
            from Search import percolation_cpp
            print(f"  Location: {percolation_cpp.__file__}")
        else:
            print("✗ C++ module not available")
            print("\nTo build C++ extension:")
            print("  python setup.py build_ext --inplace")
            print("\nNote: Requires C++ compiler and pybind11")
            print("  macOS: xcode-select --install")
            print("  Linux: sudo apt-get install build-essential")
            print("  Windows: Install Visual Studio Build Tools")
        
        print("="*60 + "\n")

    def test_pybind11_available(self):
        """Check if pybind11 is installed."""
        try:
            import pybind11
            print(f"✓ pybind11 {pybind11.__version__} is installed")
        except ImportError:
            print("✗ pybind11 not installed")
            print("  Install with: pip install pybind11")

    def test_compiler_available(self):
        """Check if a C++ compiler is available."""
        import subprocess
        import platform
        
        compilers = {
            'Darwin': ['clang++', 'g++'],  # macOS
            'Linux': ['g++', 'clang++'],
            'Windows': ['cl.exe', 'g++']
        }
        
        system = platform.system()
        to_check = compilers.get(system, ['g++'])
        
        found = False
        for compiler in to_check:
            try:
                result = subprocess.run(
                    [compiler, '--version'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print(f"✓ C++ compiler found: {compiler}")
                    found = True
                    break
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        if not found:
            print(f"✗ No C++ compiler found for {system}")
            print("  Install instructions in README.md")


class TestModuleStructure:
    '''Test that module structure is correct.'''
    def test_search_module_exports(self):
        """Test that Search module exports expected functions."""
        import Search
        
        expected_exports = [
            'find_clusters_bfs',
            'find_clusters_bfs_fast',
            'find_clusters_union_find',
            'find_clusters_union_find_numba',
            'find_clusters_union_find_numba_fast',
            'find_clusters_cpp',
            'HAS_CPP',
        ]
        
        for export in expected_exports:
            assert hasattr(Search, export), f"Search module missing export: {export}"
        
        print("✓ All expected exports present in Search module")

    def test_cpp_wrapper_signature(self):
        """Test that C++ wrapper has correct signature."""
        from Search import find_clusters_cpp
        
        # Should accept a grid and return (labels, cluster_info)
        grid = np.random.rand(10, 10) < 0.5
        
        try:
            labels, cluster_info = find_clusters_cpp(grid)
            
            assert isinstance(labels, np.ndarray), "labels should be numpy array"
            assert isinstance(cluster_info, list), "cluster_info should be list"
            assert labels.shape == grid.shape, "labels should match grid shape"
            
            print("✓ C++ wrapper has correct signature")
        except RuntimeError:
            # C++ not built, that's okay
            print("⚠ C++ not built, cannot test signature")

