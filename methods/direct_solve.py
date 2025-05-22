"""
direct_solve.py
================
Linear‑system solvers for PageRank when we rewrite the equation

    (I - (1-α)A) r = (1-α)/n · 1.

Although PageRank is usually computed iteratively, solving this *linear* system
provides a deterministic baseline for small/medium graphs.

Public API
----------
- solve_direct(M, b)     – wrapper around NumPy / SciPy *solve*
- solve_lu(M, b)         – LU decomposition (dense & sparse paths)
- solve_cholesky(M, b)   – Cholesky (only if matrix symmetric & positive‑definite)

All functions return the solution vector ``x``.  Internally auto‑detect whether
``M`` is dense (*ndarray*) or sparse (*csr/csc*).

Author: uetsymphonique
"""
from __future__ import annotations

import numpy as np
from typing import Union

try:
    import scipy.linalg as la
    import scipy.sparse as sp
    import scipy.sparse.linalg as spla
except ImportError:  # allow pure‑NumPy environment
    la = None  # type: ignore
    sp = None  # type: ignore
    spla = None  # type: ignore

Matrix = Union[np.ndarray, "sp.csr_matrix", "sp.csc_matrix"]
Vector = np.ndarray

__all__ = [
    "solve_direct",
    "solve_lu",
    "solve_cholesky",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dense_solve(M: np.ndarray, b: Vector) -> Vector:
    return np.linalg.solve(M, b)


def _sparse_solve(M: "sp.spmatrix", b: Vector) -> Vector:
    if spla is None:
        raise RuntimeError("SciPy is required for sparse solves.")
    return spla.spsolve(M, b)

# ---------------------------------------------------------------------------
# Public solvers
# ---------------------------------------------------------------------------

def solve_direct(M: Matrix, b: Vector) -> Vector:
    """General wrapper around dense ``np.linalg.solve`` or sparse ``spsolve``."""
    if hasattr(sp, "isspmatrix") and sp.isspmatrix(M):
        return _sparse_solve(M, b)
    return _dense_solve(M, b)


def solve_lu(M: Matrix, b: Vector) -> Vector:
    """Solve using LU decomposition.

    * Dense → ``scipy.linalg.lu_factor`` / ``lu_solve`` (if SciPy present)
    * Sparse → ``scipy.sparse.linalg.splu``
    """
    if hasattr(sp, "isspmatrix") and sp.isspmatrix(M):
        if spla is None:
            raise RuntimeError("SciPy sparse required for LU on sparse matrices.")
        lu = spla.splu(M.tocsc())
        return lu.solve(b)

    # Dense path -----------------------------------------------------------
    if la is None:
        # Fall back to NumPy's solve if SciPy missing
        return np.linalg.solve(M, b)
    lu, piv = la.lu_factor(M)
    return la.lu_solve((lu, piv), b)


def solve_cholesky(M: Matrix, b: Vector) -> Vector:
    """Solve via Cholesky factorisation (requires symmetric positive‑definite).

    Useful e.g. if *M* = ``I - (1-α)A`` becomes SPD (not always true for PageRank).
    """
    # Check symmetry quickly for dense
    def _is_symmetric(a: np.ndarray, tol: float = 1e-12):
        return np.allclose(a, a.T, atol=tol)

    if hasattr(sp, "isspmatrix") and sp.isspmatrix(M):
        if spla is None:
            raise RuntimeError("SciPy required for sparse Cholesky.")
        # Requires package scikit‑sparse for real sparse cholesky; fallback raise
        try:
            from sksparse.cholmod import cholesky  # type: ignore
        except Exception as exc:
            raise RuntimeError("Sparse Cholesky solver not available (install scikit‑sparse).") from exc
        factor = cholesky(M.tocsc())
        return factor(b)

    # Dense: use numpy / scipy --------------------------------------------
    if isinstance(M, np.ndarray):
        if not _is_symmetric(M):
            raise ValueError("Matrix is not symmetric; cannot use Cholesky.")
        # Use NumPy if SciPy not installed
        L = np.linalg.cholesky(M)
        y = np.linalg.solve(L, b)
        x = np.linalg.solve(L.T, y)
        return x

    raise ValueError("Unsupported matrix type for Cholesky solver.")
