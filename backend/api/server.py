"""
VyasaQuant API Server

FastAPI server that provides REST endpoints for the VyasaQuant stock analysis system.
Integrates with the stability checker agent and other analysis components.
"""

import asyncio
import logging
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import the stability checker agent
from agents.stability_checker_agent.core.loop import AgentLoop
# Use original session manager that actually works with real MCP servers
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

class EPSData(BaseModel):
    """Dynamic EPS data by year"""
    data: Dict[str, float] = Field(description="EPS data by year (year as string key, EPS as float value)")
    years_available: List[str] = Field(description="List of years for which EPS data is available")
    total_years: int = Field(description="Total number of years of data available")

class StabilityAnalysis(BaseModel):
    eps_data: EPSData = Field(description="Earnings Per Share data by year")
    eps_growth_rate: float = Field(description="EPS Compound Annual Growth Rate (%)")
    is_eps_increasing: bool = Field(description="Whether EPS is consistently increasing")
    passes_stability_criteria: bool = Field(description="Whether stock passes stability criteria")
    recommendation: str = Field(description="Analysis recommendation (BUY/SELL/HOLD/FURTHER_ANALYSIS)")
    reasoning: str = Field(description="Detailed reasoning for the recommendation")

class StockAnalysisResponse(BaseModel):
    symbol: str = Field(description="Stock ticker symbol")
    company_name: str = Field(description="Company name")
    analysis_date: str = Field(description="Date of analysis")
    stability_analysis: StabilityAnalysis = Field(description="Detailed stability analysis results")
    raw_agent_response: Optional[str] = Field(default=None, description="Full agent response for debugging")

# Global variables for agent management
multi_mcp: Optional[MultiMCP] = None
agent_config = None

@app.on_event("startup")
async def startup_event():
    """Initialize the stability checker agent on startup"""
    global multi_mcp, agent_config
    
    logger.info("🚀 Starting VyasaQuant API Server")
    logger.info("💡 Using direct MCP server connections")
    
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
        
        if not multi_mcp.servers:
            logger.warning("⚠️ No MCP servers connected")
            logger.warning("💡 Please start MCP servers first: python mcp_server_manager.py")
        else:
            logger.info("✅ VyasaQuant API Server started successfully")
            logger.info(f"🔧 Connected to servers: {list(multi_mcp.servers.keys())}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize API server: {e}")
        logger.error("💡 Make sure MCP servers are running: python mcp_server_manager.py")
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
    
    # Parse the analysis result - extract real data from agent response
    company_name = extract_company_name(answer, symbol)
    
    # Extract real data using new helper functions
    eps_data = extract_eps_data(answer)
    eps_growth_rate = extract_eps_growth_rate(answer)
    is_eps_increasing = extract_is_eps_increasing(answer)
    passes_stability_criteria = extract_passes_criteria(answer)
    recommendation = extract_recommendation(answer)
    
    # Import datetime for analysis date
    from datetime import datetime
    
    # Create response with extracted real data
    response = StockAnalysisResponse(
        symbol=symbol.upper(),
        company_name=company_name,
        analysis_date=datetime.now().strftime("%Y-%m-%d"),
        stability_analysis=StabilityAnalysis(
            eps_data=eps_data,
            eps_growth_rate=eps_growth_rate,
            is_eps_increasing=is_eps_increasing,
            passes_stability_criteria=passes_stability_criteria,
            recommendation=recommendation,
            reasoning=answer  # Use the full agent response as reasoning
        ),
        raw_agent_response=answer
    )
    
    return response

