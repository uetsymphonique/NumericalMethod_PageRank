"""
PageRank Implementation Package

This package provides various implementations of the PageRank algorithm,
including power iteration, Gauss-Seidel, GMRES, and direct LU methods.
"""

from .algorithms.power import pagerank as power_pagerank
from .algorithms.gauss_seidel import pagerank as gauss_seidel_pagerank
from .algorithms.direct_lu import pagerank as direct_lu_pagerank
from .algorithms.gmres_solver import pagerank as gmres_pagerank
from .algorithms.anderson_acceleration import pagerank as anderson_pagerank

__version__ = "0.1.0" 