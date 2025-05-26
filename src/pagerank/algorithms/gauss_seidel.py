"""
Gauss–Seidel (SOR) PageRank
---------------------------
Interface identical to other algorithms in the algorithms directory:
    pagerank(G, *, alpha, tol, max_iter, omega) -> (scores, residuals, elapsed)
omega = 1.0  ➜ Pure Gauss-Seidel.
0 < omega < 2 ➜ Successive Over-Relaxation.
omega can be a float or a callable function that takes (iteration, residuals) and returns float.
"""

from __future__ import annotations
import networkx as nx
import numpy as np, time
from scipy.sparse import csr_matrix
from typing import Union, Callable, List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

def find_optimal_omega(G: nx.DiGraph, alpha: float = 0.85, test_range: tuple = (1.0, 1.9), steps: int = 10) -> float:
    """
    Find optimal omega by testing a range of values and selecting the one with fastest convergence.
    
    Args:
        G: Input graph
        alpha: Damping factor
        test_range: Tuple of (min_omega, max_omega) to test
        steps: Number of omega values to test
        
    Returns:
        Optimal omega value that gives fastest convergence
    """
    logger.info("Finding optimal omega value...")
    
    # Test values in the range
    omega_values = np.linspace(test_range[0], test_range[1], steps)
    best_omega = None
    best_iterations = float('inf')
    best_residual = float('inf')
    test_results = []  # Store results for all tested omegas
    
    # Run a small number of iterations for each omega to find the best one
    test_iterations = 50  # Use fewer iterations for testing
    test_tol = 1e-6      # Use same tolerance as main problem
    
    for omega in omega_values:
        logger.info(f"Testing omega = {omega:.3f}")
        
        # Run Gauss-Seidel with current omega
        scores, residuals, _ = pagerank(G, alpha=alpha, tol=test_tol, max_iter=test_iterations, omega=omega)
        
        # Store results for this omega
        if residuals:
            iterations = len(residuals)
            final_residual = residuals[-1]
            test_results.append({
                'omega': omega,
                'iterations': iterations,
                'final_residual': final_residual
            })
            
            # Update best omega if this one is better
            if iterations < best_iterations or (iterations == best_iterations and final_residual < best_residual):
                best_omega = omega
                best_iterations = iterations
                best_residual = final_residual
    
    # Print summary of all tested omegas
    logger.info("\nOmega Testing Results:")
    logger.info("---------------------")
    for result in test_results:
        logger.info(f"ω = {result['omega']:.3f}: {result['iterations']} iterations, "
                   f"final residual = {result['final_residual']:.2e}")
    
    if best_omega is None:
        logger.warning("Could not find optimal omega, using default value 1.0")
        return 1.0
        
    logger.info(f"\nFound optimal omega = {best_omega:.3f} "
                f"(converged in {best_iterations} iterations, "
                f"final residual = {best_residual:.2e})")
    return best_omega

