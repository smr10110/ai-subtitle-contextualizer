"""
Text processor for filtering and preparing OCR-captured text.
Determines if text is worth sending to AI for contextualization.
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.text_utils import clean_subtitle_text


class TextProcessor:
    """Processes and filters captured text before sending to AI."""
    
    def __init__(self, min_length: int = 1):
        """
        Initialize text processor.
        
        Args:
            min_length: Minimum characters to consider processing (very permissive)
        """
        self.min_length = min_length
    
    def should_process(self, text: str) -> bool:
        """Determine if text should be sent to AI - VERY permissive approach."""
        if not text:
            return False
        
        cleaned = text.strip()
        
        # Only reject if completely empty or too short
        if len(cleaned) < self.min_length:
            return False
        
        # Accept EVERYTHING else - let AI decide if it's useful
        return True
    
    def process_text(self, raw_text: str) -> Optional[str]:
        """
        Process raw text for AI consumption.
        
        Args:
            raw_text: Raw text from clipboard/OCR
            
        Returns:
            Processed text ready for AI, or None if should not process
        """
        if not self.should_process(raw_text):
            return None
        
        # Clean the text but keep it as complete as possible
        cleaned = clean_subtitle_text(raw_text)
        
        if not cleaned:
            return None
        
        print(f"📄 Processing text: '{cleaned[:50]}{'...' if len(cleaned) > 50 else ''}'")
        return cleaned