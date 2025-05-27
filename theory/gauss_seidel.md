# Gauss-Seidel and SOR Methods for PageRank

## Overview

Gauss-Seidel (GS) and Successive Over-Relaxation (SOR) are iterative methods for solving linear systems. In PageRank, we use these methods to solve:

$$(I - \alpha P)x = (1-\alpha)v$$

### Derivation from PageRank Formula

Let's understand how we get from the original PageRank formula to the Gauss-Seidel equation:

1. **Original PageRank Formula**:
   $$x = \alpha P x + (1-\alpha)v$$
   This formula says: "The PageRank of a page is the sum of the PageRanks of pages linking to it, weighted by their out-degrees, plus a small random jump."

2. **Rearranging Terms**:
   $$x - \alpha P x = (1-\alpha)v$$
   We move all terms with $x$ to the left side.

3. **Factoring Out x**:
   $$(I - \alpha P)x = (1-\alpha)v$$
   This is the form $Ax = b$ where:
   - $A = I - \alpha P$ (system matrix)
   - $b = (1-\alpha)v$ (right-hand side vector)

### Gauss-Seidel Method: Intuitive Explanation

Gauss-Seidel is like solving a puzzle by updating one piece at a time, using the most recent information:

1. **Basic Idea**:
   - Instead of updating all components at once (like in Power Iteration)
   - We update one component at a time
   - Use the newest values immediately for the next updates

2. **Geometric Intuition**:
   - Imagine you're climbing a mountain
   - Instead of taking big steps in all directions
   - You take small steps, always moving in the best direction based on your current position

3. **Step-by-Step Process**:
   ```
   For each iteration:
      For each component i:
         1. Calculate new value using latest values
         2. Update immediately
         3. Use this new value for next components
   ```

4. **Mathematical Formulation**:
   For each component $i$:
   $$x_i^{(k+1)} = \frac{1}{a_{ii}} \left(b_i - \sum_{j=1}^{i-1} a_{ij}x_j^{(k+1)} - \sum_{j=i+1}^n a_{ij}x_j^{(k)}\right)$$

5. **Why It Works**:
   - Uses most recent information
   - Often converges faster than Jacobi method
   - Natural for sparse matrices (like PageRank)

### Successive Over-Relaxation (SOR)

SOR is an acceleration technique for Gauss-Seidel:

1. **Basic Idea**:
   - Take a weighted average of old and new values
   - Weight factor $\omega$ controls the step size
   - $\omega = 1$ gives pure Gauss-Seidel
   - $1 < \omega < 2$ gives over-relaxation

2. **Mathematical Formulation**:
   $$x_i^{(k+1)} = (1-\omega)x_i^{(k)} + \omega \cdot \text{GS update}$$

3. **Why SOR Works**:
   - Helps overcome slow convergence
   - Can significantly speed up convergence
   - Optimal $\omega$ depends on the problem

### Omega Selection Strategies

We implement three strategies for selecting the relaxation parameter $\omega$:

1. **Fixed Omega**:
   - Uses a constant value for $\omega$ throughout iterations
   - Default value is 1.0 (pure Gauss-Seidel)
   - Can be set to other values (e.g., 1.1, 1.2) for over-relaxation
   - Most stable but may be slower than optimal
   - Good for initial testing and well-behaved graphs

2. **Auto Omega**:
   - Automatically finds optimal $\omega$ by testing a range of values
   - Tests values from 1.0 to 1.3 in small steps (0.01-0.05)
   - Uses a small number of iterations (20-30) for each test
   - Selects $\omega$ with fastest convergence rate
   - Best for one-time setup of a graph
   - Parameters:
     - `omega_range`: Range of values to test (e.g., 1.0-1.3)
     - `omega_step`: Step size between values (e.g., 0.01)
     - `test_iterations`: Number of iterations for each test
     - `convergence_threshold`: Threshold for convergence test

