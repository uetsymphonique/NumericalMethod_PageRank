import argparse
import time
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import importlib
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from .logging_utils import setup_logging, get_logger
from .graph_io import load_graph
from .plotting import (
    plot_convergence_comparison,
    plot_top10_comparison,
    save_metrics_comparison
)

# Import for table plotting
import matplotlib.gridspec as gridspec
from matplotlib.table import Table

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
                   help="PageRank algorithm(s) to use. Use comma-separated list (e.g. 'power,gauss_seidel') or 'all' for all algorithms")
    ap.add_argument("--omega", type=float, default=1.0,
                   help="SOR relaxation factor (only for gauss_seidel)")
    ap.add_argument("--auto-omega", action="store_true",
                   help="Automatically find optimal omega for gauss_seidel")
    ap.add_argument("--restart", type=int, default=30,
                   help="GMRES restart size (only for gmres_solver)")
    ap.add_argument("--preconditioner", type=str, default="ilu",
                   choices=["ilu", "jacobi", "none"],
                   help="Preconditioner for GMRES (only for gmres_solver)")
    ap.add_argument("--permc-spec", type=str, default="COLAMD",
                   choices=["COLAMD", "NATURAL", "MMD_AT_PLUS_A", "MMD_ATA"],
                   help="Pivot strategy for sparse LU (only for direct_lu)")
    ap.add_argument("--direct-drop-tol", type=float, default=1e-10,
                   help="Drop tolerance for sparse LU (only for direct_lu)")
    
    args = ap.parse_args()
    
    # Validate algorithm choices
    valid_algorithms = ["power", "gauss_seidel", "gmres_solver", "direct_lu", "all"]
    if args.algorithm == "all":
        args.algorithms = valid_algorithms[:-1]  # Exclude 'all'
    else:
        args.algorithms = [algo.strip() for algo in args.algorithm.split(",")]
        invalid = [algo for algo in args.algorithms if algo not in valid_algorithms[:-1]]
        if invalid:
            ap.error(f"Invalid algorithm(s): {', '.join(invalid)}. Valid choices are: {', '.join(valid_algorithms[:-1])}")
    
    return args

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
    elif args.algorithm == "direct_lu":
        kw.update(permc_spec=args.permc_spec,
                 drop_tol=args.direct_drop_tol)
    
    return mod.pagerank(G, **kw)

def create_table_image(df: pd.DataFrame, title: str, filename: str, figsize: Tuple[int, int] = (12, 8)):
    """Create and save a table visualization as an image"""
    # Create figure with appropriate size
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    ax.axis('tight')
    ax.axis('off')
    
    # Create table
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center',
        colColours=['#f2f2f2']*len(df.columns)  # Header background color
    )
    
    # Adjust table style
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.5)
    
    # Add title
    plt.title(title, pad=20, fontsize=12)
    
    # Save image
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    plt.close()

def main():
    args = parse_args()
    setup_logging(args.log_level)
    
    # Create directory for plots
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_dir = f"plots_{timestamp}"
    os.makedirs(plot_dir, exist_ok=True)
    logger.info(f"Saving plots to {plot_dir}/")
    
    # DataFrame to store metrics
    metrics = pd.DataFrame(columns=[
        'Algorithm', 
        'Time (s)', 
        'L1 Difference', 
        'Iterations',
        'Initial Residual',
        'Final Residual',
        'Convergence Rate',
        'Convergence Type'
    ])
    
    # DataFrame to store top nodes
    top_nodes_data = []
    
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

    # NetworkX reference (run only once)
    logger.info("Running NetworkX PageRank for comparison...")
    t0 = time.perf_counter()
    nx_scores = nx.pagerank(G, alpha=args.alpha, tol=args.tolerance, max_iter=args.max_iter)
    nx_elapsed = time.perf_counter() - t0

    # Store results of all algorithms
    all_results = []
    
    # Run each algorithm
    for algo in args.algorithms:
        logger.info(f"\n=== Running {algo} PageRank ===")
        args.algorithm = algo  # Update current algorithm
        scores, residuals, elapsed = run_algorithm(G, args)

        # Store results
        all_results.append({
            'algorithm': algo,
            'scores': scores,
            'residuals': residuals,
            'elapsed': elapsed
        })

        # L1 distance between vectors (ordered by node list)
        nodes_order = list(G.nodes())
        vec_custom = np.array([scores[n] for n in nodes_order])
        vec_nx = np.array([nx_scores[n] for n in nodes_order])
        l1_diff = np.abs(vec_custom - vec_nx).sum()

        # Calculate convergence metrics
        if residuals:
            initial_residual = residuals[0]
            final_residual = residuals[-1]
            convergence_rate = initial_residual / final_residual if final_residual > 0 else float('inf')
            convergence_type = "Iterative"
        else:
            initial_residual = float('nan')
            final_residual = float('nan')
            convergence_rate = float('nan')
            convergence_type = "Direct"

        # Store metrics
        metrics.loc[len(metrics)] = {
            'Algorithm': algo,
            'Time (s)': f"{elapsed:.3f}",
            'L1 Difference': f"{l1_diff:.6f}",
            'Iterations': len(residuals),
            'Initial Residual': f"{initial_residual:.6e}" if not np.isnan(initial_residual) else "N/A",
            'Final Residual': f"{final_residual:.6e}" if not np.isnan(final_residual) else "N/A",
            'Convergence Rate': f"{convergence_rate:.2f}x" if not np.isnan(convergence_rate) else "N/A",
            'Convergence Type': convergence_type
        }

        # Store top nodes
        top10 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
        for rank, (node, score) in enumerate(top10, 1):
            top_nodes_data.append({
                'Algorithm': algo,
                'Rank': rank,
                'Node': node,
                'Score': f"{score:.6f}",
                'NetworkX Score': f"{nx_scores[node]:.6f}",
                'Difference': f"{abs(score - nx_scores[node]):.6f}"
            })

        logger.info("Results:")
        print(f"Custom PageRank time: {elapsed:.3f}s")
        print(f"NetworkX time:        {nx_elapsed:.3f}s")
        print(f"L1 difference:        {l1_diff:.6f}")
        print(f"Iterations (custom):  {len(residuals)}")

        # Convergence information
        print("\n=== Convergence Information ===")
        if residuals:  # Only show convergence info if residuals exist
            print(f"Initial residual: {residuals[0]:.6f}")
            print(f"Final residual: {residuals[-1]:.6f}")
            print(f"Convergence rate (final/initial residual): {residuals[0]/residuals[-1]:.2f}x")
        else:
            print("Direct method - no iteration residuals available")

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

    # Plot and save visualizations
    plot_convergence_comparison(all_results, f"{plot_dir}/convergence.png")
    plot_top10_comparison(all_results, nx_scores, f"{plot_dir}/top10_comparison.png")
    
    # Save metrics and create tables
    save_metrics_comparison(metrics, pd.DataFrame(top_nodes_data), plot_dir)

    # Print metrics comparison table
    print("\n=== Algorithm Comparison ===")
    print(metrics.to_string(index=False))

if __name__ == "__main__":
    main() 