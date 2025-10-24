# Percolation theory

Modelling the permeability of membranes. Membranes are made up of pores that are either open or closed.  
The **question**: What fraction of open pores is required for the membrane to transition from impermeable to permeable?  

## The model

- Start with an ($N \times N$) square lattice.
- Each site is "occupied" (open/passable) with probability $p$ (independent).
- Sites are connected if they are directly adjascent (up, down, left or right, not diagonal for square lattices).
- A cluster is a maxial set of connected occupied sites.

**Key Question:** Does a cluster span from top to bottom (or left to right)?  

## The Phase Transition

- $p < p_c$ : Only small isolated clusters, no spanning cluster, the membrane is not permeable and the water does not percolate.
- $p = p_c$ : Critical point, fractal clusters at all scales, system is at the "edge".
- $p > p_c$ : A large cluster emerges that spans the lattice, The water can flow through the membrane.

For a 2-d square lattice, $p_c \approx 0.5927$.

## Quantities to Measure

- Percolation probability $P(p)$: fraction of configurations that have a spanning cluster.
- Cluster size distribution $n_s(p)$: number of clusters of size s.
- Mean cluster size $S(p)$: Average size of the cluster containing a randomly chosen occupied site.
- Correlation length $\xi (p)$: Typical cluster size.


# Key Changes

1. **New function `run_percolation_trials()`**: This runs multiple trials at a **single p value** and aggregates statistics

2. **Statistics collected across trials**:
   - Percolation probability P(p) - the key metric!
   - Mean number of clusters
   - Mean cluster size
   - Mean spanning cluster size

3. **Outer loop over p values**: Now you test different p values and compare their percolation probabilities

## Output You'll See
```
Running p = 0.40...
  Percolation probability: 0.000
  (0/100 trials percolated)
  
Running p = 0.59...
  Percolation probability: 0.450
  (45/100 trials percolated)
  
Running p = 0.70...
  Percolation probability: 1.000
  (100/100 trials percolated)