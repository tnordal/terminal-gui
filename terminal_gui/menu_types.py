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
    def menu_button(
        caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        callback: Callable[[urwid.Button], typing.Any],
    ) -> urwid.AttrMap:
        button = urwid.Button(caption, on_press=callback)
        return urwid.AttrMap(button, None, focus_map="reversed")

    def sub_menu(
        caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        choices: Iterable[urwid.Widget],
    ) -> urwid.Widget:
        contents = menu(caption, choices)

        def open_menu(button: urwid.Button) -> None:
            return top.open_box(contents)

        return menu_button([caption, "..."], open_menu)

    def menu(
        title: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
        choices: Iterable[urwid.Widget],
    ) -> urwid.ListBox:
        body = [urwid.Text(title), urwid.Divider(), *choices]
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def build_menu(structure):
        choices = []
        for item in structure['menu']:
            if 'submenu' in item:
                submenu = sub_menu(item['name'], build_menu({'menu': item['submenu']}))
                choices.append(submenu)
            else:
                if 'command' in item:
                    choices.append(
                        CommandChoice(
                            item['name'],
                            item['command']['type'],
                            item['command']['value'],
                            item['command'].get('working_dir')
                        )
                    )
                else:
                    choices.append(menu_button(item['name'], item_chosen))

        return choices

    def item_chosen(button: urwid.Button) -> None:
        response = urwid.Text(["You chose ", button.label, "\n"])
        done = menu_button("Ok", exit_program)
        top.open_box(urwid.Filler(urwid.Pile([response, done])))

    menu_top = menu(structure['heading'], build_menu(structure))
    return CascadingBoxes(menu_top)