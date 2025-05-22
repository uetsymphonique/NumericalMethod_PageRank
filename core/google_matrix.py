"""
google_matrix.py
================
Construct the Google matrix used in PageRank with optional personalization.

Public API
----------
- build_google_matrix(A, alpha=0.85, sparse=False)
- build_personalized_google_matrix(A, teleport_vector, alpha=0.85, sparse=False)

Assumptions
-----------
* ``A`` **must** already be column‑stochastic (sum of each column = 1)
  **and** free of dangling nodes.  Use helpers in *transition_matrix.py*
  beforehand.
* ``alpha`` is the *continuation probability* (a.k.a. damping factor).
  Teleport probability is ``1 - alpha``.

Author: uetsymphonique
"""
from __future__ import annotations

import numpy as np
from typing import Union

try:
    import scipy.sparse as sp
except ImportError:
    sp = None  # type: ignore

__all__ = [
    "build_google_matrix",
    "build_personalized_google_matrix",
]

Matrix = Union[np.ndarray, "sp.csr_matrix"]

# ---------------------------------------------------------------------------
# Google matrix builders
# ---------------------------------------------------------------------------

def _as_sparse(mat: Matrix):
    """Convert *mat* to CSR if SciPy available, else raise."""
    if sp is None:
        raise RuntimeError("scipy.sparse is required for sparse matrices but not installed.")
    if sp.isspmatrix(mat):
        return mat.tocsr()
    return sp.csr_matrix(mat)


def build_google_matrix(A: Matrix, *, alpha: float = 0.85, sparse: bool | None = None) -> Matrix:
    """Return the *Google matrix* ``G = alpha*A + (1-alpha)/n * 11ᵀ``.

    Parameters
    ----------
    A
        Column‑stochastic matrix (n×n) **without dangling columns**.
    alpha
        Damping factor (probability of following a link).  Should lie in (0,1).
    sparse
        *None* (default) → inherit representation from *A*.
        Otherwise force output to be dense (False) or sparse (True).
    """
    n = A.shape[0]
    if not (0.0 < alpha < 1.0):
        raise ValueError("alpha must be in (0,1)")

    make_sparse = sp is not None and (sparse if sparse is not None else sp.isspmatrix(A))

    if make_sparse:
        A = _as_sparse(A)
        e = np.full(n, (1.0 - alpha) / n, dtype=A.dtype)  # teleport column
        # Outer product: E = e * 1ᵀ  (but build as rank‑1 update)
        G = A.copy().astype(float)
        G *= alpha
        # Add same column to every column → add vector * 1ᵀ
        # Efficient way: add e to each column's data via broadcasting-like trick
        rows = np.arange(n).repeat(n)
        cols = np.tile(np.arange(n), n)
        data = np.tile(e, n)
        teleport = sp.coo_matrix((data, (rows, cols)), shape=(n, n)).tocsr()
        G = G + teleport
        return G

    # Dense -----------------------------------------------------------------
    if isinstance(A, np.ndarray):
        G = alpha * A + ((1.0 - alpha) / n)
        return G.astype(float)

    # Fallback if user passed sparse but asked for dense
    G_dense = A.toarray().astype(float)
    return alpha * G_dense + ((1.0 - alpha) / n)


def build_personalized_google_matrix(
    A: Matrix,
    teleport_vector: np.ndarray,
    *,
    alpha: float = 0.85,
    sparse: bool | None = None,
) -> Matrix:
    """Google matrix with **personalized teleport vector**.

    ``G = alpha*A + (1-alpha) * v * 1ᵀ`` with ``v`` a probability vector
    (non‑negative, sum = 1).  Each column of ``V = v * 1ᵀ`` equals ``v``.
    """
    n = A.shape[0]
    if teleport_vector.shape != (n,):
        raise ValueError("teleport_vector must have shape (n,)")
    if not np.allclose(teleport_vector.sum(), 1.0):
        raise ValueError("teleport_vector must sum to 1")
    if (teleport_vector < 0).any():
        raise ValueError("teleport_vector must be non‑negative")

    make_sparse = sp is not None and (sparse if sparse is not None else sp.isspmatrix(A))

    if make_sparse:
        A = _as_sparse(A)
        G = A.copy().astype(float)
        G *= alpha
        # Build teleport in sparse form (rank‑1 matrix v * 1ᵀ)
        rows = np.arange(n).repeat(n)
        cols = np.tile(np.arange(n), n)
        data = np.tile((1.0 - alpha) * teleport_vector, n)
        teleport = sp.coo_matrix((data, (rows, cols)), shape=(n, n)).tocsr()
        G = G + teleport
        return G

    # Dense ---------------------------------------------------------------
    if isinstance(A, np.ndarray):
        G = alpha * A + (1.0 - alpha) * teleport_vector[:, None]
        return G.astype(float)

    # Fallback dense conversion
    A_dense = A.toarray().astype(float)
    return alpha * A_dense + (1.0 - alpha) * teleport_vector[:, None]
