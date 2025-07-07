# Financial Data Processing API

A comprehensive API for processing and searching financial PDF documents with company name and financial year metadata support.

## 🌟 Key Features

- **Document Processing**: Process multiple PDFs with company and financial year metadata
- **Enhanced Search**: Search documents by company name, financial year, and query text
- **Intelligent Filtering**: Automatic search across last 10 years when no year specified
- **Metadata Management**: Track processing statistics by company and year
- **Dual Storage**: ChromaDB for vector search and PostgreSQL for structured data

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from data_processing import FinancialDataAPI

# Initialize the API
api = FinancialDataAPI()
```

## 📋 Main Functionalities

### 1. Process Financial Documents

Process multiple PDF documents with company and financial year metadata.

#### Method: `process_financial_documents(documents_info, strategy="contents_based")`

**Parameters:**
- `documents_info` (List[Dict]): List of document information dictionaries
- `strategy` (str): Processing strategy - `'contents_based'` or `'semantic'`

**Document Info Structure:**
```python
{
    "pdf_path": "/path/to/document.pdf",     # Required
    "company_name": "Company Name",          # Optional
    "financial_year": "FY2023"              # Optional
}
```

**Example:**
```python
from data_processing import FinancialDataAPI

api = FinancialDataAPI()

documents = [
    {
        "pdf_path": "./data/abc_corp_annual_2023.pdf",
        "company_name": "ABC Corporation",
        "financial_year": "FY2023"
    },
    {
        "pdf_path": "./data/xyz_ltd_quarterly_q3_2023.pdf",
        "company_name": "XYZ Limited",
        "financial_year": "Q3-2023"
    }
]

result = api.process_financial_documents(documents, strategy="contents_based")

print(f"Processed {result['successful']} documents successfully")
print(f"Total chunks: {result['summary']['total_chunks']}")
print(f"Total tables: {result['summary']['total_tables']}")
print(f"Companies: {result['summary']['companies_processed']}")
print(f"Years: {result['summary']['financial_years_processed']}")
```

**Processing Strategies:**

- **`contents_based`** (Recommended): Uses document table of contents for intelligent chunking
- **`semantic`**: Uses AI-based semantic analysis for chunking

### 2. Search Financial Data

Search processed documents by query, company name, and financial years.

#### Method: `search_financial_data(query, company_name=None, financial_years=None, top_k=5)`

**Parameters:**
- `query` (str): Search query text
- `company_name` (str, optional): Filter by specific company name
- `financial_years` (List[str], optional): List of financial years to search
- `top_k` (int): Maximum number of results to return

**Returns:**
```python
{
    "chunks": [
        {
            "content": "Document content...",
            "company_name": "ABC Corp",
            "financial_year": "FY2023",
            "section": "Financial Performance",
            "metadata": {...},
            "distance": 0.25
        }
    ],
    "total_results": 5,
    "search_metadata": {
        "query": "revenue growth",
        "company_name": "ABC Corp",
        "financial_years": ["FY2023"],
        "search_timestamp": "2024-01-15T10:30:00"
    }
}
```

**Examples:**

```python
# Search all companies for revenue data (last 10 years)
results = api.search_financial_data("revenue growth quarterly")

# Search specific company for cash flow data
results = api.search_financial_data(
    query="cash flow from operations",
    company_name="ABC Corporation"
)

# Search specific years across all companies
results = api.search_financial_data(
    query="profit margins EBITDA",
    financial_years=["FY2023", "FY2022", "FY2021"]
)

# Search specific company and years
results = api.search_financial_data(
    query="balance sheet assets liabilities",
    company_name="XYZ Limited",
    financial_years=["FY2023"]
)

# Process results
for chunk in results['chunks']:
    print(f"Company: {chunk['company_name']}")
    print(f"Year: {chunk['financial_year']}")
    print(f"Section: {chunk['section']}")
    print(f"Content: {chunk['content'][:200]}...")
    print("-" * 50)
```

## 🔧 Utility Methods

### Get Processed Companies

```python
companies = api.get_processed_companies()
print(f"Available companies: {companies}")
# Output: ['ABC Corporation', 'XYZ Limited', 'Demo Company A']
```

### Get Processed Financial Years

```python
# All years
years = api.get_processed_years()
print(f"Available years: {years}")

# Years for specific company
company_years = api.get_processed_years("ABC Corporation")
print(f"ABC Corp years: {company_years}")
```

### Get Processing Statistics

```python
stats = api.get_processing_statistics()

print(f"Total companies: {stats['business_metrics']['total_companies']}")
print(f"Total years: {stats['business_metrics']['total_financial_years']}")
print(f"Total chunks: {stats['chromadb_stats']['total_chunks']}")
print(f"Total tables: {stats['chromadb_stats']['total_tables']}")

# Company-year matrix
for company, years in stats['business_metrics']['company_year_matrix'].items():
    print(f"{company}: {years}")
