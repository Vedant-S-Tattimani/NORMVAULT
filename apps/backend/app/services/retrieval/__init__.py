"""
Hybrid Standards Retrieval Engine services package.
"""

from app.services.retrieval.embeddings import (
    EmbeddingProvider,
    DeterministicMockEmbeddingProvider,
    get_embedding_provider,
    EmbeddingVersionMismatchError,
)
from app.services.retrieval.lexical import LexicalSearchEngine
from app.services.retrieval.query_builder import DeterministicQueryBuilder
from app.services.retrieval.metadata_filter import StandardsMetadataFilter
from app.services.retrieval.fusion import CandidateFusion, CandidateDraft
from app.services.retrieval.reranker import DeterministicFeatureReranker, RerankerProvider
from app.services.retrieval.indexer import StandardsIndexer
from app.services.retrieval.engine import HybridRetrievalEngine

__all__ = [
    "EmbeddingProvider",
    "DeterministicMockEmbeddingProvider",
    "get_embedding_provider",
    "EmbeddingVersionMismatchError",
    "LexicalSearchEngine",
    "DeterministicQueryBuilder",
    "StandardsMetadataFilter",
    "CandidateFusion",
    "CandidateDraft",
    "DeterministicFeatureReranker",
    "RerankerProvider",
    "StandardsIndexer",
    "HybridRetrievalEngine",
]
