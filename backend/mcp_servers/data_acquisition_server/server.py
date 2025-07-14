#!/usr/bin/env python3
"""
VyasaQuant MCP Server
A Model Context Protocol server for stock data analysis and financial information retrieval.
"""

import sys
import os
import json
import asyncio
import logging
import math
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import response models
try:
    from models import get_response_schema, get_response_model, RESPONSE_MODELS
    MODELS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import response models: {e}")
    MODELS_AVAILABLE = False

# Configure logging to both file and stderr
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../logs")
os.makedirs(log_dir, exist_ok=True)

# Create handlers with UTF-8 encoding
file_handler = logging.FileHandler(os.path.join(log_dir, "mcp_server.log"), encoding='utf-8')
console_handler = logging.StreamHandler(sys.stderr)

# Set UTF-8 encoding for console handler if possible
if hasattr(console_handler.stream, 'reconfigure'):
    try:
        console_handler.stream.reconfigure(encoding='utf-8')
    except:
        pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)

# Configure child loggers for file logging
utils_logger = logging.getLogger('utils.ticker_utils')
utils_logger.setLevel(logging.INFO)
utils_file_handler = logging.FileHandler(os.path.join(log_dir, "ticker_utils.log"), encoding='utf-8')
utils_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
utils_logger.addHandler(utils_file_handler)
utils_logger.propagate = True

tools_logger = logging.getLogger('tools.get_ticker_symbol')
tools_logger.setLevel(logging.INFO)
tools_file_handler = logging.FileHandler(os.path.join(log_dir, "ticker_tools.log"), encoding='utf-8')
tools_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
tools_logger.addHandler(tools_file_handler)
tools_logger.propagate = True

# Log startup (without emoji to avoid encoding issues)
logger.info("MCP Server logging configured - logs will be written to files")

def json_serializer(obj):
    """Custom JSON serializer that handles NaN values and other special objects"""
    if isinstance(obj, float):
        if math.isnan(obj):
            return None
        elif math.isinf(obj):
            return None
    return str(obj)

def safe_json_dumps(obj, **kwargs):
    """Safe JSON dumps that handles NaN values properly"""
    try:
        return json.dumps(obj, default=json_serializer, **kwargs)
    except (TypeError, ValueError) as e:
        logger.error(f"JSON serialization error: {e}")
        # Fallback to string representation
        return str(obj)

# Conditional imports with graceful degradation
AVAILABLE_TOOLS = {}

# Try to import ticker tools
try:
    from tools.get_ticker_symbol import get_ticker_symbol, search_companies, TOOL_METADATA as TICKER_TOOLS
    AVAILABLE_TOOLS.update({
            "get_ticker_symbol": {
                "function": get_ticker_symbol,
                "metadata": TICKER_TOOLS["get_ticker_symbol"]
            },
            "search_companies": {
                "function": search_companies,
                "metadata": TICKER_TOOLS["search_companies"]
            }
        })
    logger.info("Ticker tools imported successfully")
except ImportError as e:
    logger.warning(f"Ticker tools not available: {e}")

