"""
Pydantic models for MCP Tool Response Formats
Defines the expected response structure for all MCP tools in the data acquisition server.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Base response model
class MCPToolResponse(BaseModel):
    """Base response model for all MCP tools"""
    success: bool = Field(description="Whether the operation was successful")
    error: Optional[str] = Field(default=None, description="Error message if operation failed")
    
    class Config:
        extra = "forbid"  # Prevent extra fields

# Ticker symbol response models
class TickerInfo(BaseModel):
    """Information about a ticker symbol"""
    ticker_symbol: str = Field(description="The ticker symbol (e.g., 'HAL.NS')")
    company_name: str = Field(description="Full company name")
    exchange: Optional[str] = Field(default=None, description="Stock exchange")
    sector: Optional[str] = Field(default=None, description="Company sector")
    industry: Optional[str] = Field(default=None, description="Company industry")
    
class TickerSymbolResponse(MCPToolResponse):
    """Response format for get_ticker_symbol tool"""
    ticker_symbol: Optional[str] = Field(default=None, description="The ticker symbol if found")
    company_name: Optional[str] = Field(default=None, description="The company name")
    company_info: Optional[Dict[str, Any]] = Field(default=None, description="Additional company information")

class CompanySearchResponse(MCPToolResponse):
    """Response format for search_companies tool"""
    companies: List[TickerInfo] = Field(default=[], description="List of matching companies")
    total_matches: int = Field(description="Total number of matches found")
    limit_applied: bool = Field(description="Whether results were limited")

# Financial data response models
class FinancialRecord(BaseModel):
    """A single financial record (e.g., income statement entry)"""
    Date: str = Field(description="Date of the financial record")
    # Common financial fields - can be extended
    Revenue: Optional[float] = Field(default=None, description="Revenue/Sales")
    NetIncome: Optional[float] = Field(default=None, description="Net Income")
    BasicEPS: Optional[float] = Field(default=None, description="Basic Earnings Per Share", alias="Basic EPS")
    DilutedEPS: Optional[float] = Field(default=None, description="Diluted Earnings Per Share", alias="Diluted EPS")
    
    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow additional financial fields

class FinancialStatementResponse(MCPToolResponse):
    """Response format for financial statement tools (income, balance, cash flow)"""
    data: List[FinancialRecord] = Field(default=[], description="List of financial records")
    statement_type: str = Field(description="Type of financial statement")
    ticker: str = Field(description="Ticker symbol for the data")
    years_covered: int = Field(description="Number of years of data")

class IncomeStatementResponse(MCPToolResponse):
    """Response format for get_income_statement tool"""
    data: List[Dict[str, Any]] = Field(default=[], description="List of income statement records")
    ticker: str = Field(description="Ticker symbol")
    years_covered: int = Field(description="Number of years of data")

# EPS specific response models
class EPSData(BaseModel):
    """EPS data for multiple years"""
    year: str = Field(description="Year")
    eps: float = Field(description="EPS value for the year")

class EPSResponse(MCPToolResponse):
    """Response format for get_eps_data tool"""
    eps_data: Dict[str, float] = Field(default={}, description="EPS data by year (e.g., {'2021': 30.5, '2022': 35.2})")
    ticker_symbol: str = Field(description="Ticker symbol")
    years_requested: int = Field(description="Number of years requested")
    years_found: int = Field(description="Number of years with data found")

# Stock info response models
class StockInfo(BaseModel):
    """Basic stock information"""
    ticker: str = Field(description="Ticker symbol")
    company_name: str = Field(description="Company name")
    current_price: Optional[float] = Field(default=None, description="Current stock price")
    market_cap: Optional[float] = Field(default=None, description="Market capitalization")
    pe_ratio: Optional[float] = Field(default=None, description="Price-to-earnings ratio")
    
class StockInfoResponse(MCPToolResponse):
    """Response format for get_basic_stock_info tool"""
    stock_info: Optional[StockInfo] = Field(default=None, description="Basic stock information")

# Price history response models
class PriceRecord(BaseModel):
    """A single price record"""
    date: str = Field(description="Date")
    open: Optional[float] = Field(default=None, description="Opening price")
    high: Optional[float] = Field(default=None, description="High price")
    low: Optional[float] = Field(default=None, description="Low price")
    close: Optional[float] = Field(default=None, description="Closing price")
    volume: Optional[int] = Field(default=None, description="Trading volume")

class PriceHistoryResponse(MCPToolResponse):
    """Response format for price history tools"""
    price_data: List[PriceRecord] = Field(default=[], description="List of price records")
    ticker: str = Field(description="Ticker symbol")
    period: str = Field(description="Time period (daily/monthly)")
    records_count: int = Field(description="Number of records returned")

# Database operation response models
class DatabaseOperationResponse(MCPToolResponse):
    """Response format for database operations"""
    affected_rows: int = Field(default=0, description="Number of rows affected")
    operation_type: str = Field(description="Type of database operation")
    
class QueryResponse(MCPToolResponse):
    """Response format for execute_query tool"""
    results: List[Dict[str, Any]] = Field(default=[], description="Query results")
    row_count: int = Field(description="Number of rows returned")
    columns: List[str] = Field(default=[], description="Column names")

# Document/report response models
class ReportInfo(BaseModel):
    """Information about a downloaded report"""
    filename: str = Field(description="Downloaded file name")
    file_size: int = Field(description="File size in bytes")
    download_date: datetime = Field(description="When the report was downloaded")
    
class ReportDownloadResponse(MCPToolResponse):
    """Response format for download_annual_reports tool"""
    downloaded_reports: List[ReportInfo] = Field(default=[], description="List of downloaded reports")
    total_downloads: int = Field(description="Total number of reports downloaded")
    failed_downloads: int = Field(description="Number of failed downloads")

# Tool metadata models
class ToolParameter(BaseModel):
    """Parameter definition for a tool"""
    name: str = Field(description="Parameter name")
    type: str = Field(description="Parameter type")
    description: str = Field(description="Parameter description")
    required: bool = Field(description="Whether parameter is required")
    default: Optional[Any] = Field(default=None, description="Default value if any")

class ToolMetadata(BaseModel):
    """Metadata for a tool including expected response format"""
    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")
    parameters: List[ToolParameter] = Field(description="Tool parameters")
    response_model: str = Field(description="Expected response model class name")
    example_response: Dict[str, Any] = Field(description="Example response")
    
# Response format registry
RESPONSE_MODELS = {
    "get_ticker_symbol": TickerSymbolResponse,
    "search_companies": CompanySearchResponse,
    "get_income_statement": IncomeStatementResponse,
    "get_balance_sheet": FinancialStatementResponse,
    "get_cash_flow_statement": FinancialStatementResponse,
    "get_eps_data": EPSResponse,
    "get_basic_stock_info": StockInfoResponse,
    "get_daily_price_history": PriceHistoryResponse,
    "get_monthly_price_history": PriceHistoryResponse,
    "execute_query": QueryResponse,
    "download_annual_reports": ReportDownloadResponse,
}

def get_response_model(tool_name: str) -> Optional[type]:
    """Get the Pydantic response model for a tool"""
    return RESPONSE_MODELS.get(tool_name)

def get_response_schema(tool_name: str) -> Optional[Dict[str, Any]]:
    """Get the JSON schema for a tool's response format"""
    model = get_response_model(tool_name)
    if model:
        return model.model_json_schema()
    return None

def validate_response(tool_name: str, response: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and serialize a tool response using its Pydantic model"""
    model = get_response_model(tool_name)
    if model:
        try:
            validated = model(**response)
            return validated.model_dump()
        except Exception as e:
            return {
                "success": False,
                "error": f"Response validation failed: {str(e)}",
                "original_response": response
            }
    return response 