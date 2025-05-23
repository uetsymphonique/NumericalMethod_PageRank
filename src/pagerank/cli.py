import argparse
import time
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import importlib
from typing import Dict, List, Tuple
from .logging_utils import setup_logging, get_logger
from .graph_io import load_graph
from .plotting import plot_residuals, plot_top_k_comparison

logger = get_logger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    ap = argparse.ArgumentParser(description="PageRank Implementation")
    ap.add_argument("--graph", type=str, default="web-Google.txt",
                   help="Path to graph file")
    ap.add_argument("--limit", type=int, default=1000,
                   help="Limit number of nodes to process (-1 for full graph)")
    ap.add_argument("--log-level", type=str, default="INFO",
                   choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                   help="Set the logging level")
    ap.add_argument("--tolerance", type=float, default=1e-6,
                   help="Tolerance for convergence")
    ap.add_argument("--alpha", type=float, default=0.85,
                   help="Damping factor for PageRank")
    ap.add_argument("--max-iter", type=int, default=100,
                   help="Maximum number of iterations")
    ap.add_argument("--algorithm", type=str, default="power",
                   choices=["power", "gauss_seidel", "gmres_solver"],
                   help="PageRank algorithm to use")
    ap.add_argument("--omega", type=float, default=1.0,
                   help="SOR relaxation factor (only for gauss_seidel)")
    ap.add_argument("--auto-omega", action="store_true",
                   help="Automatically find optimal omega for gauss_seidel")
    ap.add_argument("--restart", type=int, default=30,
                   help="GMRES restart size (only for gmres_solver)")
    ap.add_argument("--preconditioner", type=str, default="ilu",
                   choices=["ilu", "jacobi", "none"],
                   help="Preconditioner for GMRES (only for gmres_solver)")
    return ap.parse_args()

def find_optimal_omega(G: nx.DiGraph, alpha: float = 0.85) -> float:
    """Find optimal omega using the approximate formula for Google matrix."""
    rho = alpha
    omega_opt = 2 / (1 + (1 - rho**2)**0.5)
    return omega_opt

def run_algorithm(G: nx.DiGraph, args: argparse.Namespace) -> Tuple[Dict[int, float], List[float], float]:
    """Run the specified PageRank algorithm."""
    mod = importlib.import_module(f"pagerank.algorithms.{args.algorithm}")
    kw = dict(alpha=args.alpha, tol=args.tolerance, max_iter=args.max_iter)
    
    if args.algorithm == "gauss_seidel":
        if args.auto_omega:
            omega = find_optimal_omega(G, args.alpha)
            logger.info(f"Using optimal omega = {omega:.3f}")
        else:
            omega = args.omega
        kw["omega"] = omega
    elif args.algorithm == "gmres_solver":
        kw.update(restart=args.restart, preconditioner=args.preconditioner)
    
    return mod.pagerank(G, **kw)

def main():
    args = parse_args()
    setup_logging(args.log_level)
    
    logger.info(f"Loading graph from: {args.graph}")
    if args.limit == -1:
        logger.info("Processing full graph (no node limit)")
    else:
        logger.info(f"Processing graph with node limit: {args.limit}")
    
    G = load_graph(args.graph, limit_nodes=args.limit)
    logger.info(f"Graph loaded with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    logger.info(f"Graph density: {nx.density(G):.6f}")
    logger.info(f"Number of dangling nodes: {sum(1 for n in G if G.out_degree(n) == 0)}")
    logger.info(f"Using tolerance: {args.tolerance}, alpha: {args.alpha}")

    # Run custom PageRank
    logger.info(f"Running {args.algorithm} PageRank...")
    scores, residuals, elapsed = run_algorithm(G, args)

    # NetworkX reference
    logger.info("Running NetworkX PageRank for comparison...")
    t0 = time.perf_counter()
    nx_scores = nx.pagerank(G, alpha=args.alpha, tol=args.tolerance, max_iter=args.max_iter)
    nx_elapsed = time.perf_counter() - t0

    # L1 distance between vectors (ordered by node list)
    nodes_order = list(G.nodes())
    vec_custom = np.array([scores[n] for n in nodes_order])
    vec_nx = np.array([nx_scores[n] for n in nodes_order])
    l1_diff = np.abs(vec_custom - vec_nx).sum()

    logger.info("Results:")
    print(f"Custom PageRank time: {elapsed:.3f}s")
    print(f"NetworkX time:        {nx_elapsed:.3f}s")
    print(f"L1 difference:        {l1_diff:.6f}")
    print(f"Iterations (custom):  {len(residuals)}")

    # Graph information
    print("\n=== Graph Information ===")
    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")
    print(f"Graph density: {nx.density(G):.6f}")

    # Convergence information
    print("\n=== Convergence Information ===")
    print(f"Initial residual: {residuals[0]:.6f}")
    print(f"Final residual: {residuals[-1]:.6f}")
    print(f"Convergence rate (final/initial residual): {residuals[0]/residuals[-1]:.2f}x")

    # Top nodes information
    print("\n=== Top 10 Nodes by PageRank ===")
    top10_custom = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\nCustom PageRank:")
    for node, score in top10_custom:
        print(f"Node {node}: {score:.6f}")

    top10_nx = sorted(nx_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\nNetworkX PageRank:")
    for node, score in top10_nx:
        print(f"Node {node}: {score:.6f}")

    # Plot results
    plot_residuals(residuals, title=f"{args.algorithm.capitalize()} PageRank Convergence")
    plot_top_k_comparison(scores, nx_scores, k=10, 
                         title=f"Top-10 PageRank Scores Comparison\n{args.algorithm.capitalize()} vs NetworkX")
    plt.show()

if __name__ == "__main__":
    main() 