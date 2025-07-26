#!/usr/bin/env python3
"""
MCP Server Manager for VyasaQuant

Manages independent MCP server processes outside of FastAPI to avoid
Windows asyncio subprocess compatibility issues.
"""

import asyncio
import subprocess
import sys
import os
import time
import signal
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Set Windows event loop policy for subprocess support
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

@dataclass
class ServerConfig:
    """Configuration for an MCP server"""
    id: str
    name: str
    script_path: Path
    working_directory: Path
    description: str = ""
    env_vars: Optional[Dict[str, str]] = None

class MCPServerManager:
    """Manages independent MCP server processes"""
    
    def __init__(self):
        self.servers: Dict[str, subprocess.Popen] = {}
        self.configs: List[ServerConfig] = []
        self._setup_server_configs()
        
    def _setup_server_configs(self):
        """Setup server configurations"""
        base_path = Path(__file__).parent
        
        self.configs = [
            ServerConfig(
                id="data_acquisition_server",
                name="Financial Data Acquisition Server",
                script_path=base_path / "mcp_servers" / "data_acquisition_server" / "server.py",
                working_directory=base_path / "mcp_servers" / "data_acquisition_server",
                description="Financial data acquisition using yfinance and database operations"
            )
            # Add more server configs here as needed
        ]
    
    def start_server(self, config: ServerConfig) -> bool:
        """Start a single MCP server"""
        print(f"🚀 Starting {config.name}...")
        print(f"📁 Working directory: {config.working_directory}")
        print(f"📄 Script: {config.script_path.name}")
        
        if not config.script_path.exists():
            print(f"❌ Script not found: {config.script_path}")
            return False
            
        if not config.working_directory.exists():
            print(f"❌ Working directory not found: {config.working_directory}")
            return False
        
        try:
            # Prepare environment
            env = os.environ.copy()
            if config.env_vars:
                env.update(config.env_vars)
            
            # Start server process
            process = subprocess.Popen(
                [sys.executable, str(config.script_path)],
                cwd=str(config.working_directory),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            
            self.servers[config.id] = process
            print(f"✅ Started {config.name} (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {config.name}: {e}")
            return False
    
    def start_all_servers(self) -> int:
        """Start all configured MCP servers"""
        print("🌟 VyasaQuant MCP Server Manager")
        print("=" * 60)
        print("Starting independent MCP servers...")
        
        success_count = 0
        for config in self.configs:
            if self.start_server(config):
                success_count += 1
                time.sleep(2)  # Allow server startup time
        
        print(f"\n📊 Started {success_count}/{len(self.configs)} servers successfully")
        return success_count
    
    def check_server_health(self) -> Dict[str, bool]:
        """Check health of all running servers"""
        health_status = {}
        for server_id, process in self.servers.items():
            health_status[server_id] = process.poll() is None
        return health_status
    
    def stop_server(self, server_id: str) -> bool:
        """Stop a specific server"""
        if server_id not in self.servers:
            return False
            
        process = self.servers[server_id]
        try:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
                print(f"🛑 Stopped {server_id}")
            del self.servers[server_id]
            return True
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"🔥 Force killed {server_id}")
            del self.servers[server_id]
            return True
        except Exception as e:
            print(f"⚠️ Error stopping {server_id}: {e}")
            return False
    
    def stop_all_servers(self):
        """Stop all running servers"""
        print("\n🛑 Stopping all MCP servers...")
        for server_id in list(self.servers.keys()):
            self.stop_server(server_id)
    
    def run_forever(self):
        """Run the server manager indefinitely"""
        success_count = self.start_all_servers()
        
        if success_count == 0:
            print("❌ No servers started successfully")
            return
            
        print("\n✅ MCP servers are running independently!")
        print("💡 You can now start the FastAPI server with: python start_server.py")
        print("🔍 Server health monitoring active...")
        print("⏹️ Press Ctrl+C to stop all servers")
        
        try:
            while True:
                time.sleep(10)  # Check every 10 seconds
                health = self.check_server_health()
                
                for server_id, is_healthy in health.items():
                    if not is_healthy:
                        print(f"⚠️ Server {server_id} stopped unexpectedly")
                        # Optionally restart failed servers
                        config = next((c for c in self.configs if c.id == server_id), None)
                        if config:
                            print(f"🔄 Attempting to restart {server_id}...")
                            self.start_server(config)
                        
        except KeyboardInterrupt:
            print("\n👋 Received shutdown signal...")
            self.stop_all_servers()

def main():
    """Main entry point"""
    manager = MCPServerManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            manager.run_forever()
        elif command == "stop":
            print("🛑 Stopping all MCP servers...")
            manager.stop_all_servers()
        elif command == "status":
            manager.start_all_servers()  # Just to get status
            health = manager.check_server_health()
            print("\n📊 Server Status:")
            for server_id, is_healthy in health.items():
                status = "🟢 Running" if is_healthy else "🔴 Stopped"
                print(f"  {server_id}: {status}")
        else:
            print("Usage: python mcp_server_manager.py [start|stop|status]")
    else:
        manager.run_forever()

if __name__ == "__main__":
    main() 