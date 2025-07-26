#!/usr/bin/env python3
"""
VyasaQuant Startup Script

This script helps you start the VyasaQuant system properly on Windows
by managing the startup sequence to avoid asyncio subprocess issues.
"""

import sys
import time
import subprocess
from pathlib import Path
import argparse

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🌟 VyasaQuant Stock Analysis System")
    print("=" * 60)
    print("💡 Startup sequence optimized for Windows compatibility")

def check_requirements():
    """Check if required files exist"""
    required_files = [
        "mcp_server_manager.py",
        "start_server.py",
        "mcp_servers/data_acquisition_server/server.py"
    ]
    
    base_path = Path(__file__).parent
    missing_files = []
    
    for file_path in required_files:
        if not (base_path / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def start_mcp_servers():
    """Start MCP servers in a separate process"""
    print("\n🚀 Starting MCP servers...")
    print("💡 MCP servers will run in a separate console window")
    
    try:
        if sys.platform == "win32":
            # Windows: Start in new console window
            subprocess.Popen(
                [sys.executable, "mcp_server_manager.py"],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Unix: Start in background
            subprocess.Popen(
                [sys.executable, "mcp_server_manager.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print("✅ MCP servers starting in separate process")
        print("⏳ Waiting for servers to initialize...")
        time.sleep(8)  # Give servers time to start
        return True
        
    except Exception as e:
        print(f"❌ Failed to start MCP servers: {e}")
        return False

def start_api_server():
    """Start the FastAPI server"""
    print("\n🌐 Starting FastAPI server...")
    print("📊 Stock Analysis API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    
    try:
        subprocess.run([sys.executable, "start_server.py"])
    except KeyboardInterrupt:
        print("\n👋 FastAPI server stopped")
    except Exception as e:
        print(f"❌ Failed to start FastAPI server: {e}")

def run_agent_standalone():
    """Run the agent in standalone mode"""
    print("\n🤖 Starting standalone agent...")
    print("💡 Make sure MCP servers are running first")
    
    try:
        subprocess.run([sys.executable, "-m", "agents.stability_checker_agent.agent"])
    except KeyboardInterrupt:
        print("\n👋 Agent stopped")
    except Exception as e:
        print(f"❌ Failed to start agent: {e}")

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description="VyasaQuant Startup Script")
    parser.add_argument(
        "mode",
        choices=["full", "api", "agent", "servers"],
        help="Startup mode: full (servers + api), api (api only), agent (agent only), servers (servers only)"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    if not check_requirements():
        print("\n❌ Requirements check failed")
        sys.exit(1)
    
    if args.mode == "servers":
        print("\n📡 Starting MCP servers only...")
        if start_mcp_servers():
            print("\n✅ MCP servers started")
            print("💡 You can now start the API with: python startup.py api")
            try:
                input("\nPress Enter to stop servers...")
            except KeyboardInterrupt:
                pass
        
    elif args.mode == "api":
        print("\n🌐 Starting API server only...")
        print("💡 Make sure MCP servers are running first")
        start_api_server()
        
    elif args.mode == "agent":
        print("\n🤖 Starting standalone agent only...")
        run_agent_standalone()
        
    elif args.mode == "full":
        print("\n🔄 Starting full system...")
        
        # Start MCP servers
        if not start_mcp_servers():
            print("❌ Failed to start MCP servers")
            sys.exit(1)
        
        print("\n✅ MCP servers are running")
        print("🌐 Now starting FastAPI server...")
        
        # Start API server
        start_api_server()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python startup.py [full|api|agent|servers]")
        print("")
        print("Modes:")
        print("  full    - Start MCP servers + API server")
        print("  api     - Start API server only (requires servers running)")
        print("  agent   - Start standalone agent only (requires servers running)")
        print("  servers - Start MCP servers only")
        print("")
        print("Recommended sequence:")
        print("  1. python startup.py servers")
        print("  2. python startup.py api")
        sys.exit(1)
    
    main() 