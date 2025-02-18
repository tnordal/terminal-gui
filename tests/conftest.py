import os
import pytest
import toml
import urwid

@pytest.fixture
def sample_config_data():
    return {
        'menu': {
            'title': 'Test Menu',
            'menu_type': 'simple',
            'items': [
                {
                    'name': 'Option 1',
                    'command_type': 'shell',
                    'command': "echo 'Option 1 selected'"
                },
                {
                    'name': 'Option 2',
                    'command_type': 'shell',
                    'command': "echo 'Option 2 selected'"
                }
            ],
            'colors': {
                'default_fg': 'white',
                'default_bg': 'black',
                'heading_fg': 'yellow',
                'heading_bg': 'dark blue',
                'options_fg': 'white',
                'options_bg': 'dark gray'
            }
        }
    }

@pytest.fixture
def temp_config_file(tmp_path, sample_config_data):
    config_file = tmp_path / "test_config.toml"
    with open(config_file, 'w') as f:
        toml.dump(sample_config_data, f)
    return str(config_file)

@pytest.fixture
def mock_menu():
    title = "Test Menu"
    choices = ["Option 1", "Option 2"]
    menu_widget = urwid.ListBox(urwid.SimpleFocusListWalker([
        urwid.AttrMap(urwid.Text(["\n  ", title]), "heading"),
        urwid.AttrMap(urwid.Divider("\N{LOWER ONE QUARTER BLOCK}"), "line"),
        urwid.Divider(),
        *[urwid.AttrMap(urwid.Button(c), None, 'reversed') for c in choices],
        urwid.Divider()
    ]))
    return menu_widget

@pytest.fixture
def mock_button():
    return urwid.Button("Test Button")

@pytest.fixture
def mock_colors():
    return {
        'default_fg': 'white',
        'default_bg': 'black',
        'heading_fg': 'yellow',
        'heading_bg': 'dark blue',
        'options_fg': 'white',
        'options_bg': 'dark gray',
        'focus_heading_fg': 'white',
        'focus_heading_bg': 'dark blue',
        'focus_line_fg': 'white',
        'focus_line_bg': 'dark blue',
        'focus_options_fg': 'white',
        'focus_options_bg': 'dark blue',
        'selected_fg': 'white',
        'selected_bg': 'dark blue'
    }