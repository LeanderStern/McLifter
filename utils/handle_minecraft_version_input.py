import os
import sys

from pydantic import validate_call
from semantic_version import Version, validate


def _is_stdin_available() -> bool:
    """Check if stdin is available for input (not running in PyInstaller -w mode)"""
    try:
        # Check if stdin exists and is readable
        if sys.stdin is None:
            return False
        
        # Try to get the file descriptor - fails in PyInstaller -w
        sys.stdin.fileno()
        
        # Check if it's actually readable
        if not hasattr(sys.stdin, 'readable') or not sys.stdin.readable():
            return False
            
        return True
    except (OSError, RuntimeError, AttributeError):
        return False


def _gui_version_input(input_string: str) -> str:
    """Show a GUI dialog for version input using tkinter"""
    try:
        import tkinter as tk
        from tkinter import simpledialog
        
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.lift()      # Bring to front
        root.attributes('-topmost', True)  # Keep on top
        
        while True:
            # Show input dialog
            version = simpledialog.askstring("Input Required", input_string)
            
            # Handle cancel/escape
            if version is None:
                root.destroy()
                raise ValueError("Input cancelled by user")
            
            # Validate the version
            if validate(version):
                root.destroy()
                return version
            
            # Show error for invalid version
            from tkinter import messagebox
            messagebox.showerror("Invalid Version", "Please enter a valid Minecraft version")
        
    except ImportError:
        # tkinter not available, return a default version
        print("Warning: GUI not available, defaulting to '1.21.0'")
        return "1.21.0"
    except Exception as e:
        # Any other error, return a default version
        print(f"Warning: GUI error ({e}), defaulting to '1.21.0'")
        return "1.21.0"


@validate_call
def handle_minecraft_version_input(input_string: str) -> str:
    # Check if we're running in a windowed mode (PyInstaller -w) where stdin is not available
    if not _is_stdin_available():
        return _gui_version_input(input_string)
    
    # Original console-based implementation
    while True:
        version = input(input_string)
        if validate(version):
            return version
        os.system("cls")
        print("please enter valid minecraft version")