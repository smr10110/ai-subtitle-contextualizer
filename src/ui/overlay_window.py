"""
Overlay window for displaying AI contextualizations.
Floating window that shows Llama responses in an elegant UI.
"""

import sys
import re
import queue
import tkinter.font as tkfont
from pathlib import Path
from typing import Optional, Callable, List, Tuple
import customtkinter as ctk

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_config


class OverlayWindow:
    """Floating overlay window for displaying AI responses."""
    
    def __init__(self):
        """Initialize the overlay window."""
        self.config = get_config()
        self.window: Optional[ctk.CTk] = None
        self.text_widget: Optional[ctk.CTkTextbox] = None
        self.is_visible = False
        
        # Thread-safe queue for updates from other threads
        self.update_queue: queue.Queue = queue.Queue()
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self._create_window()
    
    def _create_window(self) -> None:
        """Create the overlay window with all components."""
        self.window = ctk.CTk()
        self.window.title("AI Context")
        
        # Window properties
        self.window.geometry("450x350")
        self.window.attributes("-topmost", True)  # Always on top
        self.window.attributes("-alpha", self.config.overlay_opacity)
        
        # Handle window close button (X)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
        self.should_exit = False
        
        # Remove window decorations for cleaner look (optional)
        # self.window.overrideredirect(True)
        
        # Position in bottom-right corner
        self._position_window()
        
        # Create UI components
        self._create_ui()
        
        # Hide initially
        self.window.withdraw()
        
        print("🖼️  Overlay window created")
    
    def _position_window(self) -> None:
        """Position the window in the bottom-right corner of the screen."""
        self.window.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Window dimensions
        window_width = 450
        window_height = 350
        
        # Calculate position (bottom-right with some padding)
        padding = 20
        x = screen_width - window_width - padding
        y = screen_height - window_height - padding - 50  # Extra for taskbar
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _create_ui(self) -> None:
        """Create the UI components."""
        # Main frame with padding
        main_frame = ctk.CTkFrame(self.window, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header with title and close button
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🤖 AI Context",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(side="left")
        
        close_button = ctk.CTkButton(
            header_frame,
            text="✕",
            width=30,
            height=30,
            command=self.hide,
            fg_color="transparent",
            hover_color="#555555"
        )
        close_button.pack(side="right")
        
        # Text display area
        self.text_widget = ctk.CTkTextbox(
            main_frame,
            wrap="word",
            font=ctk.CTkFont(size=14),
            corner_radius=8
        )
        self.text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configure text tags for markdown rendering
        self._configure_text_tags()
        
        # Loading indicator (hidden by default)
        self.loading_label = ctk.CTkLabel(
            main_frame,
            text="⏳ Procesando...",
            font=ctk.CTkFont(size=14)
        )
        # Will be shown/hidden as needed
    
    def show(self) -> None:
        """Show the overlay window (thread-safe via queue)."""
        self.queue_update("show")
    
    def hide(self) -> None:
        """Hide the overlay window (thread-safe via queue)."""
        self.queue_update("hide")
    
    def toggle(self) -> None:
        """Toggle overlay visibility."""
        if self.is_visible:
            self.hide()
        else:
            self.show()
    
    def show_loading(self) -> None:
        """Show loading indicator (thread-safe via queue)."""
        self.queue_update("loading")
    
    def update_content(self, text: str) -> None:
        """Update the overlay with new content (thread-safe via queue)."""
        self.queue_update("content", text)
    
    def show_error(self, error_message: str) -> None:
        """Show an error message (thread-safe via queue)."""
        self.queue_update("error", error_message)
    
    def run(self) -> None:
        """Start the UI main loop (blocking)."""
        if self.window:
            print("🚀 Starting overlay UI...")
            self.window.mainloop()
    
    def update(self) -> None:
        """Process pending UI events (non-blocking)."""
        if self.window:
            # Process any queued updates from other threads
            self._process_queue()
            self.window.update()
    
    def _process_queue(self) -> None:
        """Process pending updates from the queue (thread-safe)."""
        try:
            while True:
                action, args = self.update_queue.get_nowait()
                if action == "content":
                    self._do_update_content(args)
                elif action == "loading":
                    self._do_show_loading()
                elif action == "error":
                    self._do_show_error(args)
                elif action == "show":
                    self._do_show()
                elif action == "hide":
                    self._do_hide()
        except queue.Empty:
            pass
    
    def _configure_text_tags(self) -> None:
        """Configure text tags for bold and italic rendering."""
        if not self.text_widget:
            return
        
        # Get the internal tkinter text widget
        tk_textbox = self.text_widget._textbox
        
        # Create font variants based on default font
        base_font = tkfont.Font(family="Segoe UI", size=11)
        bold_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        italic_font = tkfont.Font(family="Segoe UI", size=11, slant="italic")
        bold_italic_font = tkfont.Font(family="Segoe UI", size=11, weight="bold", slant="italic")
        
        # Configure tags with proper font objects
        tk_textbox.tag_configure("bold", font=bold_font)
        tk_textbox.tag_configure("italic", font=italic_font)
        tk_textbox.tag_configure("bold_italic", font=bold_italic_font)
    
    def _render_markdown(self, text: str) -> None:
        """Render text with markdown formatting (bold and italic)."""
        if not self.text_widget:
            return
        
        tk_textbox = self.text_widget._textbox
        
        # Pattern to find **bold**, *italic*, and ***bold italic***
        # Process in order: bold_italic first, then bold, then italic
        patterns = [
            (r'\*\*\*(.+?)\*\*\*', 'bold_italic'),  # ***text***
            (r'\*\*(.+?)\*\*', 'bold'),              # **text**
            (r'\*(.+?)\*', 'italic'),                # *text*
        ]
        
        # First, insert plain text
        self.text_widget.delete("1.0", "end")
        
        # Process text and collect formatting ranges
        processed_text = text
        format_ranges: List[Tuple[int, int, str]] = []
        
        for pattern, tag in patterns:
            offset = 0
            temp_text = processed_text
            processed_text = ""
            last_end = 0
            
            for match in re.finditer(pattern, temp_text):
                # Add text before match
                processed_text += temp_text[last_end:match.start()]
                # Calculate position in final text
                start_pos = len(processed_text)
                # Add matched content without markers
                content = match.group(1)
                processed_text += content
                end_pos = len(processed_text)
                # Record format range
                format_ranges.append((start_pos, end_pos, tag))
                last_end = match.end()
            
            processed_text += temp_text[last_end:]
        
        # Insert the processed text
        self.text_widget.insert("1.0", processed_text)
        
        # Apply formatting tags
        for start, end, tag in format_ranges:
            # Convert character positions to tkinter text indices
            start_idx = f"1.0+{start}c"
            end_idx = f"1.0+{end}c"
            tk_textbox.tag_add(tag, start_idx, end_idx)
    
    def _do_update_content(self, text: str) -> None:
        """Actually update content (called from main thread)."""
        if self.text_widget:
            self._render_markdown(text)
        self._do_show()
        print(f"📝 Overlay updated ({len(text)} chars)")
    
    def _do_show_loading(self) -> None:
        """Actually show loading (called from main thread)."""
        if self.text_widget:
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", "⏳ Procesando con Llama...\n\nAnalizando el texto capturado...")
        self._do_show()
    
    def _do_show_error(self, error_message: str) -> None:
        """Actually show error (called from main thread)."""
        if self.text_widget:
            self.text_widget.delete("1.0", "end")
            self.text_widget.insert("1.0", f"❌ Error\n\n{error_message}")
        self._do_show()
    
    def _do_show(self) -> None:
        """Actually show window (called from main thread)."""
        if self.window:
            self.window.deiconify()
            self.window.lift()
            self.is_visible = True
            print("👁️  Overlay shown")
    
    def _do_hide(self) -> None:
        """Actually hide window (called from main thread)."""
        if self.window:
            self.window.withdraw()
            self.is_visible = False
            print("🙈 Overlay hidden")
    
    def queue_update(self, action: str, args: str = "") -> None:
        """Queue an update to be processed in the main thread."""
        self.update_queue.put((action, args))
    
    def _on_close(self) -> None:
        """Handle window close button click."""
        print("🚪 Window closed by user")
        self.should_exit = True
    
    def destroy(self) -> None:
        """Destroy the overlay window."""
        if self.window:
            self.window.destroy()
            self.window = None
            print("🗑️  Overlay destroyed")