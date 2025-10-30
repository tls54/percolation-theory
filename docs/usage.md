# Usage Guide

Complete walkthrough from setup to simulation to visualization.

## Table of Contents

1. [Installation](#installation)
2. [Basic Simulation](#basic-simulation)
3. [Parameter Sweeps](#parameter-sweeps)
4. [Critical Probability Estimation](#critical-probability-estimation)
5. [Visualization](#visualization)
6. [Using the REST API](#using-the-rest-api)
7. [Advanced Usage](#advanced-usage)

## Installation

### Option 1: Docker (Recommended)

Quickest way to get started with zero configuration:

```bash
git clone https://github.com/tls54/percolation-theory.git
cd percolation-theory
docker-compose up -d

# Verify
curl http://localhost:8000/api/health
```

### Option 2: Local Installation

For development or custom setups:

```bash
# Clone repository
git clone https://github.com/tls54/percolation-theory.git
cd percolation-theory

# Install dependencies
pip install -r requirements.txt

# (Optional) Build C++ extension
python setup.py build_ext --inplace

# Verify
pytest
```

## Basic Simulation

### Single Simulation

Run a percolation simulation with specific parameters:

```python
from Search import find_clusters_union_find_numba_fast
from Percolation import run_percolation_trials

# Run 100 trials on 50×50 grid with p=0.6
results = run_percolation_trials(
    p=0.6,
    N=50,
    num_trials=100,
    search_algo=find_clusters_union_find_numba_fast
)

print(f"Percolation probability: {results['percolation_probability']:.3f}")
print(f"Mean number of clusters: {results['mean_num_clusters']:.1f}")
print(f"Mean cluster size: {results['mean_cluster_size']:.1f}")
```

**Output:**
```
Percolation probability: 0.850
Mean number of clusters: 14.2
Mean cluster size: 11.8
```

### Using Different Algorithms

```python
from Search import find_clusters_bfs, find_clusters_union_find_numba_fast, find_clusters_cpp
from Percolation import run_percolation_trials

# Try each algorithm
for name, algo in [("BFS", find_clusters_bfs),
                   ("Numba", find_clusters_union_find_numba_fast),
                   ("C++", find_clusters_cpp)]:
    results = run_percolation_trials(p=0.6, N=50, num_trials=100, search_algo=algo)
    print(f"{name}: {results['computation_time_ms']:.1f} ms")
```

## Parameter Sweeps

Sweep across multiple p values to observe phase transition:

```python
import numpy as np
import matplotlib.pyplot as plt
from Search import find_clusters_union_find_numba_fast
from Percolation import run_percolation_trials

# Define p values
p_values = np.linspace(0.4, 0.8, 21)
percolation_probs = []

# Run simulations
for p in p_values:
    results = run_percolation_trials(
        p=p,
        N=100,
        num_trials=200,
        search_algo=find_clusters_union_find_numba_fast
    )
    percolation_probs.append(results['percolation_probability'])
    print(f"p={p:.2f}: P(p)={results['percolation_probability']:.3f}")

# Plot phase transition
plt.figure(figsize=(10, 6))
plt.plot(p_values, percolation_probs, 'o-')
plt.axvline(0.5927, color='r', linestyle='--', label='Theoretical p_c')
plt.xlabel('Occupation Probability (p)')
plt.ylabel('Percolation Probability P(p)')
plt.title('Phase Transition in 2D Percolation')
plt.grid(True)
plt.legend()
plt.show()
```

## Critical Probability Estimation

Estimate p_c with statistical analysis:

```python
import numpy as np
from Search import find_clusters_union_find_numba_fast
from Percolation import run_percolation_trials
from Estimation import analyze_simulation_results

# Parameter sweep near critical point
p_values = np.linspace(0.55, 0.65, 31)
percolation_probs = []

for p in p_values:
    results = run_percolation_trials(
        p=p,
        N=100,
        num_trials=500,
        search_algo=find_clusters_union_find_numba_fast
    )
    percolation_probs.append(results['percolation_probability'])

# Estimate critical point
pc_results = analyze_simulation_results(
    np.array(p_values),
    np.array(percolation_probs),
    N=100,
    num_trials=500
)

print(f"Estimated p_c: {pc_results['pc_estimate']:.4f}")
print(f"Standard error: {pc_results['pc_stderr']:.4f}")
print(f"Error from theoretical: {pc_results['pc_error_percent']:.2f}%")
print(f"Theoretical p_c: 0.5927")
```

**Output:**
```
Estimated p_c: 0.5925
Standard error: 0.0012
Error from theoretical: 0.03%
Theoretical p_c: 0.5927
```

## Visualization

### Generate Visualization via API

```bash
# Start API
docker-compose up -d

# Generate visualization
curl -X POST http://localhost:8000/api/visualize/grid \
  -H "Content-Type: application/json" \
  -d '{
    "p": 0.6,
    "N": 100,
    "algorithm": "cpp",
    "seed": 42,
    "colormap": "viridis"
  }' \
  --output cluster.png
```

### Python Visualization Script

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

# Save
with open("cluster.png", "wb") as f:
    f.write(png_bytes)

print(f"Visualization saved with {num_clusters} clusters")
```

### Visualizing Phase Transition

```python
import numpy as np
import requests

# Visualize at different p values
p_values = [0.4, 0.59, 0.7]  # Below, at, and above p_c

for p in p_values:
    response = requests.post(
        "http://localhost:8000/api/visualize/grid",
        json={"p": p, "N": 200, "algorithm": "cpp", "seed": 42}
    )

    with open(f"percolation_p{p:.2f}.png", "wb") as f:
        f.write(response.content)

    print(f"Saved visualization for p={p}")
```

## Using the REST API

### Start the Server

```bash
# With Docker
docker-compose up -d

# Or manually
uvicorn api.main:app --reload
```

### Single Simulation via API

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
print(f"Computation time: {result['computation_time_ms']:.1f} ms")
```

### Parameter Sweep via API

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

# Plot results
plt.plot(result['p_values'], result['percolation_probabilities'], 'o-')
plt.axvline(result['pc_estimate'], color='r', linestyle='--',
            label=f"p_c = {result['pc_estimate']:.4f}")
plt.xlabel('Occupation Probability (p)')
plt.ylabel('Percolation Probability')
plt.legend()
plt.show()

print(f"Estimated p_c: {result['pc_estimate']:.4f} ± {result['pc_stderr']:.4f}")
```

## Advanced Usage

### Custom Analysis

```python
import numpy as np
from Search import find_clusters_union_find_numba_fast

# Generate grid
grid = np.random.rand(100, 100) < 0.6

# Find clusters
clusters, num_clusters = find_clusters_union_find_numba_fast(grid)

# Analyze cluster sizes
unique, counts = np.unique(clusters[clusters > 0], return_counts=True)
cluster_sizes = dict(zip(unique, counts))

print(f"Total clusters: {num_clusters}")
print(f"Largest cluster: {max(counts)} sites")
print(f"Smallest cluster: {min(counts)} sites")
print(f"Mean cluster size: {np.mean(counts):.1f} sites")

# Check for spanning
def spans_vertically(clusters, label):
    return label in clusters[0, :] and label in clusters[-1, :]

def spans_horizontally(clusters, label):
    return label in clusters[:, 0] and label in clusters[:, -1]

spanning_clusters = []
for label in unique:
    if spans_vertically(clusters, label) or spans_horizontally(clusters, label):
        spanning_clusters.append(label)

print(f"Spanning clusters: {len(spanning_clusters)}")
```

### Batch Processing

```python
import numpy as np
from Search import find_clusters_cpp
from Percolation import run_percolation_trials
import json

# Batch parameters
batch_config = {
    "N_values": [50, 100, 200],
    "p_values": np.linspace(0.5, 0.7, 11),
    "num_trials": 200
}

results = []

for N in batch_config["N_values"]:
    for p in batch_config["p_values"]:
        result = run_percolation_trials(
            p=p,
            N=N,
            num_trials=batch_config["num_trials"],
            search_algo=find_clusters_cpp
        )

        results.append({
            "N": N,
            "p": float(p),
            "percolation_probability": result["percolation_probability"],
            "mean_num_clusters": result["mean_num_clusters"]
        })

        print(f"N={N}, p={p:.2f}: P(p)={result['percolation_probability']:.3f}")

# Save results
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

### Performance Comparison

```python
import time
from Search import find_clusters_bfs, find_clusters_union_find_numba_fast, find_clusters_cpp
import numpy as np

N = 100
p = 0.6
num_trials = 100

# Generate grids once
grids = [np.random.rand(N, N) < p for _ in range(num_trials)]

# Benchmark each algorithm
algorithms = [
    ("BFS", find_clusters_bfs),
    ("Numba", find_clusters_union_find_numba_fast),
    ("C++", find_clusters_cpp)
]

for name, algo in algorithms:
    start = time.time()
    for grid in grids:
        clusters, num_clusters = algo(grid)
    elapsed = time.time() - start

    ms_per_grid = elapsed * 1000 / num_trials
    speedup = (elapsed_bfs / elapsed) if name != "BFS" else 1.0

    if name == "BFS":
        elapsed_bfs = elapsed

    print(f"{name:8s}: {ms_per_grid:6.2f} ms/grid  ({speedup:.1f}x)")
```

## See Also

- [API Reference](../api/README.md) - REST API documentation
- [Development Guide](development.md) - Testing and profiling
- [Algorithm Details](algorithms.md) - Implementation deep dive
- [Theory Background](theory.md) - Percolation theory
- [Troubleshooting](troubleshooting.md) - Common issues
