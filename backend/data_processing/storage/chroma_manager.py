"""
ChromaDB Manager

Handles vector storage and retrieval operations for document chunks and embeddings.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
import uuid

from ..schemas.document_chunk import DocumentChunk


class ChromaManager:
    """
    Manages ChromaDB operations for storing and retrieving document chunks
    with vector embeddings for semantic search.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize ChromaDB manager.
        
        Args:
            db_path: Path to ChromaDB persistent storage directory
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Setup ChromaDB path
        self.db_path = db_path or os.getenv("CHROMA_DB_PATH", "./chroma_db")
        Path(self.db_path).mkdir(exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Create or get collections
        self.chunks_collection = self.client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.tables_collection = self.client.get_or_create_collection(
            name="extracted_tables",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.processed_files_collection = self.client.get_or_create_collection(
            name="processed_files_metadata",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.logger.info(f"ChromaDB initialized at: {self.db_path}")
    
    def store_chunks(self, chunks: List[DocumentChunk], document_metadata: Dict[str, Any]) -> bool:
        """
        Store document chunks with embeddings in ChromaDB.
        
        Args:
            chunks: List of DocumentChunk objects with embeddings
            document_metadata: Metadata about the source document
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare data for ChromaDB
            chunk_ids = []
            chunk_documents = []
            chunk_embeddings = []
            chunk_metadatas = []
            
            for chunk in chunks:
                if not chunk.has_embeddings:
                    self.logger.warning(f"Chunk {chunk.id} has no embeddings, skipping")
                    continue
                
                chunk_ids.append(chunk.id)
                chunk_documents.append(chunk.content)
                chunk_embeddings.append(chunk.embeddings)
                
                # Combine chunk metadata with document metadata
                combined_metadata = {
                    **document_metadata,
                    "chunk_type": chunk.chunk_type,
                    "section": chunk.section,
                    "page_number": chunk.page_number,
                    "table_count": chunk.table_count,
                    "content_length": chunk.content_length,
                    **chunk.metadata
                }
                
                # ChromaDB metadata must be strings, numbers, or booleans
                sanitized_metadata = self._sanitize_metadata(combined_metadata)
                chunk_metadatas.append(sanitized_metadata)
            
            if chunk_ids:
                # Store in chunks collection
                self.chunks_collection.add(
                    ids=chunk_ids,
                    documents=chunk_documents,
                    embeddings=chunk_embeddings,
                    metadatas=chunk_metadatas
                )
                
                self.logger.info(f"Stored {len(chunk_ids)} chunks in ChromaDB")
                
                # Store tables separately if they exist
                self._store_tables(chunks, document_metadata)
                
                return True
            else:
                self.logger.warning("No chunks with embeddings to store")
                return False
                
        except Exception as e:
            self.logger.error(f"Error storing chunks in ChromaDB: {e}", exc_info=True)
            return False
    
    def _store_tables(self, chunks: List[DocumentChunk], document_metadata: Dict[str, Any]):
        """Store table data separately for better table-specific search."""
        try:
            table_ids = []
            table_documents = []
            table_embeddings = []
            table_metadatas = []
            
            for chunk in chunks:
                if chunk.has_tables and chunk.has_embeddings:
                    for i, table in enumerate(chunk.tables):
                        table_id = f"{chunk.id}_table_{i}"
                        table_content = self._format_table_content(table)
                        
                        table_ids.append(table_id)
                        table_documents.append(table_content)
                        table_embeddings.append(chunk.embeddings)  # Use chunk embeddings
                        
                        table_metadata = {
                            **document_metadata,
                            "source_chunk_id": chunk.id,
                            "table_index": i,
                            "table_type": table.get("type", "financial"),
                            "section": chunk.section,
                            "page_number": chunk.page_number,
                            **table.get("metadata", {})
                        }
                        
                        sanitized_metadata = self._sanitize_metadata(table_metadata)
                        table_metadatas.append(sanitized_metadata)
            
            if table_ids:
                self.tables_collection.add(
                    ids=table_ids,
                    documents=table_documents,
                    embeddings=table_embeddings,
                    metadatas=table_metadatas
                )
                
                self.logger.info(f"Stored {len(table_ids)} tables in ChromaDB")
                
        except Exception as e:
            self.logger.error(f"Error storing tables in ChromaDB: {e}", exc_info=True)
    
    def _format_table_content(self, table: Dict[str, Any]) -> str:
        """Format table data as searchable text content."""
        content_parts = []
        
        if "title" in table:
            content_parts.append(f"Table: {table['title']}")
        
        if "headers" in table:
            content_parts.append(f"Headers: {', '.join(table['headers'])}")
        
        if "data" in table:
            # Format first few rows as sample
            sample_rows = table["data"][:3]  # First 3 rows
            for row in sample_rows:
                if isinstance(row, dict):
                    row_text = ", ".join([f"{k}: {v}" for k, v in row.items()])
                    content_parts.append(row_text)
        
        return "\n".join(content_parts)
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata for ChromaDB storage (only str, int, float, bool allowed)."""
        sanitized = {}
        
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif value is None:
                sanitized[key] = ""
            elif isinstance(value, (list, dict)):
                sanitized[key] = str(value)
            else:
                sanitized[key] = str(value)
        
        return sanitized
    
    def search_chunks(self, query_embedding: List[float], n_results: int = 5, 
                     filter_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for similar chunks using vector similarity.
        
        Args:
            query_embedding: Query vector embedding
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            Dict containing search results
        """
        try:
            # Prepare query parameters
            query_params = {
                "query_embeddings": [query_embedding],
                "n_results": n_results
            }
            
            if filter_metadata:
                query_params["where"] = filter_metadata
            
            # Search chunks collection
            results = self.chunks_collection.query(**query_params)
            
            # Format results
            formatted_results = {
                "chunks": [],
                "total_results": len(results["ids"][0]) if results["ids"] else 0
            }
            
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    chunk_result = {
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i]
                    }
                    formatted_results["chunks"].append(chunk_result)
            
            self.logger.info(f"Found {formatted_results['total_results']} similar chunks")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error searching chunks: {e}", exc_info=True)
            return {"chunks": [], "total_results": 0}
    
    def search_tables(self, query_embedding: List[float], n_results: int = 5) -> Dict[str, Any]:
        """Search for similar tables using vector similarity."""
        try:
            results = self.tables_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            formatted_results = {
                "tables": [],
                "total_results": len(results["ids"][0]) if results["ids"] else 0
            }
            
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    table_result = {
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i]
                    }
                    formatted_results["tables"].append(table_result)
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error searching tables: {e}", exc_info=True)
            return {"tables": [], "total_results": 0}
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific chunk by ID."""
        try:
            results = self.chunks_collection.get(ids=[chunk_id])
            
            if results["ids"] and len(results["ids"]) > 0:
                return {
                    "id": results["ids"][0],
                    "content": results["documents"][0],
                    "metadata": results["metadatas"][0]
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving chunk {chunk_id}: {e}", exc_info=True)
            return None
    
    def mark_file_as_processed(self, file_path: str, strategy: str, 
                              processing_metadata: Dict[str, Any]):
        """Mark a file as processed with a specific strategy."""
        try:
            file_id = f"{Path(file_path).stem}_{strategy}"
            
            metadata = {
                "file_path": file_path,
                "strategy": strategy,
                "file_name": Path(file_path).name,
                **self._sanitize_metadata(processing_metadata)
            }
            
            # Use file path as document content for searchability
            self.processed_files_collection.upsert(
                ids=[file_id],
                documents=[file_path],
                metadatas=[metadata]
            )
            
            self.logger.info(f"Marked {file_path} as processed with {strategy} strategy")
            
        except Exception as e:
            self.logger.error(f"Error marking file as processed: {e}", exc_info=True)
    
    def is_file_processed(self, file_path: str, strategy: str) -> bool:
        """Check if a file has been processed with a specific strategy."""
        try:
            file_id = f"{Path(file_path).stem}_{strategy}"
            results = self.processed_files_collection.get(ids=[file_id])
            
            return len(results["ids"]) > 0
            
        except Exception as e:
            self.logger.error(f"Error checking file processing status: {e}", exc_info=True)
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about stored collections."""
        try:
            chunks_count = self.chunks_collection.count()
            tables_count = self.tables_collection.count()
            files_count = self.processed_files_collection.count()
            
            return {
                "chunks": chunks_count,
                "tables": tables_count, 
                "processed_files": files_count,
                "total_items": chunks_count + tables_count + files_count
            }
            
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {e}", exc_info=True)
            return {"chunks": 0, "tables": 0, "processed_files": 0, "total_items": 0} 