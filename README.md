# PageRank Implementation

This project provides various implementations of the PageRank algorithm, including:
- Power Iteration (current)
- Gauss-Seidel (planned)
- GMRES (planned)
- Direct LU (planned)

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
│        ├─ gauss_seidel.py  # (planned)
│        ├─ gmres_solver.py  # (planned)
│        └─ direct_lu.py     # (planned)
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
# Run with default settings
python -m pagerank.cli

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
- `--algorithm`: PageRank algorithm to use (default: power)

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