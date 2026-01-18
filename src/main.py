"""
AI Subtitle Contextualizer - Main Entry Point
Orchestrates clipboard monitoring, AI processing, and UI display.
"""

import sys
import time
from pathlib import Path

# Bloque 1: Añadir rutas al path
# Esto permite importar módulos desde cualquier ubicación
sys.path.insert(0, str(Path(__file__).parent))

# Bloque 2: Importar componentes del sistema
# Cada import trae un módulo que ya creamos en capas anteriores
from config import get_config, validate_config
from clipboard.monitor import ClipboardMonitor
from ai.llama_client import LlamaClient
from ai.prompt_manager import PromptManager
from ui.overlay_window import OverlayWindow


class AISubtitleContextualizer:
    """Main application class that orchestrates all components."""
    
    def __init__(self):
        """Initialize the application with all components."""
        print("🚀 AI Subtitle Contextualizer starting...")
        
        # Validate configuration first
        if not validate_config():
            print("⚠️  Configuration has warnings (using defaults)")
        
        # Load configuration
        self.config = get_config()
        
        # Initialize components
        self.overlay = OverlayWindow()
        self.llama_client = LlamaClient()
        self.prompt_manager = PromptManager()
        self.clipboard_monitor = ClipboardMonitor(
            callback=self._on_text_detected
        )
        
        # Processing state
        self.is_processing = False
        
        print("✅ All components initialized!")
    
    def _on_text_detected(self, text: str) -> None:
        """Callback when new text is detected in clipboard."""
        # Avoid processing if already processing
        if self.is_processing:
            print("⏳ Already processing, skipping...")
            return
        
        self._process_text(text)
    
    def _process_text(self, text: str) -> None:
        """Process text through AI and display result."""
        self.is_processing = True
        
        try:
            # Show loading state
            self.overlay.show_loading()
            
            # Get formatted prompt with the text inserted
            formatted_prompt = self.prompt_manager.get_prompt_for_text(text)
            
            # Get AI response (use formatted prompt as system, text as user message)
            response = self.llama_client.get_context(text, formatted_prompt)
            
            # Display the result
            self.overlay.update_content(response)
            
        except Exception as e:
            print(f"❌ Error processing: {e}")
            self.overlay.show_error(str(e))
        
        finally:
            self.is_processing = False
    
    def run(self) -> None:
        """Start the application main loop."""
        print("\n" + "="*50)
        print("🎬 AI Subtitle Contextualizer Ready!")
        print("="*50)
        print("📋 Copy any text to get AI context")
        print("🖼️  Results appear in the overlay window")
        print("❌ Close the overlay or press Ctrl+C to exit")
        print("="*50 + "\n")
        
        try:
            # Start clipboard monitoring
            self.clipboard_monitor.start()
            
            # Main UI loop
            while not self.overlay.should_exit:
                self.overlay.update()
                time.sleep(0.05)  # 50ms = 20 FPS
            
            print("\n⏹️  Window closed, shutting down...")
                
        except KeyboardInterrupt:
            print("\n⏹️  Shutting down...")
        
        finally:
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up all resources."""
        print("🧹 Cleaning up...")
        self.clipboard_monitor.stop()
        self.overlay.destroy()
        print("👋 Goodbye!")


def main():
    """Entry point for the application."""
    app = AISubtitleContextualizer()
    app.run()


if __name__ == "__main__":
    main()
