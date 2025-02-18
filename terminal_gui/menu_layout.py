from __future__ import annotations

import urwid
from .utils import exit_program

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
            raise urwid.ExitMainLoop()

class CascadingBoxes(urwid.WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self, box: urwid.Widget) -> None:
        super().__init__(urwid.SolidFill("/"))
        self.box_level = 0
        self.open_box(box)

    def open_box(self, box: urwid.Widget) -> None:
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

    def keypress(self, size, key: str) -> str | None:
        if key == "esc" and self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1
            return None

        return super().keypress(size, key)

top = HorizontalBoxes()