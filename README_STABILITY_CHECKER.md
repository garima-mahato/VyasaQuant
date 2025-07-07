# VyasaQuant Stability Checker Agent

An AI-powered stock stability analysis agent that evaluates stocks based on Earnings Per Share (EPS) growth metrics using Google's Gemini AI model. This agent uses the existing data acquisition MCP tools directly for a simplified and efficient architecture.

## Overview

The Stability Checker Agent is part of the VyasaQuant multi-agent system designed to analyze stock stability using a comprehensive EPS growth analysis approach. It connects directly to the Data Acquisition MCP Server and uses existing tools, avoiding unnecessary architectural complexity.

## Features

- **AI-Powered Analysis**: Uses Google's Gemini AI model for intelligent EPS data extraction and reasoning
- **Direct MCP Integration**: Uses existing data acquisition MCP tools directly (simplified architecture)
- **Web Search Fallback**: Automatically searches the web for missing EPS data
- **Compound Growth Rate Calculation**: Calculates EPS growth rate using compound annual growth rate (CAGR)
- **Comprehensive Reporting**: Provides detailed analysis with AI-generated reasoning
- **Async Processing**: Fully asynchronous operation for efficient performance

## Simplified Architecture

```
User → Stability Checker Agent → Data Acquisition MCP Server → Data Sources
```

**No separate MCP server needed!** The agent connects directly to the existing data acquisition server.

## Analysis Workflow

The agent follows this structured workflow:

1. **Ticker Symbol Resolution**: Uses `get_ticker_symbol` tool from data acquisition server
2. **EPS Data Collection**: Uses `fetch_complete_stock_data` tool with web search fallback
3. **Trend Analysis**: Checks if EPS is consistently increasing across all years
4. **Growth Rate Calculation**: Calculates compound annual growth rate (CAGR)
5. **Stability Assessment**: Determines if stock passes stability criteria:
   - EPS must be increasing across all years
   - EPS growth rate must be > 10%
6. **AI Reasoning**: Generates detailed analysis and recommendation

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Create .env file
GOOGLE_API_KEY=your_google_api_key_here
```

3. Ensure data acquisition MCP server is configured in `config/mcp_config.json`

## Usage

### Basic Usage

```python
import asyncio
from agents.stability_checker_agent import StabilityCheckerAgent

async def check_stock():
    agent = StabilityCheckerAgent()
    await agent.initialize()  # Connects to data_acquisition_server
    
    # Using company name
    result = await agent.process({
        "company_name": "Reliance Industries",
        "years_to_analyze": 4
    })
    
    # Using ticker symbol
    result = await agent.process({
        "ticker_symbol": "RELIANCE",
        "years_to_analyze": 4
    })
    
    print(f"Passes to Round 2: {result['passes_to_round_2']}")
    print(f"Reasoning: {result['reasoning']}")
    
    await agent.cleanup()

asyncio.run(check_stock())
```

### Running the Example

```bash
python example_stability_check.py
```

## Response Format

The agent returns a comprehensive response with the following structure:

```json
{
  "success": true,
  "company_name": "Reliance Industries",
  "ticker_symbol": "RELIANCE",
  "eps_data": [
    {
      "year": 2024,
      "eps_value": 78.90,
      "source": "web_search",
      "confidence": 0.8
    }
  ],
  "eps_growth_rate": 12.5,
  "is_increasing": true,
  "passes_stability_check": true,
  "passes_to_round_2": true,
  "reasoning": "AI-generated detailed analysis...",
  "errors": [],
  "warnings": [],
  "processing_time": 15.2
}
```

## Stability Criteria

A stock passes the stability check if:

1. **EPS Trend**: EPS must be consistently increasing across all analyzed years
2. **Growth Rate**: EPS compound annual growth rate (CAGR) must be > 10%
3. **Data Quality**: Sufficient EPS data must be available for analysis

## EPS Growth Rate Calculation

The agent calculates the compound annual growth rate (CAGR) using:

```
EPS-GR = ((EPS_final / EPS_initial) ^ (1/years)) - 1) * 100
```

Where:
- `EPS_final`: EPS of the most recent year
- `EPS_initial`: EPS of the earliest year in the analysis period
- `years`: Number of years between initial and final EPS

## Data Sources

The agent uses multiple data sources in order of preference:

1. **Data Acquisition MCP Tools**: Primary source using existing tools
   - `get_ticker_symbol` for ticker resolution
   - `fetch_complete_stock_data` for financial data (Yahoo Finance)
2. **Web Search**: Fallback using Google search with AI extraction
3. **AI Processing**: Gemini AI for extracting EPS values from unstructured data

## Architecture

### Simplified Agent Structure
```
agents/stability_checker_agent/
├── __init__.py          # Module initialization
├── agent.py             # Main agent implementation (connects to data_acquisition_server)
└── schemas.py           # Data structures and schemas
```

### Used MCP Server (Existing)
```
mcp_servers/data_acquisition_server/
├── server.py            # Existing MCP server
└── tools/
    ├── get_ticker_symbol.py      # Used by stability agent
    ├── fetch_financial_data.py   # Used by stability agent
    └── ...
```

## Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Required for Gemini AI integration
- Other environment variables as needed by data acquisition tools

### MCP Configuration

The agent uses the existing data acquisition MCP server:

```json
{
  "mcpServers": {
    "data_acquisition": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "./mcp_servers/data_acquisition_server"
    }
  }
}
```

## Testing

Run the test suite:

```bash
python test_stability_checker.py
```

The test script includes:
- Company name-based analysis
- Ticker symbol-based analysis
- Custom EPS data testing
- Direct data acquisition tools testing
- Error handling verification

## Error Handling

The agent includes comprehensive error handling for:

- Missing or invalid input data
- API failures (Gemini AI, web search)
- MCP server connection issues
- Data parsing errors
- Network timeouts

## Performance Considerations

- **Async Processing**: All operations are asynchronous for better performance
- **Direct Tool Usage**: No unnecessary MCP server wrapper layer
- **Rate Limiting**: Built-in delays to respect API rate limits
- **Caching**: Results can be cached to avoid redundant API calls
- **Timeout Handling**: Configurable timeouts for web requests

## Benefits of Simplified Architecture

1. **Simpler Setup**: Only one MCP server to manage (data_acquisition)
2. **Direct Data Flow**: Fewer hops between components
3. **Easier Debugging**: Clear path from agent to data tools
4. **Better Performance**: Less overhead
5. **Easier Testing**: Test agent directly with existing tools
6. **No Redundancy**: Avoids unnecessary wrapper layers

## Future Enhancements

1. **Enhanced EPS Extraction**: Better parsing of income statement data from MCP tools
2. **Additional Data Sources**: Integration with more financial data APIs
3. **Machine Learning**: ML-based EPS trend prediction
4. **Risk Assessment**: Additional risk metrics beyond EPS
5. **Sector Analysis**: Sector-specific stability criteria

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the test files for usage examples
- Review the error logs for debugging
- Ensure all environment variables are set correctly
- Verify data acquisition MCP server connectivity

---

**Note**: This agent uses the simplified architecture approach, connecting directly to existing MCP tools rather than creating unnecessary wrapper layers. This makes it more maintainable and efficient. 