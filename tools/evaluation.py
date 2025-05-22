"""
evaluation.py
==============
Visualization & benchmarking helpers for PageRank experiments.

Public API
----------
- plot_convergence(errors, logscale=True, ax=None)
    Plot L1‑error versus iteration for power‑method or any iterative solver.

- plot_ranks_comparison(r1, r2, nodes=None, top_k=20, ax=None)
    Show side‑by‑side bar chart (or scatter) of two PageRank vectors on the
    top‑k ranked nodes.

- timing_benchmark(methods, M, b=None, repeat=3)
    Measure elapsed time for each *callable* in ``methods`` on the same input
    matrix (and optional *b* vector).  Return *pandas.DataFrame*.

Author: uetsymphonique
"""
from __future__ import annotations

import time
from typing import Callable, Dict, List, Sequence, Any

import numpy as np
import matplotlib.pyplot as plt

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore

from tools.baseline_compare import _auto_to_vector  # type: ignore  # internal util

__all__ = [
    "plot_convergence",
    "plot_ranks_comparison",
    "timing_benchmark",
]

# ---------------------------------------------------------------------------
# Convergence curve
# ---------------------------------------------------------------------------

def plot_convergence(errors: Sequence[float], *, logscale: bool = True, ax=None) -> None:
    """Plot iteration errors (usually L1) on a line graph.

    Parameters
    ----------
    errors : list-like
        Error value per iteration.
    logscale : bool, default True
        Use semilogy (log‑y) if True.
    ax : matplotlib axes, optional
        Plot inside existing axes.
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    iters = np.arange(1, len(errors) + 1)
    if logscale:
        ax.semilogy(iters, errors, "-o", linewidth=1.5)
    else:
        ax.plot(iters, errors, "-o", linewidth=1.5)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("L1 error")
    ax.set_title("Convergence curve (iterative PageRank)")
    ax.grid(True, which="both", linestyle="--", alpha=0.3)
    fig.tight_layout()

# ---------------------------------------------------------------------------
# Rank comparison plot
# ---------------------------------------------------------------------------

def plot_ranks_comparison(
    r1: "np.ndarray | Dict",
    r2: "np.ndarray | Dict",
    *,
    nodes: Sequence[Any] | None = None,
    top_k: int = 20,
    ax=None,
) -> None:
    """Plot bar‑chart comparison of two PageRank results on top‑k nodes.

    Parameters
    ----------
    r1, r2
        PageRank outputs (vector or dict).  If vector, supply *nodes*.
    nodes : list, optional
        List of node labels matching vector order.
    top_k : int, default 20
        Number of highest ranked nodes to display.
    ax : matplotlib axes, optional
        Where to draw.
    """
    if isinstance(r1, dict):
        # align by descending ranking in r1
        sorted_nodes = sorted(r1.items(), key=lambda x: x[1], reverse=True)
        nodes_top = [n for n, _ in sorted_nodes[:top_k]]
        v1 = np.array([r1[n] for n in nodes_top])
        v2 = np.array([r2[n] if isinstance(r2, dict) else r2[nodes.index(n)] for n in nodes_top])
    else:
        if nodes is None:
            raise ValueError("nodes list required when ranks are ndarray")
        idx = np.argsort(r1)[::-1][:top_k]
        nodes_top = [nodes[i] for i in idx]
        v1 = r1[idx]
        v2 = _auto_to_vector(r2, nodes)[idx]

    x = np.arange(len(nodes_top))
    width = 0.35
    if ax is None:
        fig, ax = plt.subplots(figsize=(max(6, 0.4 * top_k), 4))
    else:
        fig = ax.figure

    ax.bar(x - width / 2, v1, width, label="Method‑1")
    ax.bar(x + width / 2, v2, width, label="Method‑2")
    ax.set_xticks(x)
    ax.set_xticklabels(nodes_top, rotation=45, ha="right")
    ax.set_ylabel("PageRank score")
    ax.set_title(f"Top {top_k} nodes – rank comparison")
    ax.legend()
    fig.tight_layout()

# ---------------------------------------------------------------------------
# Timing benchmark
# ---------------------------------------------------------------------------

def timing_benchmark(
    methods: Dict[str, Callable[..., Any]],
    M,
    *,
    b=None,
    repeat: int = 3,
) -> "pd.DataFrame | Dict[str, float]":
    """Measure average runtime for each solver.

    Parameters
    ----------
    methods : dict[str, callable]
        Mapping name → function that takes (M[, b]) and returns rank vector.
    M, b
        Inputs forwarded to each method.
    repeat : int, default 3
        Number of times to repeat timing and average.

    Returns
    -------
    pandas.DataFrame | dict
        Table with columns *method*, *avg_sec*, *std_sec*.  If pandas not
        installed, return a plain dict.
    """
    results: List[Dict[str, float]] = []
    for name, func in methods.items():
        times: List[float] = []
        for _ in range(repeat):
            t0 = time.perf_counter()
            if b is None:
                func(M)
            else:
                func(M, b)
            times.append(time.perf_counter() - t0)
        results.append({"method": name, "avg_sec": np.mean(times), "std_sec": np.std(times)})

    if pd is not None:
        return pd.DataFrame(results)
    else:
        return {row["method"]: row["avg_sec"] for row in results}
