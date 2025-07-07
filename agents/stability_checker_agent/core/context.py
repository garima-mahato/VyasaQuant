# core/context.py - Stock Stability Checker Agent Context

from typing import List, Optional, Dict, Any
from modules.memory import MemoryManager, MemoryItem
from core.session import MultiMCP  # For dispatcher typing
from pathlib import Path
import yaml
import time
import uuid
from datetime import datetime
from pydantic import BaseModel
import sys

# Add project root to path for config imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from config.config_loader import get_stability_checker_config

class StrategyProfile(BaseModel):
    planning_mode: str
    exploration_mode: Optional[str] = None
    memory_fallback_enabled: bool
    max_steps: int
    max_lifelines_per_step: int

class AgentProfile:
    def __init__(self):
        # Use centralized configuration loader
        config = get_stability_checker_config()

        self.name = config["agent"]["name"]
        self.id = config["agent"]["id"]
        self.description = config["agent"]["description"]

        self.strategy = StrategyProfile(**config["strategy"])
        self.memory_config = config["memory"]
        
        # Handle different config structures
        if "ai_model" in config:
            self.llm_config = config["ai_model"]
        elif "llm" in config:
            self.llm_config = config["llm"]
        else:
            # Default AI model config
            self.llm_config = {
                "provider": "google",
                "model": "gemini-pro",
                "temperature": 0.1,
                "max_tokens": 4000
            }
        
        # Handle persona (may not exist in all configs)
        self.persona = config.get("persona", {
            "role": "Stock Stability Analyst",
            "expertise": "EPS analysis and growth rate calculations"
        })

    def __repr__(self):
        return f"<AgentProfile {self.name} ({self.strategy})>"

class AgentContext:
    """Holds all session state, user input, memory, and strategies for stock analysis."""

    def __init__(
        self,
        user_input: str,
        session_id: Optional[str] = None,
        dispatcher: Optional[MultiMCP] = None,
        mcp_server_descriptions: Optional[List[Any]] = None,
    ):
        if session_id is None:
            today = datetime.now()
            ts = int(time.time())
            uid = uuid.uuid4().hex[:6]
            session_id = f"{today.year}/{today.month:02}/{today.day:02}/stock-stability-{ts}-{uid}"

        self.user_input = user_input
        self.agent_profile = AgentProfile()
        self.memory = MemoryManager(session_id=session_id)
        self.session_id = self.memory.session_id
        self.dispatcher = dispatcher
        self.mcp_server_descriptions = mcp_server_descriptions
        self.step = 0
        self.task_progress = []  # Track stock analysis progress
        self.final_answer = None
        
        # Stock analysis specific context
        self.stock_analysis_data = {
            "company_name": None,
            "ticker_symbol": None,
            "eps_data": [],
            "growth_rate": None,
            "is_increasing": None,
            "passes_stability_check": None,
            "passes_to_round_2": None
        }

        # Log session start
        self.add_memory(MemoryItem(
            timestamp=time.time(),
            text=f"Started stock stability analysis session: {user_input} at {datetime.utcnow().isoformat()}",
            type="run_metadata",
            session_id=self.session_id,
            tags=["run_start", "stock_analysis"],
            user_query=user_input,
            metadata={
                "start_time": datetime.now().isoformat(),
                "step": self.step,
                "analysis_type": "stock_stability"
            }
        ))

    def add_memory(self, item: MemoryItem):
        """Add item to memory"""
        self.memory.add(item)

    def update_stock_analysis_data(self, key: str, value: Any):
        """Update stock analysis specific data"""
        if key in self.stock_analysis_data:
            self.stock_analysis_data[key] = value
            self.add_memory(MemoryItem(
                timestamp=time.time(),
                text=f"Updated stock analysis data: {key} = {value}",
                type="analysis_update",
                session_id=self.session_id,
                tags=["stock_data", "analysis_progress"],
                user_query=self.user_input,
                metadata={
                    "key": key,
                    "value": value,
                    "step": self.step
                }
            ))

    def get_stock_analysis_summary(self) -> Dict[str, Any]:
        """Get current stock analysis summary"""
        return {
            "progress": self.stock_analysis_data,
            "current_step": self.step,
            "task_progress": self.task_progress,
            "session_id": self.session_id
        }

    def format_history_for_llm(self) -> str:
        """Format history for LLM with stock analysis context"""
        if not hasattr(self, 'tool_calls') or not self.tool_calls:
            return "No previous stock analysis actions"
            
        history = []
        for i, trace in enumerate(self.tool_calls, 1):
            result_str = str(trace.result)
            if i < len(self.tool_calls):  # Previous steps
                if len(result_str) > 100:
                    result_str = f"{result_str[:100]}... [STOCK DATA TRUNCATED]"
            
            history.append(f"{i}. Stock Analysis Tool: {trace.tool_name} with {trace.arguments}\nResult: {result_str}")
        
        return "\n\n".join(history)

    def log_subtask(self, tool_name: str, status: str = "pending"):
        """Log the start of a new stock analysis subtask."""
        self.task_progress.append({
            "step": self.step,
            "tool": tool_name,
            "status": status,
            "timestamp": time.time(),
            "analysis_type": "stock_stability"
        })

    def update_subtask_status(self, tool_name: str, status: str):
        """Update the status of an existing stock analysis subtask."""
        for item in reversed(self.task_progress):
            if item["tool"] == tool_name and item["step"] == self.step:
                item["status"] = status
                item["updated_at"] = time.time()
                break

    def get_analysis_stage(self) -> str:
        """Get current analysis stage based on progress"""
        if self.stock_analysis_data["ticker_symbol"] is None:
            return "ticker_lookup"
        elif not self.stock_analysis_data["eps_data"]:
            return "eps_data_collection"
        elif self.stock_analysis_data["growth_rate"] is None:
            return "growth_rate_calculation"
        elif self.stock_analysis_data["passes_to_round_2"] is None:
            return "stability_assessment"
        else:
            return "analysis_complete"

    def __repr__(self):
        return f"<StockAnalysisContext step={self.step}, stage={self.get_analysis_stage()}, session_id={self.session_id}>" 