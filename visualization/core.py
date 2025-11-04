"""Core visualization logic - renderer-agnostic."""

import numpy as np
from typing import Tuple, List, Dict, Optional
from .config import COLORS, get_adaptive_config


class ClusterColorAssigner:
    """Assigns colors to clusters based on properties."""
    
    def __init__(self, 
                 cluster_info: List[Dict],
                 labels: np.ndarray,
                 N: int,
                 min_cluster_size: Optional[int] = None,
                 max_distinct_colors: int = 17):
        
        self.cluster_info = cluster_info
        self.labels = labels
        self.N = N
        self.num_clusters = len(cluster_info)
        
        # Auto-configure if not specified
        if min_cluster_size is None:
            config = get_adaptive_config(N, self.num_clusters)
            min_cluster_size = config['min_cluster_size']
        
        self.min_cluster_size = min_cluster_size
        self.max_distinct_colors = max_distinct_colors
        
        # Classify clusters
        self._classify_clusters()
    
    def _classify_clusters(self):
        """Categorize clusters into spanning/large/small."""
        self.spanning = []
        self.large = []
        self.small = []
        
        for cluster in self.cluster_info:
            # Check if spanning (touches top and bottom)
            if self._is_spanning(cluster['id']):
                self.spanning.append(cluster)
            elif cluster['size'] >= self.min_cluster_size:
                self.large.append(cluster)
            else:
                self.small.append(cluster)
        
        # Sort large clusters by size (descending)
        self.large.sort(key=lambda c: c['size'], reverse=True)
    
    def _is_spanning(self, cluster_id: int) -> bool:
        """Check if cluster spans top-to-bottom."""
        mask = (self.labels == cluster_id)

        # Vertical spanning (top to bottom)
        if mask[0, :].any() and mask[-1, :].any():
            return True

        return False
    
    def get_color_map(self, colormap_name: str = 'tab20') -> Dict[int, str]:
        """
        Generate mapping: cluster_id → hex color.
        
        Returns dict like: {0: '#000000', 1: '#FF0000', 2: '#1f77b4', ...}
        """
        import matplotlib.pyplot as plt
        
        color_map = {0: COLORS['empty']}  # Label 0 = empty
        
        # Assign spanning clusters
        spanning_colors = [
            COLORS['spanning_1'],
            COLORS['spanning_2'],
            COLORS['spanning_3']
        ]
        for i, cluster in enumerate(self.spanning[:3]):  # Max 3 spanning
            color = spanning_colors[i] if i < 3 else spanning_colors[2]
            color_map[cluster['id']] = color
        
        # Assign large clusters
        if self.large:
            cmap = plt.get_cmap(colormap_name)
            num_colors = min(len(self.large), self.max_distinct_colors)
            
            for i, cluster in enumerate(self.large[:num_colors]):
                # Convert matplotlib color to hex
                rgba = cmap(i / max(num_colors - 1, 1))
                hex_color = '#{:02x}{:02x}{:02x}'.format(
                    int(rgba[0] * 255),
                    int(rgba[1] * 255),
                    int(rgba[2] * 255)
                )
                color_map[cluster['id']] = hex_color
            
            # Remaining large clusters get gray (too many to distinguish)
            for cluster in self.large[num_colors:]:
                color_map[cluster['id']] = COLORS['small_cluster']
        
        # Assign small clusters
        for cluster in self.small:
            color_map[cluster['id']] = COLORS['small_cluster']
        
        return color_map
    
    def get_stats(self) -> Dict:
        """Get visualization statistics."""
        return {
            'total_clusters': self.num_clusters,
            'spanning_clusters': len(self.spanning),
            'large_clusters': len(self.large),
            'small_clusters': len(self.small),
            'min_size_threshold': self.min_cluster_size,
            'colored_clusters': len(self.spanning) + min(len(self.large), self.max_distinct_colors)
        }