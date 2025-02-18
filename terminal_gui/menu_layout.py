from __future__ import annotations

import urwid
from .utils import exit_program, debug_log

focus_map = {None: 'selected', 'options': 'selected'}

class MenuOverlay(urwid.Overlay):
    def __init__(self, top_w, bottom_w, align, width, valign, height, min_width, min_height):
        super().__init__(top_w, bottom_w, align, width, valign, height, min_width, min_height)
        self.last_size = None
    
    def render(self, size, focus=False):
        self.last_size = size
        return super().render(size, focus)
    
    def mouse_event(self, size, event, button, col, row, focus):
        debug_log(f"Overlay mouse_event: {event} at ({col}, {row})")
        if self.last_size:
            size = self.last_size
        return super().mouse_event(size, event, button, col, row, focus)

class MenuFrame(urwid.Frame):
    def keypress(self, size, key):
        debug_log(f"Frame keypress: {key}")
        return super().keypress(size, key)
    
    def mouse_event(self, size, event, button, col, row, focus):
        debug_log(f"Frame mouse_event: {event} at ({col}, {row})")
        return super().mouse_event(size, event, button, col, row, focus)

def wrap_menu_widget(widget, title=None):
    """Wrap a menu widget in a frame with optional title"""
    if title:
        widget = urwid.Frame(
            widget,
            header=urwid.AttrMap(urwid.Text(title), 'heading'),
            footer=urwid.Text("ESC/Left: Back, Enter/Right: Select")
        )
    return urwid.LineBox(widget)

def create_centered_menu(widget, width=('relative', 60), height=('relative', 60)):
    """Create a centered menu with proper sizing"""
    return MenuOverlay(
        wrap_menu_widget(widget),
        urwid.SolidFill(' '),
        'center', width,
        'middle', height,
        25, 10
    )

# Initialize top-level menu container
top = urwid.WidgetPlaceholder(urwid.SolidFill(' '))