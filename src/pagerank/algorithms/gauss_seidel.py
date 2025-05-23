"""
Gauss–Seidel (SOR) PageRank
---------------------------
Interface identical to other algorithms in the algorithms directory:
    pagerank(G, *, alpha, tol, max_iter, omega) -> (scores, residuals, elapsed)
omega = 1.0  ➜ Pure Gauss-Seidel.
0 < omega < 2 ➜ Successive Over-Relaxation.
"""

from __future__ import annotations
import networkx as nx
import numpy as np, time
from scipy.sparse import csr_matrix

def pagerank(
    G: nx.DiGraph,
    *,
    alpha: float = 0.85,
    tol: float = 1e-6,
    max_iter: int = 100,
    omega: float = 1.0,          # 1 → GS, 1<ω<2 → SOR acceleration
) -> tuple[dict, list, float]:

    t0 = time.perf_counter()
    
    N = G.number_of_nodes()
    if N == 0:
        return {}, [], 0.0

    nodes = list(G)
    idx   = {n: i for i, n in enumerate(nodes)}
    outdeg = np.fromiter((G.out_degree(n) for n in nodes), float, N)

    # sparse column-stochastic matrix (same as power.py)
    rows, cols, data = [], [], []
    for u, v in G.edges():
        if outdeg[idx[u]]:
            rows.append(idx[v]); cols.append(idx[u])
            data.append(1.0 / outdeg[idx[u]])
    A = csr_matrix((data, (rows, cols)), shape=(N, N))

    v = np.full(N, 1.0 / N)
    dangling = (outdeg == 0).astype(float)

    p = v.copy()                # initialize uniform
    residual = []

    for _ in range(max_iter):
        diff = 0.0
        d_mass = p[dangling.astype(bool)].sum()   # mass from dangling nodes
        for i in range(N):
            rank_new = (1 - alpha) * v[i]
            rank_new += alpha * d_mass * v[i]
            # ∑_{j→i} α * p_j / outdeg_j
            start, end = A.indptr[i], A.indptr[i + 1]
            rank_new += alpha * A.data[start:end] @ p[A.indices[start:end]]

            # apply SOR: xᵢ ← (1-ω)·xᵢ(old) + ω·rank_new
            rank_new = (1 - omega) * p[i] + omega * rank_new
            diff += abs(rank_new - p[i])
            p[i] = rank_new

        residual.append(diff)
        if diff < tol:
            break

    p /= p.sum()                 # normalize
    
    elapsed = time.perf_counter() - t0
    return {n: p[idx[n]] for n in nodes}, residual, elapsed 