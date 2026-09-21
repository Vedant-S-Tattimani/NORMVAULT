# Candidate Fusion & Ranking Strategy

## 1. Overview

NORMVAULT rejects opaque "black-box AI confidence scores." Instead, the retrieval engine employs an explainable, multi-stage ranking strategy combining lexical frequency statistics, dense vector geometry, Reciprocal Rank Fusion (RRF), and domain feature reranking.

---

## 2. Stage 1: Lexical Scoring (BM25Okapi)

The lexical search stream scores candidate standards using the Robertson-Spärck Jones BM25Okapi formulation:

$$IDF(q_i) = \ln\left( \frac{N - n(q_i) + 0.5}{n(q_i) + 0.5} + 1 \right)$$

$$Score_{BM25}(D, Q) = \sum_{q_i \in Q} IDF(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{avgdl}\right)}$$

Where:
- $k_1 = 1.5$ (term frequency saturation constant)
- $b = 0.75$ (document length normalization constant)
- Field boosting multipliers:
  - Standard number match: $4.0\times$
  - Title match: $3.0\times$
  - Scope match: $1.0\times$
  - Clause match: $1.0\times$

Scores are normalized relative to the top candidate:
$$S_{lex}(d) = \frac{Score_{BM25}(d)}{\max_{d'}(Score_{BM25}(d'))}$$

---

## 3. Stage 2: Dense Semantic Similarity

Dense semantic similarity measures conceptual orientation in vector space:
$$S_{sem}(d) = \cos(\theta) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\|_2 \|\mathbf{d}\|_2}$$

Where $\mathbf{q}$ is the query vector and $\mathbf{d}$ is the candidate standard's canonical vector. Similarities are bounded in $[0.0, 1.0]$.

---

## 4. Stage 3: Candidate Fusion (Reciprocal Rank Fusion)

Rather than directly adding scores with disparate distributions (BM25 is unbounded $[0, \infty)$, while cosine is $[-1, 1]$), NORMVAULT utilizes **Reciprocal Rank Fusion (RRF)**:

$$RRF\_Score(d) = \frac{w_{lex}}{k_{rrf} + R_{lex}(d)} + \frac{w_{sem}}{k_{rrf} + R_{sem}(d)}$$

Where:
- $k_{rrf} = 60$ (smoothing constant preventing high ranks from dominating)
- $w_{lex} = 0.5$, $w_{sem} = 0.5$ (configurable retrieval channel weights)
- If candidate $d$ is missing from channel $i$, its rank $R_i(d) \to \infty$ ($Contribution = 0$).

---

## 5. Stage 4: Deterministic Cross-Feature Reranker

The reranker refines the candidate pool using structural domain signals:

1. **Explicit BIS Citation Signal ($C_{cite}$)**:
   - Evaluates whether the requirement explicitly quotes the candidate standard number (e.g. tender specifies *"Pipes conforming to IS 4984"*).
   - If cited: $C_{cite} = 1.0$, providing an immediate $+0.35$ relevance floor.

2. **Title Jaccard Token Overlap ($J_{title}$)**:
   $$J_{title} = \frac{|Tokens(Q) \cap Tokens(Title)|}{|Tokens(Q) \cup Tokens(Title)|}$$

3. **Scope Concept Density ($D_{scope}$)**:
   $$D_{scope} = \min\left(\frac{|Tokens(Q) \cap Tokens(Scope)|}{\max(|Tokens(Q)|, 1)}, 1.0\right)$$

4. **Multi-Channel Agreement**:
   - Rewards candidates discovered strongly in both lexical and dense channels.

### Final Score Computation:
$$\text{Final Retrieval Score} = 0.45 \cdot S_{RRF}(d) + 0.55 \cdot S_{rerank}(d)$$

---

## 6. Configurable Top-K

The engine enforces safe top-k parameter bounds:
- Default: `top_k = 5`
- Minimum: `1`
- Maximum: `50`
- Safe truncation prevents memory or payload exhaustion while allowing comprehensive candidate discovery.
