import urwid
from terminal_gui.menu import menu, item_chosen, exit_program

def test_menu_creation():
    title = "Test Menu"
    choices = ["Option 1", "Option 2"]
    menu_widget = menu(title, choices)
    assert isinstance(menu_widget, urwid.ListBox)

def test_item_chosen():
    button = urwid.Button("Test Button")
    choice = "Test Choice"
    item_chosen(button, choice)
    assert True  # Add proper assertions based on your implementation

def test_exit_program():
    button = urwid.Button("Exit")
    try:
        exit_program(button)
    except urwid.ExitMainLoop:
        assert True