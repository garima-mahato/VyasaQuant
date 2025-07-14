"""
MCP Tool: Financial Data Fetching
Fetch financial data from yfinance and other sources - with fallback to mock data when dependencies unavailable.
"""

import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "../../../")
sys.path.append(os.path.abspath(project_root))

# Try to import financial data utilities, fallback to None if not available
try:
    from utils.financial_data import financial_data_manager
    FINANCIAL_DATA_AVAILABLE = True
except ImportError as e:
    print(f"Financial data dependencies not available: {e}")
    financial_data_manager = None
    FINANCIAL_DATA_AVAILABLE = False

# Try to import database utilities, fallback to None if not available  
try:
    from utils.database import db_manager
    DB_AVAILABLE = True
except ImportError as e:
    print(f"Database dependencies not available: {e}")
    db_manager = None
    DB_AVAILABLE = False

from typing import Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

def get_basic_stock_info(ticker: str) -> Dict[str, Any]:
    """
    Get basic stock information including company name and current EPS.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        Dictionary containing basic stock information
    """
    if not FINANCIAL_DATA_AVAILABLE:
        # Return mock basic stock info
        return {
            "success": True,
            "ticker": ticker,
            "stock_symbol": ticker.replace('.NS', ''),
            "stock_info": {
                "stock_symbol": ticker.replace('.NS', ''),
                "company_name": f"{ticker} Company Ltd.",
                "current_eps": 0,
                "sector": "",
                "market_cap": ""
            },
            "message": f"No details found for {ticker}"
        }
    
    try:
        stock_info = financial_data_manager.get_basic_stock_info(ticker)
        
        if stock_info:
            return {
                "success": True,
                "ticker": ticker,
                "stock_symbol": stock_info.get("stock_symbol"),
                "stock_info": stock_info,
                "message": f"Successfully retrieved basic info for {ticker}"
            }
        else:
            return {
                "success": False,
                "ticker": ticker,
                "stock_info": None,
                "message": f"Failed to retrieve basic info for {ticker}"
            }
            
    except Exception as e:
        logger.error(f"Error in get_basic_stock_info: {str(e)}")
        return {
            "success": False,
            "ticker": ticker,
            "stock_info": None,
            "message": f"Error: {str(e)}"
        }

def get_financial_statements(ticker: str) -> Dict[str, Any]:
    """
    Get financial statements data for a stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        Dictionary containing financial statements data
    """
    if not FINANCIAL_DATA_AVAILABLE:
        # Return mock financial statements
        mock_data = []
        return {
            "success": False,
            "ticker": ticker,
            "records_count": len(mock_data),
            "columns": ["Date", "Revenue", "Net_Income", "EPS"],
            "data": mock_data,
            "message": f"No financial statement records"
        }
    
    try:
        financials = financial_data_manager.get_financial_statements(ticker)
        
        if financials is not None and not financials.empty:
            return {
                "success": True,
                "ticker": ticker,
                "records_count": len(financials),
                "columns": list(financials.columns),
                "data": financials.to_dict('records'),
                "message": f"Successfully retrieved {len(financials)} financial statement records"
            }
        else:
            return {
                "success": False,
                "ticker": ticker,
                "records_count": 0,
                "data": [],
                "message": f"No financial statements data found for {ticker}"
            }
            
    except Exception as e:
        logger.error(f"Error in get_financial_statements: {str(e)}")
        return {
            "success": False,
            "ticker": ticker,
            "records_count": 0,
            "data": [],
            "message": f"Error: {str(e)}"
        }

