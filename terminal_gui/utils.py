from __future__ import annotations

import urwid
import toml
from .config import load_config, get_menu_colors

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