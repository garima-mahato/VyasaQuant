"""
Integration tests for Data Acquisition System.
Tests the complete workflow from agent to MCP server to tools.
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import subprocess
import time
import signal
import os

from agents.data_acquisition_agent.agent import DataAcquisitionAgent


class TestDataAcquisitionIntegration:
    """Integration tests for the complete data acquisition workflow."""

    @pytest.fixture(scope="class")
    async def mcp_server_process(self):
        """Start MCP server for integration testing."""
        server_path = Path(__file__).parent.parent.parent / "mcp_servers" / "data_acquisition_server"
        start_server_path = server_path / "start_server.py"
        
        # Start the server process
        process = subprocess.Popen(
            ["python", str(start_server_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(server_path)
        )
        
        # Give the server time to start
        await asyncio.sleep(2)
        
        yield process
        
        # Cleanup
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_initialization_and_cleanup(self):
        """Test agent initialization and cleanup process."""
        agent = DataAcquisitionAgent()
        
        # Test initialization
        with patch('agents.base.mcp_client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.start = AsyncMock()
            mock_client.list_tools = AsyncMock(return_value=[
                {"name": "get_ticker_symbol"},
                {"name": "fetch_and_store_stock_data"},
                {"name": "download_annual_reports"}
            ])
            mock_client_class.return_value = mock_client
            
            success = await agent.initialize()
            assert success is True
            assert agent.initialized is True
            
            # Test cleanup
            await agent.cleanup()
            mock_client.stop.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_stock_workflow(self, mock_env_vars):
        """Test complete stock data acquisition workflow."""
        agent = DataAcquisitionAgent()
        
        with patch('agents.base.mcp_client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.start = AsyncMock()
            mock_client.list_tools = AsyncMock(return_value=[
                {"name": "get_ticker_symbol"},
                {"name": "fetch_complete_stock_data"},
                {"name": "check_existing_reports"},
                {"name": "download_annual_reports"}
            ])
            
            # Mock sequential tool calls for complete workflow
            call_responses = [
                # get_ticker_symbol response
                {
                    "success": True,
                    "ticker_symbol": "HAL",
                    "company_info": {"name": "Hindustan Aeronautics Limited"}
                },
                # check_existing_reports response
                {
                    "success": True,
                    "missing_years": [[2022, 2023], [2021, 2022]],
                    "missing_count": 2
                },
                # download_annual_reports response
                {
                    "success": True,
                    "pdf_paths": ["/path/to/report1.pdf", "/path/to/report2.pdf"],
                    "downloaded_count": 2
                },
                # fetch_complete_stock_data response
                {
                    "success": True,
                    "financial_data_results": {
                        "success": True,
                        "summary": {"successful_operations": 8}
                    },
                    "sector_info_results": {
                        "success": True,
                        "sector_info": {"sector": "Aerospace & Defense"}
                    }
                }
            ]
            
            mock_client.call_tool = AsyncMock(side_effect=call_responses)
            mock_client_class.return_value = mock_client
            
            # Initialize agent
            await agent.initialize()
            
            # Execute complete workflow
            result = await agent.process_stock_comprehensive("HAL")
            
            # Verify the workflow completed successfully
            assert result["status"] == "completed"
            assert result["stock_symbol"] == "HAL"
            assert "existing_reports" in result
            assert "download_reports" in result
            assert "stock_data" in result
            
            # Verify all expected tool calls were made
            assert mock_client.call_tool.call_count == 4

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_ticker_symbol_lookup_workflow(self, mock_env_vars):
        """Test ticker symbol lookup workflow."""
        agent = DataAcquisitionAgent()
        
        with patch('agents.base.mcp_client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.start = AsyncMock()
            mock_client.list_tools = AsyncMock(return_value=[{"name": "get_ticker_symbol"}])
            mock_client.call_tool = AsyncMock(return_value={
                "success": True,
                "ticker_symbol": "HAL",
                "company_info": {
                    "Symbol": "HAL",
                    "Company_Name": "Hindustan Aeronautics Limited",
                    "Series": "EQ"
                }
            })
            mock_client_class.return_value = mock_client
            
            await agent.initialize()
            
            # Test ticker symbol lookup
            data = {
                "type": "get_ticker_symbol",
                "company_name": "Hindustan Aeronautics"
            }
            result = await agent.process(data)
            
            assert result["success"] is True
            assert result["ticker_symbol"] == "HAL"
            mock_client.call_tool.assert_called_once_with(
                "get_ticker_symbol",
                {"company_name": "Hindustan Aeronautics"}
            )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_financial_data_fetch_workflow(self, mock_env_vars):
        """Test financial data fetching workflow."""
        agent = DataAcquisitionAgent()
        
        with patch('agents.base.mcp_client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.start = AsyncMock()
            mock_client.list_tools = AsyncMock(return_value=[{"name": "fetch_and_store_stock_data"}])
            mock_client.call_tool = AsyncMock(return_value={
                "success": True,
                "ticker": "HAL.NS",
                "stock_symbol": "HAL",
                "operations": {
                    "basic_info": {"success": True},
                    "financial_statements": {"success": True, "records_count": 10},
                    "balance_sheet": {"success": True, "records_count": 5}
                },
                "summary": {
                    "successful_operations": 8,
                    "total_operations": 9,
                    "success_rate": "88.9%"
                }
            })
            mock_client_class.return_value = mock_client
            
            await agent.initialize()
            
            # Test financial data fetch
            data = {
                "type": "fetch_stock_data",
                "stock_symbol": "HAL"
            }
            result = await agent.process(data)
            
            assert result["success"] is True
            assert result["stock_symbol"] == "HAL"
            assert "operations" in result
            assert "summary" in result

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_annual_reports_workflow(self, mock_env_vars):
        """Test annual reports download workflow."""
        agent = DataAcquisitionAgent()
        
        with patch('agents.base.mcp_client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.start = AsyncMock()
            mock_client.list_tools = AsyncMock(return_value=[
                {"name": "check_existing_reports"},
                {"name": "download_annual_reports"}
            ])
            
            # Mock check existing reports
            def mock_call_tool(tool_name, args):
                if tool_name == "check_existing_reports":
                    return {
                        "success": True,
                        "missing_years": [[2022, 2023], [2021, 2022]],
                        "missing_count": 2
                    }
                elif tool_name == "download_annual_reports":
                    return {
                        "success": True,
                        "pdf_paths": ["/path/to/report1.pdf", "/path/to/report2.pdf"],
                        "downloaded_count": 2
                    }
            
            mock_client.call_tool = AsyncMock(side_effect=mock_call_tool)
            mock_client_class.return_value = mock_client
            
            await agent.initialize()
            
            # Test check existing reports
            check_data = {
                "type": "check_existing_reports",
                "stock_symbol": "HAL"
            }
            check_result = await agent.process(check_data)
            
            assert check_result["success"] is True
            assert check_result["missing_count"] == 2
            
            # Test download reports
            download_data = {
                "type": "download_annual_reports",
                "stock_symbol": "HAL",
                "missing_years": [(2022, 2023), (2021, 2022)]
            }
            download_result = await agent.process(download_data)
            
            assert download_result["success"] is True
            assert download_result["downloaded_count"] == 2

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_handling_integration(self, mock_env_vars):
        """Test error handling in integration scenarios."""
        agent = DataAcquisitionAgent()
        
        with patch('agents.base.mcp_client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.start = AsyncMock()
            mock_client.list_tools = AsyncMock(return_value=[{"name": "get_ticker_symbol"}])
            
            # Mock error responses
            mock_client.call_tool = AsyncMock(side_effect=Exception("MCP server connection lost"))
            mock_client_class.return_value = mock_client
            
            await agent.initialize()
            
            # Test error handling
            data = {
                "type": "get_ticker_symbol",
                "company_name": "Test Company"
            }
            result = await agent.process(data)
            
            assert "error" in result
            assert "MCP server connection lost" in result["error"]

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_agent_status_monitoring(self, mock_env_vars):
        """Test agent status monitoring throughout workflow."""
        agent = DataAcquisitionAgent()
        
        # Initial status
        status = agent.get_status()
        assert status["status"] == "inactive"
        assert status["initialized"] is False
        
        with patch('agents.base.mcp_client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.start = AsyncMock()
            mock_client.list_tools = AsyncMock(return_value=[])
            mock_client_class.return_value = mock_client
            
            # Initialize and check status
            await agent.initialize()
            status = agent.get_status()
            assert status["status"] == "active"
            assert status["initialized"] is True
            
            # Cleanup and check status
            await agent.cleanup()
            status = agent.get_status()
            assert status["status"] == "inactive"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_concurrent_requests(self, mock_env_vars):
        """Test handling concurrent requests to the agent."""
        agent = DataAcquisitionAgent()
        
        with patch('agents.base.mcp_client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.start = AsyncMock()
            mock_client.list_tools = AsyncMock(return_value=[{"name": "get_ticker_symbol"}])
            mock_client.call_tool = AsyncMock(return_value={
                "success": True,
                "ticker_symbol": "TEST",
                "company_info": {"name": "Test Company"}
            })
            mock_client_class.return_value = mock_client
            
            await agent.initialize()
            
            # Create multiple concurrent requests
            requests = [
                {
                    "type": "get_ticker_symbol",
                    "company_name": f"Test Company {i}"
                }
                for i in range(5)
            ]
            
            # Process requests concurrently
            tasks = [agent.process(request) for request in requests]
            results = await asyncio.gather(*tasks)
            
            # Verify all requests completed successfully
            for result in results:
                assert result["success"] is True
                assert result["ticker_symbol"] == "TEST"
            
            # Verify the MCP client was called for each request
            assert mock_client.call_tool.call_count == 5


class TestMCPServerIntegration:
    """Test MCP server functionality in isolation."""

    @pytest.mark.integration
    def test_server_configuration(self):
        """Test MCP server configuration loading."""
        config_path = Path(__file__).parent.parent.parent / "config" / "mcp_config.json"
        
        assert config_path.exists(), "MCP configuration file should exist"
        
        with open(config_path) as f:
            config = json.load(f)
        
        assert "mcpServers" in config
        assert "data_acquisition" in config["mcpServers"]
        
        data_acq_config = config["mcpServers"]["data_acquisition"]
        assert "command" in data_acq_config
        assert "args" in data_acq_config

    @pytest.mark.integration
    def test_server_dependencies(self):
        """Test that all server dependencies are available."""
        server_path = Path(__file__).parent.parent.parent / "mcp_servers" / "data_acquisition_server"
        
        # Check server file exists
        assert (server_path / "server.py").exists()
        assert (server_path / "start_server.py").exists()
        
        # Check tools directory exists
        tools_path = server_path / "tools"
        assert tools_path.exists()
        assert (tools_path / "get_ticker_symbol.py").exists()
        assert (tools_path / "fetch_financial_data.py").exists()
        assert (tools_path / "download_reports.py").exists()


class TestEndToEndWorkflow:
    """End-to-end workflow tests with mocked external dependencies."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_stock_analysis_workflow(self, mock_env_vars):
        """Test complete stock analysis workflow from company name to data storage."""
        agent = DataAcquisitionAgent()
        
        with patch('agents.base.mcp_client.MCPClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.start = AsyncMock()
            mock_client.list_tools = AsyncMock(return_value=[
                {"name": "get_ticker_symbol"},
                {"name": "fetch_complete_stock_data"},
                {"name": "check_existing_reports"},
                {"name": "download_annual_reports"}
            ])
            
            # Define workflow responses
            workflow_responses = {
                "get_ticker_symbol": {
                    "success": True,
                    "ticker_symbol": "HAL",
                    "company_info": {"name": "Hindustan Aeronautics Limited"}
                },
                "check_existing_reports": {
                    "success": True,
                    "missing_years": [[2022, 2023]],
                    "missing_count": 1
                },
                "download_annual_reports": {
                    "success": True,
                    "pdf_paths": ["/path/to/hal_2022-23.pdf"],
                    "downloaded_count": 1
                },
                "fetch_complete_stock_data": {
                    "success": True,
                    "financial_data_results": {
                        "success": True,
                        "summary": {"successful_operations": 8, "total_operations": 9}
                    },
                    "sector_info_results": {
                        "success": True,
                        "sector_info": {"sector": "Aerospace & Defense"}
                    }
                }
            }
            
            def mock_call_tool(tool_name, args):
                return workflow_responses.get(tool_name, {"success": False, "error": "Unknown tool"})
            
            mock_client.call_tool = AsyncMock(side_effect=mock_call_tool)
            mock_client_class.return_value = mock_client
            
            # Initialize agent
            await agent.initialize()
            
            # Step 1: Get ticker symbol from company name
            ticker_result = await agent.process({
                "type": "get_ticker_symbol",
                "company_name": "Hindustan Aeronautics"
            })
            assert ticker_result["success"] is True
            ticker_symbol = ticker_result["ticker_symbol"]
            
            # Step 2: Check existing reports
            reports_result = await agent.process({
                "type": "check_existing_reports",
                "stock_symbol": ticker_symbol
            })
            assert reports_result["success"] is True
            
            # Step 3: Download missing reports
            if reports_result["missing_count"] > 0:
                download_result = await agent.process({
                    "type": "download_annual_reports",
                    "stock_symbol": ticker_symbol,
                    "missing_years": reports_result["missing_years"]
                })
                assert download_result["success"] is True
            
            # Step 4: Fetch complete financial data
            financial_result = await agent.process({
                "type": "fetch_complete_data",
                "stock_symbol": ticker_symbol
            })
            assert financial_result["success"] is True
            
            # Verify workflow completion
            assert mock_client.call_tool.call_count == 4
            
            await agent.cleanup() 