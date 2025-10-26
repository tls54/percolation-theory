import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter

from Search import find_clusters_union_find_numba_fast, find_clusters_bfs, find_clusters_cpp
from Estimation import analyze_simulation_results
from profiling import ProfilerConfig, profile_context




def check_percolation(labels, cluster_info, N):
    """Check if any cluster spans from top row to bottom row."""
    if len(cluster_info) == 0:
        return False, None
    
    top_row_clusters = set(labels[0, :])
    top_row_clusters.discard(0)
    
    bottom_row_clusters = set(labels[N-1, :])
    bottom_row_clusters.discard(0)
    
    spanning_clusters = top_row_clusters & bottom_row_clusters
    
    if spanning_clusters:
        return True, spanning_clusters.pop()
    else:
        return False, None


def run_percolation_trials(p, N, num_trials, search_algo, verbose=False):
    """
    Run multiple percolation trials at a given p and collect statistics.
    
    Returns:
        results: dict with aggregated statistics
    """
    percolation_count = 0
    all_cluster_sizes = []
    num_clusters_list = []
    spanning_cluster_sizes = []
    
    for _ in range(num_trials):
        # Generate single grid
        grid = np.random.rand(N, N) < p
        
        # Find clusters
        labels, cluster_info = search_algo(grid)
        
        # Collect statistics
        num_clusters_list.append(len(cluster_info))
        cluster_sizes = [c['size'] for c in cluster_info]
        all_cluster_sizes.extend(cluster_sizes)
        
        # Check percolation
        percolates, spanning_id = check_percolation(labels, cluster_info, N)
        
        if percolates:
            percolation_count += 1
            # Find spanning cluster size
            for cluster in cluster_info:
                if cluster['id'] == spanning_id:
                    spanning_cluster_sizes.append(cluster['size'])
                    break
    
    # Aggregate results
    results = {
        'p': p,
        'N': N,
        'num_trials': num_trials,
        'percolation_probability': percolation_count / num_trials,
        'num_percolating': percolation_count,
        'mean_num_clusters': np.mean(num_clusters_list),
        'mean_cluster_size': np.mean(all_cluster_sizes) if all_cluster_sizes else 0,
        'mean_spanning_size': np.mean(spanning_cluster_sizes) if spanning_cluster_sizes else 0,
    }
    
    if verbose:
        print(f"  Percolation probability: {results['percolation_probability']:.3f}")
        print(f"  ({results['num_percolating']}/{num_trials} trials percolated)")
        print(f"  Mean # clusters: {results['mean_num_clusters']:.1f}")
        print(f"  Mean cluster size: {results['mean_cluster_size']:.1f}")
        if results['mean_spanning_size'] > 0:
            print(f"  Mean spanning cluster size: {results['mean_spanning_size']:.1f}")
    
    return results



if __name__ == '__main__':
    # ============= CONFIGURATION =============
    N = 250  # Grid size
    num_trials = 200  # Number of realizations per p value
    p_values = np.linspace(0.4, 0.8, 101)  # Fine-grained p values
    verbose = False 
    updates = 10 
    search_algo = find_clusters_cpp

    # Profiling configuration (ONLY CHANGE THIS)
    profiler_config = ProfilerConfig(
        enabled=False)
    # =========================================

    # Plotting storage
    prob_p = []
    num_clusters = []
    mean_sizes = []

    print('\nStarting Percolation Simulation...\n')
    print(f"Grid size: {N}x{N}")
    print(f"Trials per p: {num_trials}")
    print(f"Number of p values: {len(p_values)}")
    print(f"p range: [{p_values[0]:.3f}, {p_values[-1]:.3f}]")
    print("="*60)

    if 'numba' in str(search_algo):  
        print("Warming up Numba (compiling)...")
        dummy_grid = np.random.rand(10, 10) < 0.5
        _ = find_clusters_union_find_numba_fast(dummy_grid)
        print("Numba compiled and ready!")
    
    # ============= MAIN LOOP WITH PROFILING =============
    with profile_context(profiler_config, run_name="UnionFind_numba"):
        start = perf_counter()
        for i, p in enumerate(p_values):
            if verbose:
                print(f"\nRunning p = {p:.3f}...")
            else:
                if (i + 1) % updates == 0 or i == 0 or i == len(p_values) - 1:
                    print(f"Progress: {i+1}/{len(p_values)} (p = {p:.3f})")

            
            results = run_percolation_trials(p, N, num_trials, search_algo=search_algo, verbose=verbose)
            

            prob_p.append(results['percolation_probability'])
            num_clusters.append(results['mean_num_clusters'])
            mean_sizes.append(results['mean_cluster_size'])
    # ===================================================
    
    end = perf_counter()
    print("\n" + "="*60)
    print('Simulation complete!')
    print(f'Total Run Time: {end - start:.3f}')

    # ============= P_C ESTIMATION =============
    pc_results = analyze_simulation_results(
        p_values=np.array(p_values),
        percolation_probs=np.array(prob_p),
        N=N,
        num_trials=num_trials,
        verbose=True
    )
    # ==============================================

    # Create plots (your existing plotting code)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Plot 1: Percolation Probability P(p)
    axes[0].plot(p_values, prob_p, 'o-', linewidth=2, markersize=3, color='steelblue', label='Simulation')

    # Add fitted curve if available
    if pc_results['fit_info'] is not None:
        axes[0].plot(p_values, pc_results['fit_info']['fitted_curve'], '--', 
                    linewidth=2, color='orange', alpha=0.7, label='Sigmoid fit')
        # Mark estimated p_c
        axes[0].axvline(x=pc_results['pc_estimate'], color='orange', linestyle='--', 
                    alpha=0.7, label=f'Fitted p_c = {pc_results["pc_estimate"]:.4f}')

    axes[0].axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='P(p) = 0.5')
    axes[0].axvline(x=0.5927, color='green', linestyle='--', alpha=0.5, label='Theoretical p_c')
    axes[0].set_xlabel('Occupation Probability (p)', fontsize=12)
    axes[0].set_ylabel('Percolation Probability P(p)', fontsize=12)
    axes[0].set_title('Percolation Transition', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=8)
    axes[0].set_ylim(-0.05, 1.05)
    
    # Plot 2: Mean Number of Clusters
    axes[1].plot(p_values, num_clusters, 'o-', linewidth=2, markersize=3, color='coral')
    axes[1].axvline(x=0.5927, color='green', linestyle='--', alpha=0.5, label='p_c ≈ 0.593')
    axes[1].set_xlabel('Occupation Probability (p)', fontsize=12)
    axes[1].set_ylabel('Mean Number of Clusters', fontsize=12)
    axes[1].set_title('Cluster Count vs p', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    
    # Plot 3: Mean Cluster Size
    axes[2].plot(p_values, mean_sizes, 'o-', linewidth=2, markersize=3, color='mediumseagreen')
    axes[2].axvline(x=0.5927, color='green', linestyle='--', alpha=0.5, label='p_c ≈ 0.593')
    axes[2].set_xlabel('Occupation Probability (p)', fontsize=12)
    axes[2].set_ylabel('Mean Cluster Size', fontsize=12)
    axes[2].set_title('Cluster Size vs p', fontsize=14, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()
    
    plt.tight_layout()
    plt.savefig('percolation_analysis.png', dpi=300, bbox_inches='tight')
    print("\nPlot saved as 'percolation_analysis.png'")
    plt.show()
