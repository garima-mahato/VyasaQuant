# core/strategy.py - Planning Strategies for Stock Stability Analysis

from typing import Dict, List, Any, Optional
from pathlib import Path
import random

def select_decision_prompt_path(
    planning_mode: str = "conservative",
    exploration_mode: Optional[str] = None,
    analysis_stage: Optional[str] = None
) -> str:
    """
    Select the appropriate decision prompt path based on planning mode and analysis stage.
    
    Args:
        planning_mode: "conservative" or "exploratory"
        exploration_mode: "parallel" or "sequential" (if exploratory)
        analysis_stage: Current stage of stock analysis
    
    Returns:
        Path to the appropriate prompt file
    """
    
    base_path = Path("agents/stability_checker_agent/prompts")
    
    # Stock stability analysis specific prompts
    if analysis_stage:
        stage_prompts = {
            "ticker_lookup": "stock_ticker_lookup.txt",
            "eps_data_collection": "eps_data_collection.txt", 
            "growth_rate_calculation": "growth_rate_calculation.txt",
            "stability_assessment": "stability_assessment.txt",
            "analysis_complete": "final_analysis.txt"
        }
        
        if analysis_stage in stage_prompts:
            stage_path = base_path / "stages" / stage_prompts[analysis_stage]
            if stage_path.exists():
                return str(stage_path)
    
    # Default planning mode prompts
    if planning_mode == "conservative":
        return str(base_path / "conservative_stock_analysis.txt")
    elif planning_mode == "exploratory":
        if exploration_mode == "parallel":
            return str(base_path / "exploratory_parallel_stock_analysis.txt")
        elif exploration_mode == "sequential":
            return str(base_path / "exploratory_sequential_stock_analysis.txt")
        else:
            return str(base_path / "exploratory_stock_analysis.txt")
    else:
        # Fallback to default conservative approach
        return str(base_path / "conservative_stock_analysis.txt")


def get_stock_analysis_strategy(
    company_name: Optional[str] = None,
    ticker_symbol: Optional[str] = None,
    analysis_depth: str = "standard"
) -> Dict[str, Any]:
    """
    Get stock analysis strategy configuration.
    
    Args:
        company_name: Company name to analyze
        ticker_symbol: Stock ticker symbol
        analysis_depth: "quick", "standard", or "deep"
    
    Returns:
        Strategy configuration dictionary
    """
    
    strategies = {
        "quick": {
            "max_steps": 2,
            "max_lifelines_per_step": 2,
            "eps_years": 3,
            "web_search_enabled": True,
            "ai_analysis_enabled": False,
            "tools_priority": ["ticker_lookup", "eps_data", "growth_calculation"]
        },
        "standard": {
            "max_steps": 3,
            "max_lifelines_per_step": 3,
            "eps_years": 4,
            "web_search_enabled": True,
            "ai_analysis_enabled": True,
            "tools_priority": ["ticker_lookup", "eps_data", "growth_calculation", "stability_assessment"]
        },
        "deep": {
            "max_steps": 5,
            "max_lifelines_per_step": 4,
            "eps_years": 5,
            "web_search_enabled": True,
            "ai_analysis_enabled": True,
            "tools_priority": ["ticker_lookup", "eps_data", "growth_calculation", "stability_assessment", "risk_analysis"]
        }
    }
    
    return strategies.get(analysis_depth, strategies["standard"])


def get_tool_selection_strategy(
    available_tools: List[str],
    analysis_stage: str,
    context: Optional[Dict[str, Any]] = None
) -> List[str]:
    """
    Select the most appropriate tools for the current analysis stage.
    
    Args:
        available_tools: List of available tool names
        analysis_stage: Current stage of analysis
        context: Additional context information
    
    Returns:
        Prioritized list of tool names
    """
    
    # Tool priorities by analysis stage
    stage_tools = {
        "ticker_lookup": [
            "search_company_ticker",
            "lookup_ticker_symbol", 
            "web_search_ticker",
            "company_database_search"
        ],
        "eps_data_collection": [
            "fetch_eps_data",
            "get_financial_data",
            "web_search_eps",
            "extract_financial_statements",
            "ai_eps_extraction"
        ],
        "growth_rate_calculation": [
            "calculate_compound_growth",
            "calculate_growth_rate",
            "math_calculations",
            "python_calculator"
        ],
        "stability_assessment": [
            "assess_eps_stability",
            "analyze_trend_consistency",
            "ai_stability_analysis",
            "generate_recommendation"
        ],
        "analysis_complete": [
            "generate_final_report",
            "ai_analysis_summary",
            "format_results"
        ]
    }
    
    # Get preferred tools for current stage
    preferred_tools = stage_tools.get(analysis_stage, [])
    
    # Filter available tools based on preferences
    selected_tools = []
    for tool in preferred_tools:
        if tool in available_tools:
            selected_tools.append(tool)
    
    # Add any remaining tools that might be useful
    for tool in available_tools:
        if tool not in selected_tools and is_tool_relevant(tool, analysis_stage):
            selected_tools.append(tool)
    
    return selected_tools


