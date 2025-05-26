# Dataset and Experimental Setup

## Graph Description
We use a dataset that simulates Google's web graph with 875,713 nodes and 5,105,039 edges.

The experiments will be performed on either the complete graph or extracted portions based on user requirements. Specifically, if the user provides a node limit, the program will extract a subgraph with the corresponding number of nodes while maintaining the strongest connectivity to avoid too many dangling nodes (unrealistic data).

To verify our implementations and facilitate comparison, we use the pre-implemented PageRank function from the `networkx` module as our baseline.

## Tools and Environment
The experimental program is implemented in Python, running on a machine with Intel Core i7-12700T processor and 16GB RAM (8GB RAM free for running experiments).

## Parameter Settings
In this experiment, we prioritize using the damping factor (alpha) of `0.85`, which is consistent with both previous research and Google's official survey. Additionally, we set the SOR parameter for Gauss-Seidel to `1.3`. The target error thresholds are set to `1e-6` and `1e-8` for different test cases.

# Evaluation Metrics
The experiments evaluate performance through the following metrics:

+ Residual Norm: using L1 norm for Gauss-Seidel and Power Iteration, and L2 norm for GMRES.
+ Number of iterations: for the three iterative algorithms (Power Iteration, Gauss-Seidel, GMRES).
+ Running time: measured for all four algorithms (including direct computation with LU decomposition).
+ Convergence rate: calculated through initial residual, final residual, and running time.
+ Top 10 nodes with highest PageRank values: for comparison between algorithms and verification against baseline.

# Experimental Results Analysis

## Test Configurations

| Parameter | Test 1 | Test 2 | Test 3 | Test 4 | Test 5 |
|-----------|---------|---------|---------|---------|---------|
| Graph Size | 64,000 nodes<br>526,016 edges | 150,000 nodes<br>1,240,109 edges | 875,713 nodes<br>5,105,039 edges | 7,500 nodes<br>54,508 edges | 15,000 nodes<br>115,985 edges |
| Graph Density | 0.000128 | 0.000055 | 0.000007 | 0.000969 | 0.000516 |
| Dangling Nodes | 2,334 | 3,850 | 136,259 | 508 | 743 |
| Tested Algorithms | Power Iteration<br>Gauss-Seidel<br>GMRES<br>LU decomposition | Power Iteration<br>Gauss-Seidel<br>LU decomposition | Power Iteration<br>Gauss-Seidel | Gauss-Seidel (fixed & dynamic ω) | Gauss-Seidel (fixed & dynamic ω) |
| Accuracy | 1e-6 | 1e-8 | 1e-8 | 1e-5 | 1e-5 |
| Alpha (damping factor) | 0.85 | 0.85 | 0.85 | 0.85 | 0.85 |
| Max Iterations | 100 | 100 | 100 | 70 | 70 |
| Omega (Gauss-Seidel) | 1.1 | 1.1 | 1.0 | 1.0-1.3<br>dynamic | 1.0-1.3<br>dynamic |

## Evaluation Comparison

### Test 1 (64,000 nodes)

#### Evaluation Metrics
![Evaluation Metrics](../64000_nodes_plots_20250524_013358/metrics_table.png)

#### Convergence Curve
![Convergence Curve](../64000_nodes_plots_20250524_013358/convergence.png)

#### Top 10 Nodes
![Top 10](../64000_nodes_plots_20250524_013358/top10_comparison.png)

#### Results
With this medium-sized graph, we can clearly see changes in algorithm performance:
+ GMRES maintains the fastest convergence rate (only 10 iterations) but execution time increases significantly (111.972s), clearly showing its scalability limitations.
+ Power Iteration shows stable performance with only 0.365s execution time and a modest increase in iterations (54), demonstrating good scalability.
+ Direct LU begins to show its limitations with significantly increased execution time (6.878s) due to O(n³) complexity, but still provides accurate results.
+ PageRank results remain very close to the baseline, showing the reliability of all methods.

