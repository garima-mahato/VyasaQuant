"""
Document Chunk Schema

Data structure for representing semantically chunked document segments.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class DocumentChunk:
    """
    Represents a semantically chunked document segment.
    
    This class encapsulates a piece of document content along with its metadata,
    embedded tables, and optional vector embeddings for semantic search.
    """
    
    id: str
    content: str
    metadata: Dict[str, Any]
    tables: List[Dict[str, Any]]
    embeddings: Optional[List[float]] = None
    chunk_type: str = "text"  # text, table, mixed
    section: str = ""
    page_number: Optional[int] = None
    
    def __post_init__(self):
        """Validate chunk data after initialization"""
        if not self.id:
            raise ValueError("Chunk ID cannot be empty")
        if not self.content:
            raise ValueError("Chunk content cannot be empty")
        if self.chunk_type not in ["text", "table", "mixed"]:
            raise ValueError(f"Invalid chunk_type: {self.chunk_type}")
    
    @property
    def has_tables(self) -> bool:
        """Check if this chunk contains tables"""
        return len(self.tables) > 0
    
    @property
    def table_count(self) -> int:
        """Get the number of tables in this chunk"""
        return len(self.tables)
    
    @property
    def content_length(self) -> int:
        """Get the length of the content"""
        return len(self.content)
    
    @property
    def has_embeddings(self) -> bool:
        """Check if this chunk has embeddings"""
        return self.embeddings is not None and len(self.embeddings) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chunk to dictionary representation"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "tables": self.tables,
            "embeddings": self.embeddings,
            "chunk_type": self.chunk_type,
            "section": self.section,
            "page_number": self.page_number,
            "has_tables": self.has_tables,
            "table_count": self.table_count,
            "content_length": self.content_length
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentChunk':
        """Create DocumentChunk from dictionary"""
        # Extract only the fields that are part of the dataclass
        chunk_fields = {
            "id": data["id"],
            "content": data["content"],
            "metadata": data["metadata"],
            "tables": data["tables"],
            "embeddings": data.get("embeddings"),
            "chunk_type": data.get("chunk_type", "text"),
            "section": data.get("section", ""),
            "page_number": data.get("page_number")
        }
        return cls(**chunk_fields)
    
    def get_summary(self) -> str:
        """Get a summary of this chunk"""
        preview = self.content[:100] + "..." if len(self.content) > 100 else self.content
        return f"Chunk {self.id}: {preview} ({self.content_length} chars, {self.table_count} tables)" 