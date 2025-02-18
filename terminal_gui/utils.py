from __future__ import annotations

import urwid
import toml
import logging
import os
from pathlib import Path
from .config import load_config, get_menu_colors

def setup_logger():
    """Set up logging to both file and console"""
    # Create logs directory if it doesn't exist
    log_dir = Path.home() / '.terminal_gui' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / 'terminal_gui.log'
    
    # Configure logging
    logger = logging.getLogger('terminal_gui')
    logger.setLevel(logging.DEBUG)
    
    # File handler - debug level
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)
    
    return logger

# Create logger instance
logger = setup_logger()

def debug_log(message: str):
    """Helper function to log debug messages"""
    logger.debug(message)

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