import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, List, Tuple, Optional
from matplotlib.axes import Axes
from matplotlib.table import Table

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

def plot_convergence_comparison(all_results: List[Dict], save_path: str) -> None:
    """
    Plot convergence comparison for multiple algorithms.
    
    Args:
        all_results: List of dictionaries containing algorithm results
        save_path: Path to save the plot
    """
    plt.figure(figsize=(12, 6))
    for result in all_results:
        if result['residuals']:  # Only plot if residuals exist
            plt.semilogy(result['residuals'], label=result['algorithm'].capitalize())
    plt.grid(True)
    plt.xlabel('Iteration')
    plt.ylabel('Residual (log scale)')
    plt.title('Convergence Comparison')
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.close()

def plot_top10_comparison(all_results: List[Dict], nx_scores: Dict[int, float], save_path: str) -> None:
    """
    Plot comparison of top 10 PageRank scores between multiple algorithms and NetworkX.
    
    Args:
        all_results: List of dictionaries containing algorithm results
        nx_scores: NetworkX PageRank scores
        save_path: Path to save the plot
    """
    plt.figure(figsize=(15, 6))
    x = np.arange(10)  # 10 nodes
    width = 0.8 / (len(all_results) + 1)  # +1 for NetworkX

    # Plot NetworkX
    top10_nx = sorted(nx_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    values_nx = [score for _, score in top10_nx]
    plt.bar(x, values_nx, width, label='NetworkX', alpha=0.5)

    # Plot other algorithms
    for i, result in enumerate(all_results):
        scores = result['scores']
        top10 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
        values = [score for _, score in top10]
        plt.bar(x + (i+1)*width, values, width, label=result['algorithm'].capitalize())

    plt.xlabel('Rank')
    plt.ylabel('PageRank Score')
    plt.title('Top-10 PageRank Scores Comparison')
    plt.xticks(x + width*len(all_results)/2, [f'#{i+1}' for i in range(10)])
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.close()

def create_table_image(df: pd.DataFrame, title: str, filename: str, figsize: Tuple[int, int] = (12, 8)) -> None:
    """
    Create and save a table visualization as an image.
    
    Args:
        df: DataFrame containing the data
        title: Title for the table
        filename: Path to save the image
        figsize: Figure size (width, height) in inches
    """
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

def save_metrics_comparison(metrics: pd.DataFrame, top_nodes_df: pd.DataFrame, plot_dir: str) -> None:
    """
    Save metrics comparison tables and CSV files.
    
    Args:
        metrics: DataFrame containing algorithm metrics
        top_nodes_df: DataFrame containing top nodes data
        plot_dir: Directory to save the files
    """
    # Save metrics to CSV file
    metrics.to_csv(f"{plot_dir}/metrics.csv", index=False)
    
    # Create and save metrics table image
    create_table_image(
        metrics,
        "Algorithm Comparison Metrics",
        f"{plot_dir}/metrics_table.png",
        figsize=(15, 8)
    )
    
    # Save top nodes to CSV file
    top_nodes_df.to_csv(f"{plot_dir}/top_nodes.csv", index=False)
    
    # # Create and save top nodes table image
    # # Transform data for better readability
    # top_nodes_pivot = top_nodes_df.pivot(
    #     index=['Algorithm', 'Rank'],
    #     columns=['Node', 'NetworkX Score'],
    #     values=['Score', 'Difference']
    # ).reset_index()
    
    # create_table_image(
    #     top_nodes_pivot,
    #     "Top 10 Nodes Comparison",
    #     f"{plot_dir}/top_nodes_table.png",
    #     figsize=(20, 12)
    # ) 