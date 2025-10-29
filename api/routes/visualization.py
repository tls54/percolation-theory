"""Visualization endpoints."""

from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
import json

from api.models import VisualizationRequest
from visualization.renderers.matplotlib import render_cluster_grid
from Search import get_algorithm
import numpy as np

router = APIRouter(prefix="/visualize", tags=["visualization"])


@router.post("/grid", response_class=Response)
async def visualize_grid(request: VisualizationRequest):
    """
    Generate visualization of a single percolation grid.
    
    Returns PNG image with cluster visualization.
    Stats returned in X-Visualization-Stats header.
    """
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
        image_size=request.image_size,
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
            "Cache-Control": "no-cache"  # Don't cache (each generation unique)
        }
    )