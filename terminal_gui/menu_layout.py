from __future__ import annotations

import urwid
from .utils import exit_program, debug_log

focus_map = {"heading": "focus heading", "options": "focus options", "line": "focus line"}

class HorizontalBoxes(urwid.Columns):
    def __init__(self) -> None:
        super().__init__([], dividechars=1)
        self.menu_stack = []

    def open_box(self, box: urwid.Widget) -> None:
        if self.contents:
            self.menu_stack.append(self.contents[:])
            del self.contents[self.focus_position + 1 :]
        self.contents.append(
            (
                urwid.AttrMap(box, "options", focus_map),
                self.options(urwid.GIVEN, 24),
            )
        )
        self.focus_position = len(self.contents) - 1

    def go_back(self) -> None:
        if self.menu_stack:
            self.contents[:] = self.menu_stack.pop()
            self.focus_position = len(self.contents) - 1
        else:
            exit_program()

class CascadingBoxes(urwid.WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self, box: urwid.Widget) -> None:
        super().__init__(urwid.SolidFill("/"))
        self.box_level = 0
        self.open_box(box)

    def open_box(self, box: urwid.Widget) -> None:
        debug_log(f"Opening box at level {self.box_level}")
        self.original_widget = urwid.Overlay(
            urwid.LineBox(box),
            self.original_widget,
            align=urwid.CENTER,
            width=(urwid.RELATIVE, 80),
            valign=urwid.MIDDLE,
            height=(urwid.RELATIVE, 80),
            min_width=24,
            min_height=8,
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2,
        )
        self.box_level += 1

    def get_innermost_widget(self, widget):
        """Unwrap widget until we get to the actual content"""
        while hasattr(widget, 'original_widget'):
            widget = widget.original_widget
        return widget

    def get_box_at_level(self, level):
        """Get the box widget at the specified level"""
        widget = self.original_widget
        for _ in range(self.box_level - level - 1):
            if hasattr(widget, 'bottom_w'):
                widget = widget.bottom_w
        return widget

    def keypress(self, size, key: str) -> str | None:
        debug_log(f"CascadingBoxes keypress: size={size}, key={key}")
        
        # Handle back navigation
        if key in ("esc", "left") and self.box_level > 1:
            debug_log("Handling back navigation")
            self.original_widget = self.original_widget.bottom_w
            self.box_level -= 1
            return None

        # Get the current active box
        overlay = self.original_widget
        if not isinstance(overlay, urwid.Overlay):
            return overlay.keypress(size, key)

        # Calculate the size for the top widget
        overlay_size = overlay.pack(size, focus=True)
        debug_log(f"Overlay size: {overlay_size}")

        # Get the innermost active widget
        current_box = self.get_innermost_widget(overlay.top_w)
        debug_log(f"Current box type: {type(current_box)}")

        # Handle navigation within the current menu
        if isinstance(current_box, urwid.ListBox):
            try:
                # Try handling the keypress with the focused widget first
                focused = current_box.get_focus()[0]
                debug_log(f"Current focused widget: {focused}")
                if focused:
                    key = focused.keypress(overlay_size, key)
                    if key is None:
                        return None

                # If key wasn't handled, try standard list navigation
                if key in ('up', 'down', 'page up', 'page down'):
                    debug_log(f"Delegating {key} to ListBox")
                    return current_box.keypress(overlay_size, key)

            except AttributeError as e:
                debug_log(f"AttributeError in keypress handling: {str(e)}")

        # If nothing else handled it, try the container
        if key:
            debug_log("Delegating to overlay")
            return overlay.keypress(size, key)

        return key

    def mouse_event(self, size, event, button, col, row, focus):
        debug_log(f"CascadingBoxes mouse_event: size={size}, event={event}, button={button}, col={col}, row={row}, focus={focus}")
        
        # Get the current overlay
        overlay = self.original_widget
        if not isinstance(overlay, urwid.Overlay):
            return overlay.mouse_event(size, event, button, col, row, focus)

        # Convert coordinates for the overlay
        overlay_size = overlay.pack(size, focus=True)
        top_w, _ = overlay.calculate_padding_filler(overlay_size, focus)
        
        # Adjust coordinates for the inner widget
        inner_col = col - overlay.left
        inner_row = row - overlay.top
        
        if 0 <= inner_col < top_w[0] and 0 <= inner_row < top_w[1]:
            # Get the innermost widget
            current_box = self.get_innermost_widget(overlay.top_w)
            if isinstance(current_box, urwid.ListBox):
                try:
                    debug_log(f"Delegating mouse event to ListBox at ({inner_col}, {inner_row})")
                    return current_box.mouse_event(top_w, event, button, inner_col, inner_row, focus)
                except AttributeError as e:
                    debug_log(f"AttributeError in mouse event handling: {str(e)}")
        
        # If nothing else handled it or coordinates are outside, try the container
        debug_log("Delegating to overlay")
        return overlay.mouse_event(size, event, button, col, row, focus)

top = HorizontalBoxes()