def extract_company_name(answer: str, symbol: str) -> str:
    """Extract company name from analysis result"""
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
    
    # Try to extract from common company name patterns
    if "HINDUSTAN AERONAUTICS" in answer.upper():
        return "Hindustan Aeronautics Limited"
    elif "RELIANCE" in answer.upper():
        return "Reliance Industries Limited"
    elif "TCS" in answer.upper():
        return "Tata Consultancy Services"
    elif "INFOSYS" in answer.upper():
        return "Infosys Limited"
    elif "WIPRO" in answer.upper():
        return "Wipro Limited"
    
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
    
    if "recommend further analysis" in answer_lower:
        return "FURTHER_ANALYSIS"
    elif "accept" in answer_lower:
        return "BUY"
    elif "pass" in answer_lower and "round 2" in answer_lower:
        return "BUY"
    elif "buy" in answer_lower:
        return "BUY"
    elif "reject" in answer_lower or "sell" in answer_lower:
        return "SELL"
    else:
        return "HOLD"

# Real data extraction functions

def extract_eps_data(answer: str) -> EPSData:
    """Extract EPS data by year from the agent response"""
    import re
    import json
    
    eps_dict = {}
    
    # Method 1: Look for Python dictionary format like "{'2024': 45.5, '2023': 38.2, '2022': 32.1, '2021': 28.4}"
    # or JSON format like {"2024": 45.5, "2023": 38.2}
    dict_patterns = [
        r'\{[\'\"]\d{4}[\'\"]\s*:\s*\d+\.?\d*[^}]*\}',  # Match dictionary pattern
        r'\{[^}]*\d{4}[^}]*:\s*\d+\.?\d*[^}]*\}'        # More flexible pattern
    ]
    
    for pattern in dict_patterns:
        dict_match = re.search(pattern, answer)
        if dict_match:
            try:
                dict_str = dict_match.group()
                print(f"Found dictionary string: {dict_str}")
                
                # Try to parse as JSON first (handles double quotes)
                try:
                    eps_data_dict = json.loads(dict_str)
                except json.JSONDecodeError:
                    # If JSON fails, try to parse Python dict format (single quotes)
                    dict_str_clean = dict_str.replace("'", '"')
                    eps_data_dict = json.loads(dict_str_clean)
                
                for year_str, value in eps_data_dict.items():
                    try:
                        year = int(year_str)
                        if 2000 <= year <= 2030:
                            eps_dict[year_str] = float(value)
                    except (ValueError, TypeError):
                        continue
                
                if eps_dict:  # If we successfully parsed data, break
                    break
                    
            except Exception as e:
                print(f"Failed to parse dictionary format: {e}")
                continue
    
    # Method 2: Fallback to colon-separated format like "2022: 75.96, 2023: 87.14"
    if not eps_dict:
        eps_pattern = r'(\d{4})\s*:\s*(\d+\.?\d*)'
        matches = re.findall(eps_pattern, answer)
        
        for year_str, value_str in matches:
            try:
                year = int(year_str)
                value = float(value_str)
                if 2000 <= year <= 2030:
                    eps_dict[year_str] = value
            except ValueError:
                continue
    
    # Sort years for consistent ordering
    years_available = sorted(eps_dict.keys())
    
    print(f"Final EPS data: {eps_dict}")
    
    return EPSData(
        data=eps_dict,
        years_available=years_available,
        total_years=len(years_available)
    )

