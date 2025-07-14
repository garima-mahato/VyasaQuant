"""
Unit tests for Data Acquisition MCP Tools.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path

# Add the MCP tools to path for testing
project_root = Path(__file__).parent.parent.parent.parent
mcp_tools_path = project_root / "mcp_servers" / "data_acquisition_server" / "tools"
sys.path.append(str(mcp_tools_path))
sys.path.append(str(project_root / "data_acquisition"))


class TestGetTickerSymbolTool:
    """Test suite for get_ticker_symbol tool."""

    @pytest.fixture
    def mock_ticker_manager(self):
        """Mock ticker manager for testing."""
        with patch('utils.ticker_utils.ticker_manager') as mock_manager:
            yield mock_manager

    def test_get_ticker_symbol_success(self, mock_ticker_manager):
        """Test successful ticker symbol retrieval."""
        from get_ticker_symbol import get_ticker_symbol
        
        # Mock successful response
        mock_ticker_manager.get_symbol_by_name.return_value = "HAL"
        mock_ticker_manager.get_company_info.return_value = {
            "Symbol": "HAL",
            "Company_Name": "Hindustan Aeronautics Limited",
            "Series": "EQ"
        }
        
        result = get_ticker_symbol("Hindustan Aeronautics")
        
        assert result["success"] is True
        assert result["ticker_symbol"] == "HAL"
        assert result["company_info"]["Symbol"] == "HAL"
        assert result["search_term"] == "Hindustan Aeronautics"
        
        mock_ticker_manager.get_symbol_by_name.assert_called_once_with("Hindustan Aeronautics")
        mock_ticker_manager.get_company_info.assert_called_once_with("HAL")

    def test_get_ticker_symbol_not_found(self, mock_ticker_manager):
        """Test ticker symbol not found."""
        from get_ticker_symbol import get_ticker_symbol
        
        # Mock not found response
        mock_ticker_manager.get_symbol_by_name.return_value = None
        mock_ticker_manager.search_companies.return_value = [
            {"Symbol": "BEL", "Company_Name": "Bharat Electronics Limited"}
        ]
        
        result = get_ticker_symbol("HAL XYZ")
        
        assert result["success"] is False
        assert result["ticker_symbol"] is None
        assert "No ticker symbol found" in result["error"]
        assert len(result["similar_companies"]) == 1

    def test_get_ticker_symbol_invalid_input(self, mock_ticker_manager):
        """Test invalid input handling."""
        from get_ticker_symbol import get_ticker_symbol
        
        # Test empty string
        result = get_ticker_symbol("")
        assert result["success"] is False
        assert "Company name cannot be empty" in result["error"]
        
        # Test None
        result = get_ticker_symbol(None)
        assert result["success"] is False
        assert "Company name must be a non-empty string" in result["error"]
        
        # Test non-string
        result = get_ticker_symbol(123)
        assert result["success"] is False
        assert "Company name must be a non-empty string" in result["error"]

    def test_get_ticker_symbol_exception_handling(self, mock_ticker_manager):
        """Test exception handling in get_ticker_symbol."""
        from get_ticker_symbol import get_ticker_symbol
        
        mock_ticker_manager.get_symbol_by_name.side_effect = Exception("Database error")
        
        result = get_ticker_symbol("Hindustan Aeronautics")
        
        assert result["success"] is False
        assert "Database error" in result["error"]

    def test_search_companies_success(self, mock_ticker_manager):
        """Test successful company search."""
        from get_ticker_symbol import search_companies
        
        mock_ticker_manager.search_companies.return_value = [
            {"Symbol": "HAL", "Company_Name": "Hindustan Aeronautics Limited"},
            {"Symbol": "BEL", "Company_Name": "Bharat Electronics Limited"}
        ]
        
        result = search_companies("Hindustan", 5)
        
        assert result["success"] is True
        assert len(result["results"]) == 2
        assert result["count"] == 2
        assert result["search_term"] == "Hindustan"

    def test_search_companies_invalid_input(self, mock_ticker_manager):
        """Test invalid input for search_companies."""
        from get_ticker_symbol import search_companies
        
        # Test empty string
        result = search_companies("")
        assert result["success"] is False
        assert "Search term cannot be empty" in result["error"]


class TestFetchFinancialDataTool:
    """Test suite for fetch_financial_data tool."""

    @pytest.fixture
    def mock_financial_manager(self):
        """Mock financial data manager."""
        with patch('utils.financial_data.financial_data_manager') as mock_manager:
            yield mock_manager

    @pytest.fixture
    def mock_db_manager(self):
        """Mock database manager."""
        with patch('utils.database.db_manager') as mock_manager:
            yield mock_manager

    def test_fetch_and_store_stock_data_success(self, mock_financial_manager, mock_db_manager):
        """Test successful stock data fetching and storing."""
        from fetch_financial_data import fetch_and_store_stock_data
        
        # Mock successful responses
        mock_financial_manager.get_basic_stock_info.return_value = {
            "Symbol": "HAL",
            "Company_Name": "Hindustan Aeronautics Limited"
        }
        mock_financial_manager.get_current_financial_year.return_value = 2024
        
        import pandas as pd
        mock_df = pd.DataFrame({"column1": [1, 2, 3]})
        mock_financial_manager.get_financial_statements.return_value = mock_df
        mock_financial_manager.get_balance_sheet.return_value = mock_df
        mock_financial_manager.get_income_statement.return_value = mock_df
        mock_financial_manager.get_cash_flow_statement.return_value = mock_df
        mock_financial_manager.get_daily_price_history.return_value = mock_df
        mock_financial_manager.get_monthly_price_history.return_value = mock_df
        mock_financial_manager.get_intrinsic_pe_data.return_value = mock_df
        
        mock_db_manager.upsert_stock_data.return_value = True
        mock_db_manager.update_stock_field.return_value = True
        mock_db_manager.insert_dataframe.return_value = True
        
        result = fetch_and_store_stock_data("HAL.NS")
        
        assert result["success"] is True
        assert result["stock_symbol"] == "HAL"
        assert result["ticker"] == "HAL.NS"
        assert len(result["operations"]) > 0
        assert result["summary"]["successful_operations"] > 0

    def test_fetch_and_store_stock_data_partial_failure(self, mock_financial_manager, mock_db_manager):
        """Test partial failure in stock data operations."""
        from fetch_financial_data import fetch_and_store_stock_data
        
        # Mock mixed responses
        mock_financial_manager.get_basic_stock_info.return_value = None  # Failure
        mock_financial_manager.get_current_financial_year.return_value = 2024
        
        import pandas as pd
        mock_df = pd.DataFrame({"column1": [1, 2, 3]})
        mock_financial_manager.get_financial_statements.return_value = mock_df  # Success
        
        mock_db_manager.upsert_stock_data.return_value = False
        mock_db_manager.update_stock_field.return_value = True
        mock_db_manager.insert_dataframe.return_value = True
        
        result = fetch_and_store_stock_data("HAL.NS")
        
        assert len(result["errors"]) > 0
        assert "Failed to fetch basic stock information" in result["errors"]

    def test_fetch_sector_info_success(self, mock_financial_manager, mock_db_manager):
        """Test successful sector info fetching."""
        from fetch_financial_data import fetch_sector_info
        
        mock_financial_manager.get_sector_info_from_moneycontrol.return_value = {
            "Sector": "Aerospace & Defense",
            "Sector_PE": 22.5
        }
        mock_db_manager.update_stock_field.return_value = True
        
        result = fetch_sector_info("HAL")
        
        assert result["success"] is True
        assert result["stock_symbol"] == "HAL"
        assert result["sector_info"]["Sector"] == "Aerospace & Defense"

    def test_fetch_complete_stock_data(self, mock_financial_manager, mock_db_manager):
        """Test complete stock data workflow."""
        from fetch_financial_data import fetch_complete_stock_data
        
        # Mock all required functions
        mock_financial_manager.get_basic_stock_info.return_value = {"Symbol": "HAL"}
        mock_financial_manager.get_current_financial_year.return_value = 2024
        mock_financial_manager.get_sector_info_from_moneycontrol.return_value = {"Sector": "Aerospace & Defense"}
        
        import pandas as pd
        mock_df = pd.DataFrame({"column1": [1, 2, 3]})
        for method in ["get_financial_statements", "get_balance_sheet", "get_income_statement",
                      "get_cash_flow_statement", "get_daily_price_history", 
                      "get_monthly_price_history", "get_intrinsic_pe_data"]:
            getattr(mock_financial_manager, method).return_value = mock_df
        
        mock_db_manager.upsert_stock_data.return_value = True
        mock_db_manager.update_stock_field.return_value = True
        mock_db_manager.insert_dataframe.return_value = True
        
        result = fetch_complete_stock_data("HAL.NS")
        
        assert result["success"] is True
        assert result["stock_symbol"] == "HAL"
        assert "financial_data_results" in result
        assert "sector_info_results" in result


class TestDownloadReportsTool:
    """Test suite for download_reports tool."""

    @pytest.fixture
    def mock_data_agent(self):
        """Mock DataAcquisitionAgent."""
        with patch('data_agent.DataAcquisitionAgent') as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent
            yield mock_agent

    def test_download_annual_reports_success(self, mock_data_agent):
        """Test successful annual reports download."""
        from download_reports import download_annual_reports
        
        mock_data_agent.download_annual_reports.return_value = [
            "/path/to/report1.pdf",
            "/path/to/report2.pdf"
        ]
        
        result = download_annual_reports("HAL", [[2022, 2023], [2021, 2022]])
        
        assert result["success"] is True
        assert result["stock_symbol"] == "HAL"
        assert result["downloaded_count"] == 2
        assert len(result["pdf_paths"]) == 2
        
        # Verify the missing_years conversion
        expected_tuples = [(2022, 2023), (2021, 2022)]
        mock_data_agent.download_annual_reports.assert_called_once_with("HAL", expected_tuples)

    def test_download_annual_reports_invalid_input(self, mock_data_agent):
        """Test invalid input handling for download_annual_reports."""
        from download_reports import download_annual_reports
        
        # Test empty stock symbol
        result = download_annual_reports("")
        assert result["success"] is False
        assert "Stock symbol cannot be empty" in result["error"]
        
        # Test None stock symbol
        result = download_annual_reports(None)
        assert result["success"] is False
        assert "Stock symbol must be a non-empty string" in result["error"]
        
        # Test invalid missing_years format
        result = download_annual_reports("HAL", "invalid")
        assert result["success"] is False
        assert "missing_years must be a list" in result["error"]

    def test_download_annual_reports_invalid_year_ranges(self, mock_data_agent):
        """Test invalid year ranges in missing_years."""
        from download_reports import download_annual_reports
        
        # Test invalid year range (wrong number of elements)
        result = download_annual_reports("HAL", [[2022]])
        assert result["success"] is False
        assert "Each year range must contain exactly 2 years" in result["error"]
        
        # Test invalid year range (from >= to)
        result = download_annual_reports("HAL", [[2023, 2022]])
        assert result["success"] is False
        assert "From year must be less than to year" in result["error"]

    def test_check_existing_reports_success(self, mock_data_agent):
        """Test successful check of existing reports."""
        from download_reports import check_existing_reports
        
        mock_data_agent.check_existing_data.return_value = [
            (2022, 2023),
            (2021, 2022)
        ]
        
        result = check_existing_reports("HAL")
        
        assert result["success"] is True
        assert result["stock_symbol"] == "HAL"
        assert result["missing_count"] == 2
        assert result["missing_years"] == [[2022, 2023], [2021, 2022]]

    def test_check_existing_reports_invalid_input(self, mock_data_agent):
        """Test invalid input for check_existing_reports."""
        from download_reports import check_existing_reports
        
        # Test empty stock symbol
        result = check_existing_reports("")
        assert result["success"] is False
        assert "Stock symbol cannot be empty" in result["error"]

    def test_download_reports_exception_handling(self, mock_data_agent):
        """Test exception handling in download tools."""
        from download_reports import download_annual_reports
        
        mock_data_agent.download_annual_reports.side_effect = Exception("Download failed")
        
        result = download_annual_reports("HAL")
        
        assert result["success"] is False
        assert "Download failed" in result["error"]


class TestToolMetadata:
    """Test tool metadata definitions."""

    def test_get_ticker_symbol_metadata(self):
        """Test get_ticker_symbol tool metadata."""
        from get_ticker_symbol import TOOL_METADATA
        
        metadata = TOOL_METADATA["get_ticker_symbol"]
        assert metadata["name"] == "get_ticker_symbol"
        assert "company_name" in metadata["parameters"]["properties"]
        assert "company_name" in metadata["parameters"]["required"]

    def test_fetch_financial_data_metadata(self):
        """Test fetch_financial_data tool metadata."""
        from fetch_financial_data import TOOL_METADATA
        
        assert "fetch_and_store_stock_data" in TOOL_METADATA
        assert "fetch_sector_info" in TOOL_METADATA
        assert "fetch_complete_stock_data" in TOOL_METADATA
        
        metadata = TOOL_METADATA["fetch_and_store_stock_data"]
        assert metadata["name"] == "fetch_and_store_stock_data"
        assert "ticker" in metadata["parameters"]["properties"]

    def test_download_reports_metadata(self):
        """Test download_reports tool metadata."""
        from download_reports import TOOL_METADATA
        
        assert "download_annual_reports" in TOOL_METADATA
        assert "check_existing_reports" in TOOL_METADATA
        
        metadata = TOOL_METADATA["download_annual_reports"]
        assert metadata["name"] == "download_annual_reports"
        assert "stock_symbol" in metadata["parameters"]["properties"] 