import pytest
import toml
import urwid
from terminal_gui.utils import exit_program, create_palette, load_menu_config

def test_exit_program():
    """Test exit program function"""
    with pytest.raises(urwid.ExitMainLoop):
        exit_program()
    
    # Test with button parameter
    button = urwid.Button("Exit")
    with pytest.raises(urwid.ExitMainLoop):
        exit_program(button)

def test_create_palette():
    """Test palette creation with default colors"""
    colors = {}
    palette = create_palette(colors)
    
    assert len(palette) == 8  # Check all color pairs are created
    
    # Check default colors
    assert palette[0] == (None, 'black', 'light gray')
    assert palette[1] == ('heading', 'black', 'light gray')
    assert palette[2] == ('line', 'black', 'light gray')

def test_create_palette_custom_colors():
    """Test palette creation with custom colors"""
    custom_colors = {
        'default_fg': 'white',
        'default_bg': 'black',
        'heading_fg': 'yellow',
        'heading_bg': 'dark blue',
        'options_fg': 'white',
        'options_bg': 'dark gray'
    }
    
    palette = create_palette(custom_colors)
    
    # Check custom colors are used
    assert palette[0] == (None, 'white', 'black')
    assert palette[1] == ('heading', 'yellow', 'dark blue')
    assert palette[3] == ('options', 'white', 'dark gray')

def test_load_menu_config(temp_config_file, sample_config_data):
    """Test loading menu configuration"""
    config = load_menu_config(temp_config_file)
    assert config == sample_config_data
    assert 'menu' in config
    assert isinstance(config['menu'], dict)

def test_load_menu_config_file_not_found():
    """Test loading non-existent config file"""
    with pytest.raises(FileNotFoundError):
        load_menu_config('nonexistent_config.toml')

def test_load_menu_config_invalid_toml(tmp_path):
    """Test loading invalid TOML file"""
    invalid_file = tmp_path / "invalid.toml"
    with open(invalid_file, 'w') as f:
        f.write("invalid [ toml content")
    
    with pytest.raises(toml.TomlDecodeError):
        load_menu_config(str(invalid_file))