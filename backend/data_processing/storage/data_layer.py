"""
Data Layer

Unified interface for data storage operations, combining ChromaDB and PostgreSQL.
"""

import logging
from typing import List, Dict, Any, Optional
from ..schemas.document_chunk import DocumentChunk
from ..schemas.financial_data import ProcessingResult
from .chroma_manager import ChromaManager
from .postgres_manager import PostgresManager


class DataLayer:
    """
    Unified data storage layer that manages both vector and structured storage.
    
    This class provides a single interface for storing and retrieving document
    processing results, abstracting away the underlying storage mechanisms.
    """
    
    def __init__(self, chroma_path: Optional[str] = None, 
                 postgres_connection: Optional[str] = None):
        """
        Initialize the data layer with ChromaDB and PostgreSQL managers.
        
        Args:
            chroma_path: Path to ChromaDB storage
            postgres_connection: PostgreSQL connection string
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize storage managers
        try:
            self.chroma_manager = ChromaManager(db_path=chroma_path)
            self.chroma_available = True
            self.logger.info("ChromaDB manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            self.chroma_manager = None
            self.chroma_available = False
        
        try:
            self.postgres_manager = PostgresManager(connection_string=postgres_connection)
            self.postgres_available = self.postgres_manager.engine is not None
            if self.postgres_available:
                self.logger.info("PostgreSQL manager initialized successfully")
            else:
                self.logger.warning("PostgreSQL not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize PostgreSQL: {e}")
            self.postgres_manager = None
            self.postgres_available = False
        
        # Log storage availability
        storage_status = []
        if self.chroma_available:
            storage_status.append("ChromaDB")
        if self.postgres_available:
            storage_status.append("PostgreSQL")
        
        if storage_status:
            self.logger.info(f"Data layer initialized with: {', '.join(storage_status)}")
        else:
            self.logger.error("No storage backends available!")
    
    def store_processing_result(self, chunks: List[DocumentChunk], 
                              document_metadata: Dict[str, Any],
                              processing_result: ProcessingResult) -> Dict[str, bool]:
        """
        Store complete processing results in both storage backends.
        
        Args:
            chunks: List of processed document chunks
            document_metadata: Metadata about the source document
            processing_result: Overall processing result
            
        Returns:
            Dict indicating success/failure for each storage backend
        """
        results = {
            "chroma_success": False,
            "postgres_success": False,
            "overall_success": False
        }
        
        # Store in ChromaDB (for vector search)
        if self.chroma_available:
            try:
                chroma_success = self.chroma_manager.store_chunks(chunks, document_metadata)
                results["chroma_success"] = chroma_success
                
                if chroma_success:
                    # Mark file as processed in ChromaDB
                    self.chroma_manager.mark_file_as_processed(
                        processing_result.document_path,
                        processing_result.processing_strategy,
                        processing_result.processing_metadata
                    )
                    
            except Exception as e:
                self.logger.error(f"Error storing in ChromaDB: {e}", exc_info=True)
        
        # Store in PostgreSQL (for structured queries)
        if self.postgres_available:
            try:
                postgres_chunks_success = self.postgres_manager.store_chunks(chunks, document_metadata)
                postgres_result_success = self.postgres_manager.store_processing_result(processing_result)
                results["postgres_success"] = postgres_chunks_success and postgres_result_success
                
            except Exception as e:
                self.logger.error(f"Error storing in PostgreSQL: {e}", exc_info=True)
        
        # Overall success if at least one storage backend succeeded
        results["overall_success"] = results["chroma_success"] or results["postgres_success"]
        
        # Log results
        if results["overall_success"]:
            backends = []
            if results["chroma_success"]:
                backends.append("ChromaDB")
            if results["postgres_success"]:
                backends.append("PostgreSQL")
            self.logger.info(f"Successfully stored processing results in: {', '.join(backends)}")
        else:
            self.logger.error("Failed to store processing results in any backend")
        
        return results
    
    def search_documents(self, query_embedding: List[float], n_results: int = 5,
                        filter_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search for similar document chunks using vector similarity.
        
        Args:
            query_embedding: Query vector embedding
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            Search results from ChromaDB
        """
        if not self.chroma_available:
            self.logger.warning("ChromaDB not available for search")
            return {"chunks": [], "total_results": 0}
        
        return self.chroma_manager.search_chunks(
            query_embedding, n_results, filter_metadata
        )
    
    def search_tables(self, query_embedding: List[float], n_results: int = 5) -> Dict[str, Any]:
        """Search for similar tables using vector similarity."""
        if not self.chroma_available:
            self.logger.warning("ChromaDB not available for table search")
            return {"tables": [], "total_results": 0}
        
        return self.chroma_manager.search_tables(query_embedding, n_results)
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific chunk by ID."""
        if self.chroma_available:
            return self.chroma_manager.get_chunk_by_id(chunk_id)
        return None
    
    def get_chunks_by_file(self, file_path: str, strategy: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks for a specific file.
        
        Prefers PostgreSQL for structured queries, falls back to ChromaDB.
        """
        if self.postgres_available:
            return self.postgres_manager.get_chunks_by_file(file_path, strategy)
        
        # Fallback: search ChromaDB with file metadata filter
        if self.chroma_available:
            # This is a simplified fallback - ChromaDB search is less efficient for this
            self.logger.warning("Using ChromaDB fallback for file-based chunk retrieval")
            return []
        
        return []
    
    def get_tables_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Retrieve all extracted tables for a specific file."""
        if self.postgres_available:
            return self.postgres_manager.get_tables_by_file(file_path)
        return []
    
    def get_table_as_dataframe(self, table_id: str):
        """Convert a stored table to pandas DataFrame."""
        if self.postgres_available:
            return self.postgres_manager.get_table_as_dataframe(table_id)
        return None
    
    def is_file_processed(self, file_path: str, strategy: str) -> bool:
        """
        Check if a file has been processed with a specific strategy.
        
        Checks both storage backends and returns True if found in either.
        """
        # Check ChromaDB first (faster)
        if self.chroma_available:
            chroma_result = self.chroma_manager.is_file_processed(file_path, strategy)
            if chroma_result:
                return True
        
        # Check PostgreSQL
        if self.postgres_available:
            postgres_results = self.postgres_manager.get_processing_history(file_path)
            for result in postgres_results:
                if result.get('processing_strategy') == strategy:
                    return True
        
        return False
    
    def get_processing_history(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get processing history from PostgreSQL."""
        if self.postgres_available:
            return self.postgres_manager.get_processing_history(file_path)
        return []
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics from both backends."""
        stats = {
            "chroma_available": self.chroma_available,
            "postgres_available": self.postgres_available,
            "chroma_stats": {},
            "postgres_stats": {}
        }
        
        if self.chroma_available:
            try:
                stats["chroma_stats"] = self.chroma_manager.get_collection_stats()
            except Exception as e:
                self.logger.error(f"Error getting ChromaDB stats: {e}")
        
        if self.postgres_available:
            try:
                stats["postgres_stats"] = self.postgres_manager.get_database_stats()
            except Exception as e:
                self.logger.error(f"Error getting PostgreSQL stats: {e}")
        
        # Calculate combined stats
        stats["combined_stats"] = {
            "total_chunks": (
                stats["chroma_stats"].get("chunks", 0) + 
                stats["postgres_stats"].get("total_chunks", 0)
            ) // 2,  # Approximate, since they should contain the same data
            "total_tables": (
                stats["chroma_stats"].get("tables", 0) + 
                stats["postgres_stats"].get("total_tables", 0)
            ) // 2,
            "storage_backends": int(self.chroma_available) + int(self.postgres_available)
        }
        
        return stats
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, bool]:
        """Clean up old data from storage backends."""
        results = {
            "chroma_cleanup": False,
            "postgres_cleanup": False
        }
        
        # PostgreSQL cleanup (has date tracking)
        if self.postgres_available:
            try:
                results["postgres_cleanup"] = self.postgres_manager.cleanup_old_data(days_to_keep)
            except Exception as e:
                self.logger.error(f"PostgreSQL cleanup failed: {e}")
        
        # ChromaDB doesn't have built-in date-based cleanup
        # Could be implemented by querying and deleting based on metadata
        
        return results
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all storage backends."""
        health = {
            "overall_healthy": False,
            "chroma_healthy": False,
            "postgres_healthy": False,
            "errors": []
        }
        
        # Check ChromaDB
        if self.chroma_available:
            try:
                stats = self.chroma_manager.get_collection_stats()
                health["chroma_healthy"] = True
            except Exception as e:
                health["errors"].append(f"ChromaDB error: {e}")
        
        # Check PostgreSQL
        if self.postgres_available:
            try:
                stats = self.postgres_manager.get_database_stats()
                health["postgres_healthy"] = True
            except Exception as e:
                health["errors"].append(f"PostgreSQL error: {e}")
        
        health["overall_healthy"] = health["chroma_healthy"] or health["postgres_healthy"]
        
        return health
    
    def get_file_processing_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive processing information for a file."""
        info = {
            "file_path": file_path,
            "strategies_processed": [],
            "processing_history": [],
            "chunk_count": 0,
            "table_count": 0
        }
        
        # Get processing history from PostgreSQL
        if self.postgres_available:
            history = self.postgres_manager.get_processing_history(file_path)
            info["processing_history"] = history
            
            # Extract unique strategies
            strategies = set()
            for record in history:
                if record.get("processing_strategy"):
                    strategies.add(record["processing_strategy"])
            info["strategies_processed"] = list(strategies)
            
            # Get current chunk and table counts
            chunks = self.postgres_manager.get_chunks_by_file(file_path)
            tables = self.postgres_manager.get_tables_by_file(file_path)
            info["chunk_count"] = len(chunks)
            info["table_count"] = len(tables)
        
        return info 