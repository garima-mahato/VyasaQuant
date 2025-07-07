# modules/tools.py - Tool Management for Stock Stability Analysis

from typing import Dict, List, Any

def summarize_tools(tools: Dict[str, Any]) -> str:
    """Summarize available tools for stock stability analysis"""
    
    if not tools:
        return "No tools available"
    
    # Group tools by category
    categorized_tools = {
        "Stock Analysis": [],
        "Data Collection": [],
        "Mathematical": [],
        "Web Search": [],
        "AI Analysis": [],
        "General": []
    }
    
    for tool_name, tool_info in tools.items():
        description = tool_info.get("description", "")
        
        # Categorize tools based on their purpose
        if any(keyword in tool_name.lower() for keyword in ["stock", "ticker", "eps", "stability"]):
            categorized_tools["Stock Analysis"].append((tool_name, description))
        elif any(keyword in tool_name.lower() for keyword in ["fetch", "data", "collect"]):
            categorized_tools["Data Collection"].append((tool_name, description))
        elif any(keyword in tool_name.lower() for keyword in ["calculate", "math", "growth", "compound"]):
            categorized_tools["Mathematical"].append((tool_name, description))
        elif any(keyword in tool_name.lower() for keyword in ["search", "web", "query"]):
            categorized_tools["Web Search"].append((tool_name, description))
        elif any(keyword in tool_name.lower() for keyword in ["ai", "analysis", "generate"]):
            categorized_tools["AI Analysis"].append((tool_name, description))
        else:
            categorized_tools["General"].append((tool_name, description))
    
    # Create summary
    summary_parts = []
    
    for category, tool_list in categorized_tools.items():
        if tool_list:
            summary_parts.append(f"\n{category} Tools:")
            for tool_name, description in tool_list:
                summary_parts.append(f"  - {tool_name}: {description[:100]}{'...' if len(description) > 100 else ''}")
    
    if summary_parts:
        return "\n".join(summary_parts)
    else:
        return "No categorized tools available"

def get_stock_analysis_tools(tools: Dict[str, Any]) -> List[str]:
    """Get list of stock analysis specific tools"""
    stock_tools = []
    
    for tool_name in tools.keys():
        if any(keyword in tool_name.lower() for keyword in [
            "stock", "ticker", "eps", "stability", "analyze", "financial"
        ]):
            stock_tools.append(tool_name)
    
    return stock_tools

def get_recommended_tools_for_stage(stage: str, available_tools: Dict[str, Any]) -> List[str]:
    """Get recommended tools for a specific analysis stage"""
    
    stage_tools = {
        "ticker_lookup": ["lookup_ticker_symbol", "analyze_stock_stability", "web_search"],
        "eps_data_collection": ["fetch_eps_data", "analyze_stock_stability", "web_search"],
        "growth_rate_calculation": ["calculate_eps_growth_rate", "calculate_compound_growth"],
        "stability_assessment": ["analyze_stock_stability", "calculate_eps_growth_rate"],
        "analysis_complete": ["analyze_stock_stability", "generate_ai_analysis"]
    }
    
    recommended = stage_tools.get(stage, [])
    
    # Filter by actually available tools
    available_tool_names = list(available_tools.keys())
    return [tool for tool in recommended if tool in available_tool_names] 