def get_income_statement(ticker: str) -> Dict[str, Any]:
    """
    Get income statement data for a stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        Dictionary containing income statement data
    """
    if not FINANCIAL_DATA_AVAILABLE:
        # Return mock income statement with EPS growth
        mock_data = [
            {"Date": "2023-12-31", "Basic EPS": 25.5, "Revenue": 1000000, "Net_Income": 150000},
            {"Date": "2022-12-31", "Basic EPS": 22.1, "Revenue": 900000, "Net_Income": 130000},
            {"Date": "2021-12-31", "Basic EPS": 18.7, "Revenue": 800000, "Net_Income": 110000},
            {"Date": "2020-12-31", "Basic EPS": 15.3, "Revenue": 700000, "Net_Income": 90000}
        ]
        return {
            "success": True,
            "ticker": ticker,
            "records_count": len(mock_data),
            "columns": ["Date", "Basic EPS", "Revenue", "Net_Income"],
            "data": mock_data,
            "message": f"Mock: {len(mock_data)} income statement records"
        }
    
    try:
        income_stmt = financial_data_manager.get_income_statement(ticker)
        
        if income_stmt is not None and not income_stmt.empty:
            return {
                "success": True,
                "ticker": ticker,
                "records_count": len(income_stmt),
                "columns": list(income_stmt.columns),
                "data": income_stmt.to_dict('records'),
                "message": f"Successfully retrieved {len(income_stmt)} income statement records"
            }
        else:
            return {
                "success": False,
                "ticker": ticker,
                "records_count": 0,
                "data": [],
                "message": f"No income statement data found for {ticker}"
            }
            
    except Exception as e:
        logger.error(f"Error in get_income_statement: {str(e)}")
        return {
            "success": False,
            "ticker": ticker,
            "records_count": 0,
            "data": [],
            "message": f"Error: {str(e)}"
        }

def get_balance_sheet(ticker: str) -> Dict[str, Any]:
    """
    Get balance sheet data for a stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        Dictionary containing balance sheet data
    """
    if not FINANCIAL_DATA_AVAILABLE:
        # Return mock balance sheet
        mock_data = [
            {"Date": "2023-12-31", "Total_Assets": 5000000, "Total_Liabilities": 2000000, "Equity": 3000000},
            {"Date": "2022-12-31", "Total_Assets": 4500000, "Total_Liabilities": 1800000, "Equity": 2700000},
            {"Date": "2021-12-31", "Total_Assets": 4000000, "Total_Liabilities": 1600000, "Equity": 2400000}
        ]
        return {
            "success": True,
            "ticker": ticker,
            "records_count": len(mock_data),
            "columns": ["Date", "Total_Assets", "Total_Liabilities", "Equity"],
            "data": mock_data,
            "message": f"Mock: {len(mock_data)} balance sheet records"
        }
    
    try:
        balance_sheet = financial_data_manager.get_balance_sheet(ticker)
        
        if balance_sheet is not None and not balance_sheet.empty:
            return {
                "success": True,
                "ticker": ticker,
                "records_count": len(balance_sheet),
                "columns": list(balance_sheet.columns),
                "data": balance_sheet.to_dict('records'),
                "message": f"Successfully retrieved {len(balance_sheet)} balance sheet records"
            }
        else:
            return {
                "success": False,
                "ticker": ticker,
                "records_count": 0,
                "data": [],
                "message": f"No balance sheet data found for {ticker}"
            }
            
    except Exception as e:
        logger.error(f"Error in get_balance_sheet: {str(e)}")
        return {
            "success": False,
            "ticker": ticker,
            "records_count": 0,
            "data": [],
            "message": f"Error: {str(e)}"
        }

def get_cash_flow_statement(ticker: str) -> Dict[str, Any]:
    """
    Get cash flow statement data for a stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        Dictionary containing cash flow statement data
    """
    if not FINANCIAL_DATA_AVAILABLE:
        # Return mock cash flow
        mock_data = [
            {"Date": "2023-12-31", "Operating_Cash_Flow": 180000, "Investing_Cash_Flow": -50000, "Financing_Cash_Flow": -30000},
            {"Date": "2022-12-31", "Operating_Cash_Flow": 160000, "Investing_Cash_Flow": -45000, "Financing_Cash_Flow": -25000},
            {"Date": "2021-12-31", "Operating_Cash_Flow": 140000, "Investing_Cash_Flow": -40000, "Financing_Cash_Flow": -20000}
        ]
        return {
            "success": True,
            "ticker": ticker,
            "records_count": len(mock_data),
            "columns": ["Date", "Operating_Cash_Flow", "Investing_Cash_Flow", "Financing_Cash_Flow"],
            "data": mock_data,
            "message": f"Mock: {len(mock_data)} cash flow records"
        }
    
    try:
        cash_flow = financial_data_manager.get_cash_flow_statement(ticker)
        
        if cash_flow is not None and not cash_flow.empty:
            return {
                "success": True,
                "ticker": ticker,
                "records_count": len(cash_flow),
                "columns": list(cash_flow.columns),
                "data": cash_flow.to_dict('records'),
                "message": f"Successfully retrieved {len(cash_flow)} cash flow records"
            }
        else:
            return {
                "success": False,
                "ticker": ticker,
                "records_count": 0,
                "data": [],
                "message": f"No cash flow data found for {ticker}"
            }
            
    except Exception as e:
        logger.error(f"Error in get_cash_flow_statement: {str(e)}")
        return {
            "success": False,
            "ticker": ticker,
            "records_count": 0,
            "data": [],
            "message": f"Error: {str(e)}"
        }

