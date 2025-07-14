"""
Data Processing Main Entry Point

This module provides the main interface for the VyasaQuant data processing system,
replicating the functionality of the original llm_pdf_agent.py main function.
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from .processors.financial_processor import FinancialDocumentProcessor
from .schemas.financial_data import ProcessingResult


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def setup_logging():
    """Setup logging configuration"""
    logger = logging.getLogger("VyasaQuant.DataProcessing")
    logger.setLevel(logging.INFO)
    return logger


class DataProcessingInterface:
    """
    Main interface for the VyasaQuant data processing system.
    
    Provides both interactive and programmatic access to document processing capabilities.
    """
    
    def __init__(self):
        """Initialize the data processing interface."""
        self.logger = setup_logging()
        self.logger.info("🤖 VyasaQuant Data Processing System - Initializing")
        
        # Initialize components
        self.processor = FinancialDocumentProcessor()
        
        self.logger.info("✅ Data processing system initialized successfully")
    
    def get_available_pdfs(self) -> List[Path]:
        """Get list of available PDF files in standard locations."""
        available_pdfs = []
        
        # Check data directory
        data_dir = Path("../data")
        if data_dir.exists():
            available_pdfs.extend(data_dir.glob("*.pdf"))
        
        # Check current directory
        current_pdfs = list(Path(".").glob("*.pdf"))
        available_pdfs.extend(current_pdfs)
        
        # Check data folder in current directory
        local_data_dir = Path("./data")
        if local_data_dir.exists():
            available_pdfs.extend(local_data_dir.glob("*.pdf"))
        
        self.logger.info(f"Found {len(available_pdfs)} PDF files in search directories")
        return available_pdfs
    
    def display_file_selection(self, available_pdfs: List[Path]) -> List[str]:
        """Display available files and get user selection."""
        if not available_pdfs:
            print("❌ No PDF files found in data directories")
            print("   Please place PDF files in:")
            print("   - ./data/")
            print("   - ../data/")
            print("   - Current directory")
            return []
        
        print("📁 Available PDF files:")
        for i, pdf_file in enumerate(available_pdfs, 1):
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            
            # Check processing status
            processing_info = self.processor.get_file_processing_info(str(pdf_file))
            
            # Check cache status
            cached = "✅ (cached)" if self.processor.is_file_cached(str(pdf_file)) else "🔄 (needs parsing)"
            
            strategy_status = []
            if processing_info.get("strategies_processed"):
                for strategy in processing_info["strategies_processed"]:
                    if strategy == "semantic":
                        strategy_status.append("🧠 semantic")
                    elif strategy == "contents_based":
                        strategy_status.append("📋 contents")
            
            if strategy_status:
                strategy_info = f" | Processed: {', '.join(strategy_status)}"
            else:
                strategy_info = " | Not processed"
            
            print(f"   {i:2d}. {pdf_file.name} ({size_mb:.1f} MB) {cached}{strategy_info}")
        
        print("\n📝 Selection Options:")
        print("   • Enter numbers (e.g., 1,3,5 or 1-3)")
        print("   • Enter 'all' for all files")
        print("   • Enter 'q' to quit")
        
        while True:
            selection = input("\n➤ Select files: ").strip().lower()
            
            if selection == 'q':
                return []
            elif selection == 'all':
                return [str(pdf) for pdf in available_pdfs]
            
            try:
                selected_files = []
                
                # Parse selection (support ranges and individual numbers)
                for part in selection.split(','):
                    part = part.strip()
                    if '-' in part:
                        # Range like "1-3"
                        start, end = map(int, part.split('-'))
                        for i in range(start, end + 1):
                            if 1 <= i <= len(available_pdfs):
                                selected_files.append(str(available_pdfs[i-1]))
                    else:
                        # Individual number
                        i = int(part)
                        if 1 <= i <= len(available_pdfs):
                            selected_files.append(str(available_pdfs[i-1]))
                
                if selected_files:
                    return selected_files
                else:
                    print("❌ No valid files selected")
                    
            except ValueError:
                print("❌ Invalid selection format. Use numbers, ranges (1-3), or 'all'")
    
    def get_strategy_selection(self) -> str:
        """Get chunking strategy selection from user."""
        print(f"\n🔧 Select Chunking Strategy:")
        print("=" * 30)
        print("1. 📊 Semantic Chunking")
        print("   • Content-based chunking using LLM analysis")
        print("   • Preserves semantic relationships")
        print("   • Good for general-purpose retrieval")
        print("")
        print("2. 📋 Contents-Based Chunking (Recommended)")
        print("   • Structure-aware chunking using table of contents")
        print("   • Section-based organization")
        print("   • Better for document navigation")
        print("   • Preserves document structure")
        print("")
        
        while True:
            strategy_choice = input("➤ Choose strategy (1 or 2): ").strip()
            if strategy_choice == '1':
                print("✅ Selected: Semantic Chunking")
                return "semantic"
            elif strategy_choice == '2':
                print("✅ Selected: Contents-Based Chunking")
                return "contents_based"
            else:
                print("❌ Please enter 1 or 2")
    
    def process_files_interactive(self) -> Dict[str, Any]:
        """Interactive file processing interface."""
        print("🤖 VyasaQuant Data Processing System - Interactive Mode")
        print("=" * 60)
        
        # Get available PDF files
        available_pdfs = self.get_available_pdfs()
        
        # Get user file selection
        selected_files = self.display_file_selection(available_pdfs)
        if not selected_files:
            print("👋 No files selected. Goodbye!")
            return {}
        
        # Get chunking strategy
        strategy = self.get_strategy_selection()
        
        # Process files
        print(f"\n🚀 Starting processing of {len(selected_files)} file(s) with {strategy} chunking...")
        
        if len(selected_files) == 1:
            # Single file processing
            result = self.processor.process_document(selected_files[0], strategy)
            results = {"single_file": True, "result": result.to_dict()}
        else:
            # Multiple files processing
            results = self.processor.process_multiple_documents(selected_files, strategy)
            results["single_file"] = False
        
        # Display results
        self.display_processing_results(results, strategy)
        
        return results
    
    def display_processing_results(self, results: Dict[str, Any], strategy: str):
        """Display processing results to the user."""
        print(f"\n📊 Processing Complete!")
        print("=" * 30)
        
        if results.get("single_file"):
            # Single file results
            result_data = results["result"]
            if result_data["is_successful"]:
                status_msg = "reused" if result_data["reused_existing"] else "processed"
                print(f"✅ Successfully {status_msg}: {Path(result_data['document_path']).name}")
                print(f"   📝 {result_data['total_chunks']} chunks created")
                print(f"   📋 {result_data['total_tables']} tables extracted")
                
                if result_data.get("processing_time"):
                    print(f"   ⏱️  Processing time: {result_data['processing_time']:.2f} seconds")
            else:
                print(f"❌ Failed to process: {result_data.get('errors', ['Unknown error'])[0]}")
        else:
            # Multiple files results
            print(f"📁 Processed {results['total_files']} files using {strategy} chunking:")
            print(f"   ✅ Successful: {results['successful']}")
            print(f"   ❌ Failed: {results['failed']}")
            print(f"   📊 Total chunks: {results['summary']['total_chunks']}")
            print(f"   📋 Total tables: {results['summary']['total_tables']}")
        
        # Strategy benefits
        print(f"\n💡 Strategy Benefits:")
        if strategy == "semantic":
            print("   • Content-aware chunking preserves semantic relationships")
            print("   • Good for general-purpose search and retrieval")
            print("   • Flexible chunk sizes based on content")
        else:
            print("   • Structure-aware chunking follows document organization")
            print("   • Section-based chunks for better navigation")
            print("   • Preserves table-of-contents structure")
            print("   • Better for document analysis and financial data extraction")
    
    def offer_search_functionality(self):
        """Offer search functionality to the user."""
        print(f"\n🔍 Would you like to search the processed content? (y/n): ", end="")
        search_choice = input().strip().lower()
        
        if search_choice in ['y', 'yes']:
            self.interactive_search_session()
    
    def interactive_search_session(self):
        """Interactive search session."""
        print(f"\n🔍 Interactive Search Session")
        print("=" * 30)
        print("Enter search queries to find relevant content from processed documents.")
        print("Type 'quit' or 'exit' to end the search session.")
        print("")
        
        while True:
            query = input("➤ Search query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Search session ended.")
                break
            
            if not query:
                continue
            
            print(f"\n🔍 Searching for: '{query}'")
            print("-" * 40)
            
            try:
                # Perform search
                search_results = self.processor.search_documents(query, top_k=5)
                
                if search_results.get("total_results", 0) > 0:
                    for i, chunk in enumerate(search_results["chunks"], 1):
                        print(f"\n📄 Result {i}:")
                        print(f"   📍 Section: {chunk['metadata'].get('section', 'Unknown')}")
                        print(f"   📄 File: {chunk['metadata'].get('doc_file_name', 'Unknown')}")
                        print(f"   🎯 Similarity: {1 - chunk.get('distance', 1):.3f}")
                        
                        # Show content preview
                        content = chunk['content']
                        preview = content[:200] + "..." if len(content) > 200 else content
                        print(f"   📝 Content: {preview}")
                        
                else:
                    print("❌ No results found. Try different keywords or check if documents are processed.")
                    
            except Exception as e:
                print(f"❌ Search error: {e}")
                self.logger.error(f"Search error: {e}", exc_info=True)
    
    def process_files_programmatically(self, pdf_files: List[str], 
                                     chunking_strategy: str = "contents_based",
                                     enable_search: bool = False,
                                     search_queries: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process files programmatically without user interaction.
        
        Args:
            pdf_files: List of PDF file paths to process
            chunking_strategy: Strategy to use ('semantic' or 'contents_based')
            enable_search: Whether to perform search after processing
            search_queries: Optional list of search queries to execute
            
        Returns:
            Processing results dictionary
        """
        self.logger.info(f"Starting programmatic processing of {len(pdf_files)} files")
        
        try:
            if len(pdf_files) == 1:
                result = self.processor.process_document(pdf_files[0], chunking_strategy)
                results = {
                    "status": "success" if result.is_successful else "error",
                    "single_file": True,
                    "result": result.to_dict(),
                    "search_results": None
                }
            else:
                results = self.processor.process_multiple_documents(pdf_files, chunking_strategy)
                results["status"] = "success" if results["successful"] > 0 else "error"
                results["single_file"] = False
                results["search_results"] = None
            
            # Perform search if requested
            if enable_search and search_queries:
                search_results = {}
                for query in search_queries:
                    search_results[query] = self.processor.search_documents(query, top_k=5)
                results["search_results"] = search_results
            
            self.logger.info("Programmatic processing completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in programmatic processing: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "results": None
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        stats = {
            "processor_stats": self.processor.get_processing_stats()
        }
        return stats


async def main():
    """Main entry point - Interactive mode for processing user-selected PDF files."""
    try:
        # Initialize the data processing interface
        interface = DataProcessingInterface()
        
        # Run interactive processing
        results = interface.process_files_interactive()
        
        if results:
            # Offer search functionality
            interface.offer_search_functionality()
        
        print("\n🎉 Session completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Process interrupted by user. Goodbye!")
    except Exception as e:
        logger = setup_logging()
        logger.error(f"Main function error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


def process_files_programmatically(pdf_files: List[str], 
                                 chunking_strategy: str = "contents_based",
                                 enable_search: bool = False,
                                 search_queries: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Programmatic interface for processing files (equivalent to original function).
    
    Args:
        pdf_files: List of PDF file paths
        chunking_strategy: Processing strategy ('semantic' or 'contents_based')
        enable_search: Whether to enable search after processing
        search_queries: Optional search queries to execute
        
    Returns:
        Dictionary containing processing results
    """
    interface = DataProcessingInterface()
    return interface.process_files_programmatically(
        pdf_files, chunking_strategy, enable_search, search_queries
    )


if __name__ == "__main__":
    asyncio.run(main()) 