# modules/action.py - Action Execution for Stock Stability Analysis

import asyncio
import sys
from io import StringIO
from typing import Any, Dict
from core.session import MultiMCP

async def run_python_sandbox(plan: str, dispatcher: MultiMCP) -> str:
    """Execute Python plan in sandbox environment"""
    
    try:
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
            exec(plan, allowed_globals, local_vars)
            
            # Get the solve function
            solve_func = local_vars.get("solve")
            if solve_func:
                if asyncio.iscoroutinefunction(solve_func):
                    result = await solve_func()
                else:
                    result = solve_func()
            else:
                result = "ERROR: No solve() function found in plan"
                
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
        return f"[sandbox error: {str(e)}]" 