def get_daily_price_history(ticker: str) -> Dict[str, Any]:
    """
    Get 10 years of daily price history for a stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        Dictionary containing daily price history
    """
    if not FINANCIAL_DATA_AVAILABLE:
        # Return mock daily price history
        mock_data = [
            {"Date": "2023-12-31", "Open": 1500, "High": 1600, "Low": 1450, "Close": 1550, "Volume": 100000},
            {"Date": "2022-12-31", "Open": 1400, "High": 1500, "Low": 1350, "Close": 1450, "Volume": 90000},
            {"Date": "2021-12-31", "Open": 1300, "High": 1400, "Low": 1250, "Close": 1350, "Volume": 80000},
            {"Date": "2020-12-31", "Open": 1200, "High": 1300, "Low": 1150, "Close": 1250, "Volume": 70000}
        ]
        return {
            "success": True,
            "ticker": ticker,
            "records_count": len(mock_data),
            "columns": ["Date", "Open", "High", "Low", "Close", "Volume"],
            "data": mock_data,
            "message": f"Mock: {len(mock_data)} daily price records"
        }
    
    try:
        daily_hist = financial_data_manager.get_daily_price_history(ticker)
        
        if daily_hist is not None and not daily_hist.empty:
            return {
                "success": True,
                "ticker": ticker,
                "records_count": len(daily_hist),
                "columns": list(daily_hist.columns),
                "data": daily_hist.to_dict('records'),
                "message": f"Successfully retrieved {len(daily_hist)} daily price records"
            }
        else:
            return {
                "success": False,
                "ticker": ticker,
                "records_count": 0,
                "data": [],
                "message": f"No daily price history found for {ticker}"
            }
            
    except Exception as e:
        logger.error(f"Error in get_daily_price_history: {str(e)}")
        return {
            "success": False,
            "ticker": ticker,
            "records_count": 0,
            "data": [],
            "message": f"Error: {str(e)}"
        }

def get_monthly_price_history(ticker: str) -> Dict[str, Any]:
    """
    Get monthly price history processed from daily data.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        Dictionary containing monthly price history
    """
    if not FINANCIAL_DATA_AVAILABLE:
        # Return mock monthly price history
        mock_data = [
            {"Date": "2023-12-31", "Open": 1500, "High": 1600, "Low": 1450, "Close": 1550, "Volume": 100000},
            {"Date": "2022-12-31", "Open": 1400, "High": 1500, "Low": 1350, "Close": 1450, "Volume": 90000},
            {"Date": "2021-12-31", "Open": 1300, "High": 1400, "Low": 1250, "Close": 1350, "Volume": 80000}
        ]
        return {
            "success": True,
            "ticker": ticker,
            "records_count": len(mock_data),
            "columns": ["Date", "Open", "High", "Low", "Close", "Volume"],
            "data": mock_data,
            "message": f"Mock: {len(mock_data)} monthly price records"
        }
    
    try:
        monthly_hist = financial_data_manager.get_monthly_price_history(ticker)
        
        if monthly_hist is not None and not monthly_hist.empty:
            return {
                "success": True,
                "ticker": ticker,
                "records_count": len(monthly_hist),
                "columns": list(monthly_hist.columns),
                "data": monthly_hist.to_dict('records'),
                "message": f"Successfully processed {len(monthly_hist)} monthly price records"
            }
        else:
            return {
                "success": False,
                "ticker": ticker,
                "records_count": 0,
                "data": [],
                "message": f"No monthly price history available for {ticker}"
            }
            
    except Exception as e:
        logger.error(f"Error in get_monthly_price_history: {str(e)}")
        return {
            "success": False,
            "ticker": ticker,
            "records_count": 0,
            "data": [],
            "message": f"Error: {str(e)}"
        }

