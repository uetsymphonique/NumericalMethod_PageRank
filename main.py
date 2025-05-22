"""
main.py
=======
Entry-point script to run the full PageRank workflow:

1.  Load or generate a graph (edge-list file optional via CLI)
2.  Build transition matrix → handle dangling nodes → Google matrix
3.  Compute PageRank using multiple methods:
      • power method (iterative)
      • direct linear solve
      • eigendecomposition (dense or sparse)
      • NetworkX baseline
4.  Compare results, print errors, plot convergence curve & top-k comparison.

Usage
-----
$ python main.py               # run on built-in sample graph
$ python main.py path/to/edges.txt --alpha 0.9 --max_iter 200

Author: ChatGPT (OpenAI)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

from core.graph_loader import create_sample_graph, load_graph_from_edges
from core.transition_matrix import (
    build_transition_matrix,
    handle_dangling_nodes,
)
from core.google_matrix import build_google_matrix
from methods.power_method import power_method
from methods.direct_solve import solve_direct
from methods.eig_method import eig_solve, eig_sparse
from tools.baseline_compare import compute_networkx_pagerank, compare_ranks, print_top_k
from tools.evaluation import plot_convergence, plot_ranks_comparison, timing_benchmark

try:
    import scipy.sparse as sp
except ImportError:
    sp = None  # type: ignore

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args():
    p = argparse.ArgumentParser(description="PageRank demo (Phương pháp tính project)")
    p.add_argument("edge_file", nargs="?", help="Path to edge-list (optional)")
    p.add_argument("--alpha", type=float, default=0.85, help="Damping factor (default 0.85)")
    p.add_argument("--sparse", action="store_true", help="Use sparse matrices when SciPy is available")
    p.add_argument("--max_iter", type=int, default=100, help="Max iterations for power method")
    p.add_argument("--tol", type=float, default=1e-8, help="Tolerance for power method & eig_sparse")
    p.add_argument("--top_k", type=int, default=10, help="Top-k nodes to display")
    return p.parse_args()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_matrices(G: nx.DiGraph, alpha: float, use_sparse: bool):
    """Return (A, Gmat, nodes)."""
    A, nodes = build_transition_matrix(G, sparse=use_sparse)
    A = handle_dangling_nodes(A, inplace=True)
    Gmat = build_google_matrix(A, alpha=alpha)
    return A, Gmat, nodes


def _direct_system(A, alpha):
    """Return (M_system, b) for direct solve: (I - (1-alpha)A) r = (1-alpha)/n * 1."""
    n = A.shape[0]
    I = np.eye(n) if not (sp and sp.isspmatrix(A)) else sp.identity(n, format="csr")
    M_sys = I - (1.0 - alpha) * A
    b = np.full(n, (1.0 - alpha) / n)
    return M_sys, b

# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------

def main():
    args = _parse_args()

    # 1. Graph -------------------------------------------------------------
    if args.edge_file:
        if not Path(args.edge_file).exists():
            sys.exit(f"Edge file not found: {args.edge_file}")
        G = load_graph_from_edges(args.edge_file)
    else:
        G = create_sample_graph()

    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # 2. Matrices ----------------------------------------------------------
    A, Gmat, nodes = _build_matrices(G, args.alpha, args.sparse)
    n = len(nodes)

    # 3a. Power method -----------------------------------------------------
    r_power, errors = power_method(Gmat, tol=args.tol, max_iter=args.max_iter)
    print("Power-method converged in", len(errors), "iters, final L1 error", errors[-1])

    # 3b. Direct linear solve ---------------------------------------------
    M_sys, b = _direct_system(A, args.alpha)
    r_direct = solve_direct(M_sys, b)
    r_direct /= r_direct.sum()

    # 3c. Eigen ------------------------------------------------------------
    if sp and sp.isspmatrix(Gmat):
        r_eig = eig_sparse(Gmat, tol=args.tol)
    else:
        r_eig = eig_solve(np.asarray(Gmat))

    # 3d. NetworkX baseline ----------------------------------------------
    r_nx_vec, _ = compute_networkx_pagerank(G, alpha=args.alpha, nodes=nodes)

    # 4. Comparison --------------------------------------------------------
    for name, vec in {
        "direct": r_direct,
        "eigen": r_eig,
        "power": r_power,
    }.items():
        l1, l2 = compare_ranks(vec, r_nx_vec)
        print(f"{name:<7}: L1={l1:.3e}, L2={l2:.3e}")

    print("\nTop nodes (baseline):")
    print_top_k(r_nx_vec, nodes=nodes, k=args.top_k)

    # 5. Visualisations ----------------------------------------------------
    plt.figure()
    plot_convergence(errors)

    plt.figure(figsize=(8, 4))
    plot_ranks_comparison(r_nx_vec, r_power, nodes=nodes, top_k=args.top_k)

    # 6. Timing benchmark (optional quick demo) ---------------------------
    methods = {
        "direct": lambda M: solve_direct(*_direct_system(A, args.alpha)),
        "power": lambda M: power_method(Gmat, tol=args.tol, max_iter=args.max_iter)[0],
    }
    if n < 1000:  # skip eigen for very big matrices
        methods["eigen"] = lambda M: eig_solve(np.asarray(Gmat)) if not (sp and sp.isspmatrix(Gmat)) else eig_sparse(Gmat)
    tbl = timing_benchmark(methods, Gmat, repeat=1)
    try:
        import pandas as pd
        print("\nTiming (seconds):\n", tbl.to_string(index=False))
    except ImportError:
        print("\nTiming (seconds):", tbl)

    plt.show()


if __name__ == "__main__":
    main()
