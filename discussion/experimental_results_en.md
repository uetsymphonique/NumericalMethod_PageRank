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

| Parameter | Test 1 | Test 2 | Test 3 | Test 4 |
|-----------|---------|---------|---------|---------|
| Graph Size | 4,900 nodes<br>37,993 edges | 64,000 nodes<br>526,016 edges | 150,000 nodes<br>1,240,109 edges | 875,713 nodes<br>5,105,039 edges |
| Graph Density | 0.001583 | 0.000128 | 0.000055 | 0.000007 |
| Dangling Nodes | 201 | 2,334 | 3,850 | 136,259 |
| Tested Algorithms | Power Iteration<br>Gauss-Seidel<br>GMRES<br>LU decomposition | Power Iteration<br>GMRES<br>LU decomposition | Power Iteration<br>LU decomposition | Power Iteration |
| Accuracy | 1e-6 | 1e-6 | 1e-8 | 1e-8 |
| Alpha (damping factor) | 0.85 | 0.85 | 0.85 | 0.85 |
| Max Iterations | 200 | 200 | 200 | 200 |

## Evaluation Comparison

### Test 1 (4,900 nodes)

#### Evaluation Metrics
![Evaluation Metrics](../4900_nodes_plots_20250524_012703/metrics_table.png)

#### Convergence Curve
![Convergence Curve](../4900_nodes_plots_20250524_012703/convergence.png)

#### Top 10 Nodes
![Top 10](../4900_nodes_plots_20250524_012703/top10_comparison.png)

#### Results
From the results of this small graph case, we can observe the following characteristics:
+ Both Power Iteration and GMRES show significantly better convergence rates than Gauss-Seidel, even though we added SOR to accelerate Gauss-Seidel.
+ Gauss-Seidel struggles to reach the desired error threshold (1e-6) and stops at the iteration limit (200). However, the PageRank values still approximate those from other algorithms and the baseline.
+ GMRES shows faster convergence but appears to have slower execution time than Power Iteration, which we will verify in larger graph cases.

### Test 2 (64,000 nodes)

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

### Test 3 (150,000 nodes)

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

### Test 4 (875,713 nodes)

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
+ Worst performance among all methods, included mainly to diversify the computational experiments, not suitable for practical applications.
+ Slow convergence rate, unable to achieve desired accuracy or requiring many iterations to reach acceptable accuracy.
+ Memory usage increases quadratically (O(n²)) due to storing the entire matrix.
+ Limited to very small graphs (< 5,000 nodes) due to high memory requirements.

## Conclusion

The experimental results show that Power Iteration is the most practical choice for computing PageRank on large graphs. It combines good convergence properties with excellent scalability and memory efficiency. While other methods may offer advantages in specific cases (such as Direct LU for small graphs or GMRES for medium-sized graphs), Power Iteration's ability to handle very large graphs while maintaining good performance makes it the preferred choice for practical applications.

Algorithm selection should be based on:
1. Graph size
2. Available memory
3. Required accuracy
4. Time constraints

For large-scale applications, Power Iteration stands out as the most practical choice due to:
- Consistent performance
- Good scaling behavior
- Memory efficiency
- Simple implementation
- Ability to handle very large graphs
- Excellent accuracy at large scale
- Sub-linear execution time increase 