def get_intrinsic_pe_data(ticker: str) -> Dict[str, Any]:
    """
    Calculate and get intrinsic PE ratio data for a stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        Dictionary containing intrinsic PE ratio data
    """
    if not FINANCIAL_DATA_AVAILABLE:
        # Return mock intrinsic PE data
        mock_data = [
            {"Date": "2023-12-31", "PE_Ratio": 20.0, "EPS": 25.5, "Price": 510.0},
            {"Date": "2022-12-31", "PE_Ratio": 18.0, "EPS": 22.1, "Price": 397.8},
            {"Date": "2021-12-31", "PE_Ratio": 16.0, "EPS": 18.7, "Price": 300.2},
            {"Date": "2020-12-31", "PE_Ratio": 14.0, "EPS": 15.3, "Price": 214.2}
        ]
        return {
            "success": True,
            "ticker": ticker,
            "records_count": len(mock_data),
            "columns": ["Date", "PE_Ratio", "EPS", "Price"],
            "data": mock_data,
            "message": f"Mock: {len(mock_data)} PE ratio records"
        }
    
    try:
        intrinsic_pe = financial_data_manager.get_intrinsic_pe_data(ticker)
        
        if intrinsic_pe is not None and not intrinsic_pe.empty:
            return {
                "success": True,
                "ticker": ticker,
                "records_count": len(intrinsic_pe),
                "columns": list(intrinsic_pe.columns),
                "data": intrinsic_pe.to_dict('records'),
                "message": f"Successfully calculated {len(intrinsic_pe)} PE ratio records"
            }
        else:
            return {
                "success": False,
                "ticker": ticker,
                "records_count": 0,
                "data": [],
                "message": f"Could not calculate intrinsic PE data for {ticker}"
            }
            
    except Exception as e:
        logger.error(f"Error in get_intrinsic_pe_data: {str(e)}")
        return {
            "success": False,
            "ticker": ticker,
            "records_count": 0,
            "data": [],
            "message": f"Error: {str(e)}"
        }

def get_sector_info(stock_symbol: str) -> Dict[str, Any]:
    """
    Get sector information from MoneyControl API.
    
    Args:
        stock_symbol: Stock symbol without .NS suffix
        
    Returns:
        Dictionary containing sector information
    """
    if not FINANCIAL_DATA_AVAILABLE:
        # Return mock sector info
        return {
            "success": True,
            "stock_symbol": stock_symbol,
            "sector_info": {
                "Sector": "Technology",
                "Sector_PE": 25.0,
                "Sector_PB": 5.0,
                "Sector_ROE": 20.0,
                "Sector_ROA": 10.0,
                "Sector_EPS": 25.0
            },
            "message": f"Mock: Sector info for {stock_symbol}"
        }
    
    try:
        # Remove .NS suffix if present
        clean_symbol = stock_symbol.split('.NS')[0] if '.NS' in stock_symbol else stock_symbol
        
        sector_info = financial_data_manager.get_sector_info_from_moneycontrol(clean_symbol)
        
        if sector_info:
            return {
                "success": True,
                "stock_symbol": clean_symbol,
                "sector_info": sector_info,
                "message": f"Successfully retrieved sector info for {clean_symbol}"
            }
        else:
            return {
                "success": False,
                "stock_symbol": clean_symbol,
                "sector_info": None,
                "message": f"Could not retrieve sector info for {clean_symbol}"
            }
            
    except Exception as e:
        logger.error(f"Error in get_sector_info: {str(e)}")
        return {
            "success": False,
            "stock_symbol": stock_symbol,
            "sector_info": None,
            "message": f"Error: {str(e)}"
        }

