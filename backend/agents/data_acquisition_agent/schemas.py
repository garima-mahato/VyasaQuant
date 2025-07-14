"""
Data Acquisition Agent Schemas
Pydantic models for data validation and serialization.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from pydantic import BaseModel, Field


class StockSymbolRequest(BaseModel):
    """Request for stock symbol lookup"""
    company_name: str = Field(..., description="Company name to search for")


class CompanySearchRequest(BaseModel):
    """Request for company search"""
    query: str = Field(..., description="Search query for companies")


class StockDataRequest(BaseModel):
    """Request for stock data"""
    stock_symbol: str = Field(..., description="Stock symbol (e.g., RELIANCE)")
    fetch_complete: bool = Field(default=False, description="Whether to fetch complete data")


class ReportsCheckRequest(BaseModel):
    """Request to check existing reports"""
    stock_symbol: str = Field(..., description="Stock symbol to check")


class ReportsDownloadRequest(BaseModel):
    """Request to download annual reports"""
    stock_symbol: str = Field(..., description="Stock symbol for which to download reports")
    missing_years: Optional[List[Tuple[int, int]]] = Field(
        default=None, 
        description="List of year tuples (from_year, to_year) to download"
    )


class DataAcquisitionRequest(BaseModel):
    """Generic data acquisition request"""
    type: str = Field(..., description="Type of request")
    stock_symbol: Optional[str] = Field(default=None, description="Stock symbol")
    company_name: Optional[str] = Field(default=None, description="Company name")
    query: Optional[str] = Field(default=None, description="Search query")
    missing_years: Optional[List[Tuple[int, int]]] = Field(default=None, description="Missing years")
    additional_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional parameters")


class StockInfo(BaseModel):
    """Stock information structure"""
    symbol: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    current_price: Optional[float] = None


class FinancialData(BaseModel):
    """Financial data structure"""
    stock_symbol: str
    data_type: str  # 'balance_sheet', 'income_statement', 'cash_flow'
    year: int
    data: Dict[str, Any]
    source: str
    extracted_at: datetime


class ReportInfo(BaseModel):
    """Annual report information"""
    stock_symbol: str
    from_year: int
    to_year: int
    file_url: str
    local_path: Optional[str] = None
    is_downloaded: bool = False
    extracted: bool = False


class DataAcquisitionResponse(BaseModel):
    """Response from data acquisition operations"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None 