def create_dynamic_omega() -> Callable[[int, List[float]], float]:
    """
    Create a dynamic omega adjustment function that adapts based on convergence rate.
    
    Returns:
        A function that takes (iteration, residuals) and returns the next omega value
    """
    # Use lists to maintain state between calls
    current_omega = [1.0]  # Current omega value
    last_logged_iteration = [0]  # Track last logged iteration
    last_rate = [1.0]  # Track last convergence rate
    last_residual = [float('inf')]  # Track last residual
    divergence_count = [0]  # Track number of divergences
    best_omega = [1.0]  # Track best omega so far
    best_residual = [float('inf')]  # Track best residual so far
    
    def dynamic_omega(iteration: int, residuals: List[float]) -> float:
        if iteration < 2:
            if iteration == 1:  # Log only once at start
                logger.info(f"Starting with omega = {current_omega[0]:.3f}")
            return current_omega[0]  # Start with standard Gauss-Seidel
        
        # Calculate convergence rate
        rate = residuals[-2] / residuals[-1] if residuals[-1] > 0 else 1.0
        old_omega = current_omega[0]
        
        # Update best omega if current residual is better
        if residuals[-1] < best_residual[0]:
            best_residual[0] = residuals[-1]
            best_omega[0] = current_omega[0]
        
        # Check for divergence
        if residuals[-1] > last_residual[0]:
            # Divergence detected
            divergence_count[0] += 1
            
            if divergence_count[0] >= 3:
                # After 3 divergences, stick to best omega found
                current_omega[0] = best_omega[0]
                logger.warning(f"Iteration {iteration}: Multiple divergences detected, "
                             f"switching to best omega = {best_omega[0]:.3f}")
            else:
                # Reduce omega and try again
                current_omega[0] = max(1.0, current_omega[0] - 0.1)
                logger.warning(f"Iteration {iteration}: Divergence detected (residual increased from {last_residual[0]:.2e} to {residuals[-1]:.2e}), "
                             f"reducing omega from {old_omega:.3f} to {current_omega[0]:.3f}")
        else:
            # Normal adjustment based on convergence rate
            if rate < 1.2:  # Very slow convergence
                current_omega[0] = min(1.3, current_omega[0] + 0.02)  # Very small increase
                if current_omega[0] != old_omega:
                    logger.info(f"Iteration {iteration}: Very slow convergence (rate = {rate:.3f}), "
                              f"increasing omega from {old_omega:.3f} to {current_omega[0]:.3f}")
            elif rate > 1.8:  # Fast convergence
                current_omega[0] = max(1.0, current_omega[0] - 0.02)  # Small decrease
                if current_omega[0] != old_omega:
                    logger.info(f"Iteration {iteration}: Fast convergence (rate = {rate:.3f}), "
                              f"decreasing omega from {old_omega:.3f} to {current_omega[0]:.3f}")
            elif rate < last_rate[0]:  # Convergence is slowing down
                current_omega[0] = min(1.3, current_omega[0] + 0.01)  # Tiny increase
                if current_omega[0] != old_omega:
                    logger.info(f"Iteration {iteration}: Convergence slowing (rate = {rate:.3f} < {last_rate[0]:.3f}), "
                              f"increasing omega from {old_omega:.3f} to {current_omega[0]:.3f}")
        
        last_rate[0] = rate  # Update last rate
        last_residual[0] = residuals[-1]  # Update last residual
        
        # Log progress every 10 iterations
        if iteration - last_logged_iteration[0] >= 10:
            logger.info(f"Iteration {iteration}: Current omega = {current_omega[0]:.3f}, "
                      f"convergence rate = {rate:.3f}, residual = {residuals[-1]:.2e}")
            last_logged_iteration[0] = iteration
        
        return current_omega[0]
    
    return dynamic_omega

def pagerank(
    G: nx.DiGraph,
    *,
    alpha: float = 0.85,
    tol: float = 1e-6,
    max_iter: int = 100,
    omega: Union[float, Callable[[int, list[float]], float]] = 1.0,  # Can be float or function
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
    current_omega = omega if isinstance(omega, float) else 1.0  # Start with 1.0 if dynamic

    for iteration in range(max_iter):
        diff = 0.0
        d_mass = p[dangling.astype(bool)].sum()   # mass from dangling nodes
        
        # Update omega if it's a function
        if callable(omega):
            current_omega = omega(iteration, residual)
        
        for i in range(N):
            rank_new = (1 - alpha) * v[i]
            rank_new += alpha * d_mass * v[i]
            # ∑_{j→i} α * p_j / outdeg_j
            start, end = A.indptr[i], A.indptr[i + 1]
            rank_new += alpha * A.data[start:end] @ p[A.indices[start:end]]

            # apply SOR: xᵢ ← (1-ω)·xᵢ(old) + ω·rank_new
            rank_new = (1 - current_omega) * p[i] + current_omega * rank_new
            diff += abs(rank_new - p[i])
            p[i] = rank_new

        residual.append(diff)
        if diff < tol:
            break

    p /= p.sum()                 # normalize
    
    elapsed = time.perf_counter() - t0
    return {n: p[idx[n]] for n in nodes}, residual, elapsed 