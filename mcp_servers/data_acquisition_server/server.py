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
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import tools
from tools.get_ticker_symbol import get_ticker_symbol, search_companies, TOOL_METADATA as TICKER_TOOLS
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
from tools.database_tools import (
    execute_query,
    get_stock_list,
    get_stock_financial_data,
    get_eps_data,
    upsert_stock_data,
    update_stock_field,
    TOOL_METADATA as DATABASE_TOOLS
)
from tools.download_reports import (
    download_annual_reports,
    check_existing_reports,
    TOOL_METADATA as DOWNLOAD_TOOLS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VyasaQuantMCPServer:
    """MCP Server for VyasaQuant stock data tools"""
    
    def __init__(self):
        self.tools = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        # Register ticker tools
        self.tools.update({
            "get_ticker_symbol": {
                "function": get_ticker_symbol,
                "metadata": TICKER_TOOLS["get_ticker_symbol"]
            },
            "search_companies": {
                "function": search_companies,
                "metadata": TICKER_TOOLS["search_companies"]
            }
        })
        
        # Register individual financial data tools
        self.tools.update({
            "get_basic_stock_info": {
                "function": get_basic_stock_info,
                "metadata": FINANCIAL_TOOLS["get_basic_stock_info"]
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
            }
        })
        
        # Register comprehensive financial data tools
        self.tools.update({
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
        
        # Register database tools
        self.tools.update({
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
            "get_eps_data": {
                "function": get_eps_data,
                "metadata": DATABASE_TOOLS["get_eps_data"]
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
        
        # Register download tools
        self.tools.update({
            "download_annual_reports": {
                "function": download_annual_reports,
                "metadata": DOWNLOAD_TOOLS["download_annual_reports"]
            },
            "check_existing_reports": {
                "function": check_existing_reports,
                "metadata": DOWNLOAD_TOOLS["check_existing_reports"]
            }
        })
        
        logger.info(f"Registered {len(self.tools)} tools")
    
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
                "logging": True
            },
            "available_tools": list(self.tools.keys())
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [tool_info["metadata"] for tool_info in self.tools.values()]
    
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
            
            # Call the function with the provided arguments
            result = function(**arguments)
            
            return {
                "success": True,
                "tool_name": tool_name,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}': {str(e)}")
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
                                "text": json.dumps(result, indent=2, default=str)
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