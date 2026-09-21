"""
Deterministic lexical retrieval engine based on BM25Okapi scoring.
Provides independent, transparent term frequency-inverse document frequency ranking
with token-level evidence tracking.
"""

from dataclasses import dataclass, field
import math
import re
from typing import List, Dict, Set, Optional, Any


STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "did", "do",
    "does", "doing", "don't", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its",
    "itself", "let's", "me", "more", "most", "my", "myself", "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shall", "she", "should", "so",
    "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
    "then", "there", "these", "they", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "we", "were", "what", "when", "where",
    "which", "while", "who", "whom", "why", "with", "would", "you", "your", "yours",
    "yourself", "yourselves", "shall", "must", "should", "as", "per", "grade"
}


def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text for lexical indexing and matching."""
    if not text:
        return []
    # Replace non-alphanumeric (except dashes in e.g. IS-123 or 3-phase) with space
    cleaned = re.sub(r"[^\w\s\-]", " ", text.lower())
    raw_tokens = cleaned.split()
    tokens = []
    for t in raw_tokens:
        t = t.strip("-")
        if len(t) > 1 and t not in STOPWORDS:
            tokens.append(t)
            # Expand hyphenated terms (e.g., 'three-phase' -> 'three', 'phase', 'three-phase')
            if "-" in t:
                parts = [p for p in t.split("-") if len(p) > 1 and p not in STOPWORDS]
                tokens.extend(parts)
    return tokens


@dataclass
class LexicalDocument:
    """A document indexed in the lexical search corpus."""
    standard_id: int
    standard_number: str
    title: str
    scope: str
    clauses_text: str = ""
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Pre-computed tokens
    tokens: List[str] = field(default_factory=list)
    title_tokens: Set[str] = field(default_factory=set)
    number_tokens: Set[str] = field(default_factory=set)


@dataclass
class LexicalSearchResult:
    """Individual result from a lexical search."""
    standard_id: int
    standard_number: str
    title: str
    bm25_score: float
    normalized_score: float
    matched_tokens: List[str]
    rank: int


class LexicalSearchEngine:
    """
    In-memory BM25Okapi lexical retrieval engine.
    Supports term-level importance, field boosting, and matched term extraction.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: List[LexicalDocument] = []
        self.doc_len: List[int] = []
        self.avgdl: float = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.corpus_size: int = 0

    def index_documents(self, docs: List[LexicalDocument]) -> None:
        """Build the inverted index and compute corpus-level statistics."""
        self.documents = []
        self.doc_len = []
        self.doc_freqs = {}
        self.idf = {}
        self.corpus_size = len(docs)

        if self.corpus_size == 0:
            self.avgdl = 0.0
            return

        total_length = 0
        for doc in docs:
            # Tokenize title and number separately for field-specific boosts
            t_tokens = tokenize(doc.title)
            n_tokens = tokenize(doc.standard_number)
            s_tokens = tokenize(doc.scope)
            c_tokens = tokenize(doc.clauses_text)

            # Combined weighted token stream:
            # Title tokens repeated 3x, number repeated 4x, scope repeated 1x, clauses 1x
            all_tokens = (n_tokens * 4) + (t_tokens * 3) + s_tokens + c_tokens
            
            doc.tokens = all_tokens
            doc.title_tokens = set(t_tokens)
            doc.number_tokens = set(n_tokens)
            
            self.documents.append(doc)
            d_len = len(all_tokens)
            self.doc_len.append(d_len)
            total_length += d_len

            # Document frequency
            unique_tokens = set(all_tokens)
            for token in unique_tokens:
                self.doc_freqs[token] = self.doc_freqs.get(token, 0) + 1

        self.avgdl = total_length / self.corpus_size

        # Compute Robertson-Spärck Jones IDF
        for token, df in self.doc_freqs.items():
            # Standard BM25 IDF formulation with smoothing
            self.idf[token] = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1.0)

    def search(self, query: str, top_k: int = 10) -> List[LexicalSearchResult]:
        """
        Execute BM25 search over the indexed corpus.
        Returns ranked candidates with normalized scores and matched tokens.
        """
        if self.corpus_size == 0:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores: List[float] = [0.0] * self.corpus_size
        matched_tokens_per_doc: List[Set[str]] = [set() for _ in range(self.corpus_size)]

        for q_token in query_tokens:
            if q_token not in self.idf:
                continue

            idf_val = self.idf[q_token]

            for idx, doc in enumerate(self.documents):
                # Count frequency in doc
                tf = doc.tokens.count(q_token)
                if tf > 0:
                    matched_tokens_per_doc[idx].add(q_token)
                    doc_length = self.doc_len[idx]
                    
                    # BM25 term score
                    numerator = tf * (self.k1 + 1.0)
                    denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_length / (self.avgdl or 1.0)))
                    term_score = idf_val * (numerator / denominator)

                    # Boost if term appears directly in standard number or title
                    if q_token in doc.number_tokens:
                        term_score *= 2.0
                    elif q_token in doc.title_tokens:
                        term_score *= 1.5

                    scores[idx] += term_score

        # Collect positive matches
        scored_docs = []
        max_score = max(scores) if scores else 0.0

        for idx, score in enumerate(scores):
            if score > 0.0:
                normalized = score / max_score if max_score > 0 else 0.0
                scored_docs.append((
                    score,
                    normalized,
                    self.documents[idx],
                    sorted(list(matched_tokens_per_doc[idx]))
                ))

        # Sort descending by raw BM25 score
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        results: List[LexicalSearchResult] = []
        for rank, (score, norm_score, doc, matched_terms) in enumerate(scored_docs[:top_k], start=1):
            results.append(LexicalSearchResult(
                standard_id=doc.standard_id,
                standard_number=doc.standard_number,
                title=doc.title,
                bm25_score=round(score, 4),
                normalized_score=round(norm_score, 4),
                matched_tokens=matched_terms,
                rank=rank
            ))

        return results
