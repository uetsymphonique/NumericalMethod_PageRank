# GMRES Algorithm for PageRank

## Overview

GMRES (Generalized Minimal Residual) is an iterative method for solving large, sparse linear systems of equations. In the context of PageRank, we use GMRES to solve the system:

$$(I - \alpha P^T)x = (1-\alpha)v$$

where:
- $I$ is the identity matrix
- $\alpha$ is the damping factor (typically 0.85)
- $P^T$ is the transpose of the transition matrix
- $v$ is the uniform distribution vector
- $x$ is the PageRank vector we want to find

## Algorithm Details

### 1. Problem Formulation

The PageRank problem can be written as:

$$Ax = b$$

where:
- $A = I - \alpha P^T$
- $b = (1-\alpha)v$

### 2. GMRES Method

GMRES works by:
1. Building a Krylov subspace
2. Finding the solution that minimizes the residual in this subspace
3. Restarting the process if needed

#### Krylov Subspace Construction

For a given initial guess $x_0$, GMRES builds the Krylov subspace:

$$K_m(A,r_0) = span\{r_0, Ar_0, A^2r_0, ..., A^{m-1}r_0\}$$

where $r_0 = b - Ax_0$ is the initial residual.

#### Solution Process

1. **Initialization**:
   - Start with initial guess $x_0$ (usually zero vector)
   - Calculate initial residual $r_0 = b - Ax_0$
   - Set $\beta = \|r_0\|_2$
   - Set $v_1 = r_0/\beta$

2. **Arnoldi Process**:
   For $j = 1,2,...,m$:
   - Compute $w_j = Av_j$
   - For $i = 1,...,j$:
     - $h_{i,j} = (w_j,v_i)$
     - $w_j = w_j - h_{i,j}v_i$
   - $h_{j+1,j} = \|w_j\|_2$
   - $v_{j+1} = w_j/h_{j+1,j}$

3. **Least Squares Problem**:
   - Find $y_m$ that minimizes $\|\beta e_1 - H_m y_m\|_2$
   - Update solution: $x_m = x_0 + V_m y_m$

4. **Restart Strategy**:
   - If convergence not achieved after $m$ iterations
   - Use $x_m$ as new initial guess
   - Restart the process

### 3. Preconditioning

To improve convergence, we use preconditioners:

1. **ILU Preconditioner**:
   - Incomplete LU decomposition
   - Approximates $A \approx LU$
   - Uses `scipy.sparse.linalg.spilu`
   - Parameters:
     - `drop_tol`: Drop tolerance for small elements
     - `fill_factor`: Maximum fill-in ratio

2. **Jacobi Preconditioner**:
   - Diagonal scaling
   - $M^{-1} = diag(A)^{-1}$
   - Simple but effective for diagonally dominant matrices

3. **No Preconditioner**:
   - Use GMRES without preconditioning
   - May be slower but uses less memory

### 4. Implementation Details

```python
def pagerank(G, alpha=0.85, tol=1e-6, max_iter=100, restart=30, preconditioner="ilu"):
    # Build linear operator A = I - alpha*P^T
    A_op, b = build_linear_operator(G, alpha)
    
    # Create preconditioner if needed
    M = make_preconditioner(A_csr, preconditioner)
    
    # Run GMRES
    x, info = gmres(A_op, b, 
                    rtol=tol,
                    restart=restart,
                    maxiter=max_iter,
                    M=M,
                    callback=callback)
```

### 5. Convergence Criteria

GMRES converges when:
- Relative residual norm is below tolerance: $\|r_k\|_2/\|r_0\|_2 < tol$
- Maximum iterations reached: $k \geq max\_iter$

### 6. Advantages and Limitations

#### Advantages:
- Works well for non-symmetric matrices
- No need to compute matrix powers
- Can use preconditioners to improve convergence
- Memory efficient (compared to direct methods)

#### Limitations:
- Convergence rate depends on eigenvalue distribution
- May need many iterations for ill-conditioned systems
- Restart strategy can slow down convergence
- Memory usage grows with restart size

### 7. Practical Considerations

1. **Restart Size**:
   - Larger restart size = better convergence
   - But more memory usage
   - Typical values: 20-50

2. **Preconditioner Choice**:
   - ILU: Good balance of speed and memory
   - Jacobi: Fast but less effective
   - None: Use when memory is limited

3. **Tolerance**:
   - Typical values: 1e-6 to 1e-8
   - Balance between accuracy and speed

4. **Memory Usage**:
   - Grows with restart size
   - Preconditioners add memory overhead
   - Consider graph size when choosing parameters

## References

1. Saad, Y., & Schultz, M. H. (1986). GMRES: A generalized minimal residual algorithm for solving nonsymmetric linear systems.
2. Barrett, R., et al. (1994). Templates for the Solution of Linear Systems: Building Blocks for Iterative Methods.
3. Langville, A. N., & Meyer, C. D. (2006). Google's PageRank and Beyond: The Science of Search Engine Rankings. 