3. **Dynamic Omega**:
   - Adapts $\omega$ during iteration based on convergence behavior
   - Starts with $\omega = 1.0$ (pure Gauss-Seidel)
   - Adjusts $\omega$ based on convergence rate:
     - If convergence is slow (rate < 1.2): increase $\omega$ slightly
     - If convergence is fast (rate > 1.8): decrease $\omega$ slightly
     - If divergence detected: reduce $\omega$ significantly
   - Includes safety mechanisms:
     - Tracks best $\omega$ found so far
     - Reduces $\omega$ when divergence detected
     - Switches to best $\omega$ after multiple divergences
     - Enforces upper and lower bounds (e.g., 1.0-1.3)
   - Parameters:
     - `min_omega`: Minimum allowed value (e.g., 1.0)
     - `max_omega`: Maximum allowed value (e.g., 1.3)
     - `omega_step`: Step size for adjustments (e.g., 0.01)
     - `divergence_threshold`: Threshold for detecting divergence
     - `max_divergence_count`: Maximum allowed divergences before switching to best omega

### Implementation Details

```python
def pagerank(G, alpha=0.85, tol=1e-6, max_iter=100, omega_strategy="fixed", omega=1.0):
    # Initialize
    p = v.copy()  # uniform distribution
    
    # Setup omega strategy
    if omega_strategy == "fixed":
        omega_func = lambda: omega
    elif omega_strategy == "auto":
        omega_func = find_optimal_omega(G, alpha, tol)
    else:  # dynamic
        omega_func = DynamicOmega(
            min_omega=1.0,
            max_omega=1.3,
            step=0.01,
            divergence_threshold=1e-3,
            max_divergence_count=3
        )
    
    for _ in range(max_iter):
        diff = 0.0
        d_mass = p[dangling].sum()  # mass from dangling nodes
        
        for i in range(N):
            # Calculate new rank
            rank_new = (1 - alpha) * v[i]
            rank_new += alpha * d_mass * v[i]
            rank_new += alpha * sum(p[j]/outdeg[j] for j in G.predecessors(i))
            
            # Get current omega value
            current_omega = omega_func()
            
            # Apply SOR
            rank_new = (1 - current_omega) * p[i] + current_omega * rank_new
            
            # Update and track difference
            diff += abs(rank_new - p[i])
            p[i] = rank_new
            
        if diff < tol:
            break
```

### Convergence Properties

1. **Convergence Rate**:
   - Generally faster than Power Iteration
   - SOR can be much faster with optimal $\omega$
   - Convergence depends on matrix properties
   - Dynamic omega can adapt to changing convergence rates

2. **Memory Usage**:
   - Very memory efficient
   - Only needs one vector
   - Good for large graphs

3. **Advantages**:
   - Simple to implement
   - Memory efficient
   - Can be accelerated with SOR
   - Natural for sparse matrices
   - Flexible omega selection strategies

4. **Limitations**:
   - Convergence rate varies
   - Optimal $\omega$ may be hard to find
   - Not always faster than other methods
   - Dynamic omega requires careful tuning

### Practical Considerations

1. **Choosing $\omega$ Strategy**:
   - Fixed ($\omega = 1.0$): Most stable, good for testing
   - Auto: Best for one-time setup
   - Dynamic: Best for varying convergence rates

2. **Tolerance**:
   - Typical values: 1e-6 to 1e-8
   - Balance between accuracy and speed
   - Affects convergence detection

3. **Maximum Iterations**:
   - Usually 100-1000
   - Depends on graph size and desired accuracy
   - More important for dynamic omega

4. **Dynamic Omega Parameters**:
   - Convergence rate thresholds: 1.2 (slow) and 1.8 (fast)
   - Omega adjustment steps: 0.02 (normal), 0.01 (tiny)
   - Maximum omega: 1.3 (prevent divergence)
   - Divergence recovery: -0.1 reduction

## References

1. [A Study on Comparison of Jacobi, GaussSeidel and Sor Methods for the Solution in System of Linear Equations](https://ijmttjournal.org/public/assets/volume-56/number-4/IJMTT-V56P531.pdf)
2. [Iterative Methods: SOR Method](https://engcourses-uofa.ca/books/numericalanalysis/linear-systems-of-equations/iterative-methods/sor-method/)