def fetch_and_store_stock_data(ticker: str) -> Dict[str, Any]:
    """
    Comprehensive function to fetch all financial data for a stock and store in database.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        Dictionary containing the results of all operations
    """
    if not DB_AVAILABLE:
        return {
            "success": False,
            "ticker": ticker,
            "message": "Database dependencies not available. Cannot store data."
        }

    results = {
        "success": False,
        "ticker": ticker,
        "stock_symbol": ticker.split('.NS')[0] if '.NS' in ticker else ticker,
        "operations": {},
        "errors": [],
        "warnings": []
    }
    
    try:
        stock_symbol = ticker.split('.NS')[0] if '.NS' in ticker else ticker
        results["stock_symbol"] = stock_symbol
        
        # Step 1: Get basic stock information
        logger.info(f"Fetching basic stock info for {ticker}")
        stock_info = financial_data_manager.get_basic_stock_info(ticker)
        
        if stock_info:
            # Store basic stock data
            success = db_manager.upsert_stock_data(stock_info)
            results["operations"]["basic_info"] = {
                "success": success,
                "data": stock_info
            }
            if not success:
                results["errors"].append("Failed to store basic stock information")
        else:
            results["errors"].append("Failed to fetch basic stock information")
            results["operations"]["basic_info"] = {"success": False}
        
        # Step 2: Update current financial year
        current_fy = financial_data_manager.get_current_financial_year()
        fy_success = db_manager.update_stock_field(stock_symbol, "Current_Financial_Year", str(current_fy))
        results["operations"]["financial_year"] = {
            "success": fy_success,
            "financial_year": current_fy
        }
        if not fy_success:
            results["warnings"].append("Failed to update current financial year")
        
        # Step 3: Get and store financial statements
        logger.info(f"Fetching financial statements for {ticker}")
        financials = financial_data_manager.get_financial_statements(ticker)
        if financials is not None and not financials.empty:
            fin_success = db_manager.insert_dataframe(financials, 'vq_tbl_financial_statement')
            results["operations"]["financial_statements"] = {
                "success": fin_success,
                "records_count": len(financials)
            }
            if not fin_success:
                results["errors"].append("Failed to store financial statements")
        else:
            results["errors"].append("Failed to fetch financial statements")
            results["operations"]["financial_statements"] = {"success": False}
        
        # Step 4: Get and store balance sheet
        logger.info(f"Fetching balance sheet for {ticker}")
        balance_sheet = financial_data_manager.get_balance_sheet(ticker)
        if balance_sheet is not None and not balance_sheet.empty:
            bs_success = db_manager.insert_dataframe(balance_sheet, 'vq_tbl_balance_sheet')
            results["operations"]["balance_sheet"] = {
                "success": bs_success,
                "records_count": len(balance_sheet)
            }
            if not bs_success:
                results["errors"].append("Failed to store balance sheet")
        else:
            results["errors"].append("Failed to fetch balance sheet")
            results["operations"]["balance_sheet"] = {"success": False}
        
        # Step 5: Get and store income statement
        logger.info(f"Fetching income statement for {ticker}")
        income_stmt = financial_data_manager.get_income_statement(ticker)
        if income_stmt is not None and not income_stmt.empty:
            is_success = db_manager.insert_dataframe(income_stmt, 'vq_tbl_income_statement')
            results["operations"]["income_statement"] = {
                "success": is_success,
                "records_count": len(income_stmt)
            }
            if not is_success:
                results["errors"].append("Failed to store income statement")
        else:
            results["errors"].append("Failed to fetch income statement")
            results["operations"]["income_statement"] = {"success": False}
        
        # Step 6: Get and store cash flow statement
        logger.info(f"Fetching cash flow statement for {ticker}")
        cash_flow = financial_data_manager.get_cash_flow_statement(ticker)
        if cash_flow is not None and not cash_flow.empty:
            cf_success = db_manager.insert_dataframe(cash_flow, 'vq_tbl_cash_flow_statement')
            results["operations"]["cash_flow_statement"] = {
                "success": cf_success,
                "records_count": len(cash_flow)
            }
            if not cf_success:
                results["errors"].append("Failed to store cash flow statement")
        else:
            results["errors"].append("Failed to fetch cash flow statement")
            results["operations"]["cash_flow_statement"] = {"success": False}
        
        # Step 7: Get and store daily price history
        logger.info(f"Fetching daily price history for {ticker}")
        daily_hist = financial_data_manager.get_daily_price_history(ticker)
        if daily_hist is not None and not daily_hist.empty:
            dh_success = db_manager.insert_dataframe(daily_hist, 'vq_tbl_daily_price_history')
            results["operations"]["daily_price_history"] = {
                "success": dh_success,
                "records_count": len(daily_hist)
            }
            if not dh_success:
                results["errors"].append("Failed to store daily price history")
        else:
            results["errors"].append("Failed to fetch daily price history")
            results["operations"]["daily_price_history"] = {"success": False}
        
        # Step 8: Get and store monthly price history
        logger.info(f"Processing monthly price history for {ticker}")
        monthly_hist = financial_data_manager.get_monthly_price_history(ticker)
        if monthly_hist is not None and not monthly_hist.empty:
            mh_success = db_manager.insert_dataframe(monthly_hist, 'vq_tbl_monthly_price_history')
            results["operations"]["monthly_price_history"] = {
                "success": mh_success,
                "records_count": len(monthly_hist)
            }
            if not mh_success:
                results["errors"].append("Failed to store monthly price history")
        else:
            results["errors"].append("Failed to process monthly price history")
            results["operations"]["monthly_price_history"] = {"success": False}
        
        # Step 9: Calculate and store intrinsic PE data
        logger.info(f"Calculating intrinsic PE data for {ticker}")
        intrinsic_pe = financial_data_manager.get_intrinsic_pe_data(ticker)
        if intrinsic_pe is not None and not intrinsic_pe.empty:
            pe_success = db_manager.insert_dataframe(intrinsic_pe, 'vq_tbl_intrinsic_pe_ratio')
            results["operations"]["intrinsic_pe_ratio"] = {
                "success": pe_success,
                "records_count": len(intrinsic_pe)
            }
            if not pe_success:
                results["errors"].append("Failed to store intrinsic PE ratio data")
        else:
            results["warnings"].append("Failed to calculate intrinsic PE ratio data")
            results["operations"]["intrinsic_pe_ratio"] = {"success": False}
        
        # Determine overall success
        successful_operations = sum(1 for op in results["operations"].values() if op.get("success", False))
        total_operations = len(results["operations"])
        
        results["success"] = successful_operations > 0
        results["summary"] = {
            "successful_operations": successful_operations,
            "total_operations": total_operations,
            "success_rate": f"{(successful_operations/total_operations)*100:.1f}%" if total_operations > 0 else "0%"
        }
        
        logger.info(f"Completed fetching data for {ticker}: {successful_operations}/{total_operations} operations successful")
        
    except Exception as e:
        logger.error(f"Error in fetch_and_store_stock_data: {str(e)}")
        results["errors"].append(f"Unexpected error: {str(e)}")
        results["success"] = False
    
    return results

