#!/usr/bin/env python3
"""
Quick Test Runner for Stability Checker Agent
Provides easy options to test different aspects of the agent.
"""

import asyncio
import sys
import os
from pathlib import Path

def print_header():
    print("🧪 Stability Checker Agent - Test Runner")
    print("=" * 50)
    print()

def print_menu():
    print("Select a test option:")
    print("1. 🚀 Run All Automated Tests")
    print("2. 🤖 Launch Interactive Agent")
    print("3. 🔧 Test Individual Components")
    print("4. 📊 Run Logic Tests Only")
    print("5. 🌐 Test MCP Tools")
    print("6. 📋 Show Test Guide")
    print("7. ❌ Exit")
    print()

async def run_all_tests():
    """Run the comprehensive test suite"""
    print("🚀 Running All Automated Tests...")
    print("-" * 30)
    
    try:
        # Import and run the comprehensive tests
        from test_stability_checker_refactored import StabilityCheckerTester
        tester = StabilityCheckerTester()
        await tester.run_all_tests()
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        print("💡 Make sure you're in the project root directory")

def launch_interactive_agent():
    """Launch the interactive agent"""
    print("🤖 Launching Interactive Agent...")
    print("-" * 30)
    print("💡 Use 'exit' to quit the agent")
    print("💡 Try these test inputs:")
    print("   - Reliance Industries")
    print("   - TCS")
    print("   - INFY")
    print()
    
    try:
        os.system("python agents/stability_checker_agent/agent.py")
    except Exception as e:
        print(f"❌ Error launching agent: {e}")

def test_individual_components():
    """Test individual components"""
    print("🔧 Testing Individual Components...")
    print("-" * 30)
    
    # Test utils
    print("1. Testing utils imports...")
    try:
        from utils.ticker_utils import ticker_manager
        from utils.financial_data import financial_data_manager
        print("   ✅ Utils imported successfully")
    except Exception as e:
        print(f"   ❌ Utils import error: {e}")
    
    # Test MCP tools
    print("2. Testing MCP tools...")
    try:
        from mcp_servers.data_acquisition_server.tools.get_ticker_symbol import get_ticker_symbol
        print("   ✅ MCP tools imported successfully")
    except Exception as e:
        print(f"   ❌ MCP tools import error: {e}")
    
    # Test configuration
    print("3. Testing configuration...")
    try:
        import yaml
        config_path = Path("config/agents.yaml")
        with open(config_path, "r") as f:
            all_configs = yaml.safe_load(f)
        
        # Check for stability checker agent config
        if "stability_checker_agent" in all_configs:
            print("   ✅ Centralized configuration loaded successfully")
            print(f"   ✅ Found stability_checker_agent configuration")
        else:
            print("   ⚠️  stability_checker_agent configuration not found")
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")

def run_logic_tests():
    """Run only the logic tests"""
    print("📊 Running Logic Tests...")
    print("-" * 30)
    
    # Test EPS calculation logic
    test_cases = [
        {
            "name": "Growing EPS",
            "eps_data": [10.0, 12.0, 14.5, 17.0],
            "expected_pass": True
        },
        {
            "name": "Declining EPS", 
            "eps_data": [20.0, 18.0, 15.0, 12.0],
            "expected_pass": False
        },
        {
            "name": "Low Growth EPS",
            "eps_data": [10.0, 10.5, 11.0, 11.2],
            "expected_pass": False
        }
    ]
    
    for test_case in test_cases:
        print(f"\n  Testing: {test_case['name']}")
        eps_data = test_case["eps_data"]
        
        # Calculate CAGR
        initial_eps = eps_data[0]
        final_eps = eps_data[-1]
        years = len(eps_data) - 1
        
        cagr = (((final_eps / initial_eps) ** (1/years)) - 1) * 100
        
        # Check if increasing
        is_increasing = all(eps_data[i] > eps_data[i-1] for i in range(1, len(eps_data)))
        
        # Apply criteria
        passes_criteria = is_increasing and cagr >= 10.0
        
        print(f"    EPS: {initial_eps} → {final_eps}")
        print(f"    CAGR: {cagr:.2f}%")
        print(f"    Increasing: {is_increasing}")
        print(f"    Passes: {passes_criteria}")
        
        if passes_criteria == test_case["expected_pass"]:
            print("    ✅ Test PASSED")
        else:
            print("    ❌ Test FAILED")

def test_mcp_tools():
    """Test MCP tools availability"""
    print("🌐 Testing MCP Tools...")
    print("-" * 30)
    
    tools_to_test = [
        ("get_ticker_symbol", "mcp_servers.data_acquisition_server.tools.get_ticker_symbol"),
        ("get_eps_data", "mcp_servers.data_acquisition_server.tools.database_tools"),
        ("get_income_statement", "mcp_servers.data_acquisition_server.tools.fetch_financial_data")
    ]
    
    for tool_name, module_path in tools_to_test:
        try:
            module = __import__(module_path, fromlist=[tool_name])
            tool_func = getattr(module, tool_name)
            print(f"   ✅ {tool_name} - Available")
        except Exception as e:
            print(f"   ❌ {tool_name} - Error: {e}")

def show_test_guide():
    """Show the test guide"""
    print("📋 Test Guide")
    print("-" * 30)
    print()
    print("For comprehensive testing documentation, see:")
    print("📄 test_stability_checker_guide.md")
    print()
    print("Quick commands:")
    print("   python test_stability_checker_refactored.py")
    print("   python agents/stability_checker_agent/agent.py")
    print("   python run_tests.py")
    print()

async def main():
    """Main function"""
    print_header()
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            await run_all_tests()
        elif choice == "2":
            launch_interactive_agent()
        elif choice == "3":
            test_individual_components()
        elif choice == "4":
            run_logic_tests()
        elif choice == "5":
            test_mcp_tools()
        elif choice == "6":
            show_test_guide()
        elif choice == "7":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-7.")
        
        print("\n" + "=" * 50)
        input("Press Enter to continue...")
        print()

if __name__ == "__main__":
    asyncio.run(main()) 