# VyasaQuant Frontend-Backend Integration Guide

This guide explains how the React frontend integrates with the stability checker agent through the FastAPI server.

## 🔗 Integration Architecture

```
Frontend (React) → API Server (FastAPI) → Stability Checker Agent → Data Sources
```

## 📊 Data Flow

1. **User Input**: User enters stock symbol in frontend
2. **API Request**: Frontend sends POST request to `/api/analyze`
3. **Agent Invocation**: API server creates agent context and runs analysis
4. **Data Fetching**: Agent fetches EPS data from multiple sources
5. **Analysis**: Agent calculates stability score and growth rate
6. **Response**: Structured response sent back to frontend
7. **Display**: Frontend shows analysis results with charts and metrics

## 🚀 Getting Started

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv vyasaquant_env
source vyasaquant_env/bin/activate  # Windows: vyasaquant_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start the API server
python start_server.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 3. Test Integration

```bash
# Test API directly
curl -X POST "http://localhost:8000/api/analyze" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "RELIANCE"}'

# Or run the integration test
cd backend
python test_api_integration.py
```

## 🔧 API Endpoints

### POST /api/analyze

Analyzes a stock and returns comprehensive analysis data.

**Request:**
```json
{
  "symbol": "RELIANCE"
}
```

**Response:**
```json
{
  "symbol": "RELIANCE",
  "company_name": "Reliance Industries",
  "stability_score": 75.0,
  "value_analysis": {
    "intrinsic_value": 2500.0,
    "current_price": 2400.0,
    "recommendation": "BUY"
  },
  "key_metrics": {
    "pe_ratio": 22.5,
    "pb_ratio": 1.8,
    "debt_equity": 0.3,
    "roe": 15.2
  }
}
```

### GET /health

Health check endpoint for monitoring API status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1672531200.0,
  "agent_initialized": true
}
```

## 🔄 Frontend Integration

### API Call Implementation

The frontend uses Axios to make API calls:

```typescript
// In src/App.tsx
const handleAnalyze = async () => {
  try {
    const response = await axios.post('/api/analyze', {
      symbol: symbol.toUpperCase(),
    });
    setAnalysis(response.data);
  } catch (err) {
    setError('Failed to analyze stock. Please try again.');
  }
};
```

### Response Processing

The frontend processes the API response to display:

- **Company Information**: Name and symbol
- **Stability Score**: Visual progress indicator
- **Value Analysis**: Current price vs intrinsic value
- **Recommendation**: Buy/Sell/Hold with color coding
- **Key Metrics**: Financial ratios in a grid layout

## 🧠 Agent Integration

### Stability Checker Agent Workflow

1. **Ticker Resolution**: Convert company name to ticker symbol
2. **EPS Data Collection**: Fetch 4 years of EPS data
3. **Trend Analysis**: Check if EPS is consistently increasing
4. **Growth Rate Calculation**: Calculate compound annual growth rate
5. **Stability Assessment**: Apply criteria (EPS increasing + growth > 10%)
6. **Recommendation Generation**: Provide buy/sell recommendation

### Agent Configuration

The agent uses configuration from `backend/config/agents.yaml`:

```yaml
stability_checker_agent:
  agent:
    name: "Stock Stability Checker"
    id: "stability_checker"
  
  stability_analysis:
    criteria:
      eps_years: 4
      eps_growth_threshold: 10
  
  servers:
    data_acquisition_server:
      script: "mcp_server_stock_data.py"
      cwd: "mcp_servers/data_acquisition_server"
```

## 📁 File Structure

```
backend/
├── api/
│   ├── __init__.py
│   └── server.py              # FastAPI application
├── agents/
│   └── stability_checker_agent/
│       ├── agent.py           # Main agent entry point
│       ├── core/              # Agent core components
│       └── modules/           # Agent modules
├── config/
│   └── agents.yaml           # Agent configuration
├── start_server.py           # Server startup script
└── test_api_integration.py   # Integration tests

frontend/
├── src/
│   ├── App.tsx              # Main React component
│   ├── index.tsx            # Entry point
│   └── index.css            # Styles
├── public/
│   └── index.html           # HTML template
└── package.json             # Dependencies
```

## 🛠️ Development Workflow

### Adding New Features

1. **Backend**: Add new endpoints to `api/server.py`
2. **Agent**: Extend agent capabilities in `agents/stability_checker_agent/`
3. **Frontend**: Update React components to use new endpoints
4. **Testing**: Add tests for new functionality

### Error Handling

- **API Errors**: Handled by FastAPI with structured error responses
- **Agent Errors**: Logged and converted to user-friendly messages
- **Frontend Errors**: Displayed as alerts with retry options

### Performance Considerations

- **Caching**: Agent results can be cached for repeated requests
- **Async Processing**: FastAPI handles concurrent requests efficiently
- **Connection Pooling**: Database connections are pooled for performance

## 🧪 Testing

### Unit Tests

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

### Integration Tests

```bash
# Test API integration
cd backend
python test_api_integration.py

# Test full stack
# 1. Start backend: python start_server.py
# 2. Start frontend: npm start
# 3. Test in browser: http://localhost:3000
```

### Manual Testing

1. **API Testing**: Use http://localhost:8000/docs for interactive testing
2. **Frontend Testing**: Use the React app to test user workflows
3. **Agent Testing**: Run the agent directly for debugging

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=postgresql://user:password@localhost/vyasaquant
GOOGLE_API_KEY=your_google_api_key
LLAMA_CLOUD_API_KEY=your_llama_api_key
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_VERSION=v1
```

### CORS Configuration

The API server is configured to allow requests from the frontend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 Deployment

### Development Deployment

1. Start backend: `python start_server.py`
2. Start frontend: `npm start`
3. Access: http://localhost:3000

### Production Deployment

1. **Backend**: Use Gunicorn + Uvicorn for production ASGI serving
2. **Frontend**: Build with `npm run build` and serve with Nginx
3. **Database**: Configure PostgreSQL and ChromaDB for production
4. **Environment**: Set production environment variables

## 📊 Monitoring

### API Monitoring

- **Health Checks**: `/health` endpoint for monitoring
- **Logging**: Structured logging for debugging
- **Metrics**: Request/response times and error rates

### Agent Monitoring

- **Execution Logs**: Agent execution traces
- **Performance**: Analysis completion times
- **Errors**: Failed analysis attempts

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** changes in both frontend and backend
4. **Test** integration thoroughly
5. **Submit** a pull request

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://reactjs.org/docs/
- **Material-UI**: https://mui.com/
- **Agent Architecture**: See `backend/agents/stability_checker_agent/README.md`

## 🎯 Next Steps

1. **Enhance Analysis**: Add more financial metrics and analysis types
2. **Real-time Updates**: Implement WebSocket for real-time data
3. **User Authentication**: Add user accounts and saved analyses
4. **Advanced Charting**: Add interactive charts and visualizations
5. **Mobile Support**: Optimize for mobile devices 