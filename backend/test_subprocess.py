#!/usr/bin/env python3
"""
Test script to verify asyncio subprocess creation on Windows
"""

import asyncio
import sys
from pathlib import Path

async def test_subprocess_creation():
    """Test if we can create subprocess on Windows"""
    print(f"🖥️  Platform: {sys.platform}")
    print(f"🔧 Python version: {sys.version}")
    print(f"📍 Current directory: {Path.cwd()}")
    
    # Test 1: Try subprocess with default event loop policy
    print("\n🧪 Test 1: Default event loop policy")
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-c", "print('Hello from subprocess')",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        print(f"✅ Success: {stdout.decode().strip()}")
        return True
    except NotImplementedError as e:
        print(f"❌ NotImplementedError: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

async def test_with_proactor_policy():
    """Test subprocess with Windows Proactor event loop policy"""
    print("\n🧪 Test 2: Windows Proactor event loop policy")
    
    # Set Windows Proactor policy
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("✅ Applied WindowsProactorEventLoopPolicy")
    
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-c", "print('Hello from subprocess with Proactor')",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        print(f"✅ Success: {stdout.decode().strip()}")
        return True
    except NotImplementedError as e:
        print(f"❌ NotImplementedError: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

async def main():
    """Main test function"""
    print("🔍 Testing asyncio subprocess creation on Windows")
    print("=" * 50)
    
    # Test with default policy
    default_works = await test_subprocess_creation()
    
    # If default doesn't work, try with Proactor policy
    if not default_works:
        proactor_works = await test_with_proactor_policy()
        if proactor_works:
            print("\n💡 Solution: Use WindowsProactorEventLoopPolicy for subprocess support")
        else:
            print("\n❌ Neither policy works - may be a deeper Windows/Python issue")
    else:
        print("\n✅ Default policy works fine")

if __name__ == "__main__":
    asyncio.run(main()) 