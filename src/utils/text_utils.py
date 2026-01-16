"""
Text processing utilities for subtitle analysis.
Functions to clean, filter and validate subtitle text.
"""

import re
from typing import Optional


def clean_subtitle_text(raw_text: str) -> str:
    """Clean and normalize subtitle text from OCR output."""
    if not raw_text:
        return ""
    
    # Remove extra whitespace and normalize line breaks
    cleaned = re.sub(r'\s+', ' ', raw_text.strip())
    
    # Remove common OCR artifacts
    cleaned = re.sub(r'[^\w\s\.,\!\?\:\;\-\'""]', '', cleaned)
    
    return cleaned


def is_likely_subtitle(text: str, min_length: int = 3, max_length: int = 200) -> bool:
    """Check if text looks like a subtitle based on common patterns."""
    if not text or len(text.strip()) < min_length:
        return False
    
    if len(text) > max_length:
        return False
    
    # Check for subtitle-like patterns
    has_words = bool(re.search(r'\w+', text))
    has_reasonable_length = min_length <= len(text.strip()) <= max_length
    
    # Avoid processing system messages or UI elements
    system_patterns = [
        r'^(Error|Warning|Loading|Save|Open|File|Edit)$',
        r'^\d{2}:\d{2}:\d{2}$',  # Timestamps
        r'^[A-Z_]{3,}$',         # ALL_CAPS_CONSTANTS
    ]
    
    is_system_text = any(re.search(pattern, text.strip()) for pattern in system_patterns)
    
    return has_words and has_reasonable_length and not is_system_text