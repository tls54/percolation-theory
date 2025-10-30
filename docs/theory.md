# Percolation Theory

Background on percolation theory, phase transitions, and critical phenomena.

## Introduction

Percolation theory is a branch of statistical physics that studies the behavior of connected clusters in random systems. It has applications in:

- Material science (porous materials, conductivity)
- Network theory (network resilience, epidemic spreading)
- Forest fire modeling
- Oil reservoir engineering
- Social network analysis

## Basic Concepts

### The Percolation Model

Consider a 2D square lattice (grid) where each site is:
- **Occupied** with probability **p**
- **Empty** with probability **1-p**

Two occupied sites are **connected** if they are adjacent (horizontally or vertically, not diagonally).

A **cluster** is a maximal set of connected occupied sites.

### Example

For p = 0.4 on a 10×10 grid:
```
■ ■ □ □ □ ■ □ □ ■ □    ■ = occupied
■ □ □ ■ □ □ □ ■ ■ □    □ = empty
□ □ □ □ □ □ □ □ ■ □
□ ■ ■ □ □ ■ ■ □ □ □
■ ■ □ □ □ ■ □ □ ■ □
...
```

Occupied sites form multiple disconnected clusters of varying sizes.

## Phase Transition

### The Critical Probability

As p increases from 0 to 1, the system undergoes a dramatic **phase transition** at a critical value **p_c**.

**For 2D square lattice site percolation:**
```
p_c ≈ 0.59274621...
```

This is an exact theoretical result (proven by Kesten, 1980).

### Below Critical Probability (p < p_c)

For p < 0.59:
- Many small, isolated clusters
- No large connected structures
- Largest cluster size scales as log(N)
- System is "disconnected"

**Physical Interpretation:**
- Material is non-conductive
- Network is fragmented
- Forest fires don't spread far

### At Critical Probability (p ≈ p_c)

At p ≈ 0.59:
- Critical point of the phase transition
- Largest cluster size scales as N^(91/48) ≈ N^1.9
- Self-similar fractal structures emerge
- System exhibits scale invariance
- **Spanning cluster** begins to appear

**Physical Interpretation:**
- Material becomes conductive
- Network becomes connected
- Critical transition point

### Above Critical Probability (p > p_c)

For p > 0.59:
- One dominant **spanning cluster** that crosses the entire grid
- Spanning cluster size scales as N²
- System is "connected"
- Many small satellite clusters remain

**Physical Interpretation:**
- Material is highly conductive
- Network is robust
- Forest fires spread across entire region

## Mathematical Framework

### Percolation Probability

The **percolation probability** P(p) is the probability that a randomly chosen site belongs to a spanning cluster:

```
P(p) = Probability(site is in spanning cluster)
```

Behavior:
- P(p) = 0 for p < p_c (no spanning cluster exists)
- P(p) → 1 as p → 1 (entire grid is occupied)
- Steep transition near p = p_c

### Critical Exponents

Near the critical point, physical quantities follow power laws:

**Percolation probability:**
```
P(p) ∼ (p - p_c)^β    for p > p_c
```
where β ≈ 5/36 ≈ 0.139 for 2D.

**Correlation length:**
```
ξ(p) ∼ |p - p_c|^(-ν)
```
where ν = 4/3 for 2D.

**Mean cluster size:**
```
S(p) ∼ |p - p_c|^(-γ)
```
where γ = 43/18 ≈ 2.39 for 2D.

These exponents are **universal** - they don't depend on lattice details, only dimensionality.

## Cluster Statistics

### Cluster Size Distribution

The number of clusters of size s follows:

**Below p_c:**
```
n_s(p) ∼ s^(-τ) exp(-s/s_ξ)
```
where τ = 187/91 ≈ 2.05 for 2D.

**At p_c:**
```
n_s(p_c) ∼ s^(-τ)
```
Power-law distribution (scale-free).

### Mean Cluster Size

Average cluster size excluding the spanning cluster:

```
S(p) = Σ s² n_s(p) / Σ s n_s(p)
```

Diverges as p → p_c from either direction.

## Spanning Clusters

### Definition

A cluster **spans** if it connects opposite edges of the grid:
- **Vertically**: connects top to bottom
- **Horizontally**: connects left to right

In finite systems, we typically check both.

### Finite-Size Effects

Real simulations use finite grids (N×N), leading to:

**Rounding of transition:**
- Transition is smooth, not sharp
- Width scales as 1/N^(1/ν) ≈ 1/N^0.75

**Effective p_c:**
- Apparent critical point shifts slightly with N
- Converges to true p_c as N → ∞

**Probability of spanning:**
- Below p_c: P_spanning ≈ 0 but not exactly zero
- Above p_c: P_spanning ≈ 1 but not exactly one
- At p_c: P_spanning ≈ 0.5 (finite-size approximation)

