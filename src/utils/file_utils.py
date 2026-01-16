"""
File utilities for loading prompts and other text resources.
Functions to read prompts from markdown files for Llama AI.
"""

from pathlib import Path
from typing import Optional


def load_prompt(prompt_name: str) -> Optional[str]:
    """Load a prompt from the src/prompts/ directory."""
    # Get the prompts directory relative to this file
    current_dir = Path(__file__).parent
    prompts_dir = current_dir.parent / "prompts"
    prompt_file = prompts_dir / f"{prompt_name}.md"
    
    try:
        if prompt_file.exists():
            content = prompt_file.read_text(encoding='utf-8')
            return content.strip()
        else:
            print(f"⚠️  Prompt file not found: {prompt_file}")
            return None
    except Exception as e:
        print(f"❌ Error reading prompt {prompt_name}: {e}")
        return None


def format_prompt(prompt_template: str, **variables) -> str:
    """Format a prompt template with variables using Python string formatting."""
    try:
        # Replace placeholders like {subtitle_text} with actual values
        formatted = prompt_template.format(**variables)
        return formatted
    except KeyError as e:
        print(f"❌ Missing variable in prompt: {e}")
        return prompt_template
    except Exception as e:
        print(f"❌ Error formatting prompt: {e}")
        return prompt_template


def get_formatted_prompt(prompt_name: str, **variables) -> Optional[str]:
    """Load and format a prompt in one convenient function."""
    template = load_prompt(prompt_name)
    if template is None:
        return None
    
    return format_prompt(template, **variables)