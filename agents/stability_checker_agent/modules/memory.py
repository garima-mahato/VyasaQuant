# modules/memory.py - Memory Management for Stock Stability Analysis

import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel

class MemoryItem(BaseModel):
    """Individual memory item for stock analysis"""
    timestamp: float
    text: str
    type: str  # "run_metadata", "tool_output", "analysis_update", "user_query"
    session_id: str
    tags: List[str]
    user_query: str
    metadata: Dict[str, Any] = {}

class MemoryManager:
    """Manages memory for stock stability analysis sessions"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory_dir = Path("agents/stability_checker_agent/memory")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Session-specific memory file
        self.session_file = self.memory_dir / f"{session_id.replace('/', '_')}.json"
        
        # In-memory storage for current session
        self.items: List[MemoryItem] = []
        self.load_session()
    
    def add(self, item: MemoryItem):
        """Add a memory item"""
        self.items.append(item)
        self.save_session()
    
    def add_tool_output(
        self, 
        tool_name: str, 
        tool_args: Dict[str, Any], 
        tool_result: Any,
        success: bool = True,
        tags: Optional[List[str]] = None
    ):
        """Add tool output to memory"""
        tags = tags or []
        tags.extend(["tool_output", tool_name])
        
        item = MemoryItem(
            timestamp=time.time(),
            text=f"Tool {tool_name} executed with args {tool_args}",
            type="tool_output",
            session_id=self.session_id,
            tags=tags,
            user_query="",
            metadata={
                "tool_name": tool_name,
                "tool_args": tool_args,
                "tool_result": tool_result,
                "success": success,
                "timestamp": datetime.now().isoformat()
            }
        )
        self.add(item)
    
    def add_analysis_update(
        self,
        analysis_stage: str,
        update_data: Dict[str, Any],
        user_query: str = ""
    ):
        """Add stock analysis update to memory"""
        item = MemoryItem(
            timestamp=time.time(),
            text=f"Stock analysis update: {analysis_stage}",
            type="analysis_update",
            session_id=self.session_id,
            tags=["analysis_update", analysis_stage, "stock_analysis"],
            user_query=user_query,
            metadata={
                "analysis_stage": analysis_stage,
                "update_data": update_data,
                "timestamp": datetime.now().isoformat()
            }
        )
        self.add(item)
    
    def get_session_items(self) -> List[MemoryItem]:
        """Get all items for current session"""
        return self.items
    
    def get_items_by_type(self, item_type: str) -> List[MemoryItem]:
        """Get items by type"""
        return [item for item in self.items if item.type == item_type]
    
    def get_items_by_tag(self, tag: str) -> List[MemoryItem]:
        """Get items by tag"""
        return [item for item in self.items if tag in item.tags]
    
    def get_tool_outputs(self) -> List[MemoryItem]:
        """Get all tool outputs"""
        return self.get_items_by_type("tool_output")
    
    def get_analysis_updates(self) -> List[MemoryItem]:
        """Get all analysis updates"""
        return self.get_items_by_type("analysis_update")
    
    def get_stock_analysis_history(self) -> Dict[str, Any]:
        """Get stock analysis history for current session"""
        analysis_items = self.get_items_by_tag("stock_analysis")
        tool_outputs = self.get_tool_outputs()
        
        return {
            "session_id": self.session_id,
            "analysis_items": [item.dict() for item in analysis_items],
            "tool_outputs": [item.dict() for item in tool_outputs],
            "total_items": len(self.items)
        }
    
    def search_memory(self, query: str) -> List[MemoryItem]:
        """Search memory items by text content"""
        query_lower = query.lower()
        results = []
        
        for item in self.items:
            if (query_lower in item.text.lower() or 
                query_lower in item.user_query.lower() or
                any(query_lower in tag.lower() for tag in item.tags)):
                results.append(item)
        
        return results
    
    def get_recent_items(self, count: int = 10) -> List[MemoryItem]:
        """Get most recent memory items"""
        return sorted(self.items, key=lambda x: x.timestamp, reverse=True)[:count]
    
    def get_eps_data_history(self) -> List[Dict[str, Any]]:
        """Get EPS data collection history"""
        eps_items = self.get_items_by_tag("eps_data")
        return [item.metadata for item in eps_items if "eps_data" in item.metadata]
    
    def get_growth_rate_history(self) -> List[Dict[str, Any]]:
        """Get growth rate calculation history"""
        growth_items = self.get_items_by_tag("growth_rate")
        return [item.metadata for item in growth_items if "growth_rate" in item.metadata]
    
    def get_stability_assessments(self) -> List[Dict[str, Any]]:
        """Get stability assessment history"""
        stability_items = self.get_items_by_tag("stability_assessment")
        return [item.metadata for item in stability_items if "stability_result" in item.metadata]
    
    def save_session(self):
        """Save current session to disk"""
        try:
            session_data = {
                "session_id": self.session_id,
                "items": [item.dict() for item in self.items],
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Failed to save session: {e}")
    
    def load_session(self):
        """Load session from disk"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                
                self.items = [MemoryItem(**item) for item in session_data.get("items", [])]
                print(f"📚 Loaded {len(self.items)} memory items for session {self.session_id}")
            else:
                self.items = []
                print(f"📚 Starting new session: {self.session_id}")
                
        except Exception as e:
            print(f"⚠️ Failed to load session: {e}")
            self.items = []
    
    def clear_session(self):
        """Clear current session memory"""
        self.items = []
        if self.session_file.exists():
            self.session_file.unlink()
        print(f"🧹 Cleared session memory: {self.session_id}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary statistics"""
        tool_outputs = self.get_tool_outputs()
        analysis_updates = self.get_analysis_updates()
        
        return {
            "session_id": self.session_id,
            "total_items": len(self.items),
            "tool_outputs": len(tool_outputs),
            "analysis_updates": len(analysis_updates),
            "start_time": min(item.timestamp for item in self.items) if self.items else None,
            "last_activity": max(item.timestamp for item in self.items) if self.items else None,
            "tags": list(set(tag for item in self.items for tag in item.tags))
        } 