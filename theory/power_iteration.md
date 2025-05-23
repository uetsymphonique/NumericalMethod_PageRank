# Power Iteration Method for PageRank

## Overview

Power Iteration is the simplest and most intuitive method for computing PageRank. It directly implements the original PageRank formula through iterative matrix-vector multiplication:

$$x_{k+1} = \alpha P x_k + (1-\alpha)v$$

### Derivation from PageRank Formula

The Power Iteration method directly uses the original PageRank formula:

1. **Original PageRank Formula**:
   $$x = \alpha P x + (1-\alpha)v$$
   This formula says: "The PageRank of a page is the sum of the PageRanks of pages linking to it, weighted by their out-degrees, plus a small random jump."

2. **Iterative Form**:
   $$x_{k+1} = \alpha P x_k + (1-\alpha)v$$
   - $x_k$ is the current PageRank vector
   - $x_{k+1}$ is the next PageRank vector
   - $P$ is the transition matrix
   - $\alpha$ is the damping factor
   - $v$ is the uniform distribution vector

### Power Iteration: Intuitive Explanation

Power Iteration is like a random surfer exploring the web:

1. **Basic Idea**:
   - Start with equal probability for all pages
   - At each step:
     1. Follow links with probability $\alpha$
     2. Jump to random page with probability $(1-\alpha)$
   - Repeat until probabilities stabilize

2. **Geometric Intuition**:
   - Imagine a drop of water flowing through a network of pipes
   - At each junction, the water splits according to the link weights
   - Some water evaporates and is redistributed evenly
   - Eventually, the water levels stabilize

3. **Step-by-Step Process**:
   ```
   1. Initialize: x₀ = uniform distribution
   2. For each iteration:
      a. Follow links: x' = αPx
      b. Handle dangling nodes
      c. Add random jump: x = x' + (1-α)v
      d. Check convergence
   ```

4. **Mathematical Formulation**:
   For each iteration $k$:
   $$x_{k+1} = \alpha P x_k + (1-\alpha)v$$
   where:
   - $P$ is the column-stochastic transition matrix
   - $x_k$ is the current PageRank vector
   - $v$ is the uniform distribution vector
   - $\alpha$ is the damping factor (typically 0.85)

5. **Why It Works**:
   - The process converges to the dominant eigenvector
   - The damping factor ensures convergence
   - The uniform vector prevents rank sinks
   - The process is guaranteed to converge

### Implementation Details

```python
def pagerank(G, alpha=0.85, tol=1e-6, max_iter=100):
    # Initialize
    N = G.number_of_nodes()
    p = np.full(N, 1.0/N)  # uniform distribution
    v = np.full(N, 1.0/N)  # uniform teleport
    
    # Build transition matrix
    A = build_transition_matrix(G)
    
    for _ in range(max_iter):
        # Update PageRank
        p_new = alpha * (A @ p + dangling_mass * v) + (1-alpha) * v
        
        # Check convergence
        err = np.abs(p_new - p).sum()
        if err < tol:
            break
            
        p = p_new
```

### Handling Special Cases

1. **Dangling Nodes**:
   - Nodes with no out-links
   - Their PageRank is redistributed uniformly
   - Handled by adding a uniform vector

2. **Rank Sinks**:
   - Groups of nodes that only link to each other
   - Prevented by the damping factor
   - The random jump ensures connectivity

3. **Disconnected Components**:
   - The random jump connects all components
   - Ensures a unique solution
   - Makes the matrix irreducible

### Convergence Properties

1. **Convergence Rate**:
   - Linear convergence
   - Rate depends on the second eigenvalue
   - Faster for well-connected graphs
   - Slower for sparse graphs

2. **Memory Usage**:
   - Very memory efficient
   - Only needs two vectors
   - Good for large graphs

3. **Advantages**:
   - Simple to implement
   - Memory efficient
   - Guaranteed convergence
   - Easy to understand

4. **Limitations**:
   - Linear convergence rate
   - May need many iterations
   - Not the fastest method
   - No acceleration techniques

### Practical Considerations

1. **Initialization**:
   - Uniform distribution is standard
   - Can use previous results as warm start
   - Initial guess doesn't affect final result

2. **Tolerance**:
   - Typical values: 1e-6 to 1e-8
   - Balance between accuracy and speed
   - L1 norm is used for convergence

3. **Maximum Iterations**:
   - Usually under 100
   - Depends on graph size and structure
   - Should be enough for most graphs

4. **Damping Factor**:
   - Typically 0.85
   - Controls convergence rate
   - Affects final rankings

## References

1. [The PageRank Algorithm](https://acme.byu.edu/00000180-6956-dde7-ad8c-6dde900c0001/pagerank)
2. [PageRank Algorithm - The Mathematics of Google Search](https://pi.math.cornell.edu/~mec/Winter2009/RalucaRemus/Lecture3/lecture3.html)