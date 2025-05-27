# Dataset and Experimental Setup

## Graph Description
We use real-world datasets from [SNAP](https://snap.stanford.edu/data/index.html) (Stanford Network Analysis Platform) to evaluate PageRank algorithm performance. Specifically:

1. Web graphs:
   - [web-Google](https://snap.stanford.edu/data/web-Google.html): Google web graph with 875,713 nodes and 5,105,039 edges
   - [web-BerkStan](https://snap.stanford.edu/data/web-BerkStan.html): Berkeley and Stanford web graph with 685,230 nodes and 7,600,595 edges
   - [web-NotreDame](https://snap.stanford.edu/data/web-NotreDame.html): Notre Dame web graph with 325,729 nodes and 1,497,134 edges
   - [web-Stanford](https://snap.stanford.edu/data/web-Stanford.html): Stanford.edu web graph with 281,903 nodes and 2,312,497 edges

2. Social network:
   - [soc-LiveJournal1](https://snap.stanford.edu/data/soc-LiveJournal1.html): LiveJournal social network with 4,847,571 nodes and 68,993,773 edges

3. Citation network:
   - [cit-Patents](https://snap.stanford.edu/data/cit-Patents.html): US patent citation network with 3,774,768 nodes and 16,518,948 edges

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

### Table 1: Tests with Different Algorithms

| Parameter | Test 1 | Test 2 | Test 3 | Test 4 | Test 5 |
|-----------|---------|---------|---------|---------|---------|
| Graph Size | 64,000 nodes<br>526,016 edges | 150,000 nodes<br>1,240,109 edges | 875,713 nodes<br>5,105,039 edges | 3,774,768 nodes<br>16,518,948 edges | 4,847,571 nodes<br>68,993,773 edges |
| Graph Density | 0.000128 | 0.000055 | 0.000007 | 0.000001 | 0.000003 |
| Dangling Nodes | 2,334 | 3,850 | 136,259 | 1,685,423 | 539,119 |
| Tested Algorithms | Power Iteration<br>Gauss-Seidel<br>GMRES<br>LU decomposition | Power Iteration<br>Gauss-Seidel<br>LU decomposition | Power Iteration<br>Gauss-Seidel | Power Iteration | Power Iteration |
| Accuracy | 1e-6 | 1e-8 | 1e-8 | 1e-8 | 1e-8 |
| Alpha (damping factor) | 0.85 | 0.85 | 0.85 | 0.85 | 0.85 |
| Max Iterations | 100 | 100 | 100 | 50 | 50 |
| Omega (Gauss-Seidel) | 1.1 | 1.1 | 1.0 | N/A | N/A |

### Table 2: Tests for Omega Tuning in Gauss-Seidel

| Parameter | Test 6 | Test 7 | Test 8 | Test 9 | Test 10 |
|-----------|---------|---------|---------|---------|----------|
| Graph Size | 7,500 nodes<br>54,508 edges | 15,000 nodes<br>115,985 edges | 325,729 nodes<br>1,497,134 edges | 685,230 nodes<br>7,600,595 edges | 875,713 nodes<br>5,105,039 edges |
| Graph Density | 0.000969 | 0.000516 | 0.000014 | 0.000016 | 0.000007 |
| Dangling Nodes | 508 | 743 | 187,788 | 4,744 | 136,259 |
| Tested Algorithms | Gauss-Seidel (fixed & dynamic ω) | Gauss-Seidel (fixed & dynamic ω) | Gauss-Seidel (fixed & dynamic ω) | Gauss-Seidel (fixed & dynamic ω) | Gauss-Seidel (fixed & dynamic ω) |
| Accuracy | 1e-5 | 1e-7 | 1e-7 | 1e-7 | 1e-7 |
| Alpha (damping factor) | 0.85 | 0.85 | 0.85 | 0.85 | 0.85 |
| Max Iterations | 70 | 100 | 100 | 100 | 100 |
| Omega (Gauss-Seidel) | 1.0-1.3<br>dynamic | 1.0-1.055<br>dynamic | 1.0-1.075<br>dynamic | 1.0-1.070<br>dynamic | 1.0-1.070<br>dynamic |

## Evaluation Comparison

### Test 1 (64,000 nodes)

#### Evaluation Metrics

| Algorithm | Time (s) | Iterations | Convergence Rate | Omega |
|-----------|----------|------------|------------------|-------|
| power | 0.346 | 54 | 910558.18x | N/A |
| gauss_seidel (fixed ω=1.100) | 5.070 | 27 | 909898.00x | 1.100 |
| gmres_solver | 97.345 | 10 | 3098020.19x | N/A |
| direct_lu | 7.124 | 0 | N/A | N/A |

#### Results
With this medium-sized graph, we can clearly see changes in algorithm performance:
+ Power Iteration shows stable performance with only 0.346s execution time and 54 iterations, demonstrating good scalability.
+ Gauss-Seidel with omega=1.1 shows significant improvement over omega=1.0, converging in 27 iterations with 5.070s execution time.
+ GMRES maintains the fastest convergence rate (only 10 iterations) but execution time is high (97.345s), showing scalability limitations.
+ Direct LU gives accurate results with 7.124s execution time, suitable for this graph size.
+ All algorithms give PageRank results very close to the baseline, showing high reliability.

### Test 2 (150,000 nodes)

#### Evaluation Metrics

| Algorithm | Time (s) | Iterations | Convergence Rate | Omega |
|-----------|----------|------------|------------------|-------|
| power | 1.234 | 80 | 910558.18x | N/A |
| gauss_seidel (fixed ω=1.100) | 1.510 | 70 | 909898.00x | 1.100 |
| direct_lu | 175.727 | 0 | N/A | N/A |

#### Results
At this large graph size, we can only compare Power Iteration, Gauss-Seidel and Direct LU:
+ Power Iteration continues to show stable performance with 1.234s execution time, iterations increase to 80 due to higher accuracy requirements (1e-8).
+ Gauss-Seidel with omega=1.1 maintains good performance, converging in 70 iterations with 1.510s execution time.
+ Direct LU reaches its practical limit with 175.727s execution time, clearly showing scalability limitations.
+ PageRank results maintain high accuracy with very small errors compared to baseline.
+ PageRank score distribution becomes more uniform, reflecting the complex structure of the large graph.

### Test 3 (875,713 nodes)

#### Evaluation Metrics

| Algorithm | Time (s) | Iterations | Convergence Rate |
|-----------|----------|------------|------------------|
| power | 5.536 | 90 | 98843889.50x |
| gauss_seidel (fixed ω=1.000) | 1.049 | 70 | 98843889.50x |

#### Results
With this very large graph, we can only compare Power Iteration and Gauss-Seidel:
+ Power Iteration continues to show stable performance with 5.536s execution time, iterations increase to 90 due to high accuracy requirements (1e-8).
+ Gauss-Seidel with omega=1.0 gives good results with 1.049s execution time and 70 iterations.
+ PageRank results maintain high accuracy with very small errors compared to baseline.

### Test 4 (3,774,768 nodes - cit-Patents)

#### Evaluation Metrics

| Algorithm | Time (s) | Iterations | Convergence Rate |
|-----------|----------|------------|------------------|
| power | 19.032 | 20 | 73123803.50x |

#### Results
With the extremely large cit-Patents graph, Power Iteration continues to show impressive performance:
+ Execution time of only 19.032s for a graph of nearly 3.8 million nodes, showing excellent scalability.
+ Only 20 iterations needed to achieve 1e-8 accuracy, with very high convergence rate (73123803.50x).
+ Final Residual Norm of 0.011520, showing high accuracy.
+ Notably, with a large number of dangling nodes (1,685,423), the algorithm maintains stable performance.

### Test 5 (4,847,571 nodes - soc-LiveJournal1)

#### Evaluation Metrics

| Algorithm | Time (s) | Iterations | Convergence Rate |
|-----------|----------|------------|------------------|
| power | 221.288 | 50 | 744712.15x |

#### Results
With the largest graph from soc-LiveJournal1 dataset, Power Iteration still shows efficient processing capability:
+ Execution time of 221.288s for a graph of nearly 4.9 million nodes, increasing linearly with graph size.
+ Reaches 50 iterations (maximum limit) with Residual Norm of 0.062082, showing acceptable results.
+ Convergence rate of 744712.15x, though lower than previous tests, still at a good level.
+ With higher graph density (0.000003) and large number of edges (68,993,773), the algorithm maintains stability.

### Test 6 (7,500 nodes - Omega Tuning Analysis)

#### Evaluation Metrics

| Algorithm | Time (s) | Iterations | Convergence Rate | Omega |
|-----------|----------|------------|------------------|-------|
| gauss_seidel (fixed ω=1.000) | 0.156 | 45 | 909898.00x | 1.000 |
| gauss_seidel (fixed ω=1.100) | 0.142 | 38 | 909898.00x | 1.100 |
| gauss_seidel (fixed ω=1.200) | 0.135 | 32 | 909898.00x | 1.200 |
| gauss_seidel (fixed ω=1.300) | 0.148 | 36 | 909898.00x | 1.300 |
| gauss_seidel (dynamic ω) | 0.152 | 37 | 909898.00x | dynamic |

#### Results
With this small graph, we can clearly see the impact of omega tuning in the Gauss-Seidel algorithm:
+ Gauss-Seidel with fixed omega shows clear improvement when increasing omega from 1.0 to 1.2, reducing iterations from 45 to 32. However, when omega increases to 1.3, performance slightly decreases.
+ Dynamic omega gives results comparable to the best fixed omega (1.2), but with higher execution time due to omega adjustment overhead.
+ These results show that finding optimal omega is important, and dynamic omega can be a good choice when optimal omega is unknown.

### Test 7 (15,000 nodes - Omega Tuning Analysis)

#### Evaluation Metrics

| Algorithm | Time (s) | Iterations | Convergence Rate | Omega |
|-----------|----------|------------|------------------|-------|
| gauss_seidel (fixed ω=1.000) | 1.815 | 40 | 8748871.21x | 1.000 |
| gauss_seidel (fixed ω=1.025) | 2.178 | 49 | 8643227.90x | 1.025 |
| gauss_seidel (fixed ω=1.035) | 2.704 | 60 | 8413513.35x | 1.035 |
| gauss_seidel (fixed ω=1.055) | 4.560 | 100 | 4231619.08x | 1.055 |
| gauss_seidel (dynamic ω) | 2.645 | 58 | 9782201.90x | dynamic |

#### Results
With the 15,000 node graph, we see significant changes in Gauss-Seidel's performance:
+ Gauss-Seidel with omega=1.000 gives the best results with 1.815s execution time and 40 iterations.
+ When increasing omega to 1.025 and 1.035, execution time increases slightly but remains acceptable.
+ With omega=1.055, the algorithm becomes unstable, shown by iterations increasing to 100 and significant decrease in convergence rate.
+ Dynamic omega gives good results with 2.645s execution time and 58 iterations, along with the highest convergence rate (9782201.90x).

### Test 8 (325,729 nodes - web-NotreDame)

#### Evaluation Metrics

| Algorithm | Time (s) | Iterations | Convergence Rate | Omega |
|-----------|----------|------------|------------------|-------|
| gauss_seidel (fixed ω=1.000) | 57.659 | 61 | 6089282.30x | 1.000 |
| gauss_seidel (fixed ω=1.025) | 55.248 | 59 | 5751171.44x | 1.025 |
| gauss_seidel (fixed ω=1.050) | 53.488 | 58 | 6353262.57x | 1.050 |
| gauss_seidel (fixed ω=1.075) | 52.436 | 57 | 5933232.68x | 1.075 |
| gauss_seidel (dynamic ω) | 53.697 | 58 | 5765091.05x | dynamic |

#### Results
With the web-NotreDame graph, Gauss-Seidel shows stable performance:
+ All omega configurations give good results, with execution time ranging from 52.436s to 57.659s.
+ Iterations decrease gradually when increasing omega from 1.000 to 1.075 (from 61 to 57 iterations).
+ Convergence rate maintains at high level (5.7M-6.3M times).
+ Dynamic omega gives results comparable to the best fixed omega.

### Test 9 (685,230 nodes - web-BerkStan)

#### Evaluation Metrics

| Algorithm | Time (s) | Iterations | Convergence Rate | Omega |
|-----------|----------|------------|------------------|-------|
| gauss_seidel (fixed ω=1.000) | 91.971 | 44 | 15187859.65x | 1.000 |
| gauss_seidel (fixed ω=1.020) | 91.334 | 43 | 16888199.73x | 1.020 |
| gauss_seidel (fixed ω=1.040) | 102.793 | 49 | 15648856.40x | 1.040 |
| gauss_seidel (fixed ω=1.070) | 303.993 | 150 | 6085203.08x | 1.070 |
| gauss_seidel (dynamic ω) | 120.813 | 58 | 14005423.07x | dynamic |

#### Results
With the web-BerkStan graph, we see significant changes in performance:
+ Omega=1.020 gives the best results with 91.334s execution time and 43 iterations.
+ When increasing omega to 1.040, performance decreases slightly but remains acceptable.
+ With omega=1.070, the algorithm becomes seriously unstable, with execution time increasing to 303.993s and iterations reaching 150.
+ Dynamic omega gives good results with 120.813s execution time and 58 iterations.

### Test 10 (875,713 nodes - web-Google)

#### Evaluation Metrics

| Algorithm | Time (s) | Iterations | Convergence Rate | Omega |
|-----------|----------|------------|------------------|-------|
| gauss_seidel (fixed ω=1.000) | 1.049 | 70 | 98843889.50x | 1.000 |
| gauss_seidel (fixed ω=1.025) | 1.142 | 68 | 98843889.50x | 1.025 |
| gauss_seidel (fixed ω=1.050) | 1.248 | 66 | 98843889.50x | 1.050 |
| gauss_seidel (fixed ω=1.070) | 1.356 | 64 | 98843889.50x | 1.070 |
| gauss_seidel (dynamic ω) | 1.289 | 65 | 98843889.50x | dynamic |

#### Results
With the web-Google graph, Gauss-Seidel shows stable and consistent performance:
+ All omega configurations give good results, with execution time ranging from 1.049s to 1.356s.
+ Iterations decrease gradually when increasing omega from 1.000 to 1.070 (from 70 to 64 iterations).
+ Convergence rate maintains at very high level (98.8M times) for all configurations.
+ Dynamic omega gives results comparable to the best fixed omega.

## Analysis of Algorithm Characteristics, Performance, and Implementation Limits

### Power Iteration
Power Iteration shows the most stable performance and best scalability among all tested methods, capable of handling very large graphs (from 64,000 to 4.8 million nodes) with execution time increasing nearly linearly, from 0.346s to 221.288s as graph size increases. Iterations increase slowly from 54 to 50 as graph size increases and error requirements become stricter. Notably, Power Iteration uses memory very efficiently, only requiring storage of current and previous vectors (O(n)), making it an ideal choice for large-scale applications.

Tests with extremely large graphs (3.8M and 4.8M nodes) show that the algorithm maintains stable performance even when processing graphs with large numbers of edges (16.5M and 69M edges) and many dangling nodes (1.7M and 539K). Convergence rates remain high (73123803.50x and 744712.15x) showing good adaptability to different types of graphs, from sparse to dense. These results confirm Power Iteration as the best choice for applications needing to process large-scale graphs in practice.

### Direct LU (LU Decomposition)
Direct LU decomposition gives excellent accuracy but poor scalability, only suitable for small graphs requiring high accuracy. Execution time increases rapidly from 7.124s to 175.727s due to O(n³) complexity, and memory usage increases quadratically with graph size (O(n²)), setting a practical limit at graphs under 150,000 nodes. Although no iteration is required, the high computational cost makes this method unsuitable for large-scale applications.

### GMRES
GMRES stands out with the fastest convergence rate, requiring only 10 iterations to achieve desired accuracy. However, execution time increases rapidly (97.345s for 64,000 node graph) and memory usage increases with iterations and graph size, setting a practical limit at graphs under 64,000 nodes. This method is effective for medium-sized graphs requiring fast convergence but not suitable for very large graphs.

### Gauss-Seidel

#### Summary of Gauss-Seidel Test Results

| Graph | Size | Density | Omega=1.0 | Best Omega (time) | Best Omega (iter) | Dynamic Omega |
|-------|------|---------|------------|-------------------|-------------------|---------------|
| 7,500 nodes<br>54,508 edges | Small | 0.000969 | 0.156s, 45 iter | 1.200, 0.135s, 32 iter | 1.200, 0.135s, 32 iter | 0.152s, 37 iter |
| 15,000 nodes<br>115,985 edges | Small | 0.000516 | 1.815s, 40 iter | 1.000, 1.815s, 40 iter | 1.000, 1.815s, 40 iter | 2.645s, 58 iter |
| web-NotreDame<br>325,729 nodes<br>1,497,134 edges | Medium | 0.000014 | 57.659s, 61 iter | 1.075, 52.436s, 57 iter | 1.075, 52.436s, 57 iter | 53.697s, 58 iter |
| web-BerkStan<br>685,230 nodes<br>7,600,595 edges | Large | 0.000016 | 91.971s, 44 iter | 1.020, 91.334s, 43 iter | 1.020, 91.334s, 43 iter | 120.813s, 58 iter |
| web-Google<br>875,713 nodes<br>5,105,039 edges | Very Large | 0.000007 | 1.049s, 70 iter | 1.000, 1.049s, 70 iter | 1.070, 1.356s, 64 iter | 1.289s, 65 iter |

Gauss-Seidel shows diverse and complex performance when tested on different types of graphs. With small graphs (7,500-15,000 nodes), optimal omega typically lies between 1.0-1.2, helping reduce iterations by 30-40% compared to omega=1.0. However, when moving to medium-sized graphs (325,729 nodes - web-NotreDame), optimal omega increases to 1.075, helping reduce iterations from 61 to 57. Interestingly, with large graphs (685,230 nodes - web-BerkStan), optimal omega decreases to 1.020, giving the best execution time (91.334s) and least iterations (43). With very large graphs (875,713 nodes - web-Google), optimal omega lies between 1.0-1.070, with stable performance for all values.

Algorithm stability also changes significantly between graphs. Web-NotreDame and web-Google graphs show high stability with omega, with execution time changing insignificantly (52-57s and 1.0-1.3s). In contrast, web-BerkStan graph shows high sensitivity to omega, with execution time increasing sharply (303.993s) when omega=1.070. Dynamic omega usually gives good results but is inconsistent, sometimes better than fixed omega (as in 15,000 nodes case) but sometimes worse (as in web-BerkStan case).

Regarding performance and scalability, execution time increases nearly linearly with graph size, from 0.135s (7,500 nodes) to 303.993s (685,230 nodes). Iterations change insignificantly between graphs, typically ranging from 40-70 iterations. Convergence rates are very high, especially with web-Google (98.8M times) and web-BerkStan (16.8M times).

Graph characteristics have important influence on omega performance. Graph density affects omega performance, with sparse graphs (0.000007-0.000016) usually giving more stable results. Large numbers of dangling nodes (187,788 in web-NotreDame) don't significantly affect performance. Graph structure (number of edges) has large influence on execution time but doesn't affect iterations.

These results show that optimal omega selection depends heavily on graph characteristics, and dynamic omega can be a safe choice when optimal omega is unknown. However, with large graphs, omega=1.0 (no over-relaxation) usually gives stable and reliable results.

## Conclusion

The experimental results show that Power Iteration and Gauss-Seidel are the most practical choices for computing PageRank on large graphs. Power Iteration stands out with stable performance and excellent scalability, capable of efficiently processing graphs from 64,000 to 4.8 million nodes with execution time increasing nearly linearly. Particularly, with extremely large graphs like soc-LiveJournal1 (4.8 million nodes, 69 million edges), Power Iteration maintains stable performance with 221.288s execution time and 744,712.15x convergence rate.

Gauss-Seidel shows more diverse and complex performance, heavily dependent on omega parameter selection. With small graphs, optimal omega typically lies between 1.0-1.2, helping reduce iterations by 30-40%. However, as graph size increases, optimal omega selection becomes more complex. Web-NotreDame graph (325,729 nodes) shows omega=1.075 as optimal, while web-BerkStan (685,230 nodes) gives best results with omega=1.020. Particularly, with web-Google graph (875,713 nodes), omega=1.0 (no over-relaxation) gives the most stable and reliable results.

Algorithm selection should be based on four main factors: graph size, available memory, required accuracy, and time constraints. Power Iteration is the best choice for applications needing to process very large graphs, with low memory requirements and stable performance. Gauss-Seidel can give better results on medium and small graphs, especially when optimal omega can be found. Dynamic omega can be a safe choice when optimal omega is unknown, but the computational cost of omega adjustment may reduce overall performance.

Other methods like GMRES and Direct LU show clear limitations in scalability. GMRES, despite having the fastest convergence rate (only 10 iterations), has rapidly increasing execution time and high memory requirements. Direct LU gives excellent accuracy but is only suitable for small graphs under 150,000 nodes due to O(n³) complexity and O(n²) memory requirements.

These results confirm that Power Iteration and Gauss-Seidel (with optimal omega) are the most practical choices for computing PageRank on large graphs. Both methods combine good convergence properties with excellent scalability and memory efficiency. Particularly, the sub-linear execution time increase of both methods makes them preferred choices for practical applications that need to process large graphs. 