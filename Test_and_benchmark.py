import numpy as np
import time
from Search import (
    find_clusters_bfs,
    find_clusters_bfs_fast,
    find_clusters_union_find,
    find_clusters_union_find_numba,
    find_clusters_union_find_numba_fast,
    find_clusters_cpp
)


def test_search_algorithms():
    """
    Test that all search algorithms produce identical results.
    """
    print("\n" + "="*60)
    print("VALIDATING SEARCH ALGORITHMS")
    print("="*60 + "\n")
    
    # Test on multiple grids with different characteristics
    test_cases = [
        ("Empty grid", np.zeros((10, 10), dtype=bool)),
        ("Full grid", np.ones((10, 10), dtype=bool)),
        ("Single site", np.array([[False, False], [False, True]], dtype=bool)),
        ("Two clusters", np.array([
            [True, True, False, False],
            [False, True, False, False],
            [False, False, True, True],
            [False, False, True, False]
        ], dtype=bool)),
        ("Random small (p=0.3)", np.random.rand(20, 20) < 0.3),
        ("Random small (p=0.6)", np.random.rand(20, 20) < 0.6),
        ("Random medium (p=0.5)", np.random.rand(50, 50) < 0.5),
    ]
    
    # All algorithms to test
    algorithms = [
        ("BFS", find_clusters_bfs),
        ("BFS (fast)", find_clusters_bfs_fast),
        ("Union-Find (Python)", find_clusters_union_find),
        ("Union-Find (Numba)", find_clusters_union_find_numba),
        ("Union-Find (Numba fast)", find_clusters_union_find_numba_fast),
        ("Union-Find (cpp)", find_clusters_cpp)
    ]
    
    all_passed = True
    
    for test_name, grid in test_cases:
        print(f"\nTest: {test_name} ({grid.shape[0]}×{grid.shape[1]})")
        print(f"  Occupancy: {grid.sum()}/{grid.size} ({grid.sum()/grid.size:.2%})")
        
        # Run all algorithms
        results = {}
        for algo_name, algo_func in algorithms:
            try:
                labels, cluster_info = algo_func(grid)
                results[algo_name] = {
                    'labels': labels,
                    'num_clusters': len(cluster_info),
                    'cluster_sizes': sorted([c['size'] for c in cluster_info]),
                    'total_sites': sum(c['size'] for c in cluster_info)
                }
            except Exception as e:
                print(f"  ❌ {algo_name} FAILED: {e}")
                all_passed = False
                continue
        
        # Compare all results against BFS (reference)
        if "BFS" not in results:
            print("  ❌ Reference BFS failed, skipping comparison")
            all_passed = False
            continue
        
        reference = results["BFS"]
        
        for algo_name in results:
            if algo_name == "BFS":
                continue
            
            result = results[algo_name]
            
            # Check number of clusters
            if result['num_clusters'] != reference['num_clusters']:
                print(f"  ❌ {algo_name}: Wrong cluster count "
                      f"(got {result['num_clusters']}, expected {reference['num_clusters']})")
                all_passed = False
                continue
            
            # Check cluster sizes match
            if result['cluster_sizes'] != reference['cluster_sizes']:
                print(f"  ❌ {algo_name}: Cluster sizes don't match")
                print(f"     Expected: {reference['cluster_sizes']}")
                print(f"     Got:      {result['cluster_sizes']}")
                all_passed = False
                continue
            
            # Check total occupied sites
            if result['total_sites'] != reference['total_sites']:
                print(f"  ❌ {algo_name}: Wrong total sites "
                      f"(got {result['total_sites']}, expected {reference['total_sites']})")
                all_passed = False
                continue
            
            # Check label structure (same occupied/empty pattern)
            labels_match = np.array_equal(
                result['labels'] > 0,
                reference['labels'] > 0
            )
            if not labels_match:
                print(f"  ❌ {algo_name}: Label structure doesn't match")
                all_passed = False
                continue
            
            print(f"  ✓ {algo_name}: PASS ({result['num_clusters']} clusters, sizes: {result['cluster_sizes']})")
        
        print()
    
    print("="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("="*60 + "\n")
    
    return all_passed

def benchmark_search_algorithms():
    """
    Benchmark all search algorithms on the same grids.
    """
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60 + "\n")
    
    N = 50
    num_trials = 200
    p = 0.6
    
    print(f"Configuration: {N}×{N} grid, p={p}, {num_trials} trials\n")
    
    # Generate test grids once
    print("Generating test grids...")
    test_grids = [np.random.rand(N, N) < p for _ in range(num_trials)]
    print("Done!\n")
    
    # Warmup Numba
    print("Warming up Numba...")
    dummy = np.random.rand(10, 10) < 0.5
    _ = find_clusters_union_find_numba(dummy)
    _ = find_clusters_union_find_numba_fast(dummy)
    print("Done!\n")
    
    algorithms = [
        ("BFS", find_clusters_bfs),
        ("BFS (fast)", find_clusters_bfs_fast),
        ("Union-Find (Python)", find_clusters_union_find),
        ("Union-Find (Numba)", find_clusters_union_find_numba),
        ("Union-Find (Numba fast)", find_clusters_union_find_numba_fast),
        ("Union-Find (cpp)", find_clusters_cpp)
    ]
    
    results = []
    
    for algo_name, algo_func in algorithms:
        print(f"Testing {algo_name}...")
        
        start = time.perf_counter()
        for grid in test_grids:
            labels, info = algo_func(grid)
        elapsed = time.perf_counter() - start
        
        per_grid_ms = elapsed / num_trials * 1000
        
        results.append({
            'name': algo_name,
            'total': elapsed,
            'per_grid': per_grid_ms
        })
        
        print(f"  {elapsed:.3f}s total ({per_grid_ms:.2f} ms/grid)\n")
    
    # Summary
    print("="*60)
    print("SUMMARY (sorted by speed)")
    print("="*60 + "\n")
    
    results.sort(key=lambda x: x['total'])
    baseline = results[0]['total']
    
    for i, r in enumerate(results):
        speedup = baseline / r['total']
        print(f"{i+1}. {r['name']:30s} {r['total']:6.3f}s  "
              f"({r['per_grid']:6.2f} ms/grid)  {1/speedup:.1f}x slower than fastest")
    
    print()


if __name__ == '__main__':
    # First validate correctness
    test_passed = test_search_algorithms()
    
    if test_passed:
        # Then benchmark performance
        benchmark_search_algorithms()
    else:
        print("Fix validation errors before benchmarking!")