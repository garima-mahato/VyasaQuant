"""
MCP Tool: Download Annual Reports
Downloads annual reports for companies using the data_agent.py functionality.
"""

import sys
import os

# Add the data_acquisition directory to sys.path to import data_agent
current_dir = os.path.dirname(os.path.abspath(__file__))
data_acquisition_dir = os.path.join(current_dir, "../../../data_acquisition")
sys.path.append(os.path.abspath(data_acquisition_dir))

from data_agent import DataAcquisitionAgent
from typing import Dict, Any, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

def download_annual_reports(stock_symbol: str, missing_years: Optional[List[List[int]]] = None) -> Dict[str, Any]:
    """
    Download annual reports for a company from NSE website.
    
    Args:
        stock_symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
        missing_years: Optional list of year ranges [[from_year, to_year], ...] 
                      e.g., [[2020, 2021], [2021, 2022]]
        
    Returns:
        Dictionary containing the result with downloaded PDF paths and metadata
    """
    try:
        # Input validation
        if not stock_symbol or not isinstance(stock_symbol, str):
            return {
                "success": False,
                "error": "Stock symbol must be a non-empty string",
                "pdf_paths": [],
                "stock_symbol": stock_symbol
            }
        
        stock_symbol = stock_symbol.strip().upper()
        if not stock_symbol:
            return {
                "success": False,
                "error": "Stock symbol cannot be empty",
                "pdf_paths": [],
                "stock_symbol": stock_symbol
            }
        
        # Convert missing_years format if provided
        converted_missing_years = None
        if missing_years:
            if not isinstance(missing_years, list):
                return {
                    "success": False,
                    "error": "missing_years must be a list of year ranges",
                    "pdf_paths": [],
                    "stock_symbol": stock_symbol
                }
            
            try:
                # Convert [[from_year, to_year], ...] to [(from_year, to_year), ...]
                converted_missing_years = [tuple(year_range) for year_range in missing_years]
                
                # Validate year ranges
                for year_range in converted_missing_years:
                    if len(year_range) != 2:
                        raise ValueError("Each year range must contain exactly 2 years")
                    if not all(isinstance(y, int) for y in year_range):
                        raise ValueError("Years must be integers")
                    if year_range[0] >= year_range[1]:
                        raise ValueError("From year must be less than to year")
                        
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Invalid missing_years format: {str(e)}. Expected: [[from_year, to_year], ...]",
                    "pdf_paths": [],
                    "stock_symbol": stock_symbol
                }
        
        # Initialize the data acquisition agent
        logger.info(f"Initializing DataAcquisitionAgent for {stock_symbol}")
        agent = DataAcquisitionAgent()
        
        # Download annual reports
        logger.info(f"Downloading annual reports for {stock_symbol}")
        if converted_missing_years:
            logger.info(f"Filtering for missing years: {converted_missing_years}")
        
        pdf_paths = agent.download_annual_reports(stock_symbol, converted_missing_years)
        
        return {
            "success": True,
            "error": None,
            "stock_symbol": stock_symbol,
            "pdf_paths": pdf_paths,
            "downloaded_count": len(pdf_paths),
            "missing_years_filter": converted_missing_years,
            "message": f"Successfully downloaded {len(pdf_paths)} annual reports for {stock_symbol}"
        }
        
    except Exception as e:
        logger.error(f"Error in download_annual_reports tool: {str(e)}")
        return {
            "success": False,
            "error": f"An error occurred while downloading annual reports: {str(e)}",
            "pdf_paths": [],
            "stock_symbol": stock_symbol,
            "downloaded_count": 0
        }

def check_existing_reports(stock_symbol: str) -> Dict[str, Any]:
    """
    Check which annual reports are already downloaded for a company.
    
    Args:
        stock_symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
        
    Returns:
        Dictionary containing information about existing and missing reports
    """
    try:
        # Input validation
        if not stock_symbol or not isinstance(stock_symbol, str):
            return {
                "success": False,
                "error": "Stock symbol must be a non-empty string",
                "missing_years": [],
                "stock_symbol": stock_symbol
            }
        
        stock_symbol = stock_symbol.strip().upper()
        if not stock_symbol:
            return {
                "success": False,
                "error": "Stock symbol cannot be empty",
                "missing_years": [],
                "stock_symbol": stock_symbol
            }
        
        # Initialize the data acquisition agent
        logger.info(f"Checking existing data for {stock_symbol}")
        agent = DataAcquisitionAgent()
        
        # Check existing data
        missing_years = agent.check_existing_data(stock_symbol)
        
        return {
            "success": True,
            "error": None,
            "stock_symbol": stock_symbol,
            "missing_years": [[year_range[0], year_range[1]] for year_range in missing_years],
            "missing_count": len(missing_years),
            "message": f"Found {len(missing_years)} missing year ranges for {stock_symbol}"
        }
        
    except Exception as e:
        logger.error(f"Error in check_existing_reports tool: {str(e)}")
        return {
            "success": False,
            "error": f"An error occurred while checking existing reports: {str(e)}",
            "missing_years": [],
            "stock_symbol": stock_symbol,
            "missing_count": 0
        }

# Tool metadata for MCP server
TOOL_METADATA = {
    "download_annual_reports": {
        "name": "download_annual_reports",
        "description": "Download annual reports for a company from NSE website and store in database",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_symbol": {
                    "type": "string",
                    "description": "Stock symbol (e.g., 'RELIANCE', 'TCS')"
                },
                "missing_years": {
                    "type": "array",
                    "description": "Optional list of year ranges to download [[from_year, to_year], ...] e.g., [[2020, 2021], [2021, 2022]]",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "integer"
                        },
                        "minItems": 2,
                        "maxItems": 2
                    }
                }
            },
            "required": ["stock_symbol"]
        }
    },
    "check_existing_reports": {
        "name": "check_existing_reports",
        "description": "Check which annual reports are already downloaded for a company",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_symbol": {
                    "type": "string",
                    "description": "Stock symbol (e.g., 'RELIANCE', 'TCS')"
                }
            },
            "required": ["stock_symbol"]
        }
    }
} 