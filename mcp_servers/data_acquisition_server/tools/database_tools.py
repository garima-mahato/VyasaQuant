"""
MCP Tool: Database Management Tools
Database operations for stock data storage and retrieval using PostgreSQL.
"""

import sys
import os

# Add the project root directory to sys.path to import utils
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "../../../")
sys.path.append(os.path.abspath(project_root))

from utils.database import db_manager
from typing import Dict, Any, Optional, List
import pandas as pd
import logging
import json

logger = logging.getLogger(__name__)

def execute_query(query: str, params: Optional[List] = None) -> Dict[str, Any]:
    """
    Execute a SQL query and return results as a dictionary.
    
    Args:
        query: SQL query string
        params: Optional query parameters
        
    Returns:
        Dictionary containing query results
    """
    try:
        if params is None:
            params = []
        
        result_df = db_manager.execute_query(query, tuple(params))
        
        if result_df is not None and not result_df.empty:
            return {
                "success": True,
                "query": query,
                "records_count": len(result_df),
                "columns": list(result_df.columns),
                "data": result_df.to_dict('records'),
                "message": f"Query executed successfully, returned {len(result_df)} records"
            }
        else:
            return {
                "success": True,
                "query": query,
                "records_count": 0,
                "columns": [],
                "data": [],
                "message": "Query executed successfully, no records returned"
            }
            
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        return {
            "success": False,
            "query": query,
            "records_count": 0,
            "data": [],
            "message": f"Error executing query: {str(e)}"
        }

def get_stock_list() -> Dict[str, Any]:
    """
    Get list of all stocks in the database.
    
    Returns:
        Dictionary containing stock list
    """
    try:
        query = '''
        SELECT stock_symbol, "Stock_Name", "Ticker", "Sector", "Current_Financial_Year", "Sector_PE"
        FROM vq_tbl_stock
        ORDER BY stock_symbol
        '''
        
        result = execute_query(query)
        
        if result["success"]:
            return {
                "success": True,
                "stock_count": result["records_count"],
                "stocks": result["data"],
                "message": f"Retrieved {result['records_count']} stocks from database"
            }
        else:
            return {
                "success": False,
                "stock_count": 0,
                "stocks": [],
                "message": "Failed to retrieve stock list"
            }
            
    except Exception as e:
        logger.error(f"Error getting stock list: {str(e)}")
        return {
            "success": False,
            "stock_count": 0,
            "stocks": [],
            "message": f"Error: {str(e)}"
        }

