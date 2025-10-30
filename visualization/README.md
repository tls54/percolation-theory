# Visualization

Publication-quality PNG rendering of percolation grids with intelligent cluster coloring.

## Features

- **Spanning cluster highlighting**: Automatically identifies clusters that span the grid
- **Smart color assignment**: Large clusters get distinct colors, small clusters are gray
- **Adaptive sizing**: Auto-adjusts parameters based on grid size
- **Customizable colormaps**: Support for all matplotlib colormaps
- **Reproducible**: Use seed parameter for consistent results
- **Fast rendering**: Leverages high-performance cluster algorithms

## Quick Start

### Via API (Recommended)

```bash
# Basic visualization
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{"p": 0.6, "N": 100, "algorithm": "cpp"}' \
  --output cluster.png

# With custom options
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{
    "p": 0.6,
    "N": 200,
    "algorithm": "cpp",
    "seed": 42,
    "colormap": "viridis",
    "min_cluster_size": 20
  }' \
  --output visualization.png
```

### Python Script

```python
from visualization.renderers.matplotlib import render_grid_to_png
from Search import find_clusters_cpp
import numpy as np

# Generate grid
np.random.seed(42)
grid = np.random.rand(100, 100) < 0.6

# Find clusters
clusters, num_clusters = find_clusters_cpp(grid)

# Render
png_bytes = render_grid_to_png(
    grid=grid,
    clusters=clusters,
    p=0.6,
    colormap="viridis",
    image_size=(1200, 1200)
)

# Save to file
with open("cluster.png", "wb") as f:
    f.write(png_bytes)
```

## Color Scheme

The visualization uses intelligent color assignment:

1. **Spanning clusters** (cross entire grid):
   - Red: Largest spanning cluster
   - Blue: Second largest spanning cluster
   - Green: Third largest spanning cluster

2. **Large non-spanning clusters**:
   - Distinct colors from chosen colormap
   - Based on cluster size rank

3. **Small clusters**:
   - Gray (#808080)
   - Prevents visual clutter

4. **Empty sites**:
   - Black background

## Parameters

### Required

- `grid`: NumPy boolean array (N×N)
- `clusters`: Cluster labels from search algorithm
- `p`: Occupation probability used

### Optional

- `colormap` (str): Matplotlib colormap name (default: "tab20")
  - Good options: "tab20", "viridis", "plasma", "Set3"
  - See [matplotlib colormaps](https://matplotlib.org/stable/tutorials/colors/colormaps.html)

- `min_cluster_size` (int): Minimum size to color (default: auto-calculated)
  - Auto uses: `max(5, N²/1000)`
  - Smaller values show more detail but can be cluttered

- `image_size` (tuple): Output dimensions in pixels (default: (800, 800))
  - Larger sizes: better quality, larger files
  - Recommended: (800, 800) for N≤100, (1200, 1200) for N>100

- `show_grid` (bool): Show grid lines (default: false)
  - Only useful for small grids (N≤50)

- `dpi` (int): Dots per inch (default: auto-calculated)
  - Higher DPI: sharper images, larger files

## Examples

### Near Critical Probability

```bash
# p ≈ p_c shows the phase transition
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{"p": 0.59, "N": 200, "algorithm": "cpp"}' \
  --output near_critical.png
```

At p ≈ 0.59, you'll see:
- Mix of small and medium clusters
- Possibly one large spanning cluster
- Characteristic fractal structure

### Below Critical Probability

```bash
# p < p_c: many small disconnected clusters
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{"p": 0.4, "N": 200, "algorithm": "cpp"}' \
  --output below_critical.png
```

Below p_c (≈0.59):
- Many small isolated clusters
- Mostly gray and black
- No spanning clusters

### Above Critical Probability

```bash
# p > p_c: dominant spanning cluster
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{"p": 0.7, "N": 200, "algorithm": "cpp"}' \
  --output above_critical.png
```

Above p_c:
- Large spanning cluster dominates (red)
- Few medium clusters
- Very few small clusters

### Custom Colormaps

```bash
# Viridis colormap
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{"p": 0.6, "N": 100, "colormap": "viridis"}' \
  --output viridis.png

# Plasma colormap
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{"p": 0.6, "N": 100, "colormap": "plasma"}' \
  --output plasma.png

# Set3 colormap (pastel colors)
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{"p": 0.6, "N": 100, "colormap": "Set3"}' \
  --output set3.png
```

### High Resolution

```bash
# High-res for publication
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{
    "p": 0.6,
    "N": 200,
    "algorithm": "cpp",
    "image_size": [2400, 2400]
  }' \
  --output high_res.png
```

## Reproducibility

Use the `seed` parameter for consistent results:

```python
import requests

# Same seed produces identical visualization
for i in range(3):
    response = requests.post(
        "http://localhost:8000/api/visualize/grid",
        json={"p": 0.6, "N": 100, "algorithm": "cpp", "seed": 42}
    )
    with open(f"cluster_{i}.png", "wb") as f:
        f.write(response.content)
    # All three images will be identical
```

## Statistics

The API returns cluster statistics in response headers:

```python
import requests
import json

response = requests.post(
    "http://localhost:8000/api/visualize/grid",
    json={"p": 0.6, "N": 100, "algorithm": "cpp"}
)

# Get statistics from header
stats = json.loads(response.headers.get('X-Visualization-Stats', '{}'))
print(f"Total clusters: {stats.get('num_clusters')}")
print(f"Largest cluster: {stats.get('largest_cluster_size')}")
print(f"Spanning clusters: {stats.get('num_spanning_clusters')}")
```

## Performance

Rendering time scales with grid size:

| Grid Size | Typical Render Time |
|-----------|---------------------|
| 50×50     | ~50 ms              |
| 100×100   | ~100 ms             |
| 200×200   | ~200 ms             |
| 500×500   | ~800 ms             |

The cluster-finding algorithm is the bottleneck, not the rendering itself. Use C++ algorithm for best performance.

## Troubleshooting

### Matplotlib Not Found

```bash
pip install matplotlib
```

### Memory Issues with Large Grids

For N > 500:
- Use smaller image_size: `[1000, 1000]` instead of `[2400, 2400]`
- Close figures explicitly in scripts
- Consider splitting into multiple smaller visualizations

### Colors Look Wrong

- Check colormap name is valid: see [matplotlib docs](https://matplotlib.org/stable/tutorials/colors/colormaps.html)
- Try different colormaps: "tab20", "viridis", "Set3"
- Adjust min_cluster_size to show more/fewer clusters

### Grid Lines Not Showing

- Only visible for small grids (N≤50)
- Set `show_grid: true` in request
- Not recommended for large grids (causes visual clutter)

## See Also

- [API Reference](../api/README.md) - Full API documentation
- [Usage Guide](../docs/usage.md) - End-to-end examples
- [Algorithm Details](../docs/algorithms.md) - Cluster-finding algorithms
