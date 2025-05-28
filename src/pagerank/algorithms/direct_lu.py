"""Direct LU decomposition solver for PageRank.

Solve the system (I - α Pᵀ) x = (1-α) · v
by decomposing A = LU (with pivoting) then forward/back-solve.

• Uses scipy.sparse.linalg.splu (ILUPACK from SuiteSparse)
• Completely **linear**: one-time factorization + one-time solve
• Suitable for **sub-graphs ≤ ~100k** nodes (RAM ≈ few GB)
"""

from __future__ import annotations
import networkx as nx, numpy as np, time
from scipy.sparse import csr_matrix, eye
from scipy.sparse.linalg import splu
from ..logging_utils import get_logger
from typing import Dict, List, Tuple

logger = get_logger(__name__)


def build_matrix(G, alpha: float = 0.85) -> csr_matrix:
    """Return A = I - α·P as CSR sparse matrix."""
    n = G.number_of_nodes()
    idx = {u: i for i, u in enumerate(G.nodes())}
    
    # Build P (transpose matrix)
    rows, cols, data = [], [], []
    for u, v in G.edges():
        j, i = idx[u], idx[v]          # P: source column is destination node
        rows.append(i)
        cols.append(j)
        data.append(1.0 / G.out_degree(u))
    
    P = csr_matrix((data, (rows, cols)), shape=(n, n))
    return eye(n) - alpha * P


def pagerank(
    G: nx.DiGraph,
    *,
    alpha: float = 0.85,
    tol: float = 1e-12,          # not used, kept for interface consistency
    max_iter: int = 1,           # not used
    permc_spec: str = "COLAMD",  # SuiteSparse pivot strategy
    drop_tol: float = 1e-10      # for detecting singular matrix
) -> Tuple[Dict[int, float], List[float], float]:
    """
    Return (scores, residuals=[], elapsed).
    residuals is empty because this is a Direct method.
    """
    t0 = time.perf_counter()
    
    if G.number_of_nodes() == 0:
        return {}, [], 0.0

    logger.info(f"Starting Direct LU solver with {permc_spec} pivot strategy")
    logger.debug(f"Parameters: alpha={alpha}, drop_tol={drop_tol}")

    # 1. Build A (CSR) and vector b
    A = build_matrix(G, alpha)
    b = np.ones(G.number_of_nodes()) * (1 - alpha) / G.number_of_nodes()
    
    # 2. LU decomposition
    logger.info("Factorising sparse LU...")
    lu = splu(A.tocsc(), permc_spec=permc_spec,
              options={"ILU_MILU": "SMILU_2"})  # full pivoting
    
    # 3. Solve
    logger.debug("Solving system...")
    x = lu.solve(b)
    
    # 4. Normalize & statistics
    x = np.maximum(x, 0)
    x /= x.sum()
    
    elapsed = time.perf_counter() - t0
    logger.info(f"Direct LU completed in {elapsed:.2f}s")
    return dict(zip(G.nodes(), x)), [], elapsed 