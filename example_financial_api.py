#!/usr/bin/env python3
"""
Example usage of the Enhanced Financial Data Processing API

This script demonstrates the two main functionalities:
1. Processing multiple PDFs with company name and financial year metadata
2. Searching documents by company name, financial year, and query
"""

from data_processing import FinancialDataAPI, process_financial_documents, search_financial_data
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """Demonstrate the Financial Data API usage"""
    
    print("=== Financial Data Processing API Demo ===\n")
    
    # Initialize the API
    api = FinancialDataAPI()
    
    # Example 1: Process multiple financial documents with metadata
    print("1. Processing Financial Documents with Company & Year Metadata")
    print("=" * 60)
    
    # Sample document information (replace with your actual PDF paths)
    documents_to_process = [
        {
            "pdf_path": "data/AR_22625_HAL_2022_2023.pdf",
            "company_name": "HAL",
            "financial_year": "FY2022"
        },
        {
            "pdf_path": "data/HAL_2023_2024_annual_report.pdf", 
            "company_name": "HAL",
            "financial_year": "FY2023"
        }
    ]
    
    # Filter to only existing files for demo
    existing_documents = []
    data_dir = Path("./data")
    if data_dir.exists():
        available_pdfs = list(data_dir.glob("*.pdf"))
        for i, pdf_path in enumerate(available_pdfs[:2]):  # Use first 3 PDFs for demo
            existing_documents.append({
                "pdf_path": str(pdf_path),
                "company_name": f"HAL",  # Company A, B, C
                "financial_year": f"FY{2023-i}"  # FY2023, FY2022, FY2021
            })
    
    if existing_documents:
        print(f"Processing {len(existing_documents)} documents...")
        
        # Process documents using class method
        result = api.process_financial_documents(
            documents_info=existing_documents,
            strategy="contents_based"
        )
        
        print(f"\nProcessing Results:")
        print(f"  ✅ Successful: {result['successful']}")
        print(f"  ❌ Failed: {result['failed']}")
        print(f"  📊 Total chunks: {result['summary']['total_chunks']}")
        print(f"  📋 Total tables: {result['summary']['total_tables']}")
        print(f"  🏢 Companies: {result['summary']['companies_processed']}")
        print(f"  📅 Years: {result['summary']['financial_years_processed']}")
        
        # Alternative: Use convenience function
        # result = process_financial_documents(existing_documents, "contents_based")
        
    else:
        print("No PDF files found in ./data directory. Skipping processing demo.")
    
    print("\n" + "="*60)
    
    # Example 2: Search financial data with various filters
    print("2. Searching Financial Data")
    print("=" * 30)
    
    # Search examples
    search_examples = [
        {
            "description": "Search all companies for revenue information",
            "query": "revenue growth annual",
            "company_name": None,
            "financial_years": None
        },
        {
            "description": "Search specific company for cash flow data",
            "query": "cash flow operations",
            "company_name": "Demo Company A",
            "financial_years": None
        },
        {
            "description": "Search specific years across all companies",
            "query": "profit margin EBITDA",
            "company_name": None,
            "financial_years": ["FY2023", "FY2022"]
        },
        {
            "description": "Search specific company and year",
            "query": "balance sheet assets",
            "company_name": "Demo Company B",
            "financial_years": ["FY2022"]
        }
    ]
    
    for i, search_config in enumerate(search_examples, 1):
        print(f"\n{i}. {search_config['description']}")
        print("-" * 50)
        
        # Perform search using class method
        search_results = api.search_financial_data(
            query=search_config['query'],
            company_name=search_config['company_name'],
            financial_years=search_config['financial_years'],
            top_k=3
        )
        
        print(f"Query: '{search_config['query']}'")
        print(f"Company: {search_config['company_name'] or 'Any'}")
        print(f"Years: {search_config['financial_years'] or 'Last 10 years'}")
        print(f"Results found: {search_results['total_results']}")
        
        if search_results['chunks']:
            for j, chunk in enumerate(search_results['chunks'][:2], 1):  # Show first 2 results
                print(f"\n  Result {j}:")
                print(f"    Company: {chunk['company_name']}")
                print(f"    Year: {chunk['financial_year']}")
                print(f"    Section: {chunk['section']}")
                print(f"    Content preview: {chunk['content'][:150]}...")
        else:
            print("  No relevant chunks found.")
        
        # Alternative: Use convenience function
        # search_results = search_financial_data(
        #     query=search_config['query'],
        #     company_name=search_config['company_name'],
        #     financial_years=search_config['financial_years']
        # )
    
    print("\n" + "="*60)
    
    # Example 3: Get processing statistics and available data
    print("3. System Statistics and Available Data")
    print("=" * 40)
    
    # Get processed companies
    companies = api.get_processed_companies()
    print(f"Processed companies ({len(companies)}): {companies}")
    
    # Get processed years
    years = api.get_processed_years()
    print(f"Processed years ({len(years)}): {years}")
    
    # Get years for specific company
    if companies:
        company_years = api.get_processed_years(companies[0])
        print(f"Years for '{companies[0]}': {company_years}")
    
    # Get comprehensive statistics
    stats = api.get_processing_statistics()
    if "business_metrics" in stats:
        metrics = stats["business_metrics"]
        print(f"\nBusiness Metrics:")
        print(f"  Total companies: {metrics['total_companies']}")
        print(f"  Total years: {metrics['total_financial_years']}")
        print(f"  Company-year combinations: {len(metrics['company_year_matrix'])}")
    
    print(f"\nDatabase Statistics:")
    if "chromadb_stats" in stats:
        db_stats = stats["chromadb_stats"]
        print(f"  Total chunks: {db_stats['total_chunks']}")
        print(f"  Total tables: {db_stats['total_tables']}")
        print(f"  Processed files: {db_stats['total_processed_files']}")

if __name__ == "__main__":
    main() 