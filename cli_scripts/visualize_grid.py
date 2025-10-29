#!/usr/bin/env python3
"""Generate cluster visualization from command line."""

import argparse
import numpy as np
from Search import find_clusters_cpp, find_clusters_union_find_numba_fast
from visualization.renderers.matplotlib import render_cluster_grid


def main():
    parser = argparse.ArgumentParser(description="Visualize percolation clusters")
    parser.add_argument("--p", type=float, required=True, help="Occupation probability")
    parser.add_argument("--N", type=int, default=50, help="Grid size")
    parser.add_argument("--algorithm", choices=["cpp", "numba"], default="cpp")
    parser.add_argument("--output", default="cluster_viz.png", help="Output filename")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--min-size", type=int, help="Min cluster size to color")
    
    args = parser.parse_args()
    
    # Generate grid
    if args.seed:
        np.random.seed(args.seed)
    grid = np.random.rand(args.N, args.N) < args.p
    
    # Find clusters
    algo = find_clusters_cpp if args.algorithm == "cpp" else find_clusters_union_find_numba_fast
    labels, cluster_info = algo(grid)
    
    # Render
    png_bytes, stats = render_cluster_grid(
        labels, cluster_info, args.p,
        min_cluster_size=args.min_size
    )
    
    # Save
    with open(args.output, 'wb') as f:
        f.write(png_bytes)
    
    print(f"Saved to {args.output}")
    print(f"Stats: {stats}")


if __name__ == "__main__":
    main()