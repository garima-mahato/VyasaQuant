#!/usr/bin/env python3
"""
VyasaQuant API Server Startup Script

This script starts the FastAPI server for the VyasaQuant stock analysis system.
"""

import asyncio
import os
import sys
import uvicorn
from pathlib import Path

# CRITICAL: Set Windows event loop policy for subprocess support in FastAPI
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("🖥️  Applied Windows Proactor event loop policy for FastAPI subprocess support")
    except Exception as e:
        print(f"⚠️  Failed to set Windows event loop policy: {e}")

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables for development
if not os.getenv("PYTHONPATH"):
    os.environ["PYTHONPATH"] = str(Path(__file__).parent)

def main():
    """Start the VyasaQuant API server"""
    print("🚀 Starting VyasaQuant API Server...")
    print("📊 Stock Analysis API will be available at: http://localhost:8000")
    print("📚 API Documentation will be available at: http://localhost:8000/docs")
    print("⚡ Interactive API explorer at: http://localhost:8000/redoc")
    print("\n🔧 Server Configuration:")
    print("  - Host: 0.0.0.0")
    print("  - Port: 8000")
    print("  - Reload: True (development mode)")
    print("  - Log Level: info")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    try:
        # Configure uvicorn to use Windows-compatible event loop
        uvicorn_config = {
            "app": "api.server:app",
            "host": "0.0.0.0",
            "port": 8000,
            # "reload": True, # the reload=True options causes the default ProactorEventLoop to be changed to SelectorEventLoop on windows. Refer: https://stackoverflow.com/questions/70568070/running-an-asyncio-subprocess-in-fastapi-results-in-notimplementederror
            "log_level": "info",
            "access_log": True
        }
        
        # Add Windows-specific configuration
        if sys.platform == "win32":
            uvicorn_config["loop"] = "asyncio"
            # Ensure the event loop policy is set before uvicorn starts
            import asyncio
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            print("🖥️  Configured uvicorn with Windows Proactor event loop policy")
        
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 