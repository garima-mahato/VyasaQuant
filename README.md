# [VyasaQuant](https://huggingface.co/spaces/garima-mahato/vyasaquant)

## Overview
A comprehensive stock analysis system that evaluates Indian stocks through multiple rounds of fundamental analysis to provide buy/sell recommendations based on stability and intrinsic value calculation.

![](https://raw.githubusercontent.com/garima-mahato/VyasaQuant/refs/heads/main/images/web_pg_2.JPG)

## 🏗️ Project Structure

```
VyasaQuant/
├── backend/                 # Python backend with agents and data processing
│   ├── agents/             # Stock analysis agents
│   ├── api/                # FastAPI REST API server
│   ├── config/             # Configuration files
│   ├── data_processing/    # Data processing pipeline
│   ├── mcp_servers/        # MCP server implementations
│   ├── utils/              # Utility functions
│   ├── tests/              # Backend tests
│   ├── start_server.py     # API server startup script
│   └── README.md           # Backend-specific documentation
├── frontend/               # React frontend application
│   ├── src/                # Frontend source code
│   ├── public/             # Static assets
│   └── README.md           # Frontend-specific documentation
├── images/                 # Project images and screenshots
├── README.md               # Main project documentation
├── .gitignore              # Git ignore rules
└── LICENSE                 # Project license
```

## System Architecture

### Core Components
1. **Data Acquisition Agent**
2. **Data Processing & Storage Layer** 
3. **Stability Checker Agent**
4. **Value Analysis Agent**
5. **Recommendation Agent**
6. **API & User Interface**


### Architecture

```mermaid
flowchart TD
    %% Style Definitions (Dark Colors)
    classDef component fill:#1e293b,stroke:#3b82f6,stroke-width:1.5px,color:#ffffff;
    classDef store fill:#3f3f46,stroke:#facc15,stroke-width:1.5px,color:#ffffff;
    classDef activity fill:#111827,stroke:#9ca3af,stroke-dasharray: 5 5,color:#ffffff;

    classDef requestArrow stroke:#3b82f6,stroke-width:2px;
    classDef responseArrow stroke:#ef4444,stroke-width:2px;

    %% Nodes
    U([User]):::activity
    RA([Recommendation Agent]):::component
    DA([Data Acquisition Agent]):::component
    DPL([Data Processing & Storage Layer]):::component
    G[Google]:::store
    NSE[NSE]:::store
    MC[Moneycontrol]:::store
    YF[Yahoo Finance]:::store
    ChromaDB[(ChromaDB)]:::store
    Postgres[(Postgres DB)]:::store
    SC([Stability Checker Agent]):::component
    VA([Value Analysis Agent]):::component

    %% Requests
    U -->|Query to analyze stock| RA:::requestArrow
    RA -->|Fetch data request| DA:::requestArrow
    DA --> G:::requestArrow
    DA --> NSE:::requestArrow
    DA --> MC:::requestArrow
    DA --> YF:::requestArrow
    DA --> ChromaDB:::requestArrow
    DA --> Postgres:::requestArrow
    DA -->|Send raw data| DPL:::requestArrow
    RA -->|Stability check request + data| SC:::requestArrow
    RA -->|Pass - Perform value analysis| VA:::requestArrow

    %% Responses
    DPL -->|Store embeddings & chunks| ChromaDB:::responseArrow
    DPL -->|Store structured data| Postgres:::responseArrow
    DA -->|Send collected data| RA:::responseArrow
    SC -->|Pass/Fail| RA:::responseArrow
    RA -->|Fail - Do not buy + reason| U:::responseArrow
    VA -->|Pass/Fail + reasons| RA:::responseArrow
    RA -->|Final recommendation| U:::responseArrow

```

### Technology Stack
- **Backend**: Python (FastAPI/Flask)
- **Vector Database**: 
  - **Recommended**: ChromaDB (open-source, embedded, easy deployment)
  - ~~**Alternative**: FAISS + SQLite (lightweight, no external dependencies)~~
  - ~~**Enterprise**: Pinecone (managed, scalable, but paid service)~~
- **Structured Data Storage**: 
  - **Primary**: PostgreSQL (robust, supports JSON, excellent for financial data)
  - ~~**Alternative**: SQLite (simple deployment, good for smaller datasets)~~
- **Web Scraping**: BeautifulSoup, Selenium, requests
- **Data Processing**: Pandas, NumPy
- **APIs**: Yahoo Finance, NSE APIs (where available)


## 🚀 Quick Start

### Prerequisites
- **Backend**: Python 3.8+, PostgreSQL
- **Frontend**: Node.js 16+, npm/yarn

### Backend Setup
```bash
cd backend
python -m venv vyasaquant_env
source vyasaquant_env/bin/activate  # Windows: vyasaquant_env\Scripts\activate
pip install -r requirements.txt

# Start the API server
python start_server.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 🎯 Features

### Core Analysis Components
1. **Data Acquisition Agent** - Fetches stock data from multiple sources
2. **Data Processing & Storage** - Cleans and stores data in PostgreSQL/ChromaDB
3. **Stability Checker Agent** - Evaluates stock stability metrics
4. **Value Analysis Agent** - Performs intrinsic value calculations
5. **Recommendation Agent** - Generates buy/sell recommendations
6. **REST API Server** - FastAPI server with automatic documentation
7. **Web Interface** - Modern React-based frontend

### Data Sources
- **NSE** (National Stock Exchange)
- **Yahoo Finance**
- **Moneycontrol**
- **Google Finance**


## 🔧 Development

### Backend Development
```bash
cd backend
# Activate virtual environment
source vyasaquant_env/bin/activate  # Windows: vyasaquant_env\Scripts\activate

# Run API server
python start_server.py

# Or run with uvicorn directly
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest

# Generate test coverage
pytest --cov=.
```

### Frontend Development
```bash
cd frontend
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## 📈 Usage

1. **Start the backend API server** - Handles data processing and analysis
2. **Launch the frontend** - Provides web interface for stock analysis
3. **Enter stock symbol** - Get comprehensive analysis and recommendations
4. **View results** - Detailed stability and value analysis with buy/sell recommendations

### API Endpoints

The backend provides REST endpoints:
- **POST /api/analyze** - Comprehensive stock analysis
- **GET /health** - API health check
- **GET /** - API information
- **GET /docs** - Interactive API documentation

### Example API Usage

```bash
# Analyze a stock
curl -X POST "http://localhost:8000/api/analyze" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "RELIANCE"}'

# Check API health
curl "http://localhost:8000/health"
```

## 🛠️ Configuration

### Backend Configuration
- `backend/config/agents.yaml` - Agent configurations
- `backend/config/servers.yaml` - Server settings
- `backend/config/mcp_config.json` - MCP server config

### Environment Variables
```env
# Backend (.env in backend/)
DATABASE_URL=postgresql://user:password@localhost/vyasaquant
GOOGLE_API_KEY=your_google_api_key
LLAMA_CLOUD_API_KEY=your_llama_api_key

# Frontend (.env in frontend/)
REACT_APP_API_URL=http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

<!-- ## 📝 API Documentation

The backend provides REST endpoints for:
- Stock data retrieval
- Stability analysis
- Value analysis  
- Recommendation generation

**Interactive Documentation**: http://localhost:8000/docs -->

---

## Implementation Plan

## Milestone 1: Data Preparation & Infrastructure 

### 1.1 Data Acquisition Agent

#### Annual Reports Collection
```python
# Key functionalities needed:
- Google Search automation for annual reports
- NSE website scraping for official reports
- PDF parsing and text extraction
- Data validation and verification
```

**Implementation Steps:**
1. **LLM Prompt for Search Strategy**
   - Use Google Custom Search API with queries like: `"[COMPANY_NAME] annual report [YEAR] filetype:pdf site:nse.com"` (MCP Tool)
   - Fallback to company investor relations pages (MCP Tool)
   - Implement retry mechanisms with exponential backoff

2. **PDF Processing**
   - Extract financial tables using `pdfplumber` or `PyPDF2` (MCP Tool)
   - Use LLM for chunking and extracting meaningful data

3. **Data Validation**
   - Cross-reference data from monecontrol and NSE website

#### Market Data Collection
```python
# Data sources and methods:
- Yahoo Finance API for adjusted/unadjusted prices
- NSE website scraping for official prices
- MoneyControl for industry metrics
- Real-time price feeds for CMP
```

### 1.2 Data Processing & Storage Layer: Vector Database Setup

**Recommended Database Architecture:**

**Vector Database (ChromaDB):**
```
Collections:
- annual_reports: {stock_symbol, year, content_chunks, metadata}
- financial_statements: {stock_symbol, year, parsed_data, source_text}
```

**Structured Database (PostgreSQL):**
```sql
CREATE TABLE stocks (
    stock_name VARCHAR(100) NOT NULL,
    nse_code VARCHAR(10) NOT NULL,
    PRIMARY KEY (stock_name, nse_code)
);

CREATE TABLE value_analysis_round1 (
    stock_name VARCHAR(100) NOT NULL,
    nse_code VARCHAR(10) NOT NULL,
    analysis_date DATE,
    eps NUMERIC(10,2),
    current_pe NUMERIC(5,2),
    intrinsic_value NUMERIC(10,2),
    margin_of_safety NUMERIC(5,2),
    PRIMARY KEY (stock_name, nse_code),
    FOREIGN KEY (stock_name, nse_code) REFERENCES stocks(stock_name, nse_code)
);

CREATE TABLE value_analysis_round2 (
    stock_name VARCHAR(100) NOT NULL,
    nse_code VARCHAR(10) NOT NULL,
    analysis_date DATE,
    projected_eps NUMERIC(10,2),
    expected_growth NUMERIC(5,2),
    intrinsic_value NUMERIC(10,2),
    fair_price NUMERIC(10,2),
    PRIMARY KEY (stock_name, nse_code),
    FOREIGN KEY (stock_name, nse_code) REFERENCES stocks(stock_name, nse_code)
);

CREATE TABLE pe_ratio_intrinsic (
    stock_name VARCHAR(100) NOT NULL,
    nse_code VARCHAR(10) NOT NULL,
    eps_ttm NUMERIC(10,2),
    avg_pe NUMERIC(5,2),
    intrinsic_price NUMERIC(10,2),
    calculation_date DATE,
    PRIMARY KEY (stock_name, nse_code),
    FOREIGN KEY (stock_name, nse_code) REFERENCES stocks(stock_name, nse_code)
);

```

**Implementation:**
1. **Document Chunking**: Split annual reports into meaningful sections
2. **Embedding Generation**: Use sentence transformers for semantic search
3. **Metadata Indexing**: Store structured data alongside embeddings

---

## Milestone 2: Round 1 - Stability Check Implementation (Stability Checker Agent) 

### 2.1 EPS Data Extraction & Processing
```
Round-1 (Stability Check):

A) Prompt
1) Fetch the last 4 years of the basic Earnings per share (EPS) of consolidated report. This will be the EPS.
2) Adjust EPS of an year if any stock split or issuance of bonus shares happened that year. Read the instruction section to plan out how to adjust.
3) The EPS across the 10 years must be increasing to consider it as stable.
4) Calculate EPS Growth Rate or EPS-GR = compound growth rate across the 10 year period = (power((EPS of current financial year/EPS of the previous 10th financial year),(1/10))-1)*100
If the current date is in between the current financial year, consider trailing twelve months EPS(EPS-TTM) as the current financial year's EPS
5) If the EPS across the 10 years is increasing and EPS-GR > 10%, then the stock passes the first round of stability check and goes to round 2 for value analysis
6) Otherwise, the stock is rejected.

B) Instructions	for Round 1	
1. EPS Stability Check should ideally be done over atleast a 10 year period.					
2. EPS is heavily impacted by number of outstanding shares of a company. e.g. a 1:5 Stock Split can drastically bring down the EPS in a particular year with no change in company fundamentals.					
3. EPS, therefore, needs to be historically adjusted (manually) for events like Stock Splits, Issue of Bonus Shares etc. 					
4. In such cases, we also need to be careful about Intrinsic P/E calcualtion, since the historic Price as well as EPS needs adjustment.					
5. Read these blog posts: Stock Splits(https://elevate-your-life.blogspot.com/2018/07/what-is-stock-split.html),	Bonus Shares(https://elevate-your-life.blogspot.com/2018/07/what-are-bonus-shares_26.html)		
6. To view adjusted historical prices of any stock, go to Yahoo Finance --> Search for your stock --> Historical Data					
7. To view the un-adjusted historic price of a stock, go to the most trusted source : NSE website(https://www.nseindia.com/) :					
     Select your Stock and then go to Historical Data. Select your date range and get the price for any stock for any day - what it was, without adjustments.					
8. If you find it difficult to adjust the historical EPS of a company for Bonus Shares, Stock Splits etc., then it is prudent to perform the Stability Check on 'Earnings' rather than 'Earnings per Share'.					
9. Stability Check is a relatively subjective critieria. In general, we are looking for a Stock with continiously increasing earnings barring a few justified market exceptions over a 10 year period.					

```

### 2.2 Data Sources Integration

#### NSE Data Scraping
```python
class NSEDataFetcher:
    def __init__(self):
        self.base_url = "https://www.nseindia.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0...',
            'Accept': 'application/json'
        })
    
    def get_historical_prices(self, symbol, start_date, end_date):
        # Implement NSE API calls with proper session management
        pass
    
    def get_corporate_actions(self, symbol):
        # Fetch stock splits, bonus issues, dividends
        pass
```

---

## Milestone 3: Round 2 - Value Analysis Implementation (Value Analysis Agent) 

```
Round-2 (Value Analysis)

A) Prompt
1) Find the industry of the stock
2) Find the current market price(CMP) of the stock
3) Find current date
4) Calclate trailing twelve months average EPS (EPS-TTM) or get it from moneycontrol.com
5) Calculate Current P/E ratio = CMP/EPS-TTM
6) Get Industry P/E ratio of the stock from moneycontrol.com
7) Calculate Intrinsic P/E ratio using the following steps:
	i) For the last 10 financial years, do the following:
		a) For each financial year, get the monthwise price (if available or consider the month-end closing price as the monthwise price) of the stock from moneycontrol.com for each month of the financial year. Then, take average of all these monthwise price to get the Average Price.
		b) Use the EPS of that financial year from previous steps to calculate the P/E ratio = Average Price(calculated in previous step)/EPS of that financial year
		c) In this way, calculate the P/E ratio for each of the last 10 financial years (including current)
	ii) Intrinsic P/E ratio = Average of last 10 years P/E ratio
	iii) Calculate the P/E Growth Rate(P/E-GR) similar to EPS-GR
	iv) Calculate the Best Case P/E = current year's P/E + P/E-GR. If P/E-GR is negative, then Best Case P/E=Intrinsic P/E
8) Calculate Intrinsic Value = Intrinsic P/E ratio * current financial year's EPS
9) Calculate Most Optimistic Value = Best Case P/E ratio * current financial year's EPS
10) Calculate PEG ratio = Intrinsic P/E ratio / EPS-GR
11) If CMP > 1.1*Instrinsic Value and PEG ratio < 1.5, then recommend stock otherwise the stock is rejected.

B) Instructions for Round 2					
1. Month wise price of the Stock can be found in moneycontrol.com and most other financial portals.				
2. As an example for money control, you must search your stock - then visit the section 'Historic Prices & Simple Moving Averages' and then the link --> 'Get Historical Stock Prices'					
3. However, most financial websites would show you adjusted historical prices of stocks after adjustments for Stock Splits, Bonus shares etc. This makes it virtually impossible to find out the un-adjusted historical price.					
4. To fetch the unadjusted Stock Price on any day in the history of the Stock, go to the NSE website. Select your Stock and then go to Historical Data. Select your date range and get the original price for any stock for any day.					
5. NSE India Website (https://www.nseindia.com/)			
6. Industry P/E:  There are no standardized methods of finding Industry P/E for Indian companies. The best (and effort intensive) way is to look at (or calculate) the intrinsic P/E of the top 5-7 companies of the same industry and take their average. 					
Short cut is to rely on financial portals like money control.					

```

### 3.1 Market Data Processing (MCP Tools)

#### Price Data Collection
```python
def collect_historical_prices(stock_symbol, years=10):
    price_data = []
    
    for year in range(current_year - years, current_year + 1):
        # Get monthly prices for each financial year
        monthly_prices = []
        for month in range(4, 16):  # April to March (Indian FY)
            if month > 12:
                month -= 12
                year += 1
            
            price = get_month_end_price(stock_symbol, year, month)
            monthly_prices.append(price)
        
        avg_price = sum(monthly_prices) / len(monthly_prices)
        price_data.append({
            'financial_year': f"FY{year}-{year+1}",
            'average_price': avg_price,
            'monthly_prices': monthly_prices
        })
    
    return price_data
```

#### P/E Calculation Engine
```python
def calculate_intrinsic_pe(stock_symbol, eps_data, price_data):
    pe_ratios = []
    
    for i, (eps_info, price_info) in enumerate(zip(eps_data, price_data)):
        if eps_info['eps'] > 0:  # Avoid division by zero
            pe_ratio = price_info['average_price'] / eps_info['eps']
            pe_ratios.append({
                'year': eps_info['year'],
                'pe_ratio': pe_ratio,
                'eps': eps_info['eps'],
                'avg_price': price_info['average_price']
            })
    
    intrinsic_pe = sum([pe['pe_ratio'] for pe in pe_ratios]) / len(pe_ratios)
    pe_growth_rate = calculate_compound_growth_rate([pe['pe_ratio'] for pe in pe_ratios])
    
    return {
        'intrinsic_pe': intrinsic_pe,
        'pe_growth_rate': pe_growth_rate,
        'historical_pe': pe_ratios
    }
```

### 3.2 Industry Benchmarking

#### Industry P/E Calculation
```python
def calculate_industry_pe(stock_symbol):
    # Method 1: Top companies approach
    industry = identify_industry(stock_symbol)
    top_companies = get_top_companies_in_industry(industry, limit=7)
    
    industry_pe_ratios = []
    for company in top_companies:
        try:
            company_pe = calculate_intrinsic_pe_for_company(company)
            industry_pe_ratios.append(company_pe)
        except Exception as e:
            logger.warning(f"Could not calculate PE for {company}: {e}")
    
    # Method 2: MoneyControl fallback
    if len(industry_pe_ratios) < 3:
        industry_pe = scrape_industry_pe_from_moneycontrol(industry)
        return industry_pe
    
    return sum(industry_pe_ratios) / len(industry_pe_ratios)
```

### 3.3 Valuation Calculations

#### Value Analysis Engine
```python
def perform_value_analysis(stock_symbol, stability_results):
    if not stability_results['passed']:
        return {'passed': False, 'reason': 'Failed stability check'}
    
    # Get current market data
    cmp = get_current_market_price(stock_symbol)
    eps_ttm = calculate_trailing_twelve_months_eps(stock_symbol)
    current_pe = cmp / eps_ttm
    
    # Get industry benchmark
    industry_pe = calculate_industry_pe(stock_symbol)
    
    # Calculate intrinsic metrics
    pe_analysis = calculate_intrinsic_pe(stock_symbol, 
                                        stability_results['eps_data'])
    
    intrinsic_value = pe_analysis['intrinsic_pe'] * eps_ttm
    
    # Calculate optimistic value
    pe_gr = pe_analysis['pe_growth_rate']
    best_case_pe = current_pe + pe_gr if pe_gr > 0 else pe_analysis['intrinsic_pe']
    optimistic_value = best_case_pe * eps_ttm
    
    # Calculate PEG ratio
    eps_gr = stability_results['eps_growth_rate']
    peg_ratio = pe_analysis['intrinsic_pe'] / eps_gr if eps_gr > 0 else float('inf')
    
    # Apply decision criteria - Simple Pass/Fail
    undervalued = cmp <= 1.1 * intrinsic_value
    reasonable_peg = peg_ratio < 1.5
    
    passed_round2 = undervalued and reasonable_peg
    
    return {
        'passed': passed_round2,
        'current_price': cmp,
        'intrinsic_value': intrinsic_value,
        'optimistic_value': optimistic_value,
        'current_pe': current_pe,
        'intrinsic_pe': pe_analysis['intrinsic_pe'],
        'industry_pe': industry_pe,
        'peg_ratio': peg_ratio,
        'undervaluation_margin': (intrinsic_value - cmp) / cmp * 100,
        'criteria_met': {
            'undervalued': undervalued,
            'reasonable_peg': reasonable_peg
        }
    }
```

---

## Milestone 4: Recommendation Agent  and API & User Interface 

### 4.1 Round 3 - Recommendation Agent 

1. Aggregate results from Stability Checker Agent and Value Analysis Agent to give recommendation



### 4.2 REST API Design

#### Endpoint Structure
```python
# FastAPI implementation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Stock Analysis Agent")

class StockAnalysisRequest(BaseModel):
    stock_symbol: str
    force_refresh: bool = False
    include_detailed_report: bool = True

@app.post("/analyze/{stock_symbol}")
async def analyze_stock(stock_symbol: str, request: StockAnalysisRequest):
    try:
        # Generate analysis
        report_data = generate_final_recommendation(stock_symbol)
        
        # Create detailed text report if requested
        if request.include_detailed_report:
            report_data['detailed_text_report'] = create_detailed_report_text(report_data)
        
        return report_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report/{stock_symbol}")
async def get_formatted_report(stock_symbol: str):
    """Get human-readable formatted report"""
    try:
        report_data = generate_final_recommendation(stock_symbol)
        formatted_report = create_detailed_report_text(report_data)
        
        return {
            'stock_symbol': stock_symbol,
            'recommendation': report_data['overall_recommendation'],
            'formatted_report': formatted_report,
            'raw_data': report_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```


---


---

## Implementation Timeline

### Milestone 1 (Weeks 1-2): Infrastructure Setup (15 June 2025)
- Set up development environment, chromadb and postgres setup
- Google Search automation for annual reports
- NSE website scraping for official reports
- PDF parsing and text extraction
- Yahoo Finance API for adjusted/unadjusted prices
- **Document Chunking**: Split annual reports into meaningful sections
- **Embedding Generation**: Use sentence transformers for semantic search
- **Metadata Indexing**: Store structured data alongside embeddings

### Milestone 2 (Weeks 3-4): Round 1 Implementation (29 June 2025)
- Implement EPS extraction and processing
- Build **fully automated** corporate actions detection and adjustment
- Create stability check algorithms with earnings fallback
- Add comprehensive testing and validation

### Milestone 3 (Weeks 5-6): Round 2 Implementation (13 July 2025)
- Build market data collection systems
- Implement P/E calculation engines
- Create industry benchmarking modules
- Add valuation analysis logic with pass/fail criteria

### Milestone 4 (Weeks 7-8): Final System & Reporting & UI Integration (27 July 2025)
- Implement simple pass/fail recommendation engine
- Build comprehensive detailed report generation
- Integrate with UI
- Add final integration testing


---

### ER Diagram of Database

```mermaid
erDiagram
    STOCKS {
        VARCHAR stock_name PK
        VARCHAR nse_code PK
    }

    VALUE_ANALYSIS_ROUND1 {
        VARCHAR stock_name PK, FK
        VARCHAR nse_code PK, FK
        DATE analysis_date
        NUMERIC eps
        NUMERIC current_pe
        NUMERIC intrinsic_value
        NUMERIC margin_of_safety
    }

    VALUE_ANALYSIS_ROUND2 {
        VARCHAR stock_name PK, FK
        VARCHAR nse_code PK, FK
        DATE analysis_date
        NUMERIC projected_eps
        NUMERIC expected_growth
        NUMERIC intrinsic_value
        NUMERIC fair_price
    }

    PE_RATIO_INTRINSIC {
        VARCHAR stock_name PK, FK
        VARCHAR nse_code PK, FK
        NUMERIC eps_ttm
        NUMERIC avg_pe
        NUMERIC intrinsic_price
        DATE calculation_date
    }

    STOCKS ||--o{ VALUE_ANALYSIS_ROUND1 : has
    STOCKS ||--o{ VALUE_ANALYSIS_ROUND2 : has
    STOCKS ||--o{ PE_RATIO_INTRINSIC : has

```

---


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Live Demo**: [VyasaQuant on Hugging Face](https://huggingface.co/spaces/garima-mahato/vyasaquant)
- **API Documentation**: http://localhost:8000/docs (when running locally)
- **Documentation**: See individual README files in `backend/` and `frontend/` directories
- **Issues**: Report bugs and request features via GitHub Issues

## 🙏 Acknowledgments

- Thanks to all data providers (NSE, Yahoo Finance, Moneycontrol)
- Open source community for various libraries and tools used
- Contributors and testers of the system