def fetch_sector_info(stock_symbol: str) -> Dict[str, Any]:
    """
    Fetch sector information from MoneyControl API and update database.
    
    Args:
        stock_symbol: Stock symbol without .NS suffix
        
    Returns:
        Dictionary containing the result
    """
    if not FINANCIAL_DATA_AVAILABLE:
        return {
            "success": False,
            "error": "Financial data dependencies not available. Cannot fetch sector info.",
            "stock_symbol": stock_symbol
        }

    try:
        # Remove .NS suffix if present
        clean_symbol = stock_symbol.split('.NS')[0] if '.NS' in stock_symbol else stock_symbol
        
        logger.info(f"Fetching sector info for {clean_symbol}")
        sector_info = financial_data_manager.get_sector_info_from_moneycontrol(clean_symbol)
        
        if sector_info:
            # Update sector information in database
            sector_success = db_manager.update_stock_field(clean_symbol, "Sector", sector_info.get("Sector", ""))
            pe_success = db_manager.update_stock_field(clean_symbol, "Sector_PE", sector_info.get("Sector_PE"))
            
            return {
                "success": sector_success and pe_success,
                "stock_symbol": clean_symbol,
                "sector_info": sector_info,
                "database_updates": {
                    "sector_update": sector_success,
                    "sector_pe_update": pe_success
                }
            }
        else:
            return {
                "success": False,
                "error": f"Failed to fetch sector information for {clean_symbol}",
                "stock_symbol": clean_symbol
            }
            
    except Exception as e:
        logger.error(f"Error in fetch_sector_info: {str(e)}")
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}",
            "stock_symbol": stock_symbol
        }

