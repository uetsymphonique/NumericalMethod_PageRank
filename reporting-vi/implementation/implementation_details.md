# Chi tiết cài đặt các thuật toán PageRank

## 1. Power Iteration

Power Iteration là phương pháp đơn giản nhất để tính PageRank. Thuật toán này sử dụng một hàm `pagerank` với các tham số cơ bản như đồ thị đầu vào G, hệ số damping alpha, ngưỡng hội tụ tol và số lần lặp tối đa max_iter.

Quá trình cài đặt bắt đầu bằng việc khởi tạo các tham số và tính toán các đặc trưng của đồ thị. Đầu tiên, chúng ta tính bậc ra của mỗi nút và xây dựng ma trận chuyển tiếp thưa dạng CSR. Vector xác suất ban đầu được khởi tạo với phân phối đều trên tất cả các nút.

Trong vòng lặp chính, thuật toán thực hiện các bước sau: tính toán vector xác suất mới, xử lý các nút dangling, kiểm tra điều kiện hội tụ và cập nhật vector xác suất. Việc xử lý nút dangling được thực hiện bằng cách tính tổng xác suất từ các nút này và phân phối đều cho tất cả các nút.

```python
def pagerank(G: nx.DiGraph, *, alpha: float = 0.85, tol: float = 1e-6, max_iter: int = 100):
    N = G.number_of_nodes()
    if N == 0:
        return {}, [], 0.0

    # Relabel nodes to 0..N‑1 for vectorised ops
    nodes = list(G.nodes())
    index = {n: i for i, n in enumerate(nodes)}
    out_deg = np.array([G.out_degree(n) for n in nodes], dtype=float)

    # Build sparse column‑stochastic matrix in CSR
    row_idx, col_idx, data = [], [], []
    for u, v in G.edges():
        row_idx.append(index[v])      # note: transpose for column‑stochastic
        col_idx.append(index[u])
        data.append(1.0 / out_deg[index[u]] if out_deg[index[u]] else 0.0)
    A = csr_matrix((data, (row_idx, col_idx)), shape=(N, N))

    # Uniform teleport & dangling distribution
    v = np.full(N, 1.0 / N)
    dangling = (out_deg == 0).astype(float)

    p = np.full(N, 1.0 / N)
    residuals = []

    for _ in range(max_iter):
        # p_new = α * (A @ p  + (dangling·p) * v) + (1‑α) * v
        dangling_mass = (dangling * p).sum()
        p_new = alpha * (A @ p + dangling_mass * v) + (1.0 - alpha) * v

        err = np.abs(p_new - p).sum()
        residuals.append(err)
        if err < tol:
            p = p_new
            break
        p = p_new

    # Normalise exactly
    p /= p.sum()
    
    return {n: p[index[n]] for n in nodes}, residuals, elapsed
```

## 2. Gauss-Seidel với SOR

Gauss-Seidel với SOR (Successive Over-Relaxation) là một cải tiến của phương pháp Gauss-Seidel cổ điển. Hàm `pagerank` được thiết kế với các tham số tương tự như Power Iteration, nhưng thêm vào đó là tham số omega để điều khiển quá trình over-relaxation.

Quá trình cài đặt bắt đầu với việc khởi tạo các tham số và tính toán các đặc trưng của đồ thị. Trong vòng lặp chính, thuật toán cập nhật tuần tự từng nút và áp dụng SOR cho mỗi cập nhật. Việc lựa chọn omega có thể được thực hiện theo ba chiến lược: fixed (giá trị cố định), auto (tự động tìm giá trị tối ưu) hoặc dynamic (điều chỉnh trong quá trình lặp).

```python
def pagerank(G: nx.DiGraph, *, alpha: float = 0.85, tol: float = 1e-6, max_iter: int = 100,
            omega: Union[float, Callable[[int, list[float]], float]] = 1.0):
    N = G.number_of_nodes()
    if N == 0:
        return {}, [], 0.0

    nodes = list(G)
    idx = {n: i for i, n in enumerate(nodes)}
    outdeg = np.fromiter((G.out_degree(n) for n in nodes), float, N)

    # sparse column-stochastic matrix
    rows, cols, data = [], [], []
    for u, v in G.edges():
        if outdeg[idx[u]]:
            rows.append(idx[v]); cols.append(idx[u])
            data.append(1.0 / outdeg[idx[u]])
    A = csr_matrix((data, (rows, cols)), shape=(N, N))

    v = np.full(N, 1.0 / N)
    dangling = (outdeg == 0).astype(float)

    p = v.copy()                # initialize uniform
    residual = []
    current_omega = omega if isinstance(omega, float) else 1.0  # Start with 1.0 if dynamic

    for iteration in range(max_iter):
        diff = 0.0
        d_mass = p[dangling.astype(bool)].sum()   # mass from dangling nodes
        
        # Update omega if it's a function
        if callable(omega):
            current_omega = omega(iteration, residual)
        
        for i in range(N):
            rank_new = (1 - alpha) * v[i]
            rank_new += alpha * d_mass * v[i]
            # ∑_{j→i} α * p_j / outdeg_j
            start, end = A.indptr[i], A.indptr[i + 1]
            rank_new += alpha * A.data[start:end] @ p[A.indices[start:end]]

            # apply SOR: xᵢ ← (1-ω)·xᵢ(old) + ω·rank_new
            rank_new = (1 - current_omega) * p[i] + current_omega * rank_new
            diff += abs(rank_new - p[i])
            p[i] = rank_new

        residual.append(diff)
        if diff < tol:
            break

    p /= p.sum()                 # normalize
    return {n: p[idx[n]] for n in nodes}, residual, elapsed
```

