import networkx as nx
import numpy as np
import time
from scipy.sparse import csr_matrix
from ..logging_utils import get_logger
from typing import Dict, List, Tuple

logger = get_logger(__name__)

def pagerank(
    G: nx.DiGraph,
    *,
    alpha: float = 0.85,
    tol: float = 1e-6,
    max_iter: int = 100,
) -> Tuple[Dict[int, float], List[float], float]:
    """
    Power iteration PageRank solver.
    """
    t0 = time.perf_counter()
    
    if G.number_of_nodes() == 0:
        return {}, [], 0.0

    logger.info("Starting Power Iteration solver")
    logger.debug(f"Parameters: alpha={alpha}, tol={tol}, max_iter={max_iter}")

    # Build transition matrix P
    n = G.number_of_nodes()
    idx = {u: i for i, u in enumerate(G.nodes())}
    rows, cols, data = [], [], []
    for u, v in G.edges():
        j, i = idx[u], idx[v]
        rows.append(i)
        cols.append(j)
        data.append(1.0 / G.out_degree(u))
    P = csr_matrix((data, (rows, cols)), shape=(n, n))

    # Initialize
    x = np.ones(n) / n
    res_history = []
    last_res = float('inf')

    # Power iteration
    for i in range(max_iter):
        x_new = alpha * (P @ x) + (1 - alpha) / n
        res = np.linalg.norm(x_new - x, ord=1)
        res_history.append(res)
        
        if i % 10 == 0:
            logger.debug(f"Iteration {i}: residual = {res:.2e}")
            
        if res < tol:
            logger.info(f"Converged after {i+1} iterations")
            break
            
        x = x_new
        last_res = res
    else:
        logger.warning(f"Did not converge after {max_iter} iterations")

    # Normalize
    x = np.maximum(x, 0)
    x /= x.sum()
    
    elapsed = time.perf_counter() - t0
    logger.info(f"Power Iteration completed in {elapsed:.2f}s")
    return dict(zip(G.nodes(), x)), res_history, elapsed 