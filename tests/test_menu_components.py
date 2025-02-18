import pytest
import urwid
from terminal_gui.menu_components import MenuButton, SubMenu, Choice, CommandChoice

@pytest.fixture
def mock_menu_layout(mocker):
    """Mock the menu_layout module"""
    mock_layout = mocker.Mock()
    mock_layout.top = mocker.Mock()
    mocker.patch.dict('sys.modules', {
        'terminal_gui.menu_layout': mock_layout
    })
    return mock_layout.top

def test_menu_button_creation():
    """Test MenuButton initialization"""
    def dummy_callback(button):
        pass
    
    button = MenuButton("Test Caption", dummy_callback)
    assert isinstance(button, urwid.Button)
    assert isinstance(button._w, urwid.AttrMap)
    assert isinstance(button._w.original_widget, urwid.SelectableIcon)
    assert "Test Caption" in button._w.original_widget.text

def test_submenu_creation():
    """Test SubMenu initialization"""
    choices = [
        MenuButton("Choice 1", lambda x: None),
        MenuButton("Choice 2", lambda x: None)
    ]
    submenu = SubMenu("Test Menu", choices)
    assert isinstance(submenu._w, MenuButton)
    assert isinstance(submenu.menu, urwid.AttrMap)
    
    # Check menu structure
    listbox = submenu.menu.original_widget
    assert isinstance(listbox, urwid.ListBox)
    assert len(listbox.body) == 6  # header + line + divider + 2 choices + divider

def test_choice_creation():
    """Test Choice initialization"""
    choice = Choice("Test Choice")
    assert isinstance(choice._w, MenuButton)
    assert choice.caption == "Test Choice"

def test_choice_item_chosen(mock_menu_layout):
    """Test Choice item_chosen method"""
    choice = Choice("Test Choice")
    button = choice._w
    
    choice.item_chosen(button)
    
    assert mock_menu_layout.open_box.called
    call_args = mock_menu_layout.open_box.call_args[0][0]
    assert isinstance(call_args, urwid.AttrMap)
    
    # Check response box contents
    response_box = call_args.original_widget
    assert isinstance(response_box, urwid.Filler)
    pile = response_box.original_widget
    assert isinstance(pile, urwid.Pile)
    assert len(pile.contents) == 2  # Response text and Ok button
    text_widget = pile.contents[0][0]
    assert isinstance(text_widget, urwid.Text)
    assert "Test Choice" in text_widget.text

def test_command_choice_creation():
    """Test CommandChoice initialization"""
    command_choice = CommandChoice(
        "Test Command",
        "shell",
        "echo test",
        "/tmp"
    )
    assert isinstance(command_choice._w, MenuButton)
    assert command_choice.caption == "Test Command"
    assert command_choice.command_type == "shell"
    assert command_choice.command == "echo test"
    assert command_choice.working_dir == "/tmp"

def test_command_choice_item_chosen_success(mock_menu_layout, mocker):
    """Test CommandChoice successful command execution"""
    mock_executor = mocker.patch('terminal_gui.menu_components.CommandExecutor')
    
    command_choice = CommandChoice("Test Command", "shell", "echo test")
    button = command_choice._w
    
    command_choice.item_chosen(button)
    
    mock_executor.execute_command.assert_called_once_with("shell", "echo test", None)
    assert mock_menu_layout.open_box.called
    
    # Check response message
    call_args = mock_menu_layout.open_box.call_args[0][0]
    response_box = call_args.original_widget
    assert isinstance(response_box, urwid.Filler)
    pile = response_box.original_widget
    assert isinstance(pile, urwid.Pile)
    text_widget = pile.contents[0][0]
    assert isinstance(text_widget, urwid.Text)
    assert "Executing command: echo test" in text_widget.text

def test_command_choice_item_chosen_error(mock_menu_layout, mocker):
    """Test CommandChoice command execution error"""
    mock_executor = mocker.patch('terminal_gui.menu_components.CommandExecutor')
    mock_executor.execute_command.side_effect = Exception("Test error")
    
    command_choice = CommandChoice("Test Command", "shell", "invalid")
    button = command_choice._w
    
    command_choice.item_chosen(button)
    
    assert mock_menu_layout.open_box.called
    
    # Check error message
    call_args = mock_menu_layout.open_box.call_args[0][0]
    response_box = call_args.original_widget
    assert isinstance(response_box, urwid.Filler)
    pile = response_box.original_widget
    assert isinstance(pile, urwid.Pile)
    text_widget = pile.contents[0][0]
    assert isinstance(text_widget, urwid.Text)
    assert "Error executing command: Test error" in text_widget.text