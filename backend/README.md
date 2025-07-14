# VyasaQuant Backend

This is the backend service for the VyasaQuant stock analysis system.

## Overview
A comprehensive stock analysis system that evaluates Indian stocks through multiple rounds of fundamental analysis to provide buy/sell recommendations based on stability and intrinsic value calculation.

## Architecture

### Core Components
1. **Data Acquisition Agent** (`agents/data_acquisition_agent/`)
2. **Data Processing & Storage Layer** (`data_processing/`)
3. **Stability Checker Agent** (`agents/stability_checker_agent/`)
4. **Value Analysis Agent** (planned)
5. **Recommendation Agent** (planned)
6. **MCP Servers** (`mcp_servers/`)
7. **REST API Server** (`api/server.py`)

### System Architecture

```mermaid
flowchart TD
    %% Style Definitions (Dark Colors)
    classDef component fill:#1e293b,stroke:#3b82f6,stroke-width:1.5px,color:#ffffff;
    classDef store fill:#3f3f46,stroke:#facc15,stroke-width:1.5px,color:#ffffff;
    classDef activity fill:#111827,stroke:#9ca3af,stroke-dasharray: 5 5,color:#ffffff;

    classDef requestArrow stroke:#3b82f6,stroke-width:2px;
    classDef responseArrow stroke:#ef4444,stroke-width:2px;

    %% Nodes
    UI[React Frontend]:::activity
    API[FastAPI Server]:::component
    RA([Recommendation Agent]):::component
    DA([Data Acquisition Agent]):::component
    DPL([Data Processing & Storage Layer]):::component
    G[Google]:::store
    NSE[NSE]:::store
    MC[Moneycontrol]:::store
    YF[Yahoo Finance]:::store
    ChromaDB[(ChromaDB)]:::store
    Postgres[(Postgres DB)]:::store
    SC([Stability Checker Agent]):::component
    VA([Value Analysis Agent]):::component

    %% Requests
    UI -->|POST /api/analyze| API:::requestArrow
    API -->|Query| SC:::requestArrow
    SC -->|Fetch data| DA:::requestArrow
    DA --> G:::requestArrow
    DA --> NSE:::requestArrow
    DA --> MC:::requestArrow
    SC --> DPL:::requestArrow
    DPL --> ChromaDB:::requestArrow
    DPL --> Postgres:::requestArrow
```

## Setup

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Virtual environment (recommended)

### Installation

1. **Create and activate virtual environment:**
```bash
python -m venv vyasaquant_env
source vyasaquant_env/bin/activate  # On Windows: vyasaquant_env\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
Create a `.env` file in the backend directory with:
```env
DATABASE_URL=postgresql://user:password@localhost/vyasaquant
GOOGLE_API_KEY=your_google_api_key
LLAMA_CLOUD_API_KEY=your_llama_api_key
# Add other required environment variables
```

4. **Initialize database:**
```bash
# Run database setup scripts
python database/db_scripts/setup.py
```

## Usage

### Running the API Server (Recommended)
```bash
# Start the FastAPI server
python start_server.py

# Or alternatively
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

The API server will be available at:
- **API Base URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API Explorer**: http://localhost:8000/redoc

### Running the Data Processing Module
```bash
python -m data_processing.main
```

### Running the Stability Checker Agent (Interactive)
```bash
cd agents/stability_checker_agent
python agent.py
```

### Running Tests
```bash
pytest
```

## API Endpoints

The REST API provides the following endpoints:

### Stock Analysis
- **POST /api/analyze** - Analyze stock stability and provide recommendations
  - Request body: `{"symbol": "RELIANCE"}`
  - Response: Comprehensive stock analysis with stability score, recommendations, and key metrics

### Health Check
- **GET /health** - API health status
- **GET /** - API information and available endpoints

### Example Usage

```bash
# Analyze a stock
curl -X POST "http://localhost:8000/api/analyze" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "RELIANCE"}'

# Check API health
curl "http://localhost:8000/health"
```

### Available MCP Servers
- **Data Acquisition Server**: Handles data fetching from various sources
- Located in `mcp_servers/data_acquisition_server/`

## Configuration

Configuration files are located in the `config/` directory:
- `agents.yaml` - Agent configurations
- `servers.yaml` - Server configurations  
- `mcp_config.json` - MCP server configurations

## Data Processing

The data processing pipeline handles:
- Stock data ingestion
- Data cleaning and validation
- Storage in PostgreSQL and ChromaDB
- Real-time data updates

## Frontend Integration

The backend provides a REST API that integrates seamlessly with the React frontend:

1. **Stock Analysis Flow**:
   - Frontend sends POST request to `/api/analyze`
   - Backend invokes stability checker agent
   - Agent fetches data and performs analysis
   - Results are formatted and returned to frontend

2. **Response Format**:
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

## Development

### API Development
The API server is built with FastAPI and provides:
- **Automatic API documentation** (OpenAPI/Swagger)
- **Request/response validation** with Pydantic
- **CORS support** for frontend integration
- **Async support** for optimal performance

### Adding New Endpoints
1. Add new models to `api/server.py`
2. Create endpoint functions
3. Test using the interactive docs at `/docs`

### Agent Integration
The API server integrates with agents through:
- **AgentContext** for session management
- **MultiMCP** for MCP server communication
- **Structured result parsing** for consistent responses

## Testing

Run the test suite:
```bash
pytest tests/
```

Test coverage:
```bash
pytest --cov=. tests/
```

Test the API:
```bash
# Install httpx for testing
pip install httpx

# Run API tests
pytest tests/test_api.py
```

## Logging

Logs are stored in the `logs/` directory with different levels:
- Debug logs
- Info logs
- Error logs

API server logs include:
- Request/response logging
- Agent execution logs
- Error tracking

## Performance

The API server is optimized for:
- **Async processing** for concurrent requests
- **Agent result caching** for repeated analyses
- **Connection pooling** for database operations
- **Efficient MCP server management**

## Deployment

### Production Setup
1. Set environment variables for production
2. Configure PostgreSQL and ChromaDB
3. Use proper ASGI server (Gunicorn + Uvicorn)
4. Set up reverse proxy (Nginx)
5. Configure SSL/TLS

### Docker Deployment
```bash
# Build and run with Docker
docker build -t vyasaquant-backend .
docker run -p 8000:8000 vyasaquant-backend
```

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update API documentation
4. Ensure all tests pass
5. Test API endpoints with different inputs

## License

See LICENSE file in the root directory. 