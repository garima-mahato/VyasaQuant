#!/usr/bin/env python3
"""
Debug script to test AI model configurations (Google GenAI and Ollama)
"""

import os
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv loaded successfully")
except ImportError:
    print("❌ python-dotenv not available")

def test_environment_variables():
    """Test environment variable loading"""
    print("\n🔍 Environment Variable Debug:")
    print("-" * 40)
    
    # Check Google API Key
    google_key = os.getenv('GOOGLE_API_KEY')
    if google_key:
        print(f"✅ GOOGLE_API_KEY found: {len(google_key)} characters")
        #print(f"   Starts with: {google_key[:10]}...")
    else:
        print("❌ GOOGLE_API_KEY not found")
        print("💡 Available environment variables starting with 'GOOGLE':")
        google_vars = [var for var in os.environ.keys() if var.startswith('GOOGLE')]
        if google_vars:
            for var in google_vars:
                print(f"   - {var}")
        else:
            print("   - None found")
    
    return google_key is not None

def test_google_genai():
    """Test Google GenAI import and configuration"""
    print("\n🔍 Google GenAI Test:")
    print("-" * 40)
    
    try:
        from google import genai
        from google.genai import types
        print("✅ google.genai imported successfully")
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            try:
                # Use official Google GenAI SDK API
                client = genai.Client(api_key=api_key)
                print("✅ Google GenAI client created successfully")
                
                # Test generation
                response = client.models.generate_content(
                    model="gemini-2.0-flash-001",
                    contents="Hello, respond with just 'API working'",
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=100,
                    ),
                )
                
                print(f"✅ Test generation successful: {response.text.strip()}")
                return True
                
            except Exception as e:
                print(f"⚠️ Google GenAI test failed: {e}")
                return False
        else:
            print("❌ Cannot test - no API key")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try: pip install google-genai")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_ollama():
    """Test Ollama connection and configuration"""
    print("\n🔍 Ollama Test:")
    print("-" * 40)
    
    try:
        import ollama
        print("✅ ollama imported successfully")
        
        # Create client
        client = ollama.Client(host="http://localhost:11434")
        
        # Test connection
        try:
            models = client.list()
            available_models = [m.get('name', '') for m in models.get('models', [])]
            print(f"✅ Ollama connection successful - {len(available_models)} models available")
            
            if available_models:
                print(f"📋 Available models: {available_models}")
                
                # Test generation with first available model
                test_model = available_models[0]
                print(f"🧪 Testing generation with: {test_model}")
                
                response = client.generate(
                    model=test_model,
                    prompt="Hello, respond with just 'Ollama working'",
                    options={"temperature": 0.1, "num_predict": 50}
                )
                
                print(f"✅ Test generation successful: {response.get('response', '').strip()}")
                return True
            else:
                print("⚠️ No models available in Ollama")
                print("💡 Run: ollama pull gemma3:1b")
                return False
                
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            print("💡 Make sure Ollama is running: ollama serve")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try: pip install ollama")
        return False

def test_config_loader():
    """Test the centralized configuration loader"""
    print("\n🔍 Configuration Loader Test:")
    print("-" * 40)
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.append(str(project_root))
        
        from config.config_loader import get_stability_checker_config
        config = get_stability_checker_config()
        
        print("✅ Configuration loaded successfully")
        print(f"   Agent: {config['agent']['name']}")
        print(f"   Servers: {list(config['servers'].keys())}")
        
        # Test AI model configuration
        ai_config = config.get('ai_model', {})
        print(f"   AI Provider: {ai_config.get('provider', 'not set')}")
        
        if ai_config.get('provider') == 'google':
            google_config = ai_config.get('google', {})
            print(f"   Google Model: {google_config.get('model', 'not set')}")
        
        if ai_config.get('provider') == 'ollama':
            ollama_config = ai_config.get('ollama', {})
            print(f"   Ollama Model: {ollama_config.get('model', 'not set')}")
            print(f"   Ollama URL: {ollama_config.get('base_url', 'not set')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_model_manager():
    """Test the ModelManager with current configuration"""
    print("\n🔍 ModelManager Test:")
    print("-" * 40)
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.append(str(project_root))
        sys.path.append(str(project_root / "agents" / "stability_checker_agent"))
        
        from config.config_loader import get_stability_checker_config
        from modules.model_manager import ModelManager
        
        config = get_stability_checker_config()
        ai_config = config.get('ai_model', {})
        
        # Test ModelManager initialization
        model_manager = ModelManager(ai_config)
        print(f"✅ ModelManager initialized")
        
        # Get model info
        model_info = model_manager.get_model_info()
        print(f"   Provider: {model_info['provider']}")
        print(f"   Model: {model_info['model']}")
        print(f"   Available: {model_info['available']}")
        print(f"   Fallback Enabled: {model_info['fallback_enabled']}")
        
        return model_info['available']
        
    except Exception as e:
        print(f"❌ ModelManager test failed: {e}")
        return False

def provide_solutions():
    """Provide solutions for common issues"""
    print("\n💡 Solutions for Common Issues:")
    print("=" * 50)
    
    print("\n1. Setting Google API Key:")
    print("   PowerShell:")
    print("   $env:GOOGLE_API_KEY = 'your_api_key_here'")
    print("   setx GOOGLE_API_KEY 'your_api_key_here'  # Permanent")
    
    print("\n   .env file (in project root):")
    print("   GOOGLE_API_KEY=your_api_key_here")
    
    print("\n2. Installing dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n3. Setting up Ollama:")
    print("   Download from: https://ollama.ai")
    print("   ollama serve                    # Start server")
    print("   ollama pull gemma3:1b        # Download model")
    
    print("\n4. Configuring AI Provider:")
    print("   Edit config/agents.yaml:")
    print("   ai_model:")
    print("     provider: 'google' or 'ollama'")

def main():
    """Main test function"""
    print("🧪 VyasaQuant AI Model Configuration Debug")
    print("=" * 60)
    
    results = []
    
    # Test environment variables
    env_ok = test_environment_variables()
    results.append(("Environment Variables", env_ok))
    
    # Test Google GenAI
    genai_ok = test_google_genai()
    results.append(("Google GenAI", genai_ok))
    
    # Test Ollama
    ollama_ok = test_ollama()
    results.append(("Ollama", ollama_ok))
    
    # Test configuration
    config_ok = test_config_loader()
    results.append(("Configuration Loader", config_ok))
    
    # Test ModelManager
    model_manager_ok = test_model_manager()
    results.append(("ModelManager", model_manager_ok))
    
    # Summary
    print("\n📋 Test Summary:")
    print("-" * 40)
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    any_ai_available = genai_ok or ollama_ok
    
    if any_ai_available and config_ok:
        print("\n🎉 At least one AI provider is working! Your setup is ready.")
        print("   You can now run: python agents/stability_checker_agent/agent.py")
    else:
        print("\n⚠️  Some tests failed. See solutions below:")
        provide_solutions()

if __name__ == "__main__":
    main() 