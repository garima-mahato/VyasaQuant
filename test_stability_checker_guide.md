# 🧪 Stability Checker Agent Testing Guide

## Quick Start Testing Commands

```bash
# 1. Run comprehensive automated tests
python test_stability_checker_refactored.py

# 2. Run interactive agent (manual testing)
python agents/stability_checker_agent/agent.py

# 3. Run integration tests
python agents/stability_checker_agent/test_agent_integration.py

# 4. Test individual MCP tools
python -c "from mcp_servers.data_acquisition_server.tools.get_ticker_symbol import get_ticker_symbol; print(get_ticker_symbol('Reliance'))"
```

## 🎯 Testing Levels

### Level 1: Component Testing (Unit Tests)
Test individual components in isolation:

```python
# Test utils directly
from utils.financial_data import financial_data_manager
result = financial_data_manager.get_basic_stock_info("RELIANCE.NS")

# Test MCP tools directly  
from mcp_servers.data_acquisition_server.tools.database_tools import get_eps_data
eps_result = get_eps_data("RELIANCE", 4)

# Test calculation logic
initial_eps, final_eps = 10.0, 17.0
years = 3
cagr = (((final_eps / initial_eps) ** (1/years)) - 1) * 100
print(f"CAGR: {cagr:.2f}%")
```

### Level 2: Integration Testing 
Test component interactions:

```bash
# Run automated integration tests
python test_stability_checker_refactored.py
```

### Level 3: End-to-End Testing
Test complete workflows:

```bash
# Run interactive agent
python agents/stability_checker_agent/agent.py
```

## 🚀 Testing Scenarios

### Scenario 1: Basic Functionality Test
```bash
python test_stability_checker_refactored.py
```
**Expected Output:**
- ✅ Configuration loaded
- ✅ Utils imported
- ✅ MCP tools accessible
- ✅ Logic tests pass

### Scenario 2: Interactive Agent Test
```bash
cd agents/stability_checker_agent
python agent.py
```
**Test Inputs:**
```
📊 Enter company name → Reliance Industries
📊 Enter company name → TCS  
📊 Enter company name → INFY
📊 Enter company name → exit
```

### Scenario 3: Manual MCP Server Test
```bash
# Start data acquisition server
python mcp_servers/data_acquisition_server/server.py

# In another terminal, test tools
python -c "
from mcp_servers.data_acquisition_server.tools.get_ticker_symbol import get_ticker_symbol
from mcp_servers.data_acquisition_server.tools.database_tools import get_eps_data
print('Ticker:', get_ticker_symbol('Reliance Industries'))
print('EPS:', get_eps_data('RELIANCE', 4))
"
```

## 📊 Test Cases

### Test Case 1: Growing EPS Stock (Should PASS)
- **Company**: Growing Tech Company
- **EPS Data**: [10.0, 12.0, 14.5, 17.0] 
- **Expected CAGR**: ~19.25%
- **Expected Result**: ✅ PASS (EPS increasing + CAGR > 10%)

### Test Case 2: Declining EPS Stock (Should FAIL)  
- **Company**: Declining Manufacturing Company
- **EPS Data**: [20.0, 18.0, 15.0, 12.0]
- **Expected CAGR**: ~-15.96%
- **Expected Result**: ❌ FAIL (EPS decreasing)

### Test Case 3: Low Growth Stock (Should FAIL)
- **Company**: Stable Utility Company  
- **EPS Data**: [10.0, 10.5, 11.0, 11.2]
- **Expected CAGR**: ~3.85%
- **Expected Result**: ❌ FAIL (CAGR < 10%)

## 🔧 Debugging & Troubleshooting

### Common Issues & Solutions

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'utils'
# Solution: Run from project root
cd /d/Projects/GitHub/StockAgent/VyasaQuant
python test_stability_checker_refactored.py
```

#### 2. Configuration Errors
```bash
# Error: Configuration file not found
# Solution: Check file exists
ls agents/stability_checker_agent/config/profiles.yaml
```

#### 3. Database Connection Issues
```bash
# Error: Database connection failed
# Solution: Check PostgreSQL service and .env file
# Expected: Database tests will show warnings but still pass
```

#### 4. API Rate Limits
```bash
# Error: API rate limit exceeded
# Solution: Add delays between requests or use mock data
```

## 📝 Test Environment Setup

### Prerequisites
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables (optional for testing)
export GOOGLE_API_KEY="your_key_here"
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="vyasaquant"

# 3. Ensure project structure
ls agents/stability_checker_agent/
# Should show: agent.py, config/, core/, modules/, memory/
```

### Mock Data Testing
```python
# Create test data for offline testing
test_companies = {
    "RELIANCE": {
        "eps_data": [
            {"year": 2020, "eps": 50.0},
            {"year": 2021, "eps": 60.0}, 
            {"year": 2022, "eps": 72.0},
            {"year": 2023, "eps": 86.0}
        ]
    }
}
```

## 🎯 Performance Testing

### Response Time Benchmarks
- **Ticker Lookup**: < 1 second
- **EPS Data Fetch**: < 3 seconds  
- **Analysis Calculation**: < 0.1 seconds
- **Complete Workflow**: < 10 seconds

### Load Testing
```python
import asyncio
import time

async def test_concurrent_requests():
    companies = ["RELIANCE", "TCS", "INFY", "WIPRO", "HCLTECH"]
    
    start_time = time.time()
    # Test multiple companies simultaneously
    tasks = [test_single_company(company) for company in companies]
    results = await asyncio.gather(*tasks)
    duration = time.time() - start_time
    
    print(f"Processed {len(companies)} companies in {duration:.2f} seconds")
```

## 📋 Test Checklist

### ✅ Pre-Deployment Checklist
- [ ] All automated tests pass
- [ ] Interactive agent responds correctly  
- [ ] Configuration loads successfully
- [ ] MCP tools are accessible
- [ ] Logic calculations are accurate
- [ ] Error handling works properly
- [ ] Memory usage is reasonable
- [ ] Response times are acceptable

### ✅ Production Readiness Checklist  
- [ ] Database integration tested
- [ ] API rate limits handled
- [ ] Logging is comprehensive
- [ ] Error messages are helpful
- [ ] Documentation is complete
- [ ] Security considerations addressed

## 🚀 Next Steps After Testing

1. **If All Tests Pass:**
   ```bash
   # Ready for production use
   python agents/stability_checker_agent/agent.py
   ```

2. **If Tests Fail:**
   - Review error messages
   - Check configuration files
   - Verify dependencies
   - Check database connectivity
   - Review network permissions

3. **For Real Usage:**
   - Set up PostgreSQL database
   - Configure environment variables
   - Populate ticker database
   - Test with real market data
   - Monitor performance metrics

## 📚 Additional Resources

- **Agent Configuration**: `agents/stability_checker_agent/config/profiles.yaml`
- **Utils Documentation**: `utils/` directory
- **MCP Tools**: `mcp_servers/data_acquisition_server/tools/`
- **Core Framework**: `agents/stability_checker_agent/core/`
- **Processing Modules**: `agents/stability_checker_agent/modules/` 