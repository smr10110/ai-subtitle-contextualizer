"""
Prompt manager for loading and managing AI prompts.
Handles loading prompts from external files and formatting them.
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.file_utils import load_prompt, get_formatted_prompt


class PromptManager:
    """Manages prompts for AI contextualization."""
    
    def __init__(self, prompt_name: str = "subtitle_explainer"):
        """
        Initialize prompt manager.
        
        Args:
            prompt_name: Name of prompt file to load (without .md extension)
        """
        self.prompt_name = prompt_name
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from file or use default."""
        prompt = load_prompt(self.prompt_name)
        
        if prompt:
            print(f"📝 Loaded prompt from: {self.prompt_name}.md")
            return prompt
        else:
            raise FileNotFoundError(
                f"⚠️  Prompt file not found: {self.prompt_name}.md\n"
                f"   Create src/prompts/{self.prompt_name}.md file"
            )
    
    def get_prompt_for_text(self, text: str) -> str:
        """
        Get formatted prompt ready to send to AI.
        
        Args:
            text: The captured text to analyze
            
        Returns:
            Formatted system prompt with text inserted
        """
        # Try to format with {subtitle_text} or {text} placeholder
        try:
            if "{subtitle_text}" in self.system_prompt:
                return self.system_prompt.format(subtitle_text=text)
            elif "{text}" in self.system_prompt:
                return self.system_prompt.format(text=text)
            else:
                # No placeholder, append text at the end
                return f"{self.system_prompt}\n\nText to analyze: {text}"
        except KeyError as e:
            print(f"⚠️  Prompt formatting error: {e}")
            return f"{self.system_prompt}\n\nText to analyze: {text}"
    
    def reload_prompt(self) -> None:
        """Reload prompt from file (useful for hot-reloading)."""
        self.system_prompt = self._load_system_prompt()
        print("🔄 Prompt reloaded")

    def get_image_prompt(self) -> str:
        """
        Get prompt for image/vision analysis.
        
        Returns:
            Prompt for vision model to analyze screenshot
        """
        # Load from file
        image_prompt = load_prompt("subtitle_image_explainer")
        
        if image_prompt:
            print(f"📝 Loaded image prompt from: subtitle_image_explainer.md")
            return image_prompt
        else:
            raise FileNotFoundError(
                f"⚠️  Image prompt file not found: subtitle_image_explainer.md\n"
                f"   Create src/prompts/subtitle_image_explainer.md file"
            )