#!/usr/bin/env python3
"""
Startup script for VyasaQuant MCP Server
Handles environment setup and server initialization.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_dependencies():
    """Check if required files and dependencies exist"""
    current_dir = Path(__file__).parent
    
    # Check required files for the restructured architecture
    required_files = [
        'server.py',
        'tools/__init__.py',
        'tools/get_ticker_symbol.py',
        'tools/fetch_financial_data.py',
        'tools/download_reports.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (current_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    # Check Python dependencies
    try:
        import yfinance
        import pandas
        import psycopg2
        import sqlalchemy
        import requests
        print("✅ All Python dependencies found")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages: pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check if required environment variables are set"""
    required_env_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        return False
    
    print("✅ All environment variables found")
    return True

def main():
    """Main startup function"""
    print("🚀 Starting VyasaQuant MCP Server...")
    print("=" * 50)
    
    # Check environment variables
    print("📝 Checking environment variables...")
    if not check_environment():
        print("\n❌ Environment check failed. Please resolve the issues above.")
        sys.exit(1)
    
    # Check dependencies
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please resolve the issues above.")
        sys.exit(1)
    
    print("\n✅ All checks passed!")
    print(f"\n🔗 Database: {os.getenv('DB_USER')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
    print("\n🌐 Starting MCP Server in stdio mode...")
    print("💡 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the server
    try:
        from server import main as server_main
        server_main()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 