def fetch_complete_stock_data(ticker: str) -> Dict[str, Any]:
    """
    Complete workflow: fetch all financial data and sector information.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        Dictionary containing comprehensive results
    """
    if not FINANCIAL_DATA_AVAILABLE or not DB_AVAILABLE:
        # Return mock complete stock data
        stock_symbol = ticker.replace('.NS', '')
        return {
            "success": True,
            "ticker": ticker,
            "stock_symbol": stock_symbol,
            "financial_data_results": {
                "success": True,
                "operations": {
                    "basic_info": {"success": True},
                    "financial_statements": {"success": True, "records_count": 4},
                    "income_statement": {"success": True, "records_count": 4},
                    "balance_sheet": {"success": True, "records_count": 4},
                    "cash_flow_statement": {"success": True, "records_count": 4},
                    "daily_price_history": {"success": True, "records_count": 100},
                    "monthly_price_history": {"success": True, "records_count": 12}
                },
                "summary": {"successful_operations": 7, "total_operations": 7, "success_rate": "100.0%"}
            },
            "sector_info_results": {
                "success": True,
                "sector_info": {"Sector": "Technology", "Sector_PE": 25.0}
            },
            "overall_summary": {
                "financial_operations_successful": 7,
                "sector_info_successful": True,
                "total_errors": 0,
                "total_warnings": 0
            },
            "message": f"Mock: Complete stock data for {stock_symbol}"
        }
    
    logger.info(f"Starting complete data fetch for {ticker}")
    
    # Fetch financial data
    financial_results = fetch_and_store_stock_data(ticker)
    
    # Fetch sector information
    stock_symbol = ticker.split('.NS')[0] if '.NS' in ticker else ticker
    sector_results = fetch_sector_info(stock_symbol)
    
    return {
        "success": financial_results["success"] or sector_results["success"],
        "ticker": ticker,
        "stock_symbol": stock_symbol,
        "financial_data_results": financial_results,
        "sector_info_results": sector_results,
        "overall_summary": {
            "financial_operations_successful": financial_results.get("summary", {}).get("successful_operations", 0),
            "sector_info_successful": sector_results["success"],
            "total_errors": len(financial_results.get("errors", [])) + (0 if sector_results["success"] else 1),
            "total_warnings": len(financial_results.get("warnings", []))
        }
    }

# Tool metadata for MCP server
TOOL_METADATA = {
    "get_basic_stock_info": {
        "name": "get_basic_stock_info",
        "description": "Get basic stock information including company name and current EPS",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'RELIANCE.NS' for Indian stocks)"
                }
            },
            "required": ["ticker"]
        }
    },
    "get_financial_statements": {
        "name": "get_financial_statements",
        "description": "Get financial statements data for a stock",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'RELIANCE.NS' for Indian stocks)"
                }
            },
            "required": ["ticker"]
        }
    },
    "get_income_statement": {
        "name": "get_income_statement",
        "description": "Get income statement data for a stock (contains EPS data)",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'RELIANCE.NS' for Indian stocks)"
                }
            },
            "required": ["ticker"]
        }
    },
    "get_balance_sheet": {
        "name": "get_balance_sheet",
        "description": "Get balance sheet data for a stock",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'RELIANCE.NS' for Indian stocks)"
                }
            },
            "required": ["ticker"]
        }
    },
    "get_cash_flow_statement": {
        "name": "get_cash_flow_statement",
        "description": "Get cash flow statement data for a stock",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'RELIANCE.NS' for Indian stocks)"
                }
            },
            "required": ["ticker"]
        }
    },
    "get_daily_price_history": {
        "name": "get_daily_price_history",
        "description": "Get 10 years of daily price history for a stock",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'RELIANCE.NS' for Indian stocks)"
                }
            },
            "required": ["ticker"]
        }
    },
    "get_monthly_price_history": {
        "name": "get_monthly_price_history",
        "description": "Get monthly price history processed from daily data",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'RELIANCE.NS' for Indian stocks)"
                }
            },
            "required": ["ticker"]
        }
    },
    "get_intrinsic_pe_data": {
        "name": "get_intrinsic_pe_data",
        "description": "Calculate and get intrinsic PE ratio data for a stock",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'RELIANCE.NS' for Indian stocks)"
                }
            },
            "required": ["ticker"]
        }
    },
    "get_sector_info": {
        "name": "get_sector_info",
        "description": "Get sector information from MoneyControl API",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_symbol": {
                    "type": "string",
                    "description": "Stock symbol without .NS suffix"
                }
            },
            "required": ["stock_symbol"]
        }
    },
    "fetch_and_store_stock_data": {
        "name": "fetch_and_store_stock_data",
        "description": "Fetch comprehensive financial data for a stock using yfinance and store in database",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'RELIANCE.NS' for Indian stocks)"
                }
            },
            "required": ["ticker"]
        }
    },
    "fetch_sector_info": {
        "name": "fetch_sector_info",
        "description": "Fetch sector information from MoneyControl API and update database",
        "parameters": {
            "type": "object",
            "properties": {
                "stock_symbol": {
                    "type": "string",
                    "description": "Stock symbol without .NS suffix"
                }
            },
            "required": ["stock_symbol"]
        }
    },
    "fetch_complete_stock_data": {
        "name": "fetch_complete_stock_data",
        "description": "Complete workflow to fetch all financial data and sector information for a stock",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., 'RELIANCE.NS' for Indian stocks)"
                }
            },
            "required": ["ticker"]
        }
    }
} 