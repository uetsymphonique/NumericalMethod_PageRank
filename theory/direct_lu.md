# Direct LU Method for PageRank

## Overview

Direct LU decomposition is a method for solving linear systems by decomposing the system matrix into lower and upper triangular matrices. In PageRank, we use this method to solve:

$$(I - \alpha P)x = (1-\alpha)v$$

### Derivation from PageRank Formula

Let's understand how we get from the original PageRank formula to the LU decomposition:

1. **Original PageRank Formula**:
   $$x = \alpha P x + (1-\alpha)v$$
   This formula says: "The PageRank of a page is the sum of the PageRanks of pages linking to it, weighted by their out-degrees, plus a small random jump."

2. **Rearranging Terms**:
   $$x - \alpha P x = (1-\alpha)v$$
   We move all terms with $x$ to the left side.

3. **Factoring Out x**:
   $$(I - \alpha P)x = (1-\alpha)v$$
   This is the form $Ax = b$ where:
   - $A = I - \alpha P^T$ (system matrix)
   - $b = (1-\alpha)v$ (right-hand side vector)

### LU Decomposition: Intuitive Explanation

LU decomposition is like breaking down a complex problem into simpler steps:

1. **Basic Idea**:
   - Decompose matrix $A$ into $L$ (lower triangular) and $U$ (upper triangular)
   - Solve $Ly = b$ first (forward substitution)
   - Then solve $Ux = y$ (backward substitution)

2. **Geometric Intuition**:
   - Imagine solving a maze
   - Instead of trying all paths at once
   - Break it into two simpler mazes:
     1. First maze (L): Only move down and right
     2. Second maze (U): Only move up and left

3. **Step-by-Step Process**:
   ```
   1. Decompose A into L and U
   2. Solve Ly = b (forward)
   3. Solve Ux = y (backward)
   ```

4. **Mathematical Formulation**:
   - $A = LU$ where:
     - $L$ is lower triangular with 1's on diagonal
     - $U$ is upper triangular
   - Solve $Ly = b$:
     $$y_i = \frac{1}{l_{ii}}\left(b_i - \sum_{j=1}^{i-1} l_{ij}y_j\right)$$
   - Solve $Ux = y$:
     $$x_i = \frac{1}{u_{ii}}\left(y_i - \sum_{j=i+1}^n u_{ij}x_j\right)$$

5. **Why It Works**:
   - Triangular systems are easy to solve
   - Decomposition is done once
   - Can solve for multiple right-hand sides
   - Numerically stable with pivoting

### Implementation Details

```python
def pagerank(G, alpha=0.85, permc_spec="COLAMD", drop_tol=1e-10):
    # 1. Build matrix A and vector b
    A = build_matrix(G, alpha)  # A = I - αP
    b = np.ones(n) * (1-alpha)/n
    
    # 2. LU decomposition with pivoting
    lu = splu(A.tocsc(), 
             permc_spec=permc_spec,
             options={"ILU_MILU": "SMILU_2"})
    
    # 3. Solve the system
    x = lu.solve(b)
    
    # 4. Normalize
    x = np.maximum(x, 0)
    x /= x.sum()
```

### Pivoting Strategies

1. **COLAMD (Column Approximate Minimum Degree)**:
   - Reduces fill-in during factorization
   - Good for sparse matrices
   - Default choice for PageRank

2. **NATURAL**:
   - No reordering
   - Fastest but may be unstable
   - Use only for well-conditioned matrices

3. **MMD_AT_PLUS_A**:
   - Minimum degree on $A^T + A$
   - Good for symmetric matrices
   - More expensive than COLAMD

4. **MMD_ATA**:
   - Minimum degree on $A^TA$
   - Good for least squares problems
   - Most expensive option

### Advantages and Limitations

#### Advantages:
- Direct method: no iterations needed
- High accuracy
- Can solve for multiple right-hand sides
- Numerically stable with pivoting

#### Limitations:
- Memory intensive: $O(n^2)$ storage
- Time complexity: $O(n^3)$
- Not suitable for very large graphs
- Fill-in can be significant

### Practical Considerations

1. **Graph Size**:
   - Suitable for graphs up to ~100k nodes
   - Memory usage grows quadratically
   - Consider iterative methods for larger graphs

2. **Pivoting Strategy**:
   - COLAMD: Good default choice
   - NATURAL: Fast but may be unstable
   - MMD variants: More expensive but better for special cases

3. **Drop Tolerance**:
   - Controls numerical stability
   - Typical values: 1e-10 to 1e-8
   - Smaller values = more accurate but more fill-in

4. **Memory Usage**:
   - Grows with graph size
   - Consider available RAM
   - May need to switch to iterative methods

## References

1. Davis, T. A. (2006). Direct Methods for Sparse Linear Systems
2. Langville, A. N., & Meyer, C. D. (2006). Google's PageRank and Beyond
3. Duff, I. S., et al. (2017). Direct Methods for Sparse Matrices 