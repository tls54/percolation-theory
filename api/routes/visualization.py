"""Visualization endpoints."""

from fastapi import APIRouter, Response
import json
import numpy as np

from api.models import VisualizationRequest
from visualization.renderers.matplotlib import render_cluster_grid
from Search import find_clusters_bfs, find_clusters_union_find_numba_fast, find_clusters_cpp, HAS_CPP

router = APIRouter(prefix="/visualize", tags=["visualization"])


def get_algorithm(name: str):
    """Get the requested algorithm function."""
    if name == "cpp":
        if not HAS_CPP:
            raise ValueError("C++ algorithm not available, use 'numba' or 'bfs'")
        return find_clusters_cpp
    elif name == "numba":
        return find_clusters_union_find_numba_fast
    elif name == "bfs":
        return find_clusters_bfs
    else:
        raise ValueError(f"Unknown algorithm: {name}")


@router.post("/grid")
async def visualize_grid(request: VisualizationRequest):
    """
    Generate visualization of a single percolation grid.

    Returns PNG image with cluster visualization.
    Visualization statistics returned in X-Visualization-Stats header.

    Example:
```
        curl -X POST http://localhost:8000/api/visualize/grid \\
          -H "Content-Type: application/json" \\
          -d '{"p": 0.6, "N": 100, "algorithm": "cpp", "seed": 42}' \\
          --output cluster.png
```
    """
    try:
        # Get algorithm
        algo = get_algorithm(request.algorithm)
        
        # Generate grid
        if request.seed is not None:
            np.random.seed(request.seed)
        grid = np.random.rand(request.N, request.N) < request.p
        
        # Find clusters
        labels, cluster_info = algo(grid)
        
        # Render visualization
        png_bytes, stats = render_cluster_grid(
            labels=labels,
            cluster_info=cluster_info,
            p=request.p,
            colormap=request.colormap,
            min_cluster_size=request.min_cluster_size,
            image_size=tuple(request.image_size),
            show_grid=request.show_grid
        )
        
        # Return image with stats in headers
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={
                "X-Visualization-Stats": json.dumps(stats),
                "X-Grid-Size": str(request.N),
                "X-Occupation-Probability": str(request.p),
                "X-Algorithm": request.algorithm,
                "Cache-Control": "no-cache"  # Don't cache (each generation unique)
            }
        )
    
    except ValueError as e:
        return Response(
            content=str(e),
            status_code=400,
            media_type="text/plain"
        )
    except Exception as e:
        return Response(
            content=f"Visualization error: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )