# modules/decision.py - Decision Making for Stock Stability Analysis

from typing import List, Dict, Any, Optional
from modules.memory import MemoryItem
from modules.model_manager import ModelManager

async def generate_plan(
    user_input: str,
    perception: Any,
    memory_items: List[MemoryItem],
    tool_descriptions: Dict[str, Any],
    prompt_path: str,
    step_num: int,
    max_steps: int,
    context: Any = None
) -> str:
    """Generate execution plan for stock stability analysis"""
    
    # Get AI model configuration from context (passed as parameter or from perception)
    if context and hasattr(context, 'agent_profile'):
        ai_config = context.agent_profile.llm_config
    else:
        # Fallback configuration
        ai_config = {
            "provider": "google",
            "google": {"model": "gemini-2.0-flash-001", "temperature": 0.1, "max_tokens": 4000}
        }
    
    model = ModelManager(ai_config)
    
    # Create stock analysis specific prompt
    stock_analysis_prompt = f"""
You are a stock stability analysis expert. Create a Python function called `solve()` that performs stock stability analysis.

User Request: {user_input}

Available Tools: {list(tool_descriptions.keys())}

Analysis Stage: {perception.analysis_stage}
Selected Servers: {perception.selected_servers}

Memory Context: {format_memory_context(memory_items)}

Your task is to create a solve() function that:
1. Uses the available MCP tools to analyze stock stability
2. Follows the 6-step stock stability workflow:
   - Get ticker symbol (if company name provided)
   - Fetch last 4 years of EPS data
   - Check if EPS is consistently increasing
   - Calculate EPS Growth Rate (CAGR)
   - Pass to Round 2 if EPS increasing AND EPS-GR > 10%
   - Otherwise reject the stock

3. Returns either:
   - FINAL_ANSWER: [recommendation with detailed reasoning]
   - FURTHER_PROCESSING_REQUIRED: [intermediate result that needs more processing]

Available MCP Tools:
{format_tool_descriptions(tool_descriptions)}

Generate a complete solve() function that uses these tools appropriately.

Example function structure:
```python
async def solve():
    # Step 1: Get ticker if needed
    # Step 2: Fetch EPS data
    # Step 3: Calculate growth rate
    # Step 4: Assess stability
    # Step 5: Generate recommendation
    return "FINAL_ANSWER: [your analysis]"
```
"""
    
    try:
        # Generate plan using the model
        plan = await model.generate_text(stock_analysis_prompt)
        return plan
    except Exception as e:
        return f"""
async def solve():
    return "FINAL_ANSWER: Error generating analysis plan: {str(e)}"
"""

def format_memory_context(memory_items: List[MemoryItem]) -> str:
    """Format memory items for context"""
    if not memory_items:
        return "No previous analysis steps"
    
    recent_items = memory_items[-3:]  # Last 3 items
    context = []
    
    for item in recent_items:
        if item.type == "tool_output":
            tool_name = item.metadata.get("tool_name", "unknown")
            success = item.metadata.get("success", False)
            context.append(f"- Used {tool_name}: {'Success' if success else 'Failed'}")
        elif item.type == "analysis_update":
            stage = item.metadata.get("analysis_stage", "unknown")
            context.append(f"- Completed analysis stage: {stage}")
    
    return "\n".join(context) if context else "No relevant context"

def format_tool_descriptions(tool_descriptions: Dict[str, Any]) -> str:
    """Format tool descriptions for the prompt"""
    if not tool_descriptions:
        return "No tools available"
    
    formatted = []
    for tool_name, tool_info in tool_descriptions.items():
        description = tool_info.get("description", "No description")
        formatted.append(f"- {tool_name}: {description}")
    
    return "\n".join(formatted) 