def is_tool_relevant(tool_name: str, analysis_stage: str) -> bool:
    """
    Check if a tool is relevant for the current analysis stage.
    
    Args:
        tool_name: Name of the tool
        analysis_stage: Current analysis stage
    
    Returns:
        True if tool is relevant, False otherwise
    """
    
    # General stock analysis tools
    stock_tools = [
        "web_search", "ai_analysis", "data_extraction", 
        "math_calculation", "python_sandbox"
    ]
    
    # Stage-specific tool patterns
    stage_patterns = {
        "ticker_lookup": ["ticker", "symbol", "company", "search"],
        "eps_data_collection": ["eps", "earnings", "financial", "data"],
        "growth_rate_calculation": ["growth", "rate", "calculate", "math"],
        "stability_assessment": ["stability", "analyze", "assess", "trend"],
        "analysis_complete": ["report", "summary", "format", "final"]
    }
    
    # Check if tool name contains stage-specific patterns
    patterns = stage_patterns.get(analysis_stage, [])
    for pattern in patterns:
        if pattern.lower() in tool_name.lower():
            return True
    
    # Check if it's a general stock analysis tool
    for stock_tool in stock_tools:
        if stock_tool.lower() in tool_name.lower():
            return True
    
    return False


def get_analysis_workflow(analysis_type: str = "eps_stability") -> List[Dict[str, Any]]:
    """
    Get the standard workflow for stock analysis.
    
    Args:
        analysis_type: Type of analysis to perform
    
    Returns:
        List of workflow steps
    """
    
    workflows = {
        "eps_stability": [
            {
                "stage": "ticker_lookup",
                "description": "Get ticker symbol from company name",
                "required_tools": ["ticker_lookup"],
                "success_criteria": "ticker_symbol identified"
            },
            {
                "stage": "eps_data_collection", 
                "description": "Fetch last 4 years of EPS data",
                "required_tools": ["eps_data", "web_search"],
                "success_criteria": "eps_data collected for required years"
            },
            {
                "stage": "growth_rate_calculation",
                "description": "Calculate compound annual growth rate",
                "required_tools": ["math_calculation"],
                "success_criteria": "growth_rate calculated"
            },
            {
                "stage": "stability_assessment",
                "description": "Assess if EPS is consistently increasing and growth > 10%",
                "required_tools": ["stability_analysis"],
                "success_criteria": "stability_decision made"
            },
            {
                "stage": "analysis_complete",
                "description": "Generate final recommendation with reasoning",
                "required_tools": ["ai_analysis"],
                "success_criteria": "final_recommendation generated"
            }
        ]
    }
    
    return workflows.get(analysis_type, workflows["eps_stability"])


def adapt_strategy_to_context(
    base_strategy: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Adapt strategy based on current context and available resources.
    
    Args:
        base_strategy: Base strategy configuration
        context: Current context information
    
    Returns:
        Adapted strategy configuration
    """
    
    adapted_strategy = base_strategy.copy()
    
    # Adapt based on available data
    if context.get("ticker_symbol"):
        # Skip ticker lookup if already available
        adapted_strategy["skip_stages"] = ["ticker_lookup"]
    
    # Adapt based on available tools
    available_tools = context.get("available_tools", [])
    if "ai_analysis" not in available_tools:
        adapted_strategy["ai_analysis_enabled"] = False
    
    # Adapt based on time constraints
    if context.get("quick_analysis"):
        adapted_strategy["max_steps"] = min(adapted_strategy.get("max_steps", 3), 2)
        adapted_strategy["eps_years"] = min(adapted_strategy.get("eps_years", 4), 3)
    
    return adapted_strategy 