## Estimating p_c from Simulations

### Method 1: Inflection Point

The steepest point of P(p) curve occurs near p_c:

```
p_c ≈ argmax(dP/dp)
```

Our implementation uses polynomial fitting to find this point.

### Method 2: Half-Crossing

At p_c, the percolation probability is approximately 0.5:

```
P(p_c) ≈ 0.5
```

Interpolate to find where P(p) = 0.5.

### Method 3: Scaling Analysis

Use finite-size scaling theory:

```
P(p, N) = f((p - p_c) N^(1/ν))
```

Fit data from multiple N values to extract p_c.

### Accuracy

Typical accuracy from our simulations:
- N=100, 200 trials: ±0.002 (±0.3%)
- N=200, 500 trials: ±0.001 (±0.17%)
- N=500, 1000 trials: ±0.0005 (±0.08%)

## Universality

### Universality Classes

Systems with different microscopic details but same:
- Dimensionality
- Symmetries
- Range of interactions

share the same critical exponents. This is **universality**.

**2D site percolation:**
- Square lattice: p_c ≈ 0.5927
- Triangular lattice: p_c = 0.5
- Honeycomb lattice: p_c ≈ 0.6962

Different p_c values, but **same critical exponents** (β, ν, γ).

### Connection to Other Systems

Percolation is related to:
- **Ising model**: Ferromagnetic phase transition
- **Random graphs**: Erdős-Rényi connectivity transition
- **Epidemic models**: SIR disease spreading threshold

All exhibit similar critical behavior.

## Applications

### Material Science

**Conductivity:**
- Composite materials become conductive at percolation threshold
- Model: sites are conductive particles in insulating matrix
- Application: design of conductive composites

**Porous Media:**
- Flow through porous rocks (oil extraction)
- Water absorption in soil
- Filtration systems

### Network Science

**Network Robustness:**
- How many nodes can fail before network disconnects?
- p = 1 - (failure rate)
- Critical threshold for network collapse

**Epidemic Spreading:**
- Disease spreads through social network
- Percolation threshold = epidemic threshold
- Guide for vaccination strategies

### Forest Fires

**Fire Spreading:**
- Trees = occupied sites
- Fire spreads to adjacent trees
- At p_c, fire transitions from contained to widespread

## Computational Considerations

### Grid Boundary Conditions

**Periodic boundaries:**
- Top connects to bottom, left to right
- Eliminates edge effects
- Better for measuring bulk properties

**Free boundaries:**
- Used in this simulator
- Natural for spanning cluster definition
- Edge effects decay as 1/N

### Monte Carlo Methods

Percolation is studied via Monte Carlo simulation:
1. Generate random grid with occupation probability p
2. Find clusters using efficient algorithm
3. Measure quantities of interest
4. Average over many trials

**Statistical Error:**
Standard error scales as 1/√(num_trials):
- 100 trials: ±3% typical error
- 400 trials: ±1.5% error
- 1600 trials: ±0.75% error

## Theoretical Results

### Exact Values (2D)

**Critical probability:**
```
p_c = 1/2  (proven for infinite square lattice)

Actually, p_c = 0.59274621... for site percolation
          p_c = 0.5         for bond percolation on same lattice
```

**Critical exponents:**
```
β = 5/36 ≈ 0.1389       (percolation probability)
ν = 4/3 ≈ 1.3333        (correlation length)
γ = 43/18 ≈ 2.3889      (mean cluster size)
τ = 187/91 ≈ 2.0549     (cluster size distribution)
```

### Scaling Relations

The exponents satisfy **scaling relations**:
```
γ = ν(2 - η)
dν = 2 - α
γ = (2 - η)ν
```

where d=2 is dimensionality.

## Further Reading

### Classic Papers

1. **Broadbent & Hammersley (1957)**
   - "Percolation processes I. Crystals and mazes"
   - Introduced percolation theory

2. **Kesten (1980)**
   - Proved p_c = 1/2 for 2D bond percolation

3. **Hoshen & Kopelman (1976)**
   - "Percolation and cluster distribution"
   - Introduced efficient cluster labeling algorithm

### Modern Reviews

1. **Stauffer & Aharony (1994)**
   - *Introduction to Percolation Theory*
   - Comprehensive textbook

2. **Newman & Ziff (2000)**
   - "Efficient Monte Carlo algorithm and high-precision results"
   - Modern computational methods

3. **Grimmett (1999)**
   - *Percolation*
   - Rigorous mathematical treatment

## See Also

- [Algorithm Details](algorithms.md) - Implementation of cluster-finding algorithms
- [Usage Guide](usage.md) - How to run percolation simulations
- [Estimation.py](../Estimation.py) - Implementation of p_c estimation
