# core/session.py - MCP Session Management for Stock Stability Analysis

import asyncio
import subprocess
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys
import os

# CRITICAL: Set Windows event loop policy for subprocess support
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("🖥️  Applied Windows Proactor event loop policy for MCP servers")
    except Exception as e:
        print(f"⚠️  Failed to set Windows event loop policy: {e}")

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
        self.log_forwarding_task = None
        
    async def start(self):
        """Start the MCP server process"""
        try:
            # Construct absolute paths to avoid path issues
            cwd_path = Path(self.cwd).resolve()
            script_path = cwd_path / self.script
            
            # Debug information
            print(f"🔍 Starting MCP server {self.id}")
            print(f"📍 Working directory: {cwd_path}")
            print(f"📍 Script path: {script_path}")
            
            # Verify the script exists
            if not script_path.exists():
                print(f"❌ Script file does not exist: {script_path}")
                return False
            
            # Verify the working directory exists
            if not cwd_path.exists():
                print(f"❌ Working directory does not exist: {cwd_path}")
                return False
            
            # Try subprocess creation with Windows compatibility
            try:
                self.process = await asyncio.create_subprocess_exec(
                    sys.executable, self.script,
                    cwd=str(cwd_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    stdin=asyncio.subprocess.PIPE
                )
                print(f"✅ Subprocess created successfully for {self.id}")
                
            except NotImplementedError as e:
                print(f"❌ asyncio subprocess not supported - {e}")
                print(f"💡 This is a Windows/asyncio event loop policy issue")
                print(f"💡 Try restarting the server - the event loop policy should now be correctly set")
                return False
            
            # Start log forwarding task
            self.log_forwarding_task = asyncio.create_task(self._forward_logs())
            
            # Wait a bit for server to start
            await asyncio.sleep(3)
            
            # Check if process is still running
            if self.process.returncode is not None:
                print(f"❌ Server process {self.id} exited with code: {self.process.returncode}")
                
                # Read stderr to see what went wrong
                stderr_output = await self.process.stderr.read()
                if stderr_output:
                    print(f"📋 Server stderr:\n{stderr_output.decode()}")
                
                # Read stdout too
                stdout_output = await self.process.stdout.read()
                if stdout_output:
                    print(f"📋 Server stdout:\n{stdout_output.decode()}")
                
                return False
            
            # List available tools
            await self._list_tools()
            
            print(f"✅ Started MCP server: {self.id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start MCP server {self.id}: {e}")
            import traceback
            print(f"📋 Traceback:\n{traceback.format_exc()}")
            return False
    
    async def _forward_logs(self):
        """Forward subprocess logs to console"""
        if not self.process:
            return
            
        try:
            while self.process.returncode is None:
                # Check for stderr logs (this is where most logs go)
                try:
                    stderr_line = await asyncio.wait_for(
                        self.process.stderr.readline(), 
                        timeout=0.5  # Increased timeout
                    )
                    if stderr_line:
                        log_message = stderr_line.decode().strip()
                        if log_message:
                            print(f"[{self.id}] {log_message}")
                except asyncio.TimeoutError:
                    pass
                
                # For stdout, be more careful about JSON-RPC messages
                try:
                    # Use a non-blocking read for stdout
                    if self.process.stdout:
                        stdout_line = await asyncio.wait_for(
                            self.process.stdout.readline(), 
                            timeout=0.1
                        )
                        if stdout_line:
                            log_message = stdout_line.decode().strip()
                            # Only forward if it's not a JSON-RPC message
                            if log_message and not self._is_jsonrpc_message(log_message):
                                print(f"[{self.id}] {log_message}")
                except asyncio.TimeoutError:
                    pass
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.01)
                
        except Exception as e:
            print(f"⚠️ Log forwarding error for {self.id}: {e}")
    
    def _is_jsonrpc_message(self, message: str) -> bool:
        """Check if a message is a JSON-RPC message"""
        try:
            if message.startswith('{') and message.endswith('}'):
                data = json.loads(message)
                return "jsonrpc" in data or "id" in data or "method" in data
        except:
            pass
        return False
    
    async def _list_tools(self):
        """List available tools from the server"""
        try:
            # Temporarily pause log forwarding to avoid stdout conflicts
            log_task = self.log_forwarding_task
            if log_task:
                log_task.cancel()
                try:
                    await log_task
                except asyncio.CancelledError:
                    pass
            
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
            
            # Restart log forwarding
            self.log_forwarding_task = asyncio.create_task(self._forward_logs())
                    
        except Exception as e:
            print(f"⚠️ Could not list tools for {self.id}: {e}")
            # Populate with default tools so the server can still be used
            self._populate_default_tools()
            
            # Restart log forwarding even if there was an error
            if not self.log_forwarding_task:
                self.log_forwarding_task = asyncio.create_task(self._forward_logs())
    
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
        # Cancel log forwarding task first
        if self.log_forwarding_task:
            self.log_forwarding_task.cancel()
            try:
                await self.log_forwarding_task
            except asyncio.CancelledError:
                pass
            self.log_forwarding_task = None
        
        if self.process:
            try:
                if self.process.returncode is None:
                    self.process.terminate()
                    await self.process.wait()
                    print(f"🛑 Stopped MCP server: {self.id}")
                else:
                    print(f"🛑 MCP server {self.id} was already stopped")
            except ProcessLookupError:
                print(f"⚠️ MCP server {self.id} process already terminated")
            except Exception as e:
                print(f"⚠️ Error stopping MCP server {self.id}: {e}")


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