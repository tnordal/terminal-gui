from __future__ import annotations

import typing

import urwid
import toml
from .config import load_config, get_menu_colors

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Hashable, Iterable

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

class Menu:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.menu_type = self.config.get('menu_type', 'simple')
        self.menu_structure = self.config.get('menu_structure', {})
        self.menu_colors = get_menu_colors(self.config)
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

    def create_cascading_menu(self, structure):
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

        def item_chosen(button: urwid.Button) -> None:
            response = urwid.Text(["You chose ", button.label, "\n"])
            done = menu_button("Ok", exit_program)
            top.open_box(urwid.Filler(urwid.Pile([response, done])))

        def exit_program(button: urwid.Button) -> typing.NoReturn:
            raise urwid.ExitMainLoop()

        def build_menu(structure):
            choices = []
            for item in structure['menu']:
                if 'submenu' in item:
                    submenu = sub_menu(item['name'], build_menu({'menu': item['submenu']}))
                    choices.append(submenu)
                else:
                    choices.append(menu_button(item['name'], item_chosen))
            return choices

        menu_top = menu(structure['heading'], build_menu(structure))
        top = CascadingBoxes(menu_top)
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
                try:
                    top.go_back()
                except (IndexError, AttributeError):
                    raise urwid.ExitMainLoop()
            elif self.menu_type == 'cascading':
                try:
                    top.keypress(None, key)
                except (IndexError, AttributeError):
                    raise urwid.ExitMainLoop()
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
    palette = [
        (None, menu.menu_colors['text'], menu.menu_colors['background']),
        ("heading", menu.menu_colors['text'], menu.menu_colors['background']),
        ("line", menu.menu_colors['text'], menu.menu_colors['background']),
        ("options", menu.menu_colors['text'], menu.menu_colors['background']),
        ("focus heading", menu.menu_colors['highlight'], menu.menu_colors['background']),
        ("focus line", menu.menu_colors['highlight'], menu.menu_colors['background']),
        ("focus options", menu.menu_colors['highlight'], menu.menu_colors['background']),
        ("selected", menu.menu_colors['highlight'], menu.menu_colors['background']),
    ]
    urwid.MainLoop(top_widget, palette=palette, unhandled_input=menu.keypress).run()

if __name__ == '__main__':
    main()