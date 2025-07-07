"""
MCP Tool: Get Ticker Symbol by Company Name
Fetches ticker symbol from the Indian equities database CSV file based on company name.
"""

import sys
import os

# Add the project root directory to sys.path to import utils
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "../../../")
sys.path.append(os.path.abspath(project_root))

from utils.ticker_utils import ticker_manager
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def get_ticker_symbol(company_name: str) -> Dict[str, Any]:
    """
    Get ticker symbol by company name from the Indian equities database.
    
    Args:
        company_name: Name of the company to search for
        
    Returns:
        Dictionary containing the result with ticker symbol and additional info
    """
    try:
        # Input validation
        if not company_name or not isinstance(company_name, str):
            return {
                "success": False,
                "error": "Company name must be a non-empty string",
                "ticker_symbol": None,
                "company_info": None
            }
        
        company_name = company_name.strip()
        if not company_name:
            return {
                "success": False,
                "error": "Company name cannot be empty",
                "ticker_symbol": None,
                "company_info": None
            }
        
        # Search for ticker symbol
        ticker_symbol = ticker_manager.get_symbol_by_name(company_name)
        
        if ticker_symbol:
            # Get full company information
            company_info = ticker_manager.get_company_info(ticker_symbol)
            
            return {
                "success": True,
                "error": None,
                "ticker_symbol": ticker_symbol,
                "company_info": company_info,
                "search_term": company_name
            }
        else:
            # If exact match not found, try to find similar companies
            similar_companies = ticker_manager.search_companies(company_name, limit=5)
            
            return {
                "success": False,
                "error": f"No ticker symbol found for company: {company_name}",
                "ticker_symbol": None,
                "company_info": None,
                "search_term": company_name,
                "similar_companies": similar_companies
            }
            
    except Exception as e:
        logger.error(f"Error in get_ticker_symbol tool: {str(e)}")
        return {
            "success": False,
            "error": f"An error occurred while searching for ticker symbol: {str(e)}",
            "ticker_symbol": None,
            "company_info": None,
            "search_term": company_name
        }

def search_companies(search_term: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for companies by name or ticker symbol.
    
    Args:
        search_term: Term to search for
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing search results
    """
    try:
        if not search_term or not isinstance(search_term, str):
            return {
                "success": False,
                "error": "Search term must be a non-empty string",
                "results": []
            }
        
        search_term = search_term.strip()
        if not search_term:
            return {
                "success": False,
                "error": "Search term cannot be empty",
                "results": []
            }
        
        results = ticker_manager.search_companies(search_term, limit)
        
        return {
            "success": True,
            "error": None,
            "search_term": search_term,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error in search_companies tool: {str(e)}")
        return {
            "success": False,
            "error": f"An error occurred while searching: {str(e)}",
            "results": [],
            "search_term": search_term
        }

# Tool metadata for MCP server
TOOL_METADATA = {
    "get_ticker_symbol": {
        "name": "get_ticker_symbol",
        "description": "Get ticker symbol by company name from Indian equities database",
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Name of the company to search for"
                }
            },
            "required": ["company_name"]
        }
    },
    "search_companies": {
        "name": "search_companies",
        "description": "Search for companies by name or ticker symbol",
        "parameters": {
            "type": "object",
            "properties": {
                "search_term": {
                    "type": "string",
                    "description": "Term to search for in company names or ticker symbols"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10
                }
            },
            "required": ["search_term"]
        }
    }
} 