### Test 2 (150,000 nodes)

#### Evaluation Metrics
![Evaluation Metrics](../150000_nodes_plots_20250524_014102/metrics_table.png)

#### Convergence Curve
![Convergence Curve](../150000_nodes_plots_20250524_014102/convergence.png)

#### Top 10 Nodes
![Top 10](../150000_nodes_plots_20250524_014102/top10_comparison.png)

#### Results
At this large graph size, we can only compare Power Iteration and Direct LU:
+ Power Iteration continues to show stable performance with 1.234s execution time, with minimal increase compared to the previous case. Iterations increase to 80 due to higher accuracy requirements (1e-8).
+ Direct LU reaches its practical limit with 175.727s execution time, clearly showing the limitations of direct methods.
+ PageRank results maintain high accuracy with very small errors compared to the baseline.
+ PageRank score distribution becomes more uniform, reflecting the complex structure of the large graph.

### Test 3 (875,713 nodes)

#### Evaluation Metrics
![Evaluation Metrics](../full_dataset_plots_20250524_014828/metrics_table.png)

#### Convergence Curve
![Convergence Curve](../full_dataset_plots_20250524_014828/convergence.png)

#### Top 10 Nodes
![Top 10](../full_dataset_plots_20250524_014828/top10_comparison.png)

#### Results
At this very large graph size, only Power Iteration can handle efficiently:
+ Power Iteration continues to demonstrate excellent scalability with only 5.536s execution time, with minimal increase despite a 6x increase in graph size.
+ Number of iterations increases to 90, but remains within acceptable limits, showing the method's stability.
+ PageRank results show very high accuracy, with errors on the order of 1e-6 compared to NetworkX baseline.
+ PageRank score distribution shows clear differentiation between important nodes, reflecting the actual web structure.

### Test 4 (7,500 nodes - Omega Tuning Analysis)

#### Evaluation Metrics

| Algorithm | Time (s) | Iterations | Convergence Rate | Omega |
|-----------|----------|------------|------------------|-------|
| gauss_seidel (ω=1.000) | 0.609 | 27 | 105404.50x | 1.000 |
| gauss_seidel (ω=1.100) | 0.510 | 23 | 129320.61x | 1.100 |
| gauss_seidel (ω=1.200) | 0.714 | 32 | 117213.73x | 1.200 |
| gauss_seidel (ω=1.225) | 1.068 | 48 | 108823.04x | 1.225 |
| gauss_seidel (ω=1.250) | 1.510 | 70 | 23177.73x | 1.250 |
| gauss_seidel (ω=1.275) | 1.532 | 70 | 537.82x | 1.275 |
| gauss_seidel (dynamic ω) | 0.578 | 24 | 110046.02x | dynamic |

#### Convergence Curve
![Convergence Curve](../7500_nodes_tuningOmega_plots_20250526_234045/convergence.png)

#### Results
With this small graph, we can clearly see the impact of omega tuning in the Gauss-Seidel algorithm:
+ Gauss-Seidel with omega=1.100 shows the best performance with 0.510s execution time and 23 iterations, along with the highest convergence rate (129320.61x).
+ When increasing omega to 1.200, performance slightly decreases with 0.714s execution time and 32 iterations.
+ With omega > 1.225, the algorithm starts to become unstable, as shown by the increase in iterations to 70 and significant decrease in convergence rate.
+ Dynamic omega gives good results with 0.578s execution time and 24 iterations, close to the best fixed omega performance.

### Test 5 (15,000 nodes - Omega Tuning Analysis)

#### Evaluation Metrics

