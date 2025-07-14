#!/usr/bin/env python3
"""
Debug script to test MCP server communication
"""

import asyncio
import json
import sys
from pathlib import Path

# Set Windows event loop policy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    print("🖥️  Applied Windows Proactor event loop policy")

async def test_mcp_server():
    """Test MCP server communication directly"""
    print("🔍 Testing MCP server communication...")
    
    try:
        # Start MCP server process
        server_dir = Path("mcp_servers/data_acquisition_server")
        server_script = server_dir / "server.py"
        
        print(f"📍 Server directory: {server_dir.resolve()}")
        print(f"📍 Server script: {server_script.resolve()}")
        
        if not server_script.exists():
            print(f"❌ Server script not found: {server_script}")
            return
        
        print("🚀 Starting MCP server subprocess...")
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "server.py",
            cwd=str(server_dir),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print("✅ MCP server process started")
        
        # Wait a bit for server to initialize
        await asyncio.sleep(3)
        
        # Check if process is still running
        if proc.returncode is not None:
            print(f"❌ Server process exited with code: {proc.returncode}")
            stderr_output = await proc.stderr.read()
            if stderr_output:
                print(f"📋 Server stderr:\n{stderr_output.decode()}")
            return
        
        # Test 1: tools/list
        print("\n🧪 Test 1: tools/list")
        list_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        proc.stdin.write(json.dumps(list_request).encode() + b'\n')
        await proc.stdin.drain()
        
        try:
            response_data = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)
            if response_data:
                response = json.loads(response_data.decode())
                print(f"✅ tools/list response: {json.dumps(response, indent=2)}")
            else:
                print("❌ No response to tools/list")
        except asyncio.TimeoutError:
            print("❌ Timeout waiting for tools/list response")
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Raw response: {response_data}")
        
        # Test 2: tools/call get_ticker_symbol
        print("\n🧪 Test 2: tools/call get_ticker_symbol")
        call_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_ticker_symbol",
                "arguments": {
                    "company_name": "Hindustan Aeronautics Limited"
                }
            }
        }
        
        proc.stdin.write(json.dumps(call_request).encode() + b'\n')
        await proc.stdin.drain()
        
        try:
            response_data = await asyncio.wait_for(proc.stdout.readline(), timeout=10.0)
            if response_data:
                response = json.loads(response_data.decode())
                print(f"✅ tool call response: {json.dumps(response, indent=2)}")
                
                # Extract the actual result
                if "result" in response:
                    result = response["result"]
                    print(f"\n📊 Extracted result: {json.dumps(result, indent=2)}")
                    
                    # Check if it matches expected format
                    if isinstance(result, dict) and "content" in result:
                        content = result.get("content", [])
                        if content and isinstance(content, list) and len(content) > 0:
                            text_content = content[0].get("text", "")
                            try:
                                parsed_result = json.loads(text_content)
                                print(f"\n🎯 Parsed tool result: {json.dumps(parsed_result, indent=2)}")
                            except json.JSONDecodeError as e:
                                print(f"❌ Could not parse text content as JSON: {e}")
                                print(f"Text content: {text_content}")
                        else:
                            print("❌ Content format is incorrect")
                    else:
                        print("❌ Result format is incorrect - missing 'content' field")
                else:
                    print("❌ Response missing 'result' field")
            else:
                print("❌ No response to tool call")
        except asyncio.TimeoutError:
            print("❌ Timeout waiting for tool call response")
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Raw response: {response_data}")
        
        # Cleanup
        print("\n🧹 Cleaning up...")
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
        
        print("✅ Test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        print(f"📋 Traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 