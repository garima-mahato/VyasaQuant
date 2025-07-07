"""
Financial Document Processor

Main processor for financial PDF documents including parsing, chunking, and table extraction.
Based on the LLMPDFAgent functionality from the original llm_pdf_agent.py system.
"""

import os
import json
import logging
import time
import uuid
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# External dependencies
import tiktoken
from llama_parse import LlamaParse
from google import genai
import ollama
import pandas as pd

# Database and storage
import chromadb
from chromadb.config import Settings
import psycopg2
from sqlalchemy import create_engine, text
from psycopg2.extras import execute_values

# Other utilities
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Internal imports
from ..schemas.document_chunk import DocumentChunk
from ..schemas.financial_data import ProcessingResult

# Unicode normalization function from original
import unicodedata
def unicode_to_ascii(text):
    """Normalize unicode values"""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')


class FinancialDocumentProcessor:
    """
    Main processor for financial PDF documents.
    
    Handles the complete pipeline from PDF parsing to storage:
    - PDF parsing using LlamaParse (JSON format)
    - Semantic and content-based chunking
    - Financial table extraction
    - Vector embedding generation
    - Storage in ChromaDB and PostgreSQL
    """
    
    def __init__(self):
        """Initialize the financial document processor."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing Financial Document Processor")
        
        # Initialize components exactly like original
        self.setup_apis()
        self.setup_database()
        self.setup_chunking_config()
        self.setup_file_cache()
        
        self.logger.info("Financial Document Processor initialization completed")
    
    def setup_apis(self):
        """Initialize API connections for LlamaParse, Gemini, and Ollama"""
        self.logger.info("Setting up API connections")
        
        # LlamaParse setup - exact same as original
        self.llama_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if not self.llama_api_key:
            self.logger.error("LLAMA_CLOUD_API_KEY not found in environment variables")
            raise ValueError("LLAMA_CLOUD_API_KEY not found in environment variables")
        
        self.parser = LlamaParse(
            api_key=self.llama_api_key,
            result_type="markdown",
            verbose=True,
            language="en"
        )
        self.logger.info("LlamaParse initialized successfully")
        
        # Google Gemini setup - exact same as original
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if self.google_api_key:
            self.gemini_client = genai.Client(api_key=self.google_api_key)
            self.llm_provider = "gemini"
            self.logger.info("Google Gemini client initialized")
        else:
            self.llm_provider = "ollama"
            self.logger.info("Google API key not found, using Ollama as LLM provider")
        
        # Ollama setup - exact same as original
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_llm_model = os.getenv("OLLAMA_LLM_MODEL", "gemma3:1b")
        self.ollama_embed_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        
        self.logger.info(f"Using LLM provider: {self.llm_provider}")
        self.logger.info(f"Ollama configuration - URL: {self.ollama_base_url}, LLM: {self.ollama_llm_model}, Embed: {self.ollama_embed_model}")
    
    def setup_database(self):
        """Initialize ChromaDB and PostgreSQL connections"""
        self.logger.info("Setting up database connections")
        
        # ChromaDB setup
        chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Create collections
        self.chunks_collection = self.chroma_client.get_or_create_collection(
            name="document_chunks",
            metadata={"hnsw:space": "cosine"}
        )
        self.tables_collection = self.chroma_client.get_or_create_collection(
            name="extracted_tables",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Create collection for tracking processed files
        self.processed_files_collection = self.chroma_client.get_or_create_collection(
            name="processed_files_metadata",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.logger.info(f"ChromaDB initialized at: {chroma_path}")
        
        # PostgreSQL setup
        try:
            self.pg_engine = create_engine(
                f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
                f"{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:"
                f"{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
            )
            self.create_tables()
            self.logger.info("PostgreSQL connection established successfully")
        except Exception as e:
            self.logger.warning(f"PostgreSQL connection failed: {e}. Continuing with ChromaDB only.")
            self.pg_engine = None
    
    def setup_chunking_config(self):
        """Configure chunking parameters - exact same as original"""
        self.max_chunk_size = int(os.getenv("MAX_CHUNK_SIZE", "4000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        self.table_threshold = float(os.getenv("TABLE_EXTRACTION_THRESHOLD", "0.7"))
        
        self.logger.info(f"Chunking configuration - Max size: {self.max_chunk_size}, Overlap: {self.chunk_overlap}, Table threshold: {self.table_threshold}")
        
        # Initialize tokenizer for chunk size calculation
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            self.logger.info("Tokenizer initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize tokenizer: {e}")
            self.tokenizer = None
    
    def setup_file_cache(self):
        """Setup file cache directory - exact same as original"""
        self.file_cache_dir = Path(os.getenv("FILE_CACHE_DIR", "./file_cache"))
        self.file_cache_dir.mkdir(exist_ok=True)
        self.logger.info(f"File cache directory: {self.file_cache_dir}")
    
    def get_file_cache_path(self, pdf_path: str) -> Path:
        """Get cache file path for PDF - exact same as original"""
        pdf_file = Path(pdf_path)
        cache_filename = f"{pdf_file.stem}.jsonl"
        return self.file_cache_dir / cache_filename
    
    def is_file_cached(self, pdf_path: str) -> bool:
        """Check if file is cached - exact same as original"""
        cache_path = self.get_file_cache_path(pdf_path)
        if cache_path.exists():
            pdf_mtime = Path(pdf_path).stat().st_mtime
            cache_mtime = cache_path.stat().st_mtime
            return cache_mtime >= pdf_mtime
        return False
    
    def save_file_to_cache(self, pdf_path, data_list) -> None:
        """Save parsed data to cache - exact same as original"""
        cache_path = self.get_file_cache_path(pdf_path)
        try:
            with open(cache_path, "w") as file:
                for item in data_list:
                    json.dump(item, file)
                    file.write("\n")
            self.logger.info(f"Saved to cache: {cache_path}")
        except Exception as e:
            self.logger.error(f"Error saving to cache: {e}")
    
    def load_file_from_cache(self, pdf_path) -> List[Dict[str, Any]] | None:
        """Load parsed data from cache - exact same as original"""
        cache_path = self.get_file_cache_path(pdf_path)
        data = []
        try:
            with open(cache_path, "r") as file:
                for line in file:
                    data.append(json.loads(line))
            self.logger.info(f"Loaded from cache: {cache_path}")
            return data
        except Exception as e:
            self.logger.error(f"Error loading from cache: {e}")
            return []
    
    def get_or_parse_file(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Get content from cache or parse fresh - exact same as original"""
        try:
            if self.is_file_cached(pdf_path):
                self.logger.info(f"Loading from cache: {Path(pdf_path).name}")
                content = self.load_file_from_cache(pdf_path)
                if content:
                    return content
                    
            # Parse fresh
            self.logger.info(f"Parsing fresh: {Path(pdf_path).name}")
            content = self.parse_pdf(pdf_path)
            
            # Save to cache
            if content:
                self.save_file_to_cache(pdf_path, content)
                
            return content
            
        except Exception as e:
            self.logger.error(f"Error getting/parsing file {pdf_path}: {e}")
            return []
    
    def parse_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Parse PDF using LlamaParse and return structured JSON content - exact same as original"""
        try:
            self.logger.info(f"Parsing PDF: {pdf_path}")
            documents = self.parser.get_json_result(pdf_path)  # This is the key difference - using get_json_result
            
            if not documents:
                self.logger.error("No content extracted from PDF")
                raise ValueError("No content extracted from PDF")
                
            # Return the pages from the first document
            content = documents[0]["pages"]
            self.logger.info(f"Successfully parsed PDF. Content length: {len(content)} pages")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error parsing PDF {pdf_path}: {e}")
            raise
    
    def extract_sections(self, pages):
        """
        Extract document sections based on level-1 headings - exact same as original
        Each section has 'title' and 'content' (concatenated text).
        """
        sections = []
        current_section = None
        for page in pages:
            # The 'items' key holds parsed content including headings and text
            i = 0
            for item in page.get('items', []):
                if item.get('type') == 'heading' and item.get('lvl') == 1:
                    # Start a new section at each level-1 heading
                    if current_section is not None:
                        sections.append(current_section)
                    current_section = {
                        'title': unicode_to_ascii(item.get('value', '').strip()),
                        'content': "",
                        'tables': [],
                        'metadata': {'page': page['page']}
                    }
                elif item.get('type') == 'text' and current_section is not None:
                    # Append any text items to the current section's content
                    text = unicode_to_ascii(item.get('value', '').strip())
                    if text:
                        # Add a newline or space to separate paragraphs
                        current_section['content'] += text + "\n"
                elif item.get('type') == 'table' and current_section is not None:
                    # Append any text items to the current section's content
                    table = item.get('md', '')
                    if table:
                        # Add a newline or space to separate paragraphs
                        current_section['tables'].append({str(current_section['title']+"_"+str(i)): table})
                i += 1                
        # Append the last section if any
        if current_section is not None:
            sections.append(current_section)
        return sections

    def extract_financial_tables(self, pages):
        """
        Detect and extract the specific consolidated financial tables - exact same as original
        Returns a dict mapping statement names to DataFrames.
        """
        tables = {}
        tables['consolidated_balance_sheet'] = []
        tables['consolidated_profit_and_loss'] = []
        tables['consolidated_cash_flow'] = []
        ft_pg_num = {}
        ft_pg_num['consolidated_balance_sheet'] = []
        ft_pg_num['consolidated_profit_and_loss'] = []
        ft_pg_num['consolidated_cash_flow'] = []
        for page in pages:
            for item in page.get('items', []):
                if item.get('type') == 'table':
                    rows = item.get('rows', [])
                    if not rows:
                        continue
                    header = rows[0]
                    # Identify tables by header patterns
                    if page['items'][0] and "value" in page['items'][0].keys() and "Balance Sheet" in page['items'][0]["value"] and "Consolidated" in page['items'][0]["value"]:
                        # Consolidated Balance Sheet
                        df = pd.DataFrame(rows[1:], columns=header)
                        tables['consolidated_balance_sheet'].append(df)
                        ft_pg_num['consolidated_balance_sheet'].append(page["page"])
                    elif page['items'][0] and "value" in page['items'][0].keys() and "Profit" in page['items'][0]["value"] and "Consolidated" in page['items'][0]["value"]:
                        # Consolidated Profit and Loss Statement
                        df = pd.DataFrame(rows[1:], columns=header)
                        tables['consolidated_profit_and_loss'].append(df)
                        ft_pg_num['consolidated_profit_and_loss'].append(page["page"])
                    elif page['items'][0] and "value" in page['items'][0].keys() and "Cash Flows" in page['items'][0]["value"] and "Consolidated" in page['items'][0]["value"]:
                        # Consolidated Cash Flow Statement
                        df = pd.DataFrame(rows[1:], columns=header)
                        tables['consolidated_cash_flow'].append(df)
                        ft_pg_num['consolidated_cash_flow'].append(page["page"])
        return tables, ft_pg_num
    
    def generate_llm_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response using either Gemini or Ollama - exact same as original"""
        self.logger.debug(f"Generating LLM response using {self.llm_provider}")
        try:
            if self.llm_provider == "gemini" and hasattr(self, 'gemini_client'):
                # Using new google-genai package
                response = self.gemini_client.models.generate_content(
                    model='gemini-2.0-flash-001',
                    contents=prompt
                )
                self.logger.debug("Successfully generated response using Gemini")
                return response.text
            else:
                # Use Ollama
                response = ollama.generate(
                    model=self.ollama_llm_model,
                    prompt=prompt,
                    options={'num_predict': max_tokens}
                )
                self.logger.debug("Successfully generated response using Ollama")
                return response['response']
                
        except Exception as e:
            self.logger.error(f"Error generating LLM response: {e}")
            return ""
    
    def semantic_chunking(self, content: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """Perform semantic chunking ensuring tables belong to coherent chunks - exact same as original"""
        self.logger.info("Starting semantic chunking process")
        chunks = []
        
        # Split content into sections based on headers
        sections = self.extract_sections(content)
        self.logger.info(f"Split content into {len(sections)} sections")
        
        for section in sections:
            # Create semantic chunks for this section
            section_chunks = self._create_section_chunks(section)
            self.logger.debug(f"Section '{section['title']}': {len(section['tables'])} tables found")
            
            chunks.extend(section_chunks)
            
        self.logger.info(f"Created {len(chunks)} semantic chunks")
        return chunks
    
    def _create_section_chunks(self, section: Dict[str, Any]) -> List[DocumentChunk]:
        """Create semantic chunks for a section with its tables - exact same as original"""
        self.logger.debug(f"Creating chunks for section: {section['title']}")
        chunks = []
        
        # If section is small enough, create single chunk
        if self._get_token_count(section['content']) <= self.max_chunk_size:
            chunk = DocumentChunk(
                id=f"{section['title'].lower().replace(' ', '_')}",
                content=section['content'],
                metadata={
                    "section": section['title'],
                    "token_count": self._get_token_count(section['content']),
                    "has_tables": len(section['tables']) > 0,
                    "page": section['metadata']['page']
                },
                tables=section['tables'],
                chunk_type="mixed" if section['tables'] else "text",
                section=section['title']
            )
            chunks.append(chunk)
            self.logger.debug(f"Created single chunk for section '{section['title']}'")
        else:
            # Split large sections while keeping tables with relevant text
            sub_chunks = self._split_large_section(section)
            chunks.extend(sub_chunks)
            self.logger.debug(f"Split large section '{section['title']}' into {len(sub_chunks)} chunks")
            
        return chunks
    
    def _split_large_section(self, section: Dict[str, Any]) -> List[DocumentChunk]:
        """Split large sections into smaller semantic chunks - exact same as original"""
        self.logger.debug(f"Splitting large section: {section['title']}")
        chunks = []
        
        # Use LLM to identify natural break points
        prompt = f"""
        Analyze the following text and identify natural semantic break points where the content 
        can be split into coherent, self-contained chunks. Each chunk should contain related 
        information and any tables should stay with their relevant context.
        
        Text: {section['content'][:2000]}...
        
        Return break points as line numbers or keywords where splits should occur.
        """
        
        break_points_response = self.generate_llm_response(prompt, max_tokens=500)
        
        # For now, use simple paragraph-based splitting as fallback
        paragraphs = section['content'].split('\n\n')
        current_chunk = ""
        chunk_index = 0
        
        for paragraph in paragraphs:
            # Check if adding this paragraph would exceed chunk size
            test_chunk = current_chunk + "\n" + paragraph if current_chunk else paragraph
            
            if self._get_token_count(test_chunk) > self.max_chunk_size and current_chunk:
                # Create chunk with current content
                chunk = DocumentChunk(
                    id=f"{section['title'].lower().replace(' ', '_')}_{chunk_index}",
                    content=current_chunk,
                    metadata={
                        "section": section['title'],
                        "chunk_index": chunk_index,
                        "token_count": self._get_token_count(current_chunk),
                        "page": section['metadata']['page']
                    },
                    tables=section['tables'] if chunk_index == 0 else [],  # Tables only in first chunk
                    chunk_type="mixed" if section['tables'] and chunk_index == 0 else "text",
                    section=section['title']
                )
                chunks.append(chunk)
                
                # Start new chunk
                current_chunk = paragraph
                chunk_index += 1
            else:
                current_chunk = test_chunk
        
        # Add final chunk if there's remaining content
        if current_chunk:
            chunk = DocumentChunk(
                id=f"{section['title'].lower().replace(' ', '_')}_{chunk_index}",
                content=current_chunk,
                metadata={
                    "section": section['title'],
                    "chunk_index": chunk_index,
                    "token_count": self._get_token_count(current_chunk),
                    "page": section['metadata']['page']
                },
                tables=[],
                chunk_type="text",
                section=section['title']
            )
            chunks.append(chunk)
        
        return chunks
    
    def _get_token_count(self, text: str) -> int:
        """Get token count for text - exact same as original"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback: approximate 4 characters per token
            return len(text) // 4
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp string - exact same as original"""
        return datetime.now().isoformat()
    
    def generate_embeddings(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Generate embeddings for chunks using Ollama nomic-embed-text - exact same as original"""
        self.logger.info(f"Generating embeddings for {len(chunks)} chunks")
        
        for chunk in chunks:
            try:
                # Combine content and table information for embedding
                embed_text = chunk.content
                if chunk.tables:
                    # Add table summaries to embedding text
                    for table in chunk.tables:
                        try:
                            # Handle different table structures
                            if isinstance(table, dict):
                                # Check if it's a contents-based table (has 'dataframe' key)
                                if 'dataframe' in table:
                                    headers = table.get('headers', [])
                                    row_count = table.get('rows', 0)
                                    table_summary = f"Table: {', '.join(headers)} with {row_count} rows"
                                
                                # Check if it's a table dict with table_id as key
                                elif len(table.keys()) == 1 and isinstance(list(table.values())[0], (str, pd.DataFrame)):
                                    table_id = list(table.keys())[0]
                                    table_data = table[table_id]
                                    if isinstance(table_data, pd.DataFrame):
                                        headers = list(table_data.columns)
                                        row_count = len(table_data)
                                        table_summary = f"Table {table_id}: {', '.join(headers)} with {row_count} rows"
                                    else:
                                        table_summary = f"Table {table_id}: {str(table_data)[:100]}..."
                                
                                # Check if it's an old-style table with direct keys
                                elif 'headers' in table and 'row_count' in table:
                                    headers = table.get('headers', [])
                                    row_count = table.get('row_count', 0)
                                    table_summary = f"Table: {', '.join(headers)} with {row_count} rows"
                                
                                else:
                                    # Fallback for unknown table structure
                                    table_summary = f"Table: {str(table)[:100]}..."
                            
                            else:
                                # Handle non-dict table structures
                                table_summary = f"Table: {str(table)[:100]}..."
                            
                            embed_text += f"\n{table_summary}"
                            
                        except Exception as table_error:
                            self.logger.warning(f"Error processing table for embedding in chunk {chunk.id}: {table_error}")
                            # Add a generic table summary as fallback
                            embed_text += f"\n[Table data present but could not be processed for embedding]"
                
                # Generate embedding using Ollama
                response = ollama.embeddings(
                    model=self.ollama_embed_model,
                    prompt=embed_text
                )
                chunk.embeddings = response['embedding']
                
            except Exception as e:
                self.logger.error(f"Error generating embedding for chunk {chunk.id}: {e}")
                chunk.embeddings = None
                
        self.logger.info("Embedding generation completed")
        return chunks
    
    def find_contents_page(self, pages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find the contents/table of contents page in the document - exact same as original"""
        self.logger.info("Searching for contents page")
        
        for page in pages:
            # Check if page contains "Contents" heading
            text = unicode_to_ascii(page.get('text', '').strip())
            items = page.get('items', [])
            
            # Look for "Contents" in text or as a heading
            if 'Contents' in text:
                # Verify it's actually a contents page by checking for section titles and page numbers
                for item in items:
                    if (item.get('type') == 'heading' and 
                        'Contents' in unicode_to_ascii(item.get('value', ''))):
                        self.logger.info(f"Found contents page at page {page.get('page')}")
                        return page
                        
        self.logger.warning("Contents page not found")
        return None
    
    def parse_contents_page(self, contents_page: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse the contents page to extract section titles and page numbers - exact same as original"""
        self.logger.info("Parsing contents page to extract section mappings")
        
        sections = []
        current_category = None
        
        items = contents_page.get('items', [])
        
        for item in items:
            item_type = item.get('type')
            item_value = unicode_to_ascii(item.get('value', '').strip())
            
            if item_type == 'heading' and item_value != 'Contents':
                # This is a category heading like "CORPORATE OVERVIEW", "STATUTORY REPORTS", etc.
                current_category = item_value
                self.logger.debug(f"Found category: {current_category}")
                
            elif item_type == 'text' and current_category:
                # Parse text content to extract individual sections
                lines = item_value.split('\n')
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Extract page number and title using regex
                    # Pattern to match: "03  Chairman's Statement" or "140  Independent Auditor's Report"
                    match = re.match(r'^(\d+)\s+(.+?)(?:\s*$)', line)
                    
                    if match:
                        page_num = int(match.group(1))
                        title = match.group(2).strip()
                        
                        section_info = {
                            'category': current_category,
                            'title': title,
                            'page_number': page_num,
                            'full_title': f"{current_category} - {title}" if current_category else title
                        }
                        sections.append(section_info)
                        self.logger.debug(f"Extracted section: {title} (page {page_num})")
        
        self.logger.info(f"Extracted {len(sections)} sections from contents page")
        return sections
    
    def get_section_content(self, pages: List[Dict[str, Any]], section_info: Dict[str, Any], 
                           contents_page_num: int) -> Dict[str, Any]:
        """Extract content for a specific section based on contents page mapping - exact same as original"""
        target_page = section_info['page_number']
        section_title = section_info['title']
        
        # Adjust page number if contents is not on page 1
        if contents_page_num > 1:
            target_page += contents_page_num - 1
        
        self.logger.debug(f"Looking for section '{section_title}' starting at page {target_page}")
        
        section_content = {
            'title': section_info['full_title'],
            'category': section_info['category'],
            'content': '',
            'tables': [],
            'metadata': {
                'start_page': target_page,
                'end_page': target_page,
                'section_from_contents': True
            }
        }
        
        # Find pages that belong to this section
        section_pages = []
        found_section = False
        
        for page in pages:
            page_num = page.get('page', 0)
            
            if page_num < target_page:
                continue
                
            items = page.get('items', [])
            
            # Check if this page starts with our section title
            if not found_section:
                for item in items:
                    if (item.get('type') == 'heading' and 
                        self._matches_section_title(unicode_to_ascii(item.get('value', '')), unicode_to_ascii(section_title))):
                        found_section = True
                        section_content["title"] = unicode_to_ascii(item.get('value', ''))
                        section_pages.append(page)
                        break
            else:
                # Check if this page starts a new section
                page_starts_new_section = False
                for item in items:
                    if item.get('type') == 'heading' and item.get('lvl', 0) <= 2:
                        # This might be a new section - check if it's in our sections list
                        page_starts_new_section = True
                        break
                
                if page_starts_new_section:
                    break
                else:
                    section_pages.append(page)
        
        # Extract content from section pages
        for page in section_pages:
            page_content = self._extract_page_content_for_section(page, section_info)
            section_content['content'] += page_content['text']
            section_content['tables'].extend(page_content['tables'])
            section_content['metadata']['end_page'] = page.get('page', target_page)
        
        self.logger.debug(f"Extracted content for section '{section_title}': {len(section_content['content'])} chars, {len(section_content['tables'])} tables")
        return section_content
    
    def _matches_section_title(self, heading_text: str, expected_title: str) -> bool:
        """Check if a heading matches the expected section title - exact same as original"""
        # Normalize both titles for comparison
        heading_clean = re.sub(r'[^\w\s]', '', heading_text.lower().strip())
        expected_clean = re.sub(r'[^\w\s]', '', expected_title.lower().strip())
        
        # Check for exact match or if expected title is contained in heading
        return expected_clean in heading_clean or heading_clean in expected_clean
    
    def _extract_page_content_for_section(self, page: Dict[str, Any], section_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text and tables from a page for a specific section - exact same as original"""
        page_content = {
            'text': '',
            'tables': []
        }
        
        items = page.get('items', [])
        
        for i, item in enumerate(items):
            item_type = item.get('type')
            item_value = unicode_to_ascii(item.get('value', ''))
            
            if item_type == 'text':
                page_content['text'] += item_value + '\n'
                
            elif item_type == 'heading':
                # Include headings in content
                level = item.get('lvl', 1)
                heading_prefix = '#' * level
                page_content['text'] += f"{heading_prefix} {item_value}\n\n"
                
            elif item_type == 'table':
                # Extract table and maintain structure
                table_data = self._extract_table_structure(item, f"{section_info['title']}_table_{i}")
                if table_data:
                    page_content['tables'].append(table_data)
                    
                    # Add table summary to text content
                    table_summary = f"[Table: {table_data['title']} - {table_data['rows']} rows x {table_data['columns']} columns]\n"
                    page_content['text'] += table_summary
        
        return page_content
    
    def _extract_table_structure(self, table_item: Dict[str, Any], table_id: str) -> Optional[Dict[str, Any]]:
        """Extract table structure that can be converted to pandas DataFrame - exact same as original"""
        try:
            rows = table_item.get('rows', [])
            if not rows:
                return None
            
            # Create pandas DataFrame from rows
            df = pd.DataFrame(rows[1:], columns=rows[0]) if len(rows) > 1 else pd.DataFrame()
            
            table_data = {
                'id': table_id,
                'title': f"Table_{table_id}",
                'dataframe': df,
                'rows': len(df),
                'columns': len(df.columns),
                'headers': list(df.columns),
                'raw_data': rows,
                'metadata': {
                    'extracted_from': 'contents_based_chunking',
                    'table_id': table_id
                }
            }
            
            return table_data
            
        except Exception as e:
            self.logger.error(f"Error extracting table structure: {e}")
            return None
    
    def create_pre_contents_chunks(self, pages: List[Dict[str, Any]], contents_page_num: int) -> List[DocumentChunk]:
        """Create chunks for pages before contents page - exact same as original"""
        self.logger.info(f"Creating pre-contents chunks for pages 1-{contents_page_num-1}")
        chunks = []
        
        for page in pages:
            page_num = page.get('page', 0)
            
            if page_num >= contents_page_num:
                break
                
            # Extract page content
            page_content = self._extract_page_content_for_section(page, {'title': f'Pre_Contents_Page_{page_num}'})
            
            if page_content['text'].strip():
                chunk = DocumentChunk(
                    id=f"pre_contents_page_{page_num}",
                    content=page_content['text'],
                    metadata={
                        'section': f'Pre-Contents Page {page_num}',
                        'page_number': page_num,
                        'token_count': self._get_token_count(page_content['text']),
                        'has_tables': len(page_content['tables']) > 0,
                        'chunk_type': 'pre_contents_page'
                    },
                    tables=page_content['tables'],
                    chunk_type="mixed" if page_content['tables'] else "text",
                    section=f"Pre-Contents Page {page_num}",
                    page_number=page_num
                )
                chunks.append(chunk)
                self.logger.debug(f"Created pre-contents chunk for page {page_num}")
        
        return chunks
    
    def contents_based_chunking(self, pages: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """
        New chunking strategy based on table of contents - exact same as original
        Creates separate chunks for:
        1. Pages before contents page (page-wise)
        2. Contents page itself
        3. Each section identified in contents page
        """
        self.logger.info("Starting contents-based chunking strategy")
        chunks = []
        
        # Step 1: Find contents page
        contents_page = self.find_contents_page(pages)
        if not contents_page:
            self.logger.error("Contents page not found, falling back to section-based chunking")
            return self.semantic_chunking(pages)
        
        contents_page_num = contents_page.get('page', 1)
        
        # Step 2: Create chunks for pages before contents
        pre_contents_chunks = self.create_pre_contents_chunks(pages, contents_page_num)
        chunks.extend(pre_contents_chunks)
        
        # Step 3: Create chunk for contents page itself
        contents_content = self._extract_page_content_for_section(contents_page, {'title': 'Contents'})
        contents_chunk = DocumentChunk(
            id="contents_page",
            content=contents_content['text'],
            metadata={
                'section': 'Contents',
                'page_number': contents_page_num,
                'token_count': self._get_token_count(contents_content['text']),
                'has_tables': len(contents_content['tables']) > 0,
                'chunk_type': 'contents_page'
            },
            tables=contents_content['tables'],
            chunk_type="mixed" if contents_content['tables'] else "text",
            section="Contents",
            page_number=contents_page_num
        )
        chunks.append(contents_chunk)
        
        # Step 4: Parse contents page to get section mappings
        sections = self.parse_contents_page(contents_page)
        
        # Step 5: Create chunks for each section
        for section_info in sections:
            section_content = self.get_section_content(pages, section_info, contents_page_num)
            
            if not section_content['content'].strip():
                self.logger.warning(f"No content found for section: {section_info['title']}")
                continue
            
            # Create chunk for this section
            chunk = DocumentChunk(
                id=f"section_{section_content['title'].lower().replace(' ', '_').replace('&', 'and')}",
                content=section_content['content'],
                metadata={
                    'section': section_content['title'],
                    'category': section_content['category'],
                    'start_page': section_content['metadata']['start_page'],
                    'end_page': section_content['metadata']['end_page'],
                    'token_count': self._get_token_count(section_content['content']),
                    'has_tables': len(section_content['tables']) > 0,
                    'chunk_type': 'contents_based_section',
                    'table_count': len(section_content['tables'])
                },
                tables=section_content['tables'],
                chunk_type="mixed" if section_content['tables'] else "text",
                section=section_content['title'],
                page_number=section_content['metadata']['start_page']
            )
            
            chunks.append(chunk)
            self.logger.debug(f"Created chunk for section: {section_info['title']}")
        
        self.logger.info(f"Contents-based chunking created {len(chunks)} chunks")
        return chunks
    
    def process_document(self, pdf_path: str, strategy: str = "contents_based", 
                        company_name: str = None, financial_year: str = None) -> ProcessingResult:
        """
        Process a PDF document with the specified strategy.
        
        Args:
            pdf_path: Path to the PDF file
            strategy: Processing strategy ('semantic' or 'contents_based')
            company_name: Name of the company (for filtering and search)
            financial_year: Financial year (e.g., "FY2023", "2022-23")
            
        Returns:
            ProcessingResult containing processing outcome and metadata
        """
        start_time = time.time()
        
        # Create processing result object
        result = ProcessingResult(
            status="processing",
            document_path=pdf_path,
            processing_strategy=strategy
        )
        
        try:
            self.logger.info(f"Processing PDF with {strategy} chunking: {pdf_path}")
            if company_name:
                self.logger.info(f"Company: {company_name}")
            if financial_year:
                self.logger.info(f"Financial Year: {financial_year}")
            
            # Check if file has already been processed with this strategy and metadata
            if self.is_file_processed_with_strategy(pdf_path, strategy, company_name, financial_year):
                self.logger.info(f"File {Path(pdf_path).name} already processed with {strategy} strategy for {company_name} {financial_year}, retrieving existing results")
                
                # Get existing chunks exactly like original
                chunks = self.get_chunks_by_strategy(pdf_path, strategy, company_name, financial_year)
                
                # Calculate actual counts from existing data
                total_tables = sum(len(chunk.tables) for chunk in chunks)
                
                # Prepare document metadata
                file_path = Path(pdf_path)
                document_metadata = {
                    "file_path": str(file_path.absolute()),
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size,
                    "processing_date": self._get_current_timestamp(),
                    "was_cached": True,
                    "chunking_strategy": strategy,
                    "company_name": company_name,
                    "financial_year": financial_year,
                    "reused_existing_processing": True
                }
                
                # Update result with actual data
                result.total_chunks = len(chunks)
                result.total_tables = total_tables
                result.document_metadata = document_metadata
                result.chunks_summary = [
                    {
                        "id": chunk.id,
                        "section": chunk.section,
                        "chunk_type": chunk.chunk_type,
                        "token_count": chunk.metadata.get("token_count", 0),
                        "table_count": len(chunk.tables),
                        "page_range": f"{chunk.metadata.get('start_page', chunk.page_number)}-{chunk.metadata.get('end_page', chunk.page_number)}" if chunk.metadata.get('start_page') else str(chunk.page_number),
                        "company_name": company_name,
                        "financial_year": financial_year
                    }
                    for chunk in chunks
                ]
                
                result.status = "success"
                result.reused_existing = True
                return result
            
            # Get content (from cache or parse)
            content = self.get_or_parse_file(pdf_path)
            
            # Use appropriate chunking strategy
            if strategy == "semantic":
                chunks = self.semantic_chunking(content)
            elif strategy == "contents_based":
                chunks = self.contents_based_chunking(content)
            else:
                result.status = "error"
                result.add_error(f"Unknown processing strategy: {strategy}")
                return result

            # Add company and financial year metadata to each chunk
            for chunk in chunks:
                if company_name:
                    chunk.metadata["company_name"] = company_name
                if financial_year:
                    chunk.metadata["financial_year"] = financial_year

            # Extract financial tables
            financial_tables, financial_tables_pg_num = self.extract_financial_tables(content)
            self.logger.info(f"Extracted {len(financial_tables)} financial tables")

            # Generate embeddings
            chunks = self.generate_embeddings(chunks)
            
            # Prepare document metadata
            file_path = Path(pdf_path)
            document_metadata = {
                "file_path": str(file_path.absolute()),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "processing_date": self._get_current_timestamp(),
                "total_pages": len(content),
                "content_length": len(content),
                "was_cached": self.is_file_cached(pdf_path),
                "chunking_strategy": strategy,
                "company_name": company_name,
                "financial_year": financial_year
            }
            
            # Store results using direct database methods
            self.store_chunks(chunks, document_metadata, strategy)
            
            # Mark file as processed
            self.mark_file_as_processed(pdf_path, strategy, document_metadata)
            
            # Calculate total tables from chunks
            total_tables = sum(len(chunk.tables) for chunk in chunks)
            
            # Update result with processing info
            result.total_chunks = len(chunks)
            result.total_tables = total_tables
            result.document_metadata = document_metadata
            result.chunks_summary = [
                {
                    "id": chunk.id,
                    "section": chunk.section,
                    "chunk_type": chunk.chunk_type,
                    "token_count": chunk.metadata.get("token_count", 0),
                    "table_count": len(chunk.tables),
                    "page_range": f"{chunk.metadata.get('start_page', chunk.page_number)}-{chunk.metadata.get('end_page', chunk.page_number)}" if chunk.metadata.get('start_page') else str(chunk.page_number),
                    "company_name": company_name,
                    "financial_year": financial_year
                }
                for chunk in chunks
            ]
            
            result.status = "success"
            self.logger.info(f"Successfully processed PDF with {strategy} chunking: {pdf_path}")
            
        except Exception as e:
            result.status = "error"
            result.add_error(f"Processing failed: {str(e)}")
            self.logger.error(f"Error processing document: {e}", exc_info=True)
        
        finally:
            result.processing_time = time.time() - start_time
            result.processing_metadata["processing_date"] = datetime.now().isoformat()
        
        return result
    
    def process_multiple_documents(self, documents_info: List[Dict[str, str]], 
                                 strategy: str = "contents_based") -> Dict[str, Any]:
        """
        Process multiple PDF documents with company and financial year metadata.
        
        Args:
            documents_info: List of dictionaries with keys:
                           - pdf_path: Path to PDF file
                           - company_name: Company name (optional)
                           - financial_year: Financial year (optional)
            strategy: Processing strategy to use
            
        Returns:
            Summary of processing results
        """
        self.logger.info(f"Processing {len(documents_info)} documents with {strategy} strategy")
        
        all_results = []
        successful_count = 0
        failed_count = 0
        
        for doc_info in documents_info:
            pdf_path = doc_info.get('pdf_path')
            company_name = doc_info.get('company_name')
            financial_year = doc_info.get('financial_year')
            
            if not pdf_path:
                self.logger.error("Missing pdf_path in document info")
                failed_count += 1
                continue
            
            self.logger.info(f"Processing: {Path(pdf_path).name} | Company: {company_name or 'Unknown'} | Year: {financial_year or 'Unknown'}")
            
            result = self.process_document(pdf_path, strategy, company_name, financial_year)
            all_results.append(result)
            
            if result.is_successful:
                successful_count += 1
                # Determine status message
                if result.reused_existing:
                    status_msg = "reused"
                elif result.document_metadata.get('was_cached'):
                    status_msg = "from cache"
                else:
                    status_msg = "freshly parsed"
                
                self.logger.info(f"✅ Success ({status_msg}): {result.total_chunks} chunks, {result.total_tables} tables")
            else:
                failed_count += 1
                self.logger.error(f"❌ Failed: {result.errors[0] if result.errors else 'Unknown error'}")
        
        # Combine results
        summary = {
            "total_files": len(documents_info),
            "successful": successful_count,
            "failed": failed_count,
            "chunking_strategy": strategy,
            "files_processed": [result.to_dict() for result in all_results],
            "summary": {
                "total_chunks": sum(r.total_chunks for r in all_results if r.is_successful),
                "total_tables": sum(r.total_tables for r in all_results if r.is_successful),
                "processing_date": self._get_current_timestamp(),
                "companies_processed": list(set(
                    r.document_metadata.get('company_name') 
                    for r in all_results 
                    if r.is_successful and r.document_metadata.get('company_name')
                )),
                "financial_years_processed": list(set(
                    r.document_metadata.get('financial_year') 
                    for r in all_results 
                    if r.is_successful and r.document_metadata.get('financial_year')
                ))
            }
        }
        
        self.logger.info(f"Batch processing completed: {successful_count}/{len(documents_info)} successful")
        self.logger.info(f"Companies processed: {summary['summary']['companies_processed']}")
        self.logger.info(f"Financial years processed: {summary['summary']['financial_years_processed']}")
        
        return summary
    
    def search_documents(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search processed documents"""
        # Generate query embedding using Ollama directly (same as original)
        try:
            response = ollama.embeddings(
                model=self.ollama_embed_model,
                prompt=query
            )
            query_embedding = response['embedding']
        except Exception as e:
            self.logger.error(f"Error generating query embedding: {e}")
            return {"chunks": [], "total_results": 0}
        
        # Search using direct ChromaDB method like original
        results = self.search_chunks(query, top_k)
        
        # Convert to expected format
        formatted_results = {"chunks": [], "total_results": 0}
        if results and 'documents' in results and results['documents']:
            # ChromaDB returns lists, need to combine them properly
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if results['distances'] else []
            ids = results['ids'][0] if results['ids'] else []
            
            formatted_results["total_results"] = len(documents)
            for i, doc in enumerate(documents):
                chunk_result = {
                    'content': doc,
                    'metadata': metadatas[i] if i < len(metadatas) else {},
                    'distance': distances[i] if i < len(distances) else 1.0,
                    'id': ids[i] if i < len(ids) else f"chunk_{i}"
                }
                formatted_results["chunks"].append(chunk_result)
        
        return formatted_results
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        try:
            # Get counts from ChromaDB collections
            chunks_count = self.chunks_collection.count()
            tables_count = self.tables_collection.count() 
            files_count = self.processed_files_collection.count()
            
            stats = {
                "chromadb_stats": {
                    "total_chunks": chunks_count,
                    "total_tables": tables_count,
                    "total_processed_files": files_count
                },
                "postgresql_stats": {
                    "available": self.pg_engine is not None
                }
            }
            
            if self.pg_engine:
                try:
                    with self.pg_engine.connect() as conn:
                        result = conn.execute(text("SELECT COUNT(*) FROM processed_documents"))
                        pg_docs_count = result.fetchone()[0]
                        stats["postgresql_stats"]["total_documents"] = pg_docs_count
                except Exception as e:
                    self.logger.warning(f"Could not get PostgreSQL stats: {e}")
                    stats["postgresql_stats"]["error"] = str(e)
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting processing stats: {e}")
            return {"error": str(e)}
    
    def store_chunks(self, chunks: List[DocumentChunk], document_metadata: Dict[str, Any], strategy: str = "semantic"):
        """Store chunks in ChromaDB and PostgreSQL with chunking strategy information"""
        self.logger.info(f"Storing chunks in databases with {strategy} strategy")
        
        # Add strategy to document metadata
        document_metadata["chunking_strategy"] = strategy
        
        # Store in ChromaDB
        self._store_in_chromadb(chunks, document_metadata)
        
        # Store in PostgreSQL if available
        if self.pg_engine:
            self._store_in_postgresql(chunks, document_metadata)
    
    def _store_in_chromadb(self, chunks: List[DocumentChunk], document_metadata: Dict[str, Any]):
        """Store chunks in ChromaDB"""
        self.logger.info(f"Storing {len(chunks)} chunks in ChromaDB")
        
        # Flatten document_metadata for ChromaDB (it doesn't support nested dicts)
        flattened_doc_metadata = {}
        for key, value in document_metadata.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                flattened_doc_metadata[f"doc_{key}"] = value
            else:
                # Convert complex types to strings
                flattened_doc_metadata[f"doc_{key}"] = str(value)
        
        for chunk in chunks:
            if chunk.embeddings:
                # Prepare chunk metadata (ensure all values are simple types)
                chunk_metadata = {}
                for key, value in chunk.metadata.items():
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        chunk_metadata[key] = value
                    else:
                        chunk_metadata[key] = str(value)
                
                # Add flattened document metadata
                chunk_metadata.update(flattened_doc_metadata)
                chunk_metadata["chunk_type"] = chunk.chunk_type
                chunk_metadata["section"] = chunk.section
                
                # Store chunk
                self.chunks_collection.add(
                    embeddings=[chunk.embeddings],
                    documents=[chunk.content],
                    metadatas=[chunk_metadata],
                    ids=[chunk.id]
                )
                self.logger.debug(f"Stored chunk {chunk.id} in ChromaDB")
                
                # Store tables separately
                for table in chunk.tables:
                    try:
                        # Handle different table structures
                        if isinstance(table, dict):
                            # Contents-based chunking table structure: {table_id: table_data}
                            if len(table.keys()) == 1 and not any(key in table for key in ['headers', 'row_count', 'dataframe']):
                                table_id = list(table.keys())[0]
                                table_data = table[table_id]
                                
                                if isinstance(table_data, pd.DataFrame):
                                    table_text = table_data.to_json()
                                    headers = list(table_data.columns)
                                    row_count = len(table_data)
                                    column_count = len(table_data.columns)
                                else:
                                    table_text = str(table_data)
                                    headers = []
                                    row_count = 0
                                    column_count = 0
                            
                            # Contents-based chunking with 'dataframe' key
                            elif 'dataframe' in table:
                                table_id = table.get('id', 'unknown_table')
                                table_text = json.dumps({k: v for k, v in table.items() if k != 'dataframe'}, indent=2)
                                headers = table.get('headers', [])
                                row_count = table.get('rows', 0)
                                column_count = table.get('columns', 0)
                                
                                # Add table summary to text content
                                table_summary = f"Table: {', '.join(headers)} with {row_count} rows"
                                table_text += f"\n{table_summary}"
                            
                            # Old semantic chunking table structure
                            elif 'headers' in table and 'row_count' in table:
                                table_id = table.get('table_id', 'legacy_table')
                                table_text = json.dumps(table, indent=2)
                                headers = table.get('headers', [])
                                row_count = table.get('row_count', 0)
                                column_count = table.get('column_count', 0)
                                
                                # Add table summary to text content
                                table_summary = f"Table: {', '.join(headers)} with {row_count} rows"
                                table_text += f"\n{table_summary}"
                            
                            else:
                                # Fallback for unknown structure
                                table_id = f"unknown_table_{hash(str(table))}"
                                table_text = json.dumps(table, indent=2, default=str)
                                headers = []
                                row_count = 0
                                column_count = 0
                        
                        else:
                            # Handle non-dict table structures
                            table_id = f"table_{hash(str(table))}"
                            table_text = str(table)
                            headers = []
                            row_count = 0
                            column_count = 0
                        
                        # Generate embedding for table
                        table_embedding = ollama.embeddings(
                            model=self.ollama_embed_model,
                            prompt=table_text
                        )['embedding']
                        
                        table_metadata = {
                            "chunk_id": chunk.id,
                            "table_id": table_id,
                            "headers": json.dumps(headers) if headers else "[]",
                            "row_count": row_count,
                            "column_count": column_count
                        }
                        # Add flattened document metadata
                        table_metadata.update(flattened_doc_metadata)
                        
                        self.tables_collection.add(
                            embeddings=[table_embedding],
                            documents=[table_text],
                            metadatas=[table_metadata],
                            ids=[f"{chunk.id}_{table_id}"]
                        )
                        self.logger.debug(f"Stored table {table_id} in ChromaDB")
                        
                    except Exception as e:
                        self.logger.error(f"Error storing table in chunk {chunk.id}: {e}")
                        # Continue with next table instead of failing completely
        
        self.logger.info("Successfully stored all chunks in ChromaDB")
    
    def _store_in_postgresql(self, chunks: List[DocumentChunk], document_metadata: Dict[str, Any]):
        """Store chunks in PostgreSQL"""
        try:
            self.logger.info(f"Storing {len(chunks)} chunks in PostgreSQL")
            with self.pg_engine.connect() as conn:
                # Insert document record
                doc_result = conn.execute(text("""
                    INSERT INTO processed_documents 
                    (file_path, file_name, file_size, total_chunks, total_tables, metadata)
                    VALUES (:file_path, :file_name, :file_size, :total_chunks, :total_tables, :metadata)
                    RETURNING id
                """), {
                    "file_path": document_metadata.get("file_path", ""),
                    "file_name": document_metadata.get("file_name", ""),
                    "file_size": document_metadata.get("file_size", 0),
                    "total_chunks": len(chunks),
                    "total_tables": sum(len(chunk.tables) for chunk in chunks),
                    "metadata": json.dumps(document_metadata)
                })
                
                document_id = doc_result.fetchone()[0]
                
                # Insert chunks
                for chunk in chunks:
                    conn.execute(text("""
                        INSERT INTO document_chunks 
                        (document_id, chunk_id, content, chunk_type, section, page_number, metadata)
                        VALUES (:document_id, :chunk_id, :content, :chunk_type, :section, :page_number, :metadata)
                    """), {
                        "document_id": document_id,
                        "chunk_id": chunk.id,
                        "content": chunk.content,
                        "chunk_type": chunk.chunk_type,
                        "section": chunk.section,
                        "page_number": chunk.page_number,
                        "metadata": json.dumps(chunk.metadata)
                    })
                    
                    # Insert tables
                    for table_dict in chunk.tables:
                        table_id = list(table_dict.keys())[0]
                        table = table_dict[table_id]
                        conn.execute(text("""
                            INSERT INTO extracted_tables 
                            (document_id, chunk_id, table_data, table_metadata)
                            VALUES (:document_id, :chunk_id, :table_data, :table_metadata)
                        """), {
                            "document_id": document_id,
                            "chunk_id": chunk.id,
                            "table_data": json.dumps(table, default=str),
                            "table_metadata": json.dumps({
                                "table_id": table_id,
                                "type": str(type(table))
                            })
                        })
                
                conn.commit()
                self.logger.info("Successfully stored all chunks in PostgreSQL")
                
        except Exception as e:
            self.logger.error(f"Error storing chunks in PostgreSQL: {e}")
            raise
    
    def search_chunks(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Search for relevant chunks using semantic similarity"""
        self.logger.info(f"Searching for chunks with query: '{query}' (top_k={top_k})")
        try:
            # Generate query embedding
            query_embedding = ollama.embeddings(
                model=self.ollama_embed_model,
                prompt=query
            )['embedding']
            
            # Search in ChromaDB
            results = self.chunks_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Log search results
            if results and 'documents' in results and results['documents']:
                self.logger.info(f"Found {len(results['documents'])} relevant chunks")
            else:
                self.logger.info("No relevant chunks found")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching chunks: {e}")
            # Return empty structure matching ChromaDB format
            return {
                "documents": [], 
                "metadatas": [], 
                "ids": [],
                "distances": [],
                "embeddings": None,
                "uris": None,
                "data": None,
                "included": []
            }
    
    def is_file_processed_with_strategy(self, pdf_path: str, strategy: str, company_name: str = None, financial_year: str = None) -> bool:
        """Check if a file has been processed with a specific chunking strategy"""
        try:
            file_path = Path(pdf_path).absolute()
            
            # Create unique file ID that includes company and financial year for differentiation
            file_id_parts = [file_path.stem, strategy]
            if company_name:
                file_id_parts.append(company_name.replace(" ", "_"))
            if financial_year:
                file_id_parts.append(financial_year.replace("/", "-").replace(" ", "_"))
            
            file_id = "_".join(file_id_parts)
            
            # Check in ChromaDB processed files collection
            results = self.processed_files_collection.get(
                ids=[file_id]
            )
            
            if results['ids']:
                self.logger.info(f"File {Path(pdf_path).name} already processed with {strategy} strategy for {company_name or 'Unknown'} {financial_year or 'Unknown'}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking processed file status: {e}")
            return False
    
    def mark_file_as_processed(self, pdf_path: str, strategy: str, processing_metadata: Dict[str, Any]):
        """Mark a file as processed with a specific chunking strategy"""
        try:
            file_path = Path(pdf_path).absolute()
            
            # Create unique file ID that includes company and financial year for differentiation
            company_name = processing_metadata.get("company_name")
            financial_year = processing_metadata.get("financial_year")
            
            file_id_parts = [file_path.stem, strategy]
            if company_name:
                file_id_parts.append(company_name.replace(" ", "_"))
            if financial_year:
                file_id_parts.append(financial_year.replace("/", "-").replace(" ", "_"))
            
            file_id = "_".join(file_id_parts)
            
            # Flatten metadata for ChromaDB
            flattened_metadata = {}
            for key, value in processing_metadata.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    flattened_metadata[key] = value
                else:
                    flattened_metadata[key] = str(value)
            
            # Add strategy and file info
            flattened_metadata.update({
                "file_path": str(file_path),
                "file_name": file_path.name,
                "chunking_strategy": strategy,
                "processing_timestamp": self._get_current_timestamp()
            })
            
            # Store in ChromaDB
            self.processed_files_collection.add(
                ids=[file_id],
                documents=[f"Processed {file_path.name} with {strategy} chunking for {company_name or 'Unknown'} {financial_year or 'Unknown'}"],
                metadatas=[flattened_metadata]
            )
            
            self.logger.info(f"Marked file {file_path.name} as processed with {strategy} strategy for {company_name or 'Unknown'} {financial_year or 'Unknown'}")
            
        except Exception as e:
            self.logger.error(f"Error marking file as processed: {e}")
    
    def get_file_processing_info(self, pdf_path: str) -> Dict[str, Any]:
        """Get processing information for a file across all strategies"""
        try:
            file_path = Path(pdf_path).absolute()
            processing_info = {
                "file_path": str(file_path),
                "strategies_processed": [],
                "semantic_processed": False,
                "contents_based_processed": False
            }
            
            # Check for both strategies
            for strategy in ["semantic", "contents_based"]:
                file_id = f"{file_path.stem}_{strategy}"
                
                results = self.processed_files_collection.get(
                    ids=[file_id]
                )
                
                if results['ids']:
                    processing_info["strategies_processed"].append(strategy)
                    processing_info[f"{strategy}_processed"] = True
                    
                    # Add metadata from the first result
                    if results['metadatas']:
                        metadata = results['metadatas'][0]
                        processing_info[f"{strategy}_metadata"] = metadata
            
            return processing_info
            
        except Exception as e:
            self.logger.error(f"Error getting file processing info: {e}")
            return {"error": str(e)}
    
    def get_chunks_by_strategy(self, pdf_path: str, strategy: str, company_name: str = None, financial_year: str = None) -> List[DocumentChunk]:
        """Retrieve existing chunks for a file processed with a specific strategy"""
        try:
            file_path = Path(pdf_path).absolute()
            
            # Build query conditions
            where_conditions = [
                {"doc_file_path": {"$eq": str(file_path)}},
                {"doc_chunking_strategy": {"$eq": strategy}}
            ]
            
            # Add company and financial year filters if provided
            if company_name:
                where_conditions.append({"company_name": {"$eq": company_name}})
            if financial_year:
                where_conditions.append({"financial_year": {"$eq": financial_year}})
            
            # Search for chunks with specific file, strategy, and metadata
            results = self.chunks_collection.get(
                where={"$and": where_conditions}
            )
            
            chunks = []
            if results['ids']:
                for i, chunk_id in enumerate(results['ids']):
                    metadata = results['metadatas'][i] if i < len(results['metadatas']) else {}
                    content = results['documents'][i] if i < len(results['documents']) else ""
                    
                    # Retrieve tables for this chunk - use a comprehensive approach
                    chunk_tables = []
                    try:
                        # Get all tables from the collection and filter by chunk_id prefix
                        # This is the most reliable approach given how tables are stored
                        all_tables = self.tables_collection.get()
                        
                        if all_tables and all_tables.get('ids'):
                            for j, table_full_id in enumerate(all_tables['ids']):
                                # Tables are stored with IDs like "chunk_id_table_id"
                                if table_full_id.startswith(f"{chunk_id}_"):
                                    table_metadata = all_tables['metadatas'][j] if j < len(all_tables['metadatas']) else {}
                                    table_doc = all_tables['documents'][j] if j < len(all_tables['documents']) else ""
                                    
                                    # Extract table_id from full_table_id (remove chunk_id_ prefix)
                                    table_id = table_full_id[len(f"{chunk_id}_"):]
                                    
                                    # Reconstruct table structure to match original format
                                    table_info = {
                                        table_id: table_doc
                                    }
                                    chunk_tables.append(table_info)
                                    
                        self.logger.debug(f"Found {len(chunk_tables)} tables for chunk {chunk_id}")
                                
                    except Exception as table_error:
                        self.logger.warning(f"Error retrieving tables for chunk {chunk_id}: {table_error}")
                        # Continue without tables rather than failing completely
                    
                    # Create chunk object
                    chunk = DocumentChunk(
                        id=chunk_id,
                        content=content,
                        metadata=metadata,
                        tables=chunk_tables,
                        embeddings=None,  # Embeddings stored in ChromaDB
                        chunk_type=metadata.get('chunk_type', 'text'),
                        section=metadata.get('section', ''),
                        page_number=metadata.get('page_number')
                    )
                    chunks.append(chunk)
                
                # Log retrieval stats
                total_tables = sum(len(chunk.tables) for chunk in chunks)
                self.logger.info(f"Retrieved {len(chunks)} chunks with {total_tables} total tables for {Path(pdf_path).name} ({strategy} strategy, {company_name or 'Any'} company, {financial_year or 'Any'} year)")
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Error retrieving chunks by strategy: {e}")
            return []
    
    def create_tables(self):
        """Create PostgreSQL tables for storing processed documents and chunks"""
        if not self.pg_engine:
            return
            
        self.logger.info("Creating PostgreSQL database tables")
        try:
            with self.pg_engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS processed_documents (
                        id SERIAL PRIMARY KEY,
                        file_path VARCHAR(500) UNIQUE NOT NULL,
                        file_name VARCHAR(255) NOT NULL,
                        file_size BIGINT,
                        processing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_chunks INTEGER,
                        total_tables INTEGER,
                        status VARCHAR(50) DEFAULT 'processed',
                        metadata JSONB
                    )
                """))
                
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS document_chunks (
                        id SERIAL PRIMARY KEY,
                        document_id INTEGER REFERENCES processed_documents(id),
                        chunk_id VARCHAR(1000) NOT NULL,
                        content TEXT NOT NULL,
                        chunk_type VARCHAR(50),
                        section VARCHAR(5000),
                        page_number INTEGER,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS extracted_tables (
                        id SERIAL PRIMARY KEY,
                        document_id INTEGER REFERENCES processed_documents(id),
                        chunk_id VARCHAR(1000) NOT NULL,
                        table_data JSONB NOT NULL,
                        table_metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                conn.commit()
                self.logger.info("PostgreSQL database tables created successfully")
        except Exception as e:
            self.logger.error(f"Error creating PostgreSQL tables: {e}")
            raise

    def search_by_company_and_year(self, query: str, company_name: str = None, 
                                  financial_years: List[str] = None, top_k: int = 5) -> Dict[str, Any]:
        """
        Enhanced search that filters by company name and financial years
        
        Args:
            query: Search query text
            company_name: Company name to filter by (optional)
            financial_years: List of financial years to search in (optional)
            top_k: Number of results to return
            
        Returns:
            Dictionary with search results including company and year metadata
        """
        self.logger.info(f"Searching for query: '{query}' | Company: {company_name or 'Any'} | Years: {financial_years or 'Last 10 years'}")
        
        try:
            # Generate query embedding using Ollama
            response = ollama.embeddings(
                model=self.ollama_embed_model,
                prompt=query
            )
            query_embedding = response['embedding']
            
            # Build filter conditions
            where_conditions = []
            
            if company_name:
                where_conditions.append({"company_name": {"$eq": company_name}})
            
            if financial_years:
                # Filter by specific financial years
                year_conditions = [{"financial_year": {"$eq": year}} for year in financial_years]
                if len(year_conditions) == 1:
                    where_conditions.extend(year_conditions)
                else:
                    where_conditions.append({"$or": year_conditions})
            else:
                # Default: search last 10 years (generate common financial year patterns)
                current_year = datetime.now().year
                default_years = []
                for i in range(10):
                    year = current_year - i
                    # Add common financial year formats
                    default_years.extend([
                        f"FY{year}",
                        f"FY{str(year)[-2:]}",
                        f"{year-1}-{str(year)[-2:]}",
                        f"{year-1}-{year}",
                        str(year)
                    ])
                
                year_conditions = [{"financial_year": {"$eq": year}} for year in default_years]
                if year_conditions:
                    where_conditions.append({"$or": year_conditions})
            
            # Perform the search
            if where_conditions:
                if len(where_conditions) == 1:
                    where_clause = where_conditions[0]
                else:
                    where_clause = {"$and": where_conditions}
                
                results = self.chunks_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where_clause
                )
            else:
                # No filters, search all
                results = self.chunks_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
            
            # Format results
            formatted_results = {"chunks": [], "total_results": 0, "search_metadata": {
                "query": query,
                "company_name": company_name,
                "financial_years": financial_years,
                "search_timestamp": self._get_current_timestamp()
            }}
            
            if results and 'documents' in results and results['documents']:
                documents = results['documents'][0] if results['documents'] else []
                metadatas = results['metadatas'][0] if results['metadatas'] else []
                distances = results['distances'][0] if results['distances'] else []
                ids = results['ids'][0] if results['ids'] else []
                
                formatted_results["total_results"] = len(documents)
                for i, doc in enumerate(documents):
                    metadata = metadatas[i] if i < len(metadatas) else {}
                    chunk_result = {
                        'content': doc,
                        'metadata': metadata,
                        'distance': distances[i] if i < len(distances) else 1.0,
                        'id': ids[i] if i < len(ids) else f"chunk_{i}",
                        'company_name': metadata.get('company_name', 'Unknown'),
                        'financial_year': metadata.get('financial_year', 'Unknown'),
                        'section': metadata.get('section', 'Unknown'),
                        'doc_file_name': metadata.get('doc_file_name', 'Unknown')
                    }
                    formatted_results["chunks"].append(chunk_result)
            
            self.logger.info(f"Found {formatted_results['total_results']} relevant chunks")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error in enhanced search: {e}")
            return {
                "chunks": [], 
                "total_results": 0, 
                "error": str(e),
                "search_metadata": {
                    "query": query,
                    "company_name": company_name,
                    "financial_years": financial_years,
                    "search_timestamp": self._get_current_timestamp()
                }
            } 