## 3. GMRES

GMRES (Generalized Minimal Residual) là một phương pháp Krylov subspace hiện đại. Hàm `pagerank` được thiết kế với các tham số bổ sung như restart (kích thước không gian con) và preconditioner (loại tiền xử lý).

Quá trình cài đặt bắt đầu với việc xây dựng LinearOperator và tạo preconditioner. Có ba loại preconditioner được hỗ trợ: ILU (Incomplete LU decomposition), Jacobi (Diagonal scaling) và None (không sử dụng preconditioner). Thuật toán sử dụng scipy.sparse.linalg.gmres để giải hệ phương trình.

```python
def pagerank(G: nx.DiGraph, *, alpha: float = 0.85, tol: float = 1e-6, max_iter: int = 100,
            restart: int = 30, preconditioner: str = "ilu"):
    if G.number_of_nodes() == 0:
        return {}, [], 0.0

    # Build LinearOperator
    A_op, b, dangling_mask, nodes, P = _build_linear_operator(G, alpha)

    # Build CSR matrix for preconditioner
    N = len(nodes)
    I = csr_matrix(np.eye(N))
    A_csr = I - alpha * P

    M = None
    if preconditioner != "none":
        M = _make_preconditioner(A_csr, preconditioner)

    res_history = []
    def callback(residual):
        """Callback function for GMRES"""
        if isinstance(residual, (int, float)):
            res_history.append(float(residual))
        else:
            res_history.append(float(np.linalg.norm(residual)))

    x, info = gmres(A_op, b, rtol=tol, restart=restart,
                    maxiter=max_iter, M=M, callback=callback,
                    callback_type='pr_norm')

    x = np.maximum(x, 0)
    x /= x.sum()
    
    return dict(zip(nodes, x)), res_history, elapsed
```

## 4. Direct LU

Direct LU là phương pháp trực tiếp sử dụng phân tích LU. Hàm `pagerank` được thiết kế với các tham số đặc biệt như permc_spec (chiến lược pivot) và drop_tol (ngưỡng drop).

Quá trình cài đặt bắt đầu với việc xây dựng ma trận hệ số và tạo vector vế phải. Tiếp theo, thuật toán thực hiện phân tích LU với pivot và áp dụng drop tolerance. Cuối cùng, hệ phương trình được giải bằng cách giải tuần tự hai hệ Ly = b và Ux = y, sau đó chuẩn hóa kết quả.

```python
def pagerank(G: nx.DiGraph, *, alpha: float = 0.85, tol: float = 1e-12,
            max_iter: int = 1, permc_spec: str = "COLAMD",
            drop_tol: float = 1e-10):
    if G.number_of_nodes() == 0:
        return {}, [], 0.0

    # 1. Build A (CSR) and vector b
    A = build_matrix(G, alpha)
    b = np.ones(G.number_of_nodes()) * (1 - alpha) / G.number_of_nodes()
    
    # 2. LU decomposition
    lu = splu(A.tocsc(), permc_spec=permc_spec,
              options={"ILU_MILU": "SMILU_2"})  # full pivoting
    
    # 3. Solve
    x = lu.solve(b)
    
    # 4. Normalize & statistics
    x = np.maximum(x, 0)
    x /= x.sum()
    
    return dict(zip(G.nodes(), x)), [], elapsed
```

## 5. Lưu ý 

Mỗi phương pháp có những ưu điểm và nhược điểm riêng, phù hợp với các tình huống khác nhau. Power Iteration nổi bật với tính đơn giản và hiệu quả bộ nhớ, trong khi Gauss-Seidel với SOR cung cấp tốc độ hội tụ nhanh hơn. GMRES đạt được tốc độ hội tụ nhanh nhất nhưng đòi hỏi bộ nhớ cao hơn, còn Direct LU cho độ chính xác cao nhất nhưng chỉ phù hợp với đồ thị nhỏ.


Khi cài đặt, cần lưu ý một số điểm quan trọng. Việc xử lý nút dangling cần được thực hiện cẩn thận trong Power Iteration và Gauss-Seidel, vì nó ảnh hưởng đến tốc độ hội tụ. Cấu trúc dữ liệu thưa nên được sử dụng để tối ưu bộ nhớ cho đồ thị lớn, với việc lựa chọn format lưu trữ phù hợp (CSR, CSC). Điều kiện hội tụ nên được chọn phù hợp với từng phương pháp: chuẩn L1 cho Power Iteration và Gauss-Seidel, chuẩn L2 cho GMRES.

Để tối ưu hiệu suất, nên sử dụng các thư viện tính toán vector như NumPy/SciPy, tận dụng tính thưa của ma trận và cân nhắc việc song song hóa khi có thể. Việc lựa chọn và tối ưu các tham số như alpha, omega, và preconditioner cũng đóng vai trò quan trọng trong hiệu suất tổng thể của thuật toán. 