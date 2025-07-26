#!/usr/bin/env python3
"""
SSE Session Management for MCP Client
Connects to FastAPI + MCP server via Server-Sent Events
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Any, Optional
import uuid
import time

logger = logging.getLogger(__name__)

class MCPSSESession:
    """SSE-based MCP session that connects to FastAPI + MCP server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session_id = str(uuid.uuid4())
        self.sse_url = f"{self.base_url}/mcp/sse"
        self.messages_url = f"{self.base_url}/mcp/messages"
        self.client_session = None
        self.connected = False
        self.tools = {}
        
    async def connect(self) -> bool:
        """Connect to the MCP server via SSE with retry mechanism"""
        max_retries = 5
        base_delay = 1.0  # Start with 1 second delay
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔗 Connecting to MCP server at {self.sse_url} (attempt {attempt + 1}/{max_retries})")
                
                # Create aiohttp session
                self.client_session = aiohttp.ClientSession()
                
                # Test server health first
                async with self.client_session.get(f"{self.base_url}/health") as resp:
                    if resp.status == 200:
                        health_data = await resp.json()
                        logger.info(f"✅ Server health check passed: {health_data}")
                    else:
                        logger.error(f"❌ Server health check failed: {resp.status}")
                        await self.client_session.close()
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)  # Exponential backoff
                            logger.info(f"⏳ Retrying in {delay} seconds...")
                            await asyncio.sleep(delay)
                            continue
                        return False
                
                # First establish SSE connection to get session_id
                await self._establish_sse_connection()
                
                # Initialize MCP connection
                await self._initialize_mcp()
                
                # List available tools
                await self._list_tools()
                
                self.connected = True
                logger.info(f"✅ Connected to MCP server with {len(self.tools)} tools")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to connect to MCP server (attempt {attempt + 1}): {e}")
                if self.client_session:
                    await self.client_session.close()
                
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"⏳ Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error("❌ All connection attempts failed")
                    return False
        
        return False
    
    async def _establish_sse_connection(self):
        """Establish SSE connection to get session_id"""
        try:
            logger.info(f"🔗 Establishing SSE connection to {self.sse_url}")
            
            # Make a GET request to the SSE endpoint to establish connection
            async with self.client_session.get(
                self.sse_url,
                headers={"Accept": "text/event-stream"}
            ) as resp:
                if resp.status == 200:
                    logger.info("✅ SSE connection established")
                    # Read a few lines to establish the connection
                    async for line in resp.content:
                        if line.startswith(b'data: '):
                            data = line[6:].decode('utf-8').strip()
                            if data:
                                logger.info(f"📡 SSE data received: {data}")
                                break
                else:
                    logger.error(f"❌ SSE connection failed: {resp.status}")
                    raise Exception(f"SSE connection failed with status {resp.status}")
                    
        except Exception as e:
            logger.error(f"❌ SSE connection error: {e}")
            raise
    
    async def _initialize_mcp(self):
        """Initialize MCP protocol"""
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "stability-checker-agent",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Session-ID": self.session_id
            }
            
            async with self.client_session.post(
                self.messages_url,
                json=init_request,
                headers=headers
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    logger.info("✅ MCP initialization successful")
                    return result
                else:
                    logger.error(f"❌ MCP initialization failed: {resp.status}")
                    return None
        except Exception as e:
            logger.error(f"❌ MCP initialization error: {e}")
            return None
    
    async def _list_tools(self):
        """List available tools from the MCP server"""
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Session-ID": self.session_id
            }
            
            async with self.client_session.post(
                self.messages_url,
                json=tools_request,
                headers=headers
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if "result" in result and "tools" in result["result"]:
                        tools_list = result["result"]["tools"]
                        self.tools = {tool["name"]: tool for tool in tools_list}
                        logger.info(f"📋 Loaded {len(self.tools)} tools: {list(self.tools.keys())}")
                    return result
                else:
                    logger.error(f"❌ Tools listing failed: {resp.status}")
                    return None
        except Exception as e:
            logger.error(f"❌ Tools listing error: {e}")
            return None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if not self.connected:
            logger.error("❌ Not connected to MCP server")
            return {"success": False, "error": "Not connected to MCP server"}
        
        if tool_name not in self.tools:
            logger.error(f"❌ Tool '{tool_name}' not available. Available: {list(self.tools.keys())}")
            return {"success": False, "error": f"Tool '{tool_name}' not available"}
        
        tool_request = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),  # Use timestamp as ID
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            logger.info(f"🔧 Calling tool '{tool_name}' with arguments: {arguments}")
            
            headers = {
                "Content-Type": "application/json",
                "Session-ID": self.session_id
            }
            
            async with self.client_session.post(
                self.messages_url,
                json=tool_request,
                headers=headers
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    if "result" in result and "content" in result["result"]:
                        # Extract content from MCP response
                        content = result["result"]["content"]
                        if content and len(content) > 0:
                            # Parse the JSON text content
                            tool_result = json.loads(content[0]["text"])
                            logger.info(f"✅ Tool '{tool_name}' executed successfully")
                            return tool_result
                    
                    logger.error(f"❌ Unexpected response format from tool '{tool_name}': {result}")
                    return {"success": False, "error": "Unexpected response format"}
                    
                else:
                    logger.error(f"❌ Tool call failed with status {resp.status}")
                    return {"success": False, "error": f"HTTP {resp.status}"}
                    
        except Exception as e:
            logger.error(f"❌ Tool call error: {e}")
            return {"success": False, "error": str(e)}
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.client_session:
            await self.client_session.close()
            self.client_session = None
        self.connected = False
        logger.info("🔌 Disconnected from MCP server")

class MCPSessionManager:
    """Manages MCP sessions - updated to use proper MCP protocol"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.tools = {}
        self.connected = True  # We'll use direct MCP tool calls
        self.session = None
        
    async def initialize(self) -> bool:
        """Initialize MCP session - connect to the MCP server"""
        try:
            logger.info("🚀 Initializing MCP Session Manager")
            
            # Create SSE session for proper MCP communication
            self.session = MCPSSESession(self.server_url)
            success = await self.session.connect()
            
            if success:
                self.tools = self.session.tools
                logger.info(f"✅ MCP Session Manager initialized with {len(self.tools)} tools")
                return True
            else:
                logger.error("❌ Failed to connect to MCP server")
                return False
                
        except Exception as e:
            logger.error(f"❌ MCP Session Manager initialization failed: {e}")
            return False
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a tool using proper MCP protocol"""
        try:
            logger.info(f"🔧 Calling tool '{tool_name}' with arguments: {kwargs}")
            
            if not self.session or not self.session.connected:
                logger.error("❌ Not connected to MCP server")
                return {"success": False, "error": "Not connected to MCP server"}
            
            # Use the proper MCP session to call tools
            result = await self.session.call_tool(tool_name, kwargs)
            logger.info(f"✅ Tool '{tool_name}' executed successfully")
            return result
                
        except Exception as e:
            logger.error(f"❌ Tool call error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return list(self.tools.keys())
    
    async def cleanup(self):
        """Clean up MCP session"""
        if self.session:
            await self.session.disconnect()
        logger.info("🧹 MCP Session Manager cleaned up")

# Example usage
async def test_sse_session():
    """Test the SSE session"""
    session_manager = MCPSessionManager()
    
    try:
        # Initialize
        if await session_manager.initialize():
            print("✅ Session initialized")
            
            # List tools
            tools = session_manager.get_available_tools()
            print(f"📋 Available tools: {tools}")
            
            # Test a tool call
            if "get_ticker_symbol_tool" in tools:
                result = await session_manager.call_tool(
                    "get_ticker_symbol_tool", 
                    company_name="Hindustan Aeronautics Limited"
                )
                print(f"🔧 Tool result: {result}")
        
    finally:
        await session_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(test_sse_session()) 