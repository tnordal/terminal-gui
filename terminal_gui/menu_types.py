from __future__ import annotations

import urwid
from .utils import exit_program, debug_log

class MenuDisplay:
    def __init__(self):
        self.body = urwid.SimpleFocusListWalker([])
        self.listbox = urwid.ListBox(self.body)
        self.current_menu = None
        self.menu_stack = []
        
    def push_menu(self, menu_widget):
        debug_log(f"Pushing menu to stack")
        if self.current_menu is not None:
            self.menu_stack.append(self.current_menu)
        self.current_menu = menu_widget
        self.body[:] = menu_widget.body
        
    def pop_menu(self):
        debug_log("Popping menu from stack")
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
            self.body[:] = self.current_menu.body
            return True
        return False

def create_simple_menu(structure, item_chosen_callback, exit_callback):
    debug_log("Creating simple menu")
    body = [urwid.Text(structure['heading']), urwid.Divider()]
    for item in structure['menu']:
        button = urwid.Button(item['name'])
        urwid.connect_signal(button, 'click', item_chosen_callback, item)
        body.append(urwid.AttrMap(button, None, focus_map='selected'))
    exit_button = urwid.Button('Exit')
    urwid.connect_signal(exit_button, 'click', exit_callback)
    body.append(urwid.AttrMap(exit_button, None, focus_map='selected'))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def create_horizontal_menu(structure):
    debug_log("Creating horizontal menu")
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

class MenuItem(urwid.Text):
    def __init__(self, caption):
        super().__init__(caption)
        self.caption = caption
        
    def selectable(self):
        return True
        
    def keypress(self, size, key):
        return key

class MenuButton(urwid.Button):
    button_left = urwid.Text("  ")
    button_right = urwid.Text("")

    def __init__(self, caption, callback):
        super().__init__("")
        self._label = urwid.SelectableIcon(caption, 0)
        self._w = urwid.AttrMap(
            urwid.Columns([
                ('fixed', 2, self.button_left),
                self._label,
                ('fixed', 2, self.button_right),
            ]),
            None, 'selected'
        )
        self.caption = caption
        urwid.connect_signal(self, 'click', callback)

class SubMenuButton(MenuButton):
    def __init__(self, caption, submenu):
        self.submenu = submenu
        super().__init__(caption + " ...", self.enter_submenu)
        
    def enter_submenu(self, button):
        debug_log(f"Entering submenu: {self.caption}")
        submenu_widget = create_menu(self.caption, self.submenu)
        menu_display.push_menu(submenu_widget)

class CommandButton(MenuButton):
    def __init__(self, caption, command):
        self.command = command
        super().__init__(caption, self.execute_command)
        
    def execute_command(self, button):
        debug_log(f"Executing command")
        try:
            from .command_executor import CommandExecutor
            CommandExecutor.execute_command(
                self.command['type'],
                self.command['value'],
                self.command.get('working_dir')
            )
            message = f"Executing: {self.command['value']}"
        except Exception as e:
            message = f"Error: {str(e)}"
        
        response = urwid.Text([message, "\n"])
        done = MenuButton("Ok", lambda _: menu_display.pop_menu())
        menu_display.push_menu(urwid.ListBox(urwid.SimpleFocusListWalker([response, done])))

def create_menu(title, choices):
    debug_log(f"Creating menu: {title}")
    body = [urwid.Text(title), urwid.Divider()]
    
    for choice in choices:
        if isinstance(choice, dict):
            if 'submenu' in choice:
                body.append(SubMenuButton(choice['name'], choice['submenu']))
            elif 'command' in choice:
                body.append(CommandButton(choice['name'], choice['command']))
            else:
                body.append(MenuButton(choice['name'], item_chosen))
    
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def create_menu_item(item):
    if 'command' in item:
        return CommandButton(
            item['name'],
            item['command']
        )
    return MenuItem(item['name'])

def item_chosen(button):
    debug_log(f"Item chosen: {button.caption}")
    response = urwid.Text([f"You chose {button.caption}\n"])
    done = MenuButton("Ok", lambda _: menu_display.pop_menu())
    menu_display.push_menu(urwid.ListBox(urwid.SimpleFocusListWalker([response, done])))

def create_cascading_menu(structure):
    debug_log("Creating cascading menu")
    global menu_display
    menu_display = MenuDisplay()
    
    main_menu = create_menu(structure['heading'], structure['menu'])
    menu_display.push_menu(main_menu)
    
    return urwid.Frame(
        menu_display.listbox,
        footer=urwid.Text("ESC/Left: Back, Enter/Right: Select")
    )