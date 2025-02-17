from __future__ import annotations

import typing

import urwid
import toml

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Hashable, Iterable

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
        top.open_box(self.menu)

class Choice(urwid.WidgetWrap[MenuButton]):
    def __init__(
        self,
        caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
    ) -> None:
        super().__init__(MenuButton(caption, self.item_chosen))
        self.caption = caption

    def item_chosen(self, button: MenuButton) -> None:
        response = urwid.Text(["  You chose ", self.caption, "\n"])
        done = MenuButton("Ok", exit_program)
        response_box = urwid.Filler(urwid.Pile([response, done]))
        top.open_box(urwid.AttrMap(response_box, "options"))

def exit_program(key):
    raise urwid.ExitMainLoop()

palette = [
    (None, "light gray", "black"),
    ("heading", "black", "light gray"),
    ("line", "black", "light gray"),
    ("options", "dark gray", "black"),
    ("focus heading", "white", "dark red"),
    ("focus line", "black", "dark red"),
    ("focus options", "black", "light gray"),
    ("selected", "white", "dark blue"),
]
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

top = HorizontalBoxes()

class Menu:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.menu_type = self.config.get('menu_type', 'simple')
        self.menu_structure = self.config.get('menu_structure', {})
        self.main = None
        self.menu_stack = []

    def load_config(self, file_path):
        with open(file_path, 'r') as file:
            return toml.load(file)

    def create_menu(self):
        if self.menu_type == 'simple':
            return self.create_simple_menu(self.menu_structure)
        elif self.menu_type == 'cascading':
            return self.create_cascading_menu(self.menu_structure)
        elif self.menu_type == 'horizontal':
            return self.create_horizontal_menu(self.menu_structure)
        else:
            raise ValueError(f"Unknown menu type: {self.menu_type}")

    def create_simple_menu(self, structure):
        body = [urwid.Text(structure['heading']), urwid.Divider()]
        for item in structure['menu']:
            button = urwid.Button(item['name'])
            urwid.connect_signal(button, 'click', self.item_chosen, item)
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        exit_button = urwid.Button('Exit')
        urwid.connect_signal(exit_button, 'click', self.exit_program)
        body.append(urwid.AttrMap(exit_button, None, focus_map='reversed'))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def create_horizontal_menu(self, structure):
        choices = []
        for item in structure['menu']:
            if 'submenu' in item:
                submenu = SubMenu(item['name'], [Choice(subitem['name']) for subitem in item['submenu']])
                choices.append(submenu)
            else:
                choices.append(Choice(item['name']))
        menu_top = SubMenu(structure['heading'], choices)
        top.open_box(menu_top.menu)
        return top

    def item_chosen(self, button, item):
        if 'submenu' in item:
            self.menu_stack.append(self.main.original_widget)
            submenu = self.create_simple_menu({'heading': item['name'], 'menu': item['submenu']})
            self.main.original_widget = urwid.Padding(submenu, left=2, right=2)
        else:
            response = urwid.Text([u'You chose ', item['name'], u'\n'])
            done = urwid.Button(u'Ok')
            urwid.connect_signal(done, 'click', self.exit_program)
            self.main.original_widget = urwid.Padding(urwid.Filler(urwid.Pile([response, done])), left=2, right=2)

    def keypress(self, key):
        if key == 'esc':
            if self.menu_type == 'horizontal':
                top.go_back()
            elif self.menu_stack:
                self.main.original_widget = self.menu_stack.pop()
            else:
                raise urwid.ExitMainLoop()
        else:
            return key

    def exit_program(self, button):
        raise urwid.ExitMainLoop()

def main():
    menu = Menu('menu_config.toml')
    menu_widget = menu.create_menu()
    menu.main = urwid.Padding(menu_widget, left=2, right=2)
    top_widget = urwid.Overlay(menu.main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
                               align='center', width=('relative', 60),
                               valign='middle', height=('relative', 60),
                               min_width=20, min_height=9)
    urwid.MainLoop(top_widget, palette=palette, unhandled_input=menu.keypress).run()

if __name__ == '__main__':
    main()