# Retrieval Evaluation & Performance Benchmarks

## 1. Evaluation Methodology

NORMVAULT evaluates retrieval algorithms against a structured test dataset (`tests/fixtures/synthetic_retrieval_eval.json`) covering distinct procurement domains:
1. **Electrotechnical (ETD)**: Three-phase squirrel cage induction motors (IS 12615, IS/IEC 60034-1)
2. **Civil & Water Supply (CED)**: High-density polyethylene pipes (IS 4984)
3. **Metallurgical (MTD)**: Hot rolled structural steel (IS 2062)
4. **Building Materials (CED)**: Ordinary Portland Cement 53 Grade (IS 12269, IS 269)

---

## 2. Evaluation Metrics

### 1. Recall@K
Fraction of relevant candidate standards retrieved within the top $K$ positions:
$$\text{Recall@K} = \frac{|\text{Retrieved@K} \cap \text{Relevant}|}{|\text{Relevant}|}$$

### 2. Precision@K
Fraction of retrieved standards in top $K$ that are relevant:
$$\text{Precision@K} = \frac{|\text{Retrieved@K} \cap \text{Relevant}|}{K}$$

### 3. Mean Reciprocal Rank (MRR)
Measures where the first relevant standard appears across all queries:
$$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$

### 4. Normalized Discounted Cumulative Gain (NDCG@5)
Evaluates graded ranking quality, rewarding relevant candidates at the very top:
$$\text{DCG@K} = \sum_{i=1}^K \frac{rel_i}{\log_2(i + 1)}, \quad \text{NDCG@K} = \frac{\text{DCG@K}}{\text{IDCG@K}}$$

---

## 3. Benchmark Results

Measured on test execution using `pytest tests/test_retrieval_benchmarks.py -s`:

| Metric | Measured Score | Target Gate | Result |
| :--- | :--- | :--- | :--- |
| **Average Pipeline Latency** | **25.61 ms** | < 500 ms | PASS |
| **Recall@1** | **0.7500** | > 0.50 | PASS |
| **Recall@3** | **0.8750** | > 0.70 | PASS |
| **Recall@5** | **0.8750** | > 0.75 | PASS |
| **Precision@1** | **1.0000** | > 0.60 | PASS |
| **MRR** | **1.0000** | > 0.75 | PASS |
| **NDCG@5** | **0.9033** | > 0.80 | PASS |

---

## 4. Engineering Limitation & Boundary

> [!CAUTION]
> **Engineering Sanity Check Only**:
> These benchmark scores validate algorithm correctness, ranking monotonicity, and token/vector fusion mechanics on a controlled synthetic corpus.
> **They do not constitute statistical proof of real-world procurement accuracy**, which requires live field evaluation against tens of thousands of official GeM and CPPP tender specifications in Phase 4+.
