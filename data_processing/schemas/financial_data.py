"""
Financial Data Schemas

Data structures for financial document processing results and extracted tables.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd


@dataclass
class FinancialTable:
    """
    Represents an extracted financial table from a document.
    """
    
    id: str
    title: str
    data: List[Dict[str, Any]]
    headers: List[str]
    row_count: int
    column_count: int
    table_type: str = "financial"  # financial, summary, footnote, etc.
    section: str = ""
    page_number: Optional[int] = None
    source_chunk_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate table data after initialization"""
        if not self.id:
            raise ValueError("Table ID cannot be empty")
        if not self.data:
            raise ValueError("Table data cannot be empty")
        if self.row_count != len(self.data):
            raise ValueError(f"Row count mismatch: expected {self.row_count}, got {len(self.data)}")
    
    @property
    def is_empty(self) -> bool:
        """Check if table has no data"""
        return len(self.data) == 0
    
    @property
    def size(self) -> tuple:
        """Get table dimensions as (rows, columns)"""
        return (self.row_count, self.column_count)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert table data to pandas DataFrame"""
        try:
            df = pd.DataFrame(self.data)
            if self.headers and len(self.headers) == len(df.columns):
                df.columns = self.headers
            return df
        except Exception as e:
            raise ValueError(f"Failed to convert table to DataFrame: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert table to dictionary representation"""
        return {
            "id": self.id,
            "title": self.title,
            "data": self.data,
            "headers": self.headers,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "table_type": self.table_type,
            "section": self.section,
            "page_number": self.page_number,
            "source_chunk_id": self.source_chunk_id,
            "metadata": self.metadata,
            "size": self.size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FinancialTable':
        """Create FinancialTable from dictionary"""
        table_fields = {
            "id": data["id"],
            "title": data["title"],
            "data": data["data"],
            "headers": data["headers"],
            "row_count": data["row_count"],
            "column_count": data["column_count"],
            "table_type": data.get("table_type", "financial"),
            "section": data.get("section", ""),
            "page_number": data.get("page_number"),
            "source_chunk_id": data.get("source_chunk_id"),
            "metadata": data.get("metadata", {})
        }
        return cls(**table_fields)
    
    def get_summary(self) -> str:
        """Get a summary of this table"""
        return f"Table {self.id}: {self.title} ({self.row_count}x{self.column_count}) from {self.section}"


@dataclass
class ProcessingResult:
    """
    Represents the result of document processing operation.
    """
    
    status: str  # success, error, partial
    document_path: str
    processing_strategy: str  # semantic, contents_based
    total_chunks: int = 0
    total_tables: int = 0
    chunks_summary: List[Dict[str, Any]] = field(default_factory=list)
    tables_summary: List[Dict[str, Any]] = field(default_factory=list)
    document_metadata: Dict[str, Any] = field(default_factory=dict)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: Optional[float] = None
    was_cached: bool = False
    reused_existing: bool = False
    
    def __post_init__(self):
        """Set processing timestamp if not provided"""
        if "processing_date" not in self.processing_metadata:
            self.processing_metadata["processing_date"] = datetime.now().isoformat()
    
    @property
    def is_successful(self) -> bool:
        """Check if processing was successful"""
        return self.status == "success"
    
    @property
    def has_errors(self) -> bool:
        """Check if there were any errors"""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there were any warnings"""
        return len(self.warnings) > 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate based on chunks processed"""
        if self.total_chunks == 0:
            return 0.0
        successful_chunks = len([c for c in self.chunks_summary if c.get("success", True)])
        return successful_chunks / self.total_chunks
    
    def add_error(self, error: str):
        """Add an error message"""
        self.errors.append(error)
        if self.status == "success":
            self.status = "partial" if self.total_chunks > 0 else "error"
    
    def add_warning(self, warning: str):
        """Add a warning message"""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation"""
        return {
            "status": self.status,
            "document_path": self.document_path,
            "processing_strategy": self.processing_strategy,
            "total_chunks": self.total_chunks,
            "total_tables": self.total_tables,
            "chunks_summary": self.chunks_summary,
            "tables_summary": self.tables_summary,
            "document_metadata": self.document_metadata,
            "processing_metadata": self.processing_metadata,
            "errors": self.errors,
            "warnings": self.warnings,
            "processing_time": self.processing_time,
            "was_cached": self.was_cached,
            "reused_existing": self.reused_existing,
            "is_successful": self.is_successful,
            "has_errors": self.has_errors,
            "has_warnings": self.has_warnings,
            "success_rate": self.success_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingResult':
        """Create ProcessingResult from dictionary"""
        result_fields = {
            "status": data["status"],
            "document_path": data["document_path"],
            "processing_strategy": data["processing_strategy"],
            "total_chunks": data.get("total_chunks", 0),
            "total_tables": data.get("total_tables", 0),
            "chunks_summary": data.get("chunks_summary", []),
            "tables_summary": data.get("tables_summary", []),
            "document_metadata": data.get("document_metadata", {}),
            "processing_metadata": data.get("processing_metadata", {}),
            "errors": data.get("errors", []),
            "warnings": data.get("warnings", []),
            "processing_time": data.get("processing_time"),
            "was_cached": data.get("was_cached", False),
            "reused_existing": data.get("reused_existing", False)
        }
        return cls(**result_fields)
    
    def get_summary(self) -> str:
        """Get a summary of the processing result"""
        status_emoji = "✅" if self.is_successful else "❌" if self.status == "error" else "⚠️"
        return f"{status_emoji} {self.status.title()}: {self.total_chunks} chunks, {self.total_tables} tables ({self.success_rate:.1%} success)" 