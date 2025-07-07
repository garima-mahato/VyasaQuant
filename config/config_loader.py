#!/usr/bin/env python3
"""
Centralized Configuration Loader for VyasaQuant
Provides utilities to load configurations from the centralized config folder.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """Centralized configuration loader for VyasaQuant project"""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the configuration loader
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Configuration directory not found: {config_dir}")
    
    def load_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Load configuration for a specific agent
        
        Args:
            agent_name: Name of the agent (e.g., 'stability_checker_agent')
            
        Returns:
            Agent configuration dictionary
            
        Raises:
            FileNotFoundError: If agents.yaml doesn't exist
            KeyError: If agent configuration is not found
        """
        agents_config_path = self.config_dir / "agents.yaml"
        
        if not agents_config_path.exists():
            raise FileNotFoundError(f"Agents configuration file not found: {agents_config_path}")
        
        with open(agents_config_path, "r") as f:
            all_configs = yaml.safe_load(f)
        
        if agent_name not in all_configs:
            raise KeyError(f"Agent '{agent_name}' configuration not found in agents.yaml")
        
        return all_configs[agent_name]
    
    def load_server_config(self, server_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Load MCP server configuration
        
        Args:
            server_name: Specific server name to load (optional)
            
        Returns:
            Server configuration dictionary
        """
        servers_config_path = self.config_dir / "servers.yaml"
        
        if not servers_config_path.exists():
            raise FileNotFoundError(f"Servers configuration file not found: {servers_config_path}")
        
        with open(servers_config_path, "r") as f:
            all_configs = yaml.safe_load(f)
        
        if server_name:
            if server_name not in all_configs.get("mcp_servers", {}):
                raise KeyError(f"Server '{server_name}' configuration not found")
            return all_configs["mcp_servers"][server_name]
        
        return all_configs.get("mcp_servers", {})
    
    def load_legacy_mcp_config(self) -> Dict[str, Any]:
        """
        Load legacy MCP configuration for backward compatibility
        
        Returns:
            Legacy MCP configuration dictionary
        """
        # Try servers.yaml first
        try:
            servers_config_path = self.config_dir / "servers.yaml"
            if servers_config_path.exists():
                with open(servers_config_path, "r") as f:
                    all_configs = yaml.safe_load(f)
                    return all_configs.get("legacy_mcp_config", {})
        except:
            pass
        
        # Fallback to mcp_config.json
        mcp_config_path = self.config_dir / "mcp_config.json"
        if mcp_config_path.exists():
            with open(mcp_config_path, "r") as f:
                return json.load(f)
        
        raise FileNotFoundError("No MCP configuration found")
    
    def get_all_agents(self) -> Dict[str, Any]:
        """
        Get all available agent configurations
        
        Returns:
            Dictionary of all agent configurations
        """
        agents_config_path = self.config_dir / "agents.yaml"
        
        if not agents_config_path.exists():
            return {}
        
        with open(agents_config_path, "r") as f:
            return yaml.safe_load(f) or {}
    
    def get_all_servers(self) -> Dict[str, Any]:
        """
        Get all available server configurations
        
        Returns:
            Dictionary of all server configurations
        """
        try:
            return self.load_server_config()
        except FileNotFoundError:
            return {}
    
    def validate_agent_config(self, agent_name: str) -> bool:
        """
        Validate if an agent configuration is complete and valid
        
        Args:
            agent_name: Name of the agent to validate
            
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            config = self.load_agent_config(agent_name)
            
            # Check required sections
            required_sections = ["agent", "servers", "stability_analysis"]
            for section in required_sections:
                if section not in config:
                    return False
            
            # Check required agent fields
            agent_config = config["agent"]
            required_agent_fields = ["name", "id", "description"]
            for field in required_agent_fields:
                if field not in agent_config:
                    return False
            
            return True
            
        except (FileNotFoundError, KeyError):
            return False


# Global configuration loader instance
config_loader = ConfigLoader()


def load_agent_config(agent_name: str) -> Dict[str, Any]:
    """
    Convenience function to load agent configuration
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Agent configuration dictionary
    """
    return config_loader.load_agent_config(agent_name)


def load_server_config(server_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to load server configuration
    
    Args:
        server_name: Name of the server (optional)
        
    Returns:
        Server configuration dictionary
    """
    return config_loader.load_server_config(server_name)


def get_stability_checker_config() -> Dict[str, Any]:
    """
    Convenience function to load stability checker agent configuration
    
    Returns:
        Stability checker agent configuration
    """
    return config_loader.load_agent_config("stability_checker_agent")


# Example usage:
if __name__ == "__main__":
    # Test the configuration loader
    try:
        # Load stability checker config
        stability_config = get_stability_checker_config()
        print("✅ Stability checker configuration loaded successfully")
        print(f"Agent: {stability_config['agent']['name']}")
        print(f"Servers: {list(stability_config['servers'].keys())}")
        
        # Load all servers
        all_servers = load_server_config()
        print(f"✅ Available servers: {list(all_servers.keys())}")
        
        # Validate configuration
        is_valid = config_loader.validate_agent_config("stability_checker_agent")
        print(f"✅ Configuration valid: {is_valid}")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}") 