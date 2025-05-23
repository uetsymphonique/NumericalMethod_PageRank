import networkx as nx
import numpy as np
import time
from scipy.sparse import csr_matrix
from typing import Dict, List, Tuple
from ..logging_utils import get_logger

logger = get_logger(__name__)

def pagerank(
    G: nx.DiGraph,
    *,
    alpha: float = 0.85,
    tol: float = 1e-6,
    max_iter: int = 100
) -> Tuple[Dict[int, float], List[float], float]:
    """
    Simple power‑iteration PageRank following the definition:
        p_{t+1} = α * Â * p_t + (1‑α) * v,
    where Â is a column‑stochastic adjacency matrix with dangling
    mass redistributed uniformly and v is the uniform vector.

    Returns
    -------
    pr : dict[node,float]
        Final PageRank scores (L1‑normalised).
    residuals : list[float]
        L1 error ‖p_{t+1} − p_t‖ at each iteration.
    elapsed : float
        Wall‑clock time in seconds.
    """
    t0 = time.perf_counter()
    
    N = G.number_of_nodes()
    if N == 0:
        return {}, [], 0.0

    # Relabel nodes to 0..N‑1 for vectorised ops
    nodes = list(G.nodes())
    index = {n: i for i, n in enumerate(nodes)}
    out_deg = np.array([G.out_degree(n) for n in nodes], dtype=float)

    # Build sparse column‑stochastic matrix in CSR
    row_idx, col_idx, data = [], [], []
    for u, v in G.edges():
        row_idx.append(index[v])      # note: transpose for column‑stochastic
        col_idx.append(index[u])
        data.append(1.0 / out_deg[index[u]] if out_deg[index[u]] else 0.0)
    A = csr_matrix((data, (row_idx, col_idx)), shape=(N, N))

    # Uniform teleport & dangling distribution
    v = np.full(N, 1.0 / N)
    dangling = (out_deg == 0).astype(float)

    p = np.full(N, 1.0 / N)
    residuals = []

    for _ in range(max_iter):
        # p_new = α * (A @ p  + (dangling·p) * v) + (1‑α) * v
        dangling_mass = (dangling * p).sum()
        p_new = alpha * (A @ p + dangling_mass * v) + (1.0 - alpha) * v

        err = np.abs(p_new - p).sum()
        residuals.append(err)
        if err < tol:
            p = p_new
            break
        p = p_new

    # Normalise exactly
    p /= p.sum()
    
    elapsed = time.perf_counter() - t0
    return {n: p[index[n]] for n in nodes}, residuals, elapsed 