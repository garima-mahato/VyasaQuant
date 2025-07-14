"""
Embeddings Schemas

Data structures for vector embeddings and similarity search results.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np


@dataclass
class EmbeddingVector:
    """Vector embedding with metadata"""
    id: str
    vector: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def dimension(self) -> int:
        """Get the dimension of the embedding vector"""
        return len(self.vector)
    
    @property
    def norm(self) -> float:
        """Calculate the L2 norm of the vector"""
        return float(np.linalg.norm(self.vector))
    
    def cosine_similarity(self, other: 'EmbeddingVector') -> float:
        """Calculate cosine similarity with another embedding"""
        if self.dimension != other.dimension:
            raise ValueError("Vectors must have the same dimension")
        
        dot_product = np.dot(self.vector, other.vector)
        norms = self.norm * other.norm
        
        if norms == 0:
            return 0.0
        
        return float(dot_product / norms)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "vector": self.vector,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "dimension": self.dimension,
            "norm": self.norm
        }


@dataclass
class SearchResult:
    """Single search result with similarity score"""
    id: str
    content: str
    metadata: Dict[str, Any]
    similarity_score: float
    distance: float
    rank: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "similarity_score": self.similarity_score,
            "distance": self.distance,
            "rank": self.rank
        }


@dataclass
class SearchResults:
    """Collection of search results"""
    query: str
    results: List[SearchResult] = field(default_factory=list)
    total_results: int = 0
    search_time: float = 0.0
    search_metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def top_result(self) -> Optional[SearchResult]:
        """Get the top-ranked result"""
        return self.results[0] if self.results else None
    
    @property
    def average_similarity(self) -> float:
        """Calculate average similarity score"""
        if not self.results:
            return 0.0
        
        total_similarity = sum(result.similarity_score for result in self.results)
        return total_similarity / len(self.results)
    
    def filter_by_similarity(self, min_similarity: float) -> 'SearchResults':
        """Filter results by minimum similarity score"""
        filtered_results = [
            result for result in self.results 
            if result.similarity_score >= min_similarity
        ]
        
        # Re-rank filtered results
        for i, result in enumerate(filtered_results):
            result.rank = i + 1
        
        return SearchResults(
            query=self.query,
            results=filtered_results,
            total_results=len(filtered_results),
            search_time=self.search_time,
            search_metadata={
                **self.search_metadata,
                "filtered_by_similarity": min_similarity,
                "original_count": len(self.results)
            }
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "results": [result.to_dict() for result in self.results],
            "total_results": self.total_results,
            "search_time": self.search_time,
            "search_metadata": self.search_metadata,
            "average_similarity": self.average_similarity
        }


@dataclass
class EmbeddingModel:
    """Information about an embedding model"""
    name: str
    provider: str
    dimension: int
    max_input_length: int
    model_version: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider,
            "dimension": self.dimension,
            "max_input_length": self.max_input_length,
            "model_version": self.model_version,
            "description": self.description
        }


# Common embedding models
EMBEDDING_MODELS = {
    "nomic-embed-text": EmbeddingModel(
        name="nomic-embed-text",
        provider="ollama",
        dimension=768,
        max_input_length=8192,
        description="Nomic text embedding model for semantic search"
    ),
    "text-embedding-ada-002": EmbeddingModel(
        name="text-embedding-ada-002",
        provider="openai",
        dimension=1536,
        max_input_length=8191,
        description="OpenAI's Ada embedding model"
    ),
    "models/embedding-001": EmbeddingModel(
        name="models/embedding-001",
        provider="google",
        dimension=768,
        max_input_length=2048,
        description="Google's PaLM embedding model"
    )
} 