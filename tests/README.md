# VyasaQuant Data Acquisition Agent - Testing Framework

This directory contains comprehensive tests for the VyasaQuant Data Acquisition Agent system, including unit tests, integration tests, and end-to-end workflow tests.

## Test Structure

```
tests/
├── conftest.py                          # Pytest configuration and shared fixtures
├── pytest.ini                          # Pytest settings
├── run_tests.py                         # Test runner script
├── README.md                           # This file
├── fixtures/                           # Test data and fixtures
│   └── sample_data/                    # Sample JSON data for testing
│       ├── sample_ticker_data.json     # Sample ticker symbols
│       └── sample_financial_data.json  # Sample financial data
├── unit/                               # Unit tests
│   ├── test_agents/                    # Agent unit tests
│   │   └── test_data_acquisition_agent.py
│   └── test_mcp_servers/               # MCP server unit tests
│       └── test_data_acquisition_tools.py
└── integration/                        # Integration tests
    └── test_data_acquisition_integration.py
```

## Test Categories

### Unit Tests
- **Agent Tests**: Test individual agent functionality in isolation
- **Tool Tests**: Test MCP tools with mocked dependencies
- **Component Tests**: Test individual components like data parsers, database managers

### Integration Tests
- **Agent-Server Communication**: Test MCP client-server communication
- **Workflow Tests**: Test complete data acquisition workflows
- **Error Handling**: Test error scenarios across components

### Fixtures and Mock Data
- **Sample Data**: Realistic test data for ticker symbols, financial statements
- **Mock Objects**: Pre-configured mock objects for external dependencies
- **Environment Setup**: Test environment configuration

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install pytest pytest-asyncio pytest-mock pytest-cov pytest-xdist coverage
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### Using the Test Runner

The project includes a convenient test runner script:

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run with coverage report
python run_tests.py --coverage

# Run specific test file
python run_tests.py --file tests/unit/test_agents/test_data_acquisition_agent.py

# Run specific test function
python run_tests.py --function test_agent_initialization

# Run tests in parallel
python run_tests.py --parallel 4

# Verbose output
python run_tests.py --verbose
```

### Using Pytest Directly

```bash
# Run all tests
pytest

# Run with markers
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m agent             # Agent-related tests
pytest -m tools             # Tool-related tests

# Run specific test file
pytest tests/unit/test_agents/test_data_acquisition_agent.py

# Run with coverage
pytest --cov=agents --cov=mcp_servers --cov-report=html

# Run specific test function
pytest -k "test_agent_initialization"

# Verbose output
pytest -v
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.agent` - Agent-related tests
- `@pytest.mark.tools` - Tool-related tests
- `@pytest.mark.mcp` - MCP server tests
- `@pytest.mark.asyncio` - Async tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.requires_db` - Tests requiring database
- `@pytest.mark.requires_network` - Tests requiring network access

## Test Environment Setup

### Environment Variables

Tests use mocked environment variables by default. For integration tests with real services, set:

```bash
# Database configuration
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=test_vyasaquant
export DB_USER=test_user
export DB_PASSWORD=test_password

# Test configuration
export LOG_LEVEL=DEBUG
export CHROMA_DB_PATH=./test_chroma_db
```

### Mock Configuration

Tests extensively use mocks to avoid hitting external services:

- **Database**: Mocked database operations
- **External APIs**: Mocked yfinance, NSE, MoneyControl APIs
- **File Operations**: Mocked file downloads and storage
- **Network Requests**: Mocked HTTP requests

## Writing New Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Unit Test

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.data_acquisition_agent.agent import DataAcquisitionAgent

class TestDataAcquisitionAgent:
    @pytest.fixture
    def agent(self):
        return DataAcquisitionAgent()

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent, mock_mcp_client):
        with patch('agents.base.mcp_client.MCPClient', return_value=mock_mcp_client):
            result = await agent.initialize()
            assert result is True
            assert agent.initialized is True
```

### Example Integration Test

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_complete_workflow(self, mock_env_vars):
    agent = DataAcquisitionAgent()
    
    # Setup mocks for complete workflow
    with patch('agents.base.mcp_client.MCPClient') as mock_client_class:
        # Configure mock client
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"success": True}
        mock_client_class.return_value = mock_client
        
        # Test workflow
        await agent.initialize()
        result = await agent.process_stock_comprehensive("RELIANCE")
        
        assert result["status"] == "completed"
```

### Available Fixtures

Common fixtures available in `conftest.py`:

- `mock_env_vars` - Mocked environment variables
- `sample_stock_data` - Sample stock information
- `sample_financial_statements` - Sample financial data
- `mock_yfinance_ticker` - Mocked yfinance Ticker object
- `mock_mcp_client` - Mocked MCP client
- `mock_database_manager` - Mocked database manager
- `sample_annual_reports` - Sample reports data

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest --cov=agents --cov=mcp_servers --cov-report=xml --cov-report=term

# Run only fast tests in CI
pytest -m "not slow"

# Run with parallel execution
pytest -n auto
```

## Test Coverage

Aim for high test coverage:

- **Unit Tests**: >90% coverage for individual components
- **Integration Tests**: Cover all major workflows
- **Error Handling**: Test all error scenarios

Check coverage:
```bash
pytest --cov=agents --cov=mcp_servers --cov-report=html
# Open htmlcov/index.html to view detailed coverage report
```

## Debugging Tests

For debugging failed tests:

```bash
# Run with extra verbosity
pytest -vv

# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Run specific failing test
pytest tests/unit/test_agents/test_data_acquisition_agent.py::TestDataAcquisitionAgent::test_failing_method -v
```

## Best Practices

### Test Organization
- Keep tests focused and atomic
- Use descriptive test names
- Group related tests in classes
- Use appropriate markers

### Mocking Strategy
- Mock external dependencies
- Use realistic test data
- Don't mock what you're testing
- Verify mock interactions when important

### Async Testing
- Use `@pytest.mark.asyncio` for async tests
- Use `AsyncMock` for async mocks
- Test both success and error scenarios

### Performance
- Keep tests fast
- Use markers to separate slow tests
- Mock expensive operations
- Use parallel execution for large test suites

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all paths are correctly set in `conftest.py`
2. **Async Issues**: Use `AsyncMock` for async functions
3. **Environment Variables**: Use `mock_env_vars` fixture
4. **Database Errors**: Ensure database mocks are properly configured

### Getting Help

- Check test logs for detailed error information
- Use pytest's built-in debugging features
- Refer to existing tests for patterns and examples
- Run tests individually to isolate issues 