"""
Unit tests for DataAcquisitionAgent.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from agents.data_acquisition_agent.agent import DataAcquisitionAgent
from agents.base.mcp_client import MCPClient


class TestDataAcquisitionAgent:
    """Test suite for DataAcquisitionAgent."""

    @pytest.fixture
    def agent(self):
        """Create a DataAcquisitionAgent instance for testing."""
        return DataAcquisitionAgent()

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "data_acquisition"
        assert not agent.initialized
        assert agent.mcp_client is None

    @pytest.mark.asyncio
    async def test_initialize_success(self, agent, mock_mcp_client):
        """Test successful agent initialization."""
        with patch.object(MCPClient, '__new__', return_value=mock_mcp_client):
            result = await agent.initialize()
            
            assert result is True
            assert agent.initialized is True
            assert agent.mcp_client is not None
            mock_mcp_client.start.assert_called_once()
            mock_mcp_client.list_tools.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_failure(self, agent):
        """Test agent initialization failure."""
        with patch.object(MCPClient, '__new__', side_effect=Exception("Connection failed")):
            result = await agent.initialize()
            
            assert result is False
            assert agent.initialized is False

    @pytest.mark.asyncio
    async def test_process_not_initialized(self, agent):
        """Test process method when agent is not initialized."""
        data = {"type": "fetch_stock_data", "stock_symbol": "HAL"}
        
        with pytest.raises(RuntimeError, match="Agent not initialized"):
            await agent.process(data)

    @pytest.mark.asyncio
    async def test_process_missing_stock_symbol(self, agent, mock_mcp_client):
        """Test process method with missing stock symbol."""
        agent.mcp_client = mock_mcp_client
        agent.initialized = True
        
        data = {"type": "fetch_stock_data"}
        result = await agent.process(data)
        
        assert result["error"] == "stock_symbol is required"

    @pytest.mark.asyncio
    async def test_process_check_existing_reports(self, agent, mock_mcp_client):
        """Test processing check existing reports request."""
        agent.mcp_client = mock_mcp_client
        agent.initialized = True
        
        mock_result = {
            "success": True,
            "missing_years": [[2022, 2023], [2021, 2022]],
            "stock_symbol": "HAL"
        }
        mock_mcp_client.call_tool.return_value = mock_result
        
        data = {"type": "check_existing_reports", "stock_symbol": "HAL"}
        result = await agent.process(data)
        
        assert result == mock_result
        mock_mcp_client.call_tool.assert_called_once_with(
            "check_existing_reports",
            {"stock_symbol": "HAL"}
        )

    @pytest.mark.asyncio
    async def test_process_download_annual_reports(self, agent, mock_mcp_client):
        """Test processing download annual reports request."""
        agent.mcp_client = mock_mcp_client
        agent.initialized = True
        
        mock_result = {
            "success": True,
            "pdf_paths": ["/path/to/report1.pdf", "/path/to/report2.pdf"],
            "downloaded_count": 2
        }
        mock_mcp_client.call_tool.return_value = mock_result
        
        missing_years = [(2022, 2023), (2021, 2022)]
        data = {
            "type": "download_annual_reports",
            "stock_symbol": "HAL",
            "missing_years": missing_years
        }
        result = await agent.process(data)
        
        assert result == mock_result
        mock_mcp_client.call_tool.assert_called_once_with(
            "download_annual_reports",
            {"stock_symbol": "HAL", "missing_years": missing_years}
        )

    @pytest.mark.asyncio
    async def test_process_fetch_stock_data(self, agent, mock_mcp_client):
        """Test processing fetch stock data request."""
        agent.mcp_client = mock_mcp_client
        agent.initialized = True
        
        mock_result = {
            "success": True,
            "operations": {
                "basic_info": {"success": True},
                "financial_statements": {"success": True, "records_count": 10}
            }
        }
        mock_mcp_client.call_tool.return_value = mock_result
        
        data = {"type": "fetch_stock_data", "stock_symbol": "HAL"}
        result = await agent.process(data)
        
        assert result == mock_result
        mock_mcp_client.call_tool.assert_called_once_with(
            "fetch_and_store_stock_data",
            {"stock_symbol": "HAL"}
        )

    @pytest.mark.asyncio
    async def test_process_fetch_complete_data(self, agent, mock_mcp_client):
        """Test processing fetch complete stock data request."""
        agent.mcp_client = mock_mcp_client
        agent.initialized = True
        
        mock_result = {
            "success": True,
            "financial_data_results": {"success": True},
            "sector_info_results": {"success": True}
        }
        mock_mcp_client.call_tool.return_value = mock_result
        
        data = {"type": "fetch_complete_data", "stock_symbol": "HAL"}
        result = await agent.process(data)
        
        assert result == mock_result
        mock_mcp_client.call_tool.assert_called_once_with(
            "fetch_complete_stock_data",
            {"stock_symbol": "HAL"}
        )

    @pytest.mark.asyncio
    async def test_process_get_ticker_symbol(self, agent, mock_mcp_client):
        """Test processing get ticker symbol request."""
        agent.mcp_client = mock_mcp_client
        agent.initialized = True
        
        mock_result = {
            "success": True,
            "ticker_symbol": "HAL",
            "company_info": {"name": "Hindustan Aeronautics Limited"}
        }
        mock_mcp_client.call_tool.return_value = mock_result
        
        data = {"type": "get_ticker_symbol", "company_name": "Hindustan Aeronautics"}
        result = await agent.process(data)
        
        assert result == mock_result
        mock_mcp_client.call_tool.assert_called_once_with(
            "get_ticker_symbol",
            {"company_name": "Hindustan Aeronautics"}
        )

    @pytest.mark.asyncio
    async def test_process_search_companies(self, agent, mock_mcp_client):
        """Test processing search companies request."""
        agent.mcp_client = mock_mcp_client
        agent.initialized = True
        
        mock_result = {
            "success": True,
            "results": [
                {"symbol": "HAL", "name": "Hindustan Aeronautics Limited"},
                {"symbol": "BEL", "name": "Bharat Electronics Limited"}
            ]
        }
        mock_mcp_client.call_tool.return_value = mock_result
        
        data = {"type": "search_companies", "query": "Hindustan"}
        result = await agent.process(data)
        
        assert result == mock_result
        mock_mcp_client.call_tool.assert_called_once_with(
            "search_companies",
            {"query": "Hindustan"}
        )

    @pytest.mark.asyncio
    async def test_process_fetch_sector_info(self, agent, mock_mcp_client):
        """Test processing fetch sector info request."""
        agent.mcp_client = mock_mcp_client
        agent.initialized = True
        
        mock_result = {
            "success": True,
            "sector_info": {
                "sector": "Aerospace & Defense",
                "sector_pe": 22.5
            }
        }
        mock_mcp_client.call_tool.return_value = mock_result
        
        data = {"type": "fetch_sector_info", "stock_symbol": "HAL"}
        result = await agent.process(data)
        
        assert result == mock_result
        mock_mcp_client.call_tool.assert_called_once_with(
            "fetch_sector_info",
            {"stock_symbol": "HAL"}
        )

    @pytest.mark.asyncio
    async def test_process_unknown_request_type(self, agent, mock_mcp_client):
        """Test processing unknown request type."""
        agent.mcp_client = mock_mcp_client
        agent.initialized = True
        
        data = {"type": "unknown_request", "stock_symbol": "HAL"}
        result = await agent.process(data)
        
        assert "error" in result
        assert "Unknown request type: unknown_request" in result["error"]

    @pytest.mark.asyncio
    async def test_process_exception_handling(self, agent, mock_mcp_client):
        """Test exception handling in process method."""
        agent.mcp_client = mock_mcp_client
        agent.initialized = True
        
        mock_mcp_client.call_tool.side_effect = Exception("Tool call failed")
        
        data = {"type": "fetch_stock_data", "stock_symbol": "HAL"}
        result = await agent.process(data)
        
        assert "error" in result
        assert "Tool call failed" in result["error"]

    @pytest.mark.asyncio
    async def test_process_stock_comprehensive(self, agent, mock_mcp_client):
        """Test comprehensive stock processing."""
        agent.mcp_client = mock_mcp_client
        agent.initialized = True
        
        # Mock responses for different calls
        def mock_call_tool(tool_name, args):
            if tool_name == "check_existing_reports":
                return {"missing_years": [(2022, 2023)]}
            elif tool_name == "download_annual_reports":
                return {"success": True, "downloaded_count": 1}
            elif tool_name == "fetch_complete_stock_data":
                return {"success": True, "operations": {"basic_info": {"success": True}}}
            elif tool_name == "fetch_sector_info":
                return {"success": True, "sector_info": {"sector": "Aerospace & Defense"}}
            
        mock_mcp_client.call_tool.side_effect = mock_call_tool
        
        result = await agent.process_stock_comprehensive("HAL")
        
        assert result["status"] == "completed"
        assert result["stock_symbol"] == "HAL"
        assert "existing_reports" in result
        assert "stock_data" in result
        assert "sector_info" in result

    @pytest.mark.asyncio
    async def test_cleanup(self, agent, mock_mcp_client):
        """Test agent cleanup."""
        agent.mcp_client = mock_mcp_client
        
        await agent.cleanup()
        
        mock_mcp_client.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_no_client(self, agent):
        """Test cleanup when no MCP client exists."""
        agent.mcp_client = None
        
        # Should not raise an exception
        await agent.cleanup()

    def test_get_status(self, agent):
        """Test getting agent status."""
        status = agent.get_status()
        
        assert status["name"] == "data_acquisition"
        assert status["initialized"] is False
        assert status["status"] == "inactive"
        
        # Test when initialized
        agent.initialized = True
        status = agent.get_status()
        assert status["status"] == "active" 