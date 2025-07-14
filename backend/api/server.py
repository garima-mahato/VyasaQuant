"""
VyasaQuant API Server

FastAPI server that provides REST endpoints for the VyasaQuant stock analysis system.
Integrates with the stability checker agent and other analysis components.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import the stability checker agent
from agents.stability_checker_agent.core.loop import AgentLoop
from agents.stability_checker_agent.core.session import MultiMCP
from agents.stability_checker_agent.core.context import AgentContext
from config.config_loader import get_stability_checker_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="VyasaQuant API",
    description="Stock Analysis API for VyasaQuant system",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class StockAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol or company name to analyze")

class ValueAnalysis(BaseModel):
    intrinsic_value: float = Field(default=0.0, description="Calculated intrinsic value")
    current_price: float = Field(default=0.0, description="Current market price")
    recommendation: str = Field(default="HOLD", description="Buy/Sell/Hold recommendation")

class KeyMetrics(BaseModel):
    pe_ratio: float = Field(default=0.0, description="Price to Earnings ratio")
    pb_ratio: float = Field(default=0.0, description="Price to Book ratio")
    debt_equity: float = Field(default=0.0, description="Debt to Equity ratio")
    roe: float = Field(default=0.0, description="Return on Equity percentage")

class StockAnalysisResponse(BaseModel):
    symbol: str
    company_name: str
    stability_score: float = Field(description="Stability score out of 100")
    value_analysis: ValueAnalysis
    key_metrics: KeyMetrics

# Global variables for agent management
multi_mcp: Optional[MultiMCP] = None
agent_config = None

@app.on_event("startup")
async def startup_event():
    """Initialize the stability checker agent on startup"""
    global multi_mcp, agent_config
    
    logger.info("🚀 Starting VyasaQuant API Server")
    
    try:
        # Load agent configuration
        agent_config = get_stability_checker_config()
        
        # Extract MCP server configurations
        mcp_servers_config = agent_config.get("servers", {})
        mcp_servers_list = []
        
        for server_id, server_config in mcp_servers_config.items():
            mcp_servers_list.append({
                "id": server_id,
                **server_config
            })
        
        # Initialize MCP servers
        multi_mcp = MultiMCP(server_configs=mcp_servers_list)
        await multi_mcp.initialize()
        
        logger.info("✅ VyasaQuant API Server started successfully")
        logger.info(f"🔧 Available servers: {list(mcp_servers_config.keys())}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize API server: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down VyasaQuant API Server")
    # Add cleanup code here if needed

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "VyasaQuant Stock Analysis API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "/api/analyze",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time(),
        "agent_initialized": multi_mcp is not None
    }

@app.post("/api/analyze", response_model=StockAnalysisResponse)
async def analyze_stock(request: StockAnalysisRequest):
    """
    Analyze stock stability and provide comprehensive analysis.
    
    This endpoint integrates with the stability checker agent to:
    1. Resolve ticker symbol if needed
    2. Fetch EPS data for the last 4 years
    3. Calculate growth rate and stability score
    4. Provide buy/sell recommendation
    """
    
    if not multi_mcp:
        raise HTTPException(
            status_code=503,
            detail="Analysis service not available. Please try again later."
        )
    
    try:
        logger.info(f"📊 Starting analysis for: {request.symbol}")
        
        # Format analysis request
        eps_years = agent_config['stability_analysis']['criteria']['eps_years']
        growth_threshold = agent_config['stability_analysis']['criteria']['eps_growth_threshold']
        
        formatted_input = f"""
        Analyze the stock stability for: {request.symbol}
        
        Please follow this exact workflow:
        1. Get the ticker symbol if not provided
        2. Fetch last {eps_years} years of EPS data
        3. Check if EPS is consistently increasing across all years
        4. Calculate EPS Growth Rate (compound annual growth rate)
        5. Pass to Round 2 if EPS increasing AND EPS-GR > {growth_threshold}%
        6. Otherwise reject the stock
        
        Return FINAL_ANSWER with clear recommendation and reasoning.
        """
        
        # Create agent context
        context = AgentContext(
            user_input=formatted_input,
            session_id=None,
            dispatcher=multi_mcp,
            mcp_server_descriptions={server["id"]: server for server in agent_config.get("servers", {}).values()}
        )
        
        # Run analysis
        agent = AgentLoop(context)
        result = await agent.run()
        
        # Parse result
        analysis_result = await parse_analysis_result(result, request.symbol)
        
        logger.info(f"✅ Analysis completed for: {request.symbol}")
        return analysis_result
        
    except Exception as e:
        logger.error(f"❌ Analysis failed for {request.symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

async def parse_analysis_result(result: Any, symbol: str) -> StockAnalysisResponse:
    """
    Parse the agent result and convert to the expected API response format.
    
    Args:
        result: Agent analysis result
        symbol: Stock symbol analyzed
    
    Returns:
        StockAnalysisResponse with structured data
    """
    
    # Handle different result formats
    if isinstance(result, dict):
        answer = result.get("result", str(result))
    elif isinstance(result, str):
        answer = result
    else:
        answer = str(result)
    
    # Extract final answer if present
    if "FINAL_ANSWER:" in answer:
        answer = answer.split('FINAL_ANSWER:')[1].strip()
    
    # Parse the analysis result
    # This is a simplified parser - in production, you'd want more robust parsing
    company_name = extract_company_name(answer, symbol)
    stability_score = extract_stability_score(answer)
    recommendation = extract_recommendation(answer)
    
    # Create response with default values
    # In a real implementation, you'd extract these from the agent's detailed analysis
    response = StockAnalysisResponse(
        symbol=symbol.upper(),
        company_name=company_name,
        stability_score=stability_score,
        value_analysis=ValueAnalysis(
            intrinsic_value=calculate_mock_intrinsic_value(stability_score),
            current_price=calculate_mock_current_price(stability_score),
            recommendation=recommendation
        ),
        key_metrics=KeyMetrics(
            pe_ratio=calculate_mock_pe_ratio(stability_score),
            pb_ratio=calculate_mock_pb_ratio(stability_score),
            debt_equity=calculate_mock_debt_equity(stability_score),
            roe=calculate_mock_roe(stability_score)
        )
    )
    
    return response

def extract_company_name(answer: str, symbol: str) -> str:
    """Extract company name from analysis result"""
    # Simple extraction - look for company name patterns
    import re
    
    # Look for patterns like "Company Name (SYMBOL)" or "SYMBOL - Company Name"
    patterns = [
        r'([A-Za-z\s&]+)\s*\([A-Z]+\)',
        r'[A-Z]+\s*-\s*([A-Za-z\s&]+)',
        r'Company:\s*([A-Za-z\s&]+)',
        r'analyzing\s*([A-Za-z\s&]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, answer, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Fallback to symbol
    return symbol.upper()

def extract_stability_score(answer: str) -> float:
    """Extract stability score from analysis result"""
    import re
    
    # Look for stability score patterns
    patterns = [
        r'stability\s*score[:\s]*(\d+\.?\d*)',
        r'score[:\s]*(\d+\.?\d*)',
        r'(\d+\.?\d*)%?\s*stable',
        r'growth\s*rate[:\s]*(\d+\.?\d*)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, answer, re.IGNORECASE)
        if match:
            score = float(match.group(1))
            return min(score, 100.0)  # Cap at 100
    
    # Default score based on recommendation
    if "buy" in answer.lower() or "pass" in answer.lower():
        return 75.0
    elif "reject" in answer.lower() or "sell" in answer.lower():
        return 25.0
    else:
        return 50.0

def extract_recommendation(answer: str) -> str:
    """Extract recommendation from analysis result"""
    answer_lower = answer.lower()
    
    if "pass" in answer_lower or "buy" in answer_lower:
        return "BUY"
    elif "reject" in answer_lower or "sell" in answer_lower:
        return "SELL"
    else:
        return "HOLD"

# Mock calculation functions (replace with real calculations in production)
def calculate_mock_intrinsic_value(stability_score: float) -> float:
    """Calculate mock intrinsic value based on stability score"""
    base_value = 100.0
    return base_value * (1 + stability_score / 100.0)

def calculate_mock_current_price(stability_score: float) -> float:
    """Calculate mock current price"""
    intrinsic = calculate_mock_intrinsic_value(stability_score)
    # Current price is typically different from intrinsic value
    return intrinsic * (0.8 + (stability_score / 500.0))

def calculate_mock_pe_ratio(stability_score: float) -> float:
    """Calculate mock P/E ratio"""
    return 15.0 + (stability_score / 10.0)

def calculate_mock_pb_ratio(stability_score: float) -> float:
    """Calculate mock P/B ratio"""
    return 1.5 + (stability_score / 100.0)

def calculate_mock_debt_equity(stability_score: float) -> float:
    """Calculate mock debt-to-equity ratio"""
    return max(0.1, 1.0 - (stability_score / 200.0))

def calculate_mock_roe(stability_score: float) -> float:
    """Calculate mock ROE"""
    return 10.0 + (stability_score / 5.0)

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 