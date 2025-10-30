# REST API Reference

FastAPI-based REST API for percolation simulations and visualizations.

## Quick Start

```bash
# Using Docker (recommended)
docker-compose up -d

# Or manually
uvicorn api.main:app --reload --port 8000

# Production mode with multiple workers
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Endpoints

### GET /health

Check API health and available optimizations.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "cpp_available": true,
  "numba_available": true
}
```

### POST /api/simulate

Run a single percolation simulation.

**Request:**
```bash
curl -X POST http://localhost:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "p": 0.6,
    "N": 50,
    "num_trials": 100,
    "algorithm": "numba"
  }'
```

**Parameters:**
- `p` (required): Occupation probability (0.0-1.0)
- `N` (required): Grid size (10-500)
- `num_trials` (required): Number of simulation trials (1-10000)
- `algorithm` (required): "bfs", "numba", or "cpp"

**Response:**
```json
{
  "p": 0.6,
  "percolation_probability": 0.743,
  "mean_num_clusters": 12.4,
  "mean_cluster_size": 8.2,
  "computation_time_ms": 45.2,
  "algorithm_used": "numba"
}
```

**Python Example:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/simulate",
    json={
        "p": 0.6,
        "N": 50,
        "num_trials": 100,
        "algorithm": "numba"
    }
)
result = response.json()
print(f"Percolation probability: {result['percolation_probability']:.3f}")
```

### POST /api/simulate/sweep

Run parameter sweep across multiple p values with optional p_c estimation.

**Request:**
```bash
curl -X POST http://localhost:8000/api/simulate/sweep \
  -H "Content-Type: application/json" \
  -d '{
    "p_min": 0.5,
    "p_max": 0.7,
    "p_steps": 21,
    "N": 100,
    "num_trials": 200,
    "algorithm": "cpp",
    "estimate_pc": true
  }'
```

**Parameters:**
- `p_min` (required): Minimum occupation probability
- `p_max` (required): Maximum occupation probability
- `p_steps` (required): Number of p values to test
- `N` (required): Grid size
- `num_trials` (required): Trials per p value
- `algorithm` (required): "bfs", "numba", or "cpp"
- `estimate_pc` (optional): Estimate critical probability (default: false)

**Response:**
```json
{
  "p_values": [0.5, 0.51, 0.52, ...],
  "percolation_probabilities": [0.12, 0.18, 0.24, ...],
  "pc_estimate": 0.5925,
  "pc_stderr": 0.0012,
  "pc_error_percent": 0.03,
  "total_computation_time_s": 2.34
}
```

**Python Example:**
```python
import requests
import matplotlib.pyplot as plt

response = requests.post(
    "http://localhost:8000/api/simulate/sweep",
    json={
        "p_min": 0.5,
        "p_max": 0.7,
        "p_steps": 21,
        "N": 100,
        "num_trials": 200,
        "algorithm": "cpp",
        "estimate_pc": True
    }
)
result = response.json()

# Plot phase transition
plt.plot(result['p_values'], result['percolation_probabilities'])
plt.axvline(result['pc_estimate'], color='r', linestyle='--',
            label=f"p_c = {result['pc_estimate']:.4f}")
plt.xlabel('Occupation Probability (p)')
plt.ylabel('Percolation Probability')
plt.legend()
plt.show()
```

### POST /api/visualize/grid

Generate a PNG visualization of a percolation grid with color-coded clusters.

**Request:**
```bash
# Basic visualization
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{"p": 0.6, "N": 100, "algorithm": "cpp", "seed": 42}' \
  --output cluster.png

# With custom options
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{
    "p": 0.6,
    "N": 100,
    "algorithm": "numba",
    "seed": 42,
    "colormap": "viridis",
    "min_cluster_size": 10,
    "image_size": [1200, 1200],
    "show_grid": false
  }' \
  --output visualization.png
```

**Parameters:**
- `p` (required): Occupation probability (0.0-1.0)
- `N` (required): Grid size (10-500)
- `algorithm` (required): "bfs", "numba", or "cpp"
- `seed` (optional): Random seed for reproducibility
- `colormap` (optional): Matplotlib colormap name (default: "tab20")
- `min_cluster_size` (optional): Minimum cluster size to color (default: auto)
- `image_size` (optional): [width, height] in pixels (default: [800, 800])
- `show_grid` (optional): Show grid lines for small N (default: false)

**Response:**
- Content-Type: `image/png`
- Headers:
  - `X-Visualization-Stats`: JSON with cluster statistics
  - `X-Grid-Size`: Grid dimension
  - `X-Occupation-Probability`: p value used
  - `X-Algorithm`: Algorithm used

**Python Example:**
```python
import requests
from PIL import Image
import io

response = requests.post(
    "http://localhost:8000/api/visualize/grid",
    json={
        "p": 0.6,
        "N": 100,
        "algorithm": "cpp",
        "seed": 42,
        "colormap": "viridis"
    }
)

# Save image
with open("cluster.png", "wb") as f:
    f.write(response.content)

# Get statistics from headers
stats = response.headers.get('X-Visualization-Stats')
print(f"Statistics: {stats}")

# Display in notebook
image = Image.open(io.BytesIO(response.content))
image.show()
```

## Configuration

Environment variables (set in `docker-compose.yml` or `.env`):

- `API_TITLE`: API service name (default: "Percolation Theory API")
- `API_VERSION`: Version string (default: "0.1.0")
- `DEFAULT_N`: Default grid size (default: 50)
- `DEFAULT_NUM_TRIALS`: Default trial count (default: 100)
- `MAX_N`: Maximum allowed grid size (default: 500)
- `MAX_TRIALS`: Maximum allowed trials (default: 10000)
- `USE_CPP`: Enable C++ optimization (default: true)

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid parameters
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

**Error Response:**
```json
{
  "detail": "Grid size N must be between 10 and 500"
}
```

## Rate Limiting and Performance

For production use:
- Use multiple workers: `uvicorn api.main:app --workers 4`
- Enable C++ algorithm for best performance
- Consider caching results for repeated parameter combinations
- Large grids (N > 200) may take several seconds

## Troubleshooting

**Port already in use:**
```bash
# Check what's using port 8000
lsof -i :8000

# Use different port
uvicorn api.main:app --port 8001
```

**C++ algorithm not available:**
```bash
# Check availability
curl http://localhost:8000/health

# Rebuild C++ extension
python setup.py build_ext --inplace

# Fallback to Numba
# Use "algorithm": "numba" in requests
```

**Import errors:**
```bash
# Ensure running from project root
cd /path/to/percolation-theory
uvicorn api.main:app --reload

# Check dependencies
pip install -r requirements.txt
```

## See Also

- [Usage Guide](../docs/usage.md) - Full API usage examples
- [Development Guide](../docs/development.md) - Testing and profiling
- [Troubleshooting](../docs/troubleshooting.md) - Common issues
