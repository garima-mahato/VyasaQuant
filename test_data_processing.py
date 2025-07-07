#!/usr/bin/env python3
"""
Test script for the VyasaQuant Data Processing Module

This script demonstrates basic functionality and can be used to verify
that the data_processing module is working correctly.
"""

import asyncio
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("DataProcessingTest")


def test_imports():
    """Test that all required modules can be imported."""
    try:
        from data_processing import (
            DataProcessingInterface,
            FinancialDocumentProcessor,
            EmbeddingProcessor,
            DataLayer,
            ChromaManager,
            PostgresManager,
            DocumentChunk,
            ProcessingResult,
            process_files_programmatically
        )
        logger.info("✅ All imports successful")
        return True
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False


def test_initialization():
    """Test that components can be initialized."""
    try:
        from data_processing import DataProcessingInterface
        
        # Test initialization
        interface = DataProcessingInterface()
        logger.info("✅ DataProcessingInterface initialized successfully")
        
        # Test component access
        processor = interface.processor
        data_layer = interface.data_layer
        embedding_processor = processor.embedding_processor
        
        logger.info("✅ All components accessible")
        return True
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        return False


def test_embedding_info():
    """Test embedding provider information."""
    try:
        from data_processing import EmbeddingProcessor
        
        processor = EmbeddingProcessor()
        info = processor.get_embedding_info()
        
        logger.info(f"✅ Embedding provider: {info['provider']}")
        logger.info(f"   Model: {info['model']}")
        logger.info(f"   Batch size: {info['batch_size']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Embedding info test failed: {e}")
        return False


def test_storage_stats():
    """Test storage statistics."""
    try:
        from data_processing import DataLayer
        
        data_layer = DataLayer()
        stats = data_layer.get_storage_stats()
        
        logger.info("✅ Storage statistics:")
        logger.info(f"   ChromaDB available: {stats['chroma_available']}")
        logger.info(f"   PostgreSQL available: {stats['postgres_available']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Storage stats test failed: {e}")
        return False


def test_document_chunk_schema():
    """Test DocumentChunk schema."""
    try:
        from data_processing import DocumentChunk
        
        # Create a test chunk
        chunk = DocumentChunk(
            id="test_chunk_001",
            content="This is a test chunk content for verification purposes.",
            metadata={"test": True, "source": "test_script"},
            tables=[],
            chunk_type="text",
            section="Test Section",
            page_number=1
        )
        
        # Test properties
        assert chunk.content_length > 0
        assert chunk.table_count == 0
        assert not chunk.has_tables
        assert not chunk.has_embeddings
        
        # Test dictionary conversion
        chunk_dict = chunk.to_dict()
        assert "id" in chunk_dict
        assert "content" in chunk_dict
        
        logger.info("✅ DocumentChunk schema test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ DocumentChunk test failed: {e}")
        return False


def test_processing_result_schema():
    """Test ProcessingResult schema."""
    try:
        from data_processing import ProcessingResult
        
        # Create a test result
        result = ProcessingResult(
            status="success",
            document_path="/test/path/document.pdf",
            processing_strategy="semantic",
            total_chunks=5,
            total_tables=2
        )
        
        # Test properties
        assert result.is_successful
        assert not result.has_errors
        assert result.success_rate == 0.0  # No chunks_summary yet
        
        # Test dictionary conversion
        result_dict = result.to_dict()
        assert "status" in result_dict
        assert "document_path" in result_dict
        
        logger.info("✅ ProcessingResult schema test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ ProcessingResult test failed: {e}")
        return False


async def test_main_interface():
    """Test main interface functionality (without user interaction)."""
    try:
        from data_processing.main import DataProcessingInterface
        
        interface = DataProcessingInterface()
        
        # Test PDF discovery
        available_pdfs = interface.get_available_pdfs()
        logger.info(f"✅ Found {len(available_pdfs)} PDF files in search directories")
        
        # Test system stats
        stats = interface.get_system_stats()
        logger.info("✅ System statistics retrieved")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Main interface test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and provide summary."""
    logger.info("🚀 Starting VyasaQuant Data Processing Module Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Initialization Test", test_initialization),
        ("Embedding Info Test", test_embedding_info),
        ("Storage Stats Test", test_storage_stats),
        ("DocumentChunk Schema Test", test_document_chunk_schema),
        ("ProcessingResult Schema Test", test_processing_result_schema),
        ("Main Interface Test", lambda: asyncio.run(test_main_interface()))
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 Test Summary")
    logger.info(f"✅ Passed: {passed}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        logger.info("\n🎉 All tests passed! The data_processing module is ready to use.")
        logger.info("\nTo use the module:")
        logger.info("1. Set up your environment variables (LLAMA_CLOUD_API_KEY, etc.)")
        logger.info("2. Run: python -m data_processing.main")
        logger.info("3. Or import and use programmatically")
    else:
        logger.info(f"\n⚠️  {failed} test(s) failed. Please check the error messages above.")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 