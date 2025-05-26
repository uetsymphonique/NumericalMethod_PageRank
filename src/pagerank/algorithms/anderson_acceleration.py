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
    max_iter: int = 100,
    m: int = 2  # Number of previous vectors to use for acceleration
) -> Tuple[Dict[int, float], List[float], float]:
    """
    PageRank with Anderson Acceleration:
        p_{t+1} = (1-β)G(p_t) + βG(p_{t-1})
    where G(p) = α * Â * p + (1‑α) * v is the standard PageRank update,
    and β is optimized using the previous m vectors.

    Parameters
    ----------
    G : nx.DiGraph
        Directed graph
    alpha : float, optional
        Damping factor, by default 0.85
    tol : float, optional
        Error tolerance, by default 1e-6
    max_iter : int, optional
        Maximum number of iterations, by default 100
    m : int, optional
        Number of previous vectors to use for acceleration, by default 2

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

    # Initialize vectors
    p = np.full(N, 1.0 / N)
    residuals = []
    history = []  # Store previous vectors for acceleration
    last_err = float('inf')

    for _ in range(max_iter):
        # Standard PageRank update
        dangling_mass = (dangling * p).sum()
        p_new = alpha * (A @ p + dangling_mass * v) + (1.0 - alpha) * v

        # Store current vector in history
        history.append(p_new)
        if len(history) > m:
            history.pop(0)  # Keep only last m vectors

        # Apply Anderson acceleration if we have enough history
        if len(history) > 1:
            # Calculate differences between consecutive vectors
            diffs = np.diff(history, axis=0)
            
            # Solve least squares problem to find optimal coefficients
            try:
                # Use QR decomposition for better numerical stability
                Q, R = np.linalg.qr(diffs[:-1].T)
                beta = np.linalg.solve(R, Q.T @ diffs[-1])
                
                # Apply acceleration with stability check
                beta = beta.reshape(-1, 1)
                p_acc = history[-1] + np.sum(beta * diffs[:-1], axis=0)
                
                # Check if acceleration improved the result
                err_acc = np.abs(p_acc - p).sum()
                if err_acc < last_err:
                    p_new = p_acc
                else:
                    logger.debug("Acceleration rejected, using standard update")
            except np.linalg.LinAlgError:
                # Fall back to standard update if acceleration fails
                logger.debug("Anderson acceleration failed, using standard update")
                p_new = history[-1]

        err = np.abs(p_new - p).sum()
        residuals.append(err)
        last_err = err
        
        if err < tol:
            p = p_new
            break
        p = p_new

    # Normalise exactly
    p /= p.sum()
    
    elapsed = time.perf_counter() - t0
    return {n: p[index[n]] for n in nodes}, residuals, elapsed
