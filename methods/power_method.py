"""
power_method.py
================
Iterative power‑method solver for PageRank.

Given the Google matrix *M* (column‑stochastic, all entries positive), this
module computes the principal eigenvector corresponding to eigenvalue 1 – the
PageRank vector – via repeated matrix–vector multiplication:

\[ r_{k+1} = M r_k,\  \|r_{k+1}\|_1 = 1. \]

Public API
----------
- power_method(M, tol=1e-8, max_iter=100, x0=None, return_history=True)

Returns the stationary vector and, optionally, a list of L1‑errors per step so
caller can plot a convergence curve.

Author: uetsymphonique
"""
from __future__ import annotations

import numpy as np
from typing import List, Sequence, Tuple, Union

try:
    import scipy.sparse as sp
except ImportError:  # SciPy optional
    sp = None  # type: ignore

__all__ = ["power_method"]

Vector = np.ndarray
Matrix = Union[np.ndarray, "sp.csr_matrix", "sp.csc_matrix"]

# ---------------------------------------------------------------------------
# Main solver
# ---------------------------------------------------------------------------

def power_method(
    M: Matrix,
    *,
    tol: float = 1e-8,
    max_iter: int = 100,
    x0: Vector | None = None,
    return_history: bool = True,
) -> Tuple[Vector, List[float] | None]:
    """Compute PageRank vector by power iteration.

    Parameters
    ----------
    M
        Google matrix (column‑stochastic, positive).  Can be dense *ndarray*
        or sparse CSR/CSC.
    tol
        L1‑norm stopping threshold.  Stop when ‖x_{k+1} - x_k‖₁ < `tol`.
    max_iter
        Maximum number of iterations.
    x0
        Optional initial vector.  If *None*, use uniform distribution.
    return_history
        When *True* return list of errors per iteration (for plotting).

    Returns
    -------
    r : np.ndarray, shape (n,)
        Approximate PageRank vector (∑ r = 1).
    errors : list[float] | None
        L1‑norm of successive differences.  ``None`` if `return_history`
        is *False*.
    """
    if sp is not None and sp.isspmatrix(M):
        n = M.shape[0]
        matvec = M.dot  # sparse mat‑vec
    else:
        n = M.shape[0]
        matvec = lambda v: M @ v  # dense path

    if x0 is None:
        x = np.full(n, 1.0 / n, dtype=float)
    else:
        if x0.shape != (n,):
            raise ValueError("x0 must have shape (n,)")
        if (x0 < 0).any():
            raise ValueError("x0 must be non‑negative")
        x = x0 / x0.sum()  # normalise

    errors: List[float] = []

    for _ in range(max_iter):
        y = matvec(x)
        # Numerical guard: enforce positivity & normalise L1 = 1
        y = np.abs(y)
        y_sum = y.sum()
        if y_sum == 0:
            raise RuntimeError("Vector became zero – invalid Google matrix?")
        y /= y_sum

        err = np.linalg.norm(y - x, ord=1)
        errors.append(err)
        x = y
        if err < tol:
            break

    return (x, errors if return_history else None)
