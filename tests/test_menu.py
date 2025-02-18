import pytest
import urwid
from terminal_gui.menu import Menu

def test_menu_initialization(temp_config_file, sample_config_data):
    """Test menu initialization"""
    menu = Menu(temp_config_file)
    assert menu.config == sample_config_data
    assert menu.menu_type == 'simple'
    assert isinstance(menu.menu_structure, dict)
    assert menu.main is None
    assert menu.menu_stack == []

def test_create_simple_menu(mocker, temp_config_file):
    """Test simple menu creation"""
    menu = Menu(temp_config_file)
    menu.menu_structure = {
        'heading': 'Test Menu',
        'menu': [
            {'name': 'Option 1', 'command': 'echo test 1'},
            {'name': 'Option 2', 'command': 'echo test 2'}
        ]
    }
    menu_widget = menu.create_menu()
    assert isinstance(menu_widget, urwid.Widget)

def test_create_invalid_menu_type(mocker, temp_config_file):
    """Test menu creation with invalid type"""
    menu = Menu(temp_config_file)
    menu.menu_type = 'invalid'
    with pytest.raises(ValueError) as exc:
        menu.create_menu()
    assert "Unknown menu type: invalid" in str(exc.value)

def test_item_chosen_with_submenu(mocker, temp_config_file):
    """Test item chosen with submenu"""
    menu = Menu(temp_config_file)
    menu.main = urwid.AttrMap(urwid.SolidFill(), 'body')
    button = urwid.Button('Test')
    item = {
        'name': 'Test Item',
        'submenu': [{'name': 'Submenu Item', 'command': 'test'}]
    }
    
    menu.item_chosen(button, item)
    assert len(menu.menu_stack) == 1
    assert isinstance(menu.main.original_widget, urwid.Padding)

def test_item_chosen_without_submenu(mocker, temp_config_file):
    """Test item chosen without submenu"""
    menu = Menu(temp_config_file)
    menu.main = urwid.AttrMap(urwid.SolidFill(), 'body')
    button = urwid.Button('Test')
    item = {'name': 'Test Item', 'command': 'test'}
    
    menu.item_chosen(button, item)
    assert isinstance(menu.main.original_widget, urwid.Padding)
    pile = menu.main.original_widget.original_widget.original_widget
    assert isinstance(pile, urwid.Pile)
    assert len(pile.contents) == 2  # Response text and Ok button

def test_keypress_esc_with_menu_stack(mocker, temp_config_file):
    """Test keypress esc with menu stack"""
    menu = Menu(temp_config_file)
    menu.main = urwid.AttrMap(urwid.SolidFill(), 'body')
    previous_widget = urwid.Text('Previous')
    menu.menu_stack.append(previous_widget)
    
    menu.keypress('esc')
    assert len(menu.menu_stack) == 0
    assert menu.main.original_widget == previous_widget

def test_keypress_esc_empty_stack(mocker, temp_config_file):
    """Test keypress esc with empty stack"""
    menu = Menu(temp_config_file)
    with pytest.raises(urwid.ExitMainLoop):
        menu.keypress('esc')

def test_keypress_other(mocker, temp_config_file):
    """Test keypress with other key"""
    menu = Menu(temp_config_file)
    assert menu.keypress('enter') == 'enter'

def test_exit_program(mocker, temp_config_file):
    """Test exit program"""
    menu = Menu(temp_config_file)
    with pytest.raises(urwid.ExitMainLoop):
        menu.exit_program()