import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from matplotlib.axes import Axes

def plot_residuals(residuals: List[float], title: Optional[str] = None) -> None:
    """
    Plot the convergence residuals on a semilog scale.
    
    Args:
        residuals: List of residual values
        title: Optional title for the plot
    """
    plt.figure(figsize=(10, 6))
    plt.semilogy(residuals, 'b-', label='Residual')
    plt.xlabel('Iteration')
    plt.ylabel('Residual (log scale)')
    if title:
        plt.title(title)
    plt.grid(True)
    plt.legend()

def plot_top_k_comparison(
    scores1: Dict[int, float],
    scores2: Dict[int, float],
    k: int = 10,
    title: Optional[str] = None
) -> None:
    """
    Plot comparison of top-k PageRank scores between two implementations.
    
    Args:
        scores1: First set of PageRank scores
        scores2: Second set of PageRank scores
        k: Number of top scores to compare
        title: Optional title for the plot
    """
    # Get top k nodes from both implementations
    top_k_1 = sorted(scores1.items(), key=lambda x: x[1], reverse=True)[:k]
    top_k_2 = sorted(scores2.items(), key=lambda x: x[1], reverse=True)[:k]
    
    # Create labels and values for plotting
    labels = [f"Node {node}" for node, _ in top_k_1]
    values1 = [score for _, score in top_k_1]
    values2 = [scores2[node] for node, _ in top_k_1]
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    x = np.arange(len(labels))
    width = 0.35
    
    plt.bar(x - width/2, values1, width, label='Custom')
    plt.bar(x + width/2, values2, width, label='NetworkX')
    
    plt.xlabel('Nodes')
    plt.ylabel('PageRank Score')
    if title:
        plt.title(title)
    plt.xticks(x, labels, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout() 