```

## 📝 Convenience Functions

For quick usage without creating an API instance:

```python
from data_processing import process_financial_documents, search_financial_data

# Quick processing
result = process_financial_documents(documents_info, strategy="contents_based")

# Quick search
results = search_financial_data("revenue growth", company_name="ABC Corp")
```

## 🏗️ Financial Year Formats

The API supports various financial year formats:

- `"FY2023"`, `"FY23"`
- `"2022-23"`, `"2022-2023"`
- `"Q1-2023"`, `"Q2-2023"`, `"Q3-2023"`, `"Q4-2023"`
- `"2023"` (calendar year)

## 🔍 Search Intelligence

### Automatic Year Range

When no financial years are specified, the search automatically covers the last 10 years using common formats:
- FY2024, FY2023, FY2022...
- 2023-24, 2022-23, 2021-22...
- 2024, 2023, 2022...

### Company Name Matching

Company names are matched exactly. Ensure consistent naming when processing documents.

## 📊 Use Cases

### 1. Multi-Company Financial Analysis

```python
# Process annual reports for multiple companies
companies_data = [
    {"pdf_path": "./reports/company_a_2023.pdf", "company_name": "Company A", "financial_year": "FY2023"},
    {"pdf_path": "./reports/company_b_2023.pdf", "company_name": "Company B", "financial_year": "FY2023"},
    {"pdf_path": "./reports/company_c_2023.pdf", "company_name": "Company C", "financial_year": "FY2023"},
]

api.process_financial_documents(companies_data)

# Compare revenue growth across companies
for company in ["Company A", "Company B", "Company C"]:
    results = api.search_financial_data(
        query="revenue growth year over year",
        company_name=company,
        financial_years=["FY2023"]
    )
    print(f"{company} revenue data: {len(results['chunks'])} relevant chunks found")
```

### 2. Historical Trend Analysis

```python
# Process multiple years for one company
historical_data = [
    {"pdf_path": "./data/abc_2023.pdf", "company_name": "ABC Corp", "financial_year": "FY2023"},
    {"pdf_path": "./data/abc_2022.pdf", "company_name": "ABC Corp", "financial_year": "FY2022"},
    {"pdf_path": "./data/abc_2021.pdf", "company_name": "ABC Corp", "financial_year": "FY2021"},
]

api.process_financial_documents(historical_data)

# Analyze profit trends over 3 years
results = api.search_financial_data(
    query="net profit margin operating profit",
    company_name="ABC Corp",
    financial_years=["FY2023", "FY2022", "FY2021"]
)
```

### 3. Quarterly Analysis

```python
# Process quarterly reports
quarterly_data = [
    {"pdf_path": "./q1_2023.pdf", "company_name": "Tech Corp", "financial_year": "Q1-2023"},
    {"pdf_path": "./q2_2023.pdf", "company_name": "Tech Corp", "financial_year": "Q2-2023"},
    {"pdf_path": "./q3_2023.pdf", "company_name": "Tech Corp", "financial_year": "Q3-2023"},
    {"pdf_path": "./q4_2023.pdf", "company_name": "Tech Corp", "financial_year": "Q4-2023"},
]

api.process_financial_documents(quarterly_data)

# Search across all quarters
results = api.search_financial_data(
    query="quarterly sales performance",
    company_name="Tech Corp",
    financial_years=["Q1-2023", "Q2-2023", "Q3-2023", "Q4-2023"]
)
```

## 🛠️ Error Handling

```python
try:
    result = api.process_financial_documents(documents_info)
    if result['failed'] > 0:
        print(f"Some documents failed to process: {result['failed']}")
        
    search_results = api.search_financial_data("revenue growth")
    if 'error' in search_results:
        print(f"Search error: {search_results['error']}")
        
except Exception as e:
    print(f"API error: {e}")
```

## 📈 Performance Tips

1. **Use contents_based strategy** for better chunk organization
2. **Be specific with company names** for accurate filtering
3. **Use consistent financial year formats** across documents
4. **Batch process documents** for efficiency
5. **Limit search results** with appropriate `top_k` values

## 🔗 Integration with Other Modules

```python
# Example: Integration with analysis module
from data_processing import FinancialDataAPI
# from your_analysis_module import analyze_financial_data

api = FinancialDataAPI()

# Process documents
api.process_financial_documents(documents_info)

# Search and analyze
results = api.search_financial_data("cash flow analysis")
# analysis_results = analyze_financial_data(results['chunks'])
```

## 📁 Example File Structure

```
project/
├── data/
│   ├── company_a_fy2023.pdf
│   ├── company_a_fy2022.pdf
│   ├── company_b_fy2023.pdf
│   └── quarterly_reports/
│       ├── q1_2023.pdf
│       └── q2_2023.pdf
├── example_financial_api.py
└── your_analysis_script.py
```

This enhanced API provides powerful capabilities for financial document analysis with metadata-aware processing and intelligent search functionality. 