"""
PostgreSQL Manager

Handles structured data storage in PostgreSQL for document processing results.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Text, Integer, Float, DateTime, Boolean, JSON
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import pandas as pd

from ..schemas.document_chunk import DocumentChunk
from ..schemas.financial_data import ProcessingResult


class PostgresManager:
    """
    Manages PostgreSQL operations for storing structured document processing data.
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize PostgreSQL manager.
        
        Args:
            connection_string: PostgreSQL connection string, if not provided uses env vars
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Setup connection
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = (
                f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
                f"{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:"
                f"{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
            )
        
        try:
            self.engine = create_engine(self.connection_string)
            self.metadata = MetaData()
            self._create_tables()
            self.logger.info("PostgreSQL connection established successfully")
        except Exception as e:
            self.logger.warning(f"PostgreSQL connection failed: {e}. Continuing without PostgreSQL.")
            self.engine = None
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        if not self.engine:
            return
            
        try:
            # Document chunks table
            self.chunks_table = Table(
                'document_chunks', self.metadata,
                Column('id', String(255), primary_key=True),
                Column('content', Text),
                Column('chunk_type', String(50)),
                Column('section', String(255)),
                Column('page_number', Integer),
                Column('file_path', String(500)),
                Column('file_name', String(255)),
                Column('processing_strategy', String(50)),
                Column('table_count', Integer),
                Column('content_length', Integer),
                Column('metadata', JSON),
                Column('created_at', DateTime, default=datetime.utcnow),
                Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            )
            
            # Extracted tables table
            self.tables_table = Table(
                'extracted_tables', self.metadata,
                Column('id', String(255), primary_key=True),
                Column('title', String(500)),
                Column('table_data', JSON),
                Column('headers', JSON),
                Column('row_count', Integer),
                Column('column_count', Integer),
                Column('table_type', String(50)),
                Column('section', String(255)),
                Column('page_number', Integer),
                Column('source_chunk_id', String(255)),
                Column('file_path', String(500)),
                Column('file_name', String(255)),
                Column('metadata', JSON),
                Column('created_at', DateTime, default=datetime.utcnow),
                Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            )
            
            # Processing results table
            self.processing_results_table = Table(
                'processing_results', self.metadata,
                Column('id', String(255), primary_key=True),
                Column('file_path', String(500)),
                Column('file_name', String(255)),
                Column('processing_strategy', String(50)),
                Column('status', String(50)),
                Column('total_chunks', Integer),
                Column('total_tables', Integer),
                Column('processing_time', Float),
                Column('was_cached', Boolean),
                Column('reused_existing', Boolean),
                Column('errors', JSON),
                Column('warnings', JSON),
                Column('document_metadata', JSON),
                Column('processing_metadata', JSON),
                Column('created_at', DateTime, default=datetime.utcnow),
                Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
            )
            
            # Create all tables
            self.metadata.create_all(self.engine)
            self.logger.info("PostgreSQL tables created/verified successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating PostgreSQL tables: {e}", exc_info=True)
    
    def store_chunks(self, chunks: List[DocumentChunk], document_metadata: Dict[str, Any]) -> bool:
        """
        Store document chunks in PostgreSQL.
        
        Args:
            chunks: List of DocumentChunk objects
            document_metadata: Metadata about the source document
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.engine:
            return False
            
        try:
            with self.engine.begin() as conn:
                for chunk in chunks:
                    chunk_data = {
                        'id': chunk.id,
                        'content': chunk.content,
                        'chunk_type': chunk.chunk_type,
                        'section': chunk.section,
                        'page_number': chunk.page_number,
                        'file_path': document_metadata.get('file_path', ''),
                        'file_name': document_metadata.get('file_name', ''),
                        'processing_strategy': document_metadata.get('processing_strategy', ''),
                        'table_count': chunk.table_count,
                        'content_length': chunk.content_length,
                        'metadata': {**chunk.metadata, **document_metadata}
                    }
                    
                    # Insert or update chunk
                    stmt = self.chunks_table.insert().values(**chunk_data)
                    conn.execute(stmt)
                    
                    # Store associated tables
                    if chunk.tables:
                        self._store_chunk_tables(conn, chunk, document_metadata)
            
            self.logger.info(f"Stored {len(chunks)} chunks in PostgreSQL")
            return True
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error storing chunks: {e}", exc_info=True)
            return False
        except Exception as e:
            self.logger.error(f"Error storing chunks in PostgreSQL: {e}", exc_info=True)
            return False
    
    def _store_chunk_tables(self, conn, chunk: DocumentChunk, document_metadata: Dict[str, Any]):
        """Store tables associated with a chunk."""
        for i, table in enumerate(chunk.tables):
            table_data = {
                'id': f"{chunk.id}_table_{i}",
                'title': table.get('title', ''),
                'table_data': table.get('data', []),
                'headers': table.get('headers', []),
                'row_count': len(table.get('data', [])),
                'column_count': len(table.get('headers', [])),
                'table_type': table.get('type', 'financial'),
                'section': chunk.section,
                'page_number': chunk.page_number,
                'source_chunk_id': chunk.id,
                'file_path': document_metadata.get('file_path', ''),
                'file_name': document_metadata.get('file_name', ''),
                'metadata': table.get('metadata', {})
            }
            
            stmt = self.tables_table.insert().values(**table_data)
            conn.execute(stmt)
    
    def store_processing_result(self, result: ProcessingResult) -> bool:
        """
        Store processing result in PostgreSQL.
        
        Args:
            result: ProcessingResult object
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.engine:
            return False
            
        try:
            with self.engine.begin() as conn:
                result_data = {
                    'id': f"{result.document_path}_{result.processing_strategy}_{datetime.now().timestamp()}",
                    'file_path': result.document_path,
                    'file_name': os.path.basename(result.document_path),
                    'processing_strategy': result.processing_strategy,
                    'status': result.status,
                    'total_chunks': result.total_chunks,
                    'total_tables': result.total_tables,
                    'processing_time': result.processing_time,
                    'was_cached': result.was_cached,
                    'reused_existing': result.reused_existing,
                    'errors': result.errors,
                    'warnings': result.warnings,
                    'document_metadata': result.document_metadata,
                    'processing_metadata': result.processing_metadata
                }
                
                stmt = self.processing_results_table.insert().values(**result_data)
                conn.execute(stmt)
            
            self.logger.info(f"Stored processing result for {result.document_path}")
            return True
            
        except SQLAlchemyError as e:
            self.logger.error(f"Database error storing processing result: {e}", exc_info=True)
            return False
        except Exception as e:
            self.logger.error(f"Error storing processing result: {e}", exc_info=True)
            return False
    
    def get_chunks_by_file(self, file_path: str, strategy: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve chunks for a specific file.
        
        Args:
            file_path: Path to the source file
            strategy: Optional processing strategy filter
            
        Returns:
            List of chunk dictionaries
        """
        if not self.engine:
            return []
            
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT * FROM document_chunks 
                    WHERE file_path = :file_path
                    ORDER BY page_number, id
                """)
                
                params = {'file_path': file_path}
                if strategy:
                    query = text("""
                        SELECT * FROM document_chunks 
                        WHERE file_path = :file_path AND processing_strategy = :strategy
                        ORDER BY page_number, id
                    """)
                    params['strategy'] = strategy
                
                result = conn.execute(query, params)
                chunks = [dict(row._mapping) for row in result]
                
                self.logger.info(f"Retrieved {len(chunks)} chunks for {file_path}")
                return chunks
                
        except Exception as e:
            self.logger.error(f"Error retrieving chunks: {e}", exc_info=True)
            return []
    
    def get_tables_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Retrieve extracted tables for a specific file."""
        if not self.engine:
            return []
            
        try:
            with self.engine.connect() as conn:
                query = text("""
                    SELECT * FROM extracted_tables 
                    WHERE file_path = :file_path
                    ORDER BY page_number, id
                """)
                
                result = conn.execute(query, {'file_path': file_path})
                tables = [dict(row._mapping) for row in result]
                
                self.logger.info(f"Retrieved {len(tables)} tables for {file_path}")
                return tables
                
        except Exception as e:
            self.logger.error(f"Error retrieving tables: {e}", exc_info=True)
            return []
    
    def get_table_as_dataframe(self, table_id: str) -> Optional[pd.DataFrame]:
        """Convert a stored table to pandas DataFrame."""
        if not self.engine:
            return None
            
        try:
            with self.engine.connect() as conn:
                query = text("SELECT table_data, headers FROM extracted_tables WHERE id = :table_id")
                result = conn.execute(query, {'table_id': table_id})
                row = result.fetchone()
                
                if row:
                    table_data = row.table_data
                    headers = row.headers
                    
                    df = pd.DataFrame(table_data)
                    if headers and len(headers) == len(df.columns):
                        df.columns = headers
                    
                    return df
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error converting table to DataFrame: {e}", exc_info=True)
            return None
    
    def get_processing_history(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get processing history, optionally filtered by file."""
        if not self.engine:
            return []
            
        try:
            with self.engine.connect() as conn:
                if file_path:
                    query = text("""
                        SELECT * FROM processing_results 
                        WHERE file_path = :file_path
                        ORDER BY created_at DESC
                    """)
                    params = {'file_path': file_path}
                else:
                    query = text("""
                        SELECT * FROM processing_results 
                        ORDER BY created_at DESC
                        LIMIT 100
                    """)
                    params = {}
                
                result = conn.execute(query, params)
                history = [dict(row._mapping) for row in result]
                
                return history
                
        except Exception as e:
            self.logger.error(f"Error retrieving processing history: {e}", exc_info=True)
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if not self.engine:
            return {}
            
        try:
            with self.engine.connect() as conn:
                stats = {}
                
                # Chunks count
                result = conn.execute(text("SELECT COUNT(*) as count FROM document_chunks"))
                stats['total_chunks'] = result.fetchone().count
                
                # Tables count
                result = conn.execute(text("SELECT COUNT(*) as count FROM extracted_tables"))
                stats['total_tables'] = result.fetchone().count
                
                # Processing results count
                result = conn.execute(text("SELECT COUNT(*) as count FROM processing_results"))
                stats['total_processing_runs'] = result.fetchone().count
                
                # Files processed
                result = conn.execute(text("SELECT COUNT(DISTINCT file_path) as count FROM document_chunks"))
                stats['unique_files_processed'] = result.fetchone().count
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}", exc_info=True)
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """Remove old processing data beyond the specified days."""
        if not self.engine:
            return False
            
        try:
            with self.engine.begin() as conn:
                cutoff_date = datetime.now() - pd.Timedelta(days=days_to_keep)
                
                # Clean old processing results
                query = text("DELETE FROM processing_results WHERE created_at < :cutoff_date")
                result = conn.execute(query, {'cutoff_date': cutoff_date})
                
                self.logger.info(f"Cleaned up {result.rowcount} old processing results")
                return True
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}", exc_info=True)
            return False 