"""
Core service abstractions and protocol definitions for NORMVAULT.
Defines clean seams and deep module contracts without premature implementation.
"""

from typing import Protocol, List, Dict, Any
from abc import abstractmethod


class DocumentParserProtocol(Protocol):
    """Parses tender documents (PDF/DOCX/TXT) into clean structured text and sections."""
    @abstractmethod
    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        ...


class RequirementExtractorProtocol(Protocol):
    """Extracts atomic technical clauses and quantitative parameters from procurement text."""
    @abstractmethod
    def extract(self, text: str) -> List[Dict[str, Any]]:
        ...


class StandardsRetrieverProtocol(Protocol):
    """Retrieves candidate standards using hybrid vector + lexical search."""
    @abstractmethod
    def retrieve(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        ...


class RecommendationEngineProtocol(Protocol):
    """Reranks candidates and generates explainable recommendations with evidence and gaps."""
    @abstractmethod
    def recommend(self, requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        ...
