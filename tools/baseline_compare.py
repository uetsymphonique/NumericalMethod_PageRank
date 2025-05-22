"""
baseline_compare.py
===================
Wrapper utilities around *networkx.pagerank* to form a baseline and compare
with custom PageRank solvers.

Public API
----------
- compute_networkx_pagerank(G, alpha=0.85, nodes=None)
    Return *dict* (**or** ordered vector + nodes list) with PageRank from
    NetworkX implementation.
- compare_ranks(r1, r2)
    Compute L¹ and L² norm difference between two PageRank vectors / dicts.
- print_top_k(r, nodes=None, k=5)
    Pretty‑print top‑k nodes with highest rank.

All helpers attempt to accept either *vector form* (np.ndarray) **or**
*dict* mapping node→score.

Author: uetsymphonique
"""
from __future__ import annotations

import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Sequence, Any

__all__ = [
    "compute_networkx_pagerank",
    "compare_ranks",
    "print_top_k",
]

# ---------------------------------------------------------------------------
# Helper type detection
# ---------------------------------------------------------------------------

def _dict_to_vector(d: Dict[Any, float], nodes: Sequence[Any]) -> np.ndarray:
    """Convert dict PageRank to vector ordered by *nodes* list."""
    return np.array([d.get(node, 0.0) for node in nodes], dtype=float)


def _auto_to_vector(r: "np.ndarray | Dict", nodes: Sequence[Any]) -> np.ndarray:
    if isinstance(r, dict):
        return _dict_to_vector(r, nodes)
    elif isinstance(r, np.ndarray):
        return r
    else:
        raise TypeError("Rank must be ndarray or dict")

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_networkx_pagerank(
    G: nx.DiGraph | nx.Graph,
    *,
    alpha: float = 0.85,
    nodes: Sequence[Any] | None = None,
) -> Tuple[np.ndarray | Dict[Any, float], List[Any]]:
    """Run NetworkX PageRank.

    If *nodes* provided, return **vector** aligned with this ordering and
    also return the list.  Otherwise return the dict from NetworkX & node list.
    """
    pr_dict = nx.pagerank(G, alpha=alpha)
    if nodes is None:
        nodes = list(pr_dict.keys())
    vec = _dict_to_vector(pr_dict, nodes)
    return vec, list(nodes)


def compare_ranks(r1, r2, *, nodes: Sequence[Any] | None = None) -> Tuple[float, float]:
    """Return (L1 error, L2 error) between two rank representations.

    *r1*, *r2* can be *dict* or *np.ndarray*.  If dict → require *nodes*
    ordering list to align.
    """
    if nodes is None and (isinstance(r1, dict) or isinstance(r2, dict)):
        raise ValueError("When either rank is dict, 'nodes' list is required to align")

    if nodes is None:
        # Both vectors
        v1 = np.asarray(r1, dtype=float)
        v2 = np.asarray(r2, dtype=float)
    else:
        v1 = _auto_to_vector(r1, nodes)
        v2 = _auto_to_vector(r2, nodes)

    l1 = np.linalg.norm(v1 - v2, ord=1)
    l2 = np.linalg.norm(v1 - v2, ord=2)
    return l1, l2


def print_top_k(r: "np.ndarray | Dict", *, nodes: Sequence[Any] | None = None, k: int = 5) -> None:
    """Display top‑k nodes and their PageRank scores.

    Accepts vector (with *nodes* list) or dict.
    """
    if isinstance(r, dict):
        pairs = sorted(r.items(), key=lambda x: x[1], reverse=True)[:k]
        for node, score in pairs:
            print(f"{node:>12}: {score:.6f}")
    else:
        if nodes is None:
            raise ValueError("nodes list required when r is ndarray")
        idx = np.argsort(r)[::-1][:k]
        for i in idx:
            print(f"{nodes[i]:>12}: {r[i]:.6f}")
