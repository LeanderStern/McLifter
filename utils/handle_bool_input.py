import os
import sys

from pydantic import TypeAdapter, validate_call


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


def _gui_bool_input(input_string: str) -> bool:
    """Show a GUI dialog for boolean input using tkinter"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.lift()      # Bring to front
        root.attributes('-topmost', True)  # Keep on top
        
        # Show yes/no dialog
        result = messagebox.askyesno("Input Required", input_string)
        
        # Clean up
        root.destroy()
        
        return result
    except ImportError:
        # tkinter not available, default to True
        print("Warning: GUI not available, defaulting to 'yes'")
        return True
    except Exception as e:
        # Any other error, default to True
        print(f"Warning: GUI error ({e}), defaulting to 'yes'")
        return True


@validate_call
def handle_bool_input(input_string: str) -> bool:
    # Check if we're running in a windowed mode (PyInstaller -w) where stdin is not available
    if not _is_stdin_available():
        return _gui_bool_input(input_string)
    
    # Original console-based implementation
    while True:
        print(input_string)
        try:
            return TypeAdapter(bool).validate_python(input("[yes/no]"))
        except ValueError:
            os.system("cls")
            print("Please enter yes/no")