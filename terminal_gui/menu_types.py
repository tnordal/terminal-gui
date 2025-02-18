from __future__ import annotations

import typing
import urwid
from collections.abc import Callable, Hashable, Iterable

from .menu_components import SubMenu, Choice, CommandChoice
from .menu_layout import CascadingBoxes, top
from .utils import exit_program

def create_simple_menu(structure, item_chosen_callback, exit_callback):
    body = [urwid.Text(structure['heading']), urwid.Divider()]
    for item in structure['menu']:
        button = urwid.Button(item['name'])
        urwid.connect_signal(button, 'click', item_chosen_callback, item)
        body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    exit_button = urwid.Button('Exit')
    urwid.connect_signal(exit_button, 'click', exit_callback)
    body.append(urwid.AttrMap(exit_button, None, focus_map='reversed'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def create_menu_item(item):
    if 'command' in item:
        return CommandChoice(
            item['name'],
            item['command']['type'],
            item['command']['value'],
            item['command'].get('working_dir')
        )
    return Choice(item['name'])

def create_horizontal_menu(structure):
    choices = []
    for item in structure['menu']:
        if 'submenu' in item:
            submenu_choices = [create_menu_item(subitem) for subitem in item['submenu']]
            submenu = SubMenu(item['name'], submenu_choices)
            choices.append(submenu)
        else:
            choices.append(create_menu_item(item))
    menu_top = SubMenu(structure['heading'], choices)
    top.open_box(menu_top.menu)
    return top

def create_cascading_menu(structure):
    class MenuButton(urwid.Button):
        def __init__(self, caption, callback):
            super().__init__("")
            self._w = urwid.SelectableIcon(['  ', caption], 2)
            self.callback = callback

        def keypress(self, size, key):
            if key in ('enter', 'right'):
                self.callback(self)
                return None
            return key

    def menu_button(
        caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        callback: Callable[[urwid.Button], typing.Any],
    ) -> urwid.AttrMap:
        button = MenuButton(caption, callback)
        return urwid.AttrMap(button, 'options', focus_map='focus_options')

    def sub_menu(
        caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        choices: Iterable[urwid.Widget],
    ) -> urwid.Widget:
        contents = menu(caption, choices)

        def open_menu(button: urwid.Button) -> None:
            top.open_box(contents)

        button = MenuButton([caption, " ..."], open_menu)
        return urwid.AttrMap(button, 'options', focus_map='focus_options')

    class MenuListBox(urwid.ListBox):
        def keypress(self, size, key):
            if key in ('up', 'down'):
                key = super().keypress(size, key)
                if key is None:
                    return None
                if key == 'up':
                    pos = self.focus_position - 1
                    while pos >= 0:
                        widget = self.body[pos]
                        if hasattr(widget, 'selectable') and widget.selectable():
                            self.focus_position = pos
                            return None
                        pos -= 1
                elif key == 'down':
                    pos = self.focus_position + 1
                    while pos < len(self.body):
                        widget = self.body[pos]
                        if hasattr(widget, 'selectable') and widget.selectable():
                            self.focus_position = pos
                            return None
                        pos += 1
            elif key in ('enter', 'right'):
                focused = self.focus
                if focused and hasattr(focused, 'keypress'):
                    key = focused.keypress(size, key)
                    if key is None:
                        return None
            return key

    def menu(
        title: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        choices: Iterable[urwid.Widget],
    ) -> urwid.ListBox:
        title_widget = urwid.AttrMap(urwid.Text(title), 'heading')
        divider = urwid.AttrMap(urwid.Divider(), 'line')
        
        walker = urwid.SimpleFocusListWalker([title_widget, divider])
        
        selectable_found = False
        for choice in choices:
            walker.append(choice)
            if not selectable_found and hasattr(choice, 'selectable') and choice.selectable():
                walker.set_focus(len(walker) - 1)
                selectable_found = True
        
        if not selectable_found:
            for i, widget in enumerate(walker):
                if hasattr(widget, 'selectable') and widget.selectable():
                    walker.set_focus(i)
                    break
        
        return MenuListBox(walker)

    def item_chosen(button: urwid.Button) -> None:
        response = urwid.Text(["You chose ", button.label, "\n"])
        done = menu_button("Ok", exit_program)
        top.open_box(urwid.Filler(urwid.Pile([response, done])))

    def build_menu(structure):
        choices = []
        for item in structure['menu']:
            if 'submenu' in item:
                submenu = sub_menu(item['name'], build_menu({'menu': item['submenu']}))
                choices.append(submenu)
            elif 'command' in item:
                def make_command_callback(cmd_type, cmd, work_dir):
                    def callback(button):
                        try:
                            from .command_executor import CommandExecutor
                            CommandExecutor.execute_command(cmd_type, cmd, work_dir)
                            message = f"Executing command: {cmd}"
                        except Exception as e:
                            message = f"Error executing command: {str(e)}"
                        response = urwid.Text([message, "\n"])
                        done = menu_button("Ok", exit_program)
                        top.open_box(urwid.Filler(urwid.Pile([response, done])))
                    return callback

                cmd = item['command']
                command_button = menu_button(
                    item['name'],
                    make_command_callback(
                        cmd['type'],
                        cmd['value'],
                        cmd.get('working_dir')
                    )
                )
                choices.append(command_button)
            else:
                choices.append(menu_button(item['name'], item_chosen))

        return choices

    menu_top = menu(structure['heading'], build_menu(structure))
    return CascadingBoxes(menu_top)