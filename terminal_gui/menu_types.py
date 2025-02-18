from __future__ import annotations

import typing
import urwid
from collections.abc import Callable, Hashable, Iterable

from .menu_components import SubMenu, Choice, CommandChoice
from .menu_layout import CascadingBoxes, top
from .utils import exit_program, debug_log

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
            debug_log(f"MenuButton keypress: size={size}, key={key}")
            if key in ('enter', 'right'):
                debug_log(f"MenuButton executing callback for key: {key}")
                self.callback(self)
                return None
            debug_log(f"MenuButton passing through key: {key}")
            return key

        def mouse_event(self, size, event, button, col, row, focus):
            debug_log(f"MenuButton mouse_event: size={size}, event={event}, button={button}, col={col}, row={row}, focus={focus}")
            if event == 'mouse press':
                debug_log("MenuButton executing callback for mouse press")
                self.callback(self)
                return True
            return False

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
            debug_log(f"Opening submenu: {caption}")
            top.open_box(contents)

        button = MenuButton([caption, " ..."], open_menu)
        return urwid.AttrMap(button, 'options', focus_map='focus_options')

    class MenuListBox(urwid.ListBox):
        def keypress(self, size, key):
            debug_log(f"MenuListBox keypress: size={size}, key={key}")
            if key in ('up', 'down', 'left', 'right', 'enter'):
                # First let the parent handle navigation
                debug_log("MenuListBox delegating to parent")
                key = super().keypress(size, key)
                debug_log(f"Parent returned key: {key}")
                if key is None:
                    return None

                if key in ('up', 'down'):
                    # Handle vertical navigation if parent didn't
                    current_pos = self.focus_position
                    debug_log(f"Current position: {current_pos}")
                    if key == 'up':
                        # Try to find the previous selectable widget
                        pos = current_pos - 1
                        while pos >= 0:
                            widget = self.body[pos]
                            debug_log(f"Checking widget at pos {pos}: {widget}")
                            if hasattr(widget, 'selectable') and widget.selectable():
                                self.focus_position = pos
                                debug_log(f"Found selectable widget at pos {pos}")
                                return None
                            pos -= 1
                    else:  # down
                        # Try to find the next selectable widget
                        pos = current_pos + 1
                        while pos < len(self.body):
                            widget = self.body[pos]
                            debug_log(f"Checking widget at pos {pos}: {widget}")
                            if hasattr(widget, 'selectable') and widget.selectable():
                                self.focus_position = pos
                                debug_log(f"Found selectable widget at pos {pos}")
                                return None
                            pos += 1
                elif key in ('enter', 'right'):
                    # Forward to focused widget
                    focused = self.focus
                    debug_log(f"Forwarding {key} to focused widget: {focused}")
                    if focused and hasattr(focused, 'keypress'):
                        key = focused.keypress(size, key)
                        if key is None:
                            return None
                elif key == 'left':
                    # Let the parent handle closing the submenu
                    debug_log("Returning left key to parent for submenu closing")
                    return key

            # Return unhandled keys
            debug_log(f"MenuListBox returning unhandled key: {key}")
            return key

        def mouse_event(self, size, event, button, col, row, focus):
            debug_log(f"MenuListBox mouse_event: size={size}, event={event}, button={button}, col={col}, row={row}, focus={focus}")
            return super().mouse_event(size, event, button, col, row, focus)

    def menu(
        title: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        choices: Iterable[urwid.Widget],
    ) -> urwid.ListBox:
        title_widget = urwid.AttrMap(urwid.Text(title), 'heading')
        divider = urwid.AttrMap(urwid.Divider(), 'line')
        
        walker = urwid.SimpleFocusListWalker([title_widget, divider])
        
        debug_log(f"Creating menu with title: {title}")
        selectable_found = False
        for choice in choices:
            walker.append(choice)
            if not selectable_found and hasattr(choice, 'selectable') and choice.selectable():
                walker.set_focus(len(walker) - 1)
                debug_log(f"Setting initial focus to: {choice}")
                selectable_found = True
        
        if not selectable_found:
            for i, widget in enumerate(walker):
                if hasattr(widget, 'selectable') and widget.selectable():
                    walker.set_focus(i)
                    debug_log(f"Setting fallback focus to widget at position {i}: {widget}")
                    break
        
        return MenuListBox(walker)

    def item_chosen(button: urwid.Button) -> None:
        debug_log(f"Item chosen: {button.label}")
        response = urwid.Text(["You chose ", button.label, "\n"])
        done = menu_button("Ok", exit_program)
        top.open_box(urwid.Filler(urwid.Pile([response, done])))

    def build_menu(structure):
        choices = []
        for item in structure['menu']:
            if 'submenu' in item:
                debug_log(f"Building submenu: {item['name']}")
                submenu = sub_menu(item['name'], build_menu({'menu': item['submenu']}))
                choices.append(submenu)
            elif 'command' in item:
                debug_log(f"Building command item: {item['name']}")
                def make_command_callback(cmd_type, cmd, work_dir):
                    def callback(button):
                        try:
                            from .command_executor import CommandExecutor
                            debug_log(f"Executing command: type={cmd_type}, cmd={cmd}, work_dir={work_dir}")
                            CommandExecutor.execute_command(cmd_type, cmd, work_dir)
                            message = f"Executing command: {cmd}"
                        except Exception as e:
                            debug_log(f"Error executing command: {str(e)}")
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
                debug_log(f"Building regular item: {item['name']}")
                choices.append(menu_button(item['name'], item_chosen))

        return choices

    debug_log("Creating main menu")
    menu_top = menu(structure['heading'], build_menu(structure))
    return CascadingBoxes(menu_top)