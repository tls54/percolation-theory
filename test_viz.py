import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from Search import find_clusters_bfs

# Parameters
#p = np.linspace(0.1, 0.9, 9)
p = [0.6 for i in range(3)]
N = 250
n = len(p)

# Generate random boolean grids
grids = [np.random.rand(N, N) < p[i] for i in range(n)]
grid_ints = [grid.astype(int) for grid in grids]

# Cluster labeling
clustered_grids = [find_clusters_bfs(grid)[0] for grid in grids]

def find_spanning_clusters(cluster_grid):
    """Return IDs of clusters that span top to bottom."""
    top = set(cluster_grid[0, :])
    bottom = set(cluster_grid[-1, :])
    vertical_spans = top.intersection(bottom) - {0}
    return vertical_spans

# Colormaps
base_cmap = mpl.colormaps['tab20']
n_clusters = np.max([cg.max() for cg in clustered_grids]) + 1
cluster_cmap = base_cmap.resampled(n_clusters)

# Color scheme
background_color = np.array([0.1, 0.1, 0.1, 1])  # dark grey background
highlight_palette = [
    np.array([1, 1, 0, 1]),   # yellow
    np.array([0, 1, 1, 1]),   # cyan
    np.array([1, 0, 1, 1]),   # magenta
    np.array([1, 0.5, 0, 1]), # orange
    np.array([0, 1, 0, 1]),   # bright green
    np.array([1, 0, 0, 1]),   # red
]

cols = 3
rows = int(np.ceil(n / cols))
fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows), constrained_layout=True)
axes = np.array(axes).reshape(-1)

for i, ax in enumerate(axes):
    if i >= n:
        ax.axis('off')
        continue

    clusters = clustered_grids[i]
    spanning = list(find_spanning_clusters(clusters))
    colors = cluster_cmap(clusters / n_clusters)

    # Set background color
    colors[clusters == 0] = background_color

    # Highlight spanning clusters with distinct or repeated colors
    for j, cid in enumerate(spanning):
        color = highlight_palette[j % len(highlight_palette)]
        colors[clusters == cid] = color

    # Display
    ax.imshow(colors, interpolation='none')
    ax.set_title(f"p={p[i]:.2f} | spans={len(spanning)}")
    ax.axis('off')

plt.show()