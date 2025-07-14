"""
Data Processing Module

A comprehensive financial document processing system that handles PDF parsing, 
chunking, table extraction, and intelligent search with company and financial year filtering.

Main Features:
- PDF document processing with semantic and contents-based chunking
- Company name and financial year metadata support
- Enhanced search capabilities with year-based filtering
- ChromaDB and PostgreSQL storage backends
- Vector embeddings for semantic search

Public API:
- process_financial_documents: Process multiple PDFs with company/year metadata
- search_financial_data: Search documents by company, financial year, and query
"""

from .processors.financial_processor import FinancialDocumentProcessor
from .main import DataProcessingInterface
from .schemas.document_chunk import DocumentChunk
from .schemas.financial_data import ProcessingResult, FinancialTable

# Public API classes
__all__ = [
    'FinancialDocumentProcessor',
    'DataProcessingInterface', 
    'DocumentChunk',
    'ProcessingResult',
    'FinancialTable',
    'FinancialDataAPI'
]

class FinancialDataAPI:
    """
    High-level API for financial document processing and search.
    
    This class provides simplified access to the financial document processing
    capabilities with built-in support for company names and financial years.
    """
    
    def __init__(self):
        """Initialize the Financial Data API"""
        self.processor = FinancialDocumentProcessor()
    
    def process_financial_documents(self, documents_info, strategy="contents_based"):
        """
        Process multiple financial PDF documents with company and year metadata.
        
        Args:
            documents_info (List[Dict]): List of document information dictionaries.
                Each dictionary should contain:
                - pdf_path (str): Path to the PDF file
                - company_name (str, optional): Name of the company
                - financial_year (str, optional): Financial year (e.g., "FY2023", "2022-23")
            
            strategy (str): Processing strategy - 'contents_based' or 'semantic'
                - 'contents_based': Uses document table of contents for chunking
                - 'semantic': Uses AI-based semantic analysis for chunking
        
        Returns:
            Dict: Processing summary with results for each document
        
        Example:
            >>> api = FinancialDataAPI()
            >>> documents = [
            ...     {
            ...         "pdf_path": "/path/to/annual_report_2023.pdf",
            ...         "company_name": "ABC Corp",
            ...         "financial_year": "FY2023"
            ...     },
            ...     {
            ...         "pdf_path": "/path/to/quarterly_report.pdf", 
            ...         "company_name": "XYZ Ltd",
            ...         "financial_year": "Q3-2023"
            ...     }
            ... ]
            >>> result = api.process_financial_documents(documents)
            >>> print(f"Processed {result['successful']} documents successfully")
        """
        return self.processor.process_multiple_documents(documents_info, strategy)
    
    def search_financial_data(self, query, company_name=None, financial_years=None, top_k=5):
        """
        Search financial documents by query, company name, and financial years.
        
        Args:
            query (str): Search query text (e.g., "revenue growth", "cash flow")
            company_name (str, optional): Filter by specific company name
            financial_years (List[str], optional): List of financial years to search in.
                If not provided, searches last 10 years automatically.
                Examples: ["FY2023", "FY2022"] or ["2022-23", "2021-22"]
            top_k (int): Maximum number of results to return (default: 5)
        
        Returns:
            Dict: Search results containing:
                - chunks: List of relevant document chunks
                - total_results: Number of results found
                - search_metadata: Search parameters and timestamp
        
        Example:
            >>> api = FinancialDataAPI()
            >>> 
            >>> # Search all companies for revenue data in last 10 years
            >>> results = api.search_financial_data("revenue growth")
            >>> 
            >>> # Search specific company for cash flow data
            >>> results = api.search_financial_data(
            ...     query="cash flow from operations",
            ...     company_name="ABC Corp"
            ... )
            >>> 
            >>> # Search specific years for multiple companies
            >>> results = api.search_financial_data(
            ...     query="profit margins",
            ...     financial_years=["FY2023", "FY2022", "FY2021"]
            ... )
            >>> 
            >>> for chunk in results['chunks']:
            ...     print(f"Company: {chunk['company_name']}")
            ...     print(f"Year: {chunk['financial_year']}")
            ...     print(f"Content: {chunk['content'][:200]}...")
        """
        return self.processor.search_by_company_and_year(
            query=query,
            company_name=company_name,
            financial_years=financial_years,
            top_k=top_k
        )
    
    def get_processed_companies(self):
        """
        Get list of all companies that have been processed.
        
        Returns:
            List[str]: List of company names in the database
        """
        try:
            # Get all chunks and extract unique company names
            all_chunks = self.processor.chunks_collection.get()
            companies = set()
            
            if all_chunks and all_chunks.get('metadatas'):
                for metadata in all_chunks['metadatas']:
                    company = metadata.get('company_name')
                    if company and company != 'Unknown':
                        companies.add(company)
            
            return sorted(list(companies))
        except Exception as e:
            self.processor.logger.error(f"Error getting processed companies: {e}")
            return []
    
    def get_processed_years(self, company_name=None):
        """
        Get list of financial years that have been processed.
        
        Args:
            company_name (str, optional): Filter by specific company
            
        Returns:
            List[str]: List of financial years in the database
        """
        try:
            # Build query conditions
            where_conditions = []
            if company_name:
                where_conditions.append({"company_name": {"$eq": company_name}})
            
            if where_conditions:
                chunks = self.processor.chunks_collection.get(where={"$and": where_conditions})
            else:
                chunks = self.processor.chunks_collection.get()
            
            years = set()
            if chunks and chunks.get('metadatas'):
                for metadata in chunks['metadatas']:
                    year = metadata.get('financial_year')
                    if year and year != 'Unknown':
                        years.add(year)
            
            return sorted(list(years))
        except Exception as e:
            self.processor.logger.error(f"Error getting processed years: {e}")
            return []
    
    def get_processing_statistics(self):
        """
        Get comprehensive statistics about processed documents.
        
        Returns:
            Dict: Statistics including counts by company, year, etc.
        """
        try:
            stats = self.processor.get_processing_stats()
            
            # Add company and year breakdown
            companies = self.get_processed_companies()
            years = self.get_processed_years()
            
            stats["business_metrics"] = {
                "total_companies": len(companies),
                "total_financial_years": len(years),
                "companies_list": companies,
                "years_list": years,
                "company_year_matrix": {}
            }
            
            # Create company-year matrix
            for company in companies:
                company_years = self.get_processed_years(company)
                stats["business_metrics"]["company_year_matrix"][company] = company_years
            
            return stats
        except Exception as e:
            self.processor.logger.error(f"Error getting processing statistics: {e}")
            return {"error": str(e)}


# Convenience functions for quick access
def process_financial_documents(documents_info, strategy="contents_based"):
    """
    Convenience function to process financial documents.
    
    Args:
        documents_info: List of document info dictionaries
        strategy: Processing strategy ('contents_based' or 'semantic')
    
    Returns:
        Processing results dictionary
    """
    api = FinancialDataAPI()
    return api.process_financial_documents(documents_info, strategy)


def search_financial_data(query, company_name=None, financial_years=None, top_k=5):
    """
    Convenience function to search financial data.
    
    Args:
        query: Search query text
        company_name: Optional company name filter
        financial_years: Optional list of financial years to search
        top_k: Number of results to return
    
    Returns:
        Search results dictionary
    """
    api = FinancialDataAPI()
    return api.search_financial_data(query, company_name, financial_years, top_k) 