# Try to import financial data tools
try:
    from tools.fetch_financial_data import (
        get_basic_stock_info,
        get_financial_statements,
        get_income_statement,
        get_balance_sheet,
        get_cash_flow_statement,
        get_daily_price_history,
        get_monthly_price_history,
        get_intrinsic_pe_data,
        get_sector_info,
        fetch_and_store_stock_data, 
        fetch_sector_info, 
        fetch_complete_stock_data,
        TOOL_METADATA as FINANCIAL_TOOLS
    )
    
    # Create EPS wrapper function that uses financial statements
    def get_eps_data_from_statements(ticker_symbol: str, years: int = 4) -> Dict[str, Any]:
        """
        Get EPS data by extracting from financial statements.
        This wrapper allows get_eps_data to use get_financial_statements internally.
        
        Args:
            ticker_symbol: Stock ticker symbol
            years: Number of years of data requested
            
        Returns:
            Dictionary with EPS data in the expected format
        """
        try:
            # Call get_financial_statements (note: it uses 'ticker' parameter)
            financial_result = get_financial_statements(ticker_symbol)
            logger.info(f"get_financial_statements result is:")
            logger.info(financial_result)
            
            if not financial_result.get("success", False):
                return {
                    "success": False,
                    "ticker_symbol": ticker_symbol,
                    "years_requested": years,
                    "years_found": 0,
                    "eps_data": {},
                    "error": financial_result.get("message", "Failed to get financial statements")
                }
            
            # Extract EPS data from financial records
            # fin = financial_result[['stock_symbol','Date','Basic EPS']]
            # fin = fin.rename(columns={'Basic EPS':'EPS'})
            # fin['year'] = fin.Date.dt.year
            # fin['month'] = fin.Date.dt.month
            # fin['financial_year'] = fin.apply(lambda row: row['year'] if row['month']>=4 else row['year']-1, axis=1)
            # fin = fin[['stock_symbol','financial_year','EPS']]
            financial_data = financial_result.get("data", [])
            eps_data = {}
            
            for record in financial_data:
                if "Date" in record and "Basic EPS" in record:
                    date_obj = record["Date"]
                    # Handle both Timestamp and string date formats
                    if hasattr(date_obj, 'year'):
                        # It's a Timestamp object
                        year = str(date_obj.year)
                    else:
                        # It's a string, extract year
                        year = date_obj.split("-")[0] if "-" in str(date_obj) else str(date_obj)[:4]
                    
                    eps_value = record["Basic EPS"]
                    if eps_value is not None:
                        # eps_data[year]
                        eps_float = float(eps_value)
                        import math
                        if not (math.isnan(eps_float) or math.isinf(eps_float)):
                            eps_data[year] = eps_float
            
            # Sort by year and limit to requested years
            sorted_years = sorted(eps_data.keys(), reverse=False)[:years]
            #sorted_years = sorted(rev_sorted_years, reverse=False)
            filtered_eps_data = {year: eps_data[year] for year in sorted_years}
            # logger.info(f"Extracting EPS data for {ticker_symbol} for {years} years and fin is:")
            # logger.info(fin)
            # filtered_eps_data = fin.sort_values(by='financial_year', ascending=False).head(years).set_index('financial_year')['EPS'].to_dict()
            logger.info(filtered_eps_data)
            logger.info(f"Successfully extracted EPS data for {len(filtered_eps_data)} years")
            return {
                "success": True,
                "ticker_symbol": ticker_symbol,
                "years_requested": years,
                "years_found": len(filtered_eps_data),
                "eps_data": filtered_eps_data,
                "message": f"Successfully extracted EPS data for {len(filtered_eps_data)} years"
            }
            
        except Exception as e:
            logger.error(f"Error in get_eps_data_from_statements: {str(e)}")
            return {
                "success": False,
                "ticker_symbol": ticker_symbol,
                "years_requested": years,
                "years_found": 0,
                "eps_data": {},
                "error": f"Error extracting EPS data: {str(e)}"
            }
    
    AVAILABLE_TOOLS.update({
        "get_basic_stock_info": {
            "function": get_basic_stock_info,
            "metadata": FINANCIAL_TOOLS["get_basic_stock_info"]
        },
        "get_eps_data": {
            "function": get_eps_data_from_statements,
            "metadata": {
                "name": "get_eps_data",
                "description": "Get EPS data for a stock by extracting from financial statements",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker_symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol to retrieve EPS data for"
                        },
                        "years": {
                            "type": "integer",
                            "description": "Number of years of EPS data to retrieve",
                            "default": 4
                        }
                    },
                    "required": ["ticker_symbol"]
                }
            }
        },
        "get_financial_statements": {
            "function": get_financial_statements,
            "metadata": FINANCIAL_TOOLS["get_financial_statements"]
        },
        "get_income_statement": {
            "function": get_income_statement,
            "metadata": FINANCIAL_TOOLS["get_income_statement"]
        },
        "get_balance_sheet": {
            "function": get_balance_sheet,
            "metadata": FINANCIAL_TOOLS["get_balance_sheet"]
        },
        "get_cash_flow_statement": {
            "function": get_cash_flow_statement,
            "metadata": FINANCIAL_TOOLS["get_cash_flow_statement"]
        },
        "get_daily_price_history": {
            "function": get_daily_price_history,
            "metadata": FINANCIAL_TOOLS["get_daily_price_history"]
        },
        "get_monthly_price_history": {
            "function": get_monthly_price_history,
            "metadata": FINANCIAL_TOOLS["get_monthly_price_history"]
        },
        "get_intrinsic_pe_data": {
            "function": get_intrinsic_pe_data,
            "metadata": FINANCIAL_TOOLS["get_intrinsic_pe_data"]
        },
        "get_sector_info": {
            "function": get_sector_info,
            "metadata": FINANCIAL_TOOLS["get_sector_info"]
        },
        "fetch_and_store_stock_data": {
            "function": fetch_and_store_stock_data,
            "metadata": FINANCIAL_TOOLS["fetch_and_store_stock_data"]
        },
        "fetch_sector_info": {
            "function": fetch_sector_info,
            "metadata": FINANCIAL_TOOLS["fetch_sector_info"]
        },
        "fetch_complete_stock_data": {
            "function": fetch_complete_stock_data,
            "metadata": FINANCIAL_TOOLS["fetch_complete_stock_data"]
        }
    })
    logger.info("Financial data tools imported successfully")
except ImportError as e:
    logger.warning(f"Financial data tools not available: {e}")

# Try to import database tools
try:
    from tools.database_tools import (
        execute_query,
        get_stock_list,
        get_stock_financial_data,
        upsert_stock_data,
        update_stock_field,
        TOOL_METADATA as DATABASE_TOOLS
    )
    AVAILABLE_TOOLS.update({
        "execute_query": {
            "function": execute_query,
            "metadata": DATABASE_TOOLS["execute_query"]
        },
        "get_stock_list": {
            "function": get_stock_list,
            "metadata": DATABASE_TOOLS["get_stock_list"]
        },
        "get_stock_financial_data": {
            "function": get_stock_financial_data,
            "metadata": DATABASE_TOOLS["get_stock_financial_data"]
        },
        "upsert_stock_data": {
            "function": upsert_stock_data,
            "metadata": DATABASE_TOOLS["upsert_stock_data"]
        },
        "update_stock_field": {
            "function": update_stock_field,
            "metadata": DATABASE_TOOLS["update_stock_field"]
        }
    })
    logger.info("Database tools imported successfully")
