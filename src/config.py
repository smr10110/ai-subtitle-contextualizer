"""
Configuration manager for AI Subtitle Contextualizer.
Handles environment variables and application settings.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Application configuration loaded from environment variables."""
    
    def __init__(self) -> None:
        """Initialize configuration by loading environment variables."""
        self._load_environment()
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file if it exists."""
        # Try to find .env file in project root
        project_root = Path(__file__).parent.parent
        env_file = project_root / ".env"
        
        if env_file.exists():
            load_dotenv(env_file)
            print(f"✅ Loaded environment from: {env_file}")
        else:
            print(f"⚠️  No .env file found, using defaults")
            print("   You can create .env to customize settings")
    
    @property
    def llama_model(self) -> str:
        """Get Llama model name with fallback to default."""
        return os.getenv("LLAMA_MODEL", "llama3.2")
    
    @property
    def llama_host(self) -> str:
        """Get Llama host URL (for Ollama server)."""
        return os.getenv("LLAMA_HOST", "http://localhost:11434")
    
    @property
    def overlay_opacity(self) -> float:
        """Get overlay window opacity (0.0 to 1.0)."""
        opacity_str = os.getenv("OVERLAY_OPACITY", "0.9")
        return float(opacity_str)
    
    @property
    def auto_process(self) -> bool:
        """Check if automatic processing is enabled."""
        auto_str = os.getenv("AUTO_PROCESS", "true")
        return auto_str.lower() in ("true", "1", "yes")

    def validate(self) -> bool:
        """Validate configuration and show helpful error messages."""
        is_valid = True
        
        # Check if Ollama server is accessible (basic validation)
        print(f"📡 Will connect to Llama at: {self.llama_host}")
        print(f"🤖 Using model: {self.llama_model}")
        
        # Validate opacity range
        try:
            if not (0.0 <= self.overlay_opacity <= 1.0):
                print(f"❌ OVERLAY_OPACITY must be between 0.0 and 1.0, got: {self.overlay_opacity}")
                is_valid = False
        except ValueError as e:
            print(f"❌ Invalid OVERLAY_OPACITY value: {e}")
            is_valid = False
        
        return is_valid


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance (singleton pattern)."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def validate_config() -> bool:
    """Validate global configuration and exit if invalid."""
    config = get_config()
    if not config.validate():
        print("\n💡 To fix this:")
        print("   1. Install Ollama: https://ollama.ai/")
        print("   2. Run: ollama pull llama3.2")
        print("   3. Start: ollama serve")
        print("   4. Restart the application")
        return False
    return True