import networkx as nx
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Set
from .logging_utils import get_logger

logger = get_logger(__name__)

def load_graph(path_txt: str | None = None, limit_nodes: int | None = None) -> nx.DiGraph:
    """
    Load a directed graph from a SNAP `web-Google.txt`‑style edge‑list.
    If `path_txt` is None or missing, fall back to Karate Club graph
    converted to a digraph for demo purposes.
    
    If limit_nodes is specified:
    - If positive: Keep the largest strongly connected component and limit to N nodes
    - If -1: Process the full graph
    - If None: Use the full graph
    """
    if path_txt and Path(path_txt).exists():
        G = nx.DiGraph()
        logger.info("Reading graph file using pandas...")
        
        # Read file in chunks for better memory efficiency
        chunk_size = 100000  # Adjust based on available memory
        for chunk in pd.read_csv(path_txt, 
                               sep='\s+',  # whitespace separator
                               comment='#',  # skip comment lines
                               header=None,  # no header
                               names=['source', 'target'],  # column names
                               dtype={'source': np.int32, 'target': np.int32},  # specify dtypes
                               chunksize=chunk_size):
            # Add edges from chunk to graph
            edges = list(zip(chunk['source'], chunk['target']))
            G.add_edges_from(edges)
        
        if limit_nodes and limit_nodes > 0:
            G = get_largest_component(G, limit_nodes)
        
        return G
    # fallback
    return nx.DiGraph(nx.karate_club_graph())

def get_largest_component(G: nx.DiGraph, limit_nodes: int) -> nx.DiGraph:
    """Get the largest strongly connected component and optionally limit its size"""
    logger.info("Finding largest strongly connected component...")
    largest_scc = max(nx.strongly_connected_components(G), key=len)
    G = G.subgraph(largest_scc).copy()
    
    # If still too many nodes, use BFS sampling
    if len(G) > limit_nodes:
        logger.info(f"Component too large ({len(G)} nodes), using BFS sampling...")
        G = bfs_sample(G, limit_nodes)
    
    logger.info(f"Selected component with {len(G)} nodes")
    logger.info(f"Number of dangling nodes: {sum(1 for n in G if G.out_degree(n) == 0)}")
    return G

def bfs_sample(G: nx.DiGraph, limit_nodes: int) -> nx.DiGraph:
    """Sample nodes using BFS from a random starting node"""
    start_node = list(G.nodes())[0]  # Start from first node
    bfs_nodes: Set[int] = set()
    for node in nx.bfs_tree(G, start_node).nodes():
        bfs_nodes.add(node)
        if len(bfs_nodes) >= limit_nodes:
            break
    return G.subgraph(bfs_nodes).copy() 