def extract_eps_growth_rate(answer: str) -> float:
    """Extract EPS growth rate from the agent response"""
    import re
    import math
    
    # Look for patterns like "EPS Growth Rate: 18.08%" or "growth rate is 18.08%"
    patterns = [
        r'EPS\s+growth\s+rate[:\s]+is\s+(\d+\.?\d*)%?',
        r'EPS\s+Growth\s+Rate[:\s]*(\d+\.?\d*)%?',
        r'growth\s+rate[:\s]+is\s+(\d+\.?\d*)%?',
        r'growth\s+rate[:\s]*(\d+\.?\d*)%?',
        r'CAGR[:\s]*(\d+\.?\d*)%?',
        r'compound.*growth.*rate[:\s]*(\d+\.?\d*)%?',
        # Add more comprehensive patterns to catch various formats
        r'(\d+\.?\d*)%?\s*CAGR',
        r'CAGR\s+is\s+(\d+\.?\d*)%?',
        r'growth\s+rate\s*\(CAGR\)[:\s]*(\d+\.?\d*)%?',
        r'EPS.*growth.*rate.*\(CAGR\)[:\s]*(\d+\.?\d*)%?',
        r'(\d+\.?\d*)%?\s*compound.*annual.*growth',
        r'compound.*annual.*growth.*rate[:\s]*(\d+\.?\d*)%?',
        # Look for any percentage followed by CAGR or vice versa
        r'(\d+\.?\d*)%?\s*.*CAGR',
        r'CAGR.*(\d+\.?\d*)%?',
        # More flexible patterns
        r'(\d+\.?\d*)%?\s*.*growth.*rate',
        r'growth.*?rate.*?(\d+\.?\d*)%'
    ]
    
    print(f"Searching for growth rate in: {answer}")
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, answer, re.IGNORECASE)
        if match:
            growth_rate = float(match.group(1))
            print(f"Pattern {i+1} matched: {match.group()} -> {growth_rate}%")
            return growth_rate
    
    # If no pattern matched, try to extract from the detailed analysis section
    # Look for the specific format mentioned in the image: "18.08% CAGR"
    cagr_match = re.search(r'(\d+\.?\d*)%?\s*CAGR', answer, re.IGNORECASE)
    if cagr_match:
        growth_rate = float(cagr_match.group(1))
        print(f"CAGR pattern matched: {cagr_match.group()} -> {growth_rate}%")
        return growth_rate
    
    # # Fallback: Calculate CAGR from EPS data if available
    # eps_data = extract_eps_data(answer)
    # if eps_data.total_years >= 2:
    #     years = sorted(eps_data.years_available)
    #     if len(years) >= 2:
    #         first_year = int(years[0])
    #         last_year = int(years[-1])
    #         first_eps = eps_data.data[years[0]]
    #         last_eps = eps_data.data[years[-1]]
            
    #         if first_eps > 0 and last_eps > 0:
    #             # Calculate CAGR: (Final Value / Initial Value)^(1/n) - 1
    #             n = last_year - first_year
    #             if n > 0:
    #                 cagr = (math.pow(last_eps / first_eps, 1/n) - 1) * 100
    #                 print(f"Calculated CAGR from EPS data: {cagr:.2f}%")
    #                 return cagr
    
    print("No growth rate pattern matched and could not calculate from EPS data")
    return 0.0

def extract_is_eps_increasing(answer: str) -> bool:
    """Extract whether EPS is consistently increasing"""
    answer_lower = answer.lower()
    
    # Look for indicators that EPS is increasing
    increasing_indicators = [
        "eps is consistently increasing",
        "eps consistently increasing",
        "earnings increasing",
        "growing earnings",
        "upward trend",
        "positive growth"
    ]
    
    for indicator in increasing_indicators:
        if indicator in answer_lower:
            return True
    
    # Also check if we can find decreasing indicators
    decreasing_indicators = [
        "eps is decreasing",
        "eps decreasing",
        "declining earnings",
        "negative growth"
    ]
    
    for indicator in decreasing_indicators:
        if indicator in answer_lower:
            return False
    
    return False  # Default to False if unclear

def extract_passes_criteria(answer: str) -> bool:
    """Extract whether stock passes stability criteria"""
    answer_lower = answer.lower()
    
    # Look for positive indicators
    positive_indicators = [
        "accept",
        "pass",
        "recommend further analysis",
        "meets criteria", 
        "passes",
        "suitable",
        "qualifies"
    ]
    
    # Look for negative indicators
    negative_indicators = [
        "reject",
        "does not pass",
        "fails",
        "not suitable",
        "does not meet"
    ]
    
    for indicator in positive_indicators:
        if indicator in answer_lower:
            return True
    
    for indicator in negative_indicators:
        if indicator in answer_lower:
            return False
    
    return False  # Default to False if unclear

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        # reload=True, # the reload=True options causes the default ProactorEventLoop to be changed to SelectorEventLoop on windows. Refer: https://stackoverflow.com/questions/70568070/running-an-asyncio-subprocess-in-fastapi-results-in-notimplementederror
        log_level="info"
    ) 