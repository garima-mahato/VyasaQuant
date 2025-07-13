# modules/model_manager.py - AI Model Management for Stock Stability Analysis

import os
import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any, Union

# Google GenAI imports
try:
    from google import genai
    from google.genai import types
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False

# Ollama imports
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

class ModelManager:
    """Manages AI models for stock stability analysis - supports Google GenAI and Ollama"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.google_client = None
        self.ollama_client = None
        self.current_provider = None
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize AI models based on configuration"""
        provider = self.config.get("provider", "google")
        
        print(f"🔧 Initializing AI models with provider: {provider}")
        
        # Initialize Google GenAI
        if provider == "google" or self.config.get("fallback", {}).get("enable_fallback", False):
            self._initialize_google_genai()
        
        # Initialize Ollama
        if provider == "ollama" or self.config.get("fallback", {}).get("enable_fallback", False):
            self._initialize_ollama()
        
        # Set current provider
        self.current_provider = provider
        
        # Check if primary provider is available
        if not self.is_provider_available(provider):
            fallback_provider = self.config.get("fallback", {}).get("provider")
            if fallback_provider and self.is_provider_available(fallback_provider):
                print(f"⚠️ Primary provider '{provider}' unavailable, switching to fallback: {fallback_provider}")
                self.current_provider = fallback_provider
            else:
                print(f"❌ No available AI providers. Please check your configuration.")
    
    def _initialize_google_genai(self):
        """Initialize Google GenAI using official SDK"""
        try:
            if not GOOGLE_GENAI_AVAILABLE:
                print("❌ google-genai package not available")
                print("💡 Run: pip install google-genai")
                return
            
            google_config = self.config.get("google", {})
            api_key_env_var = google_config.get("api_key_env_var", "GOOGLE_API_KEY")
            api_key = os.getenv(api_key_env_var)
            
            print(f"🔍 Debug: {api_key_env_var} found: {'Yes' if api_key else 'No'}")
            
            if api_key:
                #print(f"🔍 Debug: API Key length: {len(api_key)} characters")
                #print(f"🔍 Debug: API Key starts with: {api_key[:10]}...")
                
                # Create Google GenAI client using official SDK
                self.google_client = genai.Client(api_key=api_key)
                print("✅ Google GenAI client initialized successfully")
                
                # Test the client
                try:
                    # List available models to verify connection
                    models = list(self.google_client.models.list())
                    print(f"✅ Google GenAI connection verified - {len(models)} models available")
                except Exception as e:
                    print(f"⚠️ Google GenAI client created but connection test failed: {e}")
                
            else:
                print(f"❌ {api_key_env_var} not found in environment variables")
                print("💡 Available environment variables starting with 'GOOGLE':")
                google_vars = [var for var in os.environ.keys() if var.startswith('GOOGLE')]
                if google_vars:
                    for var in google_vars:
                        print(f"   - {var}")
                else:
                    print("   - None found")
                
        except Exception as e:
            print(f"❌ Failed to initialize Google GenAI: {e}")
            print(f"🔍 Debug: Exception type: {type(e)}")
    
    def _initialize_ollama(self):
        """Initialize Ollama client"""
        try:
            if not OLLAMA_AVAILABLE:
                print("❌ ollama package not available")
                print("💡 Run: pip install ollama")
                return
            
            ollama_config = self.config.get("ollama", {})
            base_url = ollama_config.get("base_url", "http://localhost:11434")
            
            # Create Ollama client
            self.ollama_client = ollama.Client(host=base_url)
            
            # Test connection
            try:
                models = self.ollama_client.list()
                print(f"✅ Ollama client initialized successfully - {len(models.get('models', []))} models available")
                
                # Check if configured model is available
                configured_model = ollama_config.get("model", "gemma3:1b")
                available_models = [m.get('model', '') for m in models.get('models', []) if m.get('model', '').strip()]
                #print(models.get('models', []))
                
                if configured_model in available_models:
                    print(f"✅ Configured model '{configured_model}' is available")
                else:
                    print(f"⚠️ Configured model '{configured_model}' not found")
                    if available_models:
                        print(f"💡 Available models: {available_models}")
                        print(f"💡 Consider updating config to use: {available_models[0]}")
                    else:
                        print("💡 No models available in Ollama - run: ollama pull gemma3:1b")
                
            except Exception as e:
                print(f"⚠️ Ollama client created but connection test failed: {e}")
                print("💡 Make sure Ollama is running: ollama serve")
                
        except Exception as e:
            print(f"❌ Failed to initialize Ollama: {e}")
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available"""
        if provider == "google":
            return self.google_client is not None
        elif provider == "ollama":
            return self.ollama_client is not None
        return False
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text using the configured AI provider"""
        if self.current_provider == "google":
            return await self._generate_with_google(prompt)
        elif self.current_provider == "ollama":
            return await self._generate_with_ollama(prompt)
        else:
            return "ERROR: No available AI provider"
    
    async def _generate_with_google(self, prompt: str) -> str:
        """Generate text using Google GenAI"""
        if not self.google_client:
            return "ERROR: Google GenAI client not available"
        
        try:
            google_config = self.config.get("google", {})
            model_name = google_config.get("model", "gemini-2.0-flash-001")
            
            # Use the official Google GenAI SDK API
            response = self.google_client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=google_config.get("temperature", 0.1),
                    max_output_tokens=google_config.get("max_tokens", 4000),
                ),
            )
            
            return response.text.strip() if response.text else "No response generated"
            
        except Exception as e:
            error_msg = f"ERROR: Google GenAI generation failed: {str(e)}"
            print(error_msg)
            
            # Try fallback if enabled
            if self.config.get("fallback", {}).get("enable_fallback", False):
                fallback_provider = self.config.get("fallback", {}).get("provider")
                if fallback_provider == "ollama" and self.ollama_client:
                    print("🔄 Falling back to Ollama...")
                    return await self._generate_with_ollama(prompt)
            
            return error_msg
    
    async def _generate_with_ollama(self, prompt: str) -> str:
        """Generate text using Ollama"""
        if not self.ollama_client:
            return "ERROR: Ollama client not available"
        
        try:
            ollama_config = self.config.get("ollama", {})
            model_name = ollama_config.get("model", "gemma3:1b")
            
            # Use Ollama generate API
            response = self.ollama_client.generate(
                model=model_name,
                prompt=prompt,
                options={
                    "temperature": ollama_config.get("temperature", 0.1),
                    "num_predict": ollama_config.get("max_tokens", 4000),
                },
            )
            
            return response.get("response", "No response generated").strip()
            
        except Exception as e:
            error_msg = f"ERROR: Ollama generation failed: {str(e)}"
            print(error_msg)
            
            # Try fallback if enabled
            if self.config.get("fallback", {}).get("enable_fallback", False):
                fallback_provider = self.config.get("fallback", {}).get("provider")
                if fallback_provider == "google" and self.google_client:
                    print("🔄 Falling back to Google GenAI...")
                    return await self._generate_with_google(prompt)
            
            return error_msg
    
    def is_available(self) -> bool:
        """Check if any AI model is available"""
        return self.is_provider_available(self.current_provider)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model configuration"""
        provider_config = self.config.get(self.current_provider, {})
        return {
            "provider": self.current_provider,
            "model": provider_config.get("model", "unknown"),
            "available": self.is_available(),
            "fallback_enabled": self.config.get("fallback", {}).get("enable_fallback", False),
        } 