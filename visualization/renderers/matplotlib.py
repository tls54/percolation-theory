"""Matplotlib-based renderer."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import io
from typing import Tuple, Optional
from ..core import ClusterColorAssigner


def render_cluster_grid(
    labels: np.ndarray,
    cluster_info: list,
    p: float,
    title: Optional[str] = None,
    colormap: str = 'tab20',
    min_cluster_size: Optional[int] = None,
    image_size: Tuple[int, int] = (800, 800),
    show_grid: bool = False,
    dpi: int = 100
) -> Tuple[bytes, dict]:
    """
    Render cluster grid as PNG bytes.
    
    Returns:
        (png_bytes, stats_dict)
    """
    N = labels.shape[0]
    
    # Assign colors
    assigner = ClusterColorAssigner(
        cluster_info=cluster_info,
        labels=labels,
        N=N,
        min_cluster_size=min_cluster_size
    )
    
    color_map = assigner.get_color_map(colormap)
    stats = assigner.get_stats()
    
    # Create color array (N×N RGB image)
    colored_grid = np.zeros((N, N, 3), dtype=np.uint8)
    
    for cluster_id, hex_color in color_map.items():
        # Convert hex to RGB
        rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        mask = (labels == cluster_id)
        colored_grid[mask] = rgb
    
    # Create figure
    fig_width = image_size[0] / dpi
    fig_height = image_size[1] / dpi
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)
    
    # Display image
    ax.imshow(colored_grid, interpolation='nearest')
    
    # Optional grid lines
    if show_grid and N <= 50:  # Only for small grids
        ax.set_xticks(np.arange(-0.5, N, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, N, 1), minor=True)
        ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    
    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])

    # Only show title if explicitly provided (default: no title - stats shown in UI)
    if title:
        ax.set_title(title, fontsize=12, pad=10)

    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=dpi)
    plt.close(fig)
    
    buf.seek(0)

    stats = assigner.get_stats()
    return buf.read(), stats