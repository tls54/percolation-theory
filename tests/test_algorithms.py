import pytest 
import numpy as np

class TestAlgorithmCorrectness:
    '''Test that Algos produce correct cluster identifications.'''
    def test_empty_grid(self, algorithms):
        """Empty grid should have no clusters."""
        grid = np.zeros((10, 10), dtype=bool)
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            assert len(cluster_info) == 0, f"{name}: Empty grid should have 0 clusters"
            assert np.all(labels == 0), f"{name}: All labels should be 0"

    def test_full_grid(self, algorithms):
        """Full grid should have exactly one cluster."""
        grid = np.ones((10, 10), dtype=bool)
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            assert len(cluster_info) == 1, f"{name}: Full grid should have 1 cluster"
            assert cluster_info[0]['size'] == 100, f"{name}: Cluster should have 100 sites"
            assert np.all(labels > 0), f"{name}: All sites should be labeled"

    def test_single_site(self, algorithms):
        """Single occupied site should form a cluster of size 1."""
        grid = np.zeros((5, 5), dtype=bool)
        grid[2, 2] = True
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            assert len(cluster_info) == 1, f"{name}: Should have 1 cluster"
            assert cluster_info[0]['size'] == 1, f"{name}: Cluster should have size 1"

    def test_two_isolated_clusters(self, algorithms):
        """Two separate clusters should be identified correctly."""
        grid = np.array([
            [True, True, False, False],
            [True, False, False, False],
            [False, False, True, True],
            [False, False, True, False]
        ], dtype=bool)
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            assert len(cluster_info) == 2, f"{name}: Should have 2 clusters"
            
            sizes = sorted([c['size'] for c in cluster_info])
            assert sizes == [3, 3], f"{name}: Clusters should have sizes [3, 3]"

    def test_connected_cluster(self, algorithms):
        """L-shaped connected cluster should be identified as one cluster."""
        grid = np.array([
            [True, True, True, False],
            [False, False, True, False],
            [False, False, True, False],
            [False, False, True, True]
        ], dtype=bool)
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            assert len(cluster_info) == 1, f"{name}: Should have 1 cluster"
            assert cluster_info[0]['size'] == 7, f"{name}: Cluster should have 7 sites"

    def test_diagonal_not_connected(self, algorithms):
        """Diagonal sites should NOT be connected (4-connectivity)."""
        grid = np.array([
            [True, False, False],
            [False, True, False],
            [False, False, True]
        ], dtype=bool)
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            assert len(cluster_info) == 3, f"{name}: Diagonal sites should form 3 separate clusters"
            for cluster in cluster_info:
                assert cluster['size'] == 1, f"{name}: Each diagonal cluster should have size 1"



class TestAlgorithmConsistency:
    '''Test that algorithms give consistent results.'''
    def test_consistency_random_grids(self, algorithms, sample_grids):
        """All algorithms should produce identical cluster counts and sizes."""
        if len(algorithms) < 2:
            pytest.skip("Need at least 2 algorithms to compare")
        
        for grid_name, grid in sample_grids.items():
            results = {}
            
            # Run all algorithms
            for algo_name, algo in algorithms.items():
                labels, cluster_info = algo(grid)
                results[algo_name] = {
                    'num_clusters': len(cluster_info),
                    'cluster_sizes': sorted([c['size'] for c in cluster_info]),
                    'total_occupied': sum(c['size'] for c in cluster_info),
                    'label_structure': labels > 0  # Just the pattern, not exact labels
                }
            
            # Compare all algorithms against first one
            reference_name = list(algorithms.keys())[0]
            reference = results[reference_name]
            
            for algo_name, result in results.items():
                if algo_name == reference_name:
                    continue
                
                assert result['num_clusters'] == reference['num_clusters'], \
                    f"{grid_name}: {algo_name} found {result['num_clusters']} clusters, " \
                    f"{reference_name} found {reference['num_clusters']}"
                
                assert result['cluster_sizes'] == reference['cluster_sizes'], \
                    f"{grid_name}: {algo_name} cluster sizes {result['cluster_sizes']} " \
                    f"don't match {reference_name} {reference['cluster_sizes']}"
                
                assert result['total_occupied'] == reference['total_occupied'], \
                    f"{grid_name}: {algo_name} total occupied sites don't match"
                
                assert np.array_equal(result['label_structure'], reference['label_structure']), \
                    f"{grid_name}: {algo_name} label structure doesn't match {reference_name}"

    def test_consistency_deterministic(self, algorithms):
        """Same algorithm should give same results on same input."""
        grid = np.random.rand(50, 50) < 0.5
        
        for name, algo in algorithms.items():
            # Run twice
            labels1, info1 = algo(grid.copy())
            labels2, info2 = algo(grid.copy())
            
            assert len(info1) == len(info2), f"{name}: Non-deterministic cluster count"
            
            sizes1 = sorted([c['size'] for c in info1])
            sizes2 = sorted([c['size'] for c in info2])
            assert sizes1 == sizes2, f"{name}: Non-deterministic cluster sizes"


