# 📋 VyasaQuant Centralized Configuration System

## Overview

This directory contains all configuration files for the VyasaQuant project, providing a centralized and organized approach to managing configurations for agents, servers, and other components.

## 🗂️ Configuration Files

### 1. `agents.yaml` - Agent Configurations
Contains configurations for all AI agents in the project:
- **stability_checker_agent**: Stock stability analysis agent
- **Future agents**: Value analysis, portfolio management, etc.

### 2. `servers.yaml` - MCP Server Configurations  
Contains configurations for all MCP servers:
- **data_acquisition_server**: Financial data acquisition and database operations
- **value_analysis_server**: Stock valuation analysis
- **database_server**: Database operations and management

### 3. `mcp_config.json` - Legacy MCP Configuration
Backward compatibility for existing MCP configurations.

### 4. `config_loader.py` - Configuration Loader Utility
Python utility for loading and validating configurations across the project.

## 🚀 Usage

### Loading Agent Configuration

```python
from config.config_loader import get_stability_checker_config

# Load stability checker configuration
config = get_stability_checker_config()
print(f"Agent: {config['agent']['name']}")
```

### Loading Server Configuration

```python
from config.config_loader import load_server_config

# Load all server configurations
all_servers = load_server_config()

# Load specific server configuration
data_server = load_server_config("data_acquisition_server")
```

### Generic Configuration Loading

```python
from config.config_loader import config_loader

# Load any agent configuration
agent_config = config_loader.load_agent_config("stability_checker_agent")

# Validate configuration
is_valid = config_loader.validate_agent_config("stability_checker_agent")
```

## 🔧 Configuration Structure

### Agent Configuration Structure
```yaml
agent_name:
  agent:
    name: "Agent Display Name"
    id: "unique_agent_id"
    description: "Agent description"
  
  strategy:
    planning_mode: conservative
    exploration_mode: parallel
    max_steps: 4
    
  memory:
    memory_service: true
    sessions_dir: "memory/sessions/"
    
  servers:
    server_name:
      command: python
      args: ["server.py"]
      
  # Agent-specific configurations
  stability_analysis:
    criteria:
      eps_years: 4
      eps_growth_threshold: 10.0
```

### Server Configuration Structure
```yaml
mcp_servers:
  server_name:
    id: "server_id"
    name: "Server Display Name"
    description: "Server description"
    command: python
    args: ["server.py"]
    cwd: "./mcp_servers/server_directory"
    tools:
      - tool_name_1
      - tool_name_2
```

## 🎯 Benefits of Centralized Configuration

### ✅ **Advantages**
1. **Single Source of Truth**: All configurations in one place
2. **Easy Maintenance**: Update configurations without hunting through multiple files
3. **Consistency**: Standardized format across all components
4. **Validation**: Built-in configuration validation
5. **Version Control**: Easy to track configuration changes
6. **Reusability**: Share configurations across multiple agents

### ✅ **Before vs After**
```
Before (Scattered):
├── agents/agent1/config/profiles.yaml
├── agents/agent2/config/settings.yaml
├── servers/server1/config.json
├── servers/server2/config.yaml
└── mcp_config.json

After (Centralized):
├── config/
│   ├── agents.yaml          # All agent configs
│   ├── servers.yaml         # All server configs
│   ├── mcp_config.json      # Legacy compatibility
│   ├── config_loader.py     # Utility functions
│   └── README.md           # This guide
```

## 🔄 Migration Guide

### From Old Structure to New Structure

1. **Move Agent Configs**:
   ```bash
   # Old: agents/stability_checker_agent/config/profiles.yaml
   # New: config/agents.yaml (under stability_checker_agent key)
   ```

2. **Update Import Paths**:
   ```python
   # Old
   with open("agents/stability_checker_agent/config/profiles.yaml", "r") as f:
       config = yaml.safe_load(f)
   
   # New
   from config.config_loader import get_stability_checker_config
   config = get_stability_checker_config()
   ```

3. **Remove Duplicate Folders**:
   ```bash
   # Remove agent-specific config folders
   rm -rf agents/stability_checker_agent/config/
   ```

## 🧪 Testing Configuration

### Test Configuration Loading
```python
# Test the configuration loader
python config/config_loader.py
```

### Test Agent with New Configuration
```python
# Test agent with centralized config
python agents/stability_checker_agent/agent.py
```

### Validate All Configurations
```python
from config.config_loader import config_loader

# Validate stability checker
is_valid = config_loader.validate_agent_config("stability_checker_agent")
print(f"Stability checker config valid: {is_valid}")
```

## 🔧 Adding New Configurations

### Adding a New Agent
1. Add configuration to `config/agents.yaml`:
   ```yaml
   new_agent:
     agent:
       name: "New Agent"
       id: "new_agent_001"
       description: "Description"
     # ... other config sections
   ```

2. Use the configuration loader:
   ```python
   from config.config_loader import load_agent_config
   config = load_agent_config("new_agent")
   ```

### Adding a New Server
1. Add configuration to `config/servers.yaml`:
   ```yaml
   mcp_servers:
     new_server:
       id: "new_server"
       name: "New Server"
       command: python
       args: ["server.py"]
       cwd: "./mcp_servers/new_server"
   ```

2. Use the configuration loader:
   ```python
   from config.config_loader import load_server_config
   config = load_server_config("new_server")
   ```

## 🚨 Troubleshooting

### Common Issues

1. **FileNotFoundError: config/agents.yaml**
   ```bash
   # Ensure you're in the project root
   cd /path/to/VyasaQuant
   ls config/agents.yaml
   ```

2. **KeyError: 'stability_checker_agent'**
   ```bash
   # Check if the agent configuration exists
   grep -n "stability_checker_agent" config/agents.yaml
   ```

3. **Import Error: config_loader**
   ```python
   # Add project root to Python path
   import sys
   sys.path.append("/path/to/VyasaQuant")
   from config.config_loader import get_stability_checker_config
   ```

## 📝 Best Practices

1. **Always validate configurations** before deployment
2. **Use the configuration loader utility** instead of direct file reading
3. **Keep configurations DRY** (Don't Repeat Yourself)
4. **Document any new configuration options** in this README
5. **Test configuration changes** with the test suite

## 🔮 Future Enhancements

- [ ] Environment-specific configurations (dev, staging, prod)
- [ ] Configuration encryption for sensitive data
- [ ] Web-based configuration editor
- [ ] Configuration versioning and rollback
- [ ] Configuration templates for new agents/servers

---

**Note**: This centralized configuration system replaces the old scattered approach, providing better maintainability and consistency across the VyasaQuant project. 