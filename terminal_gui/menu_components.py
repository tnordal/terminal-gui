from __future__ import annotations

import typing
import urwid
from .utils import exit_program
from .command_executor import CommandExecutor

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Hashable, Iterable
    from typing import Optional

focus_map = {"heading": "focus heading", "options": "focus options", "line": "focus line"}

class MenuButton(urwid.Button):
    def __init__(
        self,
        caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        callback: Callable[[MenuButton], typing.Any],
    ) -> None:
        super().__init__("", on_press=callback)
        self._w = urwid.AttrMap(
            urwid.SelectableIcon(["  \N{BULLET} ", caption], 2),
            None,
            "selected",
        )

class SubMenu(urwid.WidgetWrap[MenuButton]):
    def __init__(
        self,
        caption: str | tuple[Hashable, str],
        choices: Iterable[urwid.Widget],
    ) -> None:
        from .menu_layout import top  # Keep local import to avoid circular import
        super().__init__(MenuButton([caption, "\N{HORIZONTAL ELLIPSIS}"], self.open_menu))
        line = urwid.Divider("\N{LOWER ONE QUARTER BLOCK}")
        listbox = urwid.ListBox(
            urwid.SimpleFocusListWalker(
                [
                    urwid.AttrMap(urwid.Text(["\n  ", caption]), "heading"),
                    urwid.AttrMap(line, "line"),
                    urwid.Divider(),
                    *choices,
                    urwid.Divider(),
                ]
            )
        )
        self.menu = urwid.AttrMap(listbox, "options")

    def open_menu(self, button: MenuButton) -> None:
        from .menu_layout import top  # Keep local import to avoid circular import
        top.open_box(self.menu)

class Choice(urwid.WidgetWrap[MenuButton]):
    def __init__(
        self,
        caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
    ) -> None:
        super().__init__(MenuButton(caption, self.item_chosen))
        self.caption = caption

    def item_chosen(self, button: MenuButton) -> None:
        from .menu_layout import top  # Keep local import to avoid circular import
        response = urwid.Text(["  You chose ", self.caption, "\n"])
        done = MenuButton("Ok", exit_program)
        response_box = urwid.Filler(urwid.Pile([response, done]))
        top.open_box(urwid.AttrMap(response_box, "options"))

class CommandChoice(Choice):
    def __init__(
        self,
        caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        command_type: str,
        command: str,
        working_dir: Optional[str] = None,
    ) -> None:
        super().__init__(caption)
        self.command_type = command_type
        self.command = command
        self.working_dir = working_dir

    def item_chosen(self, button: MenuButton) -> None:
        from .menu_layout import top  # Keep local import to avoid circular import
        
        # Execute the command
        try:
            CommandExecutor.execute_command(self.command_type, self.command, self.working_dir)
            message = f"  Executing command: {self.command}\n"
        except Exception as e:
            message = f"  Error executing command: {str(e)}\n"
        
        response = urwid.Text([message])
        done = MenuButton("Ok", exit_program)
        response_box = urwid.Filler(urwid.Pile([response, done]))
        top.open_box(urwid.AttrMap(response_box, "options"))