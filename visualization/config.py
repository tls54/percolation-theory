"""Visualization configuration and color schemes."""

# Color definitions
COLORS = {
    'empty': '#000000',           # Black - unpopulated
    'small_cluster': '#808080',   # Gray - below threshold
    'spanning_1': '#FF0000',      # Red - primary spanning
    'spanning_2': '#FF6600',      # Orange - secondary spanning
    'spanning_3': '#FFCC00',      # Yellow - tertiary spanning
}

# Matplotlib colormaps for regular clusters
COLORMAPS = {
    'tab20': 'tab20',      # 20 distinct colors (default)
    'tab20b': 'tab20b',    # Alternative 20 colors
    'tab20c': 'tab20c',    # Another alternative
    'hsv': 'hsv',          # More colors but less distinct
}


def get_adaptive_config(N: int, num_clusters: int) -> dict:
    """
    Get smart defaults based on grid size and cluster count.
    
    Args:
        N: Grid size (N×N)
        num_clusters: Number of clusters found
    
    Returns:
        Configuration dict with adaptive settings
    """
    # Minimum cluster size to color (adaptive)
    if N <= 50:
        min_size = 2  # Show almost all clusters
    elif N <= 100:
        min_size = 3
    elif N <= 250:
        min_size = max(5, N // 50)  # Scale with grid
    else:
        min_size = max(10, N // 40)
    
    # Image size (larger grids need more pixels)
    if N <= 50:
        img_size = (600, 600)
    elif N <= 100:
        img_size = (800, 800)
    elif N <= 250:
        img_size = (1000, 1000)
    else:
        img_size = (1200, 1200)
    
    # Number of distinct colors available (tab20 = 20)
    # Reserve 3 for spanning clusters
    max_distinct_colors = 17
    
    return {
        'min_cluster_size': min_size,
        'image_size': img_size,
        'max_colors': max_distinct_colors
    }