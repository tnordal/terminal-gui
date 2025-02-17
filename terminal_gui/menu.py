import urwid
import toml

class Menu:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.menu_type = self.config.get('menu_type', 'simple')
        self.menu_structure = self.config.get('menu_structure', {})
        self.main = None

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
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def item_chosen(self, button, item):
        if 'submenu' in item:
            submenu = self.create_simple_menu({'heading': item['name'], 'menu': item['submenu']})
            self.main.original_widget = urwid.Padding(submenu, left=2, right=2)
        else:
            response = urwid.Text([u'You chose ', item['name'], u'\n'])
            done = urwid.Button(u'Ok')
            urwid.connect_signal(done, 'click', self.exit_program)
            self.main.original_widget = urwid.Padding(urwid.Filler(urwid.Pile([response, done])), left=2, right=2)

    def exit_program(self, button):
        raise urwid.ExitMainLoop()

def main():
    menu = Menu('menu_config.toml')
    menu_widget = menu.create_menu()
    menu.main = urwid.Padding(menu_widget, left=2, right=2)
    top = urwid.Overlay(menu.main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
                        align='center', width=('relative', 60),
                        valign='middle', height=('relative', 60),
                        min_width=20, min_height=9)
    urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()

if __name__ == '__main__':
    main()