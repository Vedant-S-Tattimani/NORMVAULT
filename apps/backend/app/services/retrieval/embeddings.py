"""
Embedding provider abstraction and implementations for dense semantic retrieval.
Supports model versioning, metadata tracking, and dialect-independent vector storage.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import hashlib
import logging
import math
from typing import List, Optional
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingVersionMismatchError(Exception):
    """Raised when query embedding model or version does not match the active index."""
    pass


@dataclass(frozen=True)
class EmbeddingModelMetadata:
    model_name: str
    dimension: int
    version: str
    description: str


class EmbeddingProvider(ABC):
    """Abstract interface for dense semantic embedding generators."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding vector for a single text query."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a batch of documents."""
        pass

    @abstractmethod
    def get_model_metadata(self) -> EmbeddingModelMetadata:
        """Return version and dimension metadata of the active model."""
        pass


class DeterministicMockEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic, offline embedding provider for development, testing, and CI.
    Generates reproducible unit-normalized semantic projection vectors using token and
    sub-word hashing with TF-IDF style frequency weighting.
    
    Guarantees:
    - 100% reproducible across test runs
    - No external network or model download required
    - Unit L2 norm (sum of squares = 1.0)
    - Cosine similarity reflects vocabulary and concept overlap
    """

    def __init__(self, dimension: int = 128, version: str = "v1.0"):
        self.dimension = dimension
        self.version = version
        self.model_name = f"mock-deterministic-{dimension}d"

    def get_model_metadata(self) -> EmbeddingModelMetadata:
        return EmbeddingModelMetadata(
            model_name=self.model_name,
            dimension=self.dimension,
            version=self.version,
            description="Deterministic pseudo-semantic projection for offline verification and testing.",
        )

    def _hash_token(self, token: str) -> tuple[int, float]:
        """Compute bucket index and sign for a token."""
        h = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(h[:4], "big") % self.dimension
        sign = 1.0 if (h[4] % 2 == 0) else -1.0
        return idx, sign

    def embed_text(self, text: str) -> List[float]:
        clean = text.lower().strip()
        if not clean:
            vec = np.zeros(self.dimension, dtype=np.float32)
            # Safe non-zero unit vector for empty queries
            vec[0] = 1.0
            return vec.tolist()

        tokens = [t.strip(".,;:()[]{}\"'/\\-_") for t in clean.split() if len(t) > 1]
        if not tokens:
            vec = np.zeros(self.dimension, dtype=np.float32)
            vec[0] = 1.0
            return vec.tolist()

        # Build n-grams (unigrams + bigrams)
        ngrams = list(tokens)
        for i in range(len(tokens) - 1):
            ngrams.append(f"{tokens[i]}_{tokens[i+1]}")

        vec = np.zeros(self.dimension, dtype=np.float32)
        for token in ngrams:
            idx, sign = self._hash_token(token)
            # Give longer tokens slightly higher weight
            weight = 1.0 + min(len(token) * 0.1, 1.0)
            vec[idx] += sign * weight

        # L2 Normalize
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec = vec / norm
        else:
            vec[0] = 1.0

        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    """
    Local neural embedding provider using SentenceTransformers (e.g. all-MiniLM-L6-v2).
    Employed when local neural embedding generation is enabled in environment.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", version: str = "v1.0"):
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(model_name)
            self.model_name = model_name
            self.version = version
            self.dimension = self._model.get_sentence_embedding_dimension()
        except Exception as e:
            logger.warning(f"Failed to load sentence-transformers model '{model_name}': {e}. Falling back to mock.")
            raise

    def get_model_metadata(self) -> EmbeddingModelMetadata:
        return EmbeddingModelMetadata(
            model_name=self.model_name,
            dimension=self.dimension,
            version=self.version,
            description="Local neural dense semantic representation.",
        )

    def embed_text(self, text: str) -> List[float]:
        vec = self._model.encode(text, normalize_embeddings=True)
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        vecs = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [v.tolist() for v in vecs]


def get_embedding_provider(provider_type: Optional[str] = None) -> EmbeddingProvider:
    """
    Factory to instantiate configured embedding provider.
    Defaults to deterministic mock provider for predictable, reproducible local testing.
    """
    ptype = (provider_type or settings.EMBEDDING_PROVIDER or "mock").lower()

    if ptype in ("sentence-transformers", "neural"):
        try:
            return SentenceTransformerEmbeddingProvider()
        except Exception:
            logger.info("Falling back to DeterministicMockEmbeddingProvider.")
            return DeterministicMockEmbeddingProvider()
    
    # Default to deterministic mock
    return DeterministicMockEmbeddingProvider(dimension=128)
