"""
eig_method.py
==============
Principal‑eigenvector solvers for PageRank.

Two flavours:
  • `eig_solve`  – dense matrix via ``numpy.linalg.eig`` (small graphs)
  • `eig_sparse` – sparse matrix via ``scipy.sparse.linalg.eigs`` (large graphs)

Both functions return the *dominant right eigenvector* corresponding to the
largest eigenvalue in magnitude (≈1 for a Google matrix) and normalise it so
that its L¹‑norm equals 1.

Author: uetsymphonique
"""
from __future__ import annotations

import numpy as np
from typing import Tuple, Union

try:
    import scipy.sparse as sp
    import scipy.sparse.linalg as spla
except ImportError:
    sp = None  # type: ignore
    spla = None  # type: ignore

Matrix = Union[np.ndarray, "sp.csr_matrix", "sp.csc_matrix"]
Vector = np.ndarray

__all__ = [
    "eig_solve",
    "eig_sparse",
]

# ---------------------------------------------------------------------------
# Dense eigen‑solver
# ---------------------------------------------------------------------------

def eig_solve(M: np.ndarray) -> Vector:
    """Return dominant eigenvector using full dense decomposition.

    Suitable for *n* ≲ 1 000.  For larger *n*, use ``eig_sparse``.
    """
    if M.shape[0] != M.shape[1]:
        raise ValueError("Matrix must be square")
    vals, vecs = np.linalg.eig(M)
    # Find index of eigenvalue with largest magnitude (should be ~1)
    idx = np.argmax(np.abs(vals))
    v = np.real(vecs[:, idx])
    # Ensure non‑negative & normalise L1
    v = np.abs(v)
    v /= v.sum()
    return v

# ---------------------------------------------------------------------------
# Sparse (iterative) eigen‑solver
# ---------------------------------------------------------------------------

def eig_sparse(
    M: "sp.spmatrix",
    *,
    tol: float = 1e-9,
    max_iter: int = 1_000,
) -> Vector:
    """Power‑like eigenvalue solve via ARPACK (``spla.eigs``).

    Parameters
    ----------
    M : sp.spmatrix
        Square sparse matrix (CSR/CSC) – Google matrix.
    tol : float
        Convergence tolerance passed to ARPACK.
    max_iter : int
        Maximum Arnoldi iterations.
    """
    if sp is None or spla is None:
        raise RuntimeError("SciPy with sparse support is required for eig_sparse.")
    if M.shape[0] != M.shape[1]:
        raise ValueError("Matrix must be square")

    # ARPACK may return complex values → take real part
    vals, vecs = spla.eigs(M, k=1, which="LM", tol=tol, maxiter=max_iter)
    v = np.real(vecs[:, 0])
    v = np.abs(v)
    v /= v.sum()
    return v
