# VyasaQuant Data Processing Module

This module provides comprehensive document processing capabilities for financial documents, replacing the functionality of the original `llm_pdf_agent.py`. It offers both interactive and programmatic interfaces for processing PDF documents with advanced chunking strategies and vector embeddings.

## Features

- **PDF Parsing**: Uses LlamaParse for high-quality document parsing
- **Multiple Chunking Strategies**: 
  - Semantic chunking for content-aware segmentation
  - Contents-based chunking using document structure
- **Financial Table Extraction**: Specialized extraction of financial data tables
- **Vector Embeddings**: Support for multiple embedding providers (Ollama, OpenAI, Google)
- **Dual Storage**: ChromaDB for vector search and PostgreSQL for structured queries
- **Interactive Interface**: User-friendly command-line interface
- **Programmatic API**: Easy integration into other applications

## Quick Start

### Interactive Mode

```python
import asyncio
from data_processing.main import main

# Run the interactive interface
asyncio.run(main())
```

### Programmatic Usage

```python
from data_processing import DataProcessingInterface, process_files_programmatically

# Simple programmatic processing
results = process_files_programmatically(
    pdf_files=["path/to/document.pdf"],
    chunking_strategy="contents_based",
    enable_search=True,
    search_queries=["financial performance", "revenue growth"]
)

# Advanced usage with custom interface
interface = DataProcessingInterface()
result = interface.processor.process_document(
    "path/to/document.pdf", 
    strategy="contents_based"
)
```

## Architecture

### Core Components

1. **FinancialDocumentProcessor**: Main processing engine
   - PDF parsing using LlamaParse
   - Document chunking and table extraction
   - Coordination of the processing pipeline

2. **EmbeddingProcessor**: Vector embedding generation
   - Multi-provider support (Ollama, OpenAI, Google)
   - Batch processing for efficiency
   - Query embedding generation for search

3. **DataLayer**: Unified storage interface
   - ChromaDB for vector storage and semantic search
   - PostgreSQL for structured data and analytics
   - Health monitoring and statistics

4. **Schemas**: Type-safe data structures
   - DocumentChunk: Processed document segments
   - ProcessingResult: Processing outcomes and metadata
   - FinancialTable: Extracted financial data
   - SearchResults: Vector search results

### Storage Backends

#### ChromaDB
- Vector embeddings storage
- Semantic similarity search
- Document chunks and tables collections
- Processing status tracking

#### PostgreSQL
- Structured data storage
- Processing history and analytics
- Table data with relational queries
- Performance metrics

## Configuration

Set environment variables for different providers:

```bash
# Required
LLAMA_CLOUD_API_KEY=your_llama_api_key

# Optional - Database
CHROMA_DB_PATH=./chroma_db
POSTGRES_HOST=localhost
POSTGRES_DB=vyasaquant
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Optional - LLM/Embedding providers
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text

# Optional - Processing parameters
MAX_CHUNK_SIZE=4000
CHUNK_OVERLAP=200
EMBEDDING_BATCH_SIZE=10
```

## Processing Strategies

### Semantic Chunking
- Content-aware segmentation using LLM analysis
- Preserves semantic relationships
- Good for general-purpose retrieval
- Flexible chunk sizes based on content

### Contents-Based Chunking (Recommended)
- Structure-aware chunking using table of contents
- Section-based organization
- Better for document navigation
- Preserves document structure
- Optimal for financial documents

## Usage Examples

### Basic Document Processing

```python
from data_processing import FinancialDocumentProcessor

# Initialize processor
processor = FinancialDocumentProcessor()

# Process a single document
result = processor.process_document(
    "annual_report.pdf", 
    strategy="contents_based"
)

if result.is_successful:
    print(f"Processed {result.total_chunks} chunks")
    print(f"Extracted {result.total_tables} tables")
else:
    print(f"Processing failed: {result.errors}")
```

### Batch Processing

```python
# Process multiple documents
pdf_files = ["report1.pdf", "report2.pdf", "report3.pdf"]
results = processor.process_multiple_documents(
    pdf_files, 
    strategy="contents_based"
)

print(f"Successful: {results['successful']}/{results['total_files']}")
```

### Search Functionality

```python
# Search processed documents
search_results = processor.search_documents(
    "revenue growth trends", 
    top_k=5
)

for result in search_results["chunks"]:
    print(f"Section: {result['metadata']['section']}")
    print(f"Content: {result['content'][:200]}...")
    print(f"Similarity: {1 - result['distance']:.3f}")
```

### Storage Management

```python
from data_processing import DataLayer

# Initialize storage layer
data_layer = DataLayer()

# Get storage statistics
stats = data_layer.get_storage_stats()
print(f"Total chunks: {stats['combined_stats']['total_chunks']}")
print(f"Total tables: {stats['combined_stats']['total_tables']}")

# Health check
health = data_layer.health_check()
print(f"System healthy: {health['overall_healthy']}")
```

## Migration from llm_pdf_agent.py

The data_processing module is designed as a drop-in replacement:

### Old Usage
```python
from data_parser_chunker_embedder.llm_pdf_agent import main
asyncio.run(main())
```

### New Usage
```python
from data_processing.main import main
asyncio.run(main())
```

### Programmatic Interface
```python
# Old
from data_parser_chunker_embedder.llm_pdf_agent import process_files_programmatically

# New
from data_processing import process_files_programmatically
```

## Error Handling

The module provides comprehensive error handling:

```python
result = processor.process_document("document.pdf")

if result.status == "error":
    for error in result.errors:
        print(f"Error: {error}")
elif result.status == "partial":
    print(f"Partial success with warnings: {result.warnings}")
else:
    print("Processing successful!")
```

## Performance Considerations

- **Caching**: Parsed documents are cached to avoid re-parsing
- **Batch Processing**: Embeddings are generated in configurable batches
- **Parallel Storage**: Both ChromaDB and PostgreSQL can be used simultaneously
- **Incremental Processing**: Only processes documents that haven't been processed with the selected strategy

## Monitoring and Statistics

```python
# Get comprehensive system statistics
interface = DataProcessingInterface()
stats = interface.get_system_stats()

print("Storage Stats:", stats["storage_stats"])
print("Embedding Info:", stats["embedding_info"])
```

## Troubleshooting

### Common Issues

1. **API Key Missing**: Ensure `LLAMA_CLOUD_API_KEY` is set
2. **Database Connection**: Check PostgreSQL connection parameters
3. **Embedding Provider**: Verify API keys for OpenAI/Google or Ollama availability
4. **File Access**: Ensure PDF files are accessible and not corrupted

### Logs

The module uses structured logging. Set log level:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Dependencies

Key dependencies are automatically managed:
- `llama-parse`: PDF parsing
- `chromadb`: Vector database
- `sqlalchemy`: PostgreSQL interface
- `tiktoken`: Token counting
- `pandas`: Data manipulation
- Provider-specific packages (`openai`, `google-genai`)

This module provides all the functionality of the original `llm_pdf_agent.py` with improved architecture, better error handling, and enhanced usability. 