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
            super().__init__(caption)  # Initialize with caption
            self.caption = caption  # Store caption for reference
            self.callback = callback
            # Override the default button display
            self._w = urwid.SelectableIcon(['  ', caption], 2)

        def keypress(self, size, key):
            debug_log(f"MenuButton keypress: size={size}, key={key}, caption={self.caption}")
            if key in ('enter', 'right'):
                debug_log(f"MenuButton executing callback for key: {key}")
                self.callback(self)
                return None
            debug_log(f"MenuButton passing through key: {key}")
            return key

        def mouse_event(self, size, event, button, col, row, focus):
            debug_log(f"MenuButton mouse_event: event={event}, caption={self.caption}")
            if event == 'mouse press' and button == 1:
                debug_log("MenuButton executing callback for mouse press")
                self.callback(self)
                return True
            return False

        @property
        def label(self):
            """Provide label property for consistent access"""
            return self.caption

    def menu_button(
        caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        callback: Callable[[urwid.Button], typing.Any],
    ) -> urwid.AttrMap:
        debug_log(f"Creating menu button with caption: {caption}")
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

        return menu_button(f"{caption} ...", open_menu)

    class MenuListBox(urwid.ListBox):
        def keypress(self, size, key):
            debug_log(f"MenuListBox keypress: size={size}, key={key}")
            
            # Handle vertical navigation
            if key in ('up', 'down'):
                current_pos = self.focus_position
                debug_log(f"Current focus position: {current_pos}")
                
                if key == 'up':
                    # Find previous selectable widget
                    pos = current_pos - 1
                    while pos >= 0:
                        widget = self.body[pos]
                        if hasattr(widget, 'selectable') and widget.selectable():
                            self.focus_position = pos
                            debug_log(f"Moving focus up to position {pos}")
                            return None
                        pos -= 1
                else:  # down
                    # Find next selectable widget
                    pos = current_pos + 1
                    while pos < len(self.body):
                        widget = self.body[pos]
                        if hasattr(widget, 'selectable') and widget.selectable():
                            self.focus_position = pos
                            debug_log(f"Moving focus down to position {pos}")
                            return None
                        pos += 1

                # If we reach here, try wrapping around
                if key == 'up':
                    for pos in range(len(self.body) - 1, -1, -1):
                        widget = self.body[pos]
                        if hasattr(widget, 'selectable') and widget.selectable():
                            self.focus_position = pos
                            debug_log(f"Wrapping to bottom at position {pos}")
                            return None
                else:
                    for pos in range(len(self.body)):
                        widget = self.body[pos]
                        if hasattr(widget, 'selectable') and widget.selectable():
                            self.focus_position = pos
                            debug_log(f"Wrapping to top at position {pos}")
                            return None

            # Handle enter/right/left keys
            elif key in ('enter', 'right'):
                focused = self.focus
                if focused:
                    debug_log(f"Forwarding {key} to focused widget")
                    key = focused.keypress(size, key)
                    if key is None:
                        return None

            # Pass through left key for menu closing
            elif key == 'left':
                debug_log("Returning left key for menu closing")
                return key

            return key

    def menu(
        title: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        choices: Iterable[urwid.Widget],
    ) -> urwid.ListBox:
        debug_log(f"Creating menu with title: {title}")
        
        title_widget = urwid.AttrMap(urwid.Text(title), 'heading')
        divider = urwid.AttrMap(urwid.Divider(), 'line')
        
        walker = urwid.SimpleFocusListWalker([title_widget, divider])
        
        # Add menu choices
        for choice in choices:
            walker.append(choice)
            
        # Find first selectable widget for initial focus
        for i, widget in enumerate(walker):
            if hasattr(widget, 'selectable') and widget.selectable():
                walker.set_focus(i)
                debug_log(f"Setting initial focus to widget at position {i}")
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