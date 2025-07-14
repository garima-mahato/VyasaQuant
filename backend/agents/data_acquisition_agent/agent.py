"""
Data Acquisition Agent
Handles fetching financial data from various sources through MCP tools.
"""

import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import asyncio

from ..base.agent_base import BaseAgent
from ..base.mcp_client import MCPClient


class DataAcquisitionAgent(BaseAgent):
    """Agent for acquiring financial data from various sources"""
    
    def __init__(self):
        super().__init__("data_acquisition")
        self.mcp_client = None
        
    async def initialize(self) -> bool:
        """Initialize the agent with MCP client connection"""
        try:
            # Start MCP server for data acquisition tools
            self.mcp_client = MCPClient(
                server_command=["python", "server.py"],
                cwd="mcp_servers/data_acquisition_server"
            )
            await self.mcp_client.start()
            
            # List available tools
            tools = await self.mcp_client.list_tools()
            self.logger.info(f"Available tools: {[tool['name'] for tool in tools]}")
            
            self.initialized = True
            self.logger.info("Data Acquisition Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Data Acquisition Agent: {e}")
            return False
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process stock data acquisition request"""
        if not self.initialized:
            raise RuntimeError("Agent not initialized")
        
        request_type = data.get("type")
        stock_symbol = data.get("stock_symbol")
        
        if not stock_symbol:
            return {"error": "stock_symbol is required"}
        
        try:
            if request_type == "check_existing_reports":
                return await self._check_existing_reports(stock_symbol)
            elif request_type == "download_annual_reports":
                return await self._download_annual_reports(stock_symbol, data.get("missing_years"))
            elif request_type == "fetch_stock_data":
                return await self._fetch_stock_data(stock_symbol)
            elif request_type == "fetch_complete_data":
                return await self._fetch_complete_stock_data(stock_symbol)
            elif request_type == "get_ticker_symbol":
                return await self._get_ticker_symbol(data.get("company_name"))
            elif request_type == "search_companies":
                return await self._search_companies(data.get("query"))
            elif request_type == "fetch_sector_info":
                return await self._fetch_sector_info(stock_symbol)
            else:
                return {"error": f"Unknown request type: {request_type}"}
                
        except Exception as e:
            self.logger.error(f"Error processing request: {e}")
            return {"error": str(e)}
    
    async def _check_existing_reports(self, stock_symbol: str) -> Dict[str, Any]:
        """Check existing reports for a stock symbol"""
        result = await self.mcp_client.call_tool(
            "check_existing_reports",
            {"stock_symbol": stock_symbol}
        )
        return result
    
    async def _download_annual_reports(self, stock_symbol: str, missing_years: Optional[List[Tuple[int, int]]] = None) -> Dict[str, Any]:
        """Download annual reports for a stock symbol"""
        args = {"stock_symbol": stock_symbol}
        if missing_years:
            args["missing_years"] = missing_years
            
        result = await self.mcp_client.call_tool(
            "download_annual_reports",
            args
        )
        return result
    
    async def _fetch_stock_data(self, stock_symbol: str) -> Dict[str, Any]:
        """Fetch basic stock data"""
        result = await self.mcp_client.call_tool(
            "fetch_and_store_stock_data",
            {"stock_symbol": stock_symbol}
        )
        return result
    
    async def _fetch_complete_stock_data(self, stock_symbol: str) -> Dict[str, Any]:
        """Fetch complete stock data including financials"""
        result = await self.mcp_client.call_tool(
            "fetch_complete_stock_data",
            {"stock_symbol": stock_symbol}
        )
        return result
    
    async def _get_ticker_symbol(self, company_name: str) -> Dict[str, Any]:
        """Get ticker symbol for a company name"""
        result = await self.mcp_client.call_tool(
            "get_ticker_symbol",
            {"company_name": company_name}
        )
        return result
    
    async def _search_companies(self, query: str) -> Dict[str, Any]:
        """Search for companies by name or symbol"""
        result = await self.mcp_client.call_tool(
            "search_companies",
            {"query": query}
        )
        return result
    
    async def _fetch_sector_info(self, stock_symbol: str) -> Dict[str, Any]:
        """Fetch sector information for a stock"""
        result = await self.mcp_client.call_tool(
            "fetch_sector_info",
            {"stock_symbol": stock_symbol}
        )
        return result
    
    async def process_stock_comprehensive(self, stock_symbol: str) -> Dict[str, Any]:
        """Process a stock comprehensively - check, download, and extract data"""
        try:
            # Step 1: Check existing reports
            existing_check = await self._check_existing_reports(stock_symbol)
            
            # Step 2: Download missing reports if any
            if existing_check.get("missing_years"):
                download_result = await self._download_annual_reports(
                    stock_symbol, 
                    existing_check["missing_years"]
                )
                
            # Step 3: Fetch complete stock data
            stock_data = await self._fetch_complete_stock_data(stock_symbol)
            
            # Step 4: Get sector information
            sector_info = await self._fetch_sector_info(stock_symbol)
            
            return {
                "stock_symbol": stock_symbol,
                "existing_reports": existing_check,
                "stock_data": stock_data,
                "sector_info": sector_info,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive stock processing: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.mcp_client:
            await self.mcp_client.stop()
        self.logger.info("Data Acquisition Agent cleaned up") 