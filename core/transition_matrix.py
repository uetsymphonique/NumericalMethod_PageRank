"""
transition_matrix.py
====================
Utilities for constructing the (column‑stochastic) transition matrix A
used in PageRank experiments.

Public API
----------
- build_transition_matrix(G, *, weight='weight', sparse=False, dtype=float)
    Convert a NetworkX graph to the raw adjacency / transition matrix.
- handle_dangling_nodes(A, *, inplace=False)
    Replace zero columns by a uniform vector 1/n.
- normalize_columns(A, *, inplace=False)
    Ensure each column of A sums to 1 (column‑stochastic).

All functions work with either *dense* ``numpy.ndarray`` or *sparse*
``scipy.sparse`` matrices.  The caller selects the representation via
*build_transition_matrix*.

Author: uetsymphonique
"""
from __future__ import annotations

import numpy as np
import networkx as nx
from typing import List, Tuple, Union

try:
    import scipy.sparse as sp
except ImportError:  # Allow running without SciPy for small demos
    sp = None  # type: ignore

__all__ = [
    "build_transition_matrix",
    "handle_dangling_nodes",
    "normalize_columns",
]

Matrix = Union[np.ndarray, "sp.csr_matrix"]

# ---------------------------------------------------------------------------
# Core builders
# ---------------------------------------------------------------------------

def build_transition_matrix(
    G: nx.DiGraph | nx.Graph,
    *,
    weight: str | None = "weight",
    sparse: bool = False,
    dtype: type = float,
) -> Tuple[Matrix, List[str]]:
    """Return transition matrix **A** and list of nodes (column order).

    Parameters
    ----------
    G : nx.DiGraph | nx.Graph
        Input graph.  If *G* is undirected, all edges are treated as *two*
        directed edges of equal weight.
    weight : str | None, default "weight"
        Edge attribute to use as weight. If *None*, treat all edges as 1.
    sparse : bool, default ``False``
        When *True* return a CSR sparse matrix; otherwise dense ``ndarray``.
    dtype : Python / NumPy dtype, default ``float``
        Data type of matrix entries.

    Returns
    -------
    A : ndarray or csr_matrix, shape (n, n)
        Raw transition matrix *before* dangling fix or damping.  Entry
        ``A[i, j]`` equals weight / out_degree(j) if there is an edge
        ``j → i``.
    nodes : list[str]
        Nodes in the order that corresponds to columns/rows of *A*.
    """
    if not sparse:
        # Dense path ---------------------------------------------------------
        nodes = list(G.nodes())
        n = len(nodes)
        idx = {node: k for k, node in enumerate(nodes)}
        A = np.zeros((n, n), dtype=dtype)

        # Accumulate outgoing weight per source node to normalise later
        out_weight = np.zeros(n, dtype=dtype)
        for src, dst, data in G.edges(data=True):
            w = data.get(weight, 1.0) if weight else 1.0
            j = idx[src]
            out_weight[j] += w
            A[idx[dst], j] += w  # remember: column = source, row = dest

        # Divide each column by its out_weight (if >0) -----------------------
        for j in range(n):
            if out_weight[j] > 0:
                A[:, j] /= out_weight[j]
        return A, nodes

    # Sparse path ------------------------------------------------------------
    if sp is None:
        raise RuntimeError("scipy is required for sparse=True but not installed.")

    nodes = list(G.nodes())
    n = len(nodes)
    idx = {node: k for k, node in enumerate(nodes)}

    data: list[float] = []
    rows: list[int] = []
    cols: list[int] = []
    out_weight = np.zeros(n, dtype=dtype)
    for src, dst, edge_data in G.edges(data=True):
        w = edge_data.get(weight, 1.0) if weight else 1.0
        j = idx[src]
        out_weight[j] += w
        rows.append(idx[dst])
        cols.append(j)
        data.append(w)

    # Build raw weighted adjacency in COO then normalize --------------------
    A = sp.coo_matrix((data, (rows, cols)), shape=(n, n), dtype=dtype).tocsr()
    # Need to divide each column by its out_weight
    for j in range(n):
        if out_weight[j] > 0:
            A.data[A.indptr[j] : A.indptr[j + 1]] /= out_weight[j]

    return A, nodes

# ---------------------------------------------------------------------------
# Dangling & normalisation helpers
# ---------------------------------------------------------------------------

def handle_dangling_nodes(A: Matrix, *, inplace: bool = False) -> Matrix:
    """Replace every zero column by uniform vector ``1/n``.

    Parameters
    ----------
    A
        Column‑stochastic matrix (dense or CSR).  Zero columns will be fixed.
    inplace : bool, default ``False``
        Modify *A* in place when possible (dense).  Sparse path always makes
        a copy because resizing data is tricky.

    Returns
    -------
    Matrix with no dangling columns.
    """
    n = A.shape[0]

    if isinstance(A, np.ndarray):
        col_sums = A.sum(axis=0)
        zero_cols = np.where(col_sums == 0)[0]
        if zero_cols.size == 0:
            return A  # nothing to do
        if not inplace:
            A = A.copy()
        A[:, zero_cols] = 1.0 / n
        return A

    # Sparse case -----------------------------------------------------------
    if sp is None:
        raise RuntimeError("SciPy required for sparse matrices.")

    col_sums = np.array(A.sum(axis=0)).ravel()
    zero_cols = np.where(col_sums == 0)[0]
    if zero_cols.size == 0:
        return A

    rows = np.repeat(np.arange(n), len(zero_cols))
    cols = np.tile(zero_cols, n)
    data = np.full(rows.shape, 1.0 / n, dtype=A.dtype)
    fill = sp.coo_matrix((data, (rows, cols)), shape=A.shape).tocsr()
    A = A + fill
    return A


def normalize_columns(A: Matrix, *, inplace: bool = False) -> Matrix:
    """Scale each column so that its sum equals 1.

    If a column is all‑zero, it is left unchanged (handle with
    *handle_dangling_nodes* first if needed).
    """
    if isinstance(A, np.ndarray):
        col_sums = A.sum(axis=0, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            scale = np.where(col_sums != 0, 1.0 / col_sums, 1.0)
        if inplace:
            A *= scale
            return A
        return A * scale

    # Sparse ---------------------------------------------------------------
    if sp is None:
        raise RuntimeError("SciPy required for sparse matrices.")

    n = A.shape[1]
    col_sums = np.array(A.sum(axis=0)).ravel()
    rows, cols = A.nonzero()
    new_data = A.data * (1.0 / col_sums[cols])
    return sp.csr_matrix((new_data, (rows, cols)), shape=A.shape)