def get_stock_financial_data(stock_symbol: str) -> Dict[str, Any]:
    """
    Get comprehensive financial data for a specific stock.
    
    Args:
        stock_symbol: Stock symbol to retrieve data for
        
    Returns:
        Dictionary containing financial data
    """
    try:
        results = {
            "success": False,
            "stock_symbol": stock_symbol,
            "data": {}
        }
        
        # Get basic stock information
        basic_query = 'SELECT * FROM vq_tbl_stock WHERE stock_symbol = %s'
        basic_result = execute_query(basic_query, [stock_symbol])
        results["data"]["basic_info"] = basic_result
        
        # Get financial statements
        financial_query = 'SELECT * FROM vq_tbl_financial_statement WHERE stock_symbol = %s ORDER BY "Date" DESC'
        financial_result = execute_query(financial_query, [stock_symbol])
        results["data"]["financial_statements"] = financial_result
        
        # Get income statement
        income_query = 'SELECT * FROM vq_tbl_income_statement WHERE stock_symbol = %s ORDER BY "Date" DESC'
        income_result = execute_query(income_query, [stock_symbol])
        results["data"]["income_statement"] = income_result
        
        # Get balance sheet
        balance_query = 'SELECT * FROM vq_tbl_balance_sheet WHERE stock_symbol = %s ORDER BY "Date" DESC'
        balance_result = execute_query(balance_query, [stock_symbol])
        results["data"]["balance_sheet"] = balance_result
        
        # Get cash flow statement
        cashflow_query = 'SELECT * FROM vq_tbl_cash_flow_statement WHERE stock_symbol = %s ORDER BY "Date" DESC'
        cashflow_result = execute_query(cashflow_query, [stock_symbol])
        results["data"]["cash_flow_statement"] = cashflow_result
        
        # Get intrinsic PE data
        pe_query = 'SELECT * FROM vq_tbl_intrinsic_pe_ratio WHERE stock_symbol = %s ORDER BY financial_year DESC'
        pe_result = execute_query(pe_query, [stock_symbol])
        results["data"]["intrinsic_pe_data"] = pe_result
        
        # Check if any data was found
        successful_queries = sum(1 for data in results["data"].values() if data.get("success", False))
        results["success"] = successful_queries > 0
        results["summary"] = {
            "successful_queries": successful_queries,
            "total_queries": len(results["data"]),
            "data_availability": {
                "basic_info": basic_result.get("records_count", 0) > 0,
                "financial_statements": financial_result.get("records_count", 0) > 0,
                "income_statement": income_result.get("records_count", 0) > 0,
                "balance_sheet": balance_result.get("records_count", 0) > 0,
                "cash_flow_statement": cashflow_result.get("records_count", 0) > 0,
                "intrinsic_pe_data": pe_result.get("records_count", 0) > 0
            }
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting financial data for {stock_symbol}: {str(e)}")
        return {
            "success": False,
            "stock_symbol": stock_symbol,
            "data": {},
            "message": f"Error: {str(e)}"
        }

def get_eps_data(stock_symbol: str, years: int = 4) -> Dict[str, Any]:
    """
    Get EPS data for a specific stock for the last N years.
    
    Args:
        stock_symbol: Stock symbol to retrieve EPS data for
        years: Number of years of EPS data to retrieve
        
    Returns:
        Dictionary containing EPS data
    """
    try:
        # Get EPS data from income statement
        query = '''
        SELECT 
            stock_symbol,
            "Date",
            "Basic EPS" as eps,
            EXTRACT(YEAR FROM "Date") as year
        FROM vq_tbl_income_statement 
        WHERE stock_symbol = %s 
        AND "Basic EPS" IS NOT NULL
        ORDER BY "Date" DESC
        LIMIT %s
        '''
        
        result = execute_query(query, [stock_symbol, years])
        
        if result["success"] and result["records_count"] > 0:
            # Process EPS data
            eps_data = result["data"]
            
            # Calculate EPS growth if we have multiple years
            if len(eps_data) > 1:
                # Sort by year (ascending for growth calculation)
                eps_data.sort(key=lambda x: x["year"])
                
                # Calculate year-over-year growth
                for i in range(1, len(eps_data)):
                    current_eps = eps_data[i]["eps"]
                    previous_eps = eps_data[i-1]["eps"]
                    
                    if previous_eps and previous_eps != 0:
                        growth = ((current_eps - previous_eps) / previous_eps) * 100
                        eps_data[i]["yoy_growth"] = round(growth, 2)
                    else:
                        eps_data[i]["yoy_growth"] = None
                
                # Calculate compound growth rate
                if len(eps_data) >= 2:
                    initial_eps = eps_data[0]["eps"]
                    final_eps = eps_data[-1]["eps"]
                    
                    if initial_eps and initial_eps > 0:
                        years_span = len(eps_data) - 1
                        compound_growth = (((final_eps / initial_eps) ** (1/years_span)) - 1) * 100
                        
                        return {
                            "success": True,
                            "stock_symbol": stock_symbol,
                            "years_requested": years,
                            "years_available": len(eps_data),
                            "eps_data": eps_data,
                            "analysis": {
                                "initial_eps": initial_eps,
                                "final_eps": final_eps,
                                "compound_growth_rate": round(compound_growth, 2),
                                "is_growing": compound_growth > 0,
                                "meets_10_percent_threshold": compound_growth >= 10
                            },
                            "message": f"Retrieved {len(eps_data)} years of EPS data with compound growth rate of {compound_growth:.2f}%"
                        }
                    else:
                        return {
                            "success": True,
                            "stock_symbol": stock_symbol,
                            "years_requested": years,
                            "years_available": len(eps_data),
                            "eps_data": eps_data,
                            "analysis": {
                                "compound_growth_rate": None,
                                "is_growing": False,
                                "meets_10_percent_threshold": False
                            },
                            "message": f"Retrieved {len(eps_data)} years of EPS data but cannot calculate growth due to zero/negative initial EPS"
                        }
            else:
                return {
                    "success": True,
                    "stock_symbol": stock_symbol,
                    "years_requested": years,
                    "years_available": len(eps_data),
                    "eps_data": eps_data,
                    "analysis": {
                        "compound_growth_rate": None,
                        "is_growing": False,
                        "meets_10_percent_threshold": False
                    },
                    "message": f"Retrieved {len(eps_data)} years of EPS data (insufficient for growth calculation)"
                }
        else:
            return {
                "success": False,
                "stock_symbol": stock_symbol,
                "years_requested": years,
                "years_available": 0,
                "eps_data": [],
                "message": f"No EPS data found for {stock_symbol}"
            }
            
    except Exception as e:
        logger.error(f"Error getting EPS data for {stock_symbol}: {str(e)}")
        return {
            "success": False,
            "stock_symbol": stock_symbol,
            "years_requested": years,
            "years_available": 0,
            "eps_data": [],
            "message": f"Error: {str(e)}"
        }

def upsert_stock_data(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insert or update stock data in the database.
    
    Args:
        stock_data: Dictionary containing stock data to upsert
        
    Returns:
        Dictionary containing the result
    """
    try:
        success = db_manager.upsert_stock_data(stock_data)
        
        if success:
            return {
                "success": True,
                "stock_symbol": stock_data.get("stock_symbol"),
                "operation": "upsert",
                "message": "Stock data successfully upserted"
            }
        else:
            return {
                "success": False,
                "stock_symbol": stock_data.get("stock_symbol"),
                "operation": "upsert",
                "message": "Failed to upsert stock data"
            }
            
    except Exception as e:
        logger.error(f"Error upserting stock data: {str(e)}")
        return {
            "success": False,
            "stock_symbol": stock_data.get("stock_symbol"),
            "operation": "upsert",
            "message": f"Error: {str(e)}"
        }

def update_stock_field(stock_symbol: str, field_name: str, value: Any) -> Dict[str, Any]:
    """
    Update a specific field for a stock.
    
    Args:
        stock_symbol: Stock symbol to update
        field_name: Name of the field to update
        value: New value for the field
        
    Returns:
        Dictionary containing the result
    """
    try:
        success = db_manager.update_stock_field(stock_symbol, field_name, value)
        
        if success:
            return {
                "success": True,
                "stock_symbol": stock_symbol,
                "field_name": field_name,
                "new_value": value,
                "message": f"Successfully updated {field_name} for {stock_symbol}"
            }
        else:
            return {
                "success": False,
                "stock_symbol": stock_symbol,
                "field_name": field_name,
                "new_value": value,
                "message": f"Failed to update {field_name} for {stock_symbol}"
            }
            
    except Exception as e:
        logger.error(f"Error updating stock field: {str(e)}")
        return {
            "success": False,
            "stock_symbol": stock_symbol,
            "field_name": field_name,
            "new_value": value,
            "message": f"Error: {str(e)}"
        }

# Tool metadata for MCP server
TOOL_METADATA = {
    "execute_query": {
        "name": "execute_query",
        "description": "Execute a SQL query and return results",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query string to execute"
                },
                "params": {
                    "type": "array",
                    "description": "Optional query parameters",
                    "items": {"type": "string"}
                }
            },
            "required": ["query"]
        }
    },
    "get_stock_list": {
        "name": "get_stock_list",
        "description": "Get list of all stocks in the database",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_stock_financial_data": {
        "name": "get_stock_financial_data",
        "description": "Get comprehensive financial data for a specific stock",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_symbol": {
                    "type": "string",
                    "description": "Stock symbol to retrieve data for"
                }
            },
            "required": ["stock_symbol"]
        }
    },
    "get_eps_data": {
        "name": "get_eps_data",
        "description": "Get EPS data for a specific stock with growth analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_symbol": {
                    "type": "string",
                    "description": "Stock symbol to retrieve EPS data for"
                },
                "years": {
                    "type": "integer",
                    "description": "Number of years of EPS data to retrieve",
                    "default": 4
                }
            },
            "required": ["stock_symbol"]
        }
    },
    "upsert_stock_data": {
        "name": "upsert_stock_data",
        "description": "Insert or update stock data in the database",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_data": {
                    "type": "object",
                    "description": "Dictionary containing stock data to upsert"
                }
            },
            "required": ["stock_data"]
        }
    },
    "update_stock_field": {
        "name": "update_stock_field",
        "description": "Update a specific field for a stock",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_symbol": {
                    "type": "string",
                    "description": "Stock symbol to update"
                },
                "field_name": {
                    "type": "string",
                    "description": "Name of the field to update"
                },
                "value": {
                    "description": "New value for the field"
                }
            },
            "required": ["stock_symbol", "field_name", "value"]
        }
    }
} 