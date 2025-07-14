# modules/decision.py - Decision Making for Stock Stability Analysis

from typing import List, Dict, Any, Optional
from .memory import MemoryItem

async def generate_plan(
    user_input: str,
    perception: Any,
    memory_items: List[MemoryItem],
    tool_descriptions: str,  # String, not Dict - follows S9 pattern
    prompt_path: str,
    step_num: int,
    max_steps: int,
    context: Any = None,
    model_manager: Any = None  # Accept ModelManager instance
) -> str:
    """Generate execution plan for stock stability analysis"""
    
    # Use the passed ModelManager instance or create a new one
    if model_manager is None:
        from agents.stability_checker_agent.core.model_manager import ModelManager
        model_manager = ModelManager()
    
    # Format memory context for the prompt
    memory_text = format_memory_context(memory_items)
    
    # Create stock analysis specific prompt with correct MCP tool usage
    stock_analysis_prompt = f"""
You are a stock stability analysis expert. Create a Python function called `solve()` that performs stock stability analysis.

User Request: {user_input}

Available Tools:
{tool_descriptions}

Analysis Stage: {perception.analysis_stage}
Selected Servers: {perception.selected_servers}

Memory Context: {format_memory_context(memory_items)}

IMPORTANT: Tools must be called through the MCP dispatcher using this syntax:
```python
result = await dispatcher.call_tool("data_acquisition_server", "tool_name", {{"arg1": "value1"}})
```

CRITICAL: Your solve() function must NOT take any parameters. The dispatcher is available as a global variable.

Function signature should be:
```python
async def solve():  # NO PARAMETERS!
    # Your code here
    # Use: await dispatcher.call_tool("data_acquisition_server", "tool_name", {{"args": "values"}})
```

RESPONSE PARSING: MCP tools return responses in this format:
```python
{{
  "content": [
    {{
      "type": "text", 
      "text": "{{\"result\": {{\"success\": true, \"ticker_symbol\": \"HAL.NS\", ...}}}}"
    }}
  ]
}}
```

Parse responses using this pattern:
```python
if isinstance(result, dict) and "content" in result:
    content = result.get("content", [])
    if content and isinstance(content, list) and len(content) > 0:
        text_content = content[0].get("text", "")
        try:
            import json
            parsed_result = json.loads(text_content)
            actual_result = parsed_result.get("result", {{}})
            if actual_result.get("success"):
                # For get_ticker_symbol: use ticker_symbol field
                ticker_symbol = actual_result.get("ticker_symbol")
                # For get_eps_data: use eps_data field  
                eps_data = actual_result.get("eps_data", {{}})
            else:
                error = actual_result.get("error", "Unknown error")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {{e}}")
```

Your task is to create a solve() function that:
1. Uses the MCP dispatcher to call tools correctly
2. Follows the 6-step stock stability workflow:
   - Get ticker symbol (if company name provided)
   - Fetch last 4 years of EPS data
   - Check if EPS is consistently increasing by first sorting the EPS data in ascending order of year and then checking if the EPS is increasing year by year
   - Calculate EPS Growth Rate (CAGR)
   - Pass to Round 2 if EPS increasing AND EPS-GR > 10%
   - Otherwise reject the stock

3. Returns either:
   - FINAL_ANSWER: [recommendation with detailed reasoning]
   - FURTHER_PROCESSING_REQUIRED: [intermediate result that needs more processing]

IMPORTANT PARAMETER NAMES:
- get_ticker_symbol: use "company_name" parameter
- get_eps_data: use "ticker_symbol" parameter  
- get_income_statement: use "ticker" parameter

Generate a solve() function that handles the specific user request and returns a clear recommendation with detailed reasoning for both accepted and rejected stocks. In the reasoning, include the yearly EPS data and the EPS growth rate.
"""

    # Get response from the model - use correct method name
    response = await model_manager.generate_text(stock_analysis_prompt)
    
    return response

def format_memory_context(memory_items: List[MemoryItem]) -> str:
    """Format memory items for inclusion in prompts"""
    if not memory_items:
        return "No previous context available."
    
    formatted = []
    for item in memory_items[-5:]:  # Last 5 items
        formatted.append(f"- {item.timestamp}: {item.text[:200]}...")
    
    return "\n".join(formatted)