# agent.py - Stock Stability Checker Agent

import asyncio
import yaml
from core.loop import AgentLoop
from core.session import MultiMCP
from core.context import MemoryItem, AgentContext
import datetime
from pathlib import Path
import json
import re
import sys
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("🔑 Environment variables loaded from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed - using system environment variables only")

# Add project root to path for config imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config_loader import get_stability_checker_config

def log(stage: str, msg: str):
    """Simple timestamped console logger."""
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{stage}] {msg}")

async def main():
    print("📈 Stock Stability Checker Agent Ready")
    current_session = None

    try:
        # Load configuration using centralized loader
        profile = get_stability_checker_config()
        
        # Extract MCP server configurations
        mcp_servers_config = profile.get("servers", {})
        mcp_servers_list = []
        
        for server_id, server_config in mcp_servers_config.items():
            mcp_servers_list.append({
                "id": server_id,
                **server_config
            })
        
        mcp_servers = {server["id"]: server for server in mcp_servers_list}

        print(f"📊 Loaded configuration for: {profile['agent']['name']}")
        print(f"🔧 Available servers: {list(mcp_servers.keys())}")
        print(f"📋 Analysis workflow: {profile['stability_analysis']['criteria']['eps_years']} years EPS analysis")
        print(f"📈 Growth threshold: {profile['stability_analysis']['criteria']['eps_growth_threshold']}%")

        multi_mcp = MultiMCP(server_configs=mcp_servers_list)
        await multi_mcp.initialize()

        while True:
            user_input = input("\n📊 Enter company name or ticker to check stock stability → ")
            if user_input.lower() == 'exit':
                break
            if user_input.lower() == 'new':
                current_session = None
                continue

            # Format user input for stock stability check using config parameters
            eps_years = profile['stability_analysis']['criteria']['eps_years']
            growth_threshold = profile['stability_analysis']['criteria']['eps_growth_threshold']
            
            formatted_input = f"""
            Analyze the stock stability for: {user_input}
            
            Please follow this exact workflow:
            1. Get the ticker symbol if not provided
            2. Fetch last {eps_years} years of EPS data
            3. Check if EPS is consistently increasing across all years
            4. Calculate EPS Growth Rate (compound annual growth rate)
            5. Pass to Round 2 if EPS increasing AND EPS-GR > {growth_threshold}%
            6. Otherwise reject the stock
            
            Return FINAL_ANSWER with clear recommendation and reasoning.
            """

            while True:
                context = AgentContext(
                    user_input=formatted_input,
                    session_id=current_session,
                    dispatcher=multi_mcp,
                    mcp_server_descriptions=mcp_servers,
                )
                agent = AgentLoop(context)
                if not current_session:
                    current_session = context.session_id

                result = await agent.run()

                # Handle both string and dictionary results
                if isinstance(result, dict):
                    answer = result.get("result", str(result))
                elif isinstance(result, str):
                    answer = result
                else:
                    answer = str(result)

                if "FINAL_ANSWER:" in answer:
                    print(f"\n💡 Stock Stability Analysis Result:")
                    print(f"{answer.split('FINAL_ANSWER:')[1].strip()}")
                    break
                elif "FURTHER_PROCESSING_REQUIRED:" in answer:
                    formatted_input = answer.split("FURTHER_PROCESSING_REQUIRED:")[1].strip()
                    print(f"\n🔁 Further Processing Required: {formatted_input}")
                    continue
                else:
                    print(f"\n💡 Analysis Result: {answer}")
                    break
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you're running from the project root directory")
        print("💡 Ensure config/agents.yaml exists with stability_checker_agent configuration")
        
    except KeyboardInterrupt:
        print("\n👋 Received exit signal. Shutting down...")

if __name__ == "__main__":
    asyncio.run(main())


# Example queries:
# Reliance Industries
# RELIANCE
# TCS
# What is the EPS growth rate for Infosys over the last 4 years?
# Check if Wipro passes the stability criteria 