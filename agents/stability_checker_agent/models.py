from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Stock Stability Analysis Models ---

class StockAnalysisInput(BaseModel):
    company_name: Optional[str] = None
    ticker_symbol: Optional[str] = None
    years_to_analyze: int = Field(default=4, description="Number of years to analyze")

class StockAnalysisOutput(BaseModel):
    success: bool
    company_name: str
    ticker_symbol: str
    passes_to_round_2: bool
    reasoning: str

class TickerLookupInput(BaseModel):
    company_name: str

class TickerLookupOutput(BaseModel):
    ticker_symbol: str
    company_name: str
    exchange: str
    success: bool

class EPSDataInput(BaseModel):
    ticker_symbol: str
    years: List[int]

class EPSDataPoint(BaseModel):
    year: int
    eps_value: float
    source: str
    confidence: float = 0.8

class EPSDataOutput(BaseModel):
    eps_data: List[EPSDataPoint]
    success: bool
    message: str

class GrowthRateInput(BaseModel):
    eps_data: List[EPSDataPoint]

class GrowthRateOutput(BaseModel):
    growth_rate: float
    is_increasing: bool
    passes_stability_check: bool
    reasoning: str

class WebSearchInput(BaseModel):
    query: str
    max_results: int = Field(default=10, description="Maximum number of results to return")

class WebSearchOutput(BaseModel):
    results: List[str]
    success: bool

class FinancialDataInput(BaseModel):
    ticker_symbol: str

class FinancialDataOutput(BaseModel):
    financial_data: Dict[str, Any]
    success: bool
    message: str

class AIAnalysisInput(BaseModel):
    content: str
    analysis_type: str = Field(description="Type of analysis: 'eps_extraction', 'stability_analysis', etc.")

class AIAnalysisOutput(BaseModel):
    analysis_result: Any
    confidence: float
    reasoning: str

# --- Generic Tool Models ---

class PythonCodeInput(BaseModel):
    code: str

class PythonCodeOutput(BaseModel):
    result: str

class ShellCommandInput(BaseModel):
    command: str

class FilePathInput(BaseModel):
    file_path: str

class UrlInput(BaseModel):
    url: str

class MarkdownOutput(BaseModel):
    markdown: str

class EmptyInput(BaseModel):
    pass

# --- Math Models for EPS Calculations ---

class CompoundGrowthInput(BaseModel):
    initial_value: float
    final_value: float
    years: int

class CompoundGrowthOutput(BaseModel):
    growth_rate: float
    calculation_details: str

class PercentageInput(BaseModel):
    value: float
    total: float

class PercentageOutput(BaseModel):
    percentage: float

class AverageInput(BaseModel):
    values: List[float]

class AverageOutput(BaseModel):
    average: float
    count: int

# --- Memory and Search Models ---

class SearchMemoryInput(BaseModel):
    query: str

class MemoryOutput(BaseModel):
    results: List[str]
    count: int

class StockDataSearchInput(BaseModel):
    company_name: str
    data_type: str  # 'eps', 'revenue', 'financials', etc.
    years: List[int]

class StockDataSearchOutput(BaseModel):
    data: List[Dict[str, Any]]
    source: str
    success: bool 