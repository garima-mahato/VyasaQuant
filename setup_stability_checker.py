"""
VyasaQuant Stability Checker Setup Script
Helps users set up and verify the stability checker agent installation.
"""

import os
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    required_packages = [
        'google-genai',
        'requests',
        'beautifulsoup4',
        'python-dotenv',
        'asyncio'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} is not installed")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Run: pip install -r requirements.txt")
        return False
    
    logger.info("All dependencies are installed!")
    return True

def check_environment():
    """Check environment variables"""
    logger.info("Checking environment configuration...")
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        logger.warning("❌ .env file not found")
        logger.info("Copy .env.example to .env and configure your settings")
        return False
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check required variables
    required_vars = ['GOOGLE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            logger.error(f"❌ {var} is not set")
        else:
            logger.info(f"✅ {var} is configured")
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("Environment configuration is complete!")
    return True

def check_project_structure():
    """Check if the project structure is correct"""
    logger.info("Checking project structure...")
    
    required_paths = [
        'agents/stability_checker_agent/',
        'agents/stability_checker_agent/agent.py',
        'agents/stability_checker_agent/schemas.py',
        'mcp_servers/data_acquisition_server/',
        'mcp_servers/data_acquisition_server/tools/',
        'config/mcp_config.json'
    ]
    
    missing_paths = []
    
    for path in required_paths:
        if not Path(path).exists():
            missing_paths.append(path)
            logger.error(f"❌ {path} is missing")
        else:
            logger.info(f"✅ {path} exists")
    
    if missing_paths:
        logger.error(f"Missing paths: {', '.join(missing_paths)}")
        return False
    
    logger.info("Project structure is complete!")
    return True

async def test_stability_checker():
    """Test the stability checker agent"""
    logger.info("Testing stability checker agent...")
    
    try:
        from agents.stability_checker_agent import StabilityCheckerAgent
        
        # Initialize agent
        agent = StabilityCheckerAgent()
        initialized = await agent.initialize()
        
        if not initialized:
            logger.error("❌ Failed to initialize agent")
            return False
        
        logger.info("✅ Agent initialized successfully")
        logger.info("✅ Connected to data acquisition MCP server")
        
        # Test with sample data
        test_data = {
            "company_name": "Test Company",
            "years_to_analyze": 4
        }
        
        # Note: This will likely fail without real data, but we're testing the structure
        try:
            result = await agent.process(test_data)
            logger.info("✅ Agent processing works")
        except Exception as e:
            logger.warning(f"⚠️  Agent processing test failed (expected): {e}")
            # This is expected without real data
        
        await agent.cleanup()
        logger.info("✅ Agent cleanup successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent test failed: {e}")
        return False

def create_sample_env():
    """Create a sample .env file if it doesn't exist"""
    env_file = Path('.env')
    if not env_file.exists():
        logger.info("Creating sample .env file...")
        try:
            sample_content = """# VyasaQuant Environment Configuration

# Google API Configuration
# Required for Gemini AI integration
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# Database Configuration (if applicable)
# DATABASE_URL=postgresql://user:password@localhost/vyasaquant

# Logging Configuration
# LOG_LEVEL=INFO
# LOG_FILE=vyasaquant.log

# Web Search Configuration (optional)
# SEARCH_API_KEY=your_search_api_key_here
# SEARCH_ENGINE_ID=your_search_engine_id_here

# Rate Limiting Configuration
# API_RATE_LIMIT=10
# WEB_SEARCH_DELAY=2

# Other Configuration
# CACHE_ENABLED=true
# CACHE_TTL=3600
"""
            
            with open('.env', 'w') as env:
                env.write(sample_content)
            
            logger.info("✅ Created .env file")
            logger.warning("⚠️  Please edit .env file and set your Google API key")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create .env file: {e}")
            return False
    else:
        logger.info("✅ .env file already exists")
        return True

async def main():
    """Main setup function"""
    logger.info("🚀 VyasaQuant Stability Checker Setup")
    logger.info("=" * 50)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        logger.error("❌ Dependency check failed")
        return
    
    # Step 2: Check project structure
    if not check_project_structure():
        logger.error("❌ Project structure check failed")
        return
    
    # Step 3: Create .env file if needed
    if not create_sample_env():
        logger.error("❌ Environment file creation failed")
        return
    
    # Step 4: Check environment
    if not check_environment():
        logger.error("❌ Environment check failed")
        logger.info("Please configure your .env file and run setup again")
        return
    
    # Step 5: Test agent
    if not await test_stability_checker():
        logger.error("❌ Agent test failed")
        return
    
    logger.info("🎉 Setup completed successfully!")
    logger.info("\nArchitecture Summary:")
    logger.info("• Stability Checker Agent connects directly to Data Acquisition MCP Server")
    logger.info("• Uses existing tools: get_ticker_symbol, fetch_complete_stock_data")
    logger.info("• Fallback to web search + AI for EPS data extraction")
    logger.info("• No separate MCP server for stability checking (simplified!)")
    logger.info("\nNext steps:")
    logger.info("1. Run: python example_stability_check.py")
    logger.info("2. Or run: python test_stability_checker.py")
    logger.info("3. Start building your stock analysis workflow!")

if __name__ == "__main__":
    asyncio.run(main()) 