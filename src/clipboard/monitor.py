"""
Clipboard monitor for detecting new subtitle text.
Watches for changes and triggers processing.
"""

import time
import threading
import pyperclip
from typing import Optional, Callable


class ClipboardMonitor:
    """Monitors clipboard for new text content."""
    
    def __init__(self, callback: Callable[[str], None], check_interval: float = 0.5):
        """
        Initialize clipboard monitor.
        
        Args:
            callback: Function to call when new text is detected
            check_interval: How often to check clipboard (seconds)
        """
        self.callback = callback
        self.check_interval = check_interval
        self.last_text = ""
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start monitoring clipboard in background thread."""
        if self.running:
            print("⚠️  Clipboard monitor already running")
            return
        
        print("🔍 Starting clipboard monitor...")
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Clipboard monitor started")
    
    def stop(self) -> None:
        """Stop monitoring clipboard."""
        if not self.running:
            return
        
        print("🛑 Stopping clipboard monitor...")
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        print("✅ Clipboard monitor stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop - runs in background thread."""
        print("🔄 Clipboard monitoring loop started")
        
        # Initialize with current clipboard content
        try:
            self.last_text = pyperclip.paste() or ""
        except Exception:
            self.last_text = ""
        
        while self.running:
            try:
                # Get current clipboard content
                current_text = pyperclip.paste() or ""
                
                # Check if content has changed
                if current_text != self.last_text and current_text.strip():
                    print(f"📋 New clipboard content detected ({len(current_text)} chars)")
                    self.last_text = current_text
                    
                    # Call the callback with new text
                    try:
                        self.callback(current_text)
                    except Exception as e:
                        print(f"❌ Error in callback: {e}")
                
                # Wait before next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"⚠️  Clipboard access error: {e}")
                time.sleep(1.0)  # Wait longer on error
        
        print("🔄 Clipboard monitoring loop ended")