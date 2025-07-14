"""
Pytest configuration and shared fixtures for VyasaQuant tests.
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "agents"))
sys.path.append(str(project_root / "data_acquisition"))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "test_vyasaquant",
        "DB_USER": "test_user",
        "DB_PASSWORD": "test_password",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_DB": "test_vyasaquant",
        "POSTGRES_USER": "test_user",
        "POSTGRES_PASSWORD": "test_password",
        "POSTGRES_PORT": "5432",
        "CHROMA_DB_PATH": "./test_chroma_db",
        "LOG_LEVEL": "DEBUG"
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing."""
    return {
        "symbol": "HAL",
        "company_name": "Hindustan Aeronautics Limited",
        "sector": "Aerospace & Defense",
        "current_price": 4850.75,
        "market_cap": 324000000000,
        "pe_ratio": 22.5,
        "dividend_yield": 0.8,
        "beta": 1.3
    }

@pytest.fixture
def sample_financial_statements():
    """Sample financial statements data for testing."""
    return {
        "balance_sheet": {
            "Total Assets": [1000000, 1100000, 1200000],
            "Total Liabilities": [400000, 450000, 500000],
            "Shareholders Equity": [600000, 650000, 700000]
        },
        "income_statement": {
            "Total Revenue": [800000, 850000, 900000],
            "Net Income": [120000, 135000, 150000],
            "EPS": [12.5, 14.2, 16.8]
        },
        "cash_flow": {
            "Operating Cash Flow": [150000, 160000, 170000],
            "Investing Cash Flow": [-50000, -60000, -70000],
            "Financing Cash Flow": [-30000, -35000, -40000]
        }
    }

@pytest.fixture
def mock_yfinance_ticker():
    """Mock yfinance Ticker object for testing."""
    mock_ticker = MagicMock()
    mock_ticker.info = {
        "symbol": "HAL.NS",
        "longName": "Hindustan Aeronautics Limited",
        "sector": "Aerospace & Defense",
        "currentPrice": 4850.75,
        "marketCap": 324000000000,
        "forwardPE": 22.5,
        "dividendYield": 0.008,
        "beta": 1.3,
        "fiftyTwoWeekHigh": 5200.0,
        "fiftyTwoWeekLow": 3800.0
    }
    
    # Mock historical data
    import pandas as pd
    mock_ticker.history.return_value = pd.DataFrame({
        "Open": [4800, 4820, 4840],
        "High": [4950, 4970, 4990],
        "Low": [4790, 4810, 4830],
        "Close": [4830, 4860, 4880],
        "Volume": [500000, 550000, 600000]
    })
    
    return mock_ticker

@pytest.fixture
def mock_mcp_client():
    """Mock MCP client for testing agent communication."""
    mock_client = AsyncMock()
    mock_client.start = AsyncMock()
    mock_client.stop = AsyncMock()
    mock_client.list_tools = AsyncMock(return_value=[
        {"name": "get_ticker_symbol", "description": "Get ticker symbol"},
        {"name": "fetch_and_store_stock_data", "description": "Fetch stock data"},
        {"name": "download_annual_reports", "description": "Download reports"}
    ])
    mock_client.call_tool = AsyncMock(return_value={
        "success": True,
        "result": {"data": "mock_result"}
    })
    return mock_client

@pytest.fixture
def mock_database_manager():
    """Mock database manager for testing."""
    mock_db = MagicMock()
    mock_db.upsert_stock_data.return_value = True
    mock_db.insert_dataframe.return_value = True
    mock_db.update_stock_field.return_value = True
    return mock_db

@pytest.fixture
def sample_annual_reports():
    """Sample annual reports data for testing."""
    return [
        {
            "stock_symbol": "HAL",
            "from_year": 2022,
            "to_year": 2023,
            "file_url": "https://example.com/report1.pdf",
            "local_path": "/path/to/report1.pdf",
            "is_downloaded": True
        },
        {
            "stock_symbol": "HAL",
            "from_year": 2021,
            "to_year": 2022,
            "file_url": "https://example.com/report2.pdf",
            "local_path": "/path/to/report2.pdf",
            "is_downloaded": True
        }
    ]

@pytest.fixture
def sample_ticker_database():
    """Sample ticker database data for testing."""
    return [
        {
            "Symbol": "HAL",
            "Company_Name": "Hindustan Aeronautics Limited",
            "Series": "EQ",
            "Listing_Date": "2018-03-28",
            "ISIN_Number": "INE066F01012"
        },
        {
            "Symbol": "TCS", 
            "Company_Name": "Tata Consultancy Services Limited",
            "Series": "EQ",
            "Listing_Date": "2004-08-25",
            "ISIN_Number": "INE467B01029"
        }
    ]

@pytest.fixture
def mock_nsepython():
    """Mock NSE Python functions for testing."""
    with patch('nsepython.nsefetch') as mock_nsefetch:
        mock_nsefetch.return_value = {
            "data": [
                {
                    "symbol": "HAL",
                    "companyName": "Hindustan Aeronautics Limited",
                    "fromYr": 2022,
                    "toYr": 2023,
                    "fileName": "http://example.com/report.pdf"
                }
            ]
        }
        yield mock_nsefetch

@pytest.fixture
def mock_requests():
    """Mock requests for HTTP calls."""
    with patch('requests.Session') as mock_session:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_response.text = "<html>Mock HTML content</html>"
        
        mock_session.return_value.get.return_value = mock_response
        mock_session.return_value.post.return_value = mock_response
        
        yield mock_session

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup test files after each test."""
    yield
    # Cleanup logic here if needed
    test_files = [
        "test_chroma_db",
        "test_data.csv",
        "test_reports"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path, ignore_errors=True)
            else:
                os.remove(file_path)

class TestConfig:
    """Test configuration constants."""
    TEST_STOCK_SYMBOL = "HAL"
    TEST_COMPANY_NAME = "Hindustan Aeronautics Limited"
    TEST_DB_NAME = "test_vyasaquant"
    TEST_CHROMA_PATH = "./test_chroma_db"
    
    # Test data paths
    FIXTURES_DIR = Path(__file__).parent / "fixtures"
    SAMPLE_DATA_DIR = FIXTURES_DIR / "sample_data" 