"""
AI client for text contextualization using Groq.
Sends text to Groq API and receives explanations.
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_config

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  Groq library not installed. Run: pip install groq")


class LlamaClient:
    """Client for interacting with AI models via Groq API."""
    
    def __init__(self):
        """Initialize Groq client with configuration."""
        self.config = get_config()
        self.model = "llama-3.3-70b-versatile"  # Current model
        
        # Try to get API key from environment
        import os
        self.api_key = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
        self.is_available = GROQ_AVAILABLE
        
        if self.is_available and self.api_key != "your-groq-api-key-here":
            try:
                self.client = Groq(api_key=self.api_key)
                print(f"🤖 Groq client initialized with model: {self.model}")
            except Exception as e:
                print(f"❌ Error initializing Groq: {e}")
                self.client = None
        else:
            self.client = None
            if not self.is_available:
                print("❌ Groq library not available")
            else:
                print("⚠️  Using demo mode - set GROQ_API_KEY for full functionality")
    
    def get_context(self, text: str, system_prompt: str) -> Optional[str]:
        """
        Send text to Groq and get contextual explanation.
        
        Args:
            text: The captured text to analyze
            system_prompt: Instructions for the AI
            
        Returns:
            AI response with context/explanation, or None if failed
        """
        # Demo mode - just return a formatted response
        if not self.client:
            return f"""📝 DEMO MODE - Get your free Groq API key at https://console.groq.com

🎯 TEXT ANALYZED: "{text[:100]}{'...' if len(text) > 100 else ''}"

💡 This would be contextualized by Groq's ultra-fast AI!

To enable real AI responses:
1. Get free API key from: https://console.groq.com
2. Create .env file with: GROQ_API_KEY=your-key-here
3. Restart the application

Groq is 10x faster than other AI providers! ⚡"""
        
        try:
            print(f"🧠 Sending to Groq: '{text[:40]}{'...' if len(text) > 40 else ''}'")
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                model=self.model,
                temperature=0.3,  # More focused responses
                max_tokens=1000
            )
            
            # Extract the response content
            result = chat_completion.choices[0].message.content
            print(f"✅ Groq response received ({len(result)} chars)")
            return result
            
        except Exception as e:
            print(f"❌ Groq error: {e}")
            return f"Error: {e}"