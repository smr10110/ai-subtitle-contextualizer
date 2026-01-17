"""
Llama client for AI text contextualization using Ollama.
Sends text to local Llama model and receives explanations.
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_config

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  Ollama library not installed. Run: pip install ollama")


class LlamaClient:
    """Client for interacting with local Llama model via Ollama."""
    
    def __init__(self):
        """Initialize Llama client with configuration."""
        self.config = get_config()
        self.model = self.config.llama_model
        self.host = self.config.llama_host
        self.is_available = OLLAMA_AVAILABLE
        
        if self.is_available:
            # Configure ollama client with custom host if needed
            if self.host != "http://localhost:11434":
                ollama.Client(host=self.host)
            print(f"🤖 Llama client initialized with model: {self.model}")
    
    def get_context(self, text: str, system_prompt: str) -> Optional[str]:
        """
        Send text to Llama and get contextual explanation.
        
        Args:
            text: The captured text to analyze
            system_prompt: Instructions for the AI
            
        Returns:
            AI response with context/explanation, or None if failed
        """
        if not self.is_available:
            print("❌ Ollama library not available")
            return None
        
        if not text or not text.strip():
            return None
        
        try:
            print(f"🧠 Sending to Llama: '{text[:40]}{'...' if len(text) > 40 else ''}'")
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ]
            )
            
            # Extract the response content
            result = response["message"]["content"]
            print(f"✅ Llama response received ({len(result)} chars)")
            return result
            
        except Exception as e:
            print(f"❌ Llama error: {e}")
            return None
    
    def check_connection(self) -> bool:
        """
        Verify that Ollama is running and the model is available.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.is_available:
            print("❌ Ollama library not installed")
            return False
        
        try:
            # Try to list models to verify connection
            models = ollama.list()
            model_list = models.get("models", [])
            model_names = [m.get("name", "") if isinstance(m, dict) else str(m) for m in model_list]
            
            print(f"📡 Connected to Ollama at {self.host}")
            print(f"📋 Available models: {', '.join(model_names) if model_names else 'none'}")
            
            # Check if our model is available
            model_available = any(self.model in name for name in model_names)
            
            if model_available:
                print(f"✅ Model '{self.model}' is available")
                return True
            else:
                print(f"❌ Model '{self.model}' not found!")
                print(f"   Run: ollama pull {self.model}")
                return False
                
        except Exception as e:
            print(f"❌ Cannot connect to Ollama: {e}")
            print(f"   Make sure Ollama is running: ollama serve")
            return False