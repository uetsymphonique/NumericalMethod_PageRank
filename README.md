# PageRank Implementation

This project provides various implementations of the PageRank algorithm, including:
- Power Iteration
- Gauss-Seidel (with SOR acceleration)
- GMRES (with preconditioners)
- Direct LU (with sparse matrix support)

## Project Structure

```
NumericalMethod_PageRank/
├─ src/
│  └─ pagerank/              # Main package
│     ├─ __init__.py
│     ├─ cli.py              # Command line interface
│     ├─ logging_utils.py    # Logging configuration
│     ├─ graph_io.py         # Graph loading and processing
│     ├─ plotting.py         # Visualization utilities
│     └─ algorithms/         # PageRank implementations
│        ├─ __init__.py
│        ├─ power.py         # Power iteration
│        ├─ gauss_seidel.py  # Gauss-Seidel with SOR
│        ├─ gmres_solver.py  # GMRES with preconditioners
│        └─ direct_lu.py     # Direct LU decomposition
├─ tests/                    # Test suite
├─ README.md
├─ pyproject.toml           # Project configuration
└─ requirements.txt         # Development dependencies
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pagerank.git
cd pagerank

# Install in development mode
pip install -e .
```

## Usage

```bash
# Run with default settings (Power Iteration)
python -m pagerank.cli

# Run all algorithms for comparison
python -m pagerank.cli --algorithm all

# Run Gauss-Seidel with optimal omega
python -m pagerank.cli --algorithm gauss_seidel --auto-omega

# Run GMRES with ILU preconditioner
python -m pagerank.cli --algorithm gmres_solver --preconditioner ilu

# Run Direct LU with custom parameters
python -m pagerank.cli --algorithm direct_lu --permc-spec COLAMD --direct-drop-tol 1e-10

# Run with custom parameters
python -m pagerank.cli --graph web-Google.txt --limit 1000 --tolerance 1e-7 --alpha 0.8

# Run with full graph
python -m pagerank.cli --graph web-Google.txt --limit -1

# Run with debug logging
python -m pagerank.cli --log-level DEBUG
```

## Command Line Arguments

- `--graph`: Path to the graph file (default: web-Google.txt)
- `--limit`: Limit number of nodes to process (default: 1000, use -1 for full graph)
- `--log-level`: Set the logging level (default: INFO)
- `--tolerance`: Tolerance for convergence (default: 1e-6)
- `--alpha`: Damping factor for PageRank (default: 0.85)
- `--max-iter`: Maximum number of iterations (default: 100)
- `--algorithm`: PageRank algorithm(s) to use. Use comma-separated list (e.g. 'power,gauss_seidel') or 'all' for all algorithms

### Algorithm-specific Arguments

#### Gauss-Seidel
- `--omega`: SOR relaxation factor (default: 1.0)
- `--auto-omega`: Automatically find optimal omega

#### GMRES
- `--restart`: GMRES restart size (default: 30)
- `--preconditioner`: Preconditioner type (choices: ilu, jacobi, none, default: ilu)

#### Direct LU
- `--permc-spec`: Pivot strategy for sparse LU (choices: COLAMD, NATURAL, MMD_AT_PLUS_A, MMD_ATA, default: COLAMD)
- `--direct-drop-tol`: Drop tolerance for sparse LU (default: 1e-10)

## Output

The program generates several output files in a timestamped directory (`plots_YYYYMMDD_HHMMSS/`):

1. **Convergence Plot** (`convergence.png`):
   - Shows the convergence behavior of each algorithm
   - Plots residuals on a semilog scale
   - Useful for comparing convergence rates

2. **Top-10 Comparison** (`top10_comparison.png`):
   - Bar chart comparing top 10 PageRank scores
   - Includes NetworkX reference implementation
   - Shows relative performance of each algorithm

3. **Metrics Table** (`metrics_table.png` and `metrics.csv`):
   - Detailed comparison of algorithm performance
   - Includes execution time, L1 difference, iterations
   - Shows convergence metrics (initial/final residuals)

4. **Top Nodes Data** (`top_nodes.csv`):
   - Detailed data for top 10 nodes from each algorithm
   - Includes comparison with NetworkX scores
   - Shows absolute differences

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .
```

## License

MIT License 