"""
Example: Stock Stability Analysis using VyasaQuant
This script demonstrates how to use the Stability Checker Agent for stock analysis.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the stability checker agent
from agents.stability_checker_agent import StabilityCheckerAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def check_stock_stability(company_name: str = None, ticker_symbol: str = None):
    """
    Check the stability of a stock using EPS growth analysis.
    
    Args:
        company_name: Name of the company (optional if ticker_symbol provided)
        ticker_symbol: Stock ticker symbol (optional if company_name provided)
    """
    
    if not company_name and not ticker_symbol:
        logger.error("Either company_name or ticker_symbol must be provided")
        return
    
    # Initialize the stability checker agent
    agent = StabilityCheckerAgent()
    
    try:
        # Initialize the agent
        logger.info("Initializing VyasaQuant Stability Checker...")
        initialized = await agent.initialize()
        
        if not initialized:
            logger.error("Failed to initialize agent")
            return
        
        # Prepare request data
        request_data = {
            "years_to_analyze": 4  # Analyze last 4 years including current year
        }
        
        if company_name:
            request_data["company_name"] = company_name
        if ticker_symbol:
            request_data["ticker_symbol"] = ticker_symbol
        
        # Perform stability analysis
        logger.info(f"Analyzing stock stability for {company_name or ticker_symbol}...")
        result = await agent.process(request_data)
        
        # Display results
        print("\n" + "="*80)
        print("STOCK STABILITY ANALYSIS REPORT")
        print("="*80)
        
        if result.get('success', False):
            print(f"✅ ANALYSIS COMPLETED SUCCESSFULLY")
            print(f"📊 Company: {result['company_name']}")
            print(f"🎯 Ticker Symbol: {result['ticker_symbol']}")
            print(f"⏱️  Processing Time: {result['processing_time']:.2f} seconds")
            
            # EPS Data Section
            print(f"\n📈 EPS DATA (Last {len(result.get('eps_data', []))} years):")
            print("-" * 50)
            
            if result.get('eps_data'):
                for eps in sorted(result['eps_data'], key=lambda x: x['year']):
                    source_emoji = "🔍" if eps['source'] == "web_search" else "💾"
                    print(f"  {eps['year']}: ₹{eps['eps_value']:.2f} {source_emoji} ({eps['source']})")
            else:
                print("  No EPS data available")
            
            # Analysis Results
            print(f"\n🔍 ANALYSIS RESULTS:")
            print("-" * 30)
            
            eps_growth_rate = result.get('eps_growth_rate')
            if eps_growth_rate is not None:
                print(f"📊 EPS Growth Rate: {eps_growth_rate:.2f}%")
            else:
                print("📊 EPS Growth Rate: Not calculable")
                
            print(f"📈 EPS Trend: {'Increasing' if result['is_increasing'] else 'Not Consistently Increasing'}")
            print(f"✅ Passes Stability Check: {'Yes' if result['passes_stability_check'] else 'No'}")
            
            # Final Decision
            print(f"\n🎯 FINAL DECISION:")
            print("-" * 20)
            
            if result['passes_to_round_2']:
                print("🟢 STOCK APPROVED FOR ROUND 2 (VALUE ANALYSIS)")
                print("   ✓ EPS is consistently increasing")
                print("   ✓ EPS growth rate > 10%")
                print("   ✓ Meets stability criteria")
            else:
                print("🔴 STOCK REJECTED")
                if not result['is_increasing']:
                    print("   ✗ EPS is not consistently increasing")
                if eps_growth_rate is not None and eps_growth_rate <= 10:
                    print(f"   ✗ EPS growth rate ({eps_growth_rate:.2f}%) ≤ 10%")
                if eps_growth_rate is None:
                    print("   ✗ Could not calculate EPS growth rate")
            
            # AI Reasoning
            if result.get('reasoning'):
                print(f"\n🤖 AI ANALYSIS:")
                print("-" * 15)
                print(result['reasoning'])
            
            # Warnings and Errors
            if result.get('warnings'):
                print(f"\n⚠️  WARNINGS:")
                for warning in result['warnings']:
                    print(f"   • {warning}")
            
            if result.get('errors'):
                print(f"\n❌ ERRORS:")
                for error in result['errors']:
                    print(f"   • {error}")
                    
        else:
            print("❌ ANALYSIS FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"Analysis failed with error: {e}")
    
    finally:
        # Cleanup
        await agent.cleanup()
        logger.info("Analysis completed and resources cleaned up")

async def main():
    """Main function to run stock stability analysis"""
    
    print("🚀 VyasaQuant Stock Stability Analyzer")
    print("=" * 50)
    
    # Check if required environment variables are set
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ Error: GOOGLE_API_KEY environment variable is required")
        print("Please set your Google API key in the .env file")
        return
    
    # Example companies to analyze
    companies_to_analyze = [
        {"company_name": "Reliance Industries"},
        {"ticker_symbol": "TCS"},
        {"company_name": "Infosys Limited"},
        {"ticker_symbol": "HDFCBANK"},
        {"company_name": "ITC Limited"}
    ]
    
    print(f"\nAnalyzing {len(companies_to_analyze)} companies...")
    
    for i, company in enumerate(companies_to_analyze, 1):
        print(f"\n[{i}/{len(companies_to_analyze)}] Processing next company...")
        await check_stock_stability(**company)
        
        # Wait between analyses to avoid rate limiting
        if i < len(companies_to_analyze):
            await asyncio.sleep(3)
    
    print("\n🎉 All analyses completed!")

if __name__ == "__main__":
    asyncio.run(main()) 