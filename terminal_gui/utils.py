from __future__ import annotations

import urwid
import toml
import logging
import os
from pathlib import Path
from .config import load_config, get_menu_colors

def setup_logger():
    """Set up logging to file only"""
    try:
        # Create logs directory if it doesn't exist
        log_dir = os.path.expanduser('~/.terminal_gui/logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'terminal_gui.log')
        
        # Configure logging
        logger = logging.getLogger('terminal_gui')
        logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # File handler only - no console output
        fh = logging.FileHandler(log_file, mode='w')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        logger.debug('Logger initialized - file only mode')
        return logger
        
    except Exception as e:
        print(f"Error setting up logger: {str(e)}")
        return None

# Create logger instance
logger = setup_logger()

def debug_log(message: str):
    """Helper function to log debug messages to file only"""
    if logger:
        try:
            logger.debug(message)
        except Exception as e:
            # Silently fail to avoid console output
            pass

def exit_program(button=None):
    raise urwid.ExitMainLoop()

def create_palette(colors):
    return [
        (None, colors.get('default_fg', 'black'), colors.get('default_bg', 'light gray')),
        ("heading", colors.get('heading_fg', 'black'), colors.get('heading_bg', 'light gray')),
        ("line", colors.get('line_fg', 'black'), colors.get('line_bg', 'light gray')),
        ("options", colors.get('options_fg', 'black'), colors.get('options_bg', 'light gray')),
        ("focus heading", colors.get('focus_heading_fg', 'white'), colors.get('focus_heading_bg', 'dark blue')),
        ("focus line", colors.get('focus_line_fg', 'white'), colors.get('focus_line_bg', 'dark blue')),
        ("focus options", colors.get('focus_options_fg', 'white'), colors.get('focus_options_bg', 'dark blue')),
        ("selected", colors.get('selected_fg', 'white'), colors.get('selected_bg', 'dark blue')),
    ]

def load_menu_config(file_path):
    with open(file_path, 'r') as file:
        return toml.load(file)