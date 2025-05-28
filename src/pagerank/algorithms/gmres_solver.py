"""
GMRES PageRank solver with preconditioner options.
"""
from __future__ import annotations
import networkx as nx, numpy as np, time
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import LinearOperator, gmres, spilu
from ..logging_utils import get_logger
logger = get_logger(__name__)

def _build_linear_operator(G, alpha: float):
    """Returns (LinearOperator A, vector b, danglings_mask)"""
    N = G.number_of_nodes()
    nodes = list(G)
    idx = {n:i for i,n in enumerate(nodes)}
    outdeg = np.fromiter((G.out_degree(n) for n in nodes), float, N)
    rows, cols, data = [], [], []
    for u,v in G.edges():
        j = idx[u]; i = idx[v]
        if outdeg[j]:
            rows.append(i); cols.append(j); data.append(alpha/outdeg[j])
    P = csr_matrix((data,(rows,cols)), shape=(N,N))
    # A = I - alpha*P,   b = (1-alpha)*v
    def matvec(x):            # A·x
        return x - P @ x
    A = LinearOperator((N,N), matvec=matvec, dtype=float)
    b = np.full(N, (1-alpha)/N)
    return A, b, outdeg==0, nodes, P

def _make_preconditioner(A_csr: csr_matrix, kind:str):
    """Returns LinearOperator M^{-1} or None"""
    if kind == "none":
        return None
    if kind == "jacobi":
        diag = 1.0 / A_csr.diagonal()
        return LinearOperator(A_csr.shape, matvec=lambda x: diag * x)
    if kind == "ilu":
        logger.debug("Building ILU preconditioner...")
        ilu = spilu(A_csr.tocsc(), drop_tol=1e-4, fill_factor=10)
        return LinearOperator(A_csr.shape, matvec=ilu.solve)
    raise ValueError(f"Unknown preconditioner {kind}")

def pagerank(
    G: nx.DiGraph,
    *,
    alpha: float = 0.85,
    tol: float = 1e-6,
    max_iter: int = 100,
    restart: int = 30,
    preconditioner: str = "ilu",
) -> tuple[dict, list, float]:
    """
    GMRES PageRank solver.
    
    Args:
        G: Input graph
        alpha: Damping factor
        tol: Convergence threshold
        max_iter: Maximum number of iterations
        restart: Number of iterations before restart
        preconditioner: Type of preconditioner ("ilu", "jacobi", "none")
        
    Returns:
        Tuple containing:
        - Dict[int, float]: PageRank scores
        - List[float]: Residual history
        - float: Execution time
    """
    t0 = time.perf_counter()
    
    if G.number_of_nodes() == 0:
        return {}, [], 0.0

    logger.info(f"Starting GMRES solver with {preconditioner} preconditioner")
    logger.debug(f"Parameters: alpha={alpha}, tol={tol}, max_iter={max_iter}, restart={restart}")

    # Build LinearOperator
    A_op, b, dangling_mask, nodes, P = _build_linear_operator(G, alpha)

    # Build CSR matrix for preconditioner
    N = len(nodes)
    I = csr_matrix(np.eye(N))
    A_csr = I - alpha * P

    M = None
    if preconditioner != "none":
        M = _make_preconditioner(A_csr, preconditioner)

    res_history = []
    def callback(residual):
        """Callback function for GMRES"""
        if isinstance(residual, (int, float)):
            res_history.append(float(residual))
        else:
            res_history.append(float(np.linalg.norm(residual)))

    x, info = gmres(A_op, b, rtol=tol, restart=restart,
                    maxiter=max_iter, M=M, callback=callback,
                    callback_type='pr_norm')
    if info != 0:
        logger.warning("GMRES did not converge (info=%s)", info)
    else:
        logger.info("GMRES converged successfully")

    x = np.maximum(x, 0)
    x /= x.sum()
    
    elapsed = time.perf_counter() - t0
    logger.info(f"GMRES completed in {elapsed:.2f}s with {len(res_history)} iterations")
    return dict(zip(nodes, x)), res_history, elapsed 