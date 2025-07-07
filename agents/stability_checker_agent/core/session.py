# core/session.py - MCP Session Management for Stock Stability Analysis

import asyncio
import subprocess
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys
import os

class MCPServerProcess:
    """Manages individual MCP server processes"""
    
    def __init__(self, server_config: Dict[str, Any]):
        self.id = server_config["id"]
        self.script = server_config["script"]
        self.cwd = server_config.get("cwd", ".")
        self.description = server_config.get("description", "")
        self.capabilities = server_config.get("capabilities", [])
        self.process = None
        self.tools = {}
        
    async def start(self):
        """Start the MCP server process"""
        try:
            # Change to the working directory
            script_path = Path(self.cwd) / self.script
            
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path),
                cwd=self.cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            
            # Wait a bit for server to start
            await asyncio.sleep(1)
            
            # List available tools
            await self._list_tools()
            
            print(f"✅ Started MCP server: {self.id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start MCP server {self.id}: {e}")
            return False
    
    async def _list_tools(self):
        """List available tools from the server"""
        try:
            # Send tools/list request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            if self.process and self.process.stdin:
                self.process.stdin.write(json.dumps(request).encode() + b'\n')
                await self.process.stdin.drain()
                
                # Read response with timeout
                try:
                    response_data = await asyncio.wait_for(
                        self.process.stdout.readline(), 
                        timeout=5.0
                    )
                    if response_data:
                        response = json.loads(response_data.decode())
                        if "result" in response and "tools" in response["result"]:
                            for tool in response["result"]["tools"]:
                                self.tools[tool["name"]] = tool
                            print(f"📊 Server {self.id} has {len(self.tools)} tools: {list(self.tools.keys())}")
                        else:
                            print(f"⚠️  Server {self.id} response missing tools: {response}")
                    else:
                        print(f"⚠️  No response from server {self.id}")
                except asyncio.TimeoutError:
                    print(f"⚠️  Timeout waiting for tools list from server {self.id}")
                    # Even if we can't list tools, assume server is working
                    # and populate with expected tools
                    self._populate_default_tools()
                    
        except Exception as e:
            print(f"⚠️ Could not list tools for {self.id}: {e}")
            # Populate with default tools so the server can still be used
            self._populate_default_tools()
    
    def _populate_default_tools(self):
        """Populate default tools when tool listing fails"""
        if self.id == "data_acquisition_server":
            default_tools = [
                "get_ticker_symbol", "get_income_statement", "get_eps_data",
                "get_basic_stock_info", "fetch_complete_stock_data",
                "search_companies", "get_financial_statements"
            ]
            for tool_name in default_tools:
                self.tools[tool_name] = {
                    "name": tool_name,
                    "description": f"Stock analysis tool: {tool_name}",
                    "inputSchema": {"type": "object", "properties": {}}
                }
            print(f"📊 Server {self.id} populated with {len(self.tools)} default tools")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool"""
        try:
            request = {
                "jsonrpc": "2.0",
                "id": int(time.time()),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            if self.process and self.process.stdin:
                self.process.stdin.write(json.dumps(request).encode() + b'\n')
                await self.process.stdin.drain()
                
                # Read response
                response_data = await self.process.stdout.readline()
                if response_data:
                    response = json.loads(response_data.decode())
                    if "result" in response:
                        return response["result"]
                    elif "error" in response:
                        return {"error": response["error"]}
                        
        except Exception as e:
            return {"error": str(e)}
    
    async def stop(self):
        """Stop the MCP server process"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print(f"🛑 Stopped MCP server: {self.id}")


class MultiMCP:
    """Manages multiple MCP servers for stock stability analysis"""
    
    def __init__(self, server_configs: List[Dict[str, Any]]):
        self.servers = {}
        self.server_configs = server_configs
        self.initialized = False
        
    async def initialize(self):
        """Initialize all MCP servers"""
        print("🚀 Initializing MCP servers for stock stability analysis...")
        
        for config in self.server_configs:
            server = MCPServerProcess(config)
            success = await server.start()
            if success:
                self.servers[config["id"]] = server
            else:
                print(f"⚠️ Failed to initialize server: {config['id']}")
        
        self.initialized = True
        print(f"✅ Initialized {len(self.servers)} MCP servers")
    
    def get_server(self, server_id: str) -> Optional[MCPServerProcess]:
        """Get a specific server by ID"""
        return self.servers.get(server_id)
    
    def get_tools_from_servers(self, server_ids: List[str]) -> Dict[str, Any]:
        """Get tools from specified servers"""
        tools = {}
        for server_id in server_ids:
            server = self.get_server(server_id)
            if server:
                tools.update(server.tools)
        return tools
    
    def get_all_tools(self) -> Dict[str, Any]:
        """Get all available tools from all servers"""
        all_tools = {}
        for server in self.servers.values():
            all_tools.update(server.tools)
        return all_tools
    
    async def call_tool(self, server_id: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on a specific server"""
        server = self.get_server(server_id)
        if server:
            return await server.call_tool(tool_name, arguments)
        else:
            return {"error": f"Server {server_id} not found"}
    
    def get_server_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all servers"""
        capabilities = {}
        for server_id, server in self.servers.items():
            capabilities[server_id] = server.capabilities
        return capabilities
    
    def get_stock_analysis_servers(self) -> List[str]:
        """Get servers suitable for stock analysis"""
        stock_servers = []
        for server_id, server in self.servers.items():
            # Check if server has stock/finance related capabilities
            if any(cap in server.capabilities for cap in [
                'stock_analysis', 'financial_data', 'eps_analysis', 
                'web_search', 'data_extraction', 'math_calculation'
            ]):
                stock_servers.append(server_id)
        return stock_servers
    
    async def cleanup(self):
        """Cleanup all MCP servers"""
        for server in self.servers.values():
            await server.stop()
        self.servers.clear()
        print("🧹 Cleaned up all MCP servers") 