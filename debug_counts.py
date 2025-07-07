#!/usr/bin/env python3
"""
Debug script to test chunk and table counting for already processed files
"""

from data_processing.main import DataProcessingInterface
import logging

# Enable debug logging 
logging.basicConfig(level=logging.INFO)

def debug_file_processing():
    """Debug file processing counts"""
    
    print("=== Debugging File Processing Counts ===")
    
    # Initialize interface
    interface = DataProcessingInterface()
    
    # Get available PDFs
    pdfs = interface.get_available_pdfs()
    if not pdfs:
        print("No PDFs found in data directories")
        return
    
    pdf_path = str(pdfs[0])
    print(f"Testing with: {pdf_path}")
    
    # Check if file is already processed
    info = interface.processor.get_file_processing_info(pdf_path)
    print(f"File processing info: {info}")
    
    # Check both strategies
    for strategy in ['semantic', 'contents_based']:
        print(f"\n--- Testing {strategy} strategy ---")
        
        if interface.processor.is_file_processed_with_strategy(pdf_path, strategy):
            print(f"✓ File already processed with {strategy}")
            
            # Get chunks directly
            chunks = interface.processor.get_chunks_by_strategy(pdf_path, strategy)
            print(f"Retrieved {len(chunks)} chunks")
            
            if len(chunks) == 0:
                print("ERROR: No chunks retrieved!")
                continue
            
            # Check table counts in detail
            total_tables = 0
            for i, chunk in enumerate(chunks[:5]):  # Show first 5 chunks
                table_count = len(chunk.tables)
                total_tables += table_count
                print(f"  Chunk {i}: '{chunk.id}' - {table_count} tables")
                
                # Show table details if any
                if table_count > 0:
                    for j, table in enumerate(chunk.tables):
                        if isinstance(table, dict):
                            table_keys = list(table.keys())
                            print(f"    Table {j}: {table_keys[0] if table_keys else 'Unknown'}")
                        else:
                            print(f"    Table {j}: {type(table)}")
            
            print(f"Total tables found: {total_tables}")
            
            # Now test process_document with this file to see the actual result
            print(f"\n--- Testing process_document with {strategy} ---")
            result = interface.processor.process_document(pdf_path, strategy)
            print(f"ProcessingResult - Status: {result.status}")
            print(f"ProcessingResult - Chunks: {result.total_chunks}")
            print(f"ProcessingResult - Tables: {result.total_tables}")
            print(f"ProcessingResult - Reused: {result.reused_existing}")
            
        else:
            print(f"✗ File not processed with {strategy}")

if __name__ == "__main__":
    debug_file_processing() 