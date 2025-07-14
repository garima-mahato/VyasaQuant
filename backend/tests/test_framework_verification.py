"""
Simple test to verify the testing framework is working correctly.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock


class TestFrameworkVerification:
    """Test suite to verify the testing framework is working."""

    def test_basic_functionality(self):
        """Test basic functionality to verify pytest is working."""
        assert True
        assert 1 + 1 == 2
        assert "hello" == "hello"

    def test_mock_functionality(self):
        """Test that mocking functionality works."""
        mock_obj = MagicMock()
        mock_obj.test_method.return_value = "mocked_value"
        
        result = mock_obj.test_method()
        assert result == "mocked_value"
        mock_obj.test_method.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async functionality."""
        async def async_function():
            await asyncio.sleep(0.01)
            return "async_result"
        
        result = await async_function()
        assert result == "async_result"

    @pytest.mark.asyncio
    async def test_async_mock_functionality(self):
        """Test async mock functionality."""
        mock_async = AsyncMock()
        mock_async.return_value = "async_mock_result"
        
        result = await mock_async()
        assert result == "async_mock_result"
        mock_async.assert_called_once()

    def test_fixtures(self, sample_stock_data):
        """Test that fixtures from conftest.py work."""
        assert sample_stock_data is not None
        assert "symbol" in sample_stock_data
        assert sample_stock_data["symbol"] == "HAL"

    def test_environment_variables(self, mock_env_vars):
        """Test that environment variable mocking works."""
        import os
        assert os.environ.get("DB_HOST") == "localhost"
        assert os.environ.get("DB_NAME") == "test_vyasaquant"

    @pytest.mark.unit
    def test_unit_marker(self):
        """Test that unit test marker works."""
        assert True

    @pytest.mark.integration
    def test_integration_marker(self):
        """Test that integration test marker works."""
        assert True

    def test_sample_data_loading(self):
        """Test loading sample data from fixtures."""
        import json
        from pathlib import Path
        
        fixtures_dir = Path(__file__).parent / "fixtures" / "sample_data"
        ticker_data_file = fixtures_dir / "sample_ticker_data.json"
        
        if ticker_data_file.exists():
            with open(ticker_data_file) as f:
                data = json.load(f)
                assert "ticker_data" in data
                assert len(data["ticker_data"]) > 0
                assert data["ticker_data"][0]["Symbol"] == "HAL" 