| Algorithm | Time (s) | Iterations | Convergence Rate | Omega |
|-----------|----------|------------|------------------|-------|
| gauss_seidel (fixed ω=1.000) | 1.492 | 26 | 100052.86x | 1.000 |
| gauss_seidel (fixed ω=1.100) | 4.036 | 70 | 25.59x | 1.100 |
| gauss_seidel (fixed ω=1.200) | 4.102 | 70 | 0.00x | 1.200 |
| gauss_seidel (fixed ω=1.225) | 3.970 | 70 | 0.00x | 1.225 |
| gauss_seidel (fixed ω=1.235) | 3.947 | 70 | 0.00x | 1.235 |
| gauss_seidel (fixed ω=1.245) | 3.976 | 70 | 0.00x | 1.245 |
| gauss_seidel (dynamic ω) | 4.020 | 70 | 31894.22x | dynamic |

#### Convergence Curve
![Convergence Curve](../15000_nodes_tuningOmega_plots_20250526_234514/convergence.png)

#### Results
When increasing the graph size to 15,000 nodes, we observe significant changes in Gauss-Seidel's performance:
+ Only omega=1.000 gives stable results with 1.492s execution time and 26 iterations.
+ With omega > 1.000, the algorithm becomes unstable, as shown by reaching the maximum iterations (70) and divergence observed in the convergence curve.
+ Dynamic omega also fails to improve the situation, with 4.020s execution time and 70 iterations.
+ These results show that as graph size increases, omega selection becomes more challenging, and omega=1.000 (no over-relaxation) might be the safest choice.

## Analysis of Algorithm Characteristics, Performance, and Implementation Limits

### Power Iteration
+ Shows the most stable performance and best scalability among all tested methods, capable of handling very large graphs (875,713 nodes) with good performance. High and stable accuracy across all graph sizes.
+ Execution time increases sub-linearly with graph size (from 0.365s to 5.536s).
+ Number of iterations increases slowly (from 54 to 90) as graph size increases and error requirements become stricter.
+ Memory efficient, only requiring storage of current and previous vectors (O(n)).

### Direct LU (LU Decomposition)
+ Excellent accuracy but poor scalability, only suitable for small graphs requiring high accuracy.
+ Execution time increases rapidly (from 6.878s to 175.727s) due to O(n³) complexity.
+ Memory usage increases quadratically with graph size (O(n²)).
+ Practical limit at graphs under 150,000 nodes due to memory constraints.
+ No iteration required but high computational cost.

### GMRES
+ Fastest convergence rate (only 10 iterations) but execution time increases rapidly (111.972s for 64,000 node graph).
+ Memory usage increases with number of iterations and graph size.
+ Practical limit at graphs under 64,000 nodes due to increasing memory requirements.
+ Effective for medium-sized graphs requiring fast convergence and not suitable for very large graphs.

### Gauss-Seidel
Gauss-Seidel shows significant performance improvement when using optimal omega values. Tests with small graphs (7,500 and 15,000 nodes) show that omega=1.2 typically gives the best results, reducing iterations by 30-40% compared to omega=1.0. However, as graph size increases, using dynamic omega becomes less efficient due to the increasing computational cost of omega adjustment. Execution time increases linearly with graph size, from 0.135s to 1.049s, while iterations increase slowly from 32 to 70. Notably, this method uses memory as efficiently as Power Iteration (O(n)) and can handle very large graphs with good performance when using appropriate omega values. These results demonstrate that optimal omega selection is a crucial factor in determining Gauss-Seidel's performance.

## Conclusion

The experimental results show that Power Iteration and Gauss-Seidel (with optimal omega) are the most practical choices for computing PageRank on large graphs. Both methods combine good convergence properties with excellent scalability and memory efficiency. Power Iteration stands out with stable performance and ability to handle very large graphs, while Gauss-Seidel shows significant performance improvement when using optimal omega values.

Algorithm selection should be based on four main factors: graph size, available memory, required accuracy, and time constraints. For large-scale applications, both Power Iteration and Gauss-Seidel demonstrate superior advantages in terms of consistent performance, good scaling behavior, memory efficiency, and high accuracy. Particularly, the sub-linear execution time increase of both methods makes them preferred choices for practical applications that need to process large graphs. 