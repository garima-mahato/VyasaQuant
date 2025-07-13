# modules/perception.py - Perception Module for Stock Stability Analysis

import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from core.context import AgentContext

class Perception(BaseModel):
    """Perception result for stock analysis"""
    selected_servers: List[str]
    reasoning: str
    confidence: float
    analysis_stage: str

async def run_perception(context: AgentContext, user_input: str) -> Perception:
    """
    Analyze user input and select appropriate MCP servers for stock stability analysis.
    
    Args:
        context: Agent context with memory and configuration
        user_input: User input to analyze
    
    Returns:
        Perception with selected servers and reasoning
    """
    
    # Analyze the user input to understand what stage of stock analysis is needed
    analysis_stage = determine_analysis_stage(user_input, context)
    
    # Select appropriate servers based on analysis stage
    selected_servers = select_servers_for_stage(analysis_stage, context)
    
    # Generate reasoning for server selection
    reasoning = generate_perception_reasoning(user_input, analysis_stage, selected_servers)
    
    return Perception(
        selected_servers=selected_servers,
        reasoning=reasoning,
        confidence=0.8,
        analysis_stage=analysis_stage
    )

def determine_analysis_stage(user_input: str, context: AgentContext) -> str:
    """Determine current analysis stage based on user input and context"""
    
    user_input_lower = user_input.lower()
    
    # Check context for current analysis stage
    current_stage = context.get_analysis_stage()
    if current_stage != "ticker_lookup":
        return current_stage
    
    # Analyze user input patterns
    if any(keyword in user_input_lower for keyword in ["analyze", "check", "stability", "stock"]):
        if any(keyword in user_input_lower for keyword in ["ticker", "symbol"]):
            return "ticker_lookup"
        elif any(keyword in user_input_lower for keyword in ["eps", "earnings"]):
            return "eps_data_collection"
        elif any(keyword in user_input_lower for keyword in ["growth", "rate"]):
            return "growth_rate_calculation"
        elif any(keyword in user_input_lower for keyword in ["assess", "evaluate"]):
            return "stability_assessment"
        else:
            return "ticker_lookup"  # Default starting point
    
    return "ticker_lookup"

def select_servers_for_stage(analysis_stage: str, context: AgentContext) -> List[str]:
    """Select appropriate MCP servers for the analysis stage"""
    
    # Use the actual server names from the configuration
    server_selection = {
        "ticker_lookup": ["data_acquisition_server"],
        "eps_data_collection": ["data_acquisition_server"],
        "growth_rate_calculation": ["data_acquisition_server"],
        "stability_assessment": ["data_acquisition_server"],
        "analysis_complete": ["data_acquisition_server"]
    }
    
    # Get servers for current stage
    selected = server_selection.get(analysis_stage, ["data_acquisition_server"])
    
    # Filter based on available servers in context
    available_servers = list(context.mcp_server_descriptions.keys()) if context.mcp_server_descriptions else []
    
    # Debug: Print available servers for troubleshooting
    print(f"🔍 Debug: Available servers: {available_servers}")
    print(f"🔍 Debug: Trying to select: {selected}")
    
    final_selection = [server for server in selected if server in available_servers]
    print(f"🔍 Debug: Final selection: {final_selection}")
    
    return final_selection

def generate_perception_reasoning(user_input: str, analysis_stage: str, selected_servers: List[str]) -> str:
    """Generate reasoning for perception decisions"""
    
    stage_descriptions = {
        "ticker_lookup": "Identifying ticker symbol for the company",
        "eps_data_collection": "Collecting EPS data for analysis",
        "growth_rate_calculation": "Calculating EPS growth rate",
        "stability_assessment": "Assessing stock stability criteria",
        "analysis_complete": "Finalizing analysis and recommendations"
    }
    
    stage_desc = stage_descriptions.get(analysis_stage, "Performing stock analysis")
    
    reasoning = f"""
    Analysis Stage: {analysis_stage}
    Task: {stage_desc}
    
    Selected MCP Servers: {', '.join(selected_servers)}
    
    Reasoning:
    - Current analysis stage requires {stage_desc.lower()}
    - Selected servers provide necessary tools for this stage
    - User input: "{user_input}"
    """
    
    return reasoning.strip()

def analyze_stock_keywords(user_input: str) -> Dict[str, bool]:
    """Analyze stock-related keywords in user input"""
    
    keywords = {
        "company_name": bool(re.search(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', user_input)),
        "ticker_symbol": bool(re.search(r'\b[A-Z]{2,6}\.?(NS|BO)?\b', user_input)),
        "eps_analysis": any(word in user_input.lower() for word in ["eps", "earnings", "per share"]),
        "growth_analysis": any(word in user_input.lower() for word in ["growth", "rate", "cagr"]),
        "stability_check": any(word in user_input.lower() for word in ["stability", "stable", "consistent"]),
        "investment_decision": any(word in user_input.lower() for word in ["invest", "buy", "recommend", "round 2"])
    }
    
    return keywords

def get_perception_confidence(analysis_stage: str, keyword_matches: Dict[str, bool]) -> float:
    """Calculate confidence score for perception"""
    
    base_confidence = 0.7
    
    # Boost confidence based on keyword matches
    matches = sum(keyword_matches.values())
    confidence_boost = min(matches * 0.1, 0.3)
    
    # Adjust based on analysis stage clarity
    if analysis_stage in ["ticker_lookup", "eps_data_collection"]:
        confidence_boost += 0.1
    
    return min(base_confidence + confidence_boost, 1.0) 