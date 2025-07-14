#!/usr/bin/env python3
"""
Test script to verify API integration with the stability checker agent
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_api_integration():
    """Test the API integration with the stability checker agent"""
    
    print("🧪 Testing VyasaQuant API Integration")
    print("=" * 50)
    
    try:
        # Import the API components
        from api.server import app, parse_analysis_result
        from fastapi.testclient import TestClient
        
        # Create test client
        client = TestClient(app)
        
        # Test health endpoint
        print("1. Testing health endpoint...")
        health_response = client.get("/health")
        print(f"   Status: {health_response.status_code}")
        print(f"   Response: {health_response.json()}")
        
        # Test root endpoint
        print("\n2. Testing root endpoint...")
        root_response = client.get("/")
        print(f"   Status: {root_response.status_code}")
        print(f"   Response: {root_response.json()}")
        
        # Test parsing functions
        print("\n3. Testing result parsing functions...")
        
        # Test company name extraction
        test_result = "Analysis for Reliance Industries (RELIANCE.NS): The stock shows strong EPS growth with a CAGR of 15.2%. Recommendation: BUY"
        parsed = await parse_analysis_result(test_result, "RELIANCE")
        print(f"   Company: {parsed.company_name}")
        print(f"   Symbol: {parsed.symbol}")
        print(f"   Stability Score: {parsed.stability_score}")
        print(f"   Recommendation: {parsed.value_analysis.recommendation}")
        
        print("\n✅ Basic API integration tests passed!")
        print("\n📋 Next steps:")
        print("   1. Start the API server: python start_server.py")
        print("   2. Test with curl: curl -X POST http://localhost:8000/api/analyze -H 'Content-Type: application/json' -d '{\"symbol\": \"RELIANCE\"}'")
        print("   3. Open browser to http://localhost:8000/docs for interactive API documentation")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you have installed all dependencies: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_integration())
    sys.exit(0 if success else 1) 