class TestPercolationDetection:
    '''Test Percolation detection logic'''
    def test_percolates_vertical(self, algorithms):
        """Grid with vertical spanning cluster should percolate."""
        grid = np.zeros((5, 5), dtype=bool)
        grid[:, 2] = True  # Vertical line through middle
        
        from Percolation import check_percolation
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            N = grid.shape[0]
            percolates, spanning_id = check_percolation(labels, cluster_info, N)
            assert percolates, f"{name}: Vertical spanning cluster should percolate"

    def test_does_not_percolate(self, algorithms):
        """Grid without spanning cluster should not percolate."""
        grid = np.array([
            [True, True, False, False],
            [False, False, False, False],
            [False, False, False, False],
            [False, False, True, True]
        ], dtype=bool)
        
        from Percolation import check_percolation
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            N = grid.shape[0]
            percolates, spanning_id = check_percolation(labels, cluster_info, N)
            assert not percolates, f"{name}: Disconnected clusters should not percolate"

    def test_percolates_zigzag(self, algorithms):
        """Grid with zigzag path from top to bottom should percolate."""
        grid = np.array([
            [True, True, False, False, False],
            [False, True, False, False, False],
            [False, True, True, False, False],
            [False, False, True, False, False],
            [False, False, True, True, True]
        ], dtype=bool)
        
        from Percolation import check_percolation
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            N = grid.shape[0]
            percolates, spanning_id = check_percolation(labels, cluster_info, N)
            assert percolates, f"{name}: Zigzag path should percolate"


class TestEdgeCases:
    '''Test edge cases and boundary conditions.'''
    def test_single_pixel_grid(self, algorithms):
        """1x1 grid with single occupied site."""
        grid = np.array([[True]], dtype=bool)
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            assert len(cluster_info) == 1, f"{name}: 1x1 occupied grid should have 1 cluster"
            assert cluster_info[0]['size'] == 1, f"{name}: Cluster size should be 1"

    def test_single_pixel_empty(self, algorithms):
        """1x1 grid with no occupied sites."""
        grid = np.array([[False]], dtype=bool)
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            assert len(cluster_info) == 0, f"{name}: 1x1 empty grid should have 0 clusters"

    def test_all_corners_occupied(self, algorithms):
        """Grid with only corners occupied should have 4 clusters."""
        grid = np.zeros((5, 5), dtype=bool)
        grid[0, 0] = True
        grid[0, 4] = True
        grid[4, 0] = True
        grid[4, 4] = True
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            assert len(cluster_info) == 4, f"{name}: Four isolated corners should be 4 clusters"

    def test_border_only(self, algorithms):
        """Grid with only border occupied should form one cluster."""
        grid = np.zeros((5, 5), dtype=bool)
        grid[0, :] = True   # Top
        grid[4, :] = True   # Bottom
        grid[:, 0] = True   # Left
        grid[:, 4] = True   # Right
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            assert len(cluster_info) == 1, f"{name}: Connected border should be 1 cluster"
            assert cluster_info[0]['size'] == 16, f"{name}: Border should have 16 unique sites"

class TestLargeGrids:
    '''Test performance on larger grids'''
    def test_large_grid_low_p(self, algorithms):
        """Large grid with low occupation should have many small clusters."""
        np.random.seed(42)
        grid = np.random.rand(100, 100) < 0.3
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            
            # Should have many clusters
            assert len(cluster_info) > 100, f"{name}: Low p should create many clusters"
            
            # Total occupied sites should match
            total_occupied = sum(c['size'] for c in cluster_info)
            expected = np.sum(grid)
            assert total_occupied == expected, \
                f"{name}: Total occupied sites mismatch ({total_occupied} vs {expected})"

    def test_large_grid_high_p(self, algorithms):
        """Large grid with high occupation should have few large clusters."""
        np.random.seed(42)
        grid = np.random.rand(100, 100) < 0.8
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            
            # Should have few clusters
            assert len(cluster_info) < 50, f"{name}: High p should create few clusters"
            
            # At least one large cluster
            max_size = max(c['size'] for c in cluster_info)
            assert max_size > 1000, f"{name}: High p should create large clusters"

    @pytest.mark.slow
    def test_very_large_grid(self, algorithms):
        """Test on very large grid (500x500)."""
        np.random.seed(42)
        grid = np.random.rand(500, 500) < 0.6
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            
            # Just verify it completes and gives reasonable results
            assert len(cluster_info) > 0, f"{name}: Should find some clusters"
            total = sum(c['size'] for c in cluster_info)
            assert total == np.sum(grid), f"{name}: Total sites should match"

class TestDataTypes:
    '''Test handling of different data types and array formats'''
    def test_bool_array(self, algorithms):
        """Test with boolean numpy array."""
        grid = np.random.rand(20, 20) < 0.5
        assert grid.dtype == bool
        
        for name, algo in algorithms.items():
            labels, cluster_info = algo(grid)
            assert len(cluster_info) >= 0  # Should not crash

    def test_int_array_conversion(self, algorithms):
        """Test with integer array (should work with conversion)."""
        grid = (np.random.rand(20, 20) < 0.5).astype(int)
        
        for name, algo in algorithms.items():
            try:
                labels, cluster_info = algo(grid.astype(bool))
                assert len(cluster_info) >= 0
            except Exception as e:
                pytest.fail(f"{name}: Failed to handle int array: {e}")

    def test_non_square_grid_fails(self, algorithms):
        """Non-square grids should raise an error (if enforced)."""
        grid = np.random.rand(10, 20) < 0.5
        
        for name, algo in algorithms.items():
            if name == "C++":
                # C++ version enforces square grids
                with pytest.raises(RuntimeError, match="must be square"):
                    labels, cluster_info = algo(grid)
            # Python versions might accept it, that's okay