except ImportError as e:
    logger.warning(f"Database tools not available: {e}")

# Try to import download tools
try:
    from tools.download_reports import (
        download_annual_reports,
        check_existing_reports,
        TOOL_METADATA as DOWNLOAD_TOOLS
    )
    AVAILABLE_TOOLS.update({
        "download_annual_reports": {
            "function": download_annual_reports,
            "metadata": DOWNLOAD_TOOLS["download_annual_reports"]
        },
        "check_existing_reports": {
            "function": check_existing_reports,
            "metadata": DOWNLOAD_TOOLS["check_existing_reports"]
        }
    })
    logger.info("Download tools imported successfully")
except ImportError as e:
    logger.warning(f"Download tools not available: {e}")

logger.info(f"Total available tools: {len(AVAILABLE_TOOLS)}")

class VyasaQuantMCPServer:
    """MCP Server for VyasaQuant stock data tools"""
    
    def __init__(self):
        self.tools = AVAILABLE_TOOLS.copy()
        logger.info(f"Server initialized with {len(self.tools)} tools")
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "name": "vyasaquant-mcp-server",
            "version": "2.0.0",
            "description": "MCP Server for VyasaQuant stock data analysis and financial information retrieval with comprehensive utils integration",
            "author": "VyasaQuant",
            "homepage": "https://github.com/vyasaquant/vyasaquant",
            "capabilities": {
                "tools": True,
                "resources": False,
                "prompts": False,
                "logging": True,
                "response_schemas": MODELS_AVAILABLE
            },
            "available_tools": list(self.tools.keys()),
            "response_schemas_available": MODELS_AVAILABLE
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [tool_info["metadata"] for tool_info in self.tools.values()]
    
    def get_response_schemas(self) -> Dict[str, Any]:
        """Get response schemas for all tools"""
        if not MODELS_AVAILABLE:
            return {
                "error": "Response models not available",
                "schemas": {}
            }
        
        schemas = {}
        for tool_name in self.tools.keys():
            schema = get_response_schema(tool_name)
            if schema:
                schemas[tool_name] = schema
        
        return {
            "success": True,
            "schemas": schemas,
            "total_tools": len(schemas)
        }
    
    def get_tool_response_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get response schema for a specific tool"""
        if not MODELS_AVAILABLE:
            return {
                "error": "Response models not available"
            }
        
        if tool_name not in self.tools:
            return {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tools.keys())
            }
        
        schema = get_response_schema(tool_name)
        if schema:
            return {
                "success": True,
                "tool_name": tool_name,
                "response_schema": schema
            }
        else:
            return {
                "error": f"No response schema defined for tool '{tool_name}'"
            }
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool with given arguments"""
        try:
            if tool_name not in self.tools:
                return {
                    "error": f"Tool '{tool_name}' not found",
                    "available_tools": list(self.tools.keys())
                }
            
            tool_info = self.tools[tool_name]
            function = tool_info["function"]
            
            # Log tool execution start
            logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")
            
            # Call the function with the provided arguments
            result = function(**arguments)
            
            # Log tool execution completion
            logger.info(f"Tool {tool_name} completed successfully")
            
            return {
                "success": True,
                "tool_name": tool_name,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}': {str(e)}")
            import traceback
            logger.error(f"Tool error traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": f"Error calling tool '{tool_name}': {str(e)}",
                "tool_name": tool_name
            }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {
                                "listChanged": True
                            },
                            "logging": {}
                        },
                        "serverInfo": self.get_server_info()
                    }
                }
                
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.list_tools()
                    }
                }
                
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = self.call_tool(tool_name, arguments)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": safe_json_dumps(result)
                            }
                        ]
                    }
                }
                
            elif method == "tools/response_schemas":
                # Get response schemas for all tools
                result = self.get_response_schemas()
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": safe_json_dumps(result)
                            }
                        ]
                    }
                }
                
            elif method == "tools/response_schema":
                # Get response schema for a specific tool
                tool_name = params.get("tool_name")
                result = self.get_tool_response_schema(tool_name)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": safe_json_dumps(result)
                            }
                        ]
                    }
                }
                
            elif method == "ping":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {}
                }
                
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def run_stdio(self):
        """Run the server using stdio transport"""
        logger.info("Starting VyasaQuant MCP Server with stdio transport")
        
        while True:
            try:
                # Read request from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                
                # Write response to stdout
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Error in stdio loop: {str(e)}")
                continue

def main():
    """Main entry point"""
    server = VyasaQuantMCPServer()
    
    try:
        # Run stdio server
        asyncio.run(server.run_stdio())
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")

if __name__ == "__main__":
    main() 