"""
Base Agent Class
Common functionality and interface for all VyasaQuant agents.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BaseAgent(ABC):
    """Base class for all VyasaQuant agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = self._setup_logger()
        self.initialized = False
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger for the agent"""
        logger = logging.getLogger(f"vyasaquant.agents.{self.name}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent with necessary connections and setup"""
        pass
    
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup resources when shutting down"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the agent"""
        return {
            "name": self.name,
            "initialized": self.initialized,
            "status": "active" if self.initialized else "inactive"
        } 