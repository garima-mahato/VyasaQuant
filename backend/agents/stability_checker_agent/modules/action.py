# modules/action.py - Action Execution for Stock Stability Analysis

import asyncio
import sys
from io import StringIO
from typing import Any, Dict
from ..core.session import MultiMCP
import re

async def run_python_sandbox(plan: str, dispatcher: MultiMCP) -> str:
    """Execute Python plan in sandbox environment"""
    
    try:
        # Strip markdown code block markers if present
        cleaned_plan = plan.strip()
        
        # Remove ```python at the beginning and ``` at the end
        if cleaned_plan.startswith('```python'):
            cleaned_plan = cleaned_plan[9:]  # Remove ```python
        elif cleaned_plan.startswith('```'):
            cleaned_plan = cleaned_plan[3:]   # Remove ```
        
        if cleaned_plan.endswith('```'):
            cleaned_plan = cleaned_plan[:-3]  # Remove trailing ```
        
        cleaned_plan = cleaned_plan.strip()
        
        # Debug output
        print(f"🔍 Sandbox executing code : {cleaned_plan}...")
        
        # Prepare execution environment
        allowed_globals = {
            "__builtins__": __builtins__,
            "asyncio": asyncio,
            "dispatcher": dispatcher,
            "print": print
        }
        
        local_vars = {}
        
        # Capture stdout
        stdout_backup = sys.stdout
        output_buffer = StringIO()
        sys.stdout = output_buffer
        
        try:
            # Execute the plan
            exec(cleaned_plan, allowed_globals, local_vars)
            
            # Get the solve function
            solve_func = local_vars.get("solve")
            if solve_func:
                print(f"🎯 Found solve() function, executing...")
                if asyncio.iscoroutinefunction(solve_func):
                    result = await solve_func()
                else:
                    result = solve_func()
                print(f"✅ Solve function returned: {result}")
            else:
                result = "ERROR: No solve() function found in plan"
                print(f"❌ {result}")
                
        finally:
            sys.stdout = stdout_backup
            
        # Get captured output
        captured_output = output_buffer.getvalue()
        
        # Return result or captured output
        if result:
            return str(result)
        elif captured_output:
            return captured_output
        else:
            return "FINAL_ANSWER: Plan executed but no result returned"
            
    except Exception as e:
        error_msg = f"[sandbox error: {str(e)}]"
        print(f"❌ Sandbox execution failed: {error_msg}")
        return error_msg 