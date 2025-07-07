"""
Test Script for Stability Checker Agent
Demonstrates the functionality of the AI-powered stock stability analysis.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the stability checker agent
from agents.stability_checker_agent import StabilityCheckerAgent
from agents.stability_checker_agent.schemas import EPSData

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_stability_checker():
    """Test the stability checker agent with sample companies"""
    
    # Check if required environment variables are set
    if not os.getenv('GOOGLE_API_KEY'):
        logger.error("GOOGLE_API_KEY environment variable is required")
        return
    
    # Initialize the stability checker agent
    agent = StabilityCheckerAgent()
    
    try:
        # Initialize the agent
        logger.info("Initializing Stability Checker Agent...")
        initialized = await agent.initialize()
        
        if not initialized:
            logger.error("Failed to initialize agent")
            return
        
        # Test companies for stability analysis
        test_companies = [
            {
                "name": "Test with Company Name",
                "data": {
                    "company_name": "Reliance Industries",
                    "years_to_analyze": 4
                }
            },
            {
                "name": "Test with Ticker Symbol",
                "data": {
                    "ticker_symbol": "RELIANCE",
                    "years_to_analyze": 4
                }
            },
            {
                "name": "Test with Both Name and Ticker",
                "data": {
                    "company_name": "Tata Consultancy Services",
                    "ticker_symbol": "TCS",
                    "years_to_analyze": 4
                }
            }
        ]
        
        # Run stability checks
        for test_case in test_companies:
            logger.info(f"\n{'='*60}")
            logger.info(f"Running: {test_case['name']}")
            logger.info(f"{'='*60}")
            
            try:
                # Process the stability check
                result = await agent.process(test_case['data'])
                
                # Display results
                if result.get('success', False):
                    logger.info(f"✅ Analysis completed successfully!")
                    logger.info(f"Company: {result['company_name']}")
                    logger.info(f"Ticker: {result['ticker_symbol']}")
                    logger.info(f"EPS Growth Rate: {result.get('eps_growth_rate', 'N/A')}%")
                    logger.info(f"EPS Increasing: {result['is_increasing']}")
                    logger.info(f"Passes Stability Check: {result['passes_stability_check']}")
                    logger.info(f"Advances to Round 2: {result['passes_to_round_2']}")
                    logger.info(f"Processing Time: {result['processing_time']:.2f} seconds")
                    
                    # Display EPS data
                    if result.get('eps_data'):
                        logger.info("\nEPS Data:")
                        for eps in result['eps_data']:
                            logger.info(f"  Year {eps['year']}: ₹{eps['eps_value']:.2f} (Source: {eps['source']})")
                    
                    # Display AI reasoning
                    if result.get('reasoning'):
                        logger.info(f"\nAI Analysis:\n{result['reasoning']}")
                else:
                    logger.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"❌ Error running test case: {e}")
            
            # Wait between test cases
            await asyncio.sleep(2)
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
    
    finally:
        # Cleanup
        await agent.cleanup()
        logger.info("Test completed and agent cleaned up")

async def test_with_custom_eps_data():
    """Test the stability checker with custom EPS data"""
    
    logger.info(f"\n{'='*60}")
    logger.info("Testing with Custom EPS Data")
    logger.info(f"{'='*60}")
    
    # Sample EPS data for testing
    custom_eps_data = [
        {"year": 2021, "eps_value": 50.25},
        {"year": 2022, "eps_value": 58.75},
        {"year": 2023, "eps_value": 67.20},
        {"year": 2024, "eps_value": 78.90}
    ]
    
    agent = StabilityCheckerAgent()
    
    try:
        await agent.initialize()
        
        # Convert to EPSData objects and test the analysis method directly
        eps_objects = [
            EPSData(
                year=data["year"],
                eps_value=data["eps_value"],
                source="test_data",
                confidence=1.0
            )
            for data in custom_eps_data
        ]
        
        # Use the analyze_eps_data method directly
        analysis = await agent._analyze_eps_data(eps_objects)
        
        logger.info("Custom EPS Analysis Results:")
        logger.info(f"Growth Rate: {analysis['growth_rate']:.2f}%")
        logger.info(f"Is Increasing: {analysis['is_increasing']}")
        logger.info(f"Passes Stability Check: {analysis['passes_stability_check']}")
        logger.info(f"Advances to Round 2: {analysis['passes_to_round_2']}")
        
    except Exception as e:
        logger.error(f"Custom EPS test failed: {e}")
    
    finally:
        await agent.cleanup()

async def test_direct_data_acquisition_tools():
    """Test the agent's direct usage of data acquisition tools"""
    
    logger.info(f"\n{'='*60}")
    logger.info("Testing Direct Data Acquisition Tools Usage")
    logger.info(f"{'='*60}")
    
    agent = StabilityCheckerAgent()
    
    try:
        await agent.initialize()
        
        # Test ticker symbol resolution
        logger.info("Testing ticker symbol resolution...")
        ticker_result = await agent._get_ticker_symbol("Reliance Industries")
        logger.info(f"Ticker result: {ticker_result}")
        
        # Test financial data fetch (if ticker found)
        if ticker_result.get("success", False):
            ticker_symbol = ticker_result["ticker_symbol"]
            logger.info(f"Testing financial data fetch for {ticker_symbol}...")
            
            # Try to fetch EPS data using MCP tools
            eps_data = await agent._fetch_eps_from_mcp(ticker_symbol, [2021, 2022, 2023, 2024])
            logger.info(f"EPS data from MCP tools: {len(eps_data)} records found")
        
    except Exception as e:
        logger.error(f"Direct tools test failed: {e}")
    
    finally:
        await agent.cleanup()

async def main():
    """Main test function"""
    logger.info("Starting Stability Checker Agent Tests")
    
    # Run main stability checker tests
    await test_stability_checker()
    
    # Run custom EPS data test
    await test_with_custom_eps_data()
    
    # Test direct data acquisition tools usage
    await test_direct_data_acquisition_tools()
    
    logger.info("All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 