"""
graph_loader.py
===============
Utility functions for PageRank experiments.

This module provides helper routines to
  • build a small sample graph for quick testing
  • load a directed or undirected graph from a plain‑text edge‑list file

Each public function is documented with type hints so it can be imported
and unit‑tested independently.

Author: uetsymphonique
"""
from __future__ import annotations

import networkx as nx
from pathlib import Path
from typing import Union

__all__ = [
    "load_graph_from_edges",
    "create_sample_graph",
]

def load_graph_from_edges(
    file_path: Union[str, Path],
    *,
    directed: bool = True,
    delimiter: str | None = None,
    comments: str = "#",
    weighted: bool = False,
) -> nx.Graph:
    """Load a graph from an edge‑list text file.

    Each non‑empty, non‑comment line must contain at least two tokens:
    ``src dst [weight]``.  Additional columns beyond the optional weight
    are ignored.  Nodes are treated as strings.

    Parameters
    ----------
    file_path
        Path to edge‑list text file.
    directed
        When *True* (default) create :class:`networkx.DiGraph`, otherwise
        :class:`networkx.Graph`.
    delimiter
        Column delimiter.  *None* means *split on any whitespace*.
    comments
        Lines beginning with this prefix are skipped.
    weighted
        Interpret third column as *float* edge weight.

    Returns
    -------
    nx.Graph | nx.DiGraph
        Graph populated with edges from file.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Edge list file not found: {file_path}")

    G: nx.Graph = nx.DiGraph() if directed else nx.Graph()

    with path.open("r", encoding="utf‑8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith(comments):
                continue
            parts = line.split(delimiter)
            if len(parts) < 2:
                continue  # skip malformed line
            src, dst = parts[0].strip(), parts[1].strip()
            if weighted and len(parts) >= 3:
                try:
                    w = float(parts[2])
                except ValueError:
                    w = 1.0
                G.add_edge(src, dst, weight=w)
            else:
                G.add_edge(src, dst)

    return G

def create_sample_graph() -> nx.DiGraph:
    """Return a small *directed* test graph used in many PageRank demos.

    Graph structure::

        A → B, A → C
        B → C
        C → A
        D → C

    All edges are unweighted (implicit weight 1).
    """
    edges = [
        ("A", "B"),
        ("A", "C"),
        ("B", "C"),
        ("C", "A"),
        ("D", "C"),
    ]
    G = nx.DiGraph()
    G.add_edges_from(edges)
    return G


def _demo() -> None:
    """Quick CLI demo: ``python graph_loader.py --help`` for options."""
    import argparse, sys

    parser = argparse.ArgumentParser(description="Graph loader demo (PageRank project)")
    parser.add_argument("edge_file", nargs="?", help="Path to edge‑list file (optional)")
    parser.add_argument("--undirected", action="store_true", help="Treat graph as undirected")
    parser.add_argument("--weighted", action="store_true", help="Expect third column as weight")
    args = parser.parse_args()

    if args.edge_file:
        G = load_graph_from_edges(
            args.edge_file,
            directed=not args.undirected,
            weighted=args.weighted,
        )
    else:
        G = create_sample_graph()

    print(f"Loaded graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges\n")
    print("Nodes:", list(G.nodes))
    print("Edges:", list(G.edges(data=True)))


if __name__ == "__main__":
    _demo()
