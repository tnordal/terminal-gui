from __future__ import annotations

import urwid
from .menu_types import create_simple_menu, create_horizontal_menu, create_cascading_menu
from .menu_layout import top
from .utils import exit_program, create_palette, load_menu_config
from .config import get_menu_colors

class Menu:
    def __init__(self, config_file):
        self.config = load_menu_config(config_file)
        self.menu_type = self.config.get('menu_type', 'simple')
        self.menu_structure = self.config.get('menu_structure', {})
        self.menu_colors = get_menu_colors(self.config)
        self.main = None
        self.menu_stack = []

    def create_menu(self):
        if self.menu_type == 'simple':
            menu_widget = create_simple_menu(self.menu_structure, self.item_chosen, self.exit_program)
            return menu_widget
        elif self.menu_type == 'cascading':
            return create_cascading_menu(self.menu_structure)
        elif self.menu_type == 'horizontal':
            return create_horizontal_menu(self.menu_structure)
        else:
            raise ValueError(f"Unknown menu type: {self.menu_type}")

    def item_chosen(self, button, item):
        if 'submenu' in item:
            self.menu_stack.append(self.main.original_widget)
            submenu = create_simple_menu(
                {'heading': item['name'], 'menu': item['submenu']},
                self.item_chosen,
                self.exit_program
            )
            self.main.original_widget = urwid.Padding(submenu, left=2, right=2)
        else:
            response = urwid.Text([u'You chose ', item['name'], u'\n'])
            done = urwid.Button(u'Ok')
            urwid.connect_signal(done, 'click', self.exit_program)
            self.main.original_widget = urwid.Padding(
                urwid.Filler(urwid.Pile([response, done])),
                left=2,
                right=2
            )

    def keypress(self, key):
        if key == 'esc':
            if self.menu_type == 'horizontal':
                try:
                    top.go_back()
                except (IndexError, AttributeError):
                    raise urwid.ExitMainLoop()
            elif self.menu_type == 'cascading':
                try:
                    # Get the current cascading box widget
                    cascading_box = self.main.original_widget.base_widget
                    if cascading_box.box_level > 1:
                        cascading_box.original_widget = cascading_box.original_widget[0]
                        cascading_box.box_level -= 1
                    else:
                        raise urwid.ExitMainLoop()
                except (IndexError, AttributeError):
                    raise urwid.ExitMainLoop()
            elif self.menu_stack:
                self.main.original_widget = self.menu_stack.pop()
            else:
                raise urwid.ExitMainLoop()
        elif self.menu_type == 'cascading':
            # Let the cascading menu handle all other keys
            return key
        else:
            return key

    def exit_program(self, button=None):
        raise urwid.ExitMainLoop()

def main():
    menu = Menu('menu_config.toml')
    menu_widget = menu.create_menu()
    
    if menu.menu_type == 'cascading':
        # For cascading menu, don't add extra padding/overlay
        top_widget = menu_widget
    else:
        # For other menu types, use the original padding and overlay
        menu.main = urwid.Padding(menu_widget, left=2, right=2)
        top_widget = urwid.Overlay(
            menu.main,
            urwid.SolidFill(u'\N{MEDIUM SHADE}'),
            align='center',
            width=('relative', 60),
            valign='middle',
            height=('relative', 60),
            min_width=20,
            min_height=9
        )
    
    palette = create_palette(menu.menu_colors)
    
    # Create event loop with mouse support enabled
    event_loop = urwid.MainLoop(
        top_widget,
        palette=palette,
        unhandled_input=menu.keypress,
        handle_mouse=True,  # Enable mouse support
        pop_ups=True  # Enable pop-up handling
    )
    
    # Run the event loop
    event_loop.run()